# TEST_GUIDE — Aether 5 기능 사용자 시연 가이드 (TG-1)

> **본질**: Aether 5 기능 사용자 시연 가이드. Claude Code가 4 서비스 코드 직접 정독 후 페이지 흐름 + API 흐름 + 시나리오 작성. 사용자 페이지 시연 검증 + 면접 시연 5분 자료 정착.
> **카드**: TG-1 (사용자 시연 가이드 / ADR X)
> **작성일**: 2026-05-07
> **본문 영역**: 5 기능 × 3 시나리오 (정상 + Edge + 에러) = 15 시나리오 + 사전 정착 + 진단 흐름 + 면접 시연 5분
> **다음 카드**: I-1 (면접 답변 시뮬 / KARPATHY_MAPPING §6 + INTERVIEW.md + 본 자료 인용)

---

## §1 사전 정착 의무

### §1.1 docker-compose 정착

```bash
cd /Users/kuka/Aether
docker compose up -d
docker compose ps  # 6 서비스 health check 영역
```

**정착 의무 영역** (6 서비스):
- `aether-postgres` (5432 / authdb)
- `aether-redis` (6379 / blacklist + cache)
- `aether-qdrant` (6333 / RAG aether_knowledge / 36 chunks (D-7 / ADR 0017) / 3072차원)
- `aether-auth` (8003 / Spring Boot)
- `aether-portfolio` (8001 / FastAPI)
- `aether-llm` (8002 / FastAPI)

### §1.2 health check 검증

```bash
curl http://localhost:8003/health  # auth — Spring Boot
curl http://localhost:8001/health  # portfolio — FastAPI
curl http://localhost:8002/health  # llm — FastAPI
```

각 응답: `{"status": "healthy"}` 또는 `{"status": "ok"}` 정착.

### §1.3 환경변수 정착

`.env` 파일 영역 (docker-compose.yml + portfolio/llm config):

```bash
GEMINI_API_KEY=...           # Gemini 2.0 Flash / 임베딩 영역
JWT_SECRET=...               # auth-service ↔ python 서비스 공유 (HS512 / 64 bytes 이상)
DATABASE_URL=postgresql+psycopg2://...
REDIS_URL=redis://aether-redis:6379
QDRANT_URL=http://aether-qdrant:6333
VECTOR_STORE=qdrant          # default (T-6b / ADR 0016)
```

### §1.4 검증용 임시 user (VERIFICATION.md §11 인용)

```
이메일: f1-test-1778056571@aether.local (id=4)
비밀번호: TestPass123!
```

또는 신규 가입 (signup → login 정착).

### §1.5 frontend 정착

```bash
cd frontend
npm install
npm run dev  # localhost:3000
```

브라우저: `http://localhost:3000` 진입.

### §1.6 사전 정착 체크리스트 (6 항목)

- [ ] docker compose 6 서비스 health check 통과
- [ ] frontend localhost:3000 접속 / Sparkles 로고 표시
- [ ] 환경변수 6건 정착 (.env)
- [ ] localStorage 정리 (브라우저 DevTools / Application / Storage)
- [ ] 검증용 user 정착 (signup 또는 기존 user)
- [ ] Qdrant aether_knowledge 컬렉션 36 chunks 검증 (D-7 / ADR 0017)

---

## §2 5 기능 시연 시나리오

### §2.1 회원가입 + 로그인 (auth-service)

**페이지 흐름** (frontend):
- `/signup` (frontend/src/app/signup/page.tsx:10-83) — name / email / password 입력 → signUpApi 호출
- `/login` (frontend/src/app/login/page.tsx:11-65) — email / password → loginApi → setTokens → getMe → setUser → `/dashboard`

**API 흐름** (auth-service / Spring Boot):
- `POST /api/auth/signup` (AuthController.java:29-37) → 201 + UserResponse
- `POST /api/auth/login` (AuthController.java:40-46) → 200 + TokenResponse (accessToken HS512 30분 / refreshToken 7일)
- `POST /api/auth/refresh` (AuthController.java:49-55) → 새 TokenResponse + reuse 감지
- `POST /api/auth/logout` (AuthController.java:58-66) → Redis blacklist 등록 (token TTL)
- `GET /api/auth/me` (AuthController.java:76-82) → UserResponse

**정상 시나리오**:
1. `/signup` → name="시연" / email="demo@aether.local" / password="DemoPass123!" → "계정이 생성되었습니다" → 1.5초 후 `/login`
2. `/login` → 동일 email / password → `/dashboard` 진입
3. `/dashboard` 우상단 사용자 정보 / 로그아웃 버튼 표시
4. 로그아웃 → 다시 토큰 호출 시 401 (Redis blacklist)

**Edge**:
- 이메일 형식 X (`demo@`) → 400 + "Invalid email format"
- 비밀번호 8자 미만 → 400 + "Password too short"
- 중복 가입 → 409 + "Email already exists"

**에러**:
- 401 (잘못된 비밀번호) → "로그인에 실패했습니다" 토스트
- 500 (auth-service 다운) → frontend 에러 표시
- Redis 연결 실패 → blacklist 영역 로그 / 시간 지연

---

### §2.2 포트폴리오 최적화 (portfolio-service)

**페이지 흐름** (frontend):
- `/dashboard/optimize` (frontend/src/app/dashboard/optimize/page.tsx:7-42) — useOptimize hook + OptimizeForm + ResultDisplay
- selectedTickers / startDate / endDate / strategy 입력

**API 흐름** (portfolio-service / FastAPI):
- `POST /api/optimize` (optimize.py:38-58 / verify_jwt 의무) → OptimizeResponse
  - tickers (배열) / strategy ("min_variance" / "max_sharpe") / 기간
  - 부분 실패 허용 (실패 티커 → failed_tickers / warnings)
  - 드리프트 탐지 (최근 20일 vs 과거)
- `optimizer.py` — Markowitz / Sharpe / scipy SLSQP
- `efficient_frontier()` — 프론티어 차트 영역

**정상 시나리오**:
1. `/dashboard/optimize` 진입 → 티커 5개 입력 (AAPL / GOOGL / NVDA / TSLA / META)
2. 기간 선택 (default 5y) → strategy = "max_sharpe"
3. 최적화 버튼 → ResultDisplay 표시 (5 자산 비중 + Sharpe + 프론티어 차트)
4. AI 분석 (analyze_portfolio_tool) 자동 호출 → 자연어 설명 표시

**Edge**:
- 티커 1개만 → 400 "At least 2 valid tickers"
- 티커 100개 → 처리 가능 (성능 영역 / scipy SLSQP)
- 무효 티커 (`XXXXX`) → invalid_tickers 응답 / 부분 실패

**에러**:
- yfinance 데이터 부족 (신규 상장 / 1개월 미만) → 400 + 데이터 부족 메시지
- SLSQP 수렴 실패 (특이 covariance) → 500 + 진단 정보

---

### §2.3 백테스트 (portfolio-service)

**페이지 흐름** (frontend):
- `/dashboard/backtest` — selectedTickers / period / train_window / rebalance_every 입력

**API 흐름** (portfolio-service):
- `POST /api/backtest` (backtest.py:18-30 / verify_jwt 의무) → BacktestResponse
  - walk_forward_backtest (시간순 분리 / 미래 정보 X)
  - 거래비용 반영
  - 8 메트릭 (CAGR / Sharpe / MDD / Volatility 등)

**정상 시나리오**:
1. `/dashboard/backtest` → 티커 5개 + period="5y" + train_window=252 + rebalance_every=21
2. 백테스트 버튼 → walk-forward 실행 (학습 252일 → 21일 리밸런싱)
3. 결과: 누적 수익률 line chart + 8 메트릭 표
4. 리밸런싱 영역 표시 (RebalanceRecord 배열)

**Edge**:
- 기간 1일 → 400 "Insufficient data"
- 기간 10년 → 처리 가능 (성능 영역)
- 미래 날짜 (`2030-01-01`) → 400 또는 데이터 부족 영역

**에러**:
- yfinance 데이터 부족 → 400 + 진단 메시지
- 메모리 부족 (큰 covariance) → 500

---

### §2.4 RAG 챗 (llm-service)

**페이지 흐름** (frontend):
- `/dashboard/chat` (frontend/src/app/dashboard/chat/page.tsx:10-100) — ChatMessage[] + sendChatMessage + sources

**API 흐름** (llm-service / FastAPI):
- `POST /api/chat` (chat.py / ReAct 1 호출) — extract_tickers / 5 도구 자율 판단
  - 일반 질문 → search_knowledge_base (Qdrant RAG)
  - 티커 포함 → 도메인 분석 도구 (analyze / risk / backtest / recommendation)
- `POST /api/chat/stream` (D-6 / ADR 0019) — SSE 영역
  - LangGraph astream_events v2 (react_agent.py:52-76)
  - token / tool_start / tool_end 이벤트
  - format `data: {json}\n\n`

**ReAct 5 도구** (react_agent.py:19-25):
- `analyze_portfolio_tool` → portfolio_analysis 영역
- `explain_risk_tool` → risk_analysis 영역
- `summarize_backtest_tool` → backtest_analysis 영역
- `get_recommendation_tool` → recommendation 영역
- `search_knowledge_base` (D-5 / ADR 0018) → knowledge_sources 영역

**정상 시나리오**:
1. 일반 질문 (티커 X): "Sharpe ratio가 뭐야?" → search_knowledge_base 자동 호출 → Qdrant 검색 → 답변 + sources 표시
2. 티커 분석: "AAPL TSLA 분석해줘" → analyze_portfolio_tool + explain_risk_tool 자율 호출 → 통합 답변
3. 도메인 지식: "포트폴리오 이론 설명" → portfolio_theory.md 청크 검색 → 인용
4. 통합: "GOOGL NVDA 백테스트하고 위험 분석" → summarize_backtest + explain_risk 동시 호출

**Edge**:
- 빈 메시지 → 400 + sanitize_user_input 차단
- 매우 긴 메시지 (10000+ 글자) → 토큰 한도 / context 영역 한정
- 한국어 + 영어 섞임 → ReAct 모델 자율 처리 (Gemini 2.0 Flash 다국어)

**에러**:
- Gemini API 실패 (key 만료 / quota) → 500 + "AI 응답을 받지 못했습니다"
- Qdrant 연결 실패 → search_knowledge_base 도구 에러 / fallback 영역
- ReAct 무한 루프 (recursion_limit) → 500 + 디버그 본문

---

### §2.5 MCP (Claude Desktop 통합)

**시연 영역** (Claude Desktop 외부 통합):
- Claude Desktop config 파일: `~/Library/Application Support/Claude/claude_desktop_config.json`
- portfolio-service stdio MCP server (mcp_server.py)

**MCP 4 도구** (mcp_server.py:29-52):
- `analyze_portfolio` (AnalyzePortfolioInput / mu / cov / rf)
- `compute_risk` (ComputeRiskInput / weights / mu / cov / n_simulations)
- `run_backtest` (RunBacktestInput / returns / asset_names / dates / strategy)
- `get_recommendation` (GetRecommendationInput / recent_returns / historical_returns)

**정상 시나리오**:
1. Claude Desktop config 정착 (mcp-config.json / portfolio-service stdio 명령)
2. Claude Desktop 진입 → "내 포트폴리오 분석해줘" 자연어 질문
3. Claude가 자동으로 `analyze_portfolio` 도구 호출 → mu / cov 추정 → 결과 표시
4. X-Request-ID forward 검증 (logs / aether-portfolio MCP 영역)

**Edge**:
- 인증 토큰 영역: MCP stdio = 라우터 우회 / verify_jwt 미적용 영역 (T-2c 진단 결과)
- 다중 호출 (analyze → risk → recommendation) → 자동 체이닝

**에러**:
- subprocess 실패 (MCP server 시작 실패) → Claude Desktop 에러 / config 검증
- Pydantic schema 영역 (잘못된 mu / cov 타입) → 400 + 진단 본문

---

## §3 진단 흐름 (VERIFICATION.md §0 인용)

### §3.1 logs 진단

```bash
docker logs aether-auth --tail 50      # Spring Boot
docker logs aether-portfolio --tail 50 # FastAPI
docker logs aether-llm --tail 50       # FastAPI
docker logs aether-postgres --tail 50  # DB
docker logs aether-redis --tail 50     # blacklist
docker logs aether-qdrant --tail 50    # RAG
```

### §3.2 DB 진단 (Postgres)

```bash
docker exec -it aether-postgres psql -U aether -d authdb
\dt  # 테이블 영역 (users / refresh_tokens 등)
SELECT id, email, created_at FROM users LIMIT 10;
\q
```

### §3.3 Redis 진단 (blacklist)

```bash
docker exec -it aether-redis redis-cli
KEYS *blacklist*  # blacklist 영역
KEYS *rate_limit*  # rate limit 영역
EXIT
```

### §3.4 Qdrant 진단 (RAG)

```bash
curl http://localhost:6333/collections                    # 컬렉션 영역
curl http://localhost:6333/collections/aether_knowledge   # 36 chunks 영역 (D-7 / ADR 0017)
```

### §3.5 진단 5 절차 (VERIFICATION.md §0 인용)

1. health check 6 서비스 통과 검증
2. logs 6 서비스 에러 영역 진단
3. DB / Redis / Qdrant 데이터 영역 진단
4. 환경변수 (.env) 영역 진단 (GEMINI_API_KEY / JWT_SECRET)
5. frontend 브라우저 DevTools (Network / Console / localStorage) 진단

---

## §4 면접 시연 5분 시나리오 (META_REVIEW.md §9 인용)

### §4.1 시연 흐름 (5분 / 1분 × 5 영역)

| 분 | 시연 영역 | 차별화 영역 |
|----|----------|-----------|
| 1분 | 회원가입 + 로그인 + 로그아웃 + blacklist 검증 | JWT HS512 / Redis blacklist / refresh reuse 감지 |
| 1분 | 포트폴리오 최적화 + 프론티어 차트 | Markowitz + Sharpe / scipy SLSQP / 부분 실패 허용 / 드리프트 탐지 |
| 1분 | 백테스트 line chart + 8 메트릭 | walk-forward / 시간순 분리 / 거래비용 반영 |
| 1분 | RAG 챗 5 도구 자율 판단 + sources 표시 | LangGraph ReAct / Gemini 2.0 Flash / Qdrant 3072차원 / SSE streaming |
| 1분 | MCP Claude Desktop 통합 + 차별화 카드 | T-2 stdio 4 도구 / 양면 정책 15 ADR / D-7 grid search |

### §4.2 차별화 영역 3건 (META_REVIEW §9 인용)

- **T-2 MCP**: portfolio-service stdio 4 도구 / Claude Desktop 외부 통합 / 라우터 우회 검증
- **T-6b Qdrant**: chromadb fallback / _EMBED_DIM 768→3072 정정 사례 / Skill Issue 본능 직접 사례
- **양면 정책 15 ADR**: 정착 7 + 보류 4 (T-3 / D-1 / D-9 / CL-D) + 메타 4 + 정리 1 / 결정 근거 추적 / 6개월 후 본인 답 가능

### §4.3 본질 답변 (꼬리 질문 영역)

| 꼬리 질문 | 본질 답 |
|-----------|---------|
| "왜 5 도구?" | 도메인 분리 (rag_tools ↔ portfolio_tools) + 자율 판단 본능 / 영역 분리 X = AI Agent 본질 |
| "왜 SSE? WebSocket 안 쓴 이유?" | 단방향 충분 / WebSocket = 시나리오 B 트리거 (양방향 의무) |
| "왜 Multi-Agent 안 쓴 이유?" | T-3 보류 (ADR 0010) / 시나리오 A 5 도구 자율 판단 충족 / Houseman Phase 7-12 도메인 검증 트리거 |
| "왜 ragas 안 쓴 이유?" | D-8 PRE-CHECK 분기 2 / 자체 4 메트릭 + 의존성 0 / 시나리오 B 진입 시 ragas 트리거 |

---

## §5 자가 점검 체크리스트

### §5.1 사전 정착 (6 항목 / §1.6 인용)

- [ ] docker compose 6 서비스 health check 통과
- [ ] frontend localhost:3000 접속
- [ ] 환경변수 6건 정착
- [ ] localStorage 정리
- [ ] 검증용 user 정착
- [ ] Qdrant aether_knowledge 36 chunks (D-7 / ADR 0017)

### §5.2 5 기능 정상 흐름 (5 항목)

- [ ] §2.1 signup → login → /me → logout → blacklist 검증
- [ ] §2.2 optimize 5 티커 → max_sharpe 비중 + 프론티어
- [ ] §2.3 backtest walk-forward → line chart + 8 메트릭
- [ ] §2.4 chat 일반 질문 + 티커 분석 + sources 표시
- [ ] §2.5 MCP Claude Desktop 4 도구 호출

### §5.3 진단 흐름 (3 항목)

- [ ] logs 6 서비스 에러 영역 0건
- [ ] DB / Redis / Qdrant 데이터 영역 정착
- [ ] 환경변수 + frontend DevTools 정착

### §5.4 면접 시연 5분 (5 항목)

- [ ] §4.1 시연 흐름 5 영역 1분씩 진행 가능
- [ ] §4.2 차별화 영역 3건 (T-2 / T-6b / 양면 정책 15 ADR) 인용 가능
- [ ] §4.3 꼬리 질문 4건 본질 답 가능
- [ ] META_REVIEW §9 본문 인용 가능
- [ ] AGENTS.md §7 지배 숫자 본문 인용 가능

---

> **한 문장**: TG-1 = Aether 5 기능 사용자 시연 가이드 (15 시나리오 + 사전 정착 + 진단 흐름 + 면접 5분). Claude Code 코드 직접 정독 / 실측 본문 (파일:라인) 명시. 다음 진입 = I-1 (면접 답변 시뮬).
