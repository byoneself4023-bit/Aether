"""데이터 제공자 테스트 (DBG-1 / ADR 0026 retry+fallback 포함)"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from typing import Protocol, runtime_checkable

from app.services.data_provider import (
    DataProvider,
    YFinanceProvider,
    FixtureProvider,
    CompositeProvider,
    RateLimitError,
    NetworkError,
    DataProviderError,
    MAX_RETRY,
    BACKOFF_BASE,
    _classify_yfinance_error,
    _retry_with_backoff,
    get_data_provider,
    set_data_provider,
    reset_data_provider,
)


class TestDataProviderProtocol:
    """DataProvider Protocol 테스트"""

    def test_yfinance_provider_is_data_provider(self):
        """YFinanceProvider가 DataProvider Protocol을 만족하는지"""
        provider = YFinanceProvider()

        # runtime_checkable Protocol 테스트
        assert isinstance(provider, DataProvider)

    def test_protocol_methods_exist(self):
        """Protocol 메서드들이 존재하는지"""
        provider = YFinanceProvider()

        assert hasattr(provider, "fetch_prices")
        assert hasattr(provider, "fetch_returns")
        assert hasattr(provider, "validate_ticker")
        assert callable(provider.fetch_prices)
        assert callable(provider.fetch_returns)
        assert callable(provider.validate_ticker)


class TestYFinanceProvider:
    """YFinanceProvider 테스트"""

    @patch("app.services.data_provider.yf.download")
    def test_fetch_prices_multi_ticker(self, mock_download):
        """멀티 티커 가격 수집"""
        # Mock 설정 - yfinance가 반환하는 DataFrame 형태
        dates = pd.date_range("2022-01-01", periods=10, freq="B")
        close_data = pd.DataFrame({
            "AAPL": np.random.randn(10) * 10 + 150,
            "GOOGL": np.random.randn(10) * 20 + 2800
        }, index=dates)

        # yfinance multi-ticker 응답 시뮬레이션
        # yf.download은 {"Close": DataFrame} 형태로 반환
        class MockYfData:
            def __getitem__(self, key):
                if key == "Close":
                    return close_data
                raise KeyError(key)

        mock_download.return_value = MockYfData()

        provider = YFinanceProvider()
        result = provider.fetch_prices(["AAPL", "GOOGL"], "1y")

        mock_download.assert_called_once()
        assert len(result) > 0

    @patch("app.services.data_provider.yf.download")
    def test_fetch_prices_single_ticker(self, mock_download):
        """단일 티커 가격 수집"""
        dates = pd.date_range("2022-01-01", periods=10, freq="B")
        mock_data = pd.DataFrame({
            "Close": np.random.randn(10) * 10 + 150
        }, index=dates)
        mock_download.return_value = mock_data

        provider = YFinanceProvider()
        result = provider.fetch_prices(["AAPL"], "1y")

        assert "AAPL" in result.columns

    @patch("app.services.data_provider.yf.download")
    def test_fetch_returns(self, mock_download):
        """수익률 수집"""
        dates = pd.date_range("2022-01-01", periods=11, freq="B")
        close_data = pd.DataFrame({
            "AAPL": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        }, index=dates)

        mock_data = pd.DataFrame({"Close": close_data["AAPL"]}, index=dates)
        mock_download.return_value = mock_data

        provider = YFinanceProvider()
        result = provider.fetch_returns(["AAPL"], "1y")

        # 수익률은 가격보다 1개 적음 (pct_change 후 dropna)
        assert len(result) == 10

    @patch("app.services.data_provider.yf.Ticker")
    def test_validate_ticker_valid(self, mock_ticker):
        """유효한 티커 검증"""
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame({"Close": [1, 2, 3]})
        mock_ticker.return_value = mock_instance

        provider = YFinanceProvider()
        result = provider.validate_ticker("AAPL")

        assert result is True

    @patch("app.services.data_provider.yf.Ticker")
    def test_validate_ticker_invalid(self, mock_ticker):
        """무효한 티커 검증"""
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()  # 빈 결과
        mock_ticker.return_value = mock_instance

        provider = YFinanceProvider()
        result = provider.validate_ticker("INVALID_TICKER")

        assert result is False

    @patch("app.services.data_provider.time.sleep")
    @patch("app.services.data_provider.yf.Ticker")
    def test_validate_ticker_transient_raises(self, mock_ticker, _mock_sleep):
        """transient(rate limit/network)는 retry 소진 후 raise — invalid로 위장 금지 (⑥)."""
        mock_ticker.side_effect = Exception("Too Many Requests 429")

        provider = YFinanceProvider()
        with pytest.raises(RateLimitError):
            provider.validate_ticker("AAPL")

    @patch("app.services.data_provider.yf.Ticker")
    def test_validate_ticker_permanent_returns_false(self, mock_ticker):
        """비-transient(영구) 오류는 invalid로 간주 → False."""
        mock_ticker.side_effect = Exception("delisted symbol")

        provider = YFinanceProvider()
        result = provider.validate_ticker("AAPL")

        assert result is False


class TestGetDataProvider:
    """get_data_provider 팩토리 테스트"""

    def setup_method(self):
        """테스트 전 provider 초기화"""
        reset_data_provider()

    def teardown_method(self):
        """테스트 후 provider 초기화"""
        reset_data_provider()

    def test_returns_composite_provider_by_default(self):
        """DBG-1 / ADR 0026: 기본값 = CompositeProvider(YFinance, Fixture)."""
        provider = get_data_provider()

        assert isinstance(provider, CompositeProvider)

    def test_singleton_pattern(self):
        """싱글톤 패턴 - 동일 인스턴스 반환"""
        provider1 = get_data_provider()
        provider2 = get_data_provider()

        assert provider1 is provider2


class TestSetDataProvider:
    """set_data_provider 테스트 (Mock 주입)"""

    def setup_method(self):
        reset_data_provider()

    def teardown_method(self):
        reset_data_provider()

    def test_set_mock_provider(self):
        """Mock provider 주입"""
        # Mock provider 생성
        mock_provider = MagicMock(spec=DataProvider)
        mock_provider.fetch_prices.return_value = pd.DataFrame({"AAPL": [100, 101]})

        # 주입
        set_data_provider(mock_provider)

        # 확인
        provider = get_data_provider()
        assert provider is mock_provider

    def test_mock_provider_used_in_fetch(self):
        """주입된 Mock provider가 실제로 사용되는지"""
        mock_provider = MagicMock(spec=DataProvider)
        expected_df = pd.DataFrame({"AAPL": [100, 101, 102]})
        mock_provider.fetch_prices.return_value = expected_df

        set_data_provider(mock_provider)
        provider = get_data_provider()

        result = provider.fetch_prices(["AAPL"], "1y")

        mock_provider.fetch_prices.assert_called_once_with(["AAPL"], "1y")
        pd.testing.assert_frame_equal(result, expected_df)


class TestCustomProvider:
    """커스텀 Provider 구현 테스트"""

    def setup_method(self):
        reset_data_provider()

    def teardown_method(self):
        reset_data_provider()

    def test_custom_provider_implementation(self):
        """커스텀 Provider 구현 및 사용"""

        class MockDataProvider:
            """테스트용 Mock Provider"""

            def fetch_prices(self, tickers, period="3y"):
                dates = pd.date_range("2022-01-01", periods=10, freq="B")
                data = {ticker: np.ones(10) * 100 for ticker in tickers}
                return pd.DataFrame(data, index=dates)

            def fetch_returns(self, tickers, period="3y"):
                prices = self.fetch_prices(tickers, period)
                return prices.pct_change().dropna()

            def validate_ticker(self, ticker):
                return ticker.isupper() and len(ticker) <= 5

        custom_provider = MockDataProvider()
        set_data_provider(custom_provider)

        provider = get_data_provider()
        result = provider.fetch_prices(["AAPL", "GOOGL"], "1y")

        assert len(result) == 10
        assert "AAPL" in result.columns
        assert "GOOGL" in result.columns
        assert (result["AAPL"] == 100).all()


class TestProviderIntegration:
    """Provider 통합 테스트"""

    def setup_method(self):
        reset_data_provider()

    def teardown_method(self):
        reset_data_provider()

    @patch("app.services.data_provider.yf.download")
    def test_fetch_single_ticker_prices(self, mock_download):
        """fetch_single_ticker_prices 메서드 테스트"""
        dates = pd.date_range("2022-01-01", periods=10, freq="B")
        mock_data = pd.DataFrame({
            "Close": np.random.randn(10) * 10 + 150
        }, index=dates)
        mock_download.return_value = mock_data

        provider = YFinanceProvider()
        result = provider.fetch_single_ticker_prices("AAPL", "1y")

        assert result is not None
        assert len(result) == 10

    @patch("app.services.data_provider.yf.download")
    def test_fetch_single_ticker_prices_empty(self, mock_download):
        """빈 결과 시 None 반환"""
        mock_download.return_value = pd.DataFrame()

        provider = YFinanceProvider()
        result = provider.fetch_single_ticker_prices("INVALID", "1y")

        assert result is None

    def test_period_mapping(self):
        """기간 매핑 확인"""
        provider = YFinanceProvider()

        assert provider.PERIOD_MAPPING["1y"] == "1y"
        assert provider.PERIOD_MAPPING["3y"] == "3y"
        assert provider.PERIOD_MAPPING["5y"] == "5y"
        assert provider.PERIOD_MAPPING["10y"] == "10y"


class TestClassifyYfinanceError:
    """_classify_yfinance_error — transient vs 영구 분류 (DBG-1)."""

    def test_rate_limit_message(self):
        assert _classify_yfinance_error(Exception("Too Many Requests 429")) is RateLimitError
        assert _classify_yfinance_error(Exception("Rate limit hit")) is RateLimitError

    def test_network_message(self):
        assert _classify_yfinance_error(Exception("Connection timeout")) is NetworkError
        assert _classify_yfinance_error(Exception("Network error")) is NetworkError

    def test_permanent_returns_none(self):
        """영구 영역 (영역 ValueError 등) = None → retry 영역."""
        assert _classify_yfinance_error(ValueError("Invalid ticker")) is None
        assert _classify_yfinance_error(KeyError("Close")) is None


class TestRetryWithBackoff:
    """_retry_with_backoff — exponential backoff 검증 (DBG-1 / ADR 0026)."""

    def test_first_attempt_success_no_sleep(self):
        """1회차 성공 → time.sleep 미호출."""
        call_count = {"n": 0}

        def fn():
            call_count["n"] += 1
            return "ok"

        with patch("app.services.data_provider.time.sleep") as mock_sleep:
            result = _retry_with_backoff(fn)

        assert result == "ok"
        assert call_count["n"] == 1
        mock_sleep.assert_not_called()

    def test_retry_3_then_success(self):
        """2번 transient 실패 후 3회차 성공 — sleep 2회 호출 (1s, 2s)."""
        attempts = {"n": 0}

        def fn():
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise Exception("Rate limit exceeded")
            return "ok"

        with patch("app.services.data_provider.time.sleep") as mock_sleep:
            result = _retry_with_backoff(fn)

        assert result == "ok"
        assert attempts["n"] == 3
        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0][0][0] == BACKOFF_BASE  # 1s
        assert mock_sleep.call_args_list[1][0][0] == BACKOFF_BASE * 2  # 2s

    def test_retry_exhausted_raises_rate_limit(self):
        """3회 모두 실패 → RateLimitError raise + sleep 2회 (1s, 2s)."""

        def fn():
            raise Exception("429 Too Many Requests")

        with patch("app.services.data_provider.time.sleep") as mock_sleep:
            with pytest.raises(RateLimitError):
                _retry_with_backoff(fn)

        assert mock_sleep.call_count == MAX_RETRY - 1

    def test_permanent_error_raises_immediately(self):
        """영구 영역 (transient X) → 즉시 raise + sleep 미호출."""
        def fn():
            raise ValueError("Invalid input")

        with patch("app.services.data_provider.time.sleep") as mock_sleep:
            with pytest.raises(ValueError):
                _retry_with_backoff(fn)

        mock_sleep.assert_not_called()


class TestFixtureProvider:
    """FixtureProvider — yfinance 영구 차단 시 fallback (DBG-1 / ADR 0026)."""

    def test_fetch_prices_supported_tickers(self):
        provider = FixtureProvider()
        result = provider.fetch_prices(["AAPL", "MSFT", "GOOGL"], "1y")

        assert len(result) == 252
        assert list(result.columns) == ["AAPL", "MSFT", "GOOGL"]
        # AAPL 시작 = 150.0 (deterministic seed)
        assert result["AAPL"].iloc[0] == pytest.approx(150.0, rel=1e-6)
        # MSFT 시작 = 350.0
        assert result["MSFT"].iloc[0] == pytest.approx(350.0, rel=1e-6)

    def test_fetch_prices_subset_ticker(self):
        """단일 ticker 추출 영역 영역 영역."""
        provider = FixtureProvider()
        result = provider.fetch_prices(["AAPL"], "1y")

        assert list(result.columns) == ["AAPL"]
        assert len(result) == 252

    def test_fetch_prices_unsupported_ticker_raises(self):
        provider = FixtureProvider()
        with pytest.raises(ValueError, match="미지원 ticker"):
            provider.fetch_prices(["AAPL", "TSLA"], "1y")

    def test_fetch_returns_pct_change(self):
        provider = FixtureProvider()
        result = provider.fetch_returns(["AAPL"], "1y")

        # pct_change + dropna → 251 rows
        assert len(result) == 251
        # 첫 수익률 = (147.1932 - 150.0) / 150.0 ≈ -0.0187
        assert result["AAPL"].iloc[0] == pytest.approx(-0.018712, abs=1e-4)

    def test_validate_ticker(self):
        provider = FixtureProvider()
        assert provider.validate_ticker("AAPL") is True
        assert provider.validate_ticker("MSFT") is True
        assert provider.validate_ticker("TSLA") is False

    def test_fetch_single_ticker_prices_supported(self):
        provider = FixtureProvider()
        series = provider.fetch_single_ticker_prices("GOOGL", "1y")

        assert series is not None
        assert len(series) == 252

    def test_fetch_single_ticker_prices_unsupported(self):
        provider = FixtureProvider()
        assert provider.fetch_single_ticker_prices("FOO", "1y") is None

    def test_date_range_filter(self):
        """start_date / end_date 필터 영역 영역."""
        provider = FixtureProvider()
        full = provider.fetch_prices(["AAPL"], "1y")
        all_dates = full.index

        mid = all_dates[len(all_dates) // 2]
        result = provider.fetch_prices(["AAPL"], "1y", start_date=str(mid.date()))

        assert len(result) <= len(full)
        assert result.index[0] >= mid


class TestCompositeProvider:
    """CompositeProvider — primary 정상 / transient → fallback / 영구 → re-raise (DBG-1)."""

    def test_primary_success_no_fallback(self):
        primary = MagicMock(spec=DataProvider)
        primary.fetch_prices.return_value = pd.DataFrame({"AAPL": [1, 2, 3]})
        fallback = MagicMock(spec=DataProvider)

        composite = CompositeProvider(primary=primary, fallback=fallback)
        result = composite.fetch_prices(["AAPL"], "1y")

        assert list(result.columns) == ["AAPL"]
        primary.fetch_prices.assert_called_once()
        fallback.fetch_prices.assert_not_called()

    def test_primary_rate_limit_falls_back(self):
        primary = MagicMock(spec=DataProvider)
        primary.fetch_prices.side_effect = RateLimitError("429")
        fallback = MagicMock(spec=DataProvider)
        fallback.fetch_prices.return_value = pd.DataFrame({"AAPL": [10, 20]})

        composite = CompositeProvider(primary=primary, fallback=fallback)
        result = composite.fetch_prices(["AAPL"], "1y")

        primary.fetch_prices.assert_called_once()
        fallback.fetch_prices.assert_called_once()
        assert result["AAPL"].tolist() == [10, 20]

    def test_primary_network_error_falls_back(self):
        primary = MagicMock(spec=DataProvider)
        primary.fetch_returns.side_effect = NetworkError("connection lost")
        fallback = MagicMock(spec=DataProvider)
        fallback.fetch_returns.return_value = pd.DataFrame({"AAPL": [0.01]})

        composite = CompositeProvider(primary=primary, fallback=fallback)
        result = composite.fetch_returns(["AAPL"], "1y")

        primary.fetch_returns.assert_called_once()
        fallback.fetch_returns.assert_called_once()
        assert result["AAPL"].iloc[0] == 0.01

    def test_primary_permanent_error_no_fallback(self):
        """영구 (ValueError 등) → fallback 미호출 / re-raise."""
        primary = MagicMock(spec=DataProvider)
        primary.fetch_prices.side_effect = ValueError("Invalid ticker")
        fallback = MagicMock(spec=DataProvider)

        composite = CompositeProvider(primary=primary, fallback=fallback)
        with pytest.raises(ValueError):
            composite.fetch_prices(["AAPL"], "1y")

        fallback.fetch_prices.assert_not_called()

    def test_validate_ticker_primary_success(self):
        primary = MagicMock(spec=DataProvider)
        primary.validate_ticker.return_value = True
        fallback = MagicMock(spec=DataProvider)

        composite = CompositeProvider(primary=primary, fallback=fallback)
        assert composite.validate_ticker("AAPL") is True
        fallback.validate_ticker.assert_not_called()

    def test_validate_ticker_falls_back_on_transient(self):
        primary = MagicMock(spec=DataProvider)
        primary.validate_ticker.side_effect = RateLimitError("429")
        fallback = MagicMock(spec=DataProvider)
        fallback.validate_ticker.return_value = True

        composite = CompositeProvider(primary=primary, fallback=fallback)
        assert composite.validate_ticker("AAPL") is True
        fallback.validate_ticker.assert_called_once_with("AAPL")


class TestYFinanceProviderRetry:
    """YFinanceProvider — retry 통합 검증 (DBG-1)."""

    @patch("app.services.data_provider.time.sleep")
    @patch("app.services.data_provider.yf.download")
    def test_fetch_prices_retries_on_rate_limit_then_succeeds(self, mock_download, mock_sleep):
        """transient → 2회 실패 후 3회차 성공."""
        dates = pd.date_range("2022-01-01", periods=5, freq="B")
        good_data = pd.DataFrame({"Close": [100.0, 101.0, 102.0, 103.0, 104.0]}, index=dates)

        mock_download.side_effect = [
            Exception("Rate limit exceeded"),
            Exception("Too Many Requests"),
            good_data,
        ]

        provider = YFinanceProvider()
        result = provider.fetch_prices(["AAPL"], "1y")

        assert mock_download.call_count == 3
        assert mock_sleep.call_count == 2
        assert len(result) > 0

    @patch("app.services.data_provider.time.sleep")
    @patch("app.services.data_provider.yf.download")
    def test_fetch_prices_raises_rate_limit_after_max_retry(self, mock_download, mock_sleep):
        """3회 모두 transient → RateLimitError raise."""
        mock_download.side_effect = Exception("429 Rate limit")

        provider = YFinanceProvider()
        with pytest.raises(RateLimitError):
            provider.fetch_prices(["AAPL"], "1y")

        assert mock_download.call_count == MAX_RETRY
        assert mock_sleep.call_count == MAX_RETRY - 1

    @patch("app.services.data_provider.time.sleep")
    @patch("app.services.data_provider.yf.download")
    def test_fetch_single_ticker_returns_none_on_transient_exhausted(self, mock_download, mock_sleep):
        """fetch_single_ticker_prices: transient retry 소진 시 None 반환 (호출자 영역 영역 영역)."""
        mock_download.side_effect = Exception("connection timeout")

        provider = YFinanceProvider()
        result = provider.fetch_single_ticker_prices("AAPL", "1y")

        assert result is None
        assert mock_download.call_count == MAX_RETRY
