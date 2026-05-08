# DIFFERENTIATION — Aether 직무별 차별화 영역 (DIFF-1)

> **본질**: Aether 차별화 영역을 직무 4 영역 (AI Engineer / Backend / Full Stack / 시스템 설계) 으로 정착. 이력서 직접 활용 + I-1 (면접 답변 시뮬) 진입 자료. 코드 위치 (파일:라인) 명시 의무 — 추측 X / 실측 본문.
> **카드**: DIFF-1 (차별화 자료 / ADR X — 자료 카드)
> **작성일**: 2026-05-08
> **인용 자료**: KARPATHY_MAPPING / AUDIT / TEST_GUIDE / META_REVIEW / WORK_PATTERNS / PRINCIPLES / SCENARIO / ADR 25건
> **다음 카드**: I-1 (면접 답변 시뮬 / 본 자료 + TEST_GUIDE + KARPATHY_MAPPING §6 인용)

---

## §1 한 눈에 보기

### 직무별 매핑

| 직무 | §본문 | 핵심 영역 |
|---|---|---|
| AI Engineer | §2 (5 영역) | LangGraph ReAct 자율 판단 / Qdrant + 자체 4 메트릭 / Auto Research grid search / MCP stdio / Streaming SSE |
| Backend | §3 (5 영역) | 4 MSA / JWT HS512 + Redis blacklist / 운영급 결정 / Markowitz / walk-forward |
| Full Stack | §4 (3 영역) | Next.js 페이지 분리 / SSE 클라이언트 / Docker Compose 6 서비스 |
| 시스템 설계 | §5 (5 영역) | 양면 정책 15 ADR / 시나리오 A 본질 / 카파시 영상 9 ↔ 매핑 / WORK_PATTERNS 18 + 5 가드 / D-4 패턴 |

### 인용 자료 영역

| 자료 | 위치 | 본 자료 인용 §|
|---|---|---|
| KARPATHY_MAPPING.md | docs/agent-capability-audit/ | §2.3 / §5.3 |
| AUDIT.md | docs/agent-capability-audit/ | §2.3 / §5.4 |
| TEST_GUIDE.md | docs/ | §6 (면접 시연 5분) |
| META_REVIEW.md | docs/agent-capability-audit/ | §5.2 |
| WORK_PATTERNS.md | docs/agent-capability-audit/ | §5.4 |
| PRINCIPLES.md | docs/agent-capability-audit/ | §5.1 (패턴 6 / 미적용 결정) |
| SCENARIO.md | docs/agent-capability-audit/ | §5.2 |
| docs/adr/README.md | docs/adr/ | §5.1 (양면 정책 15 ADR) |

---

## §2 AI Engineer 영역

### §2.1 LangGraph ReAct — 5 도구 자율 판단 (D-5 / ADR 0018)

**코드 위치**:
- ReAct 에이전트 클래스: `llm-service/app/agents/react_agent.py:28-44` (ReActAgent + create_react_agent)
- 자율 판단 본질: `react_agent.py:46-50` (run() / ainvoke → 모델이 도구 호출 순서 자율 판단)
- 5 도구 등록: `llm-service/app/agents/tools.py:45-59` (_register_default_tools)
- 4 portfolio 도구: `llm-service/app/agents/portfolio_tools.py:17-67` (analyze / explain_risk / summarize_backtest / get_recommendation)
- RAG 도구: `llm-service/app/agents/rag_tools.py:15-29` (search_knowledge_base / D-5 신규)

**차별화 본질**:
- 절차적 4 호출 → ReAct 1 호출 (모델 자율 판단). 환경변수 `USE_REACT_AGENT=false` 로 fallback 가능 (점진 전환 패턴 / PRINCIPLES 패턴 8).
- 5번째 도구 `search_knowledge_base` 통합 (D-5) — 도메인 지식 검색이 LLM이 판단할 도구로 격상 (라우터 분기 X).

### §2.2 Qdrant + 자체 4 메트릭 평가 (D-8 / ADR 0015)

**코드 위치**: `llm-service/scripts/eval_rag.py`
- relevance@k: 31-35 (calculate_relevance_at_k / sources 평균 스코어)
- recall@k: 38-42 (expected_source 포함 여부)
- LLM-as-judge quality: 86-92 (1-5 점수)
- LLM-as-judge faithfulness: 95-101 (0-1 비율)
- 집계: 145-158 (aggregate / 4 메트릭 평균)

**차별화 본질**:
- ragas 외부 의존 X / 자체 4 메트릭 정착. PRINCIPLES 패턴 6 (미적용 결정 = 시그널) 직접 사례.
- ground truth 8건 / CLI: `python -m scripts.eval_rag --no-llm-judge` (Gemini quota 회피 옵션).

### §2.3 Auto Research — 9 조합 grid search (D-7 / ADR 0017)

**코드 위치**: `llm-service/scripts/grid_search_chunking.py`
- 정착 값: 19-22 (SIZES_FULL [500, 1000, 1500] / OVERLAPS_FULL [100, 200, 300])
- 조합 생성: 25-28 (generate_combinations / 3×3 = 9)
- subprocess 격리: 31-97 (run_combination / lru_cache settings stale 회피)
- 최적 선정: 100-109 (select_best / recall@k ≥ 1.0 + relevance@k 최대)

**차별화 본질**:
- 인간 직관 X / 메트릭 자동 비교. 카파시 영상 §1.6 (Auto Research) 직접 적용 영역 (KARPATHY_MAPPING.md:93-106).
- baseline 진화 (AUDIT.md §3.6): chromadb 1000/200 (relevance@k 0.4444) → Qdrant 1000/200 (0.7222 / +0.2778) → Qdrant **500/300 (0.7413 / +0.0191)**.
- 누적 향상: D-8 → D-7 = +0.2969 (cosine 유사도 0.44 → 0.74).

### §2.4 MCP server — stdio transport 4 도구 (T-2 / ADR 0008)

**코드 위치**: `portfolio-service/app/mcp_server.py`
- 4 도구 등록: 114-116 (handle_list_tools / @server.list_tools)
- 호출 핸들러: 119-131 (handle_call_tool / Pydantic schema validation + _serialize)
- 직렬화: 134-155 (_serialize / numpy / pandas / dataclass / Enum 통합)
- main entry: 158-160 (async with stdio_server)

**차별화 본질**:
- Claude Desktop ↔ portfolio-service 직접 통합. 라우터 우회 (HTTP X / stdio).
- 4 도구: analyze_portfolio / compute_risk / run_backtest / get_recommendation.
- T-2c fix: 테스트 호스트 절대경로 → 동적경로 (운영 영역 정착).

### §2.5 Streaming SSE — astream_events v2 (D-6 / ADR 0019)

**코드 위치**:
- SSE endpoint: `llm-service/app/routers/chat.py:332-369` (chat_stream / StreamingResponse)
- astream_events v2: `react_agent.py:52-76` (run_stream / version="v2")
- 토큰 이벤트: `react_agent.py:67-72` (on_chat_model_stream → {"type": "token", ...})
- 도구 이벤트: `react_agent.py:73-76` (on_tool_start / on_tool_end → {"type": "tool_start"|"tool_end", ...})

**차별화 본질**:
- 신규 endpoint 분리 (기존 `/api/chat` 0 변경 / PRINCIPLES 패턴 8).
- 형식: `data: {json}\n\n` + `event: done\n\n` 종료. 이벤트 type 4종 (token / tool_start / tool_end / done).
- 우대 요건 직접 적용 (실시간 토큰 + 도구 이벤트).

### §2.6 면접 꼬리 질문 (5건)

1. **"왜 ragas 미도입?"** → ground truth 8건 / 자체 4 메트릭으로 충분 / 의존성 추가 0 본능 (PRINCIPLES 패턴 6). 시나리오 B 진입 시 재검토.
2. **"chunk_size=500 / overlap=300 어떻게 정착?"** → grid search 9 조합 자동 비교 (인간 직관 X) / recall@k ≥ 1.0 유지 + relevance@k 최대 룰. baseline 0.4444 → 0.7413.
3. **"5 도구 자율 판단 검증?"** → ReAct system prompt v1.1 + 5 도구 메타데이터 (도구 이름 / description / inputSchema). USE_REACT_AGENT=false 로 절차적 호출 fallback 가능.
4. **"MCP stdio vs HTTP 차이?"** → Claude Desktop 직접 통합 / Pydantic schema validation / 라우터 우회. portfolio-service 도메인 함수 재사용 (재구현 X).
5. **"streaming endpoint 분리 사유?"** → 기존 /api/chat 회귀 위험 0 / 점진 전환 / 환경변수 토글 X (신규 영역만).

---

## §3 Backend 영역

### §3.1 4 MSA + 인프라 2 (H-1 / ADR 0001)

**구조**:
- auth-service: Spring Boot / Java 17 / `:8003`
- portfolio-service: FastAPI / Python 3.11 / `:8001`
- llm-service: FastAPI / Python 3.11 / `:8002`
- frontend: Next.js 15 / React 19 / `:3000`
- 인프라: postgres `:5432` (auth만 사용) / redis `:6379` (refresh + blacklist) / Qdrant `:6333` (RAG)

**코드 위치**: `docker-compose.yml` (인프라 1-58 / 백엔드 63-148 / 프론트 154-182).

**차별화 본질**:
- 호출 체인 단방향: frontend → 3 백엔드 / llm-service → portfolio-service (httpx event_hooks). 비-REST 통신 0건.
- llm-service ↔ auth-service 직접 통합 X — JWT 헤더 동봉 패턴 (AGENTS.md §1).

### §3.2 JWT HS512 + Redis blacklist (F-1a / ADR 0004 v2)

**코드 위치**: `auth-service/src/main/java/com/aether/auth/api/auth/AuthController.java`
- signup: 28-37 (POST /api/auth/signup)
- login: 39-46 (POST /api/auth/login)
- refresh: 48-55 (POST /api/auth/refresh)
- logout: 57-66 (POST /api/auth/logout / Redis blacklist 영역)
- me: 75-82 (GET /api/auth/me)

**JWT 영역**: `auth-service/.../JwtTokenProvider.java:41-43` (Keys.hmacShaKeyFor / 비밀키 64 bytes 이상 → HS512 자동 선택).

**차별화 본질**:
- F-1a 통일 결정 — auth (Java jjwt) ↔ python (pyjwt) 알고리즘 일치 (HS512 단일). 호환 모드 X.
- refresh reuse 감지 + Redis blacklist (logout 시 토큰 영역 정착).

### §3.3 D-2 운영급 결정 (ADR 0012)

**코드 위치**:
- CORS 명시: `docker-compose.yml:74, 99, 135` (CORS_ORIGINS env / allow_methods=[GET,POST,OPTIONS] / allow_headers=[Authorization, Content-Type, X-Request-ID])
- API 키 검증: `llm-service/app/main.py` (lifespan startup 시점 google_api_key failfast + Pydantic validator 이중 안전장치)
- X-Request-ID forward: `llm-service/app/middleware/logging.py` (request_id_ctx ContextVar) + `llm-service/app/services/portfolio_client.py` (httpx event_hooks → _forward_headers)

**차별화 본질**:
- 운영급 정착 = "와일드카드 X / 외부 키 부재 시 startup fail / 분산 트레이싱 단방향 forward".
- cache LRU CACHE_MAXSIZE=1000 (portfolio config / 인메모리 LRU).

### §3.4 Markowitz 최적화 (T-1)

**코드 위치**: `portfolio-service/app/routers/optimize.py`
- 전략 분기: 128-131 (min_variance → optimize_min_variance / max_sharpe → optimize_max_sharpe)
- 연율화 메트릭: 134-136 (annual_return = expected_return × 252 / annual_vol = volatility × √252 / sharpe = (annual_return - rf) / annual_vol)
- 효율적 프론티어: 144-160 (request.include_frontier 옵션 / efficient_frontier 20 points)

**차별화 본질**:
- cvxopt 기반 MVP (min_variance) + MSR (max_sharpe).
- 진단 정보 영역 — converged / iterations / condition_number / covariance_validation (regularized 영역 명시).

### §3.5 walk-forward 백테스트

**코드 위치**: `portfolio-service/app/routers/backtest.py`
- 실행: 65-72 (walk_forward_backtest / train_window / rebalance_every / transaction_cost / use_shrinkage)
- 8 메트릭: 103-111 (PerformanceMetricsResponse / total_return / annual_return / annual_volatility / sharpe_ratio / max_drawdown / calmar_ratio / avg_turnover / win_rate)
- 리밸런싱 기록: 80-91 (rebalance_history / 각 시점 weights + turnover)

**차별화 본질**:
- 시간순 분리 (train_window 기간 학습 → 다음 rebalance_every 기간 예측). lookahead bias 0.
- 8 메트릭 통합 (수익률 + 위험 + 운용 비용).

### §3.6 면접 꼬리 질문 (4건)

1. **"왜 4 MSA / 모노리스 X?"** → 도메인 분리 (auth / portfolio 수치 / llm 도메인 분석). LLM 호출 timeout 60초 / 단일 모노리스 시 다른 endpoint 영향. 시나리오 B 진입 시 검토 (도메인 검증 트리거).
2. **"HS512 통일 사유?"** → F-1a 시점 검증 (auth Java jjwt HS512 / python HS256 stale) → ADR 0004 v2. 비밀키 64 bytes 이상 의무.
3. **"Redis blacklist 정확히 어떻게?"** → logout 시 access token jti + 만료 시점까지 TTL 영역. refresh 시점 blacklist 검증 (reuse 감지).
4. **"walk-forward vs 단순 backtest 차이?"** → 단순 backtest = 전체 기간 학습 → 동일 기간 평가 (lookahead bias). walk-forward = 시간순 분리 / 실 운용 시뮬.

---

## §4 Full Stack 영역

### §4.1 Next.js + TypeScript 페이지 분리 (D-3 / ADR 0013)

**코드 위치**: `frontend/src/app/dashboard/`
- optimize 페이지: `frontend/src/app/dashboard/optimize/` (344 LOC)
- backtest 페이지: `frontend/src/app/dashboard/backtest/` (217 LOC)
- chat 페이지: `frontend/src/app/dashboard/chat/`

**차별화 본질**:
- 200 LOC 임계 (페이지 50 LOC 이하 = 컴포넌트 조합만 / D-3 결정).
- 페이지별 책임 단일화 (optimize / backtest / chat 분리).

### §4.2 SSE 클라이언트

**코드 위치**: `frontend/src/services/api.ts` (streamChat API / ReadableStream 기반)

**차별화 본질**:
- 백엔드 `/api/chat/stream` (D-6) ↔ 프론트 ReadableStream + TextDecoder.
- 토큰 + 도구 이벤트 실시간 표시.

### §4.3 Docker Compose 6 서비스

**코드 위치**: `docker-compose.yml`
- 인프라 3: postgres (1-15) / redis (16-31) / qdrant (32-58)
- 백엔드 3: portfolio-service (63-89) / llm-service (90-115) / auth-service (116-148)
- 프론트엔드: frontend (154-182)
- 단일 bridge 네트워크 `aether-network` / hostname 기반 서비스 디스커버리.

**차별화 본질**:
- health check 6 서비스 정착 (TEST_GUIDE.md §1.2 인용).
- 단일 명령 (`docker compose up -d`) 으로 전체 환경 정착.

### §4.4 면접 꼬리 질문 (3건)

1. **"왜 Next.js App Router?"** → React Server Components / 페이지별 코드 분할 / SSR + CSR 통합.
2. **"SSE vs WebSocket 차이?"** → SSE = 단방향 (서버 → 클라이언트) / 토큰 + 도구 이벤트 영역 충분. WebSocket = 양방향 (chat 영역 외 도구 호출 양방향 X).
3. **"Docker Compose vs k8s?"** → 시나리오 A 본질 영역 (단일 호스트 / 사용자 0명). k8s = 시나리오 B 진입 시점 트리거.

---

## §5 시스템 설계 영역

### §5.1 양면 정책 15 ADR (정착 7 + 보류 4 + 메타 4)

**인용**: `docs/adr/README.md §2`

**정착 결정 (7건)** — 시나리오 A 본질 + 운영급:
| ADR | 카드 | 정착 본문 |
|---|---|---|
| 0012 | D-2 | CORS + API 키 + cache LRU |
| 0013 | D-3 | 페이지 분리 200 LOC 임계 |
| 0015 | D-8 | 자체 4 메트릭 (ragas 미도입) |
| 0016 | T-6b | Qdrant default + chromadb fallback |
| 0017 | D-7 | Chunking grid search (500/300) |
| 0018 | D-5 | ReAct + RAG 5 도구 |
| 0019 | D-6 | Streaming SSE |

**보류 결정 (4건)** — 시나리오 B 트리거:
| ADR | 카드 | 보류 본문 / 트리거 |
|---|---|---|
| 0010 | C-1 | T-3 Multi-Agent → Houseman Phase 7-12 |
| 0011 | D-1 | MLflow / drift / weight / RAG 정제 → 시나리오 B |
| 0014 | D-9 | RAG 정제 → 시나리오 B + 동적 데이터 |
| 0025 | CL-D | CL-2 + CL-3 cleanup → 시나리오 B (도메인 검증 + 사용자 5+ + PMF 10불) |

**메타 / 정리 (4 + 1건)**: 0020 (D-4 audit) / 0021 (P-1 메타 패턴) / 0022 (V-1 검증) / 0023 (V-1b 재작성) / 0024 (CL-1 인덱스).

**차별화 본질**:
- PRINCIPLES 패턴 6 (미적용 결정 = 시그널) 직접 사례 — 기술 도입은 누구나 가능 / 시니어 차이 = 미적용 결정 + 진입 트리거 명시.
- 양면 정책 = "정착 결정 + 보류 결정 동시 추적" — 시나리오 A 본질 일관성 + 시나리오 B 진입 영역 명시.

### §5.2 시나리오 A 본질 일관성

**인용**: `docs/agent-capability-audit/SCENARIO.md`

**시나리오 A 정착**:
- 사용자 0명 / 도메인 검증 X / 기술 데모 + 시니어 패턴 영역.
- 완성 조건: Top 10 종료 + 면접 답변 가능.

**시나리오 전환 3 질문 (B 진입 트리거)**:
1. "한국 개인 투자자가 진짜 겪는 문제 Top 5?"
2. "나는 이 서비스를 실제로 쓸 건가? 5명 인터뷰?"
3. "사용자가 10불 내고 쓸 가치 / 비즈니스 모델?"

**차별화 본질**:
- T-3 보류 결정 (ADR 0010) = 시나리오 A 본질 영역 X / Houseman Phase 7-12 학습 통합 = 시니어 시그널.
- "별도 repo → 도입 X → 다시 도입" 3번 흔들림 인지 → PRINCIPLES 패턴 7 (본질 충돌 시 두 본능 분리 검증).

### §5.3 카파시 영상 9 ↔ Aether 매핑

**인용**: `docs/agent-capability-audit/KARPATHY_MAPPING.md §1` (10-160 라인)

**5 직접 적용 영역 (본능 점수 ≥ 85)**:
| # | 항목 | Aether 적용 | 점수 |
|---|---|---|---|
| 2 | Skill Issue (T-6b) | _EMBED_DIM 768 → 3072 정정 (G1 본질 트리거) / ADR 0016 | 95 |
| 3 | Macro Actions | 카드 단위 위임 18건 (M-1 ~ V-1b) | 88 |
| 6 | Auto Research (D-7) | grid search 9 조합 / chunk_size=500 / +0.019 | 90 |
| 7 | Jaggedness Verifiable (D-8) | 자체 4 메트릭 / ragas 보류 | 88 |
| 9 | Markdown for Agents | 자료 14건 + ADR 25건 + 카드 21건 모두 Markdown | 정착 |

**4 미적용 / Houseman Phase 7-12 트리거**:
1. AI Psychosis (12월 패러다임) — 부분 (코드 검수 본인 영역)
2. Token Throughput — 미적용 (단일 세션) / 다중 세션 트리거
3. Persistent Loop / Claw — 미적용 (Claude Code 단일 세션) / sandbox 트리거
4. AGENTS.md + Soul.md — AGENTS.md O / Soul.md X / 페르소나 트리거

**차별화 본질**:
- 영상 9 ↔ Aether 매핑 = 단순 영상 정리 X / 각 항목 3 영역 통합 (본문 인용 + 적용 위치 + 적용 결과).
- 8 본능 평균 76 → 87점 (P-1 시점). Skill 95 / Auto Research 90 / Reversibility 90.

### §5.4 WORK_PATTERNS 18 누적 문제 + 5 가드

**인용**: `docs/agent-capability-audit/WORK_PATTERNS.md`

**18 누적 문제 해소 (D-4 시점)**:
- 해소 17 / 18 (94.4%)
- 부분 해소 1 / 18 (5.6%, FutureWarning)
- 미해소 0 / 18 (0%)

**5 가드 (매 카드 plan 의무)**:
1. **G1 Decision Budget** — 라운드 max + 시간 cap
2. **G2 Reversibility** — Type 1 (비가역) vs Type 2 (가역)
3. **G3 Done Definition** — "80/100점이면 종결"
4. **G4 Round Cap** — 메타 사고 max 3
5. **G5 First Principle** — 본질 1줄 / 30분마다 점검

**체크리스트 A-G** (매 카드 plan):
- A: 작업 트리 위생
- B: 사용자 prompt 검증 (실측 의무)
- C: 외부 라이브러리 호환 + 신규 패키지 의존성 매트릭스
- D: 5 가드 강제
- E: 커밋 위생
- F: PR 머지 후 정리 + F-패턴
- G: 문서 갱신

**차별화 본질**:
- 같은 실수 반복 차단 = 시니어 본질. 작업 트리 위생 + PR 머지 + prompt 검증 + 외부 SDK + 문서 갱신 + 의사결정 무한 루프 + 후속 카드 누적.
- plan 검수 13 영역 (영역 11 누락 위험 / 12 외부 영향 / 13 메타).

### §5.5 D-4 패턴 — 자료 동시 갱신 의무

**본질**: 자료 본문 변경 시 영향 § 같은 PR에 동시 갱신.

**적용 영역 4건**:
1. AGENTS.md §7 지배 숫자 변경 시 — 인용 위치 (자료 본문 / ADR) 동시 갱신
2. ADR 결정 변경 시 — v2 / v3 / git log 추적
3. 자료 추가 / 제거 시 — docs/README.md / docs/agent-capability-audit/README.md / docs/adr/README.md 동시 갱신
4. 카드 머지 시 — 카드 ID 인덱스 + AGENTS.md §7 baseline 행 갱신

**본 카드 (DIFF-1) 적용**: DIFFERENTIATION.md (신규) + docs/README.md (§3 + §7 갱신) + AGENTS.md §7 (baseline 행 추가) 동시 PR.

### §5.6 면접 꼬리 질문 (7건)

1. **"양면 정책이 뭐?"** → 정착 결정 + 보류 결정 동시 추적. 보류 = 시나리오 B 진입 트리거 명시 (도메인 검증 / 사용자 5+ / PMF 10불).
2. **"왜 T-3 Multi-Agent 보류?"** → 시나리오 A 본질 영역 X (사용자 0명 / 도메인 검증 X) / Houseman Phase 7-12 학습 적용 시점 트리거. ADR 0010 + PRINCIPLES 패턴 6.
3. **"카파시 영상 적용 사례?"** → D-7 grid search (Auto Research / 9 조합 자동 비교 / 인간 직관 X) / T-6b _EMBED_DIM 정정 (Skill Issue 본능). 8 본능 평균 76 → 87점.
4. **"WORK_PATTERNS 5 가드 매번 적용?"** → 매 카드 plan 의무 (CLAUDE.md §7). 5 가드 (G1-G5) + 체크리스트 A-G + 검수 13 영역. 18 누적 문제 17/18 해소.
5. **"왜 D-1 보류 4건? (MLflow / drift / weight / RAG 정제)"** → 본질 X 영역 / 시나리오 B 진입 시점 트리거. PRINCIPLES 패턴 6 직접 사례 (미적용 결정 = 시그널).
6. **"문서 동시 갱신 의무 사유?"** → D-4 패턴 / 자료 stale 회피. 6개월 후 다른 개발자 인지 가능 영역 (CL-1 영역 본질).
7. **"시나리오 A → B 진입 시점 어떻게 알까?"** → SCENARIO.md 3 질문 (도메인 / 사용자 5+ / PMF 10불) 통과 시점. Houseman Phase 7-12 학습 통합 시점.

---

## §6 직무 지원 시 자료 인용 흐름

### AI Engineer 지원
- **본 자료 §**: §2 (5 영역) + §5.3 (카파시 영상 영향) + §5.1 (보류 4건 결정 추적)
- **추가 자료**: KARPATHY_MAPPING.md §1 (영상 9 ↔ Aether) + AUDIT.md §3.6 (baseline 진화)
- **시연**: TEST_GUIDE.md §2.4 (chat / RAG + ReAct) + §2.5 (MCP)
- **면접 5분**: TEST_GUIDE.md §3 (시연 흐름 + 차별화 3건)

### Backend 지원
- **본 자료 §**: §3 (5 영역) + §5.2 (시나리오 A 본질) + §5.4 (5 가드)
- **추가 자료**: AGENTS.md §1 (호출 체인) + §9 (JWT + 분산 트레이싱) + ADR 0001 / 0004 v2 / 0012
- **시연**: TEST_GUIDE.md §2.1 (signup + login) + §2.2 (optimize) + §2.3 (backtest)

### Full Stack 지원
- **본 자료 §**: §2 + §3 + §4 + §5 (직무별 영역 모두)
- **추가 자료**: AGENTS.md §2 (토폴로지) + ADR 0013 (페이지 분리) + 0019 (SSE)
- **시연**: TEST_GUIDE.md §2 (5 기능 시연 / 정상 + Edge + 에러)

### 시스템 설계 강조
- **본 자료 §**: §5 (양면 정책 + 시나리오 + 카파시 매핑 + WORK_PATTERNS + D-4 패턴)
- **추가 자료**: SCENARIO.md (시나리오 A 본질) + PRINCIPLES.md (10 패턴) + META_REVIEW.md (시니어 회고)
- **본질**: "기술 도입 누구나 가능 / 차이 = 미적용 결정 + 트리거 명시" (PRINCIPLES 패턴 6).

---

> **한 문장**: Aether 차별화 = 4 직무 영역 (AI Engineer ReAct + Qdrant + Auto Research + MCP + SSE / Backend 4 MSA + JWT + 운영급 + Markowitz + walk-forward / Full Stack Next.js + SSE + Docker / 시스템 설계 양면 정책 + 시나리오 A + 카파시 매핑 + 5 가드 + D-4 패턴). 코드 위치 명시 (실측 본문) + 자료 8 인용 통합. I-1 (면접 답변 시뮬) 진입 자료 정착.
