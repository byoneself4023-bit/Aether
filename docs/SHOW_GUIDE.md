# SHOW_GUIDE — Aether 수동 시연 가이드 (브라우저 / 15분)

> **본질**: 사용자 직접 브라우저 시연 가이드 (Step 1-8 / 일상 + 면접 시점 통합).
> **카드**: SHOW_GUIDE (자료 카드 / ADR X / 카드 누적 35 → 36)
> **작성일**: 2026-05-10
> **선행 카드**: STALE-FIX (PR #57 / 3f80945) — 거짓 본문 정정 후
> **본 시점 정확 본문**: Phase 1 + AETHER-END + STALE-FIX 정착 후 / 거짓 X / stale X / 면접 답변 시점 안전

---

## §0 사전 준비 (5분 / 1회만)

```bash
cd /Users/kuka/Aether
docker compose down -v   # volume 전체 삭제 (id=1 시작)
docker compose up -d
sleep 30
docker compose ps        # 7 서비스 healthy 확인
```

7 서비스 = postgres / redis / qdrant / auth / portfolio / llm / frontend

브라우저: <http://localhost:3000>

면접 직전 = 동일 흐름 (cleanup → 재시작 → id=1 깨끗).

---

## §1 Step 1: 메인 진입 (10초)

브라우저 → <http://localhost:3000>

확인: 메인 페이지 / "회원가입" 버튼 표시.

---

## §2 Step 2: 회원가입 (1분)

1. "회원가입" 클릭 → /signup 진입
2. 입력:
   - 이름: `Demo`
   - 이메일: `demo20260510@aether.local` (오늘 날짜 / 중복 회피)
   - 비밀번호: `DemoPass123!` (대문자+소문자+숫자+특수문자 의무)
3. "계정 생성" 클릭

확인: 성공 메시지 → /login 자동 이동.

### Edge — 잘못된 이메일 (DBG-2 검증)

1. /signup 다시 진입
2. 이메일 = `foo@bar` (TLD 없음) 입력 → 가입 버튼
3. 400 에러 확인 (DBG-2 / @Email + @Pattern 이중 검증 / TLD ≥ 2자 의무)

### Edge — 짧은 비밀번호

1. /signup 다시 진입
2. 비밀번호 = `short` (8자 미만) 입력 → 가입 버튼
3. 400 에러 ("Password too short")

---

## §3 Step 3: 로그인 (30초)

1. 동일 이메일 + 비밀번호 입력
2. "로그인" 클릭

확인: /dashboard 자동 이동 / 헤더에 사용자 이름 표시.

### 에러 — 잘못된 비밀번호

1. 비밀번호 = `wrongpass` 입력 → 로그인 버튼
2. "로그인에 실패했습니다" 토스트 확인

---

## §4 Step 4: 포트폴리오 최적화 (2분)

1. 좌측 메뉴 → "최적화" 클릭 → /dashboard/optimize 진입
2. 티커: `AAPL,MSFT,GOOGL`
3. 기간: default (3년)
4. 전략: `max_sharpe`
5. "최적화 실행" 클릭 → 5-10초 대기

확인 (TG-2d 결과 일치):

- 기대 수익률 ≈ 45.98% (연율)
- 변동성 ≈ 27.54%
- Sharpe Ratio ≈ **1.5971**
- 최적 비중: GOOGL ~89.47% + AAPL ~10.53% + MSFT ~0%
- 효율적 프론티어 차트 표시
- AI 분석 자연어 설명 표시

### Edge — 티커 1개

1. 티커 1개만 선택 → 최적화 버튼 클릭
2. 사일런트 차단 (frontend 검증 / `useOptimize.ts:36` / `length < 2` return) — 결과 표시 X / 에러 메시지 X

> 비교: backtest 티커 1개 = `useBacktest.ts:36-38` setError UI 메시지 표시 (optimize와 동작 다름)

### Edge — 무효 티커

1. 티커 = `XXXXX` 입력 → 최적화 버튼
2. 부분 실패 응답 (`invalid_tickers` 표시)

> yfinance 차단 시 = 자동 fallback (DBG-1 / FixtureProvider / 결과 다를 수 있음 / 정상)

---

## §5 Step 5: 백테스트 (3분)

1. 좌측 메뉴 → "백테스트" 클릭 → /dashboard/backtest 진입
2. 티커: `AAPL,MSFT,GOOGL`
3. 기간: 5년 default (16 리밸런싱 결과 매칭)
4. rebalance_every: 63 (분기 / default) — train_window는 backend default 사용 (UI 노출 X)
5. "백테스트 실행" 클릭 → 10-20초 대기

확인 (TG-2d 결과 일치):

- 누적 수익률 ≈ **155.74%**
- 연환산 ≈ 26.61%
- Sharpe ≈ 0.9051
- MDD ≈ 30.34%
- 연환산 변동성 ≈ 27.19%
- 칼마 ≈ 0.8771
- 승률 ≈ 53.84%
- 리밸런싱 16회 (5년 / 63일 분기)
- 누적 수익률 line chart 표시

### Edge — 짧은 기간

1. 기간 = 1일 입력 → 백테스트 버튼
2. 400 에러 ("Insufficient data")

### Edge — 미래 날짜

1. start_date = `2030-01-01` 입력 → 백테스트 버튼
2. 400 에러 또는 데이터 부족 메시지

---

## §6 Step 6: RAG 채팅 (3분)

1. 좌측 메뉴 → "AI 채팅" 클릭 → /dashboard/chat 진입
2. 입력창: `샤프 비율이 무엇인가요?`
3. "전송" 또는 Enter → 15-20초 대기

확인:

- 답변 표시 (Sharpe 공식 + 해석)
- 📚 참고 sources 표시 (1건 이상)

### 추가 질문 (안전 영역 우선)

| 질문 | 동작 | 시연 안전 |
|---|---|---|
| `포트폴리오 이론 설명` | RAG 직접 / portfolio_theory.md 청크 인용 | ✓ sources ≥ 1 보장 |
| `Markowitz 모델이 뭐죠?` | RAG 직접 / sources ≥ 1 보장 | ✓ 안전 |
| `AAPL TSLA 분석해줘` | extract_tickers ≥2 / analyze 분기 / sources 0 가능 | ◐ 결과 보장 X |
| `GOOGL NVDA 백테스트하고 위험 분석` | 동일 / sources 0 가능 | ◐ 결과 보장 X |

> 시연 안전 추천: 일반 질문 (샤프 / 포트폴리오 이론 / Markowitz) 우선 / 티커 질문은 sources 0 가능성 명시

### Edge — 빈 메시지

1. 빈 메시지 입력 → 전송
2. 400 에러 (sanitize_user_input 차단)

> 본 페이지 = sync POST /api/chat 사용 (SSE 우회 / 면접 시점 답변 §C 주의)

---

## §7 Step 7: 로그아웃 (30초)

1. 헤더 우상단 → 로그아웃 아이콘 클릭 (사용자 이름 옆 / LogOut 아이콘 / 텍스트 X / aria-label="로그아웃" / hover 시 빨간색)

확인: /login 자동 이동 / 헤더 사용자 정보 사라짐 / 토큰 Redis blacklist 등록.

---

## §8 Step 8: MCP 검증 (선택 / 사용자 수동)

1. Claude Desktop config 정착:
   - 파일: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - portfolio-service stdio MCP server 등록 (mcp_server.py)
2. Claude Desktop 진입
3. 입력: `내 포트폴리오 AAPL+MSFT+GOOGL 분석해줘`
4. MCP 자동 호출 → 결과 표시 (analyze_portfolio / compute_risk / run_backtest / get_recommendation)

---

## §9 면접 시연 5분 (Step 2-7 압축)

| 분 | 페이지 | 핵심 답변 |
|---|---|---|
| 1 | signup → login → dashboard → logout | "JWT HS512 + Redis blacklist 정착 / DBG-2 이메일 검증 강화" |
| 2 | optimize | "Markowitz scipy SLSQP / Sharpe 1.5971 / DBG-1 fallback 정착" |
| 3 | backtest | "walk-forward / 8 메트릭 / 16 리밸런싱" |
| 4 | chat | "RAG + 답변 + sources / Qdrant 36 chunks / ReAct 5 도구 (env 의무)" |
| 5 | 답변 | "양면 정책 19 ADR / 카드 누적 35 / 시나리오 A 종료 → Houseman 진입" |

---

## §C 안전 확인 사항 (면접 답변 시점 주의)

> 본 §C = Claude Code 코드 직접 정독 후 거짓/stale 발견 정정. 본 답변 의무.

| 질문 | 진실 답변 |
|---|---|
| "JWT 어디 저장?" | localStorage (aether-auth zustand persist + aether-refresh-token) — httpOnly cookie X |
| "스트리밍?" | 백엔드 /api/chat/stream SSE 정착 / 단 frontend chat = sync POST 사용 (별도 curl 시연 가능) |
| "ReAct 5 도구 자율?" | 코드 정착 / 단 default RAG_FALLBACK_DIRECT=true → query_with_llm 직접 / env 변경 시 ReAct |
| "Markowitz solver?" | scipy SLSQP (optimizer.py:309,383,488,558) — cvxopt X |
| "RAG 메트릭 4건?" | relevance@k / recall@k / LLM-as-judge / faithfulness — D-8 / ADR 0015 |
| "ADR 몇 개?" | 양면 정책 19 ADR (0011-0029) — 정착 11 + 보류 4 + 메타 4 + 정리 1 |
| "Qdrant chunks?" | 36 chunks (D-7 grid search 후 / chunk_size=500/overlap=300 / T-6b baseline 26) |
| "카드 누적?" | 35 카드 마감 (32 → AETHER-END 머지 후 → 33 RETROSPECTIVE → 34 README-UPDATE → 35 STALE-FIX) |
| "리밸런싱 16회?" | 5년 기간 + rebalance_every=63 (분기) default → ~16회 정확 |

---

## §D 시연 X 영역 (면접 답변 시점 명시 의무)

본 영역 = 코드 정착 / 단 시연 X / 인용 시 "별도 검증 의무" 명시:

| 영역 | 정착 | 시연 X 사유 | 별도 검증 |
|---|---|---|---|
| F-1a 리프레시 reuse 감지 | JwtTokenProvider:166-182 | signup→login→logout만 시연 / 공격 흐름 X | refresh 토큰 2회 사용 attack 흐름 의무 |
| D-6 SSE 스트리밍 | 백엔드 /api/chat/stream | frontend chat = sync POST 사용 | curl <http://localhost:8002/api/chat/stream> -H ... -d '...' |
| D-5 ReAct 5 도구 자율 | chat.py:331-356 | RAG_FALLBACK_DIRECT=true (default) → ReAct 우회 | env 변경 (RAG_FALLBACK_DIRECT=false) 또는 ≥2 티커 질문 |
| D-7 chunking grid search | scripts/grid_search_chunking.py | 오프라인 스크립트만 | python -m scripts.grid_search_chunking |
| D-8 RAG 4 메트릭 평가 | scripts/eval_rag.py | 오프라인 스크립트만 | python -m scripts.eval_rag --no-llm-judge |
| T-1a + T-1b LangGraph | llm-service/app/agents/ | 옵티마이즈 페이지 무관 / chat 영역만 | chat 페이지 시연으로 일부 검증 |

---

## §E 에러 발생 시 디버그

### Step 1: 어느 서비스 죽었는지 확인

```bash
docker compose ps
# STATUS = unhealthy / Exited 발견
```

### Step 2: logs 확인

```bash
docker compose logs auth-service --tail 50
docker compose logs portfolio-service --tail 50
docker compose logs llm-service --tail 50
docker compose logs frontend --tail 50
```

### Step 3: DB / Redis / Qdrant 검증

```bash
# DB 확인
docker compose exec postgres psql -U aether -d aether_auth -c "\dt"

# Redis 확인
docker compose exec redis redis-cli ping

# Qdrant 확인 (36 chunks 검증)
curl http://localhost:6333/collections/aether_knowledge
```

### Step 4: 발견 시 → 디버그 카드 트리거

- yfinance 차단 → DBG-1 정착 (자동 fallback / FixtureProvider)
- 이메일 형식 → DBG-2 정착 (@Email + @Pattern 이중)
- Gemini API quota → llm-service config 검증
- Redis 연결 실패 → docker compose restart redis
- Qdrant stale → docker compose restart qdrant

---

## §F frontend 회귀 검증

```bash
cd frontend
npm test
# → 26 passed (10 files / 5 unit + 21 E2E / DEV-FE-1 정착)
```

---

## §G 자가 점검 체크리스트

```text
사전 정착 (5)
☐ docker compose down -v + up -d 진행
☐ sleep 30 + docker compose ps 7 healthy 확인
☐ API health 4 endpoint (auth + portfolio + llm + frontend)
☐ localhost:3000 브라우저 접속
☐ 환경변수 (.env / GEMINI_API_KEY + JWT_SECRET)

5 기능 시연 (5)
☐ Step 2-3 signup + login + dashboard + logout
☐ Step 4 optimize → Sharpe 1.5971 + 비중 + 차트
☐ Step 5 backtest → 155.74% + 8 메트릭 + 16 리밸런싱
☐ Step 6 chat → 답변 + 📚 sources ≥ 1
☐ Step 8 MCP (선택) → Claude Desktop 자동 호출

면접 시연 5분 (5)
☐ 분 1: signup + login + JWT HS512 + Redis blacklist + DBG-2
☐ 분 2: optimize + scipy SLSQP + Sharpe 1.5971 + DBG-1 fallback
☐ 분 3: backtest + walk-forward + 8 메트릭 + 16 리밸런싱
☐ 분 4: RAG chat + ReAct (env 의무) + 36 chunks
☐ 분 5: 양면 정책 19 ADR + 카드 35 + 카파시 매핑 + Houseman 진입

회귀 + 안전 확인 (3)
☐ frontend npm test 26 passed
☐ §C 안전 확인 9건 답변 의무
☐ §D 시연 X 영역 6건 명시 의무
```

---

## §H 시연 결과 첨부

시연 끝나면 결과 첨부:

```text
1. signup + login + logout: 정상 / Edge 400 (DBG-2) / 에러 401 통과 여부
2. optimize: Sharpe 결과값 + 비중 + 프론티어 차트 정상 여부
3. backtest: 누적 수익률 + 8 메트릭 + 16 리밸런싱 정상 여부
4. chat: sources ≥ 1 + 답변 정상 여부
5. MCP: (선택) Claude Desktop 호출 정상 여부
6. frontend npm test: 26 passed 정상 여부

[차이 발견 시]
- 별도 카드 분리 의무 (DBG-3 / DBG-4 / DBG-5)
- SHOW-RESULT 카드 (회고 §4 갱신) 본문 작성 진행
```

---

## §I 한 문장

Step 1-8 순서대로 / 브라우저만 (MCP 선택) / 결과 본문 매칭 / §C 안전 확인 + §D 시연 X 영역 = 면접 답변 시점 거짓 회피 / 본 시점 정확 본문 (PR #57 STALE-FIX 정착 후).
