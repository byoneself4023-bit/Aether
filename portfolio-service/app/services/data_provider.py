"""데이터 제공자 추상화 (Protocol 패턴 + DBG-1 fallback)

DBG-1 / ADR 0026:
- yfinance transient rate limit 회피 — retry + exponential backoff (3회 / 1s / 2s / 4s)
- 영구 차단 시 FixtureProvider fallback (AAPL/MSFT/GOOGL deterministic 1년 데이터)
- CompositeProvider primary + fallback 자동 전환
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

import numpy as np
import pandas as pd
import yfinance as yf

from app.config import get_settings
from app.middleware.logging import logger


# DBG-1 / ADR 0026: retry / backoff 파라미터
MAX_RETRY = 3
BACKOFF_BASE = 1.0  # 초 — 1s, 2s, 4s exponential


class DataProviderError(Exception):
    """데이터 제공자 공통 에러"""


class RateLimitError(DataProviderError):
    """API rate limit 에러 — transient (retry 대상)"""


class NetworkError(DataProviderError):
    """네트워크 에러 — transient (retry 대상)"""


@runtime_checkable
class DataProvider(Protocol):
    """데이터 제공자 프로토콜

    모든 데이터 제공자는 이 프로토콜을 따라야 함.
    테스트 시 mock provider로 교체 가능.
    """

    def fetch_prices(
        self,
        tickers: list[str],
        period: str = "3y",
    ) -> pd.DataFrame:
        """종목 가격 데이터 수집"""
        ...

    def fetch_returns(
        self,
        tickers: list[str],
        period: str = "3y",
    ) -> pd.DataFrame:
        """종목 수익률 데이터 수집"""
        ...

    def validate_ticker(self, ticker: str) -> bool:
        """티커 유효성 검증"""
        ...


def _classify_yfinance_error(exc: Exception) -> Optional[type[DataProviderError]]:
    """yfinance 예외를 transient 분류 — RateLimit / Network 경우만 retry 대상.

    transient 영역 영역 = None 반환 → 영구 영역 (retry 영역 영역).
    """
    msg = str(exc).lower()
    if "rate limit" in msg or "too many requests" in msg or "429" in msg:
        return RateLimitError
    if "timeout" in msg or "connection" in msg or "network" in msg or "temporarily" in msg:
        return NetworkError
    return None


def _retry_with_backoff(func, *args, max_retry: int = MAX_RETRY, backoff_base: float = BACKOFF_BASE, **kwargs):
    """exponential backoff retry — yfinance transient 차단 회피 (DBG-1).

    backoff: 1s → 2s → 4s. 각 시도 후 RateLimitError / NetworkError 영역 영역 retry.
    영구 영역 영역 즉시 raise. 모든 retry 실패 시 마지막 예외 raise.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(max_retry):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            cls = _classify_yfinance_error(exc)
            if cls is None:
                raise
            last_exc = cls(str(exc))
            if attempt >= max_retry - 1:
                break
            sleep_s = backoff_base * (2**attempt)
            logger.warning(
                "yfinance_transient_retry",
                attempt=attempt + 1,
                max_retry=max_retry,
                sleep_s=sleep_s,
                error_type=type(exc).__name__,
                error=str(exc)[:200],
            )
            time.sleep(sleep_s)
    raise last_exc if last_exc is not None else DataProviderError("retry_exhausted")


class YFinanceProvider:
    """yfinance 기반 데이터 제공자 — retry + exponential backoff 적용 (DBG-1)."""

    PERIOD_MAPPING = {
        "1y": "1y",
        "3y": "3y",
        "5y": "5y",
        "10y": "10y",
    }

    def fetch_prices(
        self,
        tickers: list[str],
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """yfinance로 종목 가격 데이터 수집 — retry 적용."""
        logger.info(
            "yfinance_fetching_prices",
            tickers=tickers[:5],
            n_tickers=len(tickers),
            period=period,
            start_date=start_date,
            end_date=end_date,
        )

        def _do_fetch() -> pd.DataFrame:
            if start_date and end_date:
                return yf.download(
                    tickers=tickers,
                    start=start_date,
                    end=end_date,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=True,
                )
            yf_period = self.PERIOD_MAPPING.get(period, "3y")
            return yf.download(
                tickers=tickers,
                period=yf_period,
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=True,
            )

        data = _retry_with_backoff(_do_fetch)

        prices = data["Close"]
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(tickers[0])

        prices = prices.ffill().dropna()
        return prices

    def fetch_returns(
        self,
        tickers: list[str],
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """yfinance로 종목 수익률 데이터 수집."""
        prices = self.fetch_prices(tickers, period, start_date=start_date, end_date=end_date)
        returns = prices.pct_change().dropna()
        return returns

    def validate_ticker(self, ticker: str) -> bool:
        """yfinance로 티커 유효성 검증 — retry 미적용 (실패 = invalid 처리)."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            return len(hist) > 0
        except Exception as e:
            logger.warning(
                "ticker_validation_failed",
                ticker=ticker,
                error=str(e),
            )
            return False

    def fetch_single_ticker_prices(
        self,
        ticker: str,
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[pd.Series]:
        """개별 티커 가격 데이터 수집 (resilient fetch용) — retry 적용."""

        def _do_fetch() -> pd.DataFrame:
            if start_date and end_date:
                return yf.download(
                    tickers=ticker,
                    start=start_date,
                    end=end_date,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=False,
                )
            yf_period = self.PERIOD_MAPPING.get(period, "3y")
            return yf.download(
                tickers=ticker,
                period=yf_period,
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )

        try:
            data = _retry_with_backoff(_do_fetch)
        except DataProviderError as e:
            logger.warning(
                "single_ticker_fetch_transient_exhausted",
                ticker=ticker,
                error_type=type(e).__name__,
                error=str(e)[:200],
            )
            return None
        except Exception as e:
            logger.warning(
                "single_ticker_fetch_failed",
                ticker=ticker,
                error_type=type(e).__name__,
                error=str(e)[:200],
            )
            return None

        if len(data) == 0:
            return None

        close = data["Close"]
        if isinstance(close, pd.DataFrame):
            return close.iloc[:, 0]
        return close


class FixtureProvider:
    """Fixture 기반 fallback 제공자 — yfinance 영구 차단 시 시연 보호 (DBG-1).

    AAPL / MSFT / GOOGL 1년 deterministic 가격 시리즈 (fixtures/sample_prices.json).
    실시간 X / 시연 + 면접 시점 안정성 ↑.
    """

    SUPPORTED_TICKERS = ("AAPL", "MSFT", "GOOGL")
    FIXTURE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "sample_prices.json"

    def __init__(self, fixture_path: Optional[Path] = None) -> None:
        self._fixture_path = fixture_path or self.FIXTURE_PATH
        self._prices: Optional[pd.DataFrame] = None

    def _load(self) -> pd.DataFrame:
        if self._prices is not None:
            return self._prices
        with self._fixture_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        index = pd.to_datetime(payload["dates"])
        data = {ticker: payload["prices"][ticker] for ticker in self.SUPPORTED_TICKERS}
        self._prices = pd.DataFrame(data, index=index)
        return self._prices

    def fetch_prices(
        self,
        tickers: list[str],
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fixture 가격 반환 — 미지원 ticker 영역 ValueError."""
        prices = self._load()
        unsupported = [t for t in tickers if t not in prices.columns]
        if unsupported:
            raise ValueError(
                f"FixtureProvider 미지원 ticker: {unsupported} / 지원: {list(self.SUPPORTED_TICKERS)}"
            )
        result = prices[tickers].copy()
        if start_date:
            result = result[result.index >= pd.to_datetime(start_date)]
        if end_date:
            result = result[result.index <= pd.to_datetime(end_date)]
        logger.info(
            "fixture_provider_fetch_prices",
            tickers=tickers,
            rows=len(result),
        )
        return result

    def fetch_returns(
        self,
        tickers: list[str],
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        prices = self.fetch_prices(tickers, period, start_date=start_date, end_date=end_date)
        return prices.pct_change().dropna()

    def validate_ticker(self, ticker: str) -> bool:
        return ticker in self.SUPPORTED_TICKERS

    def fetch_single_ticker_prices(
        self,
        ticker: str,
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[pd.Series]:
        if ticker not in self.SUPPORTED_TICKERS:
            return None
        prices = self.fetch_prices([ticker], period, start_date=start_date, end_date=end_date)
        return prices[ticker]


class CompositeProvider:
    """primary + fallback 조합 — primary 영역 transient 영역 영역 fallback 자동 전환 (DBG-1)."""

    def __init__(self, primary: DataProvider, fallback: DataProvider) -> None:
        self._primary = primary
        self._fallback = fallback

    def _with_fallback(self, op: str, func_primary, func_fallback):
        try:
            return func_primary()
        except (RateLimitError, NetworkError) as e:
            logger.warning(
                "composite_fallback_transient",
                op=op,
                error_type=type(e).__name__,
                error=str(e)[:200],
            )
            return func_fallback()
        except Exception as e:
            logger.warning(
                "composite_primary_unexpected_error",
                op=op,
                error_type=type(e).__name__,
                error=str(e)[:200],
            )
            raise

    def fetch_prices(
        self,
        tickers: list[str],
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        return self._with_fallback(
            "fetch_prices",
            lambda: self._primary.fetch_prices(tickers, period, start_date=start_date, end_date=end_date),
            lambda: self._fallback.fetch_prices(tickers, period, start_date=start_date, end_date=end_date),
        )

    def fetch_returns(
        self,
        tickers: list[str],
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        return self._with_fallback(
            "fetch_returns",
            lambda: self._primary.fetch_returns(tickers, period, start_date=start_date, end_date=end_date),
            lambda: self._fallback.fetch_returns(tickers, period, start_date=start_date, end_date=end_date),
        )

    def validate_ticker(self, ticker: str) -> bool:
        try:
            return self._primary.validate_ticker(ticker)
        except (RateLimitError, NetworkError) as e:
            logger.warning(
                "composite_fallback_validate_ticker",
                ticker=ticker,
                error_type=type(e).__name__,
            )
            return self._fallback.validate_ticker(ticker)

    def fetch_single_ticker_prices(
        self,
        ticker: str,
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[pd.Series]:
        primary = self._primary
        fallback = self._fallback
        if hasattr(primary, "fetch_single_ticker_prices"):
            try:
                return primary.fetch_single_ticker_prices(ticker, period, start_date=start_date, end_date=end_date)
            except (RateLimitError, NetworkError) as e:
                logger.warning(
                    "composite_fallback_single_ticker",
                    ticker=ticker,
                    error_type=type(e).__name__,
                )
        if hasattr(fallback, "fetch_single_ticker_prices"):
            return fallback.fetch_single_ticker_prices(ticker, period, start_date=start_date, end_date=end_date)
        return None


_provider_instance: Optional[DataProvider] = None


def get_data_provider() -> DataProvider:
    """데이터 제공자 팩토리 — DBG-1 정착 후 CompositeProvider 기본.

    설정에 따라 primary 선택 (yfinance default). fallback = FixtureProvider.
    테스트에서는 set_data_provider()로 mock 주입 가능.
    """
    global _provider_instance

    if _provider_instance is None:
        settings = get_settings()
        provider_type = getattr(settings, "data_provider", "yfinance")

        if provider_type == "fixture":
            _provider_instance = FixtureProvider()
        else:
            primary = YFinanceProvider()
            fallback = FixtureProvider()
            _provider_instance = CompositeProvider(primary=primary, fallback=fallback)

        logger.info(
            "data_provider_initialized",
            provider_type=provider_type,
            composite=isinstance(_provider_instance, CompositeProvider),
        )

    return _provider_instance


def set_data_provider(provider: DataProvider) -> None:
    """데이터 제공자 설정 (테스트용 mock 주입)."""
    global _provider_instance
    _provider_instance = provider
    logger.info("data_provider_set_manually")


def reset_data_provider() -> None:
    """데이터 제공자 초기화 (테스트 정리용)."""
    global _provider_instance
    _provider_instance = None
