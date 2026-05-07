# KARPATHY_MAPPING — 카파시 영상 9 항목 ↔ Aether 매핑 (V-1b)

> **카드**: V-1b (KARPATHY_MAPPING §1 재작성 + LECTURE 단어 위생) / P-1 (§2-§6 초기 작성)
> **작성일**: 2026-05-07
> **본질**: 카파시 영상 9 항목 (LECTURE §15) ↔ Aether 코드/카드 매핑 (§1) + §2-§6 P-1 시점 본문 보존 (영구 보류 / I-1 영역 / ADR 0023).
> **결론 한 줄**: §1 = 영상 9 ↔ Aether 매핑 정착 (각 항목 3 영역 통합) + §부록 6건 쿠카 영역 명시 + §2-§6 = 영구 보류. I-1 진입 자료 정착.

---

## §1 카파시 영상 9 항목 ↔ Aether 코드/카드 매핑

> **MAPPING 본질**: 영상 9 항목 (KARPATHY_LECTURE.md §15) ↔ Aether 코드/카드 매핑. 단순 영상 정리 X (그건 LECTURE 영역). 각 항목 = 3 영역 통합 (카파시 영상 본문 인용 + Aether 적용 위치 + 적용 결과).

---

### 항목 1: AI Psychosis — 12월 패러다임 전환

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §1):

> "I don't think I've typed like a line of code probably since December basically."
> "I'm just like in this state of psychosis of trying to figure out like what's possible."

**Aether 적용 위치**:
- 카드 진행 패턴 (M-1 ~ V-1b 18 카드 / 코드 직접 작성 X / Claude Code 위임 정착)
- 코드 변경 X (작업 흐름 영역 / 코드 영역 X)

**적용 결과**:
- 부분 적용 — 작업 흐름은 위임 정착 / 코드 검수는 본인 영역 의무.

---

### 항목 2: Skill Issue — AI 한계 X / 본인 활용 부족

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §2):

> "It's not that the capability is not there. It's that you just haven't found a way to string it together."

**Aether 적용 위치**:
- T-6b (_EMBED_DIM 768 → 3072 정정)
- ADR 0016 (Qdrant 명시 의무)
- llm-service/app/rag.py (chromadb 자동 차원 감지 → Qdrant 명시 차원 의무)

**적용 결과**:
- chromadb 자동 차원 감지로 stale 미발견 → Qdrant 명시 의무로 발견 → 즉시 정정 + ADR 0016 작성. 외부 SDK 영역 차이 인지 본능 정착.

---

### 항목 3: Macro Actions — 카드 단위 위임

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §3):

> "It's just like you can move in much larger macro actions. It's not just like here's a line of code, here's a new function. It's like here's a new functionality and delegate to agent one."

**Aether 적용 위치**:
- 카드 진행 패턴 (M-1 ~ V-1b 18 카드 / 카드 단위 위임 정착)
- 단일 인스턴스 한계 (다중 인스턴스 X — Houseman 트리거)

**적용 결과**:
- 부분 적용 — 카드 단위 위임은 정착 / 다중 인스턴스 영역 = Houseman 트리거.

---

### 항목 4: Token Throughput — 본인 = 시스템 병목 X

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §4):

> "I feel nervous when I have subscription left over that just means I haven't maximized my token throughput."

**Aether 적용 위치**:
- 단일 세션 작업 (token throughput 최대화 X)
- HOUSEMAN_APPLICATION.md 인용 (다중 세션 / Phase 7-12 트리거)

**적용 결과**:
- 미적용 — 시나리오 A에서 단일 세션 / Houseman Phase 7-12 진입 시 다중 세션 트리거.

---

### 항목 5: Persistent Loop / Claw — 지속 루프 + sandbox

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §5):

> "Has like maybe more sophisticated memory systems etc that have not yet implemented in agents."

**Aether 적용 위치**:
- 시나리오 A 한계 (Persistent Loop X / Claude Code 단일 세션)
- HOUSEMAN_APPLICATION.md 인용 (Phase 7-12 트리거 / sandbox 영역)

**적용 결과**:
- 미적용 — 시나리오 A 한계 / Houseman 트리거.

---

### 항목 6: Auto Research — 인간 결정 최소화

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §7):

> "Auto research is just yeah here's an objective here's a metric here's your boundaries of what you can and cannot do and go."

**Aether 적용 위치**:
- D-7 (RAG Chunking grid search / 9 조합)
- ADR 0017 (chunk_size=500 / overlap=300)
- scripts/grid_search_chunking.py
- relevance@k 0.7222 → 0.7413 (+0.019)

**적용 결과**:
- 정착 — 9 조합 자동 비교 / 인간 직관 X / 메트릭 자동 비교 본능 정착.

---

### 항목 7: Jaggedness — Verifiable vs 비-Verifiable

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §8):

> "I simultaneously feel like I'm talking to an extremely brilliant PhD student who's been like a systems programmer for their entire life and a 10-year-old."

**Aether 적용 위치**:
- D-8 (RAG 평가 자체 4 메트릭 / ragas 미도입)
- ADR 0015 (ragas 보류 결정)
- scripts/eval_rag.py (자체 4 메트릭: relevance@k / precision@k / latency / cost)

**적용 결과**:
- 부분 적용 — Verifiable 영역 (RAG 평가) 자체 정착 / 비-Verifiable 영역 = ragas 보류 (시나리오 B 트리거).

---

### 항목 8: AGENTS.md / Soul.md — 에이전트 인지 자료 + 페르소나

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §5):

> "It doesn't seem to care about what you're creating. It's kind of like, oh, I implemented it. It's like, okay, but do you understand what we're building?"

**Aether 적용 위치**:
- AGENTS.md (302 LOC / §7 지배 숫자 / 카드 §8 체크리스트)
- Soul.md X (페르소나 자료 X — Houseman 트리거)

**적용 결과**:
- 부분 적용 — AGENTS.md 정착 / Soul.md = Houseman 트리거.

---

### 항목 9: Markdown for Agents — 교육 패러다임 전환

**카파시 영상 본문 인용** (KARPATHY_LECTURE.md §14):

> "I'm not explaining to people anymore. I'm explaining it to agents."
> "Instead of HTML documents for humans you have markdown documents for agents."

**Aether 적용 위치**:
- 자료 본문 모두 Markdown 정착 (DIGEST / VERIFICATION / META_REVIEW / WORK_PATTERNS / PRINCIPLES / KARPATHY_LECTURE / KARPATHY_MAPPING / SCENARIO / AUDIT)
- ADR 23건 (0001-0023 모두 Markdown)
- 카드 18건 (M-1 ~ V-1b / docs/agent-capability-audit/phase3/)

**적용 결과**:
- 정착 — 자료 / ADR / 카드 모두 Markdown / 에이전트 인지 영역.

---

## §2 8 본능 매칭 점수 진화 + 사유

### 자가 평가 기준

- **70-79**: 본능 인지 + 부분 적용
- **80-89**: 본능 적용 일관성 + 사례 누적
- **90-95**: 본능 본격 정착 + 카드별 검증
- **95+**: 영상 검증 + 외부 평가 도구 (시나리오 B 트리거)

### 진화 표

| # | 본능 | 시작 (M-1) | D-4 후 | 현재 (P-1) | 진화 사유 |
|---|---|---|---|---|---|
| 1 | Skill Issue | 70 | 90 | **95** | T-6b _EMBED_DIM 768 stale 발견 — 외부 SDK 영역 차이 인지 + 자가 점검 본능 정착 |
| 2 | Auto Research | 70 | 85 | **90** | D-7 grid search 9 조합 자동 — 인간 직관 X / 메트릭 자동 비교 본능 정착 |
| 3 | Premortem | 75 | 85 | **88** | 14 카드 모두 "위험 시나리오 6+" 명시 — 사전 예측 패턴 일관성 |
| 4 | Reversibility | 80 | 88 | **90** | 14 카드 Type 1/2/3 명시 + D-5/D-6 환경변수 토글 점진 전환 본능 |
| 5 | 5 Guards | 78 | 87 | **88** | G1-G5 매 카드 적용 / Round Cap 1 의무 정착 |
| 6 | 박지 않은 결정 | 75 | 85 | **88** | ADR 0010/0011/0014 보류 결정 명시 + 양면 정책 11 ADR 정립 |
| 7 | 본질 충돌 분리 | 75 | 80 | **80** | T-3 / D-9 / D-8 본질 분리 검증 — 다만 본능 자가 인지 영역 미흡 |
| 8 | 본격 측정 vs 추정 | 70 | 80 | **85** | F-1 VERIFICATION + D-8 baseline + D-7 grid + D-6 SSE 첫 응답 시간 실측 |
| **평균** | — | **76** | **85** | **87** | +11점 진화 |

### 진화 추적 본질 (D-4 → P-1 / +2점)

- T-6b 머지 후 Skill Issue +5 (768 stale 발견 사례)
- D-7 머지 후 Auto Research +5 (grid search)
- 다만 본능 7 (본질 충돌 분리) 진화 X — 자가 인지 영역 미흡 (T-3 / D-9 답 흔들림 사례 + PRINCIPLES §7 정착 후 추가 진화 영역 의무)

---

## §3 8 본능 × 14 카드 매핑

| 카드 | 1 Skill | 2 Auto | 3 Pre | 4 Rev | 5 Guards | 6 미적용 | 7 충돌 | 8 측정 |
|---|---|---|---|---|---|---|---|---|
| C-1 (T-3 보류) | - | - | ✓ | ✓ | ✓ | **✓** | **✓** | - |
| M-1 (META_REVIEW) | ✓ | - | ✓ | - | - | - | ✓ | ✓ |
| F-1 (VERIFICATION) | ✓ | - | ✓ | ✓ | ✓ | - | - | **✓** |
| F-1a (HS512 통일) | ✓ | - | ✓ | ✓ | ✓ | - | - | ✓ |
| D-1 (본질 X 보류) | - | - | ✓ | ✓ | ✓ | **✓** | ✓ | ✓ |
| D-2 (운영급) | - | - | ✓ | ✓ | ✓ | ✓ | - | - |
| D-0 (frontend 정리) | - | - | - | ✓ | ✓ | - | - | - |
| D-3 (페이지 분리) | - | - | ✓ | ✓ | ✓ | ✓ | - | - |
| D-9 (RAG 정제 보류) | ✓ | - | ✓ | ✓ | ✓ | **✓** | ✓ | ✓ |
| D-8 (RAG 평가) | - | **✓** | ✓ | ✓ | ✓ | ✓ | - | **✓** |
| T-2c (MCP fix) | ✓ | - | ✓ | ✓ | - | - | - | ✓ |
| T-6b (Qdrant 전환) | **✓** | - | ✓ | ✓ | **✓** | - | - | ✓ |
| D-7 (Chunking grid) | - | **✓** | ✓ | ✓ | ✓ | ✓ | - | **✓** |
| D-5 (5 도구) | - | - | ✓ | **✓** | ✓ | ✓ | - | ✓ |
| D-6 (SSE) | - | - | ✓ | **✓** | ✓ | ✓ | ✓ | **✓** |
| **충족 합계** | 6 | 2 | 13 | 13 | 12 | 7 | 5 | 11 |

**핵심 매핑 시그널**:
- 본능 3 (Premortem) / 4 (Reversibility) / 5 (Guards) — 14 카드 거의 모두 충족 (12-13건)
- 본능 8 (본격 측정) — 11건 (D-8 / D-7 / D-6 baseline 측정 본능 정착)
- 본능 1 (Skill Issue) — 6건 (T-6b / F-1a / D-9 / T-2c / M-1 / F-1) / **본격 진화 시점은 T-6b**
- 본능 2 (Auto Research) — 2건 (D-8 / D-7) / **D-7이 본격 정착**
- 본능 7 (본질 충돌 분리) — 5건 / **자가 인지 영역 미흡**

---

## §4 미적용 영역 (시나리오 B 트리거)

| 영역 | 카파시 본능 | 트리거 |
|---|---|---|
| 본격 audit (security / dead code) | 본능 1 + 8 | 시나리오 B 진입 (실 사용자) |
| Multi-Agent (T-3 본격) | 본능 6 | 도메인 본격 검증 (Houseman Phase 7-12) |
| WebSocket 양방향 stream | 본능 4 | 실시간 대화 본격 의무 |
| 의존성 cleanup | 본능 1 | 본격 production |
| 매칭 점수 객관화 (자가 평가 → 외부 도구) | 본능 8 | 시나리오 B + 본격 평가 도구 |
| 카파시 영상 시간대 정확성 검증 | 본능 8 | 시나리오 B + 영상 재확인 의무 |
| 테스트 커버리지 90%+ | 본능 8 | 시나리오 B 의무 |

---

## §5 본인 영역 진화 사례 (META_REVIEW 인용)

> **0 변경 의무**: META_REVIEW.md / WORK_PATTERNS.md 본문 0 변경 — 본 §5는 인용만.

### Houseman Phase 7-12 학습 정착 (META_REVIEW §8)

| 학습 | Aether 사례 |
|---|---|
| 학습 5 (모놀리식 회피) | D-3 frontend 페이지 분리 (200 LOC 임계) |
| 학습 8 (F-패턴: 검증 + 분기 + 머지) | 14 카드 매 머지 F-패턴 적용 |
| 학습 9 (응답 호환 어댑터) | T-6 vector_store 어댑터 + T-6b 정착 |

### Skill Issue 진화 사례 (META_REVIEW §1.4 + T-6b)

- 시작: 본인 한계 인지 약함 (Skill 70)
- T-6b 머지: chromadb 자동 감지로 stale 미발견 → Qdrant 명시 의무로 발견 → 즉시 정정 (Skill 90 → 95)
- 본능 결과: 외부 SDK 영역 차이 인지 본격 정착

---

## §6 면접 답변 매핑 (5 영역 + 꼬리 질문)

### 영역 1 — AI Agent 자율 판단

**핵심 답:** "ReAct agent 4 도구 → 5 도구 (D-5) → SSE token stream (D-6) — 사용자 의도 자율 판단 본능 진화."

**꼬리 질문:**
- Q: "왜 5 도구? 분리 본능 위반?" → A: "도메인 분리 (rag_tools ↔ portfolio_tools) + 자율 판단 본능. 영역 분리 X = AI Agent 본질"
- Q: "왜 SSE? WebSocket 안 쓴 이유?" → A: "단방향 본격 적합. WebSocket = 시나리오 B 트리거 (양방향 의무 발생)"
- Q: "Multi-Agent 안 쓴 이유?" → A: "T-3 보류 결정 (ADR 0010). 도구 6+ 확장 = Multi-Agent 본격 시점. 시나리오 A에서 자율 판단 5 도구로 충분"

### 영역 2 — 시나리오 A 본질

**핵심 답:** "사용자 0명 / 기술 데모 / 면접 영역 — 양면 정책 11 ADR 정립으로 본질 적합 결정 추적."

**꼬리 질문:**
- Q: "왜 ragas 안 쓴 이유?" → A: "D-8 PRE-CHECK 분기 2 — 자체 4 메트릭 + 의존성 0. 시나리오 B 진입 시 ragas 트리거"
- Q: "왜 RAG 정제 안 한 이유?" → A: "D-9 PRE-CHECK 분기 3 — 정제 대상 부재 (정적 4 md / 이미 정형). 시나리오 B 트리거"
- Q: "왜 시나리오 A?" → A: "META_REVIEW §6.4 본질 — 사용자 0명 환경에서 본격 정책은 비용 ↑ / 시그널 ↓"

### 영역 3 — 양면 정책 11 ADR

**핵심 답:** "정착 결정 6건 (0012 / 0013 / 0015 / 0016 / 0017 / 0018 / 0019) + 보류 결정 5건 (0010 / 0011 / 0014 / 0020 / 0021) = 양면 정책 11 ADR 정립."

**꼬리 질문:**
- Q: "왜 ADR 본격?" → A: "결정 근거 추적 — 6개월 후 본인 답 가능 + 면접 답 본능 (PRINCIPLES 원칙 5)"
- Q: "보류 결정도 ADR?" → A: "PRINCIPLES 6번 — 박지 않은 결정 = 명시 결정만큼 강한 시그널. 트리거 명시 의무"

### 영역 4 — 우대 요건 매칭

**핵심 답:** "SSE (D-6) / RAG 평가 (D-8) / Chunking 튜닝 (D-7) / Multi-Agent 보류 (T-3 / 0010) — 4 우대 요건 직격 매칭."

**꼬리 질문:**
- Q: "Hybrid Search?" → A: "시나리오 B 트리거 (ADR 0018 미적용 영역). BM25 + Vector 본격 = 도메인 다양성 ↑ 시점"
- Q: "Multi-Agent?" → A: "T-3 보류 결정 (ADR 0010) — 시나리오 A에서 5 도구 자율 판단 본능 충족. Houseman Phase 7-12 도메인 검증 시점 트리거"

### 영역 5 — 본인 영역 진화 (Skill Issue → 자동 정정)

**핵심 답:** "Skill Issue 본능 70 → 95 (T-6b _EMBED_DIM 768 stale 발견 사례). 외부 SDK 영역 차이 인지 + 자가 점검 본능 정착."

**꼬리 질문:**
- Q: "왜 진화?" → A: "chromadb 자동 차원 감지로 stale 미발견 → Qdrant 명시 의무로 발견 → 즉시 정정 + ADR 0016 본문 박음. 본능 결과: 외부 SDK 영역 차이 인지 본격 정착"
- Q: "본능 7 (본질 충돌 분리) 진화 X 이유?" → A: "T-3 / D-9 답 흔들림 사례 + PRINCIPLES §7 정착 후 추가 사례 부재. 본 카드 (P-1) 후 후속 카드 트리거"

---

## §부록 — 쿠카 영역 6건 (영상 본문 X / Aether 회고 영역)

본 6 영역은 영상 본문에 X / 본인 Aether 회고에서 정착한 시니어 패턴.
각 영역은 다른 자료 본문에 이미 정착 (자료 분산 이동 X / 검색 시 인용).

- Premortem (위험 시나리오 6+ 사전 예측) → META_REVIEW.md 본문
- Reversibility (Type 1/2/3 분기 결정) → META_REVIEW.md 본문
- 5 Guards (G1-G5) → WORK_PATTERNS.md §자기 일관성 패턴
- 측정 vs 추정 (실측 우선) → WORK_PATTERNS.md 본문
- 미적용 결정 = 시그널 → PRINCIPLES.md 패턴 6
- 본질 충돌 분리 → PRINCIPLES.md 패턴 7

---

## §갱신 이력

| 일자 | 변경 |
|---|---|
| 2026-05-07 (P-1) | 초기 작성 — 카파시 8 본능 정의 + 매칭 점수 진화 (76→87) + 8×14 매핑 + 미적용 7건 + 면접 답변 5 영역. P-1 카드 산출물. |
| 2026-05-07 (V-1b) | §1 재작성 (영상 9 항목 ↔ Aether 매핑 / 3 영역 통합) + §부록 신규 (쿠카 영역 6건 1-2줄) + §2/§3/§4/§5/§6 영구 보류 (ADR 0023 명시). KARPATHY_LECTURE.md 단어 위생 전 본문 정정. |

**한 문장**: §1 = 영상 9 ↔ Aether 매핑 정착 (V-1b) / §2-§6 = P-1 시점 본문 보존 (영구 보류 / I-1 영역) / §부록 = 쿠카 영역 6건 인용 위치 명시. KARPATHY_LECTURE.md = 단어 위생 정착.
