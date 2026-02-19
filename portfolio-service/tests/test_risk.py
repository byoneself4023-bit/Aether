"""risk.py 단위 테스트"""

import numpy as np
import pytest
from app.services.risk import (
    parametric_var,
    monte_carlo_var,
    cvar,
    risk_summary,
)


@pytest.fixture
def sample_data():
    """테스트용 일간 수익률/공분산 (연율화 전)"""
    # 일간 기대수익률 (연 10% ≈ 일 0.04%)
    mu = np.array([0.0004, 0.0006, 0.0005])  # 3자산
    # 일간 공분산 (연 변동성 20%, 30%, 25% 가정)
    daily_vol = np.array([0.20, 0.30, 0.25]) / np.sqrt(252)
    corr = np.array([
        [1.0, 0.3, 0.4],
        [0.3, 1.0, 0.5],
        [0.4, 0.5, 1.0]
    ])
    cov = np.outer(daily_vol, daily_vol) * corr
    return mu, cov


@pytest.fixture
def equal_weights():
    return np.array([1/3, 1/3, 1/3])


class TestParametricVaR:
    def test_basic_var(self, sample_data, equal_weights):
        mu, cov = sample_data

        result = parametric_var(equal_weights, mu, cov, confidence=0.95)

        assert result.var >= 0
        assert result.confidence == 0.95
        assert result.holding_days == 1
        assert result.method == "parametric"

    def test_higher_confidence_higher_var(self, sample_data, equal_weights):
        mu, cov = sample_data

        var_95 = parametric_var(equal_weights, mu, cov, confidence=0.95).var
        var_99 = parametric_var(equal_weights, mu, cov, confidence=0.99).var

        # 99% VaR > 95% VaR
        assert var_99 > var_95

    def test_longer_holding_higher_var(self, sample_data, equal_weights):
        mu, cov = sample_data

        var_1d = parametric_var(equal_weights, mu, cov, holding_days=1).var
        var_10d = parametric_var(equal_weights, mu, cov, holding_days=10).var

        # 10일 VaR > 1일 VaR (√t 룰)
        assert var_10d > var_1d
        # 대략 √10 ≈ 3.16배
        assert var_10d / var_1d > 2.5

    def test_higher_volatility_higher_var(self, sample_data):
        mu, cov = sample_data

        # 저변동성 자산만
        w_low = np.array([1.0, 0.0, 0.0])
        # 고변동성 자산만
        w_high = np.array([0.0, 1.0, 0.0])

        var_low = parametric_var(w_low, mu, cov).var
        var_high = parametric_var(w_high, mu, cov).var

        assert var_high > var_low


class TestMonteCarloVaR:
    def test_basic_mc_var(self, sample_data, equal_weights):
        mu, cov = sample_data

        result = monte_carlo_var(equal_weights, mu, cov, n_simulations=10000)

        assert result.var >= 0
        assert result.method == "monte_carlo"

    def test_reproducibility(self, sample_data, equal_weights):
        mu, cov = sample_data

        var1 = monte_carlo_var(equal_weights, mu, cov, seed=42).var
        var2 = monte_carlo_var(equal_weights, mu, cov, seed=42).var

        assert var1 == var2

    def test_convergence_to_parametric(self, sample_data, equal_weights):
        """충분한 시뮬레이션에서 Parametric VaR에 수렴"""
        mu, cov = sample_data

        var_param = parametric_var(equal_weights, mu, cov, confidence=0.95).var
        var_mc = monte_carlo_var(
            equal_weights, mu, cov,
            n_simulations=100000,
            confidence=0.95,
            seed=42
        ).var

        # 10% 이내로 수렴
        assert abs(var_mc - var_param) / var_param < 0.10


class TestCVaR:
    def test_cvar_greater_than_var(self, sample_data, equal_weights):
        """CVaR >= VaR (Expected Shortfall은 VaR보다 큼)"""
        mu, cov = sample_data

        result = cvar(equal_weights, mu, cov, confidence=0.95)

        assert result.cvar >= result.var

    def test_parametric_vs_montecarlo(self, sample_data, equal_weights):
        mu, cov = sample_data

        cvar_param = cvar(equal_weights, mu, cov, method="parametric")
        cvar_mc = cvar(equal_weights, mu, cov, method="monte_carlo", n_simulations=50000)

        # 두 방법이 유사한 결과
        assert abs(cvar_param.cvar - cvar_mc.cvar) / cvar_param.cvar < 0.15

    def test_higher_confidence_higher_cvar(self, sample_data, equal_weights):
        mu, cov = sample_data

        cvar_95 = cvar(equal_weights, mu, cov, confidence=0.95).cvar
        cvar_99 = cvar(equal_weights, mu, cov, confidence=0.99).cvar

        assert cvar_99 > cvar_95


class TestRiskSummary:
    def test_summary_structure(self, sample_data, equal_weights):
        mu, cov = sample_data

        summary = risk_summary(equal_weights, mu, cov)

        # 모든 필드 존재
        assert summary.volatility > 0
        assert summary.var_95_parametric >= 0
        assert summary.var_99_parametric >= 0
        assert summary.var_95_montecarlo >= 0
        assert summary.var_99_montecarlo >= 0
        assert summary.cvar_95 >= 0
        assert summary.cvar_99 >= 0
        assert summary.max_loss_1d >= 0

    def test_risk_ordering(self, sample_data, equal_weights):
        mu, cov = sample_data

        summary = risk_summary(equal_weights, mu, cov)

        # VaR 95% < VaR 99%
        assert summary.var_95_parametric < summary.var_99_parametric
        assert summary.var_95_montecarlo < summary.var_99_montecarlo

        # CVaR >= VaR
        assert summary.cvar_95 >= summary.var_95_montecarlo * 0.9  # 오차 허용
        assert summary.cvar_99 >= summary.var_99_montecarlo * 0.9

        # Max loss >= 99% VaR
        assert summary.max_loss_1d >= summary.var_99_montecarlo
