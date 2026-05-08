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

### TG-2c (시연 영역 / 다음 세션 의무)
- **선행 의무**: Claude Code 재시작 → 본 인스턴스 영역 Playwright MCP 도구 schema 인지
- 12 시나리오 자동 시연 (auth + optimize + backtest + chat / Playwright MCP `browser_navigate` / `browser_click` / `browser_fill` 등 도구 영역)
- MCP §2.5 = 보류 (Playwright = 브라우저 영역 / Claude Desktop 영역 X / 사용자 수동 검증)
- 본 보고서 §2 + §3 + §4 실측 결과 갱신
- 발견 에러 영역 = 디버그 카드 (DBG-N) 트리거 명시

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

### §2.1 회원가입 + 로그인 (auth-service / TEST_GUIDE.md §2.1)

| # | 시나리오 | 영역 | 결과 |
|---|---|---|---|
| 1 | 정상 — signup → login → /me → refresh → logout → blacklist 검증 | JWT HS512 + Redis blacklist | 미시연 |
| 2 | Edge — 이메일 형식 / 비밀번호 길이 / 중복 가입 | 입력 검증 | 미시연 |
| 3 | 에러 — 401 Unauthorized / 500 / Redis 연결 실패 | 에러 응답 | 미시연 |

### §2.2 포트폴리오 최적화 (portfolio-service / TEST_GUIDE.md §2.2)

| # | 시나리오 | 영역 | 결과 |
|---|---|---|---|
| 1 | 정상 — Markowitz max_sharpe / 효율적 프론티어 + Sharpe ratio | cvxopt + 연율화 | 미시연 |
| 2 | Edge — 종목 1개 / 종목 ↑↑ / covariance singular | 부분 실패 허용 | 미시연 |
| 3 | 에러 — 가격 데이터 부재 / external API 타임아웃 | 에러 응답 | 미시연 |

### §2.3 백테스트 (portfolio-service / TEST_GUIDE.md §2.3)

| # | 시나리오 | 영역 | 결과 |
|---|---|---|---|
| 1 | 정상 — walk-forward / 8 메트릭 / 리밸런싱 영역 | 시간순 분리 | 미시연 |
| 2 | Edge — train_window ↑ / rebalance_every 1일 / transaction_cost 0 | 임계 영역 | 미시연 |
| 3 | 에러 — Insufficient data (min_required 미달) / 종목 부재 | 에러 응답 | 미시연 |

### §2.4 RAG 챗 (llm-service / TEST_GUIDE.md §2.4)

| # | 시나리오 | 영역 | 결과 |
|---|---|---|---|
| 1 | 정상 — 5 도구 자율 판단 (ReAct) + sources 표시 + SSE 토큰 | LangGraph + Qdrant | 미시연 |
| 2 | Edge — tickers 1개 (RAG fallback) / SSE 타임아웃 30초 / 한글 + 영문 혼합 | fallback + 영역 | 미시연 |
| 3 | 에러 — Gemini quota / Qdrant 연결 실패 / 도구 호출 실패 | 에러 응답 | 미시연 |

### §2.5 MCP (Claude Desktop / TEST_GUIDE.md §2.5)

**보류 명시**: Playwright = 브라우저 자동화 영역 / Claude Desktop 시연 X. 본 §= 사용자 수동 검증 의무 (TEST_GUIDE.md §2.5 인용).

| # | 시나리오 | 영역 | 결과 |
|---|---|---|---|
| 1 | 정상 — Claude Desktop ↔ portfolio-service stdio 4 도구 | MCP server | 사용자 수동 검증 |
| 2 | Edge — schema validation 실패 / argument 부재 | Pydantic | 사용자 수동 검증 |
| 3 | 에러 — portfolio-service 미시작 / 절대경로 stale | 에러 응답 | 사용자 수동 검증 |

---

## §3 결과 종합 영역 (TG-2b 시점 정착 의무)

### §3.1 시나리오 통계 (TG-2b 시점 갱신)

| 분류 | 영역 | 본 카드 시점 |
|---|---|---|
| 통과 시나리오 | 0 / 12 (auth + optimize + backtest + chat) | 미시연 |
| 실패 시나리오 | 0 / 12 | 미시연 |
| 보류 시나리오 | 3 / 3 (MCP / Claude Desktop) | 보류 정착 |

### §3.2 발견 에러 영역 (TG-2b 시점 갱신 의무)

본 §= 시연 시점 발견 에러 영역 본문. 본 카드 시점 = 미시연 영역 / 영역 X.

| # | 영역 | 본문 | 디버그 카드 트리거 |
|---|---|---|---|
| - | (TG-2b 시점 정착) | - | - |

### §3.3 디버그 카드 트리거 영역

발견 에러 영역에 따라 다음 카드 영역 분기:
- 에러 0건 → I-1 (면접 답변 시뮬) 직접 진입
- 에러 1-3건 → 디버그 카드 (DBG-N) 진입 후 I-1
- 에러 ↑ → 시나리오 분리 의무 (디버그 카드 N건 분리)

---

## §4 면접 시연 5분 자동 검증 (META_REVIEW §9 / TEST_GUIDE §4 인용)

### §4.1 면접 시연 5분 흐름

TEST_GUIDE.md §4 인용 — 면접 시연 5분 영역:
- 1분 — signup + login (HS512 + Redis blacklist)
- 1분 — optimize (Markowitz + Sharpe)
- 1분 — backtest (walk-forward + 8 메트릭)
- 1분 — chat (RAG + ReAct + SSE 토큰)
- 1분 — MCP 시연 (Claude Desktop / 사용자 수동)

### §4.2 자동 검증 본질

자동 시연 흐름 = 면접 시점 시연 가능 영역 검증:
- TG-2b 시점 12 / 12 통과 = 면접 시연 5분 영역 검증 정착
- 1건 이상 실패 = 디버그 카드 트리거 (면접 시연 시점 영역 의무)

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

### TG-2c (시연 영역 / 다음 세션 의무)

**선행 의무**: Claude Code 재시작 → 본 인스턴스 영역 Playwright MCP 도구 schema (`browser_navigate` / `browser_click` / `browser_fill` / `browser_snapshot` 등) 인지.

| 의무 | 정착 | 위치 |
|---|---|---|
| Claude Code 재시작 + Playwright MCP 도구 schema 인지 | TG-2c 사전 의무 | claude CLI 재시작 |
| 12 시나리오 자동 시연 (auth + optimize + backtest + chat) | TG-2c 본문 | TEST_GUIDE.md §2 인용 |
| MCP §2.5 = 보류 (사용자 수동 검증) | 보류 정착 | TEST_GUIDE.md §2.5 |
| 본 보고서 §2 + §3 + §4 실측 결과 갱신 | TG-2c 본문 | 본 보고서 |
| 발견 에러 영역 = 디버그 카드 (DBG-N) 트리거 | TG-2c 본문 | 본 보고서 §3 |

### 본 카드 위험 시나리오 #6 발견 영역 — Playwright MCP 인지 X (본 인스턴스)

**현상**: claude mcp list 영역 = `playwright: npx @playwright/mcp@latest - ✓ Connected` 정착 (외부 CLI 영역). 단 본 Claude Code 인스턴스 영역 = ToolSearch 영역 = "+playwright" 검색 0건 (도구 schema 영역 미인지).

**사유**: 본 인스턴스 = TG-2 PR #42 머지 시점 이후 시작 영역 / .mcp.json 등록 시점 X / 본 인스턴스 시작 시점 = .mcp.json 미존재 영역 → 본 인스턴스 영역 도구 schema 영역 미인지.

**정착**: Claude Code 재시작 → 본 .mcp.json 영역 인지 → Playwright MCP 도구 schema 영역 즉시 사용 가능 영역. TG-2c 카드 진입 의무.

---

> **한 문장**: TG-2 = .mcp.json + 본 보고서 골격 / TG-2b = 환경 세팅 영역 정착 (docker 7 healthy + Playwright Chromium + 검증용 user id=15 / §1 실측 결과) / TG-2c = 시연 영역 (Claude Code 재시작 후 12 시나리오 자동 시연 + MCP §2.5 사용자 수동 검증 + §2 + §3 + §4 실측 갱신).
