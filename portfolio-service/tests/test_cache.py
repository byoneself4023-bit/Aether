"""캐시 서비스 단위 테스트"""

import time
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.services.cache import (
    InMemoryCache,
    MarketDataCache,
    CacheEntry,
    get_cache,
    reset_cache,
)
from app.services.data import (
    FetchResult,
    ReturnsResult,
    fetch_prices_resilient,
    fetch_returns_resilient,
    get_returns_and_covariance_resilient,
)


class TestInMemoryCache:
    """InMemoryCache 테스트"""

    def test_set_and_get(self):
        """값 저장 및 조회"""
        cache = InMemoryCache()
        cache.set("key1", {"data": "value"}, ttl=60)

        result = cache.get("key1")
        assert result == {"data": "value"}

    def test_get_nonexistent_key(self):
        """존재하지 않는 키 조회"""
        cache = InMemoryCache()

        result = cache.get("nonexistent")
        assert result is None

    def test_ttl_expiration(self):
        """TTL 만료 테스트"""
        cache = InMemoryCache()
        cache.set("key1", "value", ttl=1)  # 1초 TTL

        # 즉시 조회 - 성공
        assert cache.get("key1") == "value"

        # 2초 후 조회 - 만료
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_delete(self):
        """값 삭제"""
        cache = InMemoryCache()
        cache.set("key1", "value", ttl=60)

        cache.delete("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        """전체 삭제"""
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)

        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size == 0

    def test_max_size_eviction(self):
        """최대 크기 초과 시 오래된 항목 삭제"""
        cache = InMemoryCache(max_size=3)

        cache.set("key1", "value1", ttl=60)
        time.sleep(0.01)
        cache.set("key2", "value2", ttl=60)
        time.sleep(0.01)
        cache.set("key3", "value3", ttl=60)
        time.sleep(0.01)

        # 4번째 항목 추가 시 가장 오래된 key1 삭제
        cache.set("key4", "value4", ttl=60)

        assert cache.size == 3
        assert cache.get("key1") is None  # 삭제됨
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_size_property(self):
        """캐시 크기 확인"""
        cache = InMemoryCache()

        assert cache.size == 0

        cache.set("key1", "value1", ttl=60)
        assert cache.size == 1

        cache.set("key2", "value2", ttl=60)
        assert cache.size == 2


class TestMarketDataCache:
    """MarketDataCache 테스트"""

    @pytest.fixture
    def cache(self):
        """테스트용 캐시 인스턴스"""
        return MarketDataCache(InMemoryCache())

    @pytest.fixture
    def sample_prices_df(self):
        """테스트용 가격 DataFrame"""
        dates = pd.date_range("2023-01-01", periods=10, freq="D")
        data = {
            "AAPL": np.random.uniform(150, 160, 10),
            "MSFT": np.random.uniform(300, 310, 10),
        }
        return pd.DataFrame(data, index=dates)

    @pytest.fixture
    def sample_returns_df(self):
        """테스트용 수익률 DataFrame"""
        dates = pd.date_range("2023-01-01", periods=10, freq="D")
        data = {
            "AAPL": np.random.uniform(-0.02, 0.02, 10),
            "MSFT": np.random.uniform(-0.02, 0.02, 10),
        }
        return pd.DataFrame(data, index=dates)

    def test_prices_cache_miss(self, cache):
        """가격 캐시 미스"""
        result = cache.get_prices(["AAPL", "MSFT"], "3y")
        assert result is None
        assert cache.stats["misses"] == 1

    def test_prices_cache_hit(self, cache, sample_prices_df):
        """가격 캐시 히트"""
        tickers = ["AAPL", "MSFT"]
        period = "3y"

        # 캐시 저장
        cache.set_prices(tickers, period, sample_prices_df)

        # 캐시 조회
        result = cache.get_prices(tickers, period)

        assert result is not None
        assert list(result.columns) == list(sample_prices_df.columns)
        assert len(result) == len(sample_prices_df)
        assert cache.stats["hits"] == 1

    def test_returns_cache(self, cache, sample_returns_df):
        """수익률 캐시 저장 및 조회"""
        tickers = ["AAPL", "MSFT"]
        period = "3y"

        cache.set_returns(tickers, period, sample_returns_df)
        result = cache.get_returns(tickers, period)

        assert result is not None
        assert len(result) == len(sample_returns_df)

    def test_ticker_validation_cache(self, cache):
        """티커 검증 캐시"""
        cache.set_ticker_validation("AAPL", True)
        cache.set_ticker_validation("INVALID", False)

        assert cache.get_ticker_validation("AAPL") is True
        assert cache.get_ticker_validation("INVALID") is False
        assert cache.get_ticker_validation("UNKNOWN") is None

    def test_cache_key_generation(self, cache, sample_prices_df):
        """캐시 키 생성 - 티커 순서 무관"""
        period = "3y"

        # 다른 순서로 저장
        cache.set_prices(["AAPL", "MSFT"], period, sample_prices_df)

        # 다른 순서로 조회해도 동일 결과
        result = cache.get_prices(["MSFT", "AAPL"], period)
        assert result is not None

    def test_invalidate(self, cache, sample_prices_df):
        """캐시 무효화"""
        tickers = ["AAPL", "MSFT"]
        period = "3y"

        cache.set_prices(tickers, period, sample_prices_df)
        assert cache.get_prices(tickers, period) is not None

        cache.invalidate(tickers, period)
        assert cache.get_prices(tickers, period) is None

    def test_stats(self, cache, sample_prices_df):
        """캐시 통계"""
        tickers = ["AAPL", "MSFT"]
        period = "3y"

        # 미스
        cache.get_prices(tickers, period)
        cache.get_prices(tickers, period)

        # 저장
        cache.set_prices(tickers, period, sample_prices_df)

        # 히트
        cache.get_prices(tickers, period)
        cache.get_prices(tickers, period)
        cache.get_prices(tickers, period)

        stats = cache.stats
        assert stats["misses"] == 2
        assert stats["hits"] == 3
        assert stats["hit_rate"] == 0.6
        assert stats["total_requests"] == 5

    def test_clear_resets_stats(self, cache, sample_prices_df):
        """캐시 클리어 시 통계 리셋"""
        cache.set_prices(["AAPL"], "3y", sample_prices_df)
        cache.get_prices(["AAPL"], "3y")

        cache.clear()

        stats = cache.stats
        assert stats["hits"] == 0
        assert stats["misses"] == 0


class TestCacheKeyGeneration:
    """캐시 키 생성 테스트"""

    def test_same_tickers_different_order(self):
        """동일 티커, 다른 순서 → 동일 키"""
        key1 = MarketDataCache._generate_key("prices", ["AAPL", "MSFT"], "3y")
        key2 = MarketDataCache._generate_key("prices", ["MSFT", "AAPL"], "3y")
        assert key1 == key2

    def test_different_period(self):
        """동일 티커, 다른 기간 → 다른 키"""
        key1 = MarketDataCache._generate_key("prices", ["AAPL"], "3y")
        key2 = MarketDataCache._generate_key("prices", ["AAPL"], "5y")
        assert key1 != key2

    def test_different_prefix(self):
        """다른 prefix → 다른 키"""
        key1 = MarketDataCache._generate_key("prices", ["AAPL"], "3y")
        key2 = MarketDataCache._generate_key("returns", ["AAPL"], "3y")
        assert key1 != key2


class TestGlobalCacheInstance:
    """전역 캐시 인스턴스 테스트"""

    def setup_method(self):
        """각 테스트 전 캐시 리셋"""
        reset_cache()

    def teardown_method(self):
        """각 테스트 후 캐시 리셋"""
        reset_cache()

    def test_get_cache_returns_singleton(self):
        """get_cache()가 싱글톤 반환"""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2

    def test_reset_cache(self):
        """캐시 리셋"""
        cache1 = get_cache()
        reset_cache()
        cache2 = get_cache()

        # 리셋 후에는 다른 인스턴스
        assert cache1 is not cache2


class TestDataFrameSerialization:
    """DataFrame 직렬화/역직렬화 테스트"""

    @pytest.fixture
    def cache(self):
        return MarketDataCache(InMemoryCache())

    def test_datetime_index_preserved(self, cache):
        """DateTime 인덱스 보존"""
        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        df = pd.DataFrame({"AAPL": [1, 2, 3, 4, 5]}, index=dates)

        cache.set_prices(["AAPL"], "3y", df)
        result = cache.get_prices(["AAPL"], "3y")

        assert isinstance(result.index, pd.DatetimeIndex)
        assert len(result.index) == 5

    def test_float_values_preserved(self, cache):
        """float 값 정밀도 보존"""
        dates = pd.date_range("2023-01-01", periods=3, freq="D")
        df = pd.DataFrame({
            "AAPL": [150.123456, 151.234567, 152.345678]
        }, index=dates)

        cache.set_prices(["AAPL"], "3y", df)
        result = cache.get_prices(["AAPL"], "3y")

        np.testing.assert_array_almost_equal(
            result["AAPL"].values,
            df["AAPL"].values,
            decimal=5
        )

    def test_multiple_columns_preserved(self, cache):
        """여러 컬럼 보존"""
        dates = pd.date_range("2023-01-01", periods=3, freq="D")
        df = pd.DataFrame({
            "AAPL": [150, 151, 152],
            "MSFT": [300, 301, 302],
            "GOOGL": [100, 101, 102],
        }, index=dates)

        cache.set_prices(["AAPL", "MSFT", "GOOGL"], "3y", df)
        result = cache.get_prices(["AAPL", "MSFT", "GOOGL"], "3y")

        assert list(result.columns) == list(df.columns)


# ============================================================
# Resilient Fetch Tests
# ============================================================

class TestFetchPricesResilient:
    """fetch_prices_resilient 테스트"""

    def setup_method(self):
        """각 테스트 전 캐시 리셋"""
        reset_cache()

    def teardown_method(self):
        """각 테스트 후 캐시 리셋"""
        reset_cache()

    @patch("app.services.data.yf.download")
    def test_all_tickers_succeed(self, mock_download):
        """모든 티커 성공"""
        # Mock 설정
        dates = pd.date_range("2023-01-01", periods=10, freq="D")
        mock_download.side_effect = [
            pd.DataFrame({"Close": range(100, 110)}, index=dates),
            pd.DataFrame({"Close": range(200, 210)}, index=dates),
        ]

        result = fetch_prices_resilient(
            ["AAPL", "MSFT"],
            period="1y",
            use_cache=False
        )

        assert isinstance(result, FetchResult)
        assert len(result.successful_tickers) == 2
        assert len(result.failed_tickers) == 0
        assert len(result.warnings) == 0
        assert "AAPL" in result.successful_tickers
        assert "MSFT" in result.successful_tickers

    @patch("app.services.data.yf.download")
    def test_partial_failure(self, mock_download):
        """부분 실패 (일부 티커만 성공)"""
        dates = pd.date_range("2023-01-01", periods=10, freq="D")

        def mock_side_effect(tickers, **kwargs):
            if tickers == "FAKE":
                return pd.DataFrame()  # 빈 DataFrame
            return pd.DataFrame({"Close": range(100, 110)}, index=dates)

        mock_download.side_effect = mock_side_effect

        result = fetch_prices_resilient(
            ["AAPL", "FAKE", "MSFT"],
            period="1y",
            min_tickers=2,
            use_cache=False
        )

        assert len(result.successful_tickers) == 2
        assert len(result.failed_tickers) == 1
        assert "FAKE" in result.failed_tickers
        assert len(result.warnings) >= 1

    @patch("app.services.data.yf.download")
    def test_insufficient_tickers_raises_error(self, mock_download):
        """최소 티커 수 미달 시 에러"""
        dates = pd.date_range("2023-01-01", periods=10, freq="D")

        def mock_side_effect(tickers, **kwargs):
            if tickers == "AAPL":
                return pd.DataFrame({"Close": range(100, 110)}, index=dates)
            return pd.DataFrame()  # 나머지는 실패

        mock_download.side_effect = mock_side_effect

        with pytest.raises(ValueError, match="Insufficient valid tickers"):
            fetch_prices_resilient(
                ["AAPL", "FAKE1", "FAKE2"],
                period="1y",
                min_tickers=2,
                use_cache=False
            )

    @patch("app.services.data.yf.download")
    def test_exception_handling(self, mock_download):
        """예외 발생 티커 처리"""
        dates = pd.date_range("2023-01-01", periods=10, freq="D")

        def mock_side_effect(tickers, **kwargs):
            if tickers == "ERROR":
                raise ConnectionError("Network error")
            return pd.DataFrame({"Close": range(100, 110)}, index=dates)

        mock_download.side_effect = mock_side_effect

        result = fetch_prices_resilient(
            ["AAPL", "ERROR", "MSFT"],
            period="1y",
            min_tickers=2,
            use_cache=False
        )

        assert len(result.successful_tickers) == 2
        assert "ERROR" in result.failed_tickers
        # Provider 패턴 사용으로 경고 메시지 형식 변경
        # 예외가 provider 내부에서 처리되어 "No data returned" 또는 원래 에러 메시지 포함
        assert any("ERROR" in w for w in result.warnings)


class TestFetchReturnsResilient:
    """fetch_returns_resilient 테스트"""

    def setup_method(self):
        reset_cache()

    def teardown_method(self):
        reset_cache()

    @patch("app.services.data.yf.download")
    def test_returns_calculation(self, mock_download):
        """수익률 계산 검증"""
        dates = pd.date_range("2023-01-01", periods=10, freq="D")

        mock_download.side_effect = [
            pd.DataFrame({"Close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]}, index=dates),
            pd.DataFrame({"Close": [200, 202, 204, 206, 208, 210, 212, 214, 216, 218]}, index=dates),
        ]

        result = fetch_returns_resilient(
            ["AAPL", "MSFT"],
            period="1y",
            use_cache=False
        )

        assert isinstance(result, FetchResult)
        # 수익률은 prices보다 1행 적음
        assert len(result.data) == 9
        assert len(result.successful_tickers) == 2


class TestGetReturnsAndCovarianceResilient:
    """get_returns_and_covariance_resilient 테스트"""

    def setup_method(self):
        reset_cache()

    def teardown_method(self):
        reset_cache()

    @patch("app.services.data.yf.download")
    def test_returns_covariance_result(self, mock_download):
        """수익률 + 공분산 결과 검증"""
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=100, freq="D")

        mock_download.side_effect = [
            pd.DataFrame({"Close": 100 + np.cumsum(np.random.randn(100) * 0.5)}, index=dates),
            pd.DataFrame({"Close": 200 + np.cumsum(np.random.randn(100) * 0.8)}, index=dates),
        ]

        result = get_returns_and_covariance_resilient(
            ["AAPL", "MSFT"],
            period="1y",
            use_shrinkage=True,
            min_tickers=2
        )

        assert isinstance(result, ReturnsResult)
        assert result.mu.shape == (2,)
        assert result.cov.shape == (2, 2)
        assert len(result.successful_tickers) == 2
        assert len(result.failed_tickers) == 0

    @patch("app.services.data.yf.download")
    def test_partial_success_with_covariance(self, mock_download):
        """부분 성공 시 공분산 계산"""
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=100, freq="D")

        def mock_side_effect(tickers, **kwargs):
            if tickers == "FAKE":
                return pd.DataFrame()
            return pd.DataFrame({
                "Close": 100 + np.cumsum(np.random.randn(100) * 0.5)
            }, index=dates)

        mock_download.side_effect = mock_side_effect

        result = get_returns_and_covariance_resilient(
            ["AAPL", "FAKE", "MSFT"],
            period="1y",
            use_shrinkage=True,
            min_tickers=2
        )

        assert len(result.successful_tickers) == 2
        assert "FAKE" in result.failed_tickers
        assert result.mu.shape == (2,)
        assert result.cov.shape == (2, 2)


class TestFetchResultDataclass:
    """FetchResult dataclass 테스트"""

    def test_fetch_result_structure(self):
        """FetchResult 구조 검증"""
        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        df = pd.DataFrame({"AAPL": range(5), "MSFT": range(5)}, index=dates)

        result = FetchResult(
            data=df,
            successful_tickers=["AAPL", "MSFT"],
            failed_tickers=["FAKE"],
            warnings=["FAKE: No data"]
        )

        assert len(result.data) == 5
        assert len(result.successful_tickers) == 2
        assert len(result.failed_tickers) == 1
        assert len(result.warnings) == 1


class TestReturnsResultDataclass:
    """ReturnsResult dataclass 테스트"""

    def test_returns_result_structure(self):
        """ReturnsResult 구조 검증"""
        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        df = pd.DataFrame({"AAPL": range(5), "MSFT": range(5)}, index=dates)
        mu = np.array([0.01, 0.02])
        cov = np.array([[0.04, 0.01], [0.01, 0.09]])

        result = ReturnsResult(
            mu=mu,
            cov=cov,
            returns_df=df,
            successful_tickers=["AAPL", "MSFT"],
            failed_tickers=[],
            warnings=[]
        )

        assert result.mu.shape == (2,)
        assert result.cov.shape == (2, 2)
        assert len(result.returns_df) == 5
