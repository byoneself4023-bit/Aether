"""리스크 분석 API 라우터"""

from fastapi import APIRouter, Depends, HTTPException
import numpy as np

from app.middleware.auth import verify_jwt
from app.schemas.portfolio import (
    RiskRequest,
    RiskResponse,
    VaRResponse,
    RiskSummaryResponse,
)
from app.services.data import get_returns_and_covariance, validate_tickers
from app.services.risk import (
    parametric_var,
    monte_carlo_var,
    cvar,
    risk_summary,
)

router = APIRouter(prefix="/api", tags=["risk"])


@router.post("/risk", response_model=RiskResponse)
def analyze_risk(
    request: RiskRequest,
    user: dict = Depends(verify_jwt),
) -> RiskResponse:
    """
    포트폴리오 리스크 분석

    주어진 비중의 포트폴리오에 대해 VaR, CVaR 등 리스크 지표를 계산합니다.
    - Parametric VaR: 정규분포 가정
    - Monte Carlo VaR: 시뮬레이션 기반
    - CVaR (Expected Shortfall): 테일 리스크 측정
    """
    tickers = request.tickers
    weights_dict = request.weights

    # 티커 검증
    valid_tickers, invalid_tickers = validate_tickers(tickers)
    if invalid_tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tickers: {invalid_tickers}"
        )

    # 비중 검증
    missing_weights = set(tickers) - set(weights_dict.keys())
    if missing_weights:
        raise HTTPException(
            status_code=400,
            detail=f"Missing weights for tickers: {list(missing_weights)}"
        )

    # 비중 합계 검증 (허용 오차 1%)
    weight_sum = sum(weights_dict[t] for t in tickers)
    if abs(weight_sum - 1.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Weights must sum to 1.0, got {weight_sum:.4f}"
        )

    try:
        # 수익률 데이터 및 공분산 계산
        mu, cov, _ = get_returns_and_covariance(
            tickers=tickers,
            period=request.period,
            use_shrinkage=True
        )

        # 비중 벡터 생성 (티커 순서 맞춤)
        weights = np.array([weights_dict[t] for t in tickers])

        # Parametric VaR
        p_var = parametric_var(
            weights=weights,
            mu=mu,
            cov=cov,
            confidence=request.confidence
        )

        # Monte Carlo VaR
        mc_var = monte_carlo_var(
            weights=weights,
            mu=mu,
            cov=cov,
            n_simulations=request.n_simulations,
            confidence=request.confidence
        )

        # CVaR
        cvar_result = cvar(
            weights=weights,
            mu=mu,
            cov=cov,
            confidence=request.confidence,
            method="monte_carlo",
            n_simulations=request.n_simulations
        )

        # 종합 리스크 요약
        summary = risk_summary(
            weights=weights,
            mu=mu,
            cov=cov,
            n_simulations=request.n_simulations
        )

        return RiskResponse(
            parametric_var=VaRResponse(
                value=round(p_var.var, 6),
                confidence=p_var.confidence,
                holding_days=p_var.holding_days,
                method=p_var.method
            ),
            monte_carlo_var=VaRResponse(
                value=round(mc_var.var, 6),
                confidence=mc_var.confidence,
                holding_days=mc_var.holding_days,
                method=mc_var.method
            ),
            cvar=round(cvar_result.cvar, 6),
            risk_summary=RiskSummaryResponse(
                volatility=round(summary.volatility, 6),
                expected_return=round(summary.expected_return, 6),
                var_95_parametric=round(summary.var_95_parametric, 6),
                var_99_parametric=round(summary.var_99_parametric, 6),
                var_95_montecarlo=round(summary.var_95_montecarlo, 6),
                var_99_montecarlo=round(summary.var_99_montecarlo, 6),
                cvar_95=round(summary.cvar_95, 6),
                cvar_99=round(summary.cvar_99, 6),
                max_loss_1d=round(summary.max_loss_1d, 6)
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk analysis failed: {str(e)}"
        )
