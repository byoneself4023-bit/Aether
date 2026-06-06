"""optimization_mapper 순수 변환 단위 테스트 (② SRP 추출 검증)."""

from __future__ import annotations

import numpy as np

from app.mappers.optimization_mapper import (
    TRADING_DAYS,
    build_frontier,
    format_portfolio_metrics,
    map_diagnostics,
)
from app.services.optimizer import (
    CovarianceValidation,
    EfficientFrontier,
    OptimizationDiagnostics,
    PortfolioMetrics,
)


class TestFormatPortfolioMetrics:
    def test_annualizes_daily_metrics(self):
        result = PortfolioMetrics(
            weights=np.array([0.5, 0.5]),
            expected_return=0.001,
            volatility=0.01,
            sharpe_ratio=0.0,
        )
        rf = 0.02

        response = format_portfolio_metrics(result, rf)

        expected_return = round(0.001 * TRADING_DAYS, 6)
        expected_vol = round(0.01 * float(np.sqrt(TRADING_DAYS)), 6)
        expected_sharpe = round((expected_return - rf) / expected_vol, 4)
        assert response.expected_return == expected_return
        assert response.volatility == expected_vol
        assert response.sharpe_ratio == expected_sharpe

    def test_zero_volatility_yields_zero_sharpe(self):
        result = PortfolioMetrics(
            weights=np.array([1.0]),
            expected_return=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
        )

        response = format_portfolio_metrics(result, rf=0.02)

        assert response.volatility == 0.0
        assert response.sharpe_ratio == 0.0


class TestMapDiagnostics:
    def _diag(self, min_eigenvalue: float) -> OptimizationDiagnostics:
        return OptimizationDiagnostics(
            converged=True,
            iterations=7,
            final_objective=0.123,
            condition_number=42.0,
            covariance_validation=CovarianceValidation(
                is_valid=True,
                issues=["minor"],
                condition_number=42.0,
                min_eigenvalue=min_eigenvalue,
                max_correlation=0.8,
                was_regularized=True,
            ),
            solver_message="ok",
            gradient_norm=0.001,
        )

    def test_maps_nested_covariance_validation(self):
        response = map_diagnostics(self._diag(min_eigenvalue=0.5))

        assert response.converged is True
        assert response.iterations == 7
        assert response.solver_message == "ok"
        assert response.gradient_norm == 0.001
        cov = response.covariance_validation
        assert cov.is_positive_definite is True  # min_eigenvalue > 0
        assert cov.regularized is True  # was_regularized 매핑
        assert cov.issues == ["minor"]

    def test_non_positive_definite_when_eigenvalue_not_positive(self):
        response = map_diagnostics(self._diag(min_eigenvalue=-0.1))

        assert response.covariance_validation.is_positive_definite is False


class TestBuildFrontier:
    def test_shapes_and_annualizes_points(self):
        frontier = EfficientFrontier(
            returns=np.array([0.001, 0.002]),
            volatilities=np.array([0.01, 0.02]),
            weights=np.array([[0.5, 0.5], [0.3, 0.7]]),
        )
        tickers = ["AAPL", "GOOGL"]

        points = build_frontier(frontier, tickers)

        assert len(points) == 2
        assert points[0].expected_return == round(0.001 * TRADING_DAYS, 6)
        assert points[1].volatility == round(0.02 * float(np.sqrt(TRADING_DAYS)), 6)
        assert set(points[0].weights.keys()) == {"AAPL", "GOOGL"}
        assert points[1].weights["GOOGL"] == round(0.7, 4)
