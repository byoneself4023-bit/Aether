# ADR 0022 — 누적 자료 검증 + V-1b 트리거 정착 (V-1)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: V-1 (검증 전용 / 코드 변경 0)
- **결정 근거**: V-0 머지 (DIGEST.md 812 LOC + KARPATHY_LECTURE.md 605 LOC) 후 베이스라인 / I-1 진입 자료 영역 / KARPATHY_MAPPING.md §1 일치율 25% 발견 / ADR 0011 / 0014 / 0020 / 0021 형식 인용

---

## 컨텍스트

V-0 머지 (PR #35 / commit `684fa40`) 후 누적 자료 12 파일 통합 (10 자료 + KARPATHY_LECTURE.md + DIGEST.md). DIGEST.md §5에서 의문 7건 명시 — V-1 본 카드 = 의문 검증 + V-1b 트리거 영역 정착 + I-1 진입 자료 영역 베이스라인 확보.

V-0 카드 본질 = 자료 추출만 (검증 X). V-1 본 카드 본질 = 검증만 (보강 X). V-1b 카드 = 보강 (KARPATHY §1 재작성 + 단어 위생 보강 + 면접 답변 재검토). 영역 분리 본능 (PRINCIPLES 패턴 7 본질 충돌 분리 직격) — V-1 / V-1b / I-1 카드 영역 각각 명확.

---

## 분기 결정 추적 (5 분기)

### 분기 1: V-1 영역 분리

| 옵션 | 본질 | 결과 |
|---|---|---|
| A | V-1 = 검증만 / V-1b = 보강 별도 | ✓ 영역 분리 정착 |
| B | V-1 = 검증 + 보강 통합 | ❌ 영역 ↑↑ / 카드 본질 모호 / PRINCIPLES 패턴 7 위반 |

### 분기 2: KARPATHY §1 재작성 영역

| 옵션 | 본질 | 결과 |
|---|---|---|
| A | V-1b 카드 별도 / 본 카드 = 트리거 영역만 정착 | ✓ 영역 분리 |
| B | V-1에서 통합 | ❌ 영역 ↑↑ |

### 분기 3: KARPATHY_LECTURE.md 단어 위생 보강

| 옵션 | 본질 | 결과 |
|---|---|---|
| A | V-1b 통합 (KARPATHY §1 + LECTURE 단어 위생 + 시간대 검증) | ✓ 통합 영역 |
| B | 별도 카드 | ❌ 카드 영역 ↑↑ |

### 분기 4: 검증 결과 산출물

| 옵션 | 본질 | 결과 |
|---|---|---|
| A | VERIFICATION_v2.md 신규 / 기존 0 변경 | ✓ D-4 패턴 일관성 (V-1 / V-2 versioning 본능) |
| B | DIGEST.md 갱신 | ❌ V-0 산출물 영역 변경 |
| C | 별도 보고서 파일 | ❌ 자료 분산 |

### 분기 5: ADR 의무

| 옵션 | 본질 | 결과 |
|---|---|---|
| A | ADR 0022 / V-1 검증 결과 결정 추적 | ✓ 양면 정책 12 ADR 정립 (0011-0022) |
| B | ADR X | ❌ 추적 약함 / PRINCIPLES 원칙 5 위반 |

---

## 결정

본 카드 V-1 = 누적 자료 검증 카드. 산출물 = VERIFICATION_v2.md (413 LOC) + 본 ADR 0022 + AGENTS.md §7 V-1 baseline 행. 7 의문 검증 결과:

- **부족 5건** (의문 1 / 2 / 4 / 6 / 7) → V-1b 통합 트리거
- **부분 충분 2건** (의문 3 / 5) — 의문 3 = META_REVIEW Phase 8 후보 (별도 카드) / 의문 5 = AGENTS §7 V-1 baseline 행 추가 (본 카드)

**V-1b 카드 본격 의무 5건 정착**:
1. KARPATHY §1 재작성 (영상 본문 9 본능 / 직접 인용 + 사례)
2. KARPATHY_LECTURE.md 단어 위생 보강 4 위반 정정 (라인 532 / 534 / 541 / 564)
3. 6건 쿠카 영역 본능 별도 자료 이동 (Premortem / Reversibility / 5 Guards / 미적용 결정 / 본질 충돌 / 측정)
4. 매칭 점수 진화 표 재계산 (실제 9 본능 기준)
5. 면접 답변 5 영역 재검토 (실제 카파시 본능 인용)

**I-1 진입 자료 영역 베이스라인 정착**: KARPATHY §6 / PRINCIPLES §8/§9/§10 / ADR 21건 / META_REVIEW §9 / SCENARIO §🎯 / AUDIT §6 / VERIFICATION §9 / KARPATHY_LECTURE 17 영역 = 자료 8건 정착. V-1b 머지 후 본격 정착 (실제 카파시 본능 인용 가능).

---

## 미적용 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| META_REVIEW v2 (Phase 8 정착) | V-1b 머지 후 또는 I-1 머지 후 |
| 카파시 영상 시간대 정확 검증 | 시나리오 B + 영상 재확인 의무 |
| 매칭 점수 객관화 (자가 평가 → 외부 도구) | 시나리오 B + 본격 평가 도구 |
| Phase 8 영역 (P-1 메타 / V-0 디제스트 / V-1 검증 / V-1b 보강 회고) | META_REVIEW v2 카드 진입 시점 |

---

## 트레이드오프

**정착**: V-1 = 검증만 / V-1b = 보강 / I-1 = 면접 답변 시뮬레이션 영역 분리 본능 = PRINCIPLES 패턴 7 (본질 충돌 분리) 직격 적용. 6개월 후 다른 개발자 *"왜 V-1 / V-1b / I-1 분리?"* 답 가능.

**비용**: 카드 영역 ↑↑ (Top 10 종료 후 카드 16건 + V-1 → 17건 / V-1b → 18건 / I-1 → 19건). V-N 시리즈 (V-0 / V-1 / V-1b) 영역 누적.

**대안 비용**: 영역 분리 X 시 V-1 영역 ↑ (검증 + 보강 + 시뮬레이션 통합) — 카드 본질 모호 + 검증 깊이 부족 + Round Cap 위반 위험.

---

## 롤백

`git revert <commit>` 1 줄. VERIFICATION_v2.md / ADR 0022 / AGENTS.md §7 V-1 baseline 행 제거. 누적 자료 11 파일 / DIGEST.md / KARPATHY_LECTURE.md / 카드 16건 결정 / 코드 본문 = 본 카드 영향 0 (모두 보존).

---

## 후속 카드 트리거

| 카드 | 트리거 조건 | 본질 |
|---|---|---|
| **V-1b** | 본 카드 머지 즉시 | KARPATHY §1 재작성 + LECTURE 단어 위생 보강 + 6건 쿠카 영역 이동 + 매칭 점수 재계산 + 면접 답변 재검토 |
| **META_REVIEW v2** | V-1b 머지 후 또는 I-1 머지 후 | Phase 8 정착 (P-1 / V-0 / V-1 / V-1b 회고) |
| **I-1** | V-1b 머지 후 | 면접 답변 시뮬레이션 (실제 카파시 본능 인용 가능) |

---

## 참조

- `docs/agent-capability-audit/VERIFICATION_v2.md` — V-1 검증 결과 본문 (의문 7건 + V-1b 트리거 5건 + I-1 진입 자료 영역)
- `docs/agent-capability-audit/DIGEST.md` §5 — 검증 X 의문 영역 7건 (V-0 산출물)
- `docs/agent-capability-audit/KARPATHY_MAPPING.md` §1 — 일치율 25% 발견 영역 (V-1b 재작성 의무)
- `docs/agent-capability-audit/KARPATHY_LECTURE.md` §15-§16 — 9 본능 + 비교 표 (V-1b source of truth)
- ADR 0011 / 0014 / 0020 / 0021 (양면 정책 형식 + 메타 결정 형식 인용)
