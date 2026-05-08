# TEST_REPORT — Aether 자동 시연 결과 (TG-2 / TG-2b / Playwright MCP)

> **본질**: docs/TEST_GUIDE.md §2 5 기능 × 3 시나리오 = 15 시나리오 자동 시연 결과 보고서. Playwright MCP (Microsoft 공식 / accessibility tree 기반) 통합 영역. 사용자 직접 시연 의무 X / 자동 검증.
> **카드**: TG-2 (사전 정착 / .mcp.json + 본 골격) + TG-2b (환경 세팅 / docker 7 서비스 + 브라우저 binary + 검증용 user) + TG-2c (시연 영역 / 다음 세션 의무) / ADR X
> **상태**: **§1 환경 세팅 영역 정착 (TG-2b 시점 실측) / §2 시연 결과 영역 = TG-2c 의무** (Playwright MCP 도구 schema 본 세션 영역 X / Claude Code 재시작 의무)
> **갱신일**: 2026-05-08 (TG-2b 시점)
> **인용 자료**: docs/TEST_GUIDE.md (TG-1 / 5 기능 시연 가이드) + .mcp.json (project scope)

---

## §0 본 보고서 영역 본질

### TG-2 (사전 정착 / 머지 정착 PR #42)
- `.mcp.json` 신규 (project scope / Playwright MCP 등록)
- 본 보고서 골격 작성 (15 시나리오 영역 정착)
- AGENTS.md §7 TG-2 baseline 행 추가

### TG-2b (환경 세팅 / 본 PR / 실측 결과 §1 갱신)
- docker compose 7 서비스 healthy 검증 (실측 / §1.2)
- API health 4 endpoint 검증 (실측 / §1.2)
- Playwright Chromium binary 정착 (실측 / §1.1)
- 검증용 user 정착 (실측 / §1.3 / id=15 / signup + login HS512 + accessToken 30분)
- 본 보고서 §0 + §1 + §5 갱신
- AGENTS.md §7 TG-2b baseline 행 추가

### TG-2c (자동 시연 / 본 PR / puppeteer MCP 영역)
- **plan 분기 3 변경**: Playwright MCP 본 인스턴스 미인지 → puppeteer MCP 영역 (본 인스턴스 7 도구 정착)
- 4 정상 시나리오 puppeteer 시연 — §2.1 ✓ + §2.2 ✗ DBG-1 + §2.3 ✗ DBG-1 + §2.4 ✓
- Edge + 에러 시나리오 API curl 영역 통합 — §2.1 Edge 2/3 통과 + 에러 2/2 통과 + Edge-1 ✗ DBG-2
- MCP §2.5 = 보류 (사용자 수동 검증 / Claude Desktop 영역)
- 본 보고서 §2 + §3 + §4 실측 결과 갱신 (6 통과 + 3 실패 + 9 보류)
- 발견 에러 영역 = **DBG-1 (yfinance) + DBG-2 (이메일 형식)** 트리거

---

## §1 사전 검증 영역 (TG-2b 실측 결과 정착)

### §1.1 환경 정착 (실측)

| 영역 | 검증 명령 | 의무 | 실측 결과 |
|---|---|---|---|
| Node.js | `node --version` | v18+ | **v25.1.0** ✓ |
| docker daemon | `docker info` | Server / Containers | **Server / Containers 10 / Running 7** ✓ |
| docker compose | `docker compose ps` | 7 서비스 healthy | **7 healthy / frontend health: starting → 200 OK** ✓ |
| Playwright MCP | `claude mcp list` | playwright 영역 등록 | **playwright: npx @playwright/mcp@latest - ✓ Connected** (단 본 인스턴스 도구 schema 영역 = 재시작 의무 / TG-2c 분리) |
| 브라우저 binary | `npx playwright install chromium` | 정착 | **Chrome Headless Shell 147.0.7727.15 / chromium-headless-shell v1217 / 96.6 MiB** ✓ |
| frontend | `curl http://localhost:3000` | 200 OK | **200** ✓ |

### §1.2 7 서비스 health check 실측 (AGENTS.md §2 인용 / docker-compose.yml 7 서비스)

| 서비스 | 포트 (호스트→컨테이너) | docker compose ps | API health 검증 |
|---|---|---|---|
| postgres | 5433 → 5432 | **healthy** ✓ | (docker check) |
| redis | 6380 → 6379 | **healthy** ✓ | (docker check) |
| qdrant | 6333-6334 | **healthy** ✓ | (docker check) |
| portfolio-service | 8001 | **healthy** ✓ | `{"status":"healthy","service":"Portfolio Service","version":"0.1.0"}` |
| llm-service | 8002 | **healthy** ✓ | `{"status":"healthy","checks":{"api_key":"ok","vectorstore":"ok","portfolio_service":"ok"}}` |
| auth-service | 8003 | **healthy** ✓ | `{"status":"UP"}` (Spring Boot Actuator) |
| frontend | 3000 | health: starting → **HTTP 200** ✓ | (Next.js 15) |

**llm-service 영역 정착**: D-2 운영급 결정 (ADR 0012) — `api_key` 영역 (Gemini lifespan startup failfast) + `vectorstore` 영역 (Qdrant 영역 정착) + `portfolio_service` 영역 (httpx event_hooks forward) 모두 ok.

### §1.3 검증용 user 실측 정착

기존 VERIFICATION.md §11 user (`f1-test-1778056571@aether.local` / id=4) 영역 = postgres volume stale 영역 / 인증 실패 (A001 / 이메일 또는 비밀번호 미일치). TG-2b 시점 신규 user 정착:

| 영역 | 본문 |
|---|---|
| 이메일 | `tg2b-1778235563@aether.local` |
| ID | 15 |
| 비밀번호 | `TestPass123!` |
| 이름 | TG2B Test User |
| signup endpoint | `POST /api/auth/signup` → `{"success":true,"data":{"id":15, ..., "createdAt":"2026-05-08T10:19:23"}}` ✓ |
| login endpoint | `POST /api/auth/login` → `{"accessToken":"eyJhbGciOiJIUzUxMiJ9...", "refreshToken":"eyJhbGciOiJIUzUxMiJ9...", "tokenType":"Bearer", "expiresIn":1800}` ✓ |
| JWT alg 검증 | accessToken header `eyJhbGciOiJIUzUxMiJ9` = base64 decode → `{"alg":"HS512"}` ✓ (F-1a / ADR 0004 v2 일관성) |
| accessToken TTL | 1800초 (30분) |
| refreshToken TTL | 7일 (TG-2c 시점 시연 영역) |

**signup 영역 발견**: TG-1 시점 본문 (TEST_GUIDE.md §2.1) 인용 영역 = nickname 필드 / 실측 = `name` 필드 의무 (Spring Boot @Valid SignUpRequest 영역). C002 ("이름은 필수입니다") 영역 발견 영역.

---

## §2 자동 시연 결과 영역 (15 시나리오 / TG-2b 시점 갱신 의무)

> **본 §**: TEST_GUIDE.md §2 인용 / Playwright MCP 자동 조작 결과 본문. 본 카드 시점 = 골격 영역 / TG-2b 시점 실측 결과 갱신.

> **본 §실측 시점**: TG-2c (puppeteer MCP 영역 — plan 분기 3 변경 / Playwright MCP 도구 schema 본 인스턴스 미인지 / puppeteer = 본 인스턴스 7 도구 영역 정착). 시연 영역 분리: **정상 시나리오 = puppeteer 브라우저 시연** / **Edge + 에러 = API curl 영역 통합** (시간 효율 영역).

### §2.1 회원가입 + 로그인 (auth-service / TEST_GUIDE.md §2.1)

| # | 시나리오 | 영역 | 결과 (TG-2c 실측) |
|---|---|---|---|
| 1 | 정상 — signup → login → /dashboard → logout → /login redirect | JWT HS512 + httpOnly cookie | **✓ 통과** (puppeteer / `tg2c-1778251644@aether.local` id=17 / TG-2b 시점 id=15 영역 영역 X — 본 시점 신규 user) |
| 2.1 | Edge — 잘못된 이메일 형식 (`foo@bar`) | 입력 검증 | **✗ 실패 / DBG-2 트리거** — id=17 정상 signup 영역 (이메일 형식 검증 영역 X / RFC 5322 영역 의무) |
| 2.2 | Edge — 짧은 비밀번호 (7자) | 입력 검증 | ✓ 통과 — C002 ("비밀번호는 8자 이상 100자 이하") |
| 2.3 | Edge — 중복 가입 (동일 이메일) | 입력 검증 | ✓ 통과 — U002 ("이미 사용 중인 이메일") |
| 3.1 | 에러 — 잘못된 비밀번호 → 401 | 인증 실패 | ✓ 통과 — A001 ("이메일 또는 비밀번호가 일치하지 않습니다") |
| 3.2 | 에러 — name 필드 누락 → 422 | 필드 검증 | ✓ 통과 — C002 ("이름은 필수입니다") |
| 3.3 | 에러 — Redis 연결 실패 | blacklist 영역 | 보류 — Redis 영역 stop 의무 / 시연 X |

**§2.1 정착 영역**:
- signup 영역 = `name` 필드 의무 (TEST_GUIDE.md §2.1 본문 = `nickname` 영역 stale / TG-2b 시점 발견 영역 일관성)
- JWT 영역 = httpOnly cookie 영역 (frontend localStorage 영역 X / D-2 운영급 / XSS 회피 영역)
- logout button 영역 = 헤더 aria-label="로그아웃" 영역 정착

### §2.2 포트폴리오 최적화 (portfolio-service / TEST_GUIDE.md §2.2)

| # | 시나리오 | 영역 | 결과 (TG-2c 실측) |
|---|---|---|---|
| 1 | 정상 — Markowitz max_sharpe / AAPL+MSFT+GOOGL / 2024-01-01~2024-12-31 | cvxopt + Sharpe | **✗ 실패 / DBG-1 트리거** — `Optimization failed: Insufficient valid tickers: 0 succeeded, minimum 2 required. Failed tickers: ['AAPL', 'MSFT', 'GOOGL']` |
| 2 | Edge — 종목 1개 / covariance singular | 부분 실패 영역 | 보류 — 정상 영역 실패 영역 / Edge 영역 시연 영역 X |
| 3 | 에러 — 가격 데이터 부재 | 에러 응답 | 보류 — DBG-1 영역 일관성 |

**§2.2 발견 영역**: portfolio-service logs 영역 — `1 Failed download` × 3 영역 (yfinance 영역 = Yahoo Finance API 차단 영역 / 네트워크 영역). DBG-1 (yfinance 영역 영역 진단) 트리거 영역.

### §2.3 백테스트 (portfolio-service / TEST_GUIDE.md §2.3)

| # | 시나리오 | 영역 | 결과 (TG-2c 실측) |
|---|---|---|---|
| 1 | 정상 — walk-forward / max_sharpe / AAPL+MSFT+GOOGL / 2024-01-01~2024-12-31 | 8 메트릭 | **✗ 실패 / DBG-1 동일 영역** — `Invalid tickers: ['AAPL', 'MSFT', 'GOOGL']` |
| 2 | Edge — 기간 1일 / 미래 날짜 | 임계 영역 | 보류 — 정상 영역 실패 영역 |
| 3 | 에러 — 데이터 부족 (min_required 미달) | 에러 응답 | 보류 — DBG-1 영역 일관성 |

**§2.3 발견 영역**: §2.2 동일 yfinance 영역 / DBG-1 영역 일관성. 본 영역 = portfolio-service 영역 외부 의존 영역 (yfinance) / 단일 디버그 카드 영역.

### §2.4 RAG 챗 (llm-service / TEST_GUIDE.md §2.4)

| # | 시나리오 | 영역 | 결과 (TG-2c 실측) |
|---|---|---|---|
| 1 | 정상 — 도메인 질문 (티커 X / "샤프 비율이 무엇인가요?") | LangGraph + search_knowledge_base + SSE | **✓ 통과** (15초 영역 응답 완료 / SSE 토큰 영역 정상 / 📚 참고 영역 = sources 표시 / D-5 + ADR 0018 일관성) |
| 2 | Edge — 빈 메시지 / 긴 메시지 / 한국어+영어 섞임 | fallback + 영역 | 보류 — 정상 영역 통과 영역 / Edge 영역 시간 영역 한정 |
| 3 | 에러 — Gemini quota / Qdrant 연결 실패 | 에러 응답 | 보류 — 외부 영역 stop 의무 / 시연 X |

**§2.4 정착 영역**:
- ReAct 영역 = `search_knowledge_base` 도구 자율 판단 영역 (5 도구 영역 / D-5 + ADR 0018)
- SSE 영역 = 응답 영역 정상 (token + tool events / D-6 + ADR 0019)
- 답변 영역 = 샤프 비율 영역 도메인 답변 + 공식 (Sharpe = (Rp - Rf) / σp) + 해석 (1.0/2.0/3.0 임계 영역)
- 📚 sources 영역 = "샤프 비율 (Sharpe Ratio), 성과 평가 지표, 포트폴리오 최적화 전략" (Qdrant 영역 정상)

### §2.5 MCP (Claude Desktop / TEST_GUIDE.md §2.5)

**보류 명시**: Playwright = 브라우저 자동화 영역 / Claude Desktop 시연 X. 본 §= 사용자 수동 검증 의무 (TEST_GUIDE.md §2.5 인용).

| # | 시나리오 | 영역 | 결과 |
|---|---|---|---|
| 1 | 정상 — Claude Desktop ↔ portfolio-service stdio 4 도구 | MCP server | 사용자 수동 검증 |
| 2 | Edge — schema validation 실패 / argument 부재 | Pydantic | 사용자 수동 검증 |
| 3 | 에러 — portfolio-service 미시작 / 절대경로 stale | 에러 응답 | 사용자 수동 검증 |

---

## §3 결과 종합 영역 (TG-2c 실측 정착)

### §3.1 시나리오 통계 (TG-2c 실측)

| 분류 | 영역 | 결과 |
|---|---|---|
| 통과 시나리오 | §2.1 정상 + §2.1 Edge-2 + §2.1 Edge-3 + §2.1 Error-1 + §2.1 Error-2 + §2.4 정상 | **6 통과** |
| 실패 시나리오 | §2.1 Edge-1 (DBG-2) + §2.2 정상 (DBG-1) + §2.3 정상 (DBG-1) | **3 실패** |
| 보류 시나리오 | §2.1 Error-3 (Redis stop) + §2.2 Edge/Error + §2.3 Edge/Error + §2.4 Edge/Error + §2.5 MCP 3 | **9 보류** |

### §3.2 발견 에러 영역 (TG-2c 실측)

| # | 영역 | 본문 | 디버그 카드 트리거 |
|---|---|---|---|
| 1 | portfolio-service yfinance 영역 | `Optimization failed: Insufficient valid tickers: 0 succeeded` + `1 Failed download` × 3 (AAPL/MSFT/GOOGL) — Yahoo Finance API 영역 차단 / 네트워크 영역. §2.2 + §2.3 동일 영역. | **DBG-1** (yfinance 영역 진단 / fallback data provider 영역 검토) |
| 2 | auth-service 이메일 형식 검증 영역 | `foo@bar` 영역 = signup 정상 (id=17) — RFC 5322 영역 검증 X / Spring Boot @Email annotation 영역 X 추정 | **DBG-2** (이메일 검증 영역 추가 / @Email + 정규식 영역 검토) |

### §3.3 디버그 카드 트리거 영역

발견 에러 영역 2건 → **디버그 카드 2건 분리 의무**:
- **DBG-1**: portfolio-service yfinance fallback 영역 (data_provider 영역 / fixture 영역 / mock 영역 검토)
- **DBG-2**: auth-service 이메일 형식 영역 (Spring @Email annotation 영역 / SignUpRequest 영역)

다음 진입 영역:
- DBG-1 + DBG-2 분리 진입 → §2.2 + §2.3 + §2.1 Edge-1 시연 영역 정착
- 또는 I-1 (면접 답변 시뮬) 직접 진입 — 본 영역 발견 영역 = 면접 영역에서 발견 + 디버그 영역 본질 시그널 영역 (PRINCIPLES 패턴 / WORK_PATTERNS 검수 13 영역 일관성)

---

## §4 면접 시연 5분 자동 검증 (TG-2c 실측)

### §4.1 면접 시연 5분 흐름 영역 검증

TEST_GUIDE.md §4 인용 — 면접 시연 5분 영역 / TG-2c 실측 결과:

| 분 | 영역 | TG-2c 실측 | 면접 시연 가능 영역 |
|---|---|---|---|
| 1분 | signup + login (HS512 + httpOnly cookie) | ✓ 통과 | ✓ 시연 가능 |
| 1분 | optimize (Markowitz + Sharpe) | ✗ DBG-1 (yfinance 영역) | ✗ 시연 X (DBG-1 정착 의무) |
| 1분 | backtest (walk-forward + 8 메트릭) | ✗ DBG-1 (yfinance 영역) | ✗ 시연 X (DBG-1 정착 의무) |
| 1분 | chat (RAG + ReAct + SSE 토큰 + sources) | ✓ 통과 | ✓ 시연 가능 |
| 1분 | MCP (Claude Desktop / 사용자 수동) | 보류 | 사용자 수동 검증 의무 |

### §4.2 면접 시연 영역 영역 (TG-2c 시점)

**시연 가능 영역 (2/5)**: signup + login + RAG chat — 본 영역 = 면접 시점 시연 가능 영역.

**시연 X 영역 (2/5 / DBG-1 의무)**: optimize + backtest — 외부 영역 (yfinance) 의존 영역 / 시연 시점 영역 의무. DBG-1 정착 후 시연 가능.

**사용자 수동 영역 (1/5)**: MCP 영역 — Claude Desktop ↔ portfolio-service stdio 4 도구 / 사용자 영역 의무 (Playwright / puppeteer 영역 X).

**면접 시연 5분 영역 정착 의무**:
1. DBG-1 (yfinance fallback 영역) 정착 → §2.2 + §2.3 시연 가능 영역
2. DBG-2 (이메일 형식 영역) 정착 → §2.1 Edge 영역 일관성
3. I-1 진입 — 본 보고서 + DIFFERENTIATION + TEST_GUIDE + KARPATHY §6 영역 통합

---

## §5 카드 분리 영역 (TG-2 / TG-2b / TG-2c)

### TG-2 (사전 정착 / PR #42 머지 정착)

| 의무 | 정착 | 위치 |
|---|---|---|
| .mcp.json 신규 (Playwright MCP) | ✓ 정착 | `.mcp.json` (project scope / git tracked) |
| 본 보고서 골격 작성 (15 시나리오 영역) | ✓ 정착 | `docs/TEST_REPORT.md` |
| AGENTS.md §7 TG-2 baseline 행 | ✓ 정착 | AGENTS.md §7 |
| docs/README.md §3 + §7 갱신 | ✓ 정착 | docs/README.md |

### TG-2b (환경 세팅 / 본 PR / 실측 결과 §1 갱신)

| 의무 | 정착 | 위치 |
|---|---|---|
| docker daemon 검증 (사용자 Docker Desktop 시작 의무) | ✓ 정착 | docker info — Server / Containers 10 |
| docker compose 7 서비스 healthy 영역 | ✓ 정착 | docker compose ps — postgres/redis/qdrant/portfolio/llm/auth/frontend 모두 healthy |
| API health 4 endpoint 정상 | ✓ 정착 | auth UP / portfolio + llm healthy / frontend HTTP 200 |
| Playwright Chromium binary | ✓ 정착 | `~/Library/Caches/ms-playwright/chromium_headless_shell-1217` |
| 검증용 user (id=15) 정착 + JWT HS512 검증 | ✓ 정착 | `tg2b-1778235563@aether.local` / accessToken HS512 + 30분 TTL |
| 본 보고서 §0 + §1 + §5 갱신 | ✓ 정착 | 본 §|
| AGENTS.md §7 TG-2b baseline 행 | ✓ 정착 | AGENTS.md §7 |

### TG-2c (시연 영역 / 본 PR / puppeteer MCP 영역)

**plan 분기 3 변경 영역**: Playwright MCP 도구 schema 본 인스턴스 영역 미인지 (claude mcp list = Connected 영역 / ToolSearch +playwright = 0건) → puppeteer MCP 영역 영역 전환 (본 인스턴스 영역 puppeteer 7 도구 영역 정착 / `puppeteer_navigate` / `puppeteer_click` / `puppeteer_fill` / `puppeteer_evaluate` 등).

| 의무 | 정착 | 위치 |
|---|---|---|
| puppeteer MCP 도구 schema 인지 | ✓ 정착 | ToolSearch +puppeteer 영역 7 도구 |
| 4 정상 시나리오 (§2.1-§2.4) puppeteer 시연 | ✓ 정착 — 2 통과 (§2.1 + §2.4) / 2 실패 (§2.2 + §2.3 / DBG-1) | 본 §2 |
| Edge + 에러 시나리오 API curl 영역 통합 | ✓ 정착 — §2.1 Edge 3 + 에러 2 / 보류 1 | 본 §2 |
| MCP §2.5 = 보류 (사용자 수동 검증) | ✓ 보류 정착 | 본 §2.5 |
| 본 보고서 §2 + §3 + §4 실측 결과 갱신 | ✓ 정착 | 본 §|
| 발견 에러 영역 = 디버그 카드 트리거 | ✓ 정착 — **DBG-1 + DBG-2** | 본 §3.2 |
| AGENTS.md §7 TG-2c baseline 행 | ✓ 정착 | AGENTS.md §7 |

### 분기 결정 영역 (TG-2c plan 분기 3 변경 영역)

**현상 영역**: Playwright MCP 외부 CLI 영역 = `claude mcp list` Connected 영역 정착 / 단 본 Claude Code 인스턴스 영역 = `ToolSearch +playwright` 0건 영역 (도구 schema 미인지).

**사유 영역**: 본 인스턴스 = TG-2 PR #42 머지 시점 이전 시작 영역 / .mcp.json 등록 시점 X / 본 인스턴스 영역 도구 schema 영역 미인지. Claude Code 재시작 영역 = 본 conversation 영역 종료 영역.

**정착 영역**: 사용자 결정 = plan 분기 3 변경 (옵션 3 / Playwright → puppeteer) — 본 인스턴스 영역 puppeteer MCP 도구 schema 영역 정착 영역 / 시연 진입 가능. plan G1 영역 = 도구 schema 영역 인지 영역 / 본 영역 정착 후 시연 진입.

### 다음 진입 영역 (TG-2c 머지 후)

| 카드 | 진입 자료 | 본질 |
|---|---|---|
| **DBG-1** | 본 §3.2 #1 + portfolio-service logs + data_provider 영역 | yfinance 영역 fallback 정착 (fixture / mock / 다른 data provider 영역 검토) |
| **DBG-2** | 본 §3.2 #2 + auth-service SignUpRequest 영역 | 이메일 형식 검증 영역 (Spring @Email annotation 영역 추가) |
| **I-1** | 본 보고서 + DIFFERENTIATION + TEST_GUIDE + KARPATHY §6 + INTERVIEW + Top 10 자료 | 면접 답변 시뮬 (TG-2c 결과 인용 — 발견 영역 영역 = 디버그 영역 본질 시그널 영역) |

---

> **한 문장**: TG-2 = .mcp.json + 본 보고서 골격 / TG-2b = 환경 세팅 (docker 7 healthy + Playwright Chromium + 검증용 user) / TG-2c = puppeteer 자동 시연 (4 정상 시나리오 시연 + Edge/에러 API curl 통합 — 6 통과 + 3 실패 + 9 보류 / DBG-1 yfinance + DBG-2 이메일 형식 영역 트리거).
