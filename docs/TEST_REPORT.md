# TEST_REPORT — Aether 자동 시연 결과 (TG-2 / Playwright MCP)

> **본질**: docs/TEST_GUIDE.md §2 5 기능 × 3 시나리오 = 15 시나리오 자동 시연 결과 보고서. Playwright MCP (Microsoft 공식 / accessibility tree 기반) 통합 영역. 사용자 직접 시연 의무 X / 자동 검증.
> **카드**: TG-2 (Playwright MCP 통합 + 사전 정착 영역) / ADR X
> **상태**: **사전 정착 정착 / 시연 결과 영역 = 다음 세션 의무** (TG-2b 별도 카드 영역)
> **작성일**: 2026-05-08
> **인용 자료**: docs/TEST_GUIDE.md (TG-1 / 5 기능 시연 가이드) + .mcp.json (project scope)

---

## §0 본 보고서 영역 본질

본 카드 = **사전 정착 영역**:
- `.mcp.json` 신규 (project scope / Playwright MCP 등록)
- 본 보고서 골격 작성 (15 시나리오 영역 정착)
- AGENTS.md §7 TG-2 baseline 행 추가

본 카드 영역 X (TG-2b 영역):
- Playwright MCP 도구 호출 시연 (Claude Code 재시작 의무)
- docker compose 6 서비스 healthy 정착 시연
- 15 시나리오 실측 결과 본문 갱신
- 발견 에러 영역 / 디버그 카드 트리거 명시

**다음 세션 진입 절차** (TG-2b):
1. `docker compose up -d` + `docker compose ps` 6 서비스 healthy 검증
2. Claude Code 재시작 → `claude mcp list` 영역 playwright 등록 검증
3. `npx playwright install` (브라우저 binary 정착)
4. 본 보고서 §1 + §2 영역 실측 결과 갱신

---

## §1 사전 검증 영역 (TG-2b 시점 정착 의무)

### §1.1 환경 정착

| 영역 | 검증 명령 | 의무 |
|---|---|---|
| Node.js | `node --version` | v18+ |
| docker compose | `docker compose ps` | 6 서비스 healthy |
| Playwright MCP | `claude mcp list` | playwright 등록 영역 |
| 브라우저 binary | `npx playwright install` | 정착 |
| frontend | `curl http://localhost:3000` | 200 OK |

### §1.2 6 서비스 health check (TEST_GUIDE.md §1.2 인용)

| 서비스 | 포트 | health check 명령 |
|---|---|---|
| auth-service | 8003 | `curl http://localhost:8003/health` |
| portfolio-service | 8001 | `curl http://localhost:8001/health` |
| llm-service | 8002 | `curl http://localhost:8002/health` |
| postgres | 5432 | docker compose ps |
| redis | 6379 | docker compose ps |
| qdrant | 6333 | docker compose ps |

### §1.3 검증용 user 정착

VERIFICATION.md §11 인용:
- 이메일: `f1-test-1778056571@aether.local` (id=4)
- 비밀번호: `TestPass123!`
- 또는 신규 가입 (signup → login 정착)

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

## §5 사전 정착 vs TG-2b 영역 분리

### 본 카드 (TG-2 / 사전 정착)

| 의무 | 정착 | 위치 |
|---|---|---|
| .mcp.json 신규 (Playwright MCP) | 정착 | `.mcp.json` (project scope / git tracked) |
| 본 보고서 골격 작성 | 정착 | `docs/TEST_REPORT.md` |
| AGENTS.md §7 baseline 행 | 정착 | AGENTS.md §7 |
| docs/README.md §3 + §7 갱신 | 정착 | docs/README.md |

### 다음 세션 진입 카드 (TG-2b / 시연 영역)

| 의무 | 정착 | 위치 |
|---|---|---|
| docker compose 6 서비스 healthy | 시연 진입 사전 의무 | docker compose up -d |
| Claude Code 재시작 + Playwright MCP 도구 사용 | 시연 진입 사전 의무 | claude mcp list 검증 |
| 12 시나리오 자동 시연 (auth + optimize + backtest + chat) | 시연 본문 | TEST_GUIDE.md §2 인용 |
| MCP 영역 사용자 수동 검증 | 보류 정착 / 사용자 영역 | TEST_GUIDE.md §2.5 |
| 본 보고서 §1 + §2 + §3 실측 결과 갱신 | 시연 본문 | 본 보고서 |

---

> **한 문장**: TG-2 = Playwright MCP 사전 정착 영역 (.mcp.json + 본 보고서 골격 + AGENTS §7) / TG-2b = 시연 영역 (Claude Code 재시작 + docker 6 서비스 + 12 시나리오 자동 시연 + 1 영역 사용자 수동 검증). 본 보고서 = TG-2b 시점 §1 + §2 + §3 실측 결과 갱신 영역.
