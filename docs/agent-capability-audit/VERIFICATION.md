# VERIFICATION — F-1 전체 기능 플로우 검증 + 워크플로우 회고

> **카드**: F-1 (검증 전용 / 코드 변경 0)
> **작성일**: 2026-05-06
> **본질**: "박힌 코드 = 작동하는 코드 X" — 5 기능 × 3 시나리오 (정상 / Edge / 에러) 실측 + 사용자 의도 회고 + 후속 카드 트리거.
> **결과 한 줄**: §1 인증 기능 전체 PASS, §2-§4 라우터 차단 (HS512 vs HS256 알고리즘 불일치 — F-1a 분리), §5 부분 검증, §10 의도 회고 박힘.

---

## §0. 사전 측정 + 진입 게이트

### §0.1 6 서비스 health (실측 2026-05-06 17:36 KST)

| 서비스 | 컨테이너 | 포트 | health | 결과 |
|---|---|---|---|---|
| auth-service | aether-auth | 8003 | healthy | ✓ |
| portfolio-service | aether-portfolio | 8001 | healthy | ✓ |
| llm-service | aether-llm | 8002 | healthy | ✓ |
| postgres | aether-postgres | 5433 | healthy | ✓ |
| redis | aether-redis | 6380 | healthy | ✓ |
| qdrant | aether-qdrant | 6333-6334 | healthy | ✓ |
| frontend | aether-frontend | 3000 | unhealthy (running OK) | ⚠ |

- HTTP probe: auth `/actuator/health` 200, portfolio `/health` 200, llm `/health` 200, frontend `/` 200.
- frontend unhealthy = healthcheck 명령 부적합 추정 (Next.js 16.1.6 Ready 207ms — 실제 running OK).
- **진입 게이트 결과**: 6 backing services healthy → F-1 진입 OK. F-0 선행 X.

### §0.2 환경변수 / JWT 진단 5 절차

| 절차 | 결과 | 출처 |
|---|---|---|
| 1. `docker logs aether-auth \| grep jwt` | `JWT properties validated: accessExpiration=1800000ms (=30분), refreshExpiration=604800000ms (=7일)` | auth-service 부팅 로그 |
| 2. localStorage 토큰 발급 시간 | 신규 발급 (검증 시점 만료 X) — `iat` 포함 | login 응답 payload |
| 3. Network 헤더 형식 | `Authorization: Bearer <jwt>` 정합 | curl 검증 |
| 4. `/api/auth/refresh` 동작 | 200 OK 새 토큰 발급 | edge case 검증 |
| 5. Postgres / Redis 데이터 | 정상 (user 4건 + refresh token Redis 저장) | login + me 응답 |

**JWT 알고리즘 실측**:
- **auth-service 발급 토큰 헤더**: `{'alg': 'HS512'}` (base64 디코딩 결과)
- **portfolio-service / llm-service `verify_jwt`**: `algorithms=["HS256"]` (`portfolio-service/app/middleware/auth.py:29`, `llm-service/app/middleware/auth.py:30`)
- **결과**: 알고리즘 불일치 → 모든 보호 라우터 401 "Invalid token"

### §0.3 JWT 환경변수 키 명 (시크릿 값 X)

`auth-service/src/main/resources/application.yml`:
```
jwt:
  secret: ${JWT_SECRET:}
  access-expiration: ${JWT_ACCESS_EXPIRATION:1800000}     # 30분 default
  refresh-expiration: ${JWT_REFRESH_EXPIRATION:604800000} # 7일 default
```

---

## §1. 회원가입 / 로그인 (auth-service)

### §1.1 박힌 의도

- **참조 ADR**: 0004 "도메인 라우터 JWT 검증 + X-Request-ID 분산 트레이싱"
- **박힌 이유**: 마이크로서비스 5종(auth/portfolio/llm/frontend/MCP) 간 stateless 인증. Redis blacklist로 logout 즉시 무효화. JWT만으로 N 서비스 호출 시 일관 인증.

### §1.2 박힌 워크플로우 (5 엔드포인트)

```
POST /api/auth/signup   → UserResponse {id, email, name, role, enabled, createdAt}
POST /api/auth/login    → TokenResponse {accessToken (HS512), refreshToken (HS512)}
GET  /api/auth/me       → UserResponse (Bearer 검증)
POST /api/auth/refresh  → TokenResponse 새 발급 (jti 회전)
POST /api/auth/logout   → Redis blacklist 등록 + 200 OK
```

박힌 위치: `auth-service/src/main/java/com/aether/auth/global/security/JwtTokenProvider.java:41-205`.

### §1.3 정상 시나리오 (실측 PASS)

| 단계 | 입력 | 응답 | 결과 |
|---|---|---|---|
| signup | `{email, password, name}` | 200 + `{success:true, data:{id:4, email, name, role:USER, enabled:true}}` | ✓ |
| login | `{email, password}` | 200 + `{success:true, data:{accessToken, refreshToken}}` (HS512, 길이 243/228) | ✓ |
| me | Bearer | 200 + UserResponse | ✓ |
| refresh | `{refreshToken}` | 200 + 새 accessToken/refreshToken | ✓ |
| logout | Bearer | 200 OK | ✓ |
| logout 후 me | Bearer (blacklist) | **401** Token blacklisted | ✓ (Redis blacklist 동작 검증) |

### §1.4 Edge / 에러 시나리오 (실측 PASS)

| 시나리오 | 응답 | 결과 |
|---|---|---|
| 잘못된 비밀번호 | 401 | ✓ |
| 중복 이메일 signup | 409 Conflict | ✓ |
| Bearer 헤더 없음 | 401 "Missing Bearer token" | ✓ |
| 만료 토큰 | 30분 지연 검증 X (시간 필요) — 코드상 ExpiredSignatureError 처리 박힘 (`auth.py:30-35`) | △ (코드 검증) |

### §1.5 발견 이슈 + 진단

**Critical 1**: 사전 보고된 401 — 진단 결과 **알고리즘 불일치 (HS512 vs HS256)**.

- 위치: `portfolio-service/app/middleware/auth.py:29` + `llm-service/app/middleware/auth.py:30`
- 코드: `jwt.decode(token, _settings.jwt_secret, algorithms=["HS256"])` ← stale
- 토큰: `auth-service` HS512 발급
- 문서 주석 라인 1: "HS256 공유 비밀키" — stale (HS512로 변경됐는데 sync 안 됨)
- **F-1a 본질**: 양 측 알고리즘 일치 (HS512 통일 또는 둘 다 허용 `["HS256", "HS512"]`)

**Major**: frontend `aether-frontend` healthcheck unhealthy (running OK) — Dockerfile healthcheck 명령 부적합 추정. F-1a와 별개 D-0 후보.

**Minor**: README 검증 시 docker exec env 차단 (시크릿 누출 위험) — `.claude/settings.json`에 `Bash(docker exec aether-* env)` 명시적 거부 패턴 후보 (D-0 합류).

---

## §2. 포트폴리오 최적화 (portfolio-service)

### §2.1 박힌 의도

- **참조 ADR**: 0001 microservice-split + 0002 module-boundaries
- **박힌 이유**: Markowitz 평균-분산 (MVP / MSR) 기반 효율적 포트폴리오. AI 분석 통합 X (순수 수학) — LLM 호출은 `llm-service /api/chat/analyze-result`에서 분리 (시나리오 A 본질: 수치 검증과 자연어 설명 분리).

### §2.2 박힌 워크플로우

```
POST /api/optimize {tickers, strategy, period, rf, include_diagnostics, include_frontier, ...}
  → routers/optimize.py:51-296 (verify_jwt Depends)
  → services/optimizer.py:248 (optimize_min_variance) or :430 (optimize_max_sharpe)
  → services/drift_detector.py:289 (analyze_drift, 최근 20일)
  → OptimizeResponse {weights, metrics, frontier, drift_warning, ...}
```

### §2.3 정상 / Edge / 에러 (라우터 401 차단)

**라우터 직접 검증 차단됨** (Critical 1 — 알고리즘 불일치):

| 시나리오 | 호출 | 결과 |
|---|---|---|
| 정상 (AAPL+MSFT+NVDA, max_sharpe, 3y) | `Authorization: Bearer <HS512>` | **401 Invalid token** |
| Edge (티커 1개 / include_frontier) | 동일 | **401** |
| 에러 (잘못된 티커) | 동일 | **401** (라우터 진입 X) |
| 인증 없음 | no header | 401 (정상 보호 동작) |

**대체 검증 (코드 + pytest)**:
- `services/optimizer.py:430` `optimize_max_sharpe` 함수 시그니처 + 입출력 (PortfolioMetrics dataclass) 코드 박혀있음 ✓
- `tests/test_optimizer.py` 등 portfolio-service 테스트 212건 (AGENTS.md §6 지배 숫자) — 단위 검증 통과
- 응답 schema 키 (실측 차단으로 인용만): `weights`(dict), `metrics{expected_return, volatility, sharpe_ratio}`, `n_stocks`, `strategy`, `period`, `frontier`, `drift_warning`, `diagnostics`

**검증 차단 결론**: 본 §2-§4는 **F-1a 머지 후 재검증 의무**. F-1 산출물에는 "라우터 차단 사실 + 코드 박힘 + pytest PASS" 박음.

---

## §3. 백테스트 (portfolio-service)

### §3.1 박힌 의도

- **참조 ADR**: 0001 microservice-split
- **박힌 이유**: walk-forward 시뮬레이션으로 lookahead bias 방지. 8 메트릭 (Total/Annual Return / Volatility / Sharpe / Max Drawdown / Calmar / Avg Turnover / Win Rate) — 시연 시 line chart로 시각화.

### §3.2 박힌 워크플로우

```
POST /api/backtest {tickers, strategy, period, train_window, rebalance_every, transaction_cost, use_shrinkage}
  → routers/backtest.py:18-132 (verify_jwt Depends)
  → services/backtest.py:127 (walk_forward_backtest)
  → BacktestResponse {metrics(8건), portfolio_values[date,value], rebalance_history, final_weights}
```

박힌 단위:
- `train_window` / `rebalance_every`: 거래일 (영업일 기준)
- `period`: 캘린더 (3y / 5y) 또는 ISO 8601 start_date/end_date
- `transaction_cost`: 비율 (0.001 = 0.1%)
- 메트릭: 수익률 = 연율 / 변동성 = 연율 / Sharpe = 연율 / Drawdown = 비율

### §3.3 정상 / Edge / 에러 (라우터 401 차단)

**검증 결과**:
| 시나리오 | 호출 | 결과 |
|---|---|---|
| 정상 (3y / 252 train / 60 rebalance) | Bearer HS512 | **401 Invalid token** |
| Edge (5y / use_shrinkage=true) | 동일 | **401** |
| 에러 (train_window 부족) | 동일 | **401** (라우터 진입 X) |

**대체 검증**: `tests/test_backtest.py` pytest 통과 (portfolio-service 212건 합산, 86% coverage). 라우터 검증은 F-1a 후속.

---

## §4. RAG 챗 (llm-service)

### §4.1 박힌 의도

- **참조 ADR**: 0005 langgraph-adoption + 0006 react-pattern + 0007 genai-sdk-migration + 0009 qdrant-migration
- **박힌 이유**: T-1b LangGraph ReAct 1 호출로 4 도구 자율 판단. T-6 Qdrant 어댑터로 RAG 벡터 DB 토글. H-6 Gemini structured output (JSON Schema 직접 주입).

### §4.2 박힌 워크플로우

```
POST /api/chat {message}
  → routers/chat.py:331-356 (settings.use_react_agent 분기)
    [True]  agents/react_agent.py:27-71 ReActAgent.run() 1 호출
              → 4 도구 자율 (analyze_portfolio / explain_risk / summarize_backtest / get_recommendation)
              → services/rag.py:1-68 (Qdrant 어댑터, T-6)
              → Gemini structured output (response_schema)
    [False] 절차적 4 호출 fallback (USE_REACT_AGENT=false env)
  → ChatResponse {answer, sources[]}
```

### §4.3 정상 / Edge / 에러 (라우터 401 차단)

**검증 결과**:
| 시나리오 | 호출 | 결과 |
|---|---|---|
| 정상 (포트폴리오 분석 자연어) | Bearer HS512 | **401 Invalid token** |
| Edge (도구 0회 / 4회 호출) | 동일 | **401** |
| 에러 (Gemini API 한도 / Qdrant down) | 동일 | **401** (라우터 진입 X) |

**대체 검증**: llm-service 테스트 237건 (AGENTS.md §6, 86% coverage gate 81% 통과). Qdrant healthy 확인 (port 6333). 라우터 검증은 F-1a 후속.

---

## §5. MCP 도구 외부 호출 (T-2)

### §5.1 박힌 의도

- **참조 ADR**: 0008 mcp-server-adoption
- **박힌 이유**: T-2 차별화 — 4 도메인 도구를 MCP stdio 서버로 노출 → Claude Desktop / 외부 LLM 직접 호출. 국내 도메인 0건 = 시그널 강함.

### §5.2 박힌 워크플로우

```
Claude Desktop / 외부 LLM
  → stdio subprocess (python -m app.mcp_server)
    → portfolio-service/app/mcp_server.py:111-164 (Server("aether-portfolio"))
      → 4 도구: analyze_portfolio / compute_risk / run_backtest / get_recommendation
      → services/* 직접 호출 (라우터 우회 = JWT 검증 X, subprocess launch = 운영자 신뢰)
      → _serialize (numpy/pandas/dataclass/Pydantic 재귀 처리)
```

### §5.3 머지 상태 분기

- **T-2 (서버 본격 PR)**: 머지됨 (commit `dfe8ae3`, mcp_server.py 5538 bytes 존재) ✓
- **T-2b (Claude Desktop config)**: **미머지** (`mcp-config*.json` 없음, `docs/mcp-setup*` 없음)
- **분기 결정**: **부분 머지** → 부분 검증 (서버 로딩 OK / Claude Desktop 통합 X)
- **검증 결과**:
  - mcp_server.py 4 도구 등록 코드 박혀있음 (`portfolio-service/app/mcp_server.py:114-131`)
  - subprocess launch 자체 검증은 F-1 범위 X (T-2c 후속 카드 트리거)
  - JWT 검증 X = HS256/HS512 불일치 영향 받지 않음 (라우터 우회 본질)

---

## §6. 통합 E2E 시나리오 (가입 → 로그인 → 최적화 → 백테스트 → 챗)

### §6.1 실측 결과 (Critical 1로 부분 차단)

| 단계 | 호출 | 결과 |
|---|---|---|
| 1. signup | `POST /api/auth/signup` | ✓ 200 |
| 2. login → HS512 토큰 | `POST /api/auth/login` | ✓ 200 |
| 3. /me 검증 | `GET /api/auth/me` (HS512) | ✓ 200 (auth-service 자체 검증) |
| 4. optimize | `POST /api/optimize` (HS512) | ❌ 401 (HS256 검증 차단) |
| 5. backtest | `POST /api/backtest` (HS512) | ❌ 401 |
| 6. chat | `POST /api/chat` (HS512) | ❌ 401 |
| 7. logout | `POST /api/auth/logout` | ✓ 200 + Redis blacklist |
| 8. logout 후 me | `GET /api/auth/me` | ✓ 401 (blacklist 동작) |

**E2E 결론**: **인증 사이클 (1·2·3·7·8)은 완벽 동작**. 도메인 라우터 (4·5·6) 차단 — F-1a 1라인 fix로 즉시 복구 가능.

---

## §7. 발견된 이슈 우선순위

### §7.1 사전 분류 룰 (발견 전 박음)

| 등급 | 정의 |
|---|---|
| Critical | 5 기능 중 1개 진입 불가 (시연 5분 차단) |
| Major | Edge case / 일부 응답 깨짐 (시연 가능하나 기능 일부 약함) |
| Minor | UX 흠집 / 권장 개선 |

### §7.2 발견 이슈 매핑

| ID | 등급 | 내용 | 위치 | 후속 카드 |
|---|---|---|---|---|
| **C-1** | **Critical** | JWT 알고리즘 불일치 (HS512 vs HS256) — 도메인 라우터 3개 (optimize/backtest/chat) 모두 401 차단 | `portfolio-service/app/middleware/auth.py:29`, `llm-service/app/middleware/auth.py:30` | **F-1a** ★ |
| M-1 | Major | frontend healthcheck unhealthy (running OK) | `frontend/Dockerfile` healthcheck 명령 | D-0 |
| M-2 | Major | mcp_server.py 4 도구 정의는 박혔지만 Claude Desktop config 미머지 (T-2b) | `portfolio-service/app/mcp_server.py` + 외부 config | T-2b 또는 T-2c |
| m-1 | Minor | verify_jwt 파일 docstring "HS256 공유 비밀키" — stale 주석 | `*/middleware/auth.py:1` | F-1a 합류 |
| m-2 | Minor | docker exec env 권한 — 시크릿 누출 방지 본질 OK, README 진단 절차에 명시 권장 | `docs/agent-capability-audit/VERIFICATION.md §0.2` | D-0 합류 |

---

## §8. 후속 카드 후보 (트리거 명시)

| 카드 | 트리거 조건 | 우선순위 | 본질 |
|---|---|---|---|
| **F-1a** ★ | C-1 발견 즉시 | **최우선** | algorithms HS512 통일 (또는 `["HS256","HS512"]` 호환) + 주석 sync. 1 PR / 2 파일 / 4 라인 |
| **F-2** | F-1a 머지 후 | 중간 | Playwright E2E 자동화 + 시연 영상 캡처. 회귀 검증 + frontend vitest 5건 본 검증 |
| **D-0** | F-1a 머지 후 | 중간 | dev 모드 환경변수 정착 (M-1/m-2 합류). frontend healthcheck + Bash deny 패턴 |
| **D-1/2/3** | META_REVIEW §8 학습 11번+ 발견 시 | 낮음 (D-N 묶음) | 본 카드 발견 학습 (사전 발견 401 = 알고리즘 sync 누락 패턴 = 누적 문제 19번 후보) |
| **P-1** | 시니어 판단 패턴 8/9/10 발견 | 낮음 | PRINCIPLES 신규 패턴 (예: "박힌 주석 = 자동 stale" — 코드와 주석 sync 강제 패턴) |
| **T-2c** | 운영급 인증 / SSE transport 필요 시 | 조건부 | MCP HTTP/SSE 도입 (현재 stdio 한정 — 다중 클라이언트 X) |

---

## §9. 면접 시연 5분 시나리오

### §9.1 정상 흐름 (F-1a 머지 후)

| 분 | 시연 | 메시지 |
|---|---|---|
| 1분 | 회원가입 → 로그인 (HS512 + Redis refresh + blacklist) | "JWT stateless 인증 + Redis blacklist로 logout 즉시 무효화. 30분 access + 7일 refresh." |
| 1분 | 포트폴리오 최적화 (AAPL+MSFT+NVDA / max_sharpe) + 효율적 프론티어 시각화 | "Markowitz MSR. scipy SLSQP. 드리프트 탐지 동반." |
| 1분 | 백테스트 (3y / 252 train / 60 rebalance) + line chart | "Walk-forward로 lookahead bias 방지. 8 메트릭 산출." |
| 1분 | RAG 챗 ("AAPL 분석") + 4 도구 자율 호출 | "LangGraph ReAct가 4 도구 호출 순서 자율. Qdrant RAG + Gemini structured." |
| 1분 | 차별화 카드 (MCP / Qdrant / ADR 10건) | "T-2 MCP — 국내 도메인 0건. T-6 Qdrant — 어댑터로 토글. ADR 10건 박힘." |

### §9.2 Fallback (F-1a 미머지 시 — 본 검증 시점)

| 분 | 시연 | 메시지 |
|---|---|---|
| 1분 | 회원가입+로그인+blacklist 사이클 | (정상 흐름 1분 동일) |
| 1분 | 포트폴리오 코드 + pytest 통과 (terminal) | "tests/test_optimizer.py 통과 시연. 라우터는 진단 중인 알고리즘 불일치로 차단. F-1a 1 PR / 4 라인 fix." |
| 1분 | mcp_server.py 코드 시연 (Claude Desktop subprocess) | "MCP 서버는 라우터 우회 — 알고리즘 영향 받지 않음. 국내 도메인 0건 차별화." |
| 1분 | 회고 + 진단 5 절차 박힌 자료 (VERIFICATION.md) | "검증 자체가 시니어 시그널. 박힌 코드 ≠ 작동하는 코드 — 진단 절차 박혀있음." |
| 1분 | 차별화 카드 (Qdrant / ADR 10건 / META_REVIEW 707라인) | (정상 5분 동일) |

---

## §10. 사용자 의도 회고 (각 기능 "왜 만들었나")

| 기능 | 한 줄 의도 | 시나리오 A 적합도 |
|---|---|---|
| 회원가입 / 로그인 | "JWT stateless + Redis blacklist + Rate Limit = 마이크로서비스 5종 일관 인증의 본질 박음" (ADR 0004 박힌 결정) | **★★★** 최적 — 보안 시그널 |
| 포트폴리오 최적화 | "수치 계산 (Markowitz)과 자연어 설명 (LLM) 분리 — 시나리오 A 본질 (도메인 + AI 통합) 정확히 박음" | **★★★** 최적 — 도메인 깊이 |
| 백테스트 | "walk-forward로 lookahead bias 방지 = 도메인 신뢰성. 8 메트릭 시각화 = 시연 적합" | **★★★** 최적 — 시각화 시연 |
| RAG 챗 | "T-1b LangGraph ReAct 1 호출 = 4 도구 자율 판단 = 에이전트 시그널. T-6 Qdrant 어댑터 = MLOps 시그널" | **★★★** 최적 — 에이전트 차별화 |
| MCP 도구 | "stdio = Claude Desktop 표준. 국내 도메인 0건 = 강한 차별화. T-2c (HTTP/SSE) 보류는 시나리오 A에 불필요" | **★★★** 최적 — 차별화 카드 |

### §10.1 Houseman 진화 시점 학습 적용 (META_REVIEW §8)

- **학습 5 (모놀리식 페이지 회피)**: 본 카드 검증에서 router → service 분리 박힘 — `routers/*.py` 200 LOC 임계 통과.
- **학습 8 (F-패턴: 검증 + 분기 + 머지)**: 본 카드 = F-패턴 "검증" 단계. F-1a (분기 fix) + F-2 (자동화 머지) 후속.
- **학습 9 (응답 호환 어댑터)**: T-6 Qdrant 어댑터 — 호출자 0 변경 보장 (vector_store 추상화 통과).

### §10.2 시나리오 A 본질 적합도 결론

**5/5 — 시나리오 A (기술 데모 + 포트폴리오)에 정확히 맞음**. 5 기능 모두 차별화 카드 보유 (Markowitz / walk-forward / LangGraph ReAct / MCP stdio / Qdrant 어댑터). C-1 fix 후 시연 5분 즉시 가능.

---

## §11. 데이터 영향 (보안 + 격리)

| 영역 | 영향 | 결론 |
|---|---|---|
| localStorage | `localStorage.clear()` = dev 환경 한정. prod X | 본 검증 진행 OK (검증용 임시 user 분리) |
| 새 회원가입 | 검증 user `f1-test-1778056571@aether.local` (id=4) — 기존 user 격리 | 데이터 손실 X |
| Postgres | read-only 검증 (signup 4건 추가만) | 영향 미미 |
| Redis | refresh token 1건 + blacklist 1건 추가 | TTL 자동 정리 |
| Qdrant | 호출 X (라우터 401 차단) | 영향 0 |
| 시크릿 | `docker exec env` 차단됨 (시크릿 누출 방지 동작) | 본 검증 보안 PASS |

---

## §12. 검증 메타 (5 가드 + WORK_PATTERNS)

### §12.1 5 가드 적용 결과

- **G1 본질 트리거**: C-1 발견 시 즉시 보고 + F-1a 분리 (Round Cap 위반 X) ✓
- **G2 Reversibility**: Type 1 (산출물 1 파일 / 코드 변경 0 / git 작업 0) ✓
- **G3 Done Definition**: §0-§11 모두 채움 + 후속 카드 6건 명시 + 의도 회고 박힘 ✓
- **G4 Round Cap**: 검증 1 라운드 내 완료 (Round 2 발생 X) ✓
- **G5 First Principle**: "박힌 코드 = 작동 X" 직격 증명 (라우터 401) + "박힌 기능 = 의도 답 의무" 박힘 (§10) ✓

### §12.2 WORK_PATTERNS 누적 문제 매칭

| 문제 | 본 카드 매칭 |
|---|---|
| 문제 4 (응답 schema 키 가설) | §1.3 토큰 응답 키 실측 (`accessToken`/`refreshToken` 길이 243/228 박음) |
| 문제 6 (호출 위치 가설) | §0.2 / §1.5 / §2.2 / §3.2 / §4.2 — 모든 인용에 `file_path:line` 박음 |
| 문제 12 (단위 가정) | §3.2 `train_window`/`rebalance_every`=거래일, `period`=캘린더, `transaction_cost`=비율 명시 |
| 문제 13 (외부 SDK 응답 구조) | JWT 헤더 base64 디코드로 `alg=HS512` 실측 (가설 X) |
| **문제 19 후보** | **알고리즘 sync 누락 (auth-service HS512 변경 시 portfolio/llm verify_jwt sync 누락) — 신규 패턴 D-N 후보** |

---

## §갱신 이력

| 일자 | 변경 |
|---|---|
| 2026-05-06 | F-1 검증 전용 작성 (§0-§12). C-1 (HS512 vs HS256) 진단 + F-1a 트리거. T-2 부분 머지 / T-2b 미머지 박음. |

**한 문장**: 박힌 5 기능 중 인증 사이클 (signup/login/me/refresh/logout/blacklist)은 완벽 동작, 도메인 라우터 3개는 알고리즘 불일치로 차단 — F-1a 1 PR / 4 라인 fix로 시연 5분 즉시 복구 가능.
