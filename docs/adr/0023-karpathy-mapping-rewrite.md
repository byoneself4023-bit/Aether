# ADR 0023 — KARPATHY_MAPPING §1 재작성 (영상 ↔ Aether 매핑) + LECTURE 단어 위생 (V-1b)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: V-1b (V-1 검증 결과 적용)
- **결정 근거**: VERIFICATION_v2.md §7 (의문 6 — KARPATHY §1 일치율 25%) + KARPATHY_LECTURE.md §16 비교 표 + MAPPING 본질 재정의

---

## 컨텍스트

V-1 검증 결과 (VERIFICATION_v2.md / 의문 7건 / 부족 5건 / 부분 충분 2건) 적용 카드. 핵심 발견: P-1 시점 작성 KARPATHY_MAPPING.md §1 8 본능 vs 카파시 영상 본문 9 본능 일치율 25% (2/8 / Skill Issue + Auto Research). 6건은 쿠카 영역 패턴 (Premortem / Reversibility / 5 Guards / 미적용 결정 / 본질 충돌 분리 / 측정 vs 추정 / 영상 본문 X).

**MAPPING 본질 재정의**: KARPATHY_MAPPING = 영상 9 항목 ↔ Aether 코드/카드 매핑. 단순 영상 정리 X (그건 LECTURE 영역). KARPATHY_MAPPING.md 자료 가치 = 매핑 본문 정착.

---

## 결정 (5 분기 추적)

### 분기 1: KARPATHY_MAPPING.md §1 재작성 본질 — **B 채택** (영상 9 ↔ Aether 매핑)

옵션 A (영상 9 항목만 정리) = LECTURE §15 중복 / MAPPING 본질 X.
옵션 B (선택) = 영상 9 항목 ↔ Aether 코드/카드 매핑 / 각 항목 = 3 영역 통합 (영상 인용 + Aether 적용 위치 + 적용 결과). MAPPING 본질 정착.
옵션 C (§1 + §2 + §3 + §4 + §5 통합 재작성) = 영역 ↑↑ / V-1b 카드 1책임 위반.

### 분기 2: 6건 쿠카 영역 처리 — **A 채택** (§부록 1-2줄 명시)

옵션 A (선택) = KARPATHY_MAPPING.md §부록 1-2줄만 명시 + 다른 자료 본문 인용 위치만. 자료 분산 이동 X.
옵션 B (META_REVIEW / WORK_PATTERNS / PRINCIPLES 분산 이동) = 자료 분산 비용 ↑ / 검색 비용 ↑ / 다른 자료 본문 이미 정착.

### 분기 3: KARPATHY_LECTURE.md 단어 위생 정정 영역 — **A 채택** (전 본문)

옵션 A (선택) = 전 본문 정정 (모든 위반 어휘 / grep 0건). V-1 시점 명시한 4 위반은 좁은 진단 — V-1b 시점 모든 위반 정정 의무.
옵션 B (4 위반만) = V-1 시점 진단 좁음 / 잔존 위반 다수 (특정 어휘 86건+).

### 분기 4: §6 면접 답변 매핑 영역 — **A 채택** (V-1b X / I-1 영역)

옵션 A (선택) = §6 = I-1 카드 본질 (면접 답변 시뮬레이션 카드) / V-1b 영역 X / KARPATHY_MAPPING.md §6 무변경.
옵션 B (V-1b 통합) = 카드 1책임 위반 / I-1 카드 분리 본질 흐림.

### 분기 5: ADR 의무 — **A 채택** (ADR 0023)

옵션 A (선택) = ADR 0023 결정 추적 + 영구 보류 영역 6건 명시 / 양면 정책 13 ADR 정립 (0011-0023).
옵션 B (ADR X) = 영구 보류 결정 추적 X / 6개월 후 본인 답 X.

---

## Decision

1. **KARPATHY_MAPPING.md §1 재작성** — 영상 9 항목 × 3 영역 통합 (영상 인용 + Aether 적용 위치 + 적용 결과)
   - 항목 1 AI Psychosis / 항목 2 Skill Issue / 항목 3 Macro Actions / 항목 4 Token Throughput
   - 항목 5 Persistent Loop / 항목 6 Auto Research / 항목 7 Jaggedness / 항목 8 AGENTS.md / 항목 9 Markdown for Agents
2. **KARPATHY_MAPPING.md §부록 신규** — 쿠카 영역 6건 (1-2줄 / 다른 자료 본문 인용 위치만)
3. **KARPATHY_LECTURE.md 단어 위생 전 본문 정정** — 5 위반 어휘 (LECTURE §16 비교 표 본문) = 0건 / grep 검증 의무
4. **AGENTS.md §7 V-1b baseline 행** — 의무 2건 정착 결과 + 양면 정책 13 ADR 정립
5. **ADR 0023** 결정 추적 (본 ADR / 5 분기 / 영구 보류 6건 / I-1 트리거)

---

## 영구 보류 영역 (V-1b 영역 X)

| 영역 | 보류 사유 |
|---|---|
| KARPATHY_MAPPING.md §2 매칭 점수 진화 표 | 본인 주관 / 객관성 X / 면접 가치 X |
| KARPATHY_MAPPING.md §3 매핑 표 | §1에 통합 / 자료 분리 가치 X |
| KARPATHY_MAPPING.md §4 미적용 영역 | §1에 통합 / 자료 분리 가치 X |
| KARPATHY_MAPPING.md §5 진화 사례 | META_REVIEW 중복 |
| KARPATHY_MAPPING.md §6 면접 답변 매핑 | I-1 카드 영역 (면접 답변 시뮬레이션) |
| 6건 쿠카 영역 분산 이동 (META_REVIEW / WORK_PATTERNS / PRINCIPLES) | 자료 분산 비용 ↑ / 다른 자료 본문 이미 정착 |

---

## 영향

### 시그널 강화 (+)

- **양면 정책 13 ADR 정립**: 0011-**0023** = 시니어 시그널 누적
- **MAPPING 본질 정착**: 영상 ↔ Aether 매핑 (단순 영상 정리 X)
- **LECTURE 단어 위생 정착**: 605 LOC 전 본문 / grep 0건 / 산출물 일관성 ↑
- **자료 단순화**: 영구 보류 6건 결정 추적 / 자료 가치 X 영역 정리
- **I-1 진입 자료 정착**: §1 = 영상 9 ↔ Aether 매핑 / I-1 시점 §6 작성 직접 인용

### 트레이드오프 (−)

- KARPATHY_LECTURE.md 86건+ 어휘 정정 영역 ↑ (Write 전 본문 재작성)
- Aether 매핑 정확성 검증 의무 (9 항목별 코드 위치 / ADR 번호 / 카드 ID)
- §2-§6 P-1 시점 본문 보존 = 단어 위생 미적용 (영구 보류 의무 우선 / G1 가드)

---

## 미적용 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| §2-§6 단어 위생 정정 | 영구 보류 / 시나리오 B 진입 시점에 정정 가능 (다만 §2-§6 가치 X 정착 = 영구 보류) |
| §6 면접 답변 매핑 재검토 | I-1 카드 (면접 답변 시뮬레이션) |
| 카파시 영상 시간대 정확성 검증 | 시나리오 B + 영상 재확인 의무 |
| 매칭 점수 객관 평가 도구 | 시나리오 B + 외부 평가 도구 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **I-1** | V-1b 머지 후 / 정리 카드 후 | 면접 답변 시뮬레이션 (KARPATHY §1 = 9 ↔ Aether 매핑 인용 / §6 작성) |
| **F-N (영상 검증)** | 시나리오 B 진입 | 카파시 영상 시간대 정확성 |
| **F-N (매칭 점수 객관화)** | 시나리오 B / 외부 평가 도구 | §2 매칭 점수 진화 표 객관화 |

---

## ADR 의존성

| ADR | 인용 위치 |
|---|---|
| 0011 D-1 보류 | 양면 정책 ADR 형식 시작 |
| 0014 D-9 보류 | 양면 정책 ADR 형식 일관성 |
| 0015 D-8 보류 | 양면 정책 ADR 형식 일관성 |
| 0020 D-4 Audit | 누적 자료 결정 추적 |
| 0021 P-1 카파시 매핑 | KARPATHY_MAPPING.md 초기 작성 (§2-§6) |
| 0022 V-1 검증 정책 | V-1 의문 7건 검증 결과 |
| **0023 (본 ADR)** | V-1b 결정 추적 (§1 재작성 + LECTURE 단어 위생 + 영구 보류 6건) |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-07 | v1 | 초기 Accepted (KARPATHY_MAPPING §1 재작성 / LECTURE 단어 위생 / §부록 6건 / 영구 보류 6건 / 양면 정책 13 ADR 정립 / I-1 트리거) |
