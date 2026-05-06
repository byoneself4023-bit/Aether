# ADR 0011 — 본질 X 기능 보류 결정 (D-1)

- **상태**: Accepted (보류 결정)
- **일자**: 2026-05-06
- **관련 카드**: D-1 (`docs/agent-capability-audit/META_REVIEW.md` §6.4 정착)
- **결정 근거**: META_REVIEW §6.4 + SCENARIO.md (시나리오 A 정의) + PRINCIPLES 패턴 6 ("박지 않은 결정 = 명시한 결정만큼 강한 시그널")

---

## 컨텍스트

META_REVIEW §6.4 (라인 438-460)는 시나리오 A (기술 데모 + 면접 / 사용자 0명) 본질 X 기능 3건을 식별했다:

| 기능 | 사유 |
|---|---|
| MLflow experiment | 사용처 미증명 / MLflow 통합 완료도 불명확 |
| drift_detector | "하면 좋아 보임" 영역 / 시그널은 있지만 데모 동작 X |
| weight_monitor | 알림 구독자 부재 |

3 기능 모두 시나리오 A 본질 X. 단순 제거가 아닌 **시나리오 적합성 기준 필터링** 결정 필요. PRINCIPLES 패턴 6 — "박지 않은 결정 + 진입 트리거 명시" = 시니어 시그널 핵심.

핵심 위험: drift_detector 모듈은 MCP `get_recommendation` 도구 (T-2 차별화 카드)가 `analyze_drift` 함수를 직접 호출하여 의존 중. 모듈 자체 제거 시 T-2 차별화 손상.

---

## 결정

### 1. MLflow experiment 완전 제거

- 라우터 (`app/routers/experiment.py`) + 모듈 (`app/services/experiment.py`) + 테스트 (`tests/test_experiment.py`) + 의존성 (`requirements.txt` `mlflow==2.9.2`) 모두 제거.
- 사유: 시나리오 A 본질 X + 외부 사용 0건 (frontend / llm / mcp 모두 미사용).
- 5 endpoints 제거 (`POST /api/experiment/optimize` / `compare` / `backtest` + `GET /results` / `best`).

### 2. drift_warning / weight_alerts 응답 키 제거

- `OptimizeResponse.drift_warning` / `OptimizeResponse.weight_alerts` 필드 + `OptimizeRequest.previous_weights` / `weight_change_threshold` 필드 제거.
- 관련 Pydantic 모델 4건 (`DriftWarning` / `DriftMetrics` / `WeightComparisonResponse` / `WeightChangeAlertResponse`) 제거.
- `routers/optimize.py` drift / weight 통합 코드 약 60 라인 제거.
- 외부 사용 0건 (frontend / llm / mcp 모두 미사용).

### 3. drift_detector.py / weight_monitor.py 모듈 보존

- 사유 1 (MCP 의존): MCP `get_recommendation` 도구가 `analyze_drift` 함수를 직접 호출 — 모듈 자체 제거 시 T-2 차별화 손상.
- 사유 2 (회복 자료): 시나리오 B 진입 시 응답 키 복원 + UI 통합 시 즉시 재활성화 가능.
- 모듈 + 단위 테스트 (`tests/test_drift_detector.py` / `tests/test_weight_monitor.py`) 보존.

### 4. 진입 트리거 (재활성화 조건)

다음 중 하나 충족 시 후속 카드 (F-N) 진입:

- **트리거 1 — 시나리오 B 진입**: 실 사용자 1+ 명 발생 (포트폴리오 이외 사용 시점). 사용자 알림 구독 의도 확인 후 weight_alerts UI 통합.
- **트리거 2 — Houseman Phase 7-12 도메인 검증**: 이 시점에 drift_detector / weight_monitor가 실제 도메인 의사결정에 시그널 제공함을 검증한 경우 응답 키 복원.

---

## 영향

### 시그널 강화 (+)

- PRINCIPLES 패턴 6 ("박지 않은 결정 + 트리거 명시") 정착 — 시니어 의사결정 직격.
- 시나리오 A 본질 X 기능 0건 도달 — 응답 schema 단순화.
- 면접 답변 가능: "drift_detector / weight_monitor는 시나리오 B 진입 시점 트리거로 박았다. 기술 데모에선 시그널 X."

### 기능 다양성 감소 (−)

- `OptimizeResponse` 응답 키 2개 제거 (drift_warning / weight_alerts) → schema breaking change.
- 영향 검증: frontend / llm / mcp 외부 사용 0건 (D-1 Phase 1 실측). 시나리오 A 사용자 0명 = 영향 없음.

### MCP T-2 차별화 보존

- drift_detector 모듈 보존 → MCP `get_recommendation` 도구 정상 동작 유지.
- ADR 0008 (MCP 도구 4종) 갱신 X.

---

## 후속 카드

| 카드 | 트리거 조건 | 본질 |
|---|---|---|
| **F-N** (재도입) | 트리거 1 또는 2 발생 | drift_warning / weight_alerts 응답 키 복원 + UI 통합 |
| **F-N+1** (실험 추적) | MLflow 재도입 시점 (시나리오 B + 실제 모델 비교 의도 발생) | experiment 라우터 + 의존성 재도입 |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-06 | v1 | 초기 Accepted (D-1 카드 산출). 3 기능 보류 결정 + 트리거 명시. ADR 0010 (T-3 보류) 형식 적용. |
