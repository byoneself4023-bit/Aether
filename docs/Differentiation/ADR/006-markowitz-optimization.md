# ADR-006: Markowitz 포트폴리오 최적화 + Shrinkage

## 상태: Accepted

---

## 맥락 (Context)

Aether의 핵심 기능은 사용자가 입력한 종목으로 최적 포트폴리오 비중을 계산하는 것이다. 최적화 알고리즘을 선택해야 했고, 실제 시장 데이터에서 안정적으로 동작해야 했다.

**요구사항**:
- 사용자가 종목 리스트를 입력하면 최적 비중 반환
- min_variance(최소 분산)와 max_sharpe(최대 샤프) 두 가지 전략 지원
- 상관관계가 높은 종목 조합에서도 안정적 결과
- 결과에 대한 해석 가능성 (왜 이 비중인지 설명)

---

## 고려한 선택지

### 옵션 A: Equal Weight (동일 비중)

- **장점**: 구현 0줄, 직관적, 추정 오차 없음
- **단점**: 최적화가 아님 — 리스크/리턴 최적화 없이 균등 분배, 포트폴리오 이론 적용이라 볼 수 없음

### 옵션 B: Markowitz Mean-Variance Optimization (MVO)

- **장점**: 현대 포트폴리오 이론(MPT)의 핵심, 학술적으로 가장 잘 정립됨, 효율적 프론티어 시각화 가능
- **단점**: 공분산 행렬 추정 오차에 민감 → 극단적 비중(한 종목 100%) 나올 수 있음, ill-conditioned 행렬에서 SLSQP 발산 가능

### 옵션 C: Black-Litterman Model

- **장점**: 시장 균형 수익률 + 투자자 뷰를 결합, Markowitz의 추정 오차 문제 완화
- **단점**: 시장 균형 가정 필요 (시가총액 데이터), 투자자 뷰 입력 UI/UX가 복잡, 구현 난이도 높음

### 옵션 D: Risk Parity

- **장점**: 각 자산이 동일한 리스크 기여 → 안정적, 2008 금융위기 이후 실무에서 인기
- **단점**: 기대수익률을 사용하지 않음 → 수익 최적화 불가, 레버리지 없이는 시장 대비 수익률 낮음

---

## 결정 (Decision)

**옵션 B: Markowitz MVO + Ledoit-Wolf Shrinkage + auto-regularization** 선택.

순수 Markowitz의 약점을 3단계로 보완:

```
1단계: Shrinkage 공분산 추정
   표본 공분산 대신 Ledoit-Wolf Shrinkage 사용
   → 추정 오차 30~50% 감소

2단계: 공분산 행렬 검증
   validate_covariance_matrix()
   → 대칭성, 양정치성, 조건수, 완전상관 검사

3단계: 자동 정칙화
   regularize_covariance()
   → 음의 고유값 클리핑 + Ridge regularization
   → 조건수를 10^8 이하로 보장
```

```python
# 실제 최적화 파이프라인
def get_returns_and_covariance_resilient(tickers, period, use_shrinkage=True):
    returns_df = fetch_returns_resilient(tickers, period)
    mu = returns_df.mean().values

    if use_shrinkage:
        cov = shrinkage_covariance(returns_df.values)    # Ledoit-Wolf
    else:
        cov = sample_covariance(returns_df.values)       # 표본 공분산

    # 검증 + 자동 정칙화
    validation = validate_covariance_matrix(cov)
    if not validation.is_valid:
        cov, validation = regularize_covariance(cov, validation)

    return ReturnsResult(mu=mu, cov=cov, ...)
```

**선택 이유**:
- Markowitz는 포트폴리오 이론의 교과서적 기반 → 면접에서 "왜 이 알고리즘?"에 대한 학술적 근거가 명확
- Shrinkage + regularization으로 실무에서의 약점(추정 오차, ill-conditioning)을 보완 → "이론만 아는 것"이 아닌 "실전 적용"을 증명
- 효율적 프론티어 계산이 가능 → UI에서 리스크-리턴 트레이드오프 시각화
- Black-Litterman은 시가총액 데이터 + 뷰 입력 UI가 필요하여 현재 범위 초과

---

## 결과 (Consequences)

**장점**:
- 수치 안정성: Shrinkage + Ridge로 어떤 종목 조합에서도 수렴하는 결과
- 진단 정보: `OptimizationDiagnostics`로 수렴 여부, 조건수, solver 메시지 투명하게 제공
- 드리프트 감지: 최근 20일 vs 과거 데이터 비교로 시장 체제 변화 경고
- 부분 실패 허용: 일부 티커 fetch 실패 시 나머지로 최적화 수행

**트레이드오프**:
- Markowitz는 "과거 = 미래" 가정 → 체제 변화(금융위기 등)에 취약. 드리프트 감지로 부분 보완
- max_sharpe의 기대수익률 추정이 과거 평균에 의존 → 예측 정확도 한계
- Shrinkage는 "타겟으로 수축"하므로 극단적 상관구조를 평활화 → 정보 손실 가능

---

## 재선택한다면?

같은 선택. 추가로 Black-Litterman을 옵션으로 제공하되, 기본값은 Markowitz + Shrinkage로 유지하겠다. Risk Parity도 백테스트 비교 전략으로 추가하면 사용자에게 선택지를 넓힐 수 있다.
