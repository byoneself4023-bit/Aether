"""리스크 분석 서비스 - VaR, CVaR, 몬테카를로 시뮬레이션"""

import numpy as np
from numpy.typing import NDArray
from scipy import stats
from dataclasses import dataclass
from typing import Literal


@dataclass
class VaRResult:
    """VaR 계산 결과"""
    var: float  # Value at Risk (손실, 양수)
    confidence: float
    holding_days: int
    method: str


@dataclass
class CVaRResult:
    """CVaR 계산 결과"""
    cvar: float  # Conditional VaR (Expected Shortfall)
    var: float
    confidence: float
    method: str


@dataclass
class RiskSummary:
    """종합 리스크 리포트"""
    volatility: float  # 연율화 변동성
    var_95_parametric: float
    var_99_parametric: float
    var_95_montecarlo: float
    var_99_montecarlo: float
    cvar_95: float
    cvar_99: float
    max_loss_1d: float  # 1일 최대 예상 손실 (99.9%)
    expected_return: float


def parametric_var(
    weights: NDArray[np.float64],
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    confidence: float = 0.95,
    holding_days: int = 1
) -> VaRResult:
    """
    정규분포 가정 Parametric VaR 계산

    VaR = -(μ_p * t - z_α * σ_p * √t)
        = z_α * σ_p * √t - μ_p * t  (손실 양수 기준)

    Args:
        weights: 자산 비중 (N,)
        mu: 일간 기대수익률 벡터 (N,)
        cov: 일간 공분산 행렬 (N x N)
        confidence: 신뢰수준 (0.95 = 95%)
        holding_days: 보유 기간 (일)

    Returns:
        VaRResult 객체
    """
    w = np.asarray(weights)

    # 포트폴리오 일간 수익률/변동성
    port_mu = float(w @ mu)
    port_sigma = float(np.sqrt(w @ cov @ w))

    # 보유 기간 조정 (√t 룰)
    port_mu_t = port_mu * holding_days
    port_sigma_t = port_sigma * np.sqrt(holding_days)

    # z-score (단측 검정)
    z_alpha = stats.norm.ppf(confidence)

    # VaR (손실 양수 기준)
    var = z_alpha * port_sigma_t - port_mu_t

    return VaRResult(
        var=max(var, 0),  # VaR는 최소 0
        confidence=confidence,
        holding_days=holding_days,
        method="parametric"
    )


def monte_carlo_var(
    weights: NDArray[np.float64],
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    n_simulations: int = 10000,
    confidence: float = 0.95,
    holding_days: int = 1,
    seed: int = 42
) -> VaRResult:
    """
    몬테카를로 시뮬레이션 VaR 계산

    다변량 정규분포에서 시뮬레이션 후 손실 분위수 계산.
    Fat tail을 직접 반영하진 않지만, 비선형 포트폴리오에 유용.

    Args:
        weights: 자산 비중 (N,)
        mu: 일간 기대수익률 벡터 (N,)
        cov: 일간 공분산 행렬 (N x N)
        n_simulations: 시뮬레이션 횟수
        confidence: 신뢰수준
        holding_days: 보유 기간
        seed: 랜덤 시드

    Returns:
        VaRResult 객체
    """
    w = np.asarray(weights)
    rng = np.random.default_rng(seed)

    # 보유 기간 조정
    mu_t = mu * holding_days
    cov_t = cov * holding_days

    # 다변량 정규분포에서 수익률 시뮬레이션
    simulated_returns = rng.multivariate_normal(mu_t, cov_t, n_simulations)

    # 포트폴리오 수익률
    portfolio_returns = simulated_returns @ w

    # VaR = -(하위 α% 분위수) = 손실
    var = -np.percentile(portfolio_returns, (1 - confidence) * 100)

    return VaRResult(
        var=max(var, 0),
        confidence=confidence,
        holding_days=holding_days,
        method="monte_carlo"
    )


def cvar(
    weights: NDArray[np.float64],
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    confidence: float = 0.95,
    method: Literal["parametric", "monte_carlo"] = "monte_carlo",
    n_simulations: int = 10000,
    seed: int = 42
) -> CVaRResult:
    """
    Conditional VaR (Expected Shortfall) 계산

    CVaR = E[Loss | Loss > VaR]
    VaR를 초과하는 손실의 평균. Tail risk를 더 잘 반영.

    Args:
        weights: 자산 비중 (N,)
        mu: 일간 기대수익률 벡터 (N,)
        cov: 일간 공분산 행렬 (N x N)
        confidence: 신뢰수준
        method: "parametric" 또는 "monte_carlo"
        n_simulations: 몬테카를로 시뮬레이션 횟수
        seed: 랜덤 시드

    Returns:
        CVaRResult 객체
    """
    w = np.asarray(weights)

    if method == "parametric":
        # Parametric CVaR (정규분포 가정)
        port_mu = float(w @ mu)
        port_sigma = float(np.sqrt(w @ cov @ w))

        z_alpha = stats.norm.ppf(confidence)
        var_value = z_alpha * port_sigma - port_mu

        # CVaR 공식 (정규분포): CVaR = σ * φ(z_α) / (1-α) - μ
        phi_z = stats.norm.pdf(z_alpha)
        cvar_value = port_sigma * phi_z / (1 - confidence) - port_mu

        return CVaRResult(
            cvar=max(cvar_value, 0),
            var=max(var_value, 0),
            confidence=confidence,
            method="parametric"
        )

    else:  # monte_carlo
        rng = np.random.default_rng(seed)

        # 수익률 시뮬레이션
        simulated_returns = rng.multivariate_normal(mu, cov, n_simulations)
        portfolio_returns = simulated_returns @ w

        # 손실로 변환 (양수)
        losses = -portfolio_returns

        # VaR (상위 α% 손실)
        var_value = np.percentile(losses, confidence * 100)

        # CVaR = VaR 초과 손실의 평균
        tail_losses = losses[losses >= var_value]
        cvar_value = float(np.mean(tail_losses)) if len(tail_losses) > 0 else var_value

        return CVaRResult(
            cvar=max(cvar_value, 0),
            var=max(var_value, 0),
            confidence=confidence,
            method="monte_carlo"
        )


def risk_summary(
    weights: NDArray[np.float64],
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    trading_days: int = 252,
    n_simulations: int = 10000,
    seed: int = 42
) -> RiskSummary:
    """
    종합 리스크 리포트 생성

    Args:
        weights: 자산 비중 (N,)
        mu: 일간 기대수익률 벡터 (N,)
        cov: 일간 공분산 행렬 (N x N)
        trading_days: 연간 거래일 수
        n_simulations: 몬테카를로 시뮬레이션 횟수
        seed: 랜덤 시드

    Returns:
        RiskSummary 객체
    """
    w = np.asarray(weights)

    # 기본 지표
    port_mu = float(w @ mu)
    port_sigma = float(np.sqrt(w @ cov @ w))

    # 연율화
    annual_return = port_mu * trading_days
    annual_vol = port_sigma * np.sqrt(trading_days)

    # Parametric VaR
    var_95_p = parametric_var(w, mu, cov, 0.95).var
    var_99_p = parametric_var(w, mu, cov, 0.99).var

    # Monte Carlo VaR
    var_95_mc = monte_carlo_var(w, mu, cov, n_simulations, 0.95, seed=seed).var
    var_99_mc = monte_carlo_var(w, mu, cov, n_simulations, 0.99, seed=seed).var

    # CVaR (Monte Carlo)
    cvar_95 = cvar(w, mu, cov, 0.95, "monte_carlo", n_simulations, seed).cvar
    cvar_99 = cvar(w, mu, cov, 0.99, "monte_carlo", n_simulations, seed).cvar

    # 최대 예상 손실 (99.9% 신뢰수준)
    max_loss = monte_carlo_var(w, mu, cov, n_simulations, 0.999, seed=seed).var

    return RiskSummary(
        volatility=annual_vol,
        var_95_parametric=var_95_p,
        var_99_parametric=var_99_p,
        var_95_montecarlo=var_95_mc,
        var_99_montecarlo=var_99_mc,
        cvar_95=cvar_95,
        cvar_99=cvar_99,
        max_loss_1d=max_loss,
        expected_return=annual_return
    )
