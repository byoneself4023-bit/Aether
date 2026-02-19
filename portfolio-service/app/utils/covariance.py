"""공분산 행렬 추정 유틸리티"""

import numpy as np
from numpy.typing import NDArray
from sklearn.covariance import LedoitWolf


def sample_covariance(returns: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    표본 공분산 행렬 계산

    Args:
        returns: 수익률 행렬 (T x N), T=기간, N=자산 수

    Returns:
        공분산 행렬 (N x N)
    """
    return np.cov(returns, rowvar=False)


def shrinkage_covariance(returns: NDArray[np.float64]) -> NDArray[np.float64]:
    """
    Ledoit-Wolf Shrinkage 공분산 행렬 계산

    표본 공분산의 추정 오류를 줄이기 위해 구조화된 타겟으로 수축.
    특히 N > T 또는 N ≈ T 상황에서 안정적인 추정 제공.

    Args:
        returns: 수익률 행렬 (T x N)

    Returns:
        Shrinkage 공분산 행렬 (N x N)
    """
    lw = LedoitWolf()
    lw.fit(returns)
    return lw.covariance_


def annualize(
    cov: NDArray[np.float64],
    trading_days: int = 252
) -> NDArray[np.float64]:
    """
    공분산 행렬 연율화

    Args:
        cov: 일간 공분산 행렬
        trading_days: 연간 거래일 수

    Returns:
        연율화된 공분산 행렬
    """
    return cov * trading_days


def annualize_returns(
    mu: NDArray[np.float64],
    trading_days: int = 252
) -> NDArray[np.float64]:
    """
    기대수익률 연율화

    Args:
        mu: 일간 기대수익률
        trading_days: 연간 거래일 수

    Returns:
        연율화된 기대수익률
    """
    return mu * trading_days
