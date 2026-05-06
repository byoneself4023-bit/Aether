# ADR 0020 — D-4 Audit 정리 vs 보류 결정 (D-4)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: D-4 (Audit 종합)
- **결정 근거**: 14 카드 머지 + WORK_PATTERNS 18 검증 + ADR 0011 / 0014 (보류 결정) 형식 인용

---

## 컨텍스트

카드 14건 머지 (M-1 / F-1 / F-1a / D-1 / D-2 / D-0 / D-3 / D-9 / D-8 / T-2c / T-6b / D-7 / D-5 / D-6) 후 종합 Audit 결과 미세 영역 4 라인 발견. 정리 vs 보류 결정 추적.

D-4 본질: 카드 결정 변경 X / 누적 학습 정착만 + 미세 정리 영역만.

---

## 결정

### 정리 영역 (본 카드 commit)

| 영역 | 라인 | 본질 | 회귀 검증 |
|---|---|---|---|
| `portfolio-service/app/config.py:37` HS256 주석 → HS512 | 1 | F-1a sync 누락 정리 | docstring만 / 회귀 0 |
| `llm-service/app/config.py:45` HS256 주석 → HS512 | 1 | 동일 | docstring만 / 회귀 0 |
| `portfolio-service/app/config.py:26-27` mlflow_tracking_uri / mlflow_experiment_name 제거 | 2 | D-1 잔재 정리 | 사용처 0 검증 (grep) |
| **합계** | **4** | — | llm 357 + portfolio 203 통과 |

### 보류 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| 본격 코드 audit (security / dead code 본격 분석) | 시나리오 B 진입 |
| 의존성 cleanup (사용 X 패키지 제거) | 본격 production |
| 테스트 커버리지 90%+ (현재 81%) | 시나리오 B 의무 |
| deprecation warning 본격 처리 (asyncio / Pydantic) | 본격 production / 비용 ↑ |
| 본격 LLM 비용 추적 (Token Tracker) | 시나리오 B 진입 |

---

## 영향

### 시그널 강화 (+)

- **양면 정책 10 ADR 정립**: 0011-**0020** = 본격 시니어 시그널 누적
- 누적 학습 정착 — WORK_PATTERNS 18 검증 (17 해소 / 1 부분 / 0 미해소)
- 면접 답변 객관 자료 — 14,414 LOC / 635 테스트 / 19 ADR / 3,354 누적 자료 LOC
- P-1 / I-1 진입 베이스라인 확보 — 깨끗한 main + 미세 잔재 0
- AUDIT.md 단일 자료 — 카드 14건 자료 분산 X

### 트레이드오프 (−)

- 본격 audit 미적용 (시나리오 B 트리거)
- 의존성 cleanup 미적용 — 비용 ↑ + 시나리오 A 영역 X
- 미세 영역만 정리 — 전수 검증 X

---

## 누적 baseline 진화 (D-4 시점)

| 영역 | 카드 시작 | 카드 14건 후 |
|---|---|---|
| ADR 수 | 9 | **19** (+10 / 0011-0019) |
| llm pytest | 232 | **357** (+125) |
| portfolio pytest | 212 | **203** (D-1로 −20 + T-2c +5 + D-2 +4 / 정확) |
| RAG relevance@k | N/A | **0.7413** (D-7 baseline) |
| 누적 자료 LOC | M-1 707 | **3,354** (+2,647) |
| ReAct 도구 | 4 | **5** (D-5 RAG 통합) |
| Streaming endpoint | 0 | **1** (D-6 SSE) |

---

## 미적용 영역 (시나리오 B 트리거 / ADR 0011 형식 일관)

본격 audit / 의존성 cleanup / 커버리지 90%+ / deprecation 본격 / Token Tracker — 모두 시나리오 B 진입 시점.

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **P-1** | D-4 머지 후 즉시 | PRINCIPLES 8/9/10 신규 패턴 |
| **I-1** | P-1 후 | 면접 답변 시뮬레이션 |
| **F-N (본격 audit)** | 시나리오 B 진입 | security / dead code 본격 |
| **F-N (의존성 cleanup)** | 본격 production | 사용 X 패키지 제거 |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-07 | v1 | 초기 Accepted (정리 4 라인 + 보류 5 영역 + 양면 정책 10 ADR 정립) |
