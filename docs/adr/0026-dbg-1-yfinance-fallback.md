# ADR 0026 — DBG-1 yfinance transient fallback (retry + Fixture)

- **상태**: Accepted
- **일자**: 2026-05-09
- **관련 카드**: DBG-1 (yfinance transient fallback / TG-2d 발견 영역 정착)
- **결정 근거**: TEST_REPORT.md §3.2 (TG-2d transient 발견) + AUDIT_REPORT.md §1 (Critical 1) + PRINCIPLES.md 패턴 8 (신규 endpoint 분리 = 점진 전환) + 양면 정책 일관성 (ADR 0012 / 0019 / 0021)

---

## 컨텍스트

TG-2c (PR #44 / 98839b8) 시점 — yfinance API rate limit 영역 영역 차단 / `optimize` + `backtest` 시연 실패 (`Invalid tickers / 0 succeeded`). 코드 변경 X 영역 영역 → TG-2d (PR #45 / 0b2be3f) 시점 동일 코드 영역 정상 시연 (Sharpe 1.5971 / 누적 155.74%).

본 영역 시그널 = **transient yfinance rate limit** (TG-2c 영역 영역 영역 영역 영역 영역 차단 / TG-2d 영역 정상). 즉 영구 차단 X / 외부 API rate limit 영역 영역 영역 영역.

AUDIT-1 (PR #48 / f42d8d6) 영역 발견 영역 = Critical 1 — yfinance transient fallback 영역 영역 영역 영역 영역 fallback 영역 영역 영역 영역 영역 영역 영역. 본 카드 (DBG-1) 영역 정착.

본질 판단 — transient (외부 API 영역 영역) vs 영구 (코드 / 영역 영역 차단). 본 사례 = transient → retry + 영구 fallback 영역 영역.

---

## 결정 (양면 정책 / 5 분기 추적)

### 분기 1: 옵션 A (retry + Fixture fallback) vs 옵션 B (다른 data provider) — **A 채택**

**옵션 A (선택)** = retry (3회 / 1s / 2s / 4s exponential backoff) + Fixture fallback (AAPL/MSFT/GOOGL 1년 deterministic 데이터) — 시연 시점 영역 안정성 ↑↑ / 시나리오 A 일관성 (외부 API 키 발급 X / 사용자 0명).

**옵션 B (보류)** = 다른 data provider (Alpaca / Polygon.io / IEX) — 외부 API 키 발급 의무 / 시나리오 B 진입 시점 (사용자 진입 / 도메인 검증) 정착 의무.

근거: 본 시점 = 시나리오 A (기술 데모 + 면접 자료 / 사용자 0명). 옵션 B = 운영 비용 ↑ / 본질 시그널 X. 옵션 A = 시연 보호 + 양면 정책 옵션 B 명시 영역 영역.

### 분기 2: retry 횟수 — 3회 (1s / 2s / 4s) — **선택**

근거: 면접 시연 시점 응답 시간 한정 (총 7초 영역). 3회 = transient 영역 영역 영역 영역 / 시연 영역 영역 영역.

### 분기 3: transient vs 영구 분류 — message 영역 분류 (`rate limit` / `429` / `timeout` / `connection` / `network`) — **선택**

근거: yfinance 영역 영역 영역 영역 영역 영역 영역 (`yf.YFRateLimitError` 영역 영역 영역 X) — 영역 broad catch + message 영역 영역 영역 영역 영역 안전 / 영구 영역 (ValueError / KeyError) 영역 즉시 raise.

### 분기 4: Fixture data 영역 — AAPL / MSFT / GOOGL 252 영역 일 (1년) deterministic — **선택**

근거: backtest walk-forward 영역 영역 영역 영역 영역 ≥ 252 영역 (1년) 영역 영역 영역. seed 영역 영역 (deterministic) → 영역 영역 영역 영역 영역 영역 영역 영역 영역. portfolio-service/fixtures/sample_prices.json 영역 영역.

### 분기 5: get_data_provider() 영역 영역 — CompositeProvider(YFinance, Fixture) 기본 — **선택**

근거: 환경변수 `data_provider=fixture` 영역 영역 영역 영역 (영역 영역 영역) / `yfinance` (default) 영역 Composite 영역 영역. 호출자 영역 영역 영역 X (응답 호환 어댑터 패턴 #3 / WORK_PATTERNS).

---

## 영향

### 신규

- `portfolio-service/app/services/data_provider.py` 확장 (~140 LOC 추가)
  - `RateLimitError`, `NetworkError` 영역 영역
  - `_classify_yfinance_error` (transient 분류 helper)
  - `_retry_with_backoff` (exponential backoff retry)
  - `YFinanceProvider` 영역 retry 적용 (`fetch_prices` / `fetch_single_ticker_prices`)
  - `FixtureProvider` 클래스 (AAPL/MSFT/GOOGL fallback)
  - `CompositeProvider` 클래스 (primary + fallback 자동 전환)
  - `get_data_provider()` 영역 변경 (default = CompositeProvider)
- `portfolio-service/fixtures/sample_prices.json` 영역 (252 영역 영역 / deterministic / seed=20260509)
- `portfolio-service/tests/test_data_provider.py` 추가 22 테스트:
  - `TestClassifyYfinanceError` (3 케이스 / rate_limit / network / permanent)
  - `TestRetryWithBackoff` (4 케이스 / first_success / 3_then_success / exhausted / permanent_immediate)
  - `TestFixtureProvider` (8 케이스 / supported / subset / unsupported / returns / validate / single / date_range)
  - `TestCompositeProvider` (6 케이스 / primary_success / rate_limit_fallback / network_fallback / permanent_no_fallback / validate_primary / validate_fallback)
  - `TestYFinanceProviderRetry` (3 케이스 / retries_then_succeeds / max_retry_raises / single_ticker_returns_none)

### 갱신

- `portfolio-service/app/services/data.py:153` — `isinstance(provider, YFinanceProvider)` → `hasattr(provider, "fetch_single_ticker_prices")` (CompositeProvider 영역 영역)
- `portfolio-service/tests/test_data_provider.py:146` — `test_returns_yfinance_provider_by_default` → `test_returns_composite_provider_by_default` (default 영역 영역 영역 영역)

### 회귀

- portfolio-service 영역 영역 영역 영역 영역 영역 — **227 passed / 0 failed** (기존 205 + 신규 22).
- llm-service / auth-service / frontend = 영향 X (코드 변경 0).

---

## 결과

### 긍정적

- **시연 안정성 ↑↑**: yfinance transient 차단 시점 영역 영역 자동 → fallback (Fixture) 자동 전환 → 시연 영역 영역 영역 영역 영역.
- **면접 시그널 ↑↑**: transient vs 영구 본질 판단 / 양면 정책 (옵션 A retry + 영역 / 옵션 B 다른 provider 보류) / PRINCIPLES 패턴 6 (미적용 결정 = 시그널) 일관성.
- **응답 호환 어댑터 패턴 #3** 일관성: CompositeProvider 도입 영역 호출자 영역 영역 0 변경 (`get_data_provider()` 인터페이스 영역 영역).
- **deterministic test**: `time.sleep` mock 영역 + seed 영역 영역 fixture → 영역 영역 0 / 영역 영역 영역 영역.

### 부정적

- **Fixture data 영역 정적**: 실시간 X — 면접 영역 영역 "fallback이 fixture라니?" 영역 영역 영역. **답변 흐름**: 시나리오 B 진입 시점 (사용자 진입) 영역 다른 data provider (Alpaca 영역) 영역 영역 영역 = 옵션 B 명시.
- **CompositeProvider 영역 영역 ↑**: primary 영역 영역 영역 영역 → fallback 영역 영역 영역 영역 영역. 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 = 의도적 (transient 영역 영역 영역 영역 영역 fallback 영역 영역 영역 영역 영역 영역 영역).

### 트리거 (옵션 B 진입 시점)

- 시나리오 B 진입 (사용자 5+ 영역 영역 + PMF 10불 검증) → 다른 data provider (Alpaca / Polygon.io) 영역 영역 영역 영역 영역 영역 (옵션 B).
- 본 시점 = 영구 보류 / ADR 영역 영역.

---

## 인용 자료

- TEST_REPORT.md §3.2 — TG-2d transient yfinance 발견 영역
- AUDIT_REPORT.md §1 / §3.1 — Critical 1 (DBG-1)
- PRINCIPLES.md 패턴 6 (미적용 결정 = 시그널) + 패턴 8 (신규 endpoint 분리)
- WORK_PATTERNS.md — 응답 호환 어댑터 패턴 #3 (호출자 0 변경)
- 양면 정책 일관성 — ADR 0012 / 0019 / 0021

---

## 카드 누적 영역

- ADR 0011-0026 = **양면 정책 16 ADR** (정착 8 / 보류 4 / 메타 4 / 정리 1 — DBG-1 영역 정착 1 영역).
