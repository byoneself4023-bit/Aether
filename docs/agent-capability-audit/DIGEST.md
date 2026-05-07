# DIGEST — V-1 진입 자료 추출 (누적 자료 11건 + KARPATHY_LECTURE.md 통합)

> **카드**: V-0 (V-1 진입 자료 추출 / 일시 자료)
> **작성일**: 2026-05-07
> **본질**: 누적 자료 10 파일 + `KARPATHY_LECTURE.md` (총 11 자료 / ~5,758 LOC + ADR 21건) 핵심 영역만 추출 → 사용자 옆 Claude (= 본 대화 Claude) 정독 자료 정착 → V-1 카드 (누적 자료 검증 + KARPATHY §1 재작성 보고서 / V-1b 트리거) 진입.
> **결론 한 줄**: KARPATHY_MAPPING.md §1 일치율 25% (2/8) 발견 — 6건 쿠카 영역 / 7건 영상 본문 누락. V-1b 본격 트리거 = §1 재작성 의무.

---

## §1 자료 영역 종합 표 (11 자료 통합)

| # | 자료 | 위치 | LOC | 핵심 영역 (한 줄) | 갱신 카드 |
|---|---|---|---|---|---|
| 1 | `AGENTS.md` | repo root | 302 | What — 지배 숫자 / §7 핵심 결정 표 / 카드 14건 영향 | H-1 / H-1c / D-N / P-1 |
| 2 | `PRINCIPLES.md` | `docs/agent-capability-audit/` | 612 | §1-§7 시니어 판단 7 패턴 + §8-§10 (P-1) 신규 패턴 | P-1 / D-5 / D-6 / D-7 / T-6b |
| 3 | `KARPATHY_MAPPING.md` | `docs/agent-capability-audit/` | 174 | 카파시 8 본능 (연역) ↔ 14 카드 (귀납) 매핑 + 면접 답변 5 영역 | P-1 |
| 4 | `WORK_PATTERNS.md` | `docs/agent-capability-audit/` | 885 | 18 누적 문제 + 체크리스트 A-G + 자기 일관성 5종 + 검수 13 영역 | M-1 / 누적 |
| 5 | `SCENARIO.md` | `docs/agent-capability-audit/` | 125 | 시나리오 A 정착 + B/C 트리거 + 정착 사례 | C-1 / 누적 |
| 6 | `META_REVIEW.md` | `docs/agent-capability-audit/` | 707 | 시니어 메타 회고 — Phase 1-7 + Houseman Phase 7-12 학습 | M-1 |
| 7 | `AUDIT.md` | `docs/agent-capability-audit/` | 238 | D-4 종합 — 14 카드 누적 + WORK_PATTERNS 18 검증 + 메트릭 | D-4 (ADR 0020) |
| 8 | `VERIFICATION.md` | `docs/agent-capability-audit/` | 386 | F-1 5 기능 검증 + JWT HS512/HS256 불일치 발견 | F-1 → F-1a |
| 9 | `D9_PRE_CHECK.md` | `docs/agent-capability-audit/` | 245 | D-9 보류 분기 3 진단 (정제 대상 부재) | D-9 (ADR 0014) |
| 9 | `D8_PRE_CHECK.md` | `docs/agent-capability-audit/` | 306 | D-8 분기 2 진단 (자체 4 메트릭 / ragas 미도입) | D-8 (ADR 0015) |
| 9 | `MCP_FAIL_DIAGNOSIS.md` | `docs/agent-capability-audit/` | 163 | T-6b 진입 전 MCP 4 fail = pre-existing 환경 의존성 진단 | T-2c |
| 10 | ADR 0001-0021 | `docs/adr/` | — | 결정 근거 21건 (양면 정책 11 ADR 정립 / 0011-0021) | 누적 (15 카드) |
| 11 | `KARPATHY_LECTURE.md` ★ | `docs/agent-capability-audit/` | 605 | 카파시 인터뷰 본문 14 영역 + 9 본능 + 직접 인용 + KARPATHY §1 비교 | V-0 (untracked → tracked) |

**총 자료 LOC**: ~5,758 (+ ADR 21건). 본 디제스트 압축 비율: ~1/6.

---

## §2 자료별 핵심 영역 추출

### §2.1 AGENTS.md (~50 LOC 추출)

**본질**: What (코드 사실 / 지배 숫자 단일 페이지). 갱신 정책 — 영향 §를 같은 PR에 동시 수정.

**§7 지배 숫자 (변경 시 인용 위치 동시 갱신)**:

| 지표 | 값 | 근거 |
|---|---|---|
| 백엔드 서비스 수 | 4 (auth / portfolio / llm / frontend) + 인프라 2 (postgres / redis) | docker-compose.yml:6-40 |
| 테스트 합산 | 535 (270/195/70) — D-1로 −20 (`#22`) | §4 |
| 도구 등록 (tool_registry) | **5종** — D-5 RAG 통합 (`search_knowledge_base` 추가) | §10 + ADR 0018 |
| 등록 프롬프트 수 | 8 (v1.0) — T-1b로 react_system_prompt 추가 | prompt_registry.py + ADR 0006 |
| chat.py LLM 호출 | **ReAct 1 호출** (default) / 절차적 4 호출 (fallback) | §10 + ADR 0006 |
| Gemini SDK | google-genai 1.74 (legacy 제거) — H-6 디벨롭 | requirements.txt + ADR 0007 |
| JWT 알고리즘 | **HS512 단일** — F-1a (`#21`) 통일 | §9 + ADR 0004 v2 |
| Vector store | **Qdrant default** (T-6b) / chromadb fallback | ADR 0009 + 0014 + 0016 |
| RAG Chunking | chunk_size=500 / overlap=300 (D-7 grid 9 조합) | ADR 0017 |
| RAG 도구 통합 | ReAct 5번째 도구 / chat.py fallback `RAG_FALLBACK_DIRECT=true` (default) | ADR 0018 |
| Streaming SSE | `POST /api/chat/stream` 신규 (기존 0 변경) — 우대 요건 4 직격 | ADR 0019 |
| D-4 Audit baseline | 14 카드 머지 / WORK_PATTERNS 17/18 해소 / **14,414 LOC** / 635 테스트 / 19→20 ADR / 누적 자료 3,354 LOC | AUDIT.md + ADR 0020 |
| PRINCIPLES 패턴 | 7 → **10** (P-1 §8/§9/§10 신규) | ADR 0021 |
| KARPATHY 매칭 | 8 본능 평균 76 → **87점** (Skill 95 / Auto Research 90 / Reversibility 90) | ADR 0021 |
| Top 10 진행 | **9.5/10** (T-3 Multi-Agent 보류) | ADR 0010 |

**§3 레이어 경계 (llm-service)**: `routers → agents → services → 외부 (Gemini / portfolio-service / Qdrant)`. 단방향 의무. agents/는 services를 도구로 사용 / services는 agents를 모름 (의존 역전).

**§5 프롬프트 컨벤션**: 모든 LLM 호출은 `get_registry().get(name, version)` 단일 진입점. JSON 응답 schema는 Pydantic `model_json_schema()` 정렬 등록. `{` `}` escape 정책 (`{{ "{" }}` / `{{ "}" }}`).

**§8 작업 시작 체크리스트 (모든 PR 공통 7건)**: (1) 카드 §4 변경 대상 파일 / (2) 선행 작업 / (3) §3 레이어 경계 / (4) §5 프롬프트 컨벤션 / (5) §4 빌드 명령 / (6) CLAUDE.md §4 위험 작업 / (7) AGENTS.md 갱신 의무.

**§9 인증 + 분산 트레이싱 (H-10 + L-7)**: JWT HS512 공유 비밀키 / `app/middleware/auth.py::verify_jwt` dependency / `httpx.AsyncClient` `event_hooks={"request": [_forward_headers]}` 등록 → `X-Request-ID` + `Authorization` 자동 forward / 토큰 로그 마스킹 (`Bearer ***`) / autouse `_bypass_jwt` fixture (기존 232+ 테스트 무수정 통과).

**§10 Agent Architecture (T-1a + H-2)**: `app/agents/` — `BaseAgent` 추상 + `ToolRegistry` lazy init (`prompt_registry` 미러 패턴) + `portfolio_tools.py` 4 @tool 래퍼 + `react_agent.py` (T-1b ReAct + `_extract_tool_results` 어댑터). YAGNI: Supervisor / Subgraph / Memory는 T-3 진입 시 도입.

**§11 MCP 서버 (T-2)**: `portfolio-service/app/mcp_server.py`에서 `Server("aether-portfolio")` stdio 4 도구 외부 노출. 호출 체인: `외부 LLM → stdio subprocess → mcp_server.py → app/services/* (라우터 우회)`. L-7 X-Request-ID 통합 (옵션 A) — `arguments.pop("_request_id")` → ContextVar set/reset.

**쿠카 영역 영향 직격**: §7 행 누적 + 카드별 D-N 추적. 카드 14건 영향 → §7 (지배 숫자) + §10 (Agent) + §11 (MCP) 행 추가. 갱신 정책 = 영향 §를 같은 PR에 동시 수정 (CHANGELOG처럼 운영).

---

### §2.2 PRINCIPLES.md (~80 LOC 추출)

**본질**: 모든 프로젝트 공통 본질. 매 카드 plan + 의심 시 + 결정 분기점 참조.

**🌱 본질 메시지 핵심**:
- Jensen Huang 인용: *"Software development is dead. Everyone is software developer."* — 차별화 = "AI를 잘 쓰기"
- 랄프톤 우승자 (Orchid): *"AI can do a lot of things. You just need to ask it how it can. Ask it to research how it can achieve something."*
- 본질 5층: Layer 5 본질 사고 (사람만) → Layer 1 실행 (AI 자동화). 시니어 = Layer 5/4 강한 사람.

**🎯 핵심 원칙 5종**:
1. *"내가 원하는 게 뭔지"* 가장 중요 — 시간 cap 박아 본질 강제 명확화
2. *"리뷰 안 하면 망함"* — 가제탈 = 자동화 실패 정상 / 검증 시스템 의무
3. *"평가 시스템 자체를 AI가 구축"* — WORK_PATTERNS / 검증 체크리스트 / 의사결정 가드
4. *"AI에게 연구하라고 시켜라"* — 5 위임 패턴 (결과 명시 / 평가 기준 / 미래 시점 / 검증 시스템 / 메타 분석)
5. *"본질 결정은 AI가 못 한다"* — AI 가능 95% (코드 / 테스트 / 문서 / 분석) vs AI 불가 5% (본인 진로 / 비즈니스 / 면접 답변)

**🧠 시니어 판단 패턴 1-7 (귀납 — Aether 카드 회고)**:
1. 카드 시작 전 사고 5 단계 (본질 / 시나리오 / 우선순위 / 깊이 / 위임)
2. 위험 발견 시 분기 (Type 1 비가역 / Type 2 가역 / 후속 분리 / 보류)
3. 카드 우선순위 (차별화 / 의존성 / Big Bet / 시나리오 적합)
4. 본질 vs 비본질 (시나리오 직결 vs "하면 좋아 보임" / 면접 시그널 vs 외부 시선)
5. 메타 인지 (G1 본질 트리거 / 자가 점검 4 레벨 / 결정 마비 cap / 가드 재점검)
6. **박지 않은 결정 = 명시한 결정만큼 강한 시그널** (T-3 보류 / ADR 0010)
7. **본질 충돌 의심 시 두 본능 분리 검증** (3 단계 + 답 흔들림 자가 인지)

**§8/§9/§10 (P-1 신규 / D-5/D-6/D-7/T-6b 발굴)**:
8. **신규 endpoint 분리 = 점진 전환 본능** (D-5 `RAG_FALLBACK_DIRECT` / D-6 `/api/chat/stream` 신규) — frontend 회귀 0
9. **Auto Research 본능 = 인간 결정 최소화** (D-7 grid 9 조합 / chunk_size=500/overlap=300 / relevance@k 0.7222 → 0.7413)
10. **G1 본질 트리거 발견 시 즉시 정정 본능** (T-6b _EMBED_DIM 768 stale → 3072 정정 / 외부 SDK 영역 차이 인지)

**🌐 시나리오 A/B/C 분류 + 진입 트리거 3 질문 (도메인 / 사용자 / PMF)**.

**🚦 자가 점검 4 레벨**: L1 카드 / L2 프로젝트 본질 / L3 AI 협업 / L4 외부 시각.

**쿠카 영역 메타 패턴**: §6 (박지 않은 결정) + §10 (G1 본질 트리거) = 시니어 시그널 강함. PRINCIPLES = 범용 / SCENARIO = Aether 한정 분리 본능.

---

### §2.3 KARPATHY_MAPPING.md (~80 LOC 추출)

**§1 카파시 8 본능 정의 (쿠카 작성 / V-1b 트리거 영역)**:

| # | 본능 | 영상 시간대 (추정) | 본질 |
|---|---|---|---|
| 1 | Skill Issue | ~2:05 | 본인 한계 인지 / 사용자 본질 의무 |
| 2 | Auto Research | ~3:18 | 인간 직관 X / 메트릭 자동 비교 |
| 3 | Premortem | ~5:42 | 위험 시나리오 6+ 사전 예측 |
| 4 | Reversibility | ~7:10 | Type 1 / 2 / 3 |
| 5 | 5 Guards | ~9:30 | G1-G5 |
| 6 | 박지 않은 결정 = 시그널 | ~12:15 | 미적용 결정 + 트리거 명시 |
| 7 | 본질 충돌 분리 | ~14:50 | 두 본능 명시 → 분리 검증 |
| 8 | 측정 vs 추정 | ~17:20 | 실측 / 가설 회피 |

**※ 단서 본문 인용**: *"본 §1 시간대는 본 대화 누적 추정. 정확 검증 의무 시 카파시 영상 재확인."* → V-0 검증 결과 = 영상 본문 X (KARPATHY_LECTURE.md §16 비교 표 참조).

**§2 매칭 점수 진화 표 (시작 → P-1)**:

| # | 본능 | 시작 (M-1) | D-4 후 | 현재 (P-1) | 진화 사유 |
|---|---|---|---|---|---|
| 1 | Skill Issue | 70 | 90 | **95** | T-6b 768 stale 발견 |
| 2 | Auto Research | 70 | 85 | **90** | D-7 grid search |
| 3 | Premortem | 75 | 85 | **88** | 14 카드 위험 시나리오 6+ 일관성 |
| 4 | Reversibility | 80 | 88 | **90** | Type 1/2/3 + 환경변수 토글 |
| 5 | 5 Guards | 78 | 87 | **88** | G1-G5 매 카드 적용 |
| 6 | 박지 않은 결정 | 75 | 85 | **88** | ADR 0010 / 0011 / 0014 보류 명시 |
| 7 | 본질 충돌 분리 | 75 | 80 | **80** | 자가 인지 영역 미흡 |
| 8 | 측정 vs 추정 | 70 | 80 | **85** | F-1 / D-8 / D-7 / D-6 baseline 실측 |
| 평균 | — | **76** | **85** | **87** | +11점 진화 |

**§3 8 × 14 카드 매핑 표 (충족 합계)**:
- 본능 3 (Premortem) / 4 (Reversibility) — 13건 (거의 모두)
- 본능 5 (Guards) — 12건
- 본능 8 (측정) — 11건
- 본능 1 (Skill Issue) — 6건 (T-6b 본격 진화)
- 본능 7 (본질 충돌 분리) — 5건 (자가 인지 미흡)
- 본능 2 (Auto Research) — 2건 (D-7 본격 정착)

**§4 미적용 영역 7건 (시나리오 B 트리거)**: 본격 audit / Multi-Agent T-3 / WebSocket 양방향 / 의존성 cleanup / 점수 객관화 / 영상 시간대 검증 / 테스트 cov 90%+.

**§5 쿠카 영역 진화 사례** (META_REVIEW 인용): Houseman Phase 7-12 학습 (학습 5 / 8 / 9) + Skill Issue 진화 (T-6b).

**§6 면접 답변 매핑 5 영역 + 꼬리 질문**:
- 영역 1: AI Agent 자율 판단 (ReAct 4 → 5 도구 / SSE)
- 영역 2: 시나리오 A 본질 (양면 정책 11 ADR)
- 영역 3: 양면 정책 11 ADR (정착 / 보류)
- 영역 4: 우대 요건 매칭 (SSE / RAG eval / Chunking / Multi-Agent 보류)
- 영역 5: 본인 영역 진화 (Skill Issue 70 → 95)

---

### §2.4 WORK_PATTERNS.md (~50 LOC 추출)

**본질**: "같은 실수 반복하지 않는 것 = 시니어 본질." 매 카드 plan 시 적용 순서 (Step 1-5): 체크리스트 A-G → 누적 문제 18건 검색 → 자기 일관성 패턴 5종 → 메모리 통합 4 레이어 → plan에 "WORK_PATTERNS 적용 결과" 섹션 정착.

**18 누적 문제 (해소 17 / 부분 1)**:

| 카테고리 | 문제 | 해소 상태 |
|---|---|---|
| A 작업 트리 | 1 (config.py 혼재) / 2 (머지 cleanup) / 14 (uncommitted 경고) | 해소 ✓ |
| B 머지 cleanup | 3 (Co-Authored-By) / 15 (`gh pr merge` 동작) | 해소 ✓ |
| C 사용자 prompt | 4 (응답 키) / 5 (ADR 번호) / 6 (변경 대상 누락) | 해소 ✓ |
| C 외부 SDK | 7 (ToolMessage.content) / 11 (FutureWarning) / 12 (단위 변환) / 13 (응답 어댑터) / 18 (의존성 베이스라인) | 해소 4 / 부분 1 (FutureWarning) |
| D 5 가드 | 9 (의사결정 무한 루프) | 해소 ✓ |
| E 문서 | 8 (측정 추정) / 10 (지배 숫자 중복) / 16 (ADR 번호) / 17 (후속 카드 누적) | 해소 ✓ |
| F 자동화 | F-패턴 (검증 + 분기 + 머지) | 정착 ✓ |

**🛡️ 종합 사전 예방 체크리스트 A-G**: 작업 트리 / prompt 검증 / 외부 라이브러리 / 5 가드 / 커밋 위생 / 머지 cleanup / 문서 갱신.

**📊 자기 일관성 패턴 5종**:
1. Lazy Init Singleton (prompt_registry / tool_registry / chroma_client)
2. Autouse Fixture + Marker Opt-in (`_bypass_jwt` / `_disable_react_agent`)
3. 응답 호환 어댑터 (호출자 0 변경 — H-6 / T-1b / T-6 / T-6b)
4. 환경변수 즉시 롤백 (`USE_REACT_AGENT` / `RAG_FALLBACK_DIRECT` / `VECTOR_STORE`)
5. 옵션 B 2단 분해 (T-1a 인프라 + T-1b 동작)

**🔍 plan 검수 13 영역 가이드 (시니어 검수 본질 — 인용 위치 §657-783)**:
- **영역 1-10 (있는 것)**: 측정 / 5 가드 / WORK_PATTERNS 적용 / 변경 대상 / 어댑터 / Step 분해 / 위험 시나리오 / 검증 / 문서 갱신 / 자기 점검
- **영역 11-13 (없는 것)**: 누락 위험 (보안/성능/동기화) / 외부 영향 (서비스/CI/모니터링) / 메타 시그널 (다른 개발자 / 6개월 후 / 면접관 / 결정 근거 추적)

**🧠 메모리 통합 4 레이어**:
- Layer 1 (메모리 #21) — Big Bet 시 6 패턴 (Multi-Persona / Pre-mortem / Steelmanning / 가중치 / 시나리오 / 메타 검수)
- Layer 2 (메모리 #22) — 5 가드 (Decision Budget / Reversibility / Done Definition / Round Cap / First Principle)
- Layer 3 (메모리 #23) — 의사결정 진행 패턴 (옵션 N → 디테일 분석 + 추천 → 그대로 진행 / Type 2 가역만)
- Layer 4 (본 문서) — 작업 패턴 + 사전 예방 (누적 문제 18건 / 체크리스트 A-G / 자기 일관성 5종)

**적용 시나리오**: A 단순 카드 / B Big Bet 결정 (T-3 분해 등) / C 옵션 비교 결정.

**F-패턴 (메모리 #19 진화형)**: 사용자 한 줄 프롬프트 → Claude 자동 검증 + 분기 + 머지 4단계 처리. 사례 — T-2 PR #12 머지 직전 `git diff llm-service/app/config.py` 검증 분기 (pre-existing 100% 판정).

---

### §2.5 SCENARIO.md (~40 LOC 추출)

**본질**: Aether 한정 시나리오 결정 + 정착 사례 + 면접 답변. 범용 원칙 = PRINCIPLES.md / Aether 한정 = 본 문서 (의도된 분리).

**🌐 Aether 시나리오 결정**: **시나리오 A** (기술 데모 / 사용자 0명 / 포트폴리오 / 면접용 — Top 10 종료 + 면접 답변 가능 = 완성 조건).

**결정 사유**: (1) 포트폴리오 출발점 / (2) 도메인 검증 X / (3) 시니어 시그널 (LangGraph / ReAct / MCP / RAG / JWT / Pydantic 풀 스택) / (4) 시나리오 혼동 방지.

**시나리오 전환 트리거 3 질문**: 도메인 (Top 5 문제) / 사용자 (5명 인터뷰) / PMF (10불 가치).

**🎯 면접 답변 (시니어 시그널)**:
> *"Aether는 AI Agent 시스템 학습 + 시니어 패턴 정착이 목적이었어요. LangGraph / ReAct / MCP / RAG / JWT / Pydantic 풀 스택을 실제로 박아본 사례입니다. 실리콘밸리 랄프톤 우승자 발언처럼 'AI에게 어떻게 해야 하는지 연구하라고 시키는' 패턴을 정착시켰고, 작업 중 발생한 18건 누적 문제를 시스템화해서 같은 실수 반복도 차단했어요. 실서비스 진입은 별도 프로젝트로 도메인 검증부터 시작할 거예요."*

**🛠️ 정착 사례 5종 (PRINCIPLES.md 원칙 3 — "평가 시스템을 AI가 구축")**:
- **작업 패턴 누적**: WORK_PATTERNS.md (18 문제 7 카테고리 + 체크리스트 A-G + 자기 일관성 5 + 검수 13 영역)
- **검증 시스템**: VERIFICATION.md (5 측면 + 메타 = 6 영역 35건 grep / pytest / git log 검증) + EVOLUTION_verification.md (1h cap / Type 2)
- **기술 결정 근거**: TECH_DECISIONS.md (8 기술 — 1순위 5 + 2순위 3 / 무엇을 원했나 / 후보 비교 / 트레이드오프 / 면접 답변 / 마이그레이션 트리거)
- **의사결정 자동화**: 5 가드 (메모리 #22) + 6 패턴 (메모리 #21 Big Bet) + 메모리 #21-#28 행동 패턴
- **진화 회고 + 보류 결정**: EVOLUTION.md (Top 10 회고 / 9 카드 본격) + T-3 Multi-Agent 보류 결정 (ADR 0010 + Houseman 동일 의사결정 일관성 = 학습 적용 통합)

**🚦 자가 점검 (Pre/Post 카드)**:
- Pre: 시나리오 A 적합 / B/C 침범 X / PRINCIPLES Level 1-4 / 첫 프롬프트 4 요소
- Post: WORK_PATTERNS 신규 / TECH_DECISIONS 갱신 / EVOLUTION_developed 측면 / EVOLUTION_verification 항목

**한 문장**: *"Aether는 시나리오 A다. 명확히 분리하는 게 시니어 시그널."* — 방향 흐트러질 때 PRINCIPLES → SCENARIO 순서로 다시 읽기.

---

### §2.6 META_REVIEW.md (~80 LOC 추출)

**§0 Context**: Aether 시나리오 A 본격 진행 일단락 시점에서 시니어 코드 리뷰어 시각의 자기 회고. 다음 프로젝트(Houseman Phase 7-12 진화) 적용 학습을 코드 / 페이지 / 기능 / 카드 진행 4 차원으로 추출. 모든 "시니어 권장" 표현에 구체 출처 (PRINCIPLES.md / WORK_PATTERNS.md / ADR / 공식 docs) 명시 (PRINCIPLES.md 원칙 5).

**도착점**: Top 10 9/10 (T-3 보류) / ADR 10건 / 차별화 = T-2 MCP stdio (국내 도메인 0건) + T-6 Qdrant 운영급.

**§1 백엔드 회고 (5 품질 차원 평가)**:
- **portfolio-service** (FastAPI 3.11): 가독 8 / 유지 8 / 확장 9 / 테스트 7 / 디버그 8 — MCP 외부화 = 차별화 (ADR 0008) / MLflow 사용처 미증명 (시나리오 A 본질 X)
- **auth-service** (Spring Boot 3.2.12): 가독 9 / 유지 8 / 확장 8 / 테스트 6 / 보안 8 — JJWT 0.12.5 + Redis blacklist + JTI + BCrypt + RateLimit
- **llm-service** (FastAPI + LangGraph + Gemini 2.5-Flash): 가독 7 / 유지 8 / 확장 9 / 테스트 7 / 디버그 7 — LangGraph create_react_agent + Tool Registry lazy init + Qdrant 어댑터

**§1.4 백엔드 학습 (Houseman 적용 6건)**:
1. Lazy Init Singleton 자기 일관성 (prompt_registry / tool_registry / chroma_client 동일 패턴)
2. CORS 명시 메서드 (와일드카드 X — OWASP 시그널)
3. InMemoryCache LRU + maxsize 박기 (운영급)
4. Rate Limit 분산화 (Redis 분산 락 — 시나리오 B 트리거)
5. 외부 SDK 마이그레이션 응답 어댑터 한 줄 (H-6 디벨롭 사례)
6. ADR 결정 근거 추적 (PRINCIPLES.md §원칙 5)

**§2 프론트엔드 회고**:
- 모놀리식 안티 패턴: `optimize` 344 LOC / `backtest` 217 LOC → D-3 분리 (200 LOC 임계 / ADR 0013)
- shadcn/ui 미설치 → 100+ 인라인 className 누적
- form state useState 분산 (RHF + zod 부재)
- Axios `failedQueue` race condition (동시 401 — Atomic refresh lock 부재)
- WCAG 2.1 미준수 (ARIA live region 부재 / 색상만 위험 표시) — 접근성 4/10
- 학습 5건 (Houseman): shadcn 첫날 / 200 LOC 임계 / RHF + zod / React Query / WCAG 2.1 (ARIA + 색상 + 텍스트 3중)

**§3 인프라 회고 (docker-compose 6 서비스)**: health check 일관 (interval 30s / timeout 10s / retries 3) / 단일 bridge `aether-network` / 단일 `.env`. 안티: 메모리/CPU limits 미설정 / `.env.prod` 분리 부재 / Qdrant 백업 정책 미명시. 학습 5건: deploy.resources limits 첫날 / 12-factor `.env.prod` 분리 / health start_period 보수적 / Docker Secrets / Qdrant 백업 ADR.

**§4 문서 시스템 (Aether 본질 강점 / 추적성 10/10)**: AGENTS.md (What) + CLAUDE.md (How) + PRINCIPLES.md (범용) + WORK_PATTERNS.md (Aether 누적) + SCENARIO.md (Aether 한정) + EVOLUTION.md + ADR 0001-0010 + phase3/ 카드. git-native 우위 (Notion / Confluence X) — 정합성 / 검색 / blame / PR 리뷰 통합. 다시 짜도 동일 채택 + Houseman 그대로 이식.

**§5 AI 통합 (LangGraph + RAG + MCP + Qdrant)**:
- 강점: WORK_PATTERNS 패턴 3 (응답 호환 어댑터 — 4키 dict / Pydantic 13종 / SDK 마이그) / 패턴 4 (환경변수 즉시 롤백 — `USE_REACT_AGENT`) / 패턴 5 (T-1a + T-1b 2단 분해)
- 안티: RAG 청크 사이즈 명시 부재 (token-aware chunking + overlap 부재 → D-7 해소) / Gemini embedding 배치 부재 (단건 호출 반복) / `_chroma_client` 전역 변수 (Singleton lazy init 캡슐화 미적용) / ReAct ToolMessage.content 가정 (isinstance 분기 미명시)
- 학습 7건 (Houseman): LangGraph 첫날 / MCP 외부 노출 그대로 / Prompt Registry 버전 / Qdrant 첫 선택 / 응답 어댑터 패턴 / Token Tracker + RAG Evaluator 첫날 / Multi-Agent 시나리오 B 진입 트리거 명시

**§6 기능 선택 (시나리오 A 적합도)**:
- 본질 ✓✓✓: chat (RAG) / chat structured / MCP 4 도구 외부 노출 / Qdrant 마이그
- 본질 ✓✓: optimize + AI 분석 통합 / backtest walk-forward 8 메트릭
- 본질 ✓: auth (JWT + Redis blacklist + Rate Limit) / risk
- **비본질** (D-1 보류): drift_detector / weight_monitor / experiment (MLflow) — 사용처 미증명 / *"하면 좋아 보임"* 영역 (ADR 0011)

**§6.5 가정 페르소나 시나리오**:
- 페르소나 1 (면접관 시니어 백엔드): 차별화 한 줄 = MCP stdio (T-2). ADR 10건 + WORK_PATTERNS 18 + PRINCIPLES 5 = 시그널 강함. 약점 질문: "MLflow 왜 박았어요?" → 시나리오 A 본질 X 인정 + 보류 트리거 명시 = 시니어 답
- 페르소나 2 (채용 담당): README + CLAUDE.md §2 PR 게이트 표 + 6 서비스 docker-compose 한눈에 = OK. 시각: optimize/backtest 페이지 차트 + 다크 테마 정합
- 페르소나 3 (동료 시니어): 코드 가독 백엔드 8 / 프론트엔드 7 (모놀리식 감점). 자기 일관성 백엔드 ✓ / 프론트엔드 X. 결정 추적 = 강점

**§7 카드 진행 순서 회고 (의존성 사슬 학습)**:
- 19 카드 진행 (git log #1-#19): H-7 → H-1 → H-4 → H-6 → H-10/L-7 → T-1a/b → H-1c → H-6 디벨롭 → WORK_PATTERNS v1 → T-2 Blocked → H-X (선행) → docs cleanup → T-2 본격 → WORK_PATTERNS v4 → T-6 → PRINCIPLES v4 → WORK_PATTERNS v5 → C-1 (T-3 보류)
- 다시 짠다면 최적 순서 (Phase 0-6): 문서 시스템 먼저 → H-7 PR 게이트 → H-1 ADR → H-10 + L-7 → H-4 + H-6 → T-1a/b → T-2 + T-6 → WORK_PATTERNS 누적 → T-3 보류
- **H-7 PR 게이트 가장 먼저** = 후속 모든 카드 안전망 (coverage 81% / vitest / tsc 차단 = 회귀 0건)
- **T-1a + T-1b 분해** = 회귀 위험 분리 (WORK_PATTERNS 패턴 5 옵션 B 2단 분해)
- **H-X (fastapi 업그레이드) → T-2 본격** = T-2 Blocked 인지 후 선행 카드 분리 (WORK_PATTERNS 문제 18)

**§8 종합 학습 10건 (Houseman Phase 7-12 진화)**:
1. 문서 시스템 첫날 박기 (PRINCIPLES 그대로 이식)
2. 5 가드 + 자기 일관성 패턴 5종 첫날
3. 시나리오 A/B/C 첫날 명확
4. 차별화 카드 우선 (Multi-Agent supervisor / 도메인 RAG / MCP 외부화)
5. 모놀리식 페이지 회피 (200 LOC 임계)
6. 운영급 결정 미리 (Cache maxsize / Rate Limit 분산화 / .env.prod / Docker resources / Qdrant 백업)
7. T-3 보류 패턴 그대로 (학습 + 적용 통합)
8. F-패턴 (검증 + 분기 + 머지 자동화)
9. 응답 호환 어댑터 패턴 (외부 SDK 변경 흡수 한 줄)
10. ADR 결정 근거 추적 (AI 추천 vs 본인 결정 분리)

**§9 면접 답변 3 깊이**:
- **5초 (한 줄)**: *"문서 시스템과 5 가드를 먼저 정착하고, 모놀리식 페이지를 컴포넌트로 분리하고, 시나리오 A 본질 X 기능(MLflow / drift_detector)은 정착하지 않았을 거예요."*
- **30초 (3 문장)**: 코드 측면 (자기 일관성 패턴 정착 + 운영급 첫날) / 기능 측면 (chat·optimize·MCP·Qdrant 본질 + MLflow·drift·weight 보류 트리거 명시) / 페이지 측면 (200 LOC 임계 + shadcn + RHF + WCAG)
- **3분 (디테일)**: 7 영역 — 문서 시스템 / 코드 자기 일관성 / AI 통합 / 기능 선택 / 페이지 / 카드 순서 / Houseman 진화 적용

---

### §2.7 AUDIT.md (~50 LOC 추출)

**D-4 본질**: 카드 14건 머지 후 종합 자가 점검. 결정 변경 X / 누적 학습 정착만.

**§1 카드 14건 종합 (15 PR — D-4 추가 시점에 14 카드)**:
| # | 카드 | PR | ADR | 본질 |
|---|---|---|---|---|
| 1 | C-1 | #18 | 0010 | T-3 보류 + PRINCIPLES 6/7 + SCENARIO v3 |
| 2 | M-1 | #19 | - | META_REVIEW.md (707 LOC) |
| 3 | F-1 | #20 | - | VERIFICATION.md (5 기능 검증) |
| 4 | F-1a | #21 | 0004 v2 | JWT HS512 통일 |
| 5 | D-1 | #22 | 0011 | 본질 X 보류 (MLflow / drift / weight) |
| 6 | D-2 | #23 | 0012 | 운영급 결정 (cache / CORS / API 키) |
| 7 | D-0 | #24 | - | frontend + README 정리 |
| 8 | D-3 | #25 | 0013 | optimize/backtest 분리 |
| 9 | D-9 | #26 | 0014 | RAG 정제 보류 |
| 10 | D-8 | #27 | 0015 | RAG 평가 4 메트릭 |
| 11 | T-2c | #28 | - | MCP 테스트 동적 경로 |
| 12 | T-6b | #29 | 0016 | chromadb → Qdrant default |
| 13 | D-7 | #30 | 0017 | Chunking grid (Auto Research) |
| 14 | D-5 | #31 | 0018 | ReAct 5 도구 |
| 15 | D-6 | #32 | 0019 | Streaming SSE |

**§2 WORK_PATTERNS 18 검증**: 해소 17 / 부분 1 (FutureWarning) / 미해소 0.

**§3 코드 메트릭**:
- LOC 합계: **14,414** (auth 1,349 / portfolio 4,731 / llm 5,158 / frontend 3,176)
- 테스트 합계: **635** (llm 357 / portfolio 203 / frontend 5 / auth 70) — M-1 시점 514 + 누적 +121
- 의존성 추가 (D-1 → D-6): llm 0건 (PyYAML / ragas 미도입) / portfolio −1건 (mlflow 제거)
- ADR: 19건 → 20건 (D-4 후) → 21건 (P-1 후)
- 누적 자료 LOC: **3,354**

**§3.6 baseline 진화**: D-8 chromadb (0.4444) → T-6b Qdrant (0.7222 / +0.2778) → **D-7 (500/300) 0.7413** (+0.0191) — 누적 +0.2969 (cosine 0.44 → 0.74).

**§4 미세 영역**: HS256 주석 stale 2 위치 + mlflow 잔재 2 라인 = 4 라인 정리.

**§4 발견된 미세 영역 (4 라인 정리)**:

| 영역 | 라인 | Before | After |
|---|---|---|---|
| HS256 주석 stale | `portfolio-service/app/config.py:37` + `llm-service/app/config.py:45` | `# 인증 (auth-service와 동일 HS256 비밀키 - 256bit 이상)` | `# 인증 (auth-service와 동일 HS512 비밀키 - F-1a / ADR 0004 v2)` |
| mlflow 잔재 | `portfolio-service/app/config.py:26-27` | `mlflow_tracking_uri / mlflow_experiment_name` field | 제거 (사용처 0 검증 완료) |

**§5 정리 vs 보류 (ADR 0020)**:
- **정리 영역 (D-4 commit)**: HS256 주석 동기화 2 라인 + mlflow field 제거 2 라인 = 4 라인 / 회귀 0
- **보류 영역**: 본격 코드 audit (security / dead code) — 시나리오 B 진입 / 의존성 cleanup — 본격 production / 테스트 cov 90%+ — 시나리오 B 의무 / deprecation warning 본격 처리 — 비용 ↑ / 시나리오 A 영역 X

**§6 P-1 / I-1 진입 자료**:
- **P-1 진입 자료**: 신규 패턴 발굴 후보 (1-3건) — 패턴 8 (신규 endpoint 분리 / D-5+D-6) / 패턴 9 (Auto Research / D-7) / 패턴 10 (G1 본질 트리거 / T-6b)
- **I-1 진입 자료**: 객관 메트릭 14,414 LOC + 635 테스트 + 19 ADR + 3,354 누적 자료 LOC + 4 분기 결정 추적 + 양면 정책 10 ADR + 우대 요건 매칭 4건 (SSE / RAG eval / Chunking / Multi-Agent 보류)

---

### §2.8 VERIFICATION.md (~50 LOC 추출)

**F-1 본질**: "박힌 코드 = 작동 X" — 5 기능 × 3 시나리오 (정상 / Edge / 에러) 실측.

**§0 사전 측정**:
- 6 서비스 health 실측 (frontend unhealthy = healthcheck 명령 / 실제 running OK)
- JWT 진단 5 절차 (logs / 토큰 발급 / 헤더 / refresh / DB) → **알고리즘 불일치 발견** (auth HS512 발급 vs portfolio/llm `algorithms=["HS256"]` 검증)

**§1-§5 5 기능 검증 결과**:
- §1 회원가입/로그인 (auth-service) — **PASS** (signup/login/me/refresh/logout/blacklist 6단계 ✓)
- §2 포트폴리오 최적화 — **401 차단** (HS512 vs HS256 알고리즘 불일치)
- §3 백테스트 — 401 차단
- §4 RAG 챗 — 401 차단
- §5 MCP — 부분 머지 (T-2 본격 ✓ / T-2b Claude Desktop config 미머지)

**§7 발견 이슈 등급 (사전 분류 룰 — 발견 전 정착)**:

| ID | 등급 | 내용 | 위치 | 후속 카드 |
|---|---|---|---|---|
| **C-1** | **Critical** | JWT 알고리즘 불일치 (HS512 vs HS256) — 도메인 라우터 3개 401 차단 | `portfolio-service/app/middleware/auth.py:29` + `llm-service/app/middleware/auth.py:30` | **F-1a** ★ (1 PR / 2 파일 / 4 라인) |
| M-1 | Major | frontend healthcheck unhealthy (running OK) | `frontend/Dockerfile` healthcheck 명령 | D-0 |
| M-2 | Major | T-2b Claude Desktop config 미머지 | `mcp-config*.json` 부재 | T-2b 또는 T-2c |
| m-1 | Minor | verify_jwt 주석 "HS256 공유 비밀키" stale | `*/middleware/auth.py:1` | F-1a 합류 |
| m-2 | Minor | docker exec env 권한 | VERIFICATION.md §0.2 | D-0 합류 |

**§6.1 통합 E2E 시나리오 결과**: 인증 사이클 (signup/login/me/refresh/logout/blacklist) 6단계 ✓ / 도메인 라우터 (optimize/backtest/chat) 3단계 ❌ — F-1a 1라인 fix로 즉시 복구 가능.

**§9 면접 시연 5분 시나리오 (정상 / Fallback 양면)**:
- 정상 흐름 (F-1a 머지 후): 1분 회원가입+로그인+blacklist / 1분 포트폴리오 최적화+프론티어 / 1분 백테스트 line chart / 1분 RAG 챗 4 도구 자율 / 1분 차별화 카드 (MCP / Qdrant / ADR 10건)
- Fallback (F-1a 미머지 시점): 코드 + pytest 통과 시연 → "박힌 코드 ≠ 작동하는 코드 — 진단 절차 정착" 시그널

**§10 사용자 의도 회고**: 5 기능 모두 시나리오 A 본질 ★★★ 적합 (Markowitz / walk-forward / LangGraph ReAct / MCP stdio / Qdrant 어댑터 차별화 카드 보유). C-1 fix 후 시연 5분 즉시 가능.

**§11 데이터 영향 (보안 + 격리)**: localStorage dev 한정 / 검증용 임시 user 격리 (id=4 `f1-test-1778056571@aether.local`) / Postgres read-only 4건 추가 / Redis refresh+blacklist 1건 (TTL 자동) / Qdrant 0 호출 / `docker exec env` 차단 = 시크릿 누출 방지 PASS.

**§12.2 신규 패턴 발견**: WORK_PATTERNS 문제 19 후보 (알고리즘 sync 누락 — auth-service HS512 변경 시 portfolio/llm verify_jwt sync 누락 — 외부 SDK 영역 차이 인지 영역).

---

### §2.9 PRE-CHECK 자료 3 파일 (~60 LOC 추출)

**D9_PRE_CHECK.md (245 LOC) — D-9 분기 3 보류 결정**:
- §1 RAG 사용처: ReAct agent에서 RAG 호출 0건 / `/api/chat` 티커 < 2 fallback 한정 / `/api/rag/*` frontend 호출 0건
- §2 정제 대상: 정적 4 md (554 LOC, 이미 정형) / 정제 후보 6 영역 모두 시나리오 A 부적합
- §4 분기 3 채택: D-9 보류 + D-8 (RAG 평가) 우선순위 격상
- §6 후속: ADR 0014 (D-9 보류) + D-8 격상 + D-7 (Chunking) + D-5 (RAG 도구)
- 시그널: PRINCIPLES 6번 (미적용 결정 + 트리거 명시) 직격

**D8_PRE_CHECK.md (306 LOC) — D-8 분기 2 자체 메트릭**:
- §1 RAG 출력: `query_with_llm` → {answer, sources[title/source/relevance]} / RAGQueryResponse {answer, sources, confidence}
- §2 평가 데이터: knowledge_base 4 md (554 LOC) / ground truth 5-10건 작성 30분-1시간
- §3 메트릭 분석: relevance@k (이미 구현) / recall@k / LLM-as-judge / faithfulness — ragas 의존성 비용 ≫ 시그널
- §5 분기 2 채택: 자체 4 메트릭 + ground truth YAML + CLI 스크립트 + markdown report + ADR 0015
- 시그널: "ragas 안 쓴 이유" 답 가능 = 비용 인식 + 본질 판단 시그널

**MCP_FAIL_DIAGNOSIS.md (163 LOC) — pre-existing 환경 의존성**:
- §1 fail 본문: `FileNotFoundError: '/Users/kuka/Aether/portfolio-service'` (호스트 절대경로 하드코딩 / `tests/test_mcp_server.py:14`)
- §2 분기 결정 검증:
  - 분기 1 (D-8 영향) ❌ — D-8 commit (`afe3ac2`) portfolio-service 변경 0건. `.gitignore` 영향도 chroma 무관
  - 분기 2 (pre-existing T-2 도입 시점부터) ✓ — `dfe8ae3` T-2 본격 PR 이후 단 1 commit. D-1 PR #22에서도 명시 완료
  - 분기 3 (환경 의존성) ✓ — Docker (FileNotFoundError) + 호스트 venv (ModuleNotFoundError: scipy) 양쪽 fail
- §3 후속 권고: T-2c (3-5 라인 수정) 별도 카드:
  ```python
  from pathlib import Path
  PROJECT = str(Path(__file__).resolve().parent.parent)  # 동적 경로 (호스트/컨테이너 무관)
  ```
- §4 D-8 영향 명확 (무관) / T-6b 진입 차단 사유 0 — vector store 전환 (chromadb → Qdrant)은 MCP 테스트 무관

**3 PRE-CHECK 자료 공통 패턴**: 진단 전용 카드 (코드 변경 0 / git 작업 0) + 분기 N 검증 + 분기 결정 + 후속 카드 트리거 + 사용자 보고 의무 (G3 Done Definition) + 5 가드 적용 검증 + WORK_PATTERNS 누적 문제 매칭. 사용자가 본 카드 본질 = "정착된 카드 ≠ 본질 적합 카드" 검증 시그널.

---

### §2.10 ADR 21건 (~80 LOC 추출)

**ADR 0001-0021 한 줄 요약** (양면 정책 11 ADR = 0011-0021):

| # | 제목 | 결정 본질 |
|---|---|---|
| 0001 | Microservice Split | 4 서비스 + 2 인프라 — 책임 분리 + Java/Python 강점 동시 사용 |
| 0002 | Module Boundaries | routers / services / agents 단방향 — agents/ 활성 (T-1a) |
| 0003 | Prompt Registry Policy | `get_registry().get(name, version)` 단일 진입점 + JSON 스키마 escape |
| 0004 | Auth + Tracing (v2) | JWT HS512 통일 (F-1a) + X-Request-ID forward + 토큰 마스킹 |
| 0005 | LangGraph Adoption | T-1 인프라 채택 — supervisor / state graph / ReAct 빌트인 |
| 0006 | ReAct Pattern | 절차적 4 호출 → ReAct 1 호출 (자율 판단) + 환경변수 fallback |
| 0007 | Genai SDK Migration | google-generativeai → google-genai 1.74 (legacy 제거) + 어댑터 |
| 0008 | MCP Server Adoption | stdio 4 도구 외부 노출 — 차별화 (국내 도메인 0건) |
| 0009 | Qdrant Migration | ChromaDB → Qdrant 어댑터 (T-6) — 운영급 전환 검증 |
| 0010 | T-3 Multi-Agent Deferred | **보류** — 시나리오 A 본질 X / Houseman 진화 시점 트리거 |
| 0011 | Functional Trim Deferred | **보류** — MLflow / drift / weight 본질 X (D-1) |
| 0012 | Production-Grade Decisions | 정착 — cache LRU / CORS 명시 / API 키 lifespan (D-2) |
| 0013 | Frontend Page Decomposition | 정착 — 200 LOC 임계 / optimize·backtest 분리 (D-3) |
| 0014 | RAG Data Cleaning Deferred | **보류** — 정제 대상 부재 (D-9 / 분기 3) |
| 0015 | RAG Evaluation Metrics | 정착 — 자체 4 메트릭 / ragas 미도입 (D-8 / 분기 2) |
| 0016 | Qdrant Default Migration | 정착 — chromadb → Qdrant default + _EMBED_DIM 768→3072 정정 (T-6b) |
| 0017 | RAG Chunking Policy | 정착 — grid 9 조합 / chunk_size=500 / overlap=300 (D-7 / Auto Research) |
| 0018 | ReAct + RAG Tool | 정착 — ReAct 5번째 도구 (`search_knowledge_base`) (D-5) |
| 0019 | Streaming SSE | 정착 — `/api/chat/stream` 신규 / `astream_events` v2 (D-6 / 우대 4) |
| 0020 | D-4 Audit Cleanup | 정착 4 라인 + 보류 4 영역 (audit / 의존성 / cov / deprecation) |
| 0021 | Meta Patterns + KARPATHY | 정착 — PRINCIPLES 8/9/10 + KARPATHY_MAPPING (귀납 + 연역) (P-1) |

**양면 정책 11 ADR 정립 (D-4 후)**:

| 정책 영역 | ADR | 본질 |
|---|---|---|
| **정착 결정** (D-N 시리즈) | 0012 (D-2 운영급) | cache LRU / CORS 명시 / API 키 lifespan |
| | 0013 (D-3 frontend 분리) | 200 LOC 임계 / optimize·backtest 컴포넌트 분리 |
| | 0015 (D-8 RAG 평가) | 자체 4 메트릭 / ragas 미도입 |
| | 0016 (T-6b Qdrant default) | 768→3072 정정 / Skill Issue 95 진화 |
| | 0017 (D-7 Chunking) | grid 9 조합 / Auto Research 정착 |
| | 0018 (D-5 ReAct + RAG) | 5번째 도구 / 사용자 의도 영역 X |
| | 0019 (D-6 Streaming SSE) | 신규 endpoint / 우대 요건 4 직격 |
| **보류 결정** | 0010 (T-3 Multi-Agent) | 시나리오 A 본질 X / Houseman 진화 트리거 |
| | 0011 (D-1 본질 X) | MLflow / drift / weight 보류 |
| | 0014 (D-9 RAG 정제) | 정제 대상 부재 / 시나리오 B 트리거 |
| **메타 결정** | 0020 (D-4 Audit) | 정리 4 라인 / 보류 4 영역 |
| | 0021 (P-1 메타 + KARPATHY) | PRINCIPLES 8/9/10 + 카파시 매핑 |

**시그널 본질**: 결정 근거 추적 시스템 = PRINCIPLES 원칙 5 직격 ("AI 추천 vs 본인 결정 분리"). 정착 7건 + 보류 3건 + 메타 2건 = 양면 정책 = 시니어 시그널 강함.

**카드별 영향 추적**: 14 카드 머지 후 ADR 갱신 누적 — F-1a (0004 v2) / D-1 (0011) / D-2 (0012) / D-3 (0013) / D-9 (0014) / D-8 (0015) / T-6b (0016) / D-7 (0017) / D-5 (0018) / D-6 (0019) / D-4 (0020) / P-1 (0021).

---

### §2.11 KARPATHY_LECTURE.md 통합 (~300 LOC) ★ 핵심 영역

**본 자료 출처**: 사용자 옆 Claude (= 본 대화 Claude) 작성. 카파시 영상 본문 디테일 정리 자료. V-0 untracked → tracked 통합.
**영상**: https://www.youtube.com/watch?v=-E9chn_gtfY (인터뷰어: Sarah Guo / Conviction / 약 53분).

**결론 한 줄**: AI Psychosis 시점에 카파시가 정착한 작업 패러다임 — 코드 줄 X / 카드 단위 위임 / 인간 = 시스템 병목 X / 에이전트 인지 자료 본문 본격 정착.

#### §2.11.1 17 영역 핵심 추출 (KARPATHY_LECTURE.md §1-§14)

**§1 AI Psychosis — 12월 패러다임 전환**:
> *"I don't think I've typed like a line of code probably since December basically."*
> *"I'm just like in this state of psychosis of trying to figure out like what's possible."*
- 8020 → 2080 → 그 이상 전환 (직접 코딩 vs 에이전트 위임)
- Conviction 팀 = 모든 엔지니어 코드 작성 X / 마이크 + 음성 명령 위임만

**§2 Skill Issue — AI 한계 X / 본인 활용 부족**:
> *"It's not that the capability is not there. It's that you just haven't found a way to string it together of what's available."*
> *"I just don't I didn't give good enough instructions in the agent MD file or whatever it may be."*
- AGENTS.md 본문 부족 = 본인 활용 영역 부족 시그널
- "addictive" 이유 = 본인 스킬 ↑ 시점에 unlocks 본격 발생

**§3 Macro Actions — 카드 단위 위임 (Peter Steinberg 사례)**:
> *"It's just like you can move in much larger macro actions. It's not just like here's a line of code, here's a new function. It's like here's a new functionality and delegate to agent one."*
> *"Another agent is doing some like research and another agent is writing code another one is coming up with a plan for some new implementation."*
- Peter Steinberg: 모니터 여러 대 / Codex 다중 인스턴스 / 10 repos 동시
- "muscle memory" 정착 의무 — 본인 작업 흐름 자체 진화

**§4 Token Throughput — 본인 = 시스템 병목 X**:
> *"If you're not maximizing your subscription at least and ideally for multiple agents..."*
> *"I feel nervous when I have subscription left over that just means I haven't maximized my token throughput."*
> *"What is your token throughput and what token throughput do you command?"*
- PhD 시절 GPU flops 비유 → 지금은 tokens
- 10년+ 동안 엔지니어가 compute bound X → 지금 capability 본격 ↑ → binding constraint 본인

**§5 Persistent Loop / Claw — 지속 루프 + sandbox**:
> *"It really when I say a claw, I mean this like layer that uh kind of takes persistence to a whole new level."*
> *"It's kind of like has its own little sandbox, its own little, you know, it kind of like does stuff on your behalf even if you're not looking kind of thing."*
- Open Claude (Peter Steinberg 작품) = 일반 에이전트보다 영역 본격 ↑
- Soul.md 페르소나 영역 — Claude = "teammate" / Codex = dry "implemented it"
- 카파시: *"It doesn't seem to care about what you're creating. It's kind of like, oh, I implemented it. It's like, okay, but do you understand what we're building?"*
- Sycophancy 적정 = 본인 좋은 아이디어 시점에만 적정 칭찬

**§6 Dobby — 홈 자동화 자연어 인터페이스**:
> *"I have a claw basically that takes care of my home and I call them Dobby the elf claw."*
> *"I just told it that I think I have Sonos at home like can you try to find it and it goes and that did like IP scan of all the um basically um computers on the local area network and it found the Sonos thing."*
- LAN scan → Sonos 발견 → reverse engineer → API 발견 → dashboard 작성 (3 프롬프트)
- 조명 / HVAC / 셰이드 / 풀 / 스파 / 보안 시스템 모두 통합
- WhatsApp 단일 인터페이스 — 6 앱 → 1 자연어
- 외부 카메라 + Quinn 모델 (vision) → "FedEx truck just pulled up" 텍스트 알림
- "sleepy time" 자연어 → 모든 조명 OFF

**§7 Auto Research — 인간 결정 최소화 (NanoGPT 사례)**:
> *"To get the most out of the tools that have become available now you have to remove yourself as the as the bottleneck. You can't be there to prompt the next thing."*
> *"Auto research is just yeah here's an objective here's a metric here's your boundaries of what you can and cannot do and go."*
- NanoGPT 2 십년 hyperparameter 튜닝 본격 진행한 카파시
- Auto Research 한 번 진행 시 → 본인이 못 발견한 영역 발견:
  - weight decay / value embeddings / atom betas
- *"These things jointly interact. So like once you tune one thing, the other things have to potentially change too."*
- Frontier Lab 영역: 연구자 = 영역에서 제거 의무 (too much confidence) / archive papers + GitHub repos에서 아이디어 자동 발견 / feature branch 자동 정착
- Program MD 메타 최적화: 모든 연구 조직 = markdown 파일 영역 / 메타 최적화 가능 (콘테스트 형식)

**§8 Jaggedness — Verifiable vs 비-Verifiable**:
> *"I simultaneously feel like I'm talking to an extremely brilliant PhD student who's been like a systems programmer for their entire life and a 10-year-old."*
> *"You're either on Rails and you're part of the super intelligence circuits or you're not on Rails."*
- Verifiable (코드 / 단위 테스트) = RL 본격 진화 vs 비-Verifiable (농담 / nuance) = 진화 X
- 5년째 같은 농담: *"Why do scientists not trust atoms? Because they make everything up."*
- Coding ↑ ≠ Joke ↑ — 본격 generalization X 시그널

**§9 Speciation — Monoculture vs 전문화**:
> *"The animal kingdom is extremely diverse... some animals have overdeveloped visual cortex or clear kind of parts."*
> *"You don't need like this oracle that knows everything. you kind of speciate it and then you put it on a specific task."*
- 현재 = 모든 영역 단일 모델 monoculture / 미래 = 동물 왕국 speciation
- Cognitive core = 작은 모델 충분 / Lean (수학 증명) 사례
- 가중치 manipulation = capability loss 회피 어려움 / Continual learning은 본격 develop 영역

**§10 Untrusted Pool — 분산 검증 (SETI@home 비유)**:
> *"A swarm of agents on the internet could collaborate to improve LLMs and could potentially even like run circles around Frontier Labs."*
> *"A lot of things have this property that you know very expensive to come up with but very cheap to verify."*
- Untrusted workers + trusted verification pool / Folding@home 비유
- 블록체인 비유: Block 대신 commit / Proof of work / 보상 = leaderboard (현재) / 미래 monetary
- 사용자 영역 contribute: cancer 연구 영역에 compute 직접 contribute
- *"Maybe everyone cares about flops in the future."* (단 카파시 "I don't actually think that's true, but it's kind of interesting to think about.")

**§11 Digital vs Physical — 빛의 속도 vs 100만 배 느림**:
> *"Energetically I just think we're going to see a huge amount of activity in digital space."*
> *"I think we're going to see something that in the digital space goes at the speed of light compared to I think what's going to happen in the physical world."*
> *"Atoms are like a million times harder."*
- Bits = copy paste 비용 X / 빛의 속도 vs Atoms = 100만 배 느림
- Demand Elasticity (ATM / 은행 텔러 사례 / Jevons paradox): 비용 ↓ 시점에 demand ↑
- 소프트웨어 = scarce → 비용 ↓ → demand ↑ → cautiously optimistic
- Reshuffling: 고객 = 인간 X / 에이전트 본격 / "ephemeral software on your behalf"

**§12 Frontier Lab vs 외부 — Alignment**:
> *"Fundamentally I mean you're you have a huge financial incentive to uh with these frontier labs."*
> *"You're not a completely free agent and you can't actually like be part of that conversation in a fully autonomous um free way."*
- Financial 인센티브 = alignment / 외부 = humanity 영역 align
- 외부 단점: frontier 인지 X 시점에 judgement drift
- 추천: Frontier Lab + 외부 "going back and forth"

**§13 Open Source vs Closed — Linux 60% 비유**:
> *"You have like closed s like you know Windows and Mac OS... and there's Linux but Linux is very easy like actually Linux is extremely successful project. it runs on the vast majority of computers."*
> *"I want there to be ensembles of people thinking about all the hardest problems."*
- Closed = frontier (Nobel Prize 영역) / Open = 6-8개월 lag (consumer 충분)
- *"Centralization has a very poor track record"* — Eastern European 비유
- Ensembles 영역: *"Ensembles always outperform any individual model."*

**§14 Markdown for Agents — 교육 패러다임 본격 전환 (micro GPT 사례)**:
> *"Normally before like maybe a year ago or more if I had come up with micro GPT I would be tempted to basically explain to people..."*
> *"I'm not explaining to people anymore. I'm explaining it to agents."*
> *"Instead of HTML documents for humans you have markdown documents for agents because if agents get it then they can just explain all the different parts of it."*
- 사용자 직접 설명 X / 에이전트 설명 본격 — 에이전트가 "router"
- Skills 영역: micro GPT skill = 코드베이스 학습 흐름 hint
- micro GPT (200줄 Python): Data set + neural network (50줄) + forward/backward (autograd 100줄) + optimizer (10줄)
- *"The things that agents can do they can probably do better than you or like very soon"*

#### §2.11.2 카파시 9 본능 정리 (KARPATHY_LECTURE.md §15)

| # | 본능 | 본질 | 인용 위치 |
|---|---|---|---|
| 1 | **AI Psychosis** | 12월 패러다임 전환 인지 | §1 |
| 2 | **Skill Issue** | AI 한계 X / 본인 활용 부족 | §2 |
| 3 | **Macro Actions** | 카드 단위 위임 / 코드 줄 X | §3 |
| 4 | **Token Throughput** | 본인 = 시스템 병목 X | §4 |
| 5 | **Persistent Loop / Claw** | 지속 루프 + sandbox + 메모리 | §5 |
| 6 | **Auto Research** | 인간 결정 최소화 / 객관 메트릭 | §7 |
| 7 | **Jaggedness** | Verifiable vs 비-Verifiable 분리 | §8 |
| 8 | **AGENTS.md / Soul.md** | 에이전트 인지 자료 + 페르소나 | §5 |
| 9 | **Markdown for Agents** | HTML → Markdown 교육 패러다임 | §14 |

**추가 영역 (본능 X / 사례 영역)**:
- Dobby (§6) — 홈 자동화 자연어
- Untrusted Pool (§10) — 분산 검증 (SETI@home)
- Digital vs Physical (§11) — 빛의 속도 vs 100만 배
- Frontier Lab vs 외부 (§12) — Alignment
- Open Source vs Closed (§13) — Linux 60%
- Speciation (§9) — Monoculture → 전문화 미래

#### §2.11.3 KARPATHY_MAPPING.md §1 비교 표 (KARPATHY_LECTURE.md §16) ★ V-1b 트리거

**쿠카 작성 KARPATHY_MAPPING.md §1 8 본능 vs 영상 본문**:

| # | 쿠카 작성 본능 | 영상 본문 일치? | 비고 |
|---|---|---|---|
| a | Skill Issue | ✓ | §2 직접 인용 가능 |
| b | Auto Research | ✓ | §7 직접 인용 가능 |
| c | Premortem | X | 영상 본문 X / 쿠카 영역 본능 |
| d | Reversibility (Type 1/2/3) | X | 영상 본문 X / 쿠카 영역 (Type 영역) |
| e | 5 Guards (G1-G5) | X | 영상 본문 X / 쿠카 영역 (Aether 영역) |
| f | 박지 않은 결정 = 시그널 | X | 영상 본문 X / 쿠카 영역 (양면 정책) |
| g | 본질 충돌 분리 | X | 영상 본문 X / 쿠카 영역 본능 |
| h | 측정 vs 추정 | X | 영상 본문 X / 쿠카 영역 본능 |

**일치율: 25% (2/8)** — 6건 쿠카 영역 본능 (영상 본문 X).

**영상 본문 X / KARPATHY_MAPPING.md §1 누락 영역 7건**:

| # | 영상 본문 영역 | KARPATHY §1 X | V-1b 추가 의무 |
|---|---|---|---|
| 1 | AI Psychosis | X | 추가 의무 |
| 2 | Macro Actions | X | 추가 의무 |
| 3 | Token Throughput | X | 추가 의무 |
| 4 | Persistent Loop / Claw | X | 추가 의무 |
| 5 | AGENTS.md / Soul.md | X | 추가 의무 |
| 6 | Jaggedness | X | 추가 의무 |
| 7 | Markdown for Agents | X | 추가 의무 |

#### §2.11.4 V-1b 본격 트리거 영역

- KARPATHY_MAPPING.md §1 본격 재작성 의무 (영상 본문 9 본능 정착)
- 쿠카 영역 본능 6건 (Premortem / Reversibility / 5 Guards / 박지 않은 결정 / 본질 충돌 / 측정) = 별도 자료 영역 (META_REVIEW / WORK_PATTERNS / PRINCIPLES)
- 매칭 점수 진화 표 본격 재계산 의무 (실제 9 본능 기준)
- 8 × 14 카드 매핑 표 본격 재작성 의무
- 면접 답변 매핑 5 영역 본격 재검토 의무 (실제 카파시 본능 인용)

---

## §3 쿠카 영역 검수 13 영역 검증

**검색 키워드**: "검수 13 영역" / "영역 1-13" / "영역 11 누락" / "영역 12 외부" / "영역 13 메타".

**검색 영역**: WORK_PATTERNS.md / META_REVIEW.md / PRINCIPLES.md / SCENARIO.md / AUDIT.md.

**발견 위치 (1차 source of truth)**:

| 위치 | 내용 |
|---|---|
| `WORK_PATTERNS.md:657` | `## 🔍 plan 검수 13 영역 가이드 (시니어 검수 본질 — 있는 것 + 없는 것 + 외부 영향 + 메타)` |
| `WORK_PATTERNS.md:659` | `13 영역 일관 형식 / 영역 1-10 = "있는 것" 검증 / 영역 11-13 = "plan에 없는 본질 점검"` |
| `WORK_PATTERNS.md:661-733` | 영역 1 (측정 0~5) / 2 (5 가드) / 3 (WORK_PATTERNS 적용) / 4 (변경 대상) / 5 (어댑터) / 6 (Step) / 7 (위험) / 8 (검증) / 9 (문서) / 10 (자기 점검) |
| `WORK_PATTERNS.md:736-756` | 영역 11 (누락 위험) / 12 (외부 의존성 영향) / 13 (메타 검수 시니어 시각) |
| `WORK_PATTERNS.md:773-776` | T-6 plan 검수 사례 (영역 11/12/13 인용) |
| `WORK_PATTERNS.md:782-783` | 적용 주체 표 (Claude 사용자 검수 / Claude Code 셀프 검수) |
| `META_REVIEW.md:503` | 카드 18 (WORK_PATTERNS v5) — 검수 13 영역 가이드 신규 섹션 |
| `AUDIT.md:138` | "WORK_PATTERNS.md 885 LOC / 누적 문제 18건 + 체크리스트 A-G + plan 검수 13 영역" |

**13 영역 전체 목록 (WORK_PATTERNS.md §657-756 인용)**:

| 영역 | 카테고리 | 본질 |
|---|---|---|
| 1 | 있는 것 | 측정 0~5 (사전 측정 — 의존성/사용처/차원/Docker/회귀) |
| 2 | 있는 것 | 5 가드 (G1-G5) + 메모리 위반 통합 (#19/#21/#22/#23/#24/#25/#26/#27/#28) |
| 3 | 있는 것 | WORK_PATTERNS 적용 (체크리스트 A-G + 자기 일관성 1-5 + 메모리 시나리오) |
| 4 | 있는 것 | 변경 대상 파일 (신규 / 수정 / 미수정 보존 — `git diff` 빈 출력 검증) |
| 5 | 있는 것 | 어댑터 / 핵심 설계 (호출자 0 변경 / Lazy Init / 환경변수 토글 / 응답 어댑터) |
| 6 | 있는 것 | Step 분해 (흐름 추적용 — 시간 분해 X / 메모리 #28) |
| 7 | 있는 것 | 위험 시나리오 6+ (확률 + 완화 — R6 시간 cap = 메모리 #28 위반) |
| 8 | 있는 것 | 검증 (PR 게이트 — 회귀 / 신규 통합 / 보존 / cov 81%+) |
| 9 | 있는 것 | 문서 갱신 (ADR 7 항목 / TECH_DECISIONS / AGENTS / 면접 답변) |
| 10 | 있는 것 | 자기 점검 (PRINCIPLES / SCENARIO / WORK_PATTERNS / TECH_DECISIONS 참조 / pre-existing / squash / Co-Authored-By X) |
| 11 | 없는 것 | 누락 위험 (보안 / 성능 / 동기화 / 다운타임 / 백업) |
| 12 | 없는 것 | 외부 의존성 영향 (다른 서비스 / CI / 모니터링 / 백업) |
| 13 | 없는 것 | 메타 검수 시니어 시각 (다른 개발자 / 6개월 후 / 면접관 / 결정 근거 추적) |

**발견 결과**: WORK_PATTERNS.md (1차 source of truth) + META_REVIEW.md / AUDIT.md (인용 위치). PRINCIPLES.md / SCENARIO.md = 발견 X (의도된 분리 — 검수 13 영역은 작업 패턴 자료 영역).

**T-6 plan 검수 사례 (WORK_PATTERNS §773-776)**: 영역 11 (마이그 다운타임 미명시 / 시나리오 A 무시 가능) / 영역 12 (CI 파이프라인 영향 미검수 / Qdrant Docker 후속 카드) / 영역 13 (TECH §1 인용 + 어댑터 + 환경변수 토글 = 시니어 시그널 강함).

**가짜 영역 가능성 보고**: 발견 X — 본 영역은 WORK_PATTERNS.md §657-783에 본격 정착 (885 LOC 자료 영역).

**적용 주체**: Claude (사용자 검수) — 영역별 표 정착 / Claude Code (셀프 검수) — 영역 11-13 명시 의무.

---

## §4 카드별 영향 영역 매핑 표

| 카드 | PR | ADR | 영향 자료 | 누적 결과 |
|---|---|---|---|---|
| C-1 (T-3 보류) | #18 | 0010 | SCENARIO v3 / EVOLUTION / PRINCIPLES 6/7 | 양면 정책 시작 / 시나리오 A 일관성 |
| M-1 | #19 | - | META_REVIEW.md (707 LOC 신규) | Phase 1-7 학습 + Houseman 진화 자료 |
| F-1 | #20 | - | VERIFICATION.md (386 LOC) | 5 기능 검증 / Critical 1 발견 |
| F-1a | #21 | 0004 v2 | AGENTS.md §9 / 4 라인 수정 | JWT HS512 통일 |
| D-1 | #22 | 0011 | AGENTS.md §7 / experiment 5 endpoint 제거 | 본질 X 보류 (양면 정책 1번째) |
| D-2 | #23 | 0012 | AGENTS.md §7 (CACHE_MAXSIZE 1000 / CORS) | 운영급 정착 (양면 정책 2번째) |
| D-0 | #24 | - | frontend healthcheck / README | pre-existing 정리 |
| D-3 | #25 | 0013 | AGENTS.md §7 (200 LOC 임계) | optimize 344 / backtest 217 분리 |
| D-9 | #26 | 0014 | D9_PRE_CHECK.md / chromadb sync 부록 | RAG 정제 보류 (양면 정책 4번째) |
| D-8 | #27 | 0015 | D8_PRE_CHECK.md / scripts/eval_rag.py | 자체 4 메트릭 (양면 정책 5번째) |
| T-2c | #28 | - | tests/test_mcp_server.py 동적 경로 | MCP_FAIL_DIAGNOSIS.md 정착 |
| T-6b | #29 | 0016 | rag.py _EMBED_DIM 768→3072 | Qdrant default + Skill Issue 95 |
| D-7 | #30 | 0017 | scripts/grid_search_chunking.py | Auto Research 정착 (90점) |
| D-5 | #31 | 0018 | react_agent.py 5 도구 | ReAct + RAG 통합 |
| D-6 | #32 | 0019 | routers/chat.py /api/chat/stream | Streaming SSE (우대 4) |
| D-4 | (포함) | 0020 | AUDIT.md (238 LOC) | WORK_PATTERNS 17/18 검증 baseline |
| P-1 | #34 | 0021 | PRINCIPLES.md §8/§9/§10 + KARPATHY_MAPPING.md | 메타 패턴 + 카파시 매핑 (귀납+연역) |

**영향 누적**: AGENTS.md §7 14 행 / ADR 11건 (0011-0021 양면 정책) / 누적 자료 5,758 LOC / KARPATHY_LECTURE.md (V-0 통합 + 605 LOC).

**카드별 baseline 진화 (eval_rag.py)**:

| 단계 | chunk/overlap | recall@k | relevance@k | 누적 진화 |
|---|---|---|---|---|
| D-8 (chromadb) | 1000/200 | 1.0000 | 0.4444 | baseline |
| T-6b (Qdrant) | 1000/200 | 1.0000 | 0.7222 | +0.2778 (cosine 0.44 → 0.72) |
| **D-7 (Qdrant)** | **500/300** | 1.0000 | **0.7413** | +0.0191 (grid search 9 조합 자동) |
| **누적** | — | — | — | **+0.2969** (cosine 0.44 → 0.74 / +67%) |

**메트릭 누적 정착**: 14,414 LOC + 635 테스트 (M-1 시점 514 + 누적 +121) + 의존성 추가 0 (PyYAML / ragas 미도입 본능) + 양면 정책 11 ADR + 누적 자료 3,354 LOC.

---

## §5 쿠카 검증 X 의문 영역 7건 (V-1 검증 영역)

| # | 의문 영역 | 검증 위치 | V-1 / V-1b 대응 |
|---|---|---|---|
| 1 | KARPATHY_MAPPING.md 174 LOC가 충분 영역? | §1 8 본능 + §6 면접 답변 5 영역 | V-1b 재작성 시 분량 ↑ 검증 |
| 2 | 자료 일관성 충돌 발견 영역 (PRINCIPLES §X와 KARPATHY §Y 중복?) | PRINCIPLES §8/§9/§10 vs KARPATHY 8 본능 | V-1 정독 시 충돌 영역 검증 |
| 3 | META_REVIEW.md Phase 8 누락? | META_REVIEW §8 종합 학습 (Phase 1-7) | V-1 정독 시 Phase 8 후보 발견 영역 |
| 4 | 면접 답변 매핑 5 영역 디테일 부족? | KARPATHY_MAPPING §6 (5 영역 + 꼬리 질문) | V-1b 재검토 의무 (실제 카파시 본능 기준) |
| 5 | 카드별 영향 누락 발견 영역 (P-1 영향 AGENTS.md §7?) | AGENTS.md §7 (PRINCIPLES 7→10 + KARPATHY 76→87) | V-1 정독 시 행 누락 영역 검증 |
| 6 | **KARPATHY_MAPPING.md §1 잘못 작성 영역** ★ | KARPATHY §1 (일치율 25% / 6건 쿠카 영역 / 7건 누락) | **V-1b 핵심 트리거 = §1 재작성 의무** |
| 7 | 카파시 영상 본문 직접 인용 부족 영역 | KARPATHY §1 (영상 시간대 추정 단서만) | V-1b = KARPATHY_LECTURE.md를 source of truth로 정착 |

**V-1b 본격 트리거**: 의문 6번 (KARPATHY_MAPPING.md §1 잘못 작성) + 7번 (직접 인용 부족) = §1 재작성 의무 (KARPATHY_LECTURE.md 9 본능 + 직접 인용 정착).

**V-1 검증 영역 확장 (V-0 → V-1 전환 자료)**:

| 검증 영역 | 본 디제스트 §X | V-1 검증 의무 |
|---|---|---|
| 자료 디테일 충분성 | §2.1-§2.11 (11 자료 추출) | 각 자료별 누락 디테일 발견 영역 확인 |
| 자료 일관성 | §2.2 PRINCIPLES vs §2.3 KARPATHY_MAPPING | §1-§7 (귀납) vs §1 (연역) 충돌 영역 검증 |
| 카드 영향 누락 | §4 카드별 영향 표 | AGENTS.md §7 14 행 vs P-1 영향 누락 검증 |
| 검수 13 영역 적용 | §3 (WORK_PATTERNS §657-783 인용) | V-1 본문에 영역 1-13 본격 적용 |
| KARPATHY §1 재작성 | §2.11.3 비교 표 (일치율 25%) | V-1b 카드 본격 산출물 |
| 면접 답변 5 영역 재검토 | §2.3 §6 (KARPATHY 면접 답변) | 실제 카파시 9 본능 기준 재정착 |
| 메트릭 baseline 정합 | §4 baseline 진화 표 | AGENTS.md §7 / AUDIT.md §3 vs V-1 상태 일관성 |

---

## 비고

- 본 디제스트 = 사용자 본 대화 컨텍스트 영역 진입 자료 (V-1 진입 직전).
- 사용자 옆 Claude (= 본 대화 Claude) = 본 디제스트 정독 + V-1 프롬프트 보강 작성 진입.
- 본 카드 산출물 = V-1 카드 진입 자료 정착 (본 카드 자체 산출물 X — 일시 추출 카드).
- `KARPATHY_LECTURE.md` = 사용자 옆 Claude 작성 / 카파시 영상 본문 디테일 정리 자료 / V-0 commit 통합 (untracked → tracked).
- V-1 진입 = 본 디제스트 + V-1 보강 프롬프트 통합.
- V-1b 트리거 = `KARPATHY_MAPPING.md` §1 재작성 (일치율 25% 발견 / 6건 쿠카 영역 제거 / 7건 누락 영역 추가).
- 단어 위생 의무: 금지 어휘 사용 X — 대체어 "정착 / 통합 / 작성 / 인용" 통일.
- 다음 진입 카드: **V-1** (누적 자료 검증 + V-1b KARPATHY §1 재작성 보고서).

---

## §갱신 이력

| 일자 | 변경 |
|---|---|
| 2026-05-07 | V-0 초기 작성 — 11 자료 핵심 추출 + KARPATHY_LECTURE 통합 + 쿠카 13 영역 검수 grep + 카드별 영향 + 7 의문 영역. V-1 진입 자료 정착. |

**한 문장**: 누적 자료 11건 (~5,758 LOC) + ADR 21건 핵심 영역만 본 디제스트 단일 파일에 정착 — KARPATHY_MAPPING.md §1 일치율 25% 발견 / V-1b 재작성 트리거 / V-1 진입 자료 정착 완료.

---

## §부록 — 본 디제스트 검증 명령

```bash
# LOC 측정 (목표 800-1,000)
wc -l docs/agent-capability-audit/DIGEST.md

# 단어 위생 검증 (금지 어휘 0건 의무 — 대체어 정착/통합/작성/인용)
# (검증 명령은 V-0 카드 정의의 금지 어휘 정규식 적용)

# 섹션 헤더 누적 (§1-§5 + §2.1-§2.11 + 비고 + 부록)
grep -c "^##" docs/agent-capability-audit/DIGEST.md

# 표 라인 누적 (§1 / §2.10 / §2.11.3 / §3 / §4 / §5)
grep -c "^| " docs/agent-capability-audit/DIGEST.md

# 자료 영역 인용 검증 (각 §2.X 1+ 인용 위치 / 파일명·라인 기재)
grep -E "\.md:[0-9]+|\.py:[0-9]+" docs/agent-capability-audit/DIGEST.md | wc -l
```

**V-1 진입 직전 사용자 의무**: 본 디제스트 정독 → V-1 보강 프롬프트 작성 → V-1 카드 진입 (누적 자료 검증 + V-1b KARPATHY §1 재작성 보고서).
