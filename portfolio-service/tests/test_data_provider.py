"""데이터 제공자 테스트"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from typing import Protocol, runtime_checkable

from app.services.data_provider import (
    DataProvider,
    YFinanceProvider,
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

    @patch("app.services.data_provider.yf.Ticker")
    def test_validate_ticker_exception(self, mock_ticker):
        """티커 검증 중 예외 처리"""
        mock_ticker.side_effect = Exception("Network error")

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

    def test_returns_yfinance_provider_by_default(self):
        """기본값으로 YFinanceProvider 반환"""
        provider = get_data_provider()

        assert isinstance(provider, YFinanceProvider)

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
