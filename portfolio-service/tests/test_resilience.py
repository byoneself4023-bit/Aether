"""장애 시뮬레이션 테스트 (portfolio-service)

외부 API 장애, 수치 안정성 등 장애 상황에서의 graceful degradation 확인.
모킹 기반 장애 주입 (unittest.mock).
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from app.services.optimizer import (
    optimize_min_variance,
    optimize_max_sharpe,
    validate_covariance_matrix,
    regularize_covariance,
)
from app.services.data import fetch_prices_resilient, FetchResult
from app.services.data_provider import (
    YFinanceProvider,
    set_data_provider,
    reset_data_provider,
    DataProvider,
)


@pytest.fixture(autouse=True)
def cleanup_provider():
    """각 테스트 후 provider 초기화"""
    yield
    reset_data_provider()


def _make_mock_provider(prices_map: dict[str, pd.Series | None]) -> MagicMock:
    """모킹 DataProvider 생성 헬퍼

    Args:
        prices_map: {ticker: Series or None} 매핑.
                    None이면 fetch 실패를 의미.
    """
    provider = MagicMock(spec=YFinanceProvider)

    def mock_single_fetch(ticker, period="3y", start_date=None, end_date=None):
        result = prices_map.get(ticker)
        if result is None:
            return None
        return result

    provider.fetch_single_ticker_prices = MagicMock(side_effect=mock_single_fetch)
    return provider


def _make_price_series(n_days: int = 252, start_price: float = 100.0,
                       daily_return: float = 0.0005, seed: int = 42) -> pd.Series:
    """테스트용 가격 시계열 생성"""
    rng = np.random.RandomState(seed)
    returns = rng.normal(daily_return, 0.02, n_days)
    prices = start_price * np.cumprod(1 + returns)
    dates = pd.date_range("2023-01-01", periods=n_days, freq="B")
    return pd.Series(prices, index=dates)


# ============================================================
# A. 외부 API 장애
# ============================================================

class TestExternalAPIFailure:
    """yfinance 네트워크 에러, 빈 데이터, 부분 실패 테스트"""

    # --- A-1. yfinance 네트워크 에러 ---

    def test_network_error_returns_structured_error(self):
        """A-1. yfinance 네트워크 에러 시 → 구조화된 에러 (ValueError)"""
        # Given: 모든 티커가 Exception을 던짐
        provider = MagicMock(spec=YFinanceProvider)
        provider.fetch_single_ticker_prices = MagicMock(
            side_effect=ConnectionError("Network unreachable")
        )
        set_data_provider(provider)

        # When & Then: 모든 티커 실패 → min_tickers 미만 → ValueError
        with pytest.raises(ValueError, match="Insufficient valid tickers"):
            fetch_prices_resilient(
                tickers=["AAPL", "GOOGL", "MSFT"],
                period="3y",
                min_tickers=2,
                use_cache=False
            )

    # --- A-2. yfinance 빈 데이터 반환 ---

    def test_empty_data_returns_error(self):
        """A-2. yfinance 빈 데이터 반환 시 → '데이터 없음' 에러"""
        # Given: 모든 티커가 None (빈 데이터) 반환
        provider = _make_mock_provider({
            "AAPL": None,
            "GOOGL": None,
            "MSFT": None,
        })
        set_data_provider(provider)

        # When & Then
        with pytest.raises(ValueError, match="Insufficient valid tickers"):
            fetch_prices_resilient(
                tickers=["AAPL", "GOOGL", "MSFT"],
                period="3y",
                min_tickers=2,
                use_cache=False
            )

    # --- A-3. 부분 실패 (4개 중 2개만 성공) ---

    def test_partial_failure_continues_with_remaining(self):
        """A-3. yfinance 부분 실패 (4개 중 2개만 성공) → 나머지 2개로 최적화"""
        # Given: AAPL, MSFT 성공 / FAKE1, FAKE2 실패
        provider = _make_mock_provider({
            "AAPL": _make_price_series(252, seed=1),
            "MSFT": _make_price_series(252, seed=2),
            "FAKE1": None,
            "FAKE2": None,
        })
        set_data_provider(provider)

        # When
        result = fetch_prices_resilient(
            tickers=["AAPL", "MSFT", "FAKE1", "FAKE2"],
            period="3y",
            min_tickers=2,
            use_cache=False
        )

        # Then
        assert isinstance(result, FetchResult)
        assert set(result.successful_tickers) == {"AAPL", "MSFT"}
        assert set(result.failed_tickers) == {"FAKE1", "FAKE2"}
        assert len(result.data.columns) == 2
        assert len(result.warnings) >= 2  # 실패한 2개에 대한 경고


# ============================================================
# B. 수치 안정성
# ============================================================

class TestNumericalStability:
    """공분산 행렬 이상, 데이터 부족 등 수치 안정성 테스트"""

    # --- B-4. 완전 상관(correlation=1.0) 종목 ---

    def test_perfect_correlation_regularized(self):
        """B-4. 완전 상관(rho=1.0) 종목 → 정칙화 후 정상 결과"""
        mu = np.array([0.10, 0.15, 0.12])

        # 거의 완전 상관 (rho ≈ 0.9999)
        # sigma1=0.2, sigma2=0.3, cov12 = 0.9999 * 0.2 * 0.3
        cov = np.array([
            [0.04, 0.05999, 0.01],
            [0.05999, 0.09, 0.015],
            [0.01, 0.015, 0.0625]
        ])

        # 검증: 문제 있는 행렬임을 확인
        validation = validate_covariance_matrix(cov)
        assert not validation.is_valid
        assert validation.max_correlation > 0.999

        # 정칙화 후 최적화 성공
        result = optimize_min_variance(mu, cov, auto_regularize=True)

        assert np.isclose(np.sum(result.weights), 1.0, atol=1e-6)
        assert np.all(result.weights >= -1e-6)
        assert result.volatility > 0

    # --- B-5. 데이터 부족 (5일치만) ---

    def test_insufficient_data_still_returns_result(self):
        """B-5. 데이터 부족 (5일치만) → 경고 + 결과 반환"""
        # 5일치 수익률로 3자산 공분산 계산
        np.random.seed(42)
        returns = np.random.randn(5, 3) * 0.01

        mu = np.mean(returns, axis=0)
        cov = np.cov(returns.T)

        # 데이터가 적어도 최적화는 수행 가능
        # (공분산이 양정치인 경우)
        validation = validate_covariance_matrix(cov)

        if validation.is_valid:
            result = optimize_min_variance(mu, cov)
            assert np.isclose(np.sum(result.weights), 1.0, atol=1e-6)
        else:
            # 데이터 부족으로 문제 있는 공분산 → 정칙화 후 성공
            result = optimize_min_variance(mu, cov, auto_regularize=True)
            assert np.isclose(np.sum(result.weights), 1.0, atol=1e-6)

    # --- B-6. 음수 가중치 방지 ---

    def test_no_negative_weights(self):
        """B-6. 음수 가중치 방지 → bounds=(0,1) 확인"""
        # 음수 가중치가 나올 수 있는 시나리오:
        # 높은 상관관계 + 큰 수익률 차이
        mu = np.array([0.05, 0.25, 0.10])  # 큰 수익률 차이
        cov = np.array([
            [0.04, 0.035, 0.015],
            [0.035, 0.09, 0.025],
            [0.015, 0.025, 0.0625]
        ])

        # min_variance
        result_mv = optimize_min_variance(mu, cov)
        assert np.all(result_mv.weights >= -1e-6), \
            f"음수 가중치 발견: {result_mv.weights}"

        # max_sharpe
        result_ms = optimize_max_sharpe(mu, cov, rf=0.02)
        assert np.all(result_ms.weights >= -1e-6), \
            f"음수 가중치 발견: {result_ms.weights}"

        # 가중치 합 = 1
        assert np.isclose(np.sum(result_mv.weights), 1.0, atol=1e-6)
        assert np.isclose(np.sum(result_ms.weights), 1.0, atol=1e-6)
