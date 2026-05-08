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
- **chat.py → ReActAgent → 4 도구**: `chat.py:331-356`에서 `settings.use_react_agent`가 True면 `ReActAgent.run()` 1 호출 (T-1b). 모델이 4 도구(analyze/risk/backtest/recommend)의 호출 순서 자율 판단. `USE_REACT_AGENT=false` env로 절차적 호출 fallback (§10 참조).
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
| 벡터 DB | ChromaDB 1.5.0 / Qdrant v1.12.0 어댑터 토글 (`VECTOR_STORE=chromadb\|qdrant`, default chromadb) | `llm-service/app/services/vector_store.py` + `docs/adr/0009-qdrant-migration.md` |
| 관계형 DB | PostgreSQL 16 | `docker-compose.yml:7` (auth-service 전용) |
| 캐시 | Redis 7 | `docker-compose.yml:27` (auth-service 전용) |
| 시장 데이터 | yfinance | `portfolio-service/requirements.txt` |

- **단일 LLM Provider**: `LLMProvider` 추상 + `GeminiProvider` 구현(`llm-service/app/services/llm_provider.py`). OpenAI/Anthropic/Bedrock 분기 부재.
- **벡터 DB 어댑터 (T-6 머지)**: `vector_store.py`에서 ChromaDBStore / QdrantStore 추상화. `VECTOR_STORE` 환경변수로 즉시 전환, 사고 시 `unset`만으로 ChromaDB 복원. ChromaDB는 `llm_chroma_data` 볼륨에 묶이는 한계가 있고, 운영 진입 시 `qdrant` 토글로 멀티 인스턴스 동기화 가능.

---

## §7. 지배 숫자 (변경 시 본 § + 인용 위치 동시 갱신)

| 지표 | 값 | 근거 |
|---|---|---|
| 백엔드 서비스 수 | 4 | docs/agent-capability-audit/01_architecture.md:§1 |
| 인프라 컴포넌트 수 | 2 (postgres, redis) | docker-compose.yml:6-40 |
| 테스트 합산 | 535 (270/195/70) — D-1로 −20 (test_experiment 제거 / `#22`) | 본 § §4 갱신 |
| 도구 등록 (tool_registry) | 5종 (analyze_portfolio / explain_risk / summarize_backtest / get_recommendation / **search_knowledge_base**) — D-5 RAG 통합 | §10 + ADR 0005 + ADR 0018 |
| 등록 프롬프트 수 | 8 (v1.0) — T-1b로 react_system_prompt 추가 | prompt_registry.py + ADR 0006 |
| chat.py:/api/chat/analyze LLM 호출 | **ReAct 1 호출** (USE_REACT_AGENT=true 기본) / 절차적 4 호출 (fallback) | §10 + ADR 0006 |
| Gemini SDK | google-genai 1.74 (legacy google-generativeai 제거) — H-6 디벨롭 | requirements.txt + ADR 0007 |
| RAG eval 쿼리 수 | 6 (in-code) | 05:§2 라인 62 — 외부 .jsonl 이전이 향후 과제 |
| llm-service Python | 3.11-slim | llm-service/Dockerfile:2 |
| LLM 호출 timeout | 60초 (httpx) | portfolio_client.py |
| CI 백엔드 병렬 stage | 3 (portfolio/llm/auth) | Jenkinsfile:36-77 |
| JWT 알고리즘 | HS512 단일 (호환 모드 X) — F-1a (`#21`) 통일 | §9 + ADR 0004 v2 |
| JWT 검증 적용 라우터 | 12 (llm 9 + portfolio 3) — D-1 (`#22`)에서 experiment 5 endpoint 제거 | §9 + ADR 0004 |
| 보류 기능 (시나리오 A 본질 X) | 4건 (MLflow / drift_warning / weight_alerts / RAG 데이터 정제) — D-1 (`#22`) + D-9 보류 | ADR 0011 + ADR 0014 |
| Vector store backend | **Qdrant default** (T-6b) — chromadb fallback (`VECTOR_STORE=chromadb` env). aether_knowledge 컬렉션 26 chunks / 3072차원 cosine | ADR 0009 + 0014 + 0016 |
| RAG 평가 메트릭 | 4건 (relevance@k / recall@k / LLM-as-judge quality / faithfulness) — D-8 자체 구현 (ragas 미도입). ground truth 8건. CLI: `python -m scripts.eval_rag --no-llm-judge` (Gemini quota 회피) | ADR 0015 |
| RAG Chunking 정책 | chunk_size=500 / overlap=300 (D-7 grid search 9 조합). Auto Research 본능 — `python -m scripts.grid_search_chunking`. relevance@k 0.7222 → 0.7413 (+0.0191) | ADR 0017 |
| RAG 도구 통합 | ReAct 5번째 도구 (search_knowledge_base) — D-5 자율 판단. chat.py fallback `RAG_FALLBACK_DIRECT=true` (default). ReAct system prompt v1.1 (5 도구 + 판단 규칙) | ADR 0018 |
| Streaming SSE | `POST /api/chat/stream` — D-6 신규 endpoint (기존 /api/chat 0 변경). LangGraph `astream_events` v2 / token + tool events / format `data: {json}\n\n` / 우대 요건 4 직격 | ADR 0019 |
| D-4 Audit baseline | 카드 14건 머지 / WORK_PATTERNS 17/18 해소 / 14,414 LOC / 635 테스트 / 19→**20** ADR / 누적 자료 3,354 LOC | AUDIT.md + ADR 0020 |
| PRINCIPLES 패턴 | 7 → **10** (P-1 / §8 신규 endpoint 분리 / §9 Auto Research / §10 G1 본질 트리거 정정) | PRINCIPLES.md + ADR 0021 |
| KARPATHY 매칭 | 8 본능 평균 76 → **87점** (Skill 95 / Auto Research 90 / Reversibility 90 등) — 면접 답변 5 영역 매핑. V-1b: §1 재작성 (영상 9 항목 ↔ Aether 매핑 / 3 영역 통합) + §부록 6건 쿠카 영역. §2-§6 = 영구 보류 (ADR 0023) | KARPATHY_MAPPING.md + ADR 0021 + ADR 0023 |
| V-0 / V-1 baseline | V-0 DIGEST.md 812 LOC + KARPATHY_LECTURE.md 605 LOC 통합 (누적 자료 12 파일). V-1 의문 7건 검증 — 부족 5 (V-1b 트리거) + 부분 충분 2. V-1b 의무 5건 정착 (KARPATHY §1 재작성 / LECTURE 단어 위생 / 6건 쿠카 영역 이동 / 매칭 점수 재계산 / 면접 답변 재검토). 양면 정책 12 ADR (0011-**0022**) | DIGEST.md + VERIFICATION_v2.md + ADR 0022 |
| V-1b baseline | V-1 검증 결과 적용 — 의무 5건 → 2건 정정 (§6 면접 답변 = I-1 영역 / 6건 쿠카 영역 분산 = 영구 보류). 정착 영역: KARPATHY_MAPPING §1 재작성 (영상 9 항목 ↔ Aether 매핑 / 3 영역 통합) + §부록 6건 쿠카 영역 인용 위치. KARPATHY_LECTURE.md 단어 위생 전 본문 정정 (605 LOC / 5 위반 어휘 grep = 0건). 영구 보류 6건 (§2-§6 + 6 쿠카 영역 분산). **양면 정책 13 ADR (0011-0023)** | KARPATHY_MAPPING.md + KARPATHY_LECTURE.md + ADR 0023 |
| CL-1 baseline | 자료 인덱스 정착 — docs/README.md (~150 LOC / 폴더 영역 + 카드 18건) + docs/agent-capability-audit/README.md (~180 LOC / 정착 14 + pre-existing 8 분류) + docs/adr/README.md (~150 LOC / 23건 카테고리 + 양면 정책 14 ADR). pre-existing untracked 14건 분류 본문 (A 면접/이력서 2 + B Phase 2 9 + C PoC 1 + D 코드 영역 2) — 자동 처리 X / 사용자 결정 의무. 영구 보류 3건 (코드 = CL-2 / 의존성 = CL-3 / pre-existing 자동 처리). **양면 정책 14 ADR (0011-0024)** | docs/README.md + docs/agent-capability-audit/README.md + docs/adr/README.md + ADR 0024 |
| CL-D baseline | CL-2 (코드 cleanup) + CL-3 (의존성 cleanup) **영구 보류 결정** (ADR 0025) — 시나리오 A 본질 X / 시나리오 B 진입 시점 (도메인 검증 + 사용자 5+ 인터뷰 + PMF 10불) 트리거 명시. PRINCIPLES 패턴 6 (미적용 결정 = 시그널) 직접 사례 — ADR 0010 / 0011 / 0014 보류 결정 패턴 일관성. **양면 정책 15 ADR (0011-0025)** = 정착 7 + 보류 4 (0010 / 0011 / 0014 / **0025**) + 메타 4 + 정리 1. 다음 진입: TG-1 (시연 가이드) → I-1 (면접 답변) → Aether 종료 | ADR 0025 + docs/adr/README.md + docs/README.md |
| TG-1 baseline | docs/TEST_GUIDE.md 신규 (~280 LOC / 5 기능 × 3 시나리오 = 15 시나리오 + 사전 정착 + 진단 흐름 + 면접 시연 5분 + 자가 점검 19 항목). Claude Code 4 서비스 코드 직접 정독 (auth/portfolio/llm/frontend) — 실측 본문 (파일:라인) 명시. 5 기능: §2.1 signup+login (HS512+blacklist) / §2.2 optimize (Markowitz+Sharpe) / §2.3 backtest (walk-forward) / §2.4 chat (LangGraph ReAct + 5 도구 + Qdrant + SSE) / §2.5 MCP (stdio 4 도구). I-1 진입 자료 영역 정착 (TEST_GUIDE + KARPATHY_MAPPING §6 + INTERVIEW + Top 10) | docs/TEST_GUIDE.md + docs/README.md + docs/agent-capability-audit/README.md |
| DIFF-1 baseline | docs/DIFFERENTIATION.md 신규 (~400 LOC / 직무별 4 영역 + 면접 꼬리 질문 19건 + 자료 인용 흐름). 4 영역: §2 AI Engineer (5 영역 — ReAct 자율 판단 / Qdrant + 자체 4 메트릭 / Auto Research grid search / MCP stdio / Streaming SSE) / §3 Backend (5 영역 — 4 MSA / JWT HS512 + Redis blacklist / D-2 운영급 / Markowitz / walk-forward) / §4 Full Stack (3 영역 — Next.js 페이지 분리 / SSE 클라이언트 / Docker Compose 6) / §5 시스템 설계 (5 영역 — 양면 정책 15 ADR / 시나리오 A 본질 / 카파시 영상 9 ↔ 매핑 / WORK_PATTERNS 18 + 5 가드 / D-4 패턴). 코드 위치 (파일:라인) 명시 의무 — 추측 X / 실측 본문. 자료 8 인용 통합 (KARPATHY_MAPPING / AUDIT / TEST_GUIDE / META_REVIEW / WORK_PATTERNS / PRINCIPLES / SCENARIO / ADR README). I-1 진입 자료 (DIFFERENTIATION + TEST_GUIDE + KARPATHY §6 + INTERVIEW + Top 10) | docs/DIFFERENTIATION.md + docs/README.md §3 + §7 |
| CACHE_MAXSIZE | 1000 (기본) — 인메모리 LRU 캐시 항목 수 | docker-compose.yml + portfolio config.py + .env.example |
| CORS 명시 정책 | allow_methods=[GET,POST,OPTIONS] / allow_headers=[Authorization,Content-Type,X-Request-ID] — D-2 통일 | ADR 0012 |
| API 키 검증 (llm) | lifespan startup + config Pydantic validator 이중 안전장치 — D-2 (`#23`) | ADR 0012 |
| Frontend 페이지 LOC 임계 | 200 LOC (페이지 50 LOC 이하 = 컴포넌트 조합만) — D-3 (`#25`) | ADR 0013 |
| 분산 트레이싱 forward | X-Request-ID + Authorization (httpx event_hooks) | §9 |
| MCP 서버 도구 | 4종 (analyze_portfolio / compute_risk / run_backtest / get_recommendation, stdio transport) | docs/adr/0008-mcp-server-adoption.md + portfolio-service/app/mcp_server.py |
| Top 10 진행 상황 | **9.5/10** (T-3 Multi-Agent 보류 결정 — 시나리오 A 일관성 + Houseman Phase 7-12 학습 적용 통합) | docs/agent-capability-audit/EVOLUTION.md + docs/adr/0010-t3-multi-agent-deferred.md |

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

### JWT 검증 (HS512 공유 비밀키)

- 알고리즘: **HS512** — `auth-service` `JwtTokenProvider.java:41-43` (`Keys.hmacShaKeyFor`, jjwt가 비밀키 길이 64 bytes 이상에서 HS512 자동 선택) ↔ python 서비스 `pyjwt.decode(..., algorithms=["HS512"])`. F-1a (`#21`)에서 양 측 통일. ADR 0004 v2 참조.
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
| `react_agent.py` (T-1b) | `ReActAgent(BaseAgent)` — `langgraph.prebuilt.create_react_agent` + `_extract_tool_results` 어댑터 (ToolMessage → AnalysisResponse 4 필드 매핑) |

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

**T-1a는 인프라만** — chat.py / services/llm.py **0 변경**. **T-1b 통합 완료** — `chat.py:331-356`이 `if settings.use_react_agent:` 분기로 ReAct 1 호출 (모델이 4 도구 자율 판단) + fallback 절차적 호출 보존. `USE_REACT_AGENT=false` env로 즉시 롤백 가능.

### Tool 함수명 → AnalysisResponse 필드 매핑 (T-1b 어댑터)

`react_agent.py::_TOOL_NAME_TO_FIELD`:

| Tool name | AnalysisResponse 필드 |
|---|---|
| `analyze_portfolio_tool` | `portfolio_analysis` |
| `explain_risk_tool` | `risk_analysis` |
| `summarize_backtest_tool` | `backtest_analysis` |
| `get_recommendation_tool` | `recommendation` |

ToolMessage.content는 JSON 문자열 또는 dict — 어댑터가 try/except로 분기 처리.

### 테스트 우회 패턴 (T-1b)

`tests/conftest.py`의 autouse `_disable_react_agent` fixture가 `settings.use_react_agent = False`로 강제 → 기존 258 mock 테스트 호환. ReAct 검증은 `@pytest.mark.use_react_agent` 마커로 opt-in.

### 의존성

- `langgraph>=0.2` (1.1.10 측정)
- `langchain-google-genai>=2.0` (4.2.2)
- `langchain-core>=0.3` (1.3.2)
- `google-genai` (1.74, langchain-google-genai 전이의존 — H-6 디벨롭으로 legacy `google-generativeai` 제거)

상세 채택 사유는 ADR 0005 (LangGraph) + ADR 0007 (genai SDK 마이그레이션) 참조.

---

## §11. MCP 서버 (T-2)

### 외부 노출 채널

`portfolio-service/app/mcp_server.py`에서 `Server("aether-portfolio")` 인스턴스가 stdio transport로 4 도메인 도구 외부 노출. 외부 LLM (Claude Desktop / Cursor / 외부 LangChain 에이전트)이 subprocess launch로 직접 호출.

호출 체인: `외부 LLM → stdio subprocess → mcp_server.py → app/services/* (라우터 우회, services 직접 호출)`.

인증: subprocess launch = 운영자 신뢰 (HTTP 헤더 X). 운영급 인증은 후속 카드 T-2c (HTTP/SSE transport)에서.

### 4 도구 매핑

| MCP Tool | 호출 대상 | 반환 |
|---|---|---|
| `analyze_portfolio` | `services/optimizer.py:optimize_max_sharpe` | `PortfolioMetrics` |
| `compute_risk` | `services/risk.py:risk_summary` | `RiskSummary` |
| `run_backtest` | `services/backtest.py:walk_forward_backtest` | `BacktestResult` |
| `get_recommendation` | `services/drift_detector.py:analyze_drift` | `CombinedDriftAnalysis` |

### L-7 X-Request-ID 통합 (옵션 A)

`call_tool` 핸들러가 `arguments.pop("_request_id")` → `request_id_ctx.set()` → finally `token.reset()`. inputSchema 미노출 (외부 LLM 모름, 자동 RID 생성). 기존 `RequestLoggingMiddleware`와 자기 일관성.

### `_serialize()` 어댑터

dataclass / numpy / pandas / Enum / Pydantic → JSON dict 8 분기 recursion. `services/*` 도메인 함수 0 변경 보존.

### entrypoint

```bash
PYTHONPATH=/path/to/portfolio-service python -m app.mcp_server
```

상세 채택 사유는 ADR 0008 (MCP 서버 채택) + TECH_DECISIONS.md §5 (MCP 결정 근거) 참조.
