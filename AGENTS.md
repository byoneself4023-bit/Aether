# AGENTS.md

> Aether 모노레포 컨텍스트 단일 페이지. Claude Code/AI 에이전트가 작업 시작 시 본 문서를 컨텍스트로 참조한다.
> 갱신 정책 — 코드 변경 시 영향 받는 §를 같은 PR에 동시 수정 (CHANGELOG처럼 운영, H-7 PR 게이트 체크박스로 강제 예정).

---

## §1. 호출 체인 (서비스 간 통합 단방향)

```text
frontend ──HTTP──┬──> auth-service     (JWT 발급/검증)
                 ├──> portfolio-service (수치 계산)
                 └──> llm-service ──HTTP──> portfolio-service
                                                  │
                                                  └─> ChromaDB (in-process volume)
                                                  └─> Gemini API (외부 SaaS)
```

- **요점**: `llm-service`는 `auth-service`와 **직접 통합되지 않는다**. 인증은 frontend가 auth-service로부터 JWT를 받아 portfolio/llm 호출 시 헤더에 동봉하는 방식. (`docs/agent-capability-audit/01_architecture.md:§1` 라인 8)
- **LLM → Portfolio**: `llm-service/app/services/portfolio_client.py` — `httpx.AsyncClient`에 `event_hooks={"request": [_forward_headers]}` 등록 → 호출 시 `X-Request-ID` + `Authorization` 자동 forward (H-10/L-7, §9 참조).
- **Frontend → 3 백엔드**: `frontend/src/lib/utils/constants.ts:2-6` — `API_URLS = { AUTH: 8003, PORTFOLIO: 8001, LLM: 8002 }`.
- **비-REST 통신 미사용**: gRPC/Kafka/Redis Streams 분석 범위 0건 (01:§2). 모든 서비스 간 호출은 동기 HTTP/JSON.

---

## §2. 토폴로지 (4 서비스 + 2 인프라)

| 컴포넌트 | 포트 | 스택 | 책임 |
|---|---|---|---|
| frontend | 3000 | Next.js 15 / React 19 / Axios | UI, JWT 보관, 3개 백엔드 호출 |
| auth-service | 8003 | Spring Boot / Java 17 | 인증, JWT 발급/검증, 리프레시 |
| portfolio-service | 8001 | FastAPI / Python 3.11 | 최적화·리스크·백테스트 수치 계산 |
| llm-service | 8002 | FastAPI / Python 3.11 | RAG, 도메인 분석(LLM 호출) |
| postgres | 5433→5432 | postgres:16-alpine | users 테이블 (auth만 사용) |
| redis | 6380→6379 | redis:7-alpine | refresh token, blacklist (auth만 사용) |

- 근거: `docker-compose.yml:6-160` (서비스/인프라 정의), `docker-compose.yml:14-15, 30-31, 52-53, 73-74, 101-102, 142-143` (포트 매핑 6행).
- 단일 bridge 네트워크 `aether-network`. 서비스 디스커버리는 docker-compose hostname (예: `portfolio-service:8001`).

---

## §3. 레이어 경계 (llm-service)

```text
routers/        ──>  agents/        ──>  services/        ──>  외부 (Gemini / portfolio-service / ChromaDB)
                       │                  │
                       │                  ├── prompts.py / prompt_registry.py  (프롬프트 자산)
                       │                  ├── llm.py / llm_provider.py          (LLM 호출)
                       │                  ├── rag.py                            (인덱싱·검색·답변)
                       │                  ├── guardrails.py / validators.py    (입출력 검증)
                       │                  └── portfolio_client.py              (외부 HTTP)
                       │
                       ├── base.py            (BaseAgent 추상)
                       ├── tools.py           (ToolRegistry + lazy init)
                       └── portfolio_tools.py (4 도메인 함수 @tool 래퍼)
                                              ▲
schemas/  ────────────────────────  middleware/ ────┘  (X-Request-ID, rate limit, JWT)
```

- **규칙**: routers → agents → services → 외부 (단방향). schemas는 자유. middleware는 main.py에 등록만 (services에서 import 금지). agents는 services를 도구로 사용, services는 agents를 모른다 (의존 역전).
- **agents/ 도입 (T-1a + H-2)**: `app/agents/` 신설 — `BaseAgent` 추상 + `ToolRegistry` + 4 도메인 도구 래퍼. T-1a는 인프라만 (chat.py 미수정), T-1b가 ReAct 통합 예정.
- 근거: `llm-service/app/main.py:8-13, 64-66`, ADR 0002 §결정 두 번째 블록 (활성).

---

## §4. 빌드·테스트·린트

```bash
# llm-service
cd llm-service && python -m venv .venv && . .venv/bin/activate
pip install -q -r requirements-dev.txt   # H-7 후: ruff/black/mypy/pytest-cov 포함
ruff check . || true                       # 1차 비차단 (H-7c에서 차단 전환)
black --check . || true                    # 1차 비차단
mypy app/ --ignore-missing-imports || true # 1차 비차단
pytest tests/ -q --cov=app --cov-fail-under=81  # 차단 (측정 86% - 5%)

# portfolio-service (동일 패턴, 단 cov-fail-under=0 — H-7d collection 오류 정리 후 차단 전환)
cd portfolio-service && pytest tests/ -q --cov=app --cov-fail-under=0

# auth-service (Spring Boot — Java 게이트는 H-7b 별도 카드)
cd auth-service && ./gradlew test --no-daemon -Dspring.profiles.active=test

# frontend
cd frontend && npm ci --prefer-offline
npx tsc --noEmit             # 차단
npx eslint src/ || true      # 1차 비차단
npx vitest run               # 5건 차단 (Dashboard/Chat/Backtest/Optimize/Header)
npm run build                # 차단

# 문서 (루트에서)
npx --yes markdownlint-cli AGENTS.md CLAUDE.md docs/adr/*.md  # 차단 (MD040 강제)
```

- **테스트 합산**: 519건 (llm 237 + portfolio 212 + auth 70). Phase 1 audit는 514건 기록(232/212/70) — H-4(`e9acdf8`) 후 prompt registry 테스트 5건 증가. (`docs/agent-capability-audit/05_evaluation_testing.md:§1` 표).
- **린트/타입 (H-7 도입됨)**: ruff + black + mypy + pytest-cov 백엔드 4종 + tsc + eslint + vitest 프론트 3종 + markdownlint = 8종. 1차 도입은 측정값 -5% 임계 + lint/type 비차단 (CLAUDE.md §2 표).
- **CI 파이프라인**: `Jenkinsfile:35-90` (백엔드 3종 병렬, llm/portfolio에 lint/type/cov 추가), `94-104` (frontend tsc/eslint/vitest/build), `109-115` (Lint Markdown 신규), `120-138` (docker build), `144-165` (push, main 한정), `171-193` (SSH 배포 + 4개 헬스체크).

---

## §5. 프롬프트 컨벤션 (registry 단일 진입점)

- **모든 LLM 호출은 `get_registry().get(name, version)` 단일 진입점을 거친다**. 코드 상수로 직접 f-string/format 호출 금지.
- 등록 7종 v1.0 — `system_prompt`, `portfolio_analysis_schema`, `risk_explanation_schema`, `backtest_summary_schema`, `recommendation_schema`, `rag_system`, `rag_user` (`llm-service/app/services/prompt_registry.py:130-189`).
- **JSON 응답 스키마는 `app/schemas/llm_output.py` Pydantic 모델로 정의**하고 registry는 `model_json_schema()` 정렬 JSON 문자열을 등록한다. Gemini `response_schema`가 모델을 강제 출력하므로 프롬프트 텍스트에 schema를 주입하지 않는다 (H-6).
- 새 프롬프트 추가 절차: (1) `prompts.py`에 상수 정의, (2) `_register_default_prompts`에 `register(name, version, template, metadata)` 추가, (3) 호출부에서 `registry.get(...).template` 또는 `.format(...)` 사용.
- 새 버전 등록은 동일 `name` + 새 `version` 문자열로. 환경변수 `PROMPT_VERSION_<NAME>`으로 런타임 선택 (현재 v1.0만 등록). 자세한 정책은 ADR 0003.
- **{ } escape 정책**: Jinja2 템플릿(`{{ var }}`)과 JSON 스키마(`{"key": ...}`)가 한 프롬프트에 혼재할 때 JSON 중괄호는 `{{ "{" }}` / `{{ "}" }}`로 escape. 자세한 사례는 ADR 0003 §{} escape.

---

## §6. 외부 의존성

| 카테고리 | 종류 | 위치 |
|---|---|---|
| LLM Provider | Google Gemini 2.5-Flash | `llm-service/app/config.py:20`, `requirements.txt:4` |
| Embedding | Gemini embedding-001 | `llm-service/app/config.py:27` |
| 벡터 DB | ChromaDB 1.5.0 (in-process persistent) | `llm-service/requirements.txt:3` |
| 관계형 DB | PostgreSQL 16 | `docker-compose.yml:7` (auth-service 전용) |
| 캐시 | Redis 7 | `docker-compose.yml:27` (auth-service 전용) |
| 시장 데이터 | yfinance | `portfolio-service/requirements.txt` |

- **단일 LLM Provider**: `LLMProvider` 추상 + `GeminiProvider` 구현(`llm-service/app/services/llm_provider.py`). OpenAI/Anthropic/Bedrock 분기 부재.
- **벡터 DB 수평 확장 제약**: ChromaDB가 `llm-service` 컨테이너 볼륨에 묶여 있어 인스턴스 다중화 시 인덱스 분리 문제. T-6에서 Qdrant 이전 예정 (01:§4).

---

## §7. 지배 숫자 (변경 시 본 § + 인용 위치 동시 갱신)

| 지표 | 값 | 근거 |
|---|---|---|
| 백엔드 서비스 수 | 4 | docs/agent-capability-audit/01_architecture.md:§1 |
| 인프라 컴포넌트 수 | 2 (postgres, redis) | docker-compose.yml:6-40 |
| 테스트 합산 | 543 (258/215/70) — T-1a로 +10 (agents 단위) + H-10/L-7로 +13 | 본 § §4 갱신 |
| 도구 등록 (tool_registry) | 4종 (analyze_portfolio / explain_risk / summarize_backtest / get_recommendation) | §10 + ADR 0005 |
| 등록 프롬프트 수 | 7 (v1.0) | prompt_registry.py:130-189 |
| RAG eval 쿼리 수 | 6 (in-code) | 05:§2 라인 62 — 외부 .jsonl 이전이 향후 과제 |
| llm-service Python | 3.11-slim | llm-service/Dockerfile:2 |
| LLM 호출 timeout | 60초 (httpx) | portfolio_client.py |
| CI 백엔드 병렬 stage | 3 (portfolio/llm/auth) | Jenkinsfile:36-77 |
| JWT 검증 적용 라우터 | 17 (llm 9 + portfolio 8) | §9 + ADR 0004 |
| 분산 트레이싱 forward | X-Request-ID + Authorization (httpx event_hooks) | §9 |

---

## §8. 작업 시작 체크리스트 (모든 PR 공통)

작업 카드를 받으면 본 페이지 외에 다음 7가지를 순서대로 확인한다:

1. **카드 §4 변경 대상 파일 목록** — 그 외 파일은 건드리지 않는다 (CLAUDE.md §6 1책임 원칙).
2. **선행 작업 완료 여부** — 카드 §1 메타의 "선행 작업"이 main에 머지됐는지.
3. **§3 레이어 경계** — 새 코드의 import 방향이 `routers → services → 외부`를 위반하지 않는지.
4. **§5 프롬프트 컨벤션** — LLM 호출이 registry 단일 진입점을 거치는지. 코드 상수 f-string 금지.
5. **§4 빌드 명령** — 변경 대상 서비스의 pytest를 로컬에서 통과시킨 뒤 PR 올린다.
6. **CLAUDE.md §4 위험 작업** — force push, db drop, secrets 노출 등은 사용자 확인 필수.
7. **AGENTS.md 갱신** — 본 카드가 §7 지배 숫자나 §1-§6의 사실을 변경했다면 같은 PR에 본 문서 갱신 포함.

---

## §9. 인증 · 분산 트레이싱 (H-10 + L-7)

### JWT 검증 (HS256 공유 비밀키)

- 알고리즘: **HS256** — `auth-service` `JwtTokenProvider.java:41-43` (`Keys.hmacShaKeyFor`) ↔ python 서비스 `pyjwt.decode(..., algorithms=["HS256"])`. ADR 0004 참조.
- 비밀키: `JWT_SECRET` 환경변수. 세 서비스(auth/llm/portfolio)가 동일 값 공유 (`docker-compose.yml`).
- 검증 dependency: `app/middleware/auth.py::verify_jwt`. 라우터에 `user: dict = Depends(verify_jwt)` 1줄 추가.
- 적용 17건 + 면제 7건 (`/health`, `/`, `/metrics`, `/tokens`) — 카드 08:§결정2/3.

### X-Request-ID 자동 forward

- 기존 미들웨어가 요청마다 RID 발급 (`app/middleware/logging.py`의 `request_id_var` ContextVar).
- `httpx.AsyncClient`에 `event_hooks={"request": [_forward_headers]}` 등록 — llm → portfolio 호출 시 `X-Request-ID` + `Authorization` 자동 헤더 포함.
- forward 정책: `_forward_headers`는 `request_id_var` / `auth_token_var` 가 set된 경우만 헤더 추가. RID는 64자 truncate.

### 토큰 로그 마스킹

- 두 서비스 `logging.py`에 `_mask_secrets` regex 적용 (`Bearer [...]` → `Bearer ***`).
- JSON dump 전체에 적용해 `extra` 필드까지 커버.

### 테스트 우회 패턴

- `tests/conftest.py`의 autouse `_bypass_jwt` fixture가 모든 테스트에서 `verify_jwt`를 stub (기존 232+ 테스트 무수정 통과).
- 실제 JWT 검증을 테스트하려면 `@pytest.mark.no_jwt_bypass` 마커로 opt-out (`tests/test_auth_middleware.py` 참조).

---

## §10. Agent Architecture (T-1a + H-2)

### 모듈 책임 (`llm-service/app/agents/`)

| 파일 | 책임 |
|---|---|
| `base.py` | `BaseAgent` 추상 — `run(user_input, context) -> dict` 1 메서드 (YAGNI, T-1b ReAct 구현 / T-3 Multi-Agent 시 확장) |
| `tools.py` | `ToolRegistry` + `get_tool_registry()` lazy init + `_register_default_tools()` — prompt_registry와 동일 패턴 (자기 일관성) |
| `portfolio_tools.py` | 4 도메인 함수 @tool 래퍼 — `services/llm.py` 원본을 0 변경 호출 |

### Lazy init 패턴 (prompt_registry 미러)

```python
_tool_registry: ToolRegistry | None = None

def get_tool_registry() -> ToolRegistry:
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        _register_default_tools(_tool_registry)
    return _tool_registry
```

- 테스트에서 `_tool_registry = None` reset 가능 (autouse fixture로 상태 공유 차단).
- import 사이드 이펙트 회피 — 도구 등록은 첫 `get_tool_registry()` 호출 시.

### YAGNI 정책 — 미도입 항목

T-3 Multi-Agent 진입 시 도입:
- Supervisor 패턴 (멀티 에이전트 조율)
- Subgraph 추상 (LangGraph 고급)
- Memory / Checkpointer (상태 저장)

**T-1a는 인프라만** — chat.py / services/llm.py **0 변경**. T-1b가 `chat.py:331-349` 절차적 4 호출을 ReAct 1 호출로 통합.

### 의존성

- `langgraph>=0.2` (1.1.10 측정)
- `langchain-google-genai>=2.0` (4.2.2)
- `langchain-core>=0.3` (1.3.2)

상세 채택 사유는 ADR 0005 참조.
