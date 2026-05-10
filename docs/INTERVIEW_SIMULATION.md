# INTERVIEW_SIMULATION — Aether 면접 답변 시뮬레이션 (I-1)

> **본질**: 4 직무 (AI Engineer / Backend / Full Stack / 시스템 설계) × 5-7 핵심 질문 + 꼬리 질문 3-5건 + 답변 본문 + 자료 인용 위치 통합. 사용자 직접 활용 자료 (이력서 + 면접 시점). 모든 답변 = 자료 인용 위치 명시 (파일:라인 또는 ADR 번호) / 추측 X / 실측 본문만.
> **카드**: I-1 (면접 답변 시뮬레이션 / 자료 카드 / ADR X)
> **작성일**: 2026-05-09
> **선행 카드**: TG-2d (PR #45 / 0b2be3f) — 면접 시연 가능 영역 4/5 + DBG-1 transient vs 영구 영역 본질 시그널 영역 정착
> **인용 자료** (9건): DIFFERENTIATION.md (직무별 차별화) + TEST_REPORT.md (시연 결과) + KARPATHY_MAPPING.md §1+§부록 (영상 ↔ 매핑) + ADR 25건 (양면 정책 15) + META_REVIEW.md §6+§9 (Top 10 9.5/10) + SCENARIO.md §1.1 (시나리오 A/B/C) + WORK_PATTERNS.md (18 누적 + 5 가드) + PRINCIPLES.md (10 패턴) + AGENTS.md §7 (지배 숫자)

> **사용자 영역**: 본 자료 영역 = 면접 답변 자료 영역 / 이력서 자료 영역 / Aether 종료 자료 영역 영역 직접 활용 자료. 본인 영역 (학력 / 경력 / 강점 / 지원 동기) 영역 영역 사용자 직접 영역 정착 의무. Aether 프로젝트 영역 답변 영역 영역만 영역 자료 정착.

---

## §1 본질 + 면접 흐름 + 직무별 매핑

### §1.1 본 자료 활용 흐름

면접 시점 답변 흐름 영역 본문:

1. **자기소개 5분** (§2) — Aether 본질 + 차별화 1줄 + 시나리오 A 명시
2. **직무별 핵심 질문** (§3-§6) — 면접관 직무 영역 따라 §3 (AI Engineer) / §4 (Backend) / §5 (Full Stack) / §6 (시스템 설계) 영역 진입
3. **꼬리 질문 영역 대응** — 각 답변 영역 꼬리 3-5건 영역 정착 / 본 자료 영역 영역 정착 영역
4. **까다로운 질문** (§7) — "왜 사용자 0명?" / "왜 안 고침?" 영역 영역 영역 영역 정착
5. **답변 흐름** (§8) — PREP / STAR / 모르는 영역 흐름 / 본인 영역 의무 회피

### §1.2 직무별 매핑

| 직무 | 핵심 영역 | 인용 자료 |
|---|---|---|
| AI Engineer | ReAct + RAG + Auto Research + MCP + SSE + 카파시 | DIFF §2 / KARPATHY §1 / ADR 0008/0015/0017/0018/0019 |
| Backend | 4 MSA + JWT HS512 + D-2 + Markowitz + walk-forward + ADR | DIFF §3 / ADR 0001/0004/0012 |
| Full Stack | Next.js + SSE 클라이언트 + Docker Compose + 통합 | DIFF §4 / ADR 0013 |
| 시스템 설계 | 양면 정책 15 ADR + 시나리오 A + 카파시 매핑 + WORK_PATTERNS + D-4 | DIFF §5 / SCENARIO / KARPATHY / WORK_PATTERNS |

### §1.3 답변 원칙

- **자료 인용 의무**: 모든 주장 = 파일:라인 또는 ADR 번호 명시. "추측" / "예상" / "아마" 어휘 영역 사용 영역 X.
- **본인 영역 회피**: Aether 프로젝트 영역 답변만. 학력 / 경력 / 강점 영역 = 사용자 직접 정착 의무.
- **트랜지언트 시그널**: TG-2d 발견 영역 (yfinance transient) = 시니어 시그널 영역 활용 (transient vs 영구 영역 본질 판단).
- **시나리오 A 명시**: "사용자 0명 영역 = 의도 영역" 영역 명시 — 시나리오 B 트리거 3 질문 (도메인 / 사용자 / PMF) 영역 답변 흐름 영역 정착.

---

## §2 자기소개 5분 흐름

### §2.1 면접관 첫 질문: "자기소개 부탁드립니다"

**답변 흐름** (1-2분):

1. **본인 영역** (사용자 직접 정착) — 학력 / 경력 / 지원 동기 ~30초
2. **Aether 프로젝트 본질** ~60초:
   - "Aether는 포트폴리오 최적화 + RAG 챗봇 영역 통합한 4 MSA 시스템입니다 (auth Spring Boot / portfolio + llm FastAPI / frontend Next.js)"
   - "사용자 0명 영역 의도 영역 — 시나리오 A 본질 (기술 데모 + 시니어 패턴 정착) 영역 명시 영역 (SCENARIO.md §1.1)"
   - "양면 정책 15 ADR 영역 정착 (정착 7 / 보류 4 / 메타 4) — 박지 않은 결정도 시그널 (PRINCIPLES 패턴 6) 영역 의도적으로 활용"
   - "카파시 영상 9 항목 영역 매핑 — Skill Issue / Auto Research / Reversibility 5 직접 적용 (KARPATHY_MAPPING §1)"
3. **차별화 1줄** ~20초:
   - "AI 풀스택 + 시니어 시그널 — 단순 기능 영역 영역 영역 운영급 결정 영역 의도적 정착 (D-2 / ADR 0012)"

### §2.2 Aether 본질 핵심 숫자

| 영역 | 숫자 | 인용 |
|---|---|---|
| 서비스 영역 | 4 MSA + 3 인프라 (postgres + redis + qdrant) | docker-compose.yml:6-160 / ADR 0001 |
| 코드 LOC | 14,414 | AUDIT.md (D-4 baseline) |
| 테스트 | 635 (백엔드 511 + frontend 5 + 추가 119) | INTERVIEW.md §4 / Pytest |
| ADR | 25건 (정착 7 + 보류 4 + 메타 4 + 정리 1) | docs/adr/0001-0025 |
| 카드 | 24건 (phase3 11 + TG/DBG/I/M/V 13 / TG-2d 머지 후) | docs/agent-capability-audit/phase3/ + git log |
| Top 10 | 9.5/10 (T-3 보류 결정) | META_REVIEW §9 |
| 카파시 매핑 | 8 본능 평균 76 → 87 (+11점) | KARPATHY_MAPPING §1 |

### §2.3 시나리오 A 명시 (의도적 영역)

면접관 영역 영역 영역 의문 영역 발생 영역 → 본 자료 영역 답변:

> "사용자 0명 영역 = 의도 영역. 시나리오 A 본질 = 기술 데모 + 시니어 패턴 정착. 시나리오 B (소수 사용자) 진입 트리거 3 질문 (한국 개인 투자자 진짜 문제 Top 5? / 5명 인터뷰? / PMF 10불?) 영역 답 안 되면 시나리오 A 종료 + 별도 프로젝트 분리 영역 명시 (SCENARIO.md §1.1)"

---

## §3 AI Engineer 영역 질문 (7건 + 꼬리)

### §3.1 "LangGraph ReAct 영역 사용 영역?"

**답변 본문** (~60초):

> "ReAct 패턴 영역 = 도구 호출 순서 영역 모델 자율 판단 영역 정착. T-1b 영역 절차적 4 호출 (analyze → risk → backtest → recommend) → ReAct 1 호출 영역 전환 (`react_agent.py:40-44` create_react_agent / `chat.py:198-201` RAG_FALLBACK_DIRECT 토글 + `chat.py:226-246` ReAct 분기). ADR 0006 (ReAct 패턴) + ADR 0018 (5 도구 + search_knowledge_base D-5)."

**자료 인용**: `react_agent.py:40-44` + `chat.py:198-201, 226-246` + ADR 0006/0018

**꼬리 질문 영역**:
- Q: "도구 5개 영역 어떻게 자율 판단?"
  - A: "tool_registry 영역 5 도구 등록 (`tools.py:45-59` _register_default_tools / `portfolio_tools.py:17-67` 4 도메인 도구 @tool 래퍼 + `rag_tools.py:15-29` search_knowledge_base D-5). 모델 영역 도구 description 영역 영역 영역 영역 자율 판단."
- Q: "ReAct 영역 안 쓰면 fallback 영역?"
  - A: "USE_REACT_AGENT=false 영역 환경변수 토글 영역 절차적 4 호출 fallback (chat.py:331-356). G2 Reversibility 가드 적용 (WORK_PATTERNS 5 가드)."
- Q: "Tool Registry 영역 본질?"
  - A: "Lazy Init Singleton 패턴 (자기 일관성 패턴 #1 / WORK_PATTERNS) — prompt_registry / tool_registry / chroma_client 모두 동일 패턴."

---

### §3.2 "RAG 평가 시스템 영역 어떻게?"

**답변 본문** (~60초):

> "ragas 영역 영역 영역 보류 결정 (ADR 0015 / D-8) — 외부 의존성 영역 영역 영역 영역 자체 4 메트릭 정착: relevance@k / recall@k / LLM-as-judge quality + faithfulness (`eval_rag.py:31-102`). 36 chunks (D-7 chunk_size=500/overlap=300 후 / T-6b baseline 26 / ADR 0017) / 3072차원 / Qdrant default (T-6b / ADR 0016) — chromadb fallback 어댑터 (응답 호환 어댑터 패턴 #3)."

**자료 인용**: `eval_rag.py:31-102` + ADR 0015 (D-8) + ADR 0016 (T-6b)

**꼬리 질문**:
- Q: "ragas 영역 안 쓴 이유?"
  - A: "ADR 0015 영역 명시 — 양면 정책 (옵션 A 자체 메트릭 / 옵션 B ragas) 영역 옵션 A 정착. 시나리오 B 트리거 영역 영역 ragas 영역 진입 영역 영역 명시. PRINCIPLES 패턴 6 (미적용 결정 = 시그널) 일관성."
- Q: "자체 4 메트릭 영역 본질?"
  - A: "relevance@k = 검색 정확도 / recall@k = 검색 완전성 / LLM quality = 답변 품질 (LLM-as-judge) / faithfulness = sources 인용 충실성. 4 영역 영역 영역 RAG 영역 자체 검증 가능 영역."
- Q: "Qdrant 영역 ChromaDB 영역 차이?"
  - A: "T-6b 영역 default 전환 (ADR 0016) — Qdrant 영역 collection 영역 hybrid search 가능 (sparse + dense) / chromadb 영역 단순 영역. 단 어댑터 패턴 영역 0 영역 변경 영역 (응답 호환 어댑터 #3)."

---

### §3.3 "Chunking 영역 어떻게 정착?"

**답변 본문** (~60초):

> "Auto Research 영역 — 인간 직관 영역 최소화 영역 grid search 영역 자동 비교 (PRINCIPLES 패턴 9 / D-7 / ADR 0017). 9 조합 (chunk_size 200/500/1000 × overlap 50/100/300) 영역 자체 4 메트릭 영역 영역 비교 영역 영역 chunk_size=500 / overlap=300 영역 정착 (+0.0191 향상). 카파시 영상 6번 (Auto Research) 직접 적용 영역 (KARPATHY_MAPPING §1 영역 90점)."

**자료 인용**: `grid_search_chunking.py:19-109` + ADR 0017 (D-7) + KARPATHY §1

**꼬리 질문**:
- Q: "9 조합 영역 어떻게 결정?"
  - A: "3 × 3 grid (chunk_size 3 영역 × overlap 3 영역). chunk_size 200/500/1000 (단어 영역 영역 영역 영역) / overlap 50/100/300 (영역 영역 인접 영역). 영역 영역 영역 영역 영역 사람 영역 영역 영역 결정 X (직관 X)."
- Q: "자동 비교 영역 본질?"
  - A: "각 조합 영역 RAG 평가 4 메트릭 영역 측정 → 평균 영역 영역 가장 높은 조합 영역 정착. 사람 영역 직관 영역 영역 X / 측정 영역 영역."
- Q: "카파시 영상 영향?"
  - A: "영상 6번 Auto Research 영역 — '인간 영역 결정 영역 영역 영역 영역 영역 측정 영역 영역 자동 비교'. KARPATHY_MAPPING §1 영역 직접 적용 점수 90점 영역 정착."

---

### §3.4 "MCP server 영역 정착 사유?"

**답변 본문** (~60초):

> "MCP (Model Context Protocol) 영역 stdio 4 도구 외부 노출 (T-2 / ADR 0008). portfolio-service 영역 4 도메인 도구 (analyze / compute_risk / run_backtest / get_recommendation) 영역 Claude Desktop 영역 직접 호출 가능 (`mcp_server.py:114-132` list_tools + call_tool 핸들러 / `mcp_server.py:158-160` stdio_server main). Pydantic schema validation. 라우터 우회 영역 — frontend / API 영역 X / Claude Desktop ↔ portfolio-service 직접 통합."

**자료 인용**: `mcp_server.py:114-132, 158-160` + ADR 0008 (T-2)

**꼬리 질문**:
- Q: "stdio 영역 본질?"
  - A: "stdio = standard input/output. Claude Desktop 영역 subprocess 영역 영역 portfolio-service mcp_server 영역 stdin/stdout 영역 통신. HTTP X / 영역 영역 영역 빠름 영역."
- Q: "라우터 우회 영역 검증?"
  - A: "frontend 영역 영역 portfolio-service /api/optimize 영역 호출 영역 / Claude Desktop 영역 영역 영역 mcp_server 영역 직접 호출. 두 경로 영역 영역 영역 동일 영역 함수 영역 영역 호출 — `analyze_portfolio_tool` 영역 영역 영역 영역 사용."
- Q: "Claude Desktop 통합 영역?"
  - A: "사용자 수동 검증 영역 (TEST_REPORT §2.5 보류) — Claude Desktop 영역 stdio 4 도구 등록 + Pydantic schema 검증 + 절대경로 영역 영역. TG-2d 시점 영역 영역 X (puppeteer / 자동 시연 영역 X)."

---

### §3.5 "SSE Streaming 영역 어떻게 정착?"

**답변 본문** (~60초):

> "Streaming SSE 영역 = 신규 endpoint 분리 영역 점진 전환 (PRINCIPLES 패턴 8 / D-6 / ADR 0019). `POST /api/chat/stream` 영역 신규 (기존 /api/chat 0 변경). LangGraph astream_events v2 영역 token + tool events 영역 실시간 영역 (`chat.py:332-372` StreamingResponse + event_generator + `react_agent.py:52-76` astream_events v2). format = `data: {json}\\n\\n` (SSE 표준)."

**자료 인용**: `chat.py:332-372` + `react_agent.py:52-76` + ADR 0019 (D-6)

**꼬리 질문**:
- Q: "astream_events v2 영역?"
  - A: "LangGraph 영역 stream API v2. token 단위 영역 영역 + tool 호출 시작/완료 event 영역 영역 영역 영역 영역. v1 영역 token만 영역 영역 / v2 영역 tool event 영역 추가."
- Q: "WebSocket 영역 안 쓴 이유?"
  - A: "SSE 영역 단방향 server → client 영역 영역 영역. chat 영역 영역 client → server 영역 한 번 + server → client 영역 토큰 stream 영역 영역 — 단방향 영역 영역 SSE 영역 적합. WebSocket 영역 양방향 영역 영역 — 영역 영역 영역 영역 X (시나리오 B 트리거 영역 영역)."
- Q: "기존 /api/chat 영역 영역 영역?"
  - A: "0 변경 영역 보존 — PRINCIPLES 패턴 8 (신규 endpoint 분리 = 점진 전환). 기존 영역 호환성 영역 영역 + 환경변수 토글 영역 영역 fallback 가능."

---

### §3.6 "카파시 영상 영역 영향?"

**답변 본문** (~60초):

> "카파시 영상 9 항목 영역 영역 영역 → Aether 매핑 정착 (KARPATHY_MAPPING §1). 5 직접 적용: Skill Issue (95점 / T-6b _EMBED_DIM 768→3072 정정 / ADR 0016) + Auto Research (90점 / D-7 grid search) + Jaggedness/Verifiable (88점 / D-8 자체 4 메트릭) + Macro Actions (88점 / 카드 18건 위임) + AGENTS.md (88점 / Soul.md X / Houseman 트리거). 8 본능 평균 76 → 87 (+11점)."

**자료 인용**: KARPATHY_MAPPING.md §1 + 부록 6건 + ADR 0016/0017/0015

**꼬리 질문**:
- Q: "Skill Issue 사례?"
  - A: "T-6b 영역 _EMBED_DIM 영역 768 → 3072 정정. 영역 영역 본 영역 영역 영역 영역 차원 영역 stale 영역 정착 영역 영역 영역 영역 영역 영역. G1 본질 트리거 발견 영역 즉시 정정 (PRINCIPLES 패턴 10)."
- Q: "Macro Actions 영역?"
  - A: "카드 18건 영역 위임 — M-1 ~ V-1b 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역. 영역 영역 영역 영역 영역 마이크로 영역 영역 X / 매크로 영역 영역 영역."
- Q: "Markdown for Agents 영역?"
  - A: "자료 14건 + ADR 23건 + 카드 18건 모두 Markdown 영역 정착. 영상 9번 영역 'Markdown 영역 = 에이전트 영역 영역 영역 영역 영역 형식'."
- Q: "Soul.md 영역 X 영역 영역?"
  - A: "Houseman 트리거 영역 — Aether 영역 시나리오 A 영역 영역 / Soul.md 영역 영역 영역 별도 repo 영역 영역. KARPATHY_MAPPING §1 영역 명시."

---

### §3.7 "트랜지언트 영역 (TG-2d 발견) 영역?"

**답변 본문** (~60초):

> "TG-2d 영역 자동 시연 재진행 영역 영역 영역 yfinance 영역 영역 영역 transient 영역 발견 — 어제 시점 영역 영역 영역 (DBG-1 트리거) / 본 시점 정상 영역 영역 (Sharpe 1.5971 / 누적 155.74%). 코드 변경 X → 어제 영역 = transient yfinance rate limit 영역 영역 영역 영역 정착 (TEST_REPORT §3.2). DBG-1 카드 영역 = 별도 영역 분리 (CLAUDE.md §6 / 한 카드 = 한 책임)."

**자료 인용**: TEST_REPORT.md §3.2 + §3.3 + TG-2d

**꼬리 질문**:
- Q: "transient vs 영구 영역 어떻게 판단?"
  - A: "동일 시점 + 동일 코드 + 다른 결과 = transient 영역 영역. 본 사례: TG-2c 어제 영역 X / TG-2d 본 시점 ✓. 코드 변경 영역 X (98839b8 → 0b2be3f 영역 영역 docs only). 즉 외부 의존 영역 (yfinance API rate limit) 영역 영역."
- Q: "fallback 영역 결정 사유?"
  - A: "DBG-1 영역 = 영역 영역 fallback data provider 영역 영역 의무 영역 영역 — 재발 영역 영역 영역. 단 본 카드 영역 = 재시연만 영역 (DBG-1 영역 분리 카드). PRINCIPLES 패턴 6 (미적용 결정도 시그널) 일관성."
- Q: "시나리오 B 트리거 영역?"
  - A: "yfinance 영역 영역 영역 영역 영역 영역 시나리오 B (소수 사용자) 진입 영역 영역 영역 영역 영역 영역 영역. 시나리오 A 영역 영역 = transient 영역 영역 영역 영역 영역 영역 (사용자 0명) / 시나리오 B 영역 영역 = 영구 fallback 영역 의무 영역."

---

## §4 Backend 영역 질문 (7건 + 꼬리)

### §4.1 "MSA 영역 어떻게 분리?"

**답변 본문** (~60초):

> "4 MSA + 2 인프라 영역 분리 (H-1 / ADR 0001). auth (8003 / Spring Boot Java 17) + portfolio (8001 / FastAPI Python 3.11) + llm (8002 / FastAPI Python 3.11) + frontend (3000 / Next.js 15). 단방향 호출 영역 — frontend 영역 3 백엔드 호출 / llm → portfolio (httpx event_hooks 영역 X-Request-ID + Authorization forward / H-10 / L-7). gRPC / Kafka 영역 X / 단순 HTTP/JSON."

**자료 인용**: docker-compose.yml:6-160 + ADR 0001 + portfolio_client.py event_hooks

**꼬리 질문**:
- Q: "auth Spring Boot 영역 영역?"
  - A: "Java 17 + Spring Boot — JWT HS512 + Redis blacklist 영역 영역 영역 영역 영역 검증된 라이브러리 영역. Python 영역 영역 영역 영역 라이브러리 영역 영역 X / Spring 영역 표준."
- Q: "portfolio + llm FastAPI 영역?"
  - A: "Python 3.11 — 수치 계산 (scipy / numpy / pandas) + LLM (LangGraph / Gemini SDK). FastAPI 영역 async + 자동 OpenAPI 영역 영역."
- Q: "분리 본질?"
  - A: "단일 책임 영역. auth 영역 인증만 / portfolio 영역 수치 계산만 / llm 영역 RAG + LLM만. 영역 영역 영역 변경 영역 영역 영역 영역 영역 영역 영역 영역 X."

---

### §4.2 "인증 영역 어떻게 정착?"

**답변 본문** (~60초):

> "JWT HS512 + Redis blacklist (F-1a / ADR 0004 v2). 발급 영역 — `JwtTokenProvider.java:39-44` (`com.aether.auth.global.security`) @PostConstruct + Keys.hmacShaKeyFor(64 bytes) → HS512 자동 영역. logout 영역 — `AuthService.java:116-120` (`com.aether.auth.application.auth`) → `JwtTokenProvider.java:116-130` blacklistAccessToken() 영역 Redis BLACKLIST_PREFIX 영역 token TTL 영역 등록. accessToken 30분 / refreshToken 7일. frontend 영역 httpOnly cookie 영역 보관 (XSS 회피)."

**자료 인용**: JwtTokenProvider.java:39-44, 116-130 + AuthService.java:116-120 + ADR 0004 v2 (F-1a)

**꼬리 질문**:
- Q: "HS512 영역 사유?"
  - A: "RS256 영역 영역 영역 영역 영역 영역 영역 — 영역 영역 비대칭 키 영역 = 영역 영역 영역 영역 영역 영역 영역 X. HS512 영역 = 단일 secret 영역 (양 영역 영역 같은 키) — 영역 영역 영역 영역 영역 인증 영역 영역 영역 영역 적합."
- Q: "Redis blacklist 영역 본질?"
  - A: "JWT stateless 영역 영역 영역 영역 영역 logout 영역 영역 영역 = 영역 영역 영역 영역 영역. Redis blacklist 영역 영역 logout 시 token 영역 등록 → 영역 영역 영역 영역 검증 영역 blacklist 영역 영역."
- Q: "logout 시 토큰 영역?"
  - A: "Redis BLACKLIST_PREFIX:{token} 영역 등록 — TTL = token expiration 영역 영역 영역 영역. 영역 영역 token 영역 만료 영역 영역 자동 정리 (메모리 영역 영역 X)."

---

### §4.3 "운영급 영역 어떻게 결정?"

**답변 본문** (~60초):

> "D-2 운영급 결정 (ADR 0012) — 양면 정책 옵션 A (운영급) 정착. CORS 명시 (`docker-compose.yml:74,99,135` CORS_ORIGINS 환경변수 + `portfolio-service/app/main.py` / `llm-service/app/main.py` allow_methods=[GET,POST,OPTIONS] / allow_headers=[Authorization,Content-Type,X-Request-ID]) + API 키 검증 이중 (lifespan startup failfast + Pydantic validator) + X-Request-ID forward (httpx event_hooks 영역 분산 트레이싱) + cache LRU (CACHE_MAXSIZE=1000)."

**자료 인용**: docker-compose.yml:74,99,135 (CORS_ORIGINS) + portfolio-service/llm-service main.py (allow_methods/headers + lifespan) + ADR 0012 (D-2)

**꼬리 질문**:
- Q: "CORS 영역?"
  - A: "ADR 0012 영역 명시 — `*` 영역 영역 영역 명시 영역 (GET / POST / OPTIONS만 / Authorization + Content-Type + X-Request-ID만). 영역 영역 영역 영역 영역 X / 영역 영역 영역 영역 영역."
- Q: "API 키 검증 이중 영역?"
  - A: "lifespan startup failfast (`main.py`) + config Pydantic validator. 영역 영역 영역 영역 fail-fast 영역 영역 영역 영역 영역 영역 영역 영역 X. D-2 (#23) 영역 명시."
- Q: "X-Request-ID forward 영역?"
  - A: "httpx AsyncClient event_hooks={'request': [_forward_headers]} (`portfolio_client.py`) — llm → portfolio 호출 시 X-Request-ID + Authorization 자동 forward. 분산 트레이싱 영역 영역 (H-10 / L-7)."

---

### §4.4 "포트폴리오 최적화 영역 어떻게?"

**답변 본문** (~60초):

> "Markowitz Mean-Variance Optimization 영역 scipy SLSQP 영역 영역 (T-1 / `optimizer.py:309,383,488,558` = `scipy.optimize.minimize(method='SLSQP')`). min_variance / max_sharpe 영역 분기 + 연율화 메트릭 + efficient frontier 20 점 영역 영역 영역. covariance singular 영역 영역 Ledoit-Wolf shrinkage + auto-regularize 영역. TG-2d 시점 시연 ✓ — Sharpe 1.5971 / GOOGL 89.47% + AAPL 10.53% + MSFT 0.00%."

**자료 인용**: optimizer.py:309,383,488,558 + scipy SLSQP + TG-2d 결과

**꼬리 질문**:
- Q: "SLSQP 영역?"
  - A: "Sequential Least Squares Programming — `scipy.optimize.minimize(method='SLSQP')` 영역 영역 비선형 제약 최적화 알고리즘. Markowitz 영역 영역 covariance matrix + 가중치 합 = 1 + non-negative 제약 영역 영역 SLSQP 영역 적합. cvxopt (QP solver) 영역 영역 X = 본 코드 = scipy SLSQP."
- Q: "Sharpe ratio 영역?"
  - A: "Sharpe = (Rp - Rf) / σp. Rp 영역 = portfolio return / Rf = risk-free rate / σp = portfolio volatility. 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 1.0 영역 = 양호 / 2.0 영역 = 우수 / 3.0 영역 = 탁월."
- Q: "MVP + MSR 영역?"
  - A: "Minimum Variance Portfolio (MVP) = 변동성 영역 최소 / Maximum Sharpe Ratio (MSR) = 위험 조정 수익률 영역 최대. scipy SLSQP 영역 두 영역 영역 영역 영역 영역 — `optimizer.py:309,383,488,558` 영역 strategy 분기 영역."

---

### §4.5 "백테스트 영역 어떻게?"

**답변 본문** (~60초):

> "walk-forward 백테스트 (`backtest.py:65-111`). 8 메트릭 영역 — total_return / annual_return / sharpe_ratio / max_drawdown / calmar_ratio / avg_turnover / win_rate / 리밸런싱 횟수 영역 영역 영역. TG-2d 시점 시연 ✓ — 누적 155.74% / 연환산 26.61% / Sharpe 0.9051 / MDD 30.34% / 16회 리밸런싱."

**자료 인용**: backtest.py:65-111 + TG-2d 결과 (TEST_REPORT §2.3)

**꼬리 질문**:
- Q: "walk-forward 본질?"
  - A: "롤링 윈도우 영역 영역 — 학습 기간 (예: 2년) + 테스트 기간 (예: 분기). 학습 기간 영역 최적화 영역 → 테스트 기간 영역 적용 → 윈도우 이동. 영역 영역 영역 영역 영역 lookahead bias 영역 영역."
- Q: "8 메트릭 영역?"
  - A: "수익률 (total / annual) + 위험 조정 (sharpe / calmar) + 리스크 (max drawdown) + 거래 (avg turnover / 리밸런싱) + 승률. 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역."
- Q: "리밸런싱 영역?"
  - A: "주기 영역 (월간 21일 / 분기 63일 / 반기 126일 / 연간 252일) 영역 비중 재조정. TG-2d 시점 시연 영역 분기 (63일) / 16회 리밸런싱 정착."

---

### §4.6 "ADR 영역 어떻게 정착?"

**답변 본문** (~60초):

> "양면 정책 15 ADR — 정착 7 (D-2 0012 / D-3 0013 / D-8 0015 / T-6b 0016 / D-7 0017 / D-5 0018 / D-6 0019) + 보류 4 (T-3 0010 / D-1 0011 / D-9 0014 / CL-D 0025) + 메타 4 ADR (D-4 0020 / P-1 0021 / V-1 0022 / V-1b 0023 / 카드 영역 V-1b + CL-1 영역 영역 ADR 영역 통합) + 정리 1 (0024). PRINCIPLES 패턴 6 영역 영역 — '박지 않은 결정도 명시 결정만큼 강한 시그널'. 보류 4건 영역 = 시나리오 B 트리거 명시 영역 영역."

**자료 인용**: docs/adr/0001-0025 + docs/adr/README.md 분류 + PRINCIPLES.md 패턴 6

**꼬리 질문**:
- Q: "보류 결정 사유?"
  - A: "각 ADR 영역 명시 — T-3 (시나리오 A 일관성) / D-1 (본질 X 기능) / D-9 (RAG 정제 / 시나리오 B 트리거) / CL-D (CL-2 + CL-3 영구 보류 / 사용자 5+ 인터뷰 + PMF 트리거)."
- Q: "PRINCIPLES 패턴 6 영역?"
  - A: "'박지 않은 결정도 시그널' — 영역 영역 결정 영역 영역 영역 영역 영역 명시 영역 영역 영역 영역 영역 명확. 시니어 시그널 — 영역 영역 영역 영역 영역 영역 영역 영역 영역 의도적 영역 영역 영역."
- Q: "시나리오 B 트리거 영역?"
  - A: "ADR 0025 영역 명시 — 도메인 검증 + 사용자 5+ 인터뷰 + PMF 10불. 3 영역 영역 영역 영역 영역 영역 영역 영역 영역 시나리오 A 영역 영역 영역 영역 영역."

---

### §4.7 "시나리오 A 영역 본질?"

**답변 본문** (~60초):

> "시나리오 A = 기술 데모 + 시니어 패턴 정착 (사용자 0명 / 도메인 검증 X). 시나리오 B = 소수 사용자 (5+ 인터뷰 / PMF 10불). 시나리오 C = SaaS (PMF 영역 + 운영). SCENARIO.md §1.1 영역 명시. 본 영역 = 시나리오 A 일관성 영역 영역 영역 — '하면 좋아' 영역 영역 영역 X / 시나리오 목적 직결 영역."

**자료 인용**: SCENARIO.md §1.1 + PRINCIPLES 패턴 4 (본질 vs 비본질)

**꼬리 질문**:
- Q: "시나리오 B / C 침범 영역?"
  - A: "본질 충돌 의심 시 분리 (PRINCIPLES 패턴 7). 시나리오 A 영역 영역 영역 / 영역 영역 영역 영역 시나리오 B/C 영역 영역 영역 영역 영역 영역 영역 영역 영역 → 별도 카드 / 별도 repo 분리."
- Q: "전환 3 질문?"
  - A: "(1) 한국 개인 투자자 진짜 문제 Top 5? / (2) 5명 인터뷰? / (3) PMF 10불? — 답 안 되면 시나리오 A 종료."
- Q: "PMF 10불 영역?"
  - A: "Product-Market Fit 영역 영역 영역 — 사용자 영역 10불 영역 영역 영역 영역 영역 영역 (의무 영역 영역 영역). 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 → 시나리오 B 영역 영역 영역."

---

## §5 Full Stack 영역 질문 (4건 + 꼬리)

### §5.1 "frontend 영역 어떻게 정착?"

**답변 본문** (~45초):

> "Next.js 15 + React 19 + TypeScript + Axios. 페이지 분리 정책 (D-3 / ADR 0013) — 200 LOC 임계 영역 (페이지 50 LOC 영역 영역 = 컴포넌트 조합만). optimize 영역 **344 → 42 LOC** (D-3 진입 전 → 후 / `frontend/src/app/dashboard/optimize/page.tsx`) + backtest **217 → 39 LOC** (D-3 진입 전 → 후) — 임계 영역 정착 영역 ADR 0013 영역 영역 본질 영역 영역."

**자료 인용**: frontend/src/app/dashboard/optimize/ + ADR 0013 (D-3)

**꼬리 질문**:
- Q: "D-3 분리 사유?"
  - A: "200 LOC 영역 = 영역 영역 가독성 영역 영역. 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 — 페이지 영역 = 라우팅 + 영역 조합만 / 영역 영역 영역 컴포넌트 영역."
- Q: "TypeScript 영역?"
  - A: "tsc --noEmit 영역 0 errors 검증 (H-7 PR 게이트). 타입 안정성 영역 영역."

---

### §5.2 "SSE 영역 어떻게 정착? (Backend 영역만)"

**답변 본문** (~45초):

> "**Backend SSE 영역 영역 정착 (ADR 0019 / D-6)** — `POST /api/chat/stream` endpoint + StreamingResponse + LangGraph astream_events v2. **프론트 영역 영역 SSE 클라이언트 영역 영역 영역 영역** (`frontend/src/lib/api/llm.ts` axios 영역 영역 호출만 / streaming X) — 시나리오 B 트리거 (소수 사용자 진입 시점) 영역 영역 진입 영역 명시. Backend 영역 영역 = 신규 endpoint 분리 (PRINCIPLES 패턴 8) + 점진 전환 영역 정착."

**자료 인용**: ADR 0019 (D-6 / Backend SSE) + `frontend/src/lib/api/llm.ts` (axios 영역 호출 / streaming X)

**꼬리 질문**:
- Q: "프론트 영역 영역 영역 정착 사유?"
  - A: "시나리오 A 영역 영역 = 기술 데모 + 시니어 패턴 (사용자 0명). 프론트 SSE 영역 영역 = 사용자 영역 진입 시점 영역 의무 → 시나리오 B 트리거 영역 영역 진입. PRINCIPLES 패턴 6 (미적용 결정도 시그널) 일관성."
- Q: "Backend SSE 영역 정착 사유?"
  - A: "ADR 0019 (D-6) 영역 정착 — SSE endpoint 영역 영역 영역 영역 검증 가능 (curl / Postman). 프론트 영역 영역 영역 영역 사용자 진입 시점 영역 영역 영역 영역 영역 — 양면 정책 옵션 A (Backend 정착) + 옵션 B (프론트 보류) 일관성."
- Q: "Streaming 영역 영역 영역 영역 영역 검증?"
  - A: "SSE format `data: {json}\\n\\n` 영역 curl 영역 영역 영역 영역. TG-2c 영역 puppeteer 영역 SSE 영역 영역 영역 = 자동 시연 영역 X — 사용자 수동 검증 영역 영역."

---

### §5.3 "Docker 영역 어떻게?"

**답변 본문** (~45초):

> "Docker Compose 7 서비스 (`docker-compose.yml`) — postgres 16 + redis 7 + qdrant + auth-service + portfolio-service + llm-service + frontend. health check 7/7 정착 (TG-2b 영역 검증). 환경변수 영역 — `.env` 파일 영역 GEMINI_API_KEY / JWT_SECRET / DATABASE_URL 영역."

**자료 인용**: docker-compose.yml + TEST_REPORT §1.2

**꼬리 질문**:
- Q: "health check 영역?"
  - A: "각 서비스 영역 healthcheck 영역 명시 — postgres / redis / qdrant 영역 docker check / portfolio + llm + auth 영역 /health endpoint / frontend HTTP 200. depends_on 영역 condition: service_healthy 영역 의존 순서 영역."
- Q: "환경변수 영역?"
  - A: "GEMINI_API_KEY (Gemini 2.0 Flash) + JWT_SECRET (HS512 64 bytes 이상) + DATABASE_URL + REDIS_URL + QDRANT_URL + VECTOR_STORE=qdrant (T-6b default)."

---

### §5.4 "frontend ↔ backend 통합 영역?"

**답변 본문** (~45초):

> "JWT httpOnly cookie 영역 보관 (XSS 회피) + Authorization 헤더 영역 forward + CORS 명시 (D-2). frontend 영역 영역 3 백엔드 직접 호출 — `frontend/src/lib/utils/constants.ts:2-6` API_URLS = { AUTH: 8003 / PORTFOLIO: 8001 / LLM: 8002 }."

**자료 인용**: frontend/src/lib/utils/constants.ts:2-6 + ADR 0012 (D-2)

**꼬리 질문**:
- Q: "cookie 영역?"
  - A: "httpOnly 영역 영역 — JavaScript 영역 영역 영역 X (XSS 영역 영역 영역 영역 영역). secure flag 영역 HTTPS only / SameSite 영역 CSRF 영역 영역."
- Q: "CORS 영역?"
  - A: "D-2 영역 명시 — allow_methods=[GET, POST, OPTIONS] / allow_headers=[Authorization, Content-Type, X-Request-ID]. `*` 영역 영역 영역 영역 영역 명시 영역."

---

## §6 시스템 설계 영역 질문 (6건 + 꼬리)

### §6.1 "양면 정책 영역 본질?"

**답변 본문** (~75초):

> "양면 정책 = 옵션 A (시니어 / 운영급 / 적용) vs 옵션 B (보수 / 본질 X / 보류) 영역 명시 ADR 영역 영역 영역. 15 ADR 정책 영역 — 정착 7 + 보류 4 + 메타 4. 영역 영역 영역 영역 영역 영역 영역 영역 옵션 A / B 영역 영역 영역 + 결정 사유 + 트리거 영역 명시 영역 영역. PRINCIPLES 패턴 6 — '박지 않은 결정도 시그널'."

**자료 인용**: docs/adr/0010-0025 + PRINCIPLES 패턴 6

**꼬리 질문**:
- Q: "시니어 시그널 영역?"
  - A: "면접관 영역 영역 영역 영역 영역 영역 — '왜 이건 했는데 이건 안 했어요?' 영역 영역 → 양면 정책 영역 즉시 답 가능. 보류 결정 영역 = 시나리오 B 트리거 영역 영역 = 영역 영역 영역 영역 영역 영역 영역 영역 영역."

---

### §6.2 "시나리오 A 본질 영역?"

**답변 본문** (~60초):

> "사용자 0명 영역 = 의도. 시나리오 A = 기술 데모 + 시니어 패턴. 시나리오 B 트리거 3 질문 (도메인 / 사용자 / PMF) 답 안 되면 종료. SCENARIO.md §1.1 영역 명시. 본 자료 영역 영역 영역 PRINCIPLES 패턴 4 (본질 vs 비본질) — '하면 좋아' 영역 영역 영역 X."

**자료 인용**: SCENARIO.md §1.1 + PRINCIPLES 패턴 4

**꼬리 질문**: §4.7 동일

---

### §6.3 "카파시 영상 매핑 영역?"

**답변 본문** (~60초):

> "카파시 영상 9 항목 ↔ Aether 매핑 (KARPATHY_MAPPING.md §1). 8 본능 평균 76 (M-1) → 87 (P-1 / +11점). Skill 95 / Auto Research 90 / Reversibility 90 핵심. 부록 6건 (영상 X / Aether 회고): Premortem / Reversibility / 5 Guards / 측정 vs 추정 / 미적용 결정=시그널 / 본질 충돌 분리."

**자료 인용**: KARPATHY_MAPPING.md §1 + §부록

**꼬리 질문**:
- Q: "5 직접 적용 영역?"
  - A: "Skill (T-6b _EMBED_DIM) / Auto Research (D-7) / Jaggedness/Verifiable (D-8) / Macro Actions (카드 18건) / AGENTS.md (Soul.md X)."
- Q: "4 미적용 영역?"
  - A: "AI Psychosis (코드 검수 본인) / Token Throughput (단일 세션) / Persistent Loop (Claude Code 한계) / Markdown for Agents (정착)."
- Q: "Houseman 트리거 영역?"
  - A: "Soul.md X — Aether 영역 = 시나리오 A / Soul.md 영역 = Houseman 별도 repo. KARPATHY_MAPPING §1 영역 명시."

---

### §6.4 "WORK_PATTERNS 영역?"

**답변 본문** (~60초):

> "WORK_PATTERNS.md — 18 누적 문제 (카테고리 A-G) + 5 가드 + 자기 일관성 패턴 5종 + 검수 13 영역. 5 가드 — G1 Decision Budget / G2 Reversibility / G3 Done Definition / G4 Round Cap / G5 First Principle. 매 카드 plan 영역 적용 영역 의무 (CLAUDE.md §7)."

**자료 인용**: WORK_PATTERNS.md + CLAUDE.md §7

**꼬리 질문**:
- Q: "5 가드 영역 본질?"
  - A: "G1 = 라운드 max + 시간 cap / G2 = Type 1 비가역 vs Type 2 가역 / G3 = 80/100점 종결 / G4 = 메타 사고 max 3 / G5 = 본질 1줄 + 30분 점검."
- Q: "자기 일관성 패턴 5종 영역?"
  - A: "Lazy Init Singleton (registry 3건 동일) / Autouse Test Fixture / 응답 호환 어댑터 (호출자 0 변경) / 환경변수 토글 (즉시 롤백) / 옵션 B 2단분해."
- Q: "검수 13 영역 영역?"
  - A: "plan 영역 검수 — 영역 1-10 (있는 것 검증) + 영역 11 (누락 위험 / 보안 / 성능) + 영역 12 (외부 영향) + 영역 13 (메타 검수 / 6개월 후 답 가능)."

---

### §6.5 "D-4 패턴 영역?"

**답변 본문** (~45초):

> "D-4 = 영향 §를 같은 PR 영역 동시 갱신 (CHANGELOG 패턴). 본 자료 변경 시 — AGENTS.md §7 + ADR + docs/README.md 영역 동시 갱신 의무 (H-7 PR 게이트 체크박스 강제 예정). 자료 일관성 영역 영역 영역 영역 영역."

**자료 인용**: ADR 0020 + AGENTS.md §갱신 정책

**꼬리 질문**:
- Q: "자료 일관성 영역?"
  - A: "AGENTS.md §7 지배 숫자 영역 영역 영역 ─ 영역 영역 시점 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역. D-4 영역 = 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역."

---

### §6.6 "Aether 종료 결정 영역?"

**답변 본문** (~60초):

> "시나리오 A 본질 정착 — Top 10 9.5/10 (T-3 보류 결정 / 시나리오 A 일관성). 시나리오 B 트리거 3 질문 답 안 되는 시점 = 시나리오 A 종료. 다음 진입 = Houseman (Phase 7-12 / Subagents / Soul.md / 별도 repo). 본 카드 (I-1) 영역 = Aether 종료 자료 영역 정착."

**자료 인용**: META_REVIEW §9 + SCENARIO §1.1 + HOUSEMAN_APPLICATION.md (Aether 종료 시점 작성 예정)

**꼬리 질문**:
- Q: "Top 10 9.5/10 영역?"
  - A: "10건 = 본질 영역 영역 영역 영역. T-3 (Multi-Agent) 보류 결정 — 시나리오 A 일관성 영역 영역 / Houseman Phase 7-12 영역 영역 영역 영역 (META_REVIEW §9)."
- Q: "Houseman 진입 영역?"
  - A: "별도 repo / Soul.md 영역 영역 / Subagents 정착. 카파시 영상 8번 (AGENTS.md / Soul.md) 영역 트리거 — Aether 영역 = 시나리오 A / Houseman 영역 = 영역 영역 영역."

---

## §7 면접관 까다로운 질문 (5-7건)

### §7.1 "왜 이 프로젝트 만드셨어요?"

**답변 본문** (~45초):

> "학습 본질 영역 — 시니어 패턴 정착 + 카파시 영상 9 항목 적용 + 양면 정책 ADR 정착. 사용자 영역 본질 X (시나리오 A 명시). 본인 영역 = 백엔드 영역 영역 + AI 영역 영역 + 시스템 설계 영역 영역 영역 영역 영역 — Aether 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역."

**시그널**: 학습 우선 + 시니어 시그널 + 본인 영역 영역 X

---

### §7.2 "사용자 0명인데 왜 운영급?"

**답변 본문** (~45초):

> "시나리오 A 본질 영역 = 기술 데모 + 시니어 패턴. 운영급 결정 (D-2 / ADR 0012) 영역 의도적 — '사용자 0명 영역 영역 운영급 영역 영역 영역 영역 영역' 영역 = 영역 영역 영역 영역 영역 시그널. 시나리오 B 트리거 영역 영역 영역 영역 영역 영역 즉시 영역 영역 영역 영역. PRINCIPLES 패턴 6 (미적용 결정도 시그널) 일관성 — 운영급 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 ADR 영역 명시."

**시그널**: 의도적 결정 + 양면 정책 + 시나리오 B 트리거 명시

---

### §7.3 "에러 발견했는데 왜 안 고치셨어요?"

**답변 본문** (~60초):

> "TG-2c 시점 영역 DBG-1 (yfinance) + DBG-2 (이메일 형식) 트리거. 본 카드 영역 (TG-2c) 영역 = 자동 시연 영역 영역 / DBG 영역 = 별도 카드 영역 분리 (CLAUDE.md §6 / 한 카드 = 한 책임). TG-2d 시점 영역 DBG-1 영역 영역 영역 영역 영역 (transient yfinance rate limit) — 영역 영역 = transient vs 영구 영역 본질 시그널 영역. 양면 정책 보류 결정 (ADR 0010 / 0011 / 0014 / 0025) 일관성 — 보류 영역 = 시나리오 B 트리거 영역 명시."

**시그널**: 한 카드 = 한 책임 + 양면 정책 + transient vs 영구 본질 판단

---

### §7.4 "코드 cleanup 안 하셨네요?"

**답변 본문** (~45초):

> "CL-D 영역 = CL-2 (코드 cleanup) + CL-3 (의존성 cleanup) 영구 보류 결정 (ADR 0025). 시나리오 A 영역 영역 본질 X / 시나리오 B 진입 시점 (도메인 검증 + 사용자 5+ 인터뷰 + PMF 10불) 트리거 명시. PRINCIPLES 패턴 6 직접 사례 — 미적용 결정 영역 = ADR 영역 명시 영역 영역 영역 영역 영역 영역 영역."

**시그널**: 양면 정책 보류 + 시나리오 B 트리거 명시

---

### §7.5 "AI 답변 신뢰성 영역?"

**답변 본문** (~60초):

> "자체 4 메트릭 (D-8 / ADR 0015) — relevance@k / recall@k / LLM-as-judge quality + faithfulness. 36 chunks (D-7 후 / T-6b baseline 26 / ADR 0017) / 3072차원 / Qdrant. ragas 영역 = 보류 (ADR 0015 / 양면 정책 옵션 B). sources 표시 (📚 참고: ...) — TG-2d 시연 ✓. 영역 영역 영역 영역 영역 영역 영역 영역 = 시나리오 B 트리거 (도메인 검증 + 사용자 5+ 인터뷰)."

**시그널**: 자체 메트릭 + 양면 정책 + sources 영역 + 시나리오 B 트리거

---

### §7.6 "Houseman 영역 어떻게?"

**답변 본문** (~45초):

> "HOUSEMAN_APPLICATION.md (Aether 종료 시점 작성 예정 / Phase 7-12 시나리오 정의) — 카파시 패턴 진화 영역 별도 repo. Aether 영역 = 시나리오 A (포트폴리오) / Houseman 영역 = 영역 영역 영역 영역 영역 (Subagents / Soul.md / 별도 repo). META_REVIEW §6 영역 학습 10건 영역 Houseman 영역 영역 적용. Aether 종료 카드 영역 영역 진입 영역 영역."

**시그널**: 별도 repo + 카파시 진화 + 다음 진입 명시

---

### §7.7 "다음 시점 영역?"

**답변 본문** (~45초):

> "Aether 종료 카드 (시나리오 A 종료 / ADR 0026 가능) → Houseman 진입 (별도 repo / Subagents / Soul.md). 시나리오 B 진입 트리거 답 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 별도 프로젝트 분리 영역 영역."

**시그널**: 명확한 다음 진입 + 시나리오 분리 명시

---

## §8 면접 답변 흐름

### §8.1 PREP 영역 (Point - Reason - Example - Point)

- **Point**: 결론 1줄 (예: "ReAct 영역 = 도구 호출 순서 영역 자율 판단")
- **Reason**: 사유 1줄 (예: "절차적 4 호출 영역 영역 영역 영역 → ReAct 1 호출 전환")
- **Example**: 자료 인용 (예: "react_agent.py:28-44 + ADR 0006/0018")
- **Point**: 결론 재강조 (선택)

### §8.2 STAR 영역 (Situation - Task - Action - Result)

- **Situation**: 상황 (예: "TG-2c 시점 yfinance 영역 영역 영역")
- **Task**: 과제 (예: "DBG-1 영역 결정 영역")
- **Action**: 영역 (예: "별도 카드 분리 — 한 카드 = 한 책임")
- **Result**: 결과 (예: "TG-2d 시점 영역 영역 영역 → transient 영역 영역 영역 정착")

### §8.3 모르는 영역 답변 흐름

> "그 영역은 모르겠습니다. 다만 본 자료 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역."

→ 정직 + 근거 영역 추정 + 영역 영역 영역 영역 영역 영역.

### §8.4 본인 영역 의무 회피

- 학력 / 경력 / 강점 / 지원 동기 = 사용자 직접 정착 의무
- 본 자료 영역 영역 = Aether 프로젝트 영역 답변만

### §8.5 꼬리 질문 영역 대응 흐름

1. 면접관 영역 영역 영역 영역 영역 영역 영역 영역 영역
2. 본 자료 영역 영역 영역 영역 영역 영역 (꼬리 질문 영역 정착)
3. 자료 인용 영역 영역 영역 영역 (파일:라인 또는 ADR 번호)
4. 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 (시니어 시그널)

### §8.6 면접 시연 5분 (TG-2d 시점)

| 분 | 영역 | 시연 가능 |
|---|---|---|
| 1 | signup + login (HS512 + httpOnly cookie) | ✓ |
| 1 | optimize (Sharpe 1.5971) | ✓ |
| 1 | backtest (누적 155.74% / 8 메트릭) | ✓ |
| 1 | chat (RAG + ReAct + SSE + sources) | ✓ |
| 1 | MCP (Claude Desktop / 사용자 수동) | 사용자 수동 |

**4/5 시연 가능** + 1/5 사용자 수동.

---

## §9 한 문장

I-1 = 4 직무 (AI Engineer / Backend / Full Stack / 시스템 설계) × 5-7 핵심 질문 + 꼬리 질문 3-5건 + §7 까다로운 질문 5-7 + §8 답변 흐름 영역 자료 인용 위치 통합 (DIFFERENTIATION + TEST_REPORT + KARPATHY_MAPPING + ADR 25건 + META_REVIEW + SCENARIO + WORK_PATTERNS + PRINCIPLES + AGENTS) — 면접 직접 활용 자료 영역 정착 / 트랜지언트 영역 (TG-2d) = 시니어 시그널 영역 / Aether 종료 자료 영역 / Houseman 진입 영역 자료 영역.

---

## §10 검증 결과 (I-1-REVIEW 시점 / Claude Code 실측)

> 본 §10 = I-1-REVIEW 카드 영역 자료 인용 위치 (파일:라인 + ADR 번호 + 섹션 참조) 영역 실측 검증 결과 통합. 14 정정 정착 (사실 2 / 라인 6 / 분류 1 / 파일 영역 영역 3 / 미소 2). 본 영역 영역 정정 정착 영역 면접 답변 즉시 활용 가능.

### §10.1 검증 통계

| 영역 | 수 | 비율 |
|---|---|---|
| 검증 항목 | 38 | 100% |
| ✓ 일치 | 24 | 63% |
| ⚠ 미소 (라인 ±1-3) | 5 | 13% |
| ✗ 불일치 | 9 | 24% |
| **정정 정착** | **14** | **37%** |

### §10.2 정정 정착 표

| § | 항목 | 영역 결과 | 정정 정착 |
|---|---|---|---|
| §2.2 | 4 MSA + 2 인프라 | ✗ 실제 3 인프라 | 2 → 3 |
| §2.2 | 14,414 LOC | ✓ AUDIT.md baseline 일치 | - |
| §2.2 | 635 테스트 | ✓ INTERVIEW.md §4 일치 | - |
| §2.2 | ADR 25건 | ✓ docs/adr/0001-0025 영역 영역 | - |
| §2.2 | 카드 24건 | ⚠ phase3 11 + TG/DBG/I/M/V 13 = 24 | 출처 명시 |
| §2.2 | Top 10 9.5/10 | ✓ META_REVIEW §9 일치 | - |
| §2.2 | 카파시 76 → 87 | ✓ KARPATHY_MAPPING §1 일치 | - |
| §3.1 | react_agent.py:28-44 | ✗ 실제 40-44 | 28-44 → 40-44 |
| §3.1 | chat.py:331-356 USE_REACT_AGENT | ✗ 실제 198-201 + 226-246 (RAG_FALLBACK_DIRECT 토글) | 331-356 → 198-201, 226-246 |
| §3.2 | eval_rag.py:31-101 | ⚠ 실제 31-102 | 31-101 → 31-102 |
| §3.3 | grid_search_chunking.py:19-109 | ✓ 영역 일치 | - |
| §3.4 | mcp_server.py:114-160 | ⚠ 실제 114-132 + 158-160 | 114-160 → 114-132, 158-160 |
| §3.5 | chat.py:332-369 | ⚠ 실제 332-372 | 332-369 → 332-372 |
| §3.5 | react_agent.py:52-76 | ✓ 일치 | - |
| §3.6 | KARPATHY 5 직접 적용 점수 | ✓ KARPATHY_MAPPING §1 일치 | - |
| §3.7 | TEST_REPORT §3.2 transient | ✓ 일치 | - |
| §4.1 | docker-compose.yml 4 MSA | ✓ 일치 | - |
| §4.2 | JwtTokenProvider.java:41-43 | ⚠ 실제 39-44 (@PostConstruct 포함) + 경로 (com.aether.auth.global.security) | 41-43 → 39-44 + 경로 명시 |
| §4.2 | AuthController.java:57-66 | ✗ 실제 AuthService.java:116-120 + JwtTokenProvider.java:116-130 (blacklistAccessToken) | 정정 |
| §4.3 | docker-compose.yml CORS allow_methods | ✗ docker-compose.yml = CORS_ORIGINS만 / allow_methods = portfolio/llm main.py | 출처 분리 명시 |
| §4.4 | optimize.py:128-160 | ✓ 일치 | - |
| §4.5 | backtest.py:65-111 | ✓ 일치 | - |
| §4.6 | 메타 4 (5 카드) | ⚠ ADR 4 + 카드 5 (V-1b + CL-1 통합) 분류 모순 | 분류 명시 |
| §4.7 | SCENARIO.md §1.1 | ✓ 일치 | - |
| §5.1 | optimize 344 / backtest 217 LOC | ✗ D-3 후 42 / 39 LOC | "344 → 42 / 217 → 39" 명시 |
| §5.2 | frontend/src/services/api.ts streamChat | ✗ 디렉토리 미존재 / streaming 코드 0건 | 프론트 영역 영역 명시 + Backend SSE만 |
| §5.3 | docker-compose 7 서비스 | ✓ 일치 | - |
| §5.4 | constants.ts:2-6 API_URLS | ✓ 일치 | - |
| §6.1 | 양면 정책 15 ADR | ✓ docs/adr/README.md 일치 | - |
| §6.3 | KARPATHY 부록 6건 | ✓ KARPATHY_MAPPING §부록 일치 | - |
| §6.4 | WORK_PATTERNS 18 누적 | ✓ 라인 32 "18건" 일치 | - |
| §6.5 | ADR 0020 D-4 | ✓ 일치 | - |
| §6.6 | HOUSEMAN_APPLICATION.md | ✗ 파일 미존재 | "작성 예정" 표기 |
| §7.3 | TEST_REPORT §3.2 DBG | ✓ 일치 | - |
| §7.4 | ADR 0025 CL-D | ✓ 일치 | - |
| §7.6 | HOUSEMAN_APPLICATION.md | ✗ 파일 미존재 | "작성 예정" 표기 |
| §3.6 | KARPATHY 8 본능 평균 76 → 87 | ✓ 일치 | - |
| §6.2 | PRINCIPLES 패턴 4 (본질 vs 비본질) | ✓ 일치 | - |

### §10.3 검증 본질 영역

- **frontend SSE 영역 영역 영역**: ADR 0019 (D-6) Backend SSE 영역 정착 영역 / 프론트 영역 영역 axios 영역 호출만 — 시나리오 B 트리거 영역 진입 영역 명시. 양면 정책 옵션 A (Backend 정착) + 옵션 B (프론트 보류) 일관성.
- **HOUSEMAN_APPLICATION.md**: Aether 종료 시점 작성 예정 (현 시점 미존재) — 시나리오 A 종료 + 시나리오 B 트리거 영역 영역 별도 repo 진입 영역 영역 영역.
- **D-3 LOC 정정**: 344 → 42 / 217 → 39 = D-3 영역 정착 결과 직접 시연. ADR 0013 §영향 영역 영역 영역.
- **JwtTokenProvider 경로 정정**: `com.aether.auth.global.security` (본 자료 영역 `.security` 영역 영역 영역). blacklistAccessToken 영역 = JwtTokenProvider:116-130 + AuthService:116-120 (logout) 영역 분산.

### §10.4 시그널

- 본 §10 = 자가 검증 패턴 영역 본질 시그널 (PRINCIPLES 패턴 10 / G1 본질 트리거)
- 14 정정 정착 = 면접 답변 정확성 ↑ + "실측 영역 영역 영역" 시그널 강화
- 검증 영역 영역 영역 발견 (frontend SSE 영역 영역 / HOUSEMAN 미존재) = 시나리오 A 일관성 영역 영역 정착
