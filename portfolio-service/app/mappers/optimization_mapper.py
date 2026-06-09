"""최적화 서비스 결과를 응답 스키마로 변환하는 순수 mapper (② SRP)."""

from __future__ import annotations

import numpy as np

from app.schemas.portfolio import (
    CovarianceValidationResponse,
    FrontierPoint,
    OptimizationDiagnosticsResponse,
    PortfolioMetricsResponse,
)
from app.services.optimizer import (
    EfficientFrontier,
    OptimizationDiagnostics,
    PortfolioMetrics,
)

TRADING_DAYS = 252


def format_portfolio_metrics(result: PortfolioMetrics, rf: float) -> PortfolioMetricsResponse:
    """일간 메트릭을 연율화해 응답 스키마로 변환 (rf=연율 무위험 이자율)."""
    annual_return = float(result.expected_return * TRADING_DAYS)
    annual_vol = float(result.volatility * np.sqrt(TRADING_DAYS))
    sharpe = (annual_return - rf) / annual_vol if annual_vol > 0 else 0
    return PortfolioMetricsResponse(
        expected_return=round(annual_return, 6),
        volatility=round(annual_vol, 6),
        sharpe_ratio=round(sharpe, 4),
    )


def map_diagnostics(diag: OptimizationDiagnostics) -> OptimizationDiagnosticsResponse:
    """최적화 진단 dataclass를 응답 스키마로 변환 (공분산 검증 중첩 포함)."""
    return OptimizationDiagnosticsResponse(
        converged=diag.converged,
        iterations=diag.iterations,
        final_objective=diag.final_objective,
        condition_number=diag.condition_number,
        solver_message=diag.solver_message,
        gradient_norm=diag.gradient_norm,
        covariance_validation=CovarianceValidationResponse(
            is_valid=diag.covariance_validation.is_valid,
            condition_number=diag.covariance_validation.condition_number,
            is_positive_definite=diag.covariance_validation.min_eigenvalue > 0,
            min_eigenvalue=diag.covariance_validation.min_eigenvalue,
            max_correlation=diag.covariance_validation.max_correlation,
            issues=list(diag.covariance_validation.issues),
            regularized=diag.covariance_validation.was_regularized,
        ),
    )


def build_frontier(frontier: EfficientFrontier, tickers: list[str]) -> list[FrontierPoint]:
    """효율적 프론티어를 포인트별 연율화·weights 매핑해 응답 리스트로 변환."""
    return [
        FrontierPoint(
            expected_return=round(float(ret * TRADING_DAYS), 6),
            volatility=round(float(vol * np.sqrt(TRADING_DAYS)), 6),
            weights={
                ticker: round(float(w), 4)
                for ticker, w in zip(tickers, weights)
            },
        )
        for ret, vol, weights in zip(
            frontier.returns,
            frontier.volatilities,
            frontier.weights,
        )
    ]
