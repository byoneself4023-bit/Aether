"""데이터 수집 서비스 (캐시 지원, Provider 패턴)"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional
from dataclasses import dataclass

from app.middleware.logging import logger
from app.services.cache import MarketDataCache, get_cache
from app.services.data_provider import get_data_provider, YFinanceProvider


@dataclass
class TickerInfo:
    """종목 정보"""
    ticker: str
    name: str
    sector: Optional[str]
    industry: Optional[str]
    currency: str


@dataclass
class FetchResult:
    """데이터 수집 결과 (부분 성공 지원)"""
    data: pd.DataFrame  # 성공한 티커의 데이터
    successful_tickers: list[str]  # 성공한 티커 리스트
    failed_tickers: list[str]  # 실패한 티커 리스트
    warnings: list[str]  # 경고 메시지 리스트


@dataclass
class ReturnsResult:
    """수익률 + 공분산 결과 (부분 성공 지원)"""
    mu: np.ndarray  # 기대수익률 벡터
    cov: np.ndarray  # 공분산 행렬
    returns_df: pd.DataFrame  # 수익률 DataFrame
    successful_tickers: list[str]  # 성공한 티커 리스트
    failed_tickers: list[str]  # 실패한 티커 리스트
    warnings: list[str]  # 경고 메시지 리스트


def period_to_yf(period: str) -> str:
    """
    기간 문자열을 yfinance 포맷으로 변환

    Args:
        period: "1y", "3y", "5y", "10y"

    Returns:
        yfinance period string
    """
    mapping = {
        "1y": "1y",
        "3y": "3y",
        "5y": "5y",
        "10y": "10y",
    }
    return mapping.get(period, "3y")


def fetch_prices(
    tickers: list[str],
    period: str = "3y",
    use_cache: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    종목 가격 데이터 수집 (캐시 지원, Provider 패턴)

    Args:
        tickers: 종목 티커 리스트
        period: 데이터 기간 ("1y", "3y", "5y", "10y")
        use_cache: 캐시 사용 여부

    Returns:
        Adjusted Close 가격 DataFrame (date x tickers)
    """
    cache = get_cache() if use_cache else None

    # 캐시 조회
    if cache:
        cached_prices = cache.get_prices(tickers, period)
        if cached_prices is not None:
            return cached_prices

    # Provider를 통해 데이터 수집
    provider = get_data_provider()
    prices = provider.fetch_prices(tickers, period, start_date=start_date, end_date=end_date)

    # 캐시 저장 (날짜 지정 시에도 period 키로 저장)
    if cache and len(prices) > 0:
        cache.set_prices(tickers, period, prices)

    return prices


def fetch_prices_resilient(
    tickers: list[str],
    period: str = "3y",
    min_tickers: int = 2,
    use_cache: bool = True,
    timeout: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> FetchResult:
    """
    부분 실패를 허용하는 가격 데이터 수집 (Provider 패턴)

    일부 티커가 실패해도 나머지 티커로 계속 진행.
    AAPL,MSFT,FAKE,GOOGL 요청 시 FAKE만 제외하고 나머지 반환.

    Args:
        tickers: 종목 티커 리스트
        period: 데이터 기간
        min_tickers: 최소 필요 티커 수 (미만이면 에러)
        use_cache: 캐시 사용 여부
        timeout: 개별 티커 타임아웃 (초)

    Returns:
        FetchResult(data, successful_tickers, failed_tickers, warnings)

    Raises:
        ValueError: 성공한 티커가 min_tickers 미만일 때
    """
    cache = get_cache() if use_cache else None
    provider = get_data_provider()

    successful_prices: dict[str, pd.Series] = {}
    failed_tickers: list[str] = []
    warnings: list[str] = []

    logger.info(
        "fetching_prices_resilient",
        tickers=tickers[:5],
        n_tickers=len(tickers),
        period=period
    )

    for ticker in tickers:
        # 캐시에서 개별 티커 검증 결과 확인
        if cache:
            cached_valid = cache.get_ticker_validation(ticker)
            if cached_valid is False:
                failed_tickers.append(ticker)
                warnings.append(f"{ticker}: Previously marked as invalid (cached)")
                continue

        try:
            # Provider를 통해 개별 티커 다운로드
            if isinstance(provider, YFinanceProvider):
                prices = provider.fetch_single_ticker_prices(
                    ticker, period, start_date=start_date, end_date=end_date
                )
            else:
                # 일반 provider의 경우 fetch_prices 사용
                prices_df = provider.fetch_prices([ticker], period)
                prices = prices_df[ticker] if len(prices_df) > 0 else None

            if prices is None or len(prices) == 0:
                failed_tickers.append(ticker)
                warnings.append(f"{ticker}: No data returned from provider")
                if cache:
                    cache.set_ticker_validation(ticker, False)
                continue

            successful_prices[ticker] = prices

            # 캐시에 유효 표시
            if cache:
                cache.set_ticker_validation(ticker, True)

        except Exception as e:
            failed_tickers.append(ticker)
            warnings.append(f"{ticker}: {type(e).__name__} - {str(e)[:100]}")
            logger.warning(
                "ticker_fetch_failed",
                ticker=ticker,
                error_type=type(e).__name__,
                error=str(e)[:200]
            )
            if cache:
                cache.set_ticker_validation(ticker, False)

    # 최소 티커 수 체크
    if len(successful_prices) < min_tickers:
        raise ValueError(
            f"Insufficient valid tickers: {len(successful_prices)} succeeded, "
            f"minimum {min_tickers} required. "
            f"Failed tickers: {failed_tickers}"
        )

    # DataFrame 생성
    prices_df = pd.DataFrame(successful_prices)

    # 결측치 처리
    prices_df = prices_df.ffill().dropna()

    if len(prices_df) == 0:
        raise ValueError(
            f"No overlapping data for successful tickers after cleaning. "
            f"Successful: {list(successful_prices.keys())}"
        )

    successful_tickers = list(prices_df.columns)

    # 실패한 티커가 있으면 로깅
    if failed_tickers:
        logger.warning(
            "partial_fetch_success",
            successful=len(successful_tickers),
            failed=len(failed_tickers),
            failed_tickers=failed_tickers
        )

    return FetchResult(
        data=prices_df,
        successful_tickers=successful_tickers,
        failed_tickers=failed_tickers,
        warnings=warnings
    )


def fetch_returns_resilient(
    tickers: list[str],
    period: str = "3y",
    min_tickers: int = 2,
    use_cache: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> FetchResult:
    """
    부분 실패를 허용하는 수익률 데이터 수집

    Args:
        tickers: 종목 티커 리스트
        period: 데이터 기간
        min_tickers: 최소 필요 티커 수
        use_cache: 캐시 사용 여부

    Returns:
        FetchResult(data=returns_df, successful_tickers, failed_tickers, warnings)
    """
    prices_result = fetch_prices_resilient(
        tickers=tickers,
        period=period,
        min_tickers=min_tickers,
        use_cache=use_cache,
        start_date=start_date,
        end_date=end_date,
    )

    # 수익률 계산
    returns_df = prices_result.data.pct_change().dropna()

    return FetchResult(
        data=returns_df,
        successful_tickers=prices_result.successful_tickers,
        failed_tickers=prices_result.failed_tickers,
        warnings=prices_result.warnings
    )


def fetch_returns(
    tickers: list[str],
    period: str = "3y",
    use_cache: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    일간 수익률 데이터 수집 (캐시 지원, Provider 패턴)

    Args:
        tickers: 종목 티커 리스트
        period: 데이터 기간 ("1y", "3y", "5y", "10y")
        use_cache: 캐시 사용 여부

    Returns:
        일간 수익률 DataFrame (date x tickers)
    """
    cache = get_cache() if use_cache else None

    # 수익률 캐시 조회
    if cache:
        cached_returns = cache.get_returns(tickers, period)
        if cached_returns is not None:
            return cached_returns

    prices = fetch_prices(tickers, period, use_cache, start_date=start_date, end_date=end_date)

    # 일간 수익률 계산 (로그 수익률 대신 단순 수익률)
    returns = prices.pct_change().dropna()

    # 캐시 저장
    if cache and len(returns) > 0:
        cache.set_returns(tickers, period, returns)

    return returns


def get_ticker_info(tickers: list[str]) -> list[TickerInfo]:
    """
    종목 기본 정보 조회

    Args:
        tickers: 종목 티커 리스트

    Returns:
        TickerInfo 리스트
    """
    result = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            result.append(TickerInfo(
                ticker=ticker,
                name=info.get("longName", info.get("shortName", ticker)),
                sector=info.get("sector"),
                industry=info.get("industry"),
                currency=info.get("currency", "USD")
            ))
        except Exception:
            # 정보 조회 실패 시 기본값
            result.append(TickerInfo(
                ticker=ticker,
                name=ticker,
                sector=None,
                industry=None,
                currency="USD"
            ))

    return result


def get_returns_and_covariance(
    tickers: list[str],
    period: str = "3y",
    use_shrinkage: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    수익률 데이터에서 기대수익률과 공분산 행렬 계산

    Args:
        tickers: 종목 티커 리스트
        period: 데이터 기간
        use_shrinkage: Shrinkage 공분산 사용 여부

    Returns:
        (mu, cov, returns_df) 튜플
        - mu: 일간 기대수익률 벡터
        - cov: 일간 공분산 행렬
        - returns_df: 수익률 DataFrame
    """
    from app.utils.covariance import shrinkage_covariance, sample_covariance

    returns_df = fetch_returns(tickers, period, start_date=start_date, end_date=end_date)
    returns = returns_df.values

    # 일간 기대수익률
    mu = np.mean(returns, axis=0)

    # 공분산 행렬
    if use_shrinkage:
        cov = shrinkage_covariance(returns)
    else:
        cov = sample_covariance(returns)

    return mu, cov, returns_df


def get_returns_and_covariance_resilient(
    tickers: list[str],
    period: str = "3y",
    use_shrinkage: bool = True,
    min_tickers: int = 2,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> ReturnsResult:
    """
    부분 실패를 허용하는 수익률 + 공분산 계산

    일부 티커가 실패해도 나머지로 계속 진행.

    Args:
        tickers: 종목 티커 리스트
        period: 데이터 기간
        use_shrinkage: Shrinkage 공분산 사용 여부
        min_tickers: 최소 필요 티커 수

    Returns:
        ReturnsResult(mu, cov, returns_df, successful_tickers, failed_tickers, warnings)
    """
    from app.utils.covariance import shrinkage_covariance, sample_covariance

    # 부분 실패 허용 수익률 수집
    fetch_result = fetch_returns_resilient(
        tickers=tickers,
        period=period,
        min_tickers=min_tickers,
        start_date=start_date,
        end_date=end_date,
    )

    returns_df = fetch_result.data
    returns = returns_df.values

    # 기대수익률 계산
    mu = np.mean(returns, axis=0)

    # 공분산 행렬 계산
    if use_shrinkage:
        cov = shrinkage_covariance(returns)
    else:
        cov = sample_covariance(returns)

    return ReturnsResult(
        mu=mu,
        cov=cov,
        returns_df=returns_df,
        successful_tickers=fetch_result.successful_tickers,
        failed_tickers=fetch_result.failed_tickers,
        warnings=fetch_result.warnings
    )


def validate_tickers(
    tickers: list[str],
    use_cache: bool = True
) -> tuple[list[str], list[str]]:
    """
    유효한 티커 검증 (캐시 지원, Provider 패턴)

    Args:
        tickers: 종목 티커 리스트
        use_cache: 캐시 사용 여부

    Returns:
        (valid_tickers, invalid_tickers) 튜플
    """
    cache = get_cache() if use_cache else None
    provider = get_data_provider()

    valid = []
    invalid = []

    for ticker in tickers:
        # 캐시 조회
        if cache:
            cached_result = cache.get_ticker_validation(ticker)
            if cached_result is not None:
                if cached_result:
                    valid.append(ticker)
                else:
                    invalid.append(ticker)
                continue

        # Provider로 검증
        try:
            is_valid = provider.validate_ticker(ticker)

            if is_valid:
                valid.append(ticker)
            else:
                invalid.append(ticker)

            # 캐시 저장
            if cache:
                cache.set_ticker_validation(ticker, is_valid)

        except Exception as e:
            invalid.append(ticker)
            logger.warning(
                "ticker_validation_failed",
                ticker=ticker,
                error=str(e)
            )
            if cache:
                cache.set_ticker_validation(ticker, False)

    return valid, invalid
