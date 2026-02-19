"""데이터 제공자 추상화 (Protocol 패턴)"""

from typing import Protocol, Optional, runtime_checkable
import pandas as pd
import yfinance as yf

from app.config import get_settings
from app.middleware.logging import logger


@runtime_checkable
class DataProvider(Protocol):
    """데이터 제공자 프로토콜

    모든 데이터 제공자는 이 프로토콜을 따라야 함.
    테스트 시 mock provider로 교체 가능.
    """

    def fetch_prices(
        self,
        tickers: list[str],
        period: str = "3y"
    ) -> pd.DataFrame:
        """
        종목 가격 데이터 수집

        Args:
            tickers: 종목 티커 리스트
            period: 데이터 기간 ("1y", "3y", "5y", "10y")

        Returns:
            Adjusted Close 가격 DataFrame (date x tickers)
        """
        ...

    def fetch_returns(
        self,
        tickers: list[str],
        period: str = "3y"
    ) -> pd.DataFrame:
        """
        종목 수익률 데이터 수집

        Args:
            tickers: 종목 티커 리스트
            period: 데이터 기간

        Returns:
            일간 수익률 DataFrame (date x tickers)
        """
        ...

    def validate_ticker(self, ticker: str) -> bool:
        """
        티커 유효성 검증

        Args:
            ticker: 종목 티커

        Returns:
            유효 여부
        """
        ...


class YFinanceProvider:
    """yfinance 기반 데이터 제공자"""

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
        """yfinance로 종목 가격 데이터 수집"""
        logger.info(
            "yfinance_fetching_prices",
            tickers=tickers[:5],
            n_tickers=len(tickers),
            period=period,
            start_date=start_date,
            end_date=end_date,
        )

        # start_date/end_date가 있으면 우선 사용
        if start_date and end_date:
            data = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
        else:
            yf_period = self.PERIOD_MAPPING.get(period, "3y")
            data = yf.download(
                tickers=tickers,
                period=yf_period,
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=True,
            )

        # Close 가격 추출 (yfinance 1.x: always MultiIndex columns)
        prices = data["Close"]
        # 단일 티커일 경우 컬럼명 정리
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(tickers[0])

        # 결측치 처리 (forward fill → drop remaining)
        prices = prices.ffill().dropna()

        return prices

    def fetch_returns(
        self,
        tickers: list[str],
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """yfinance로 종목 수익률 데이터 수집"""
        prices = self.fetch_prices(tickers, period, start_date=start_date, end_date=end_date)
        returns = prices.pct_change().dropna()
        return returns

    def validate_ticker(self, ticker: str) -> bool:
        """yfinance로 티커 유효성 검증"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            return len(hist) > 0
        except Exception as e:
            logger.warning(
                "ticker_validation_failed",
                ticker=ticker,
                error=str(e)
            )
            return False

    def fetch_single_ticker_prices(
        self,
        ticker: str,
        period: str = "3y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[pd.Series]:
        """
        개별 티커 가격 데이터 수집 (resilient fetch용)

        Args:
            ticker: 종목 티커
            period: 데이터 기간
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)

        Returns:
            가격 Series 또는 None (실패 시)
        """
        try:
            if start_date and end_date:
                data = yf.download(
                    tickers=ticker,
                    start=start_date,
                    end=end_date,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=False,
                )
            else:
                yf_period = self.PERIOD_MAPPING.get(period, "3y")
                data = yf.download(
                    tickers=ticker,
                    period=yf_period,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=False,
                )

            if len(data) == 0:
                return None

            close = data["Close"]
            # yfinance 1.x returns DataFrame even for single ticker
            if isinstance(close, pd.DataFrame):
                return close.iloc[:, 0]
            return close

        except Exception as e:
            logger.warning(
                "single_ticker_fetch_failed",
                ticker=ticker,
                error_type=type(e).__name__,
                error=str(e)[:200]
            )
            return None


# 전역 provider 인스턴스 (싱글톤)
_provider_instance: Optional[DataProvider] = None


def get_data_provider() -> DataProvider:
    """
    데이터 제공자 팩토리 함수

    설정에 따라 적절한 provider를 반환.
    테스트에서는 set_data_provider()로 mock 주입 가능.

    Returns:
        DataProvider 구현체
    """
    global _provider_instance

    if _provider_instance is None:
        settings = get_settings()
        provider_type = getattr(settings, "data_provider", "yfinance")

        if provider_type == "yfinance":
            _provider_instance = YFinanceProvider()
        else:
            # 기본값: yfinance
            _provider_instance = YFinanceProvider()

        logger.info(
            "data_provider_initialized",
            provider_type=provider_type
        )

    return _provider_instance


def set_data_provider(provider: DataProvider) -> None:
    """
    데이터 제공자 설정 (테스트용)

    테스트에서 mock provider를 주입할 때 사용.

    Args:
        provider: DataProvider 구현체
    """
    global _provider_instance
    _provider_instance = provider
    logger.info("data_provider_set_manually")


def reset_data_provider() -> None:
    """
    데이터 제공자 초기화 (테스트 정리용)

    테스트 후 provider를 초기 상태로 되돌림.
    """
    global _provider_instance
    _provider_instance = None
