"""optimizer.py 단위 테스트"""

import numpy as np
import pytest
from app.services.optimizer import (
    optimize_min_variance,
    optimize_max_sharpe,
    optimize_min_variance_with_diagnostics,
    optimize_max_sharpe_with_diagnostics,
    efficient_frontier,
    portfolio_metrics,
    validate_covariance_matrix,
    regularize_covariance,
    CovarianceValidation,
    OptimizationDiagnostics,
    OptimizationResult,
)
from app.utils.covariance import (
    sample_covariance,
    shrinkage_covariance,
    annualize,
)


# 테스트용 데이터 (3자산)
@pytest.fixture
def sample_data():
    """테스트용 기대수익률/공분산"""
    mu = np.array([0.10, 0.15, 0.12])  # 연 10%, 15%, 12%
    cov = np.array([
        [0.04, 0.006, 0.010],   # σ1=20%, 상관계수 반영
        [0.006, 0.09, 0.015],   # σ2=30%
        [0.010, 0.015, 0.0625]  # σ3=25%
    ])
    return mu, cov


class TestPortfolioMetrics:
    def test_equal_weight(self, sample_data):
        mu, cov = sample_data
        w = np.array([1/3, 1/3, 1/3])

        result = portfolio_metrics(w, mu, cov, rf=0.02)

        assert np.isclose(result.expected_return, np.mean(mu))
        assert result.volatility > 0
        assert result.sharpe_ratio > 0

    def test_single_asset(self, sample_data):
        mu, cov = sample_data
        w = np.array([1.0, 0.0, 0.0])

        result = portfolio_metrics(w, mu, cov)

        assert np.isclose(result.expected_return, 0.10)
        assert np.isclose(result.volatility, 0.20)


class TestMinVariance:
    def test_global_mvp(self, sample_data):
        mu, cov = sample_data

        result = optimize_min_variance(mu, cov)

        # 비중 합 = 1
        assert np.isclose(np.sum(result.weights), 1.0)
        # 모든 비중 >= 0
        assert np.all(result.weights >= -1e-6)
        # 변동성이 개별 자산보다 낮아야 함
        min_individual_vol = np.sqrt(np.min(np.diag(cov)))
        assert result.volatility <= min_individual_vol + 0.01

    def test_with_target_return(self, sample_data):
        mu, cov = sample_data
        target = 0.12

        result = optimize_min_variance(mu, cov, target_return=target)

        assert np.isclose(result.expected_return, target, atol=1e-4)
        assert np.isclose(np.sum(result.weights), 1.0)


class TestMaxSharpe:
    def test_msr(self, sample_data):
        mu, cov = sample_data
        rf = 0.02

        result = optimize_max_sharpe(mu, cov, rf)

        assert np.isclose(np.sum(result.weights), 1.0)
        assert np.all(result.weights >= -1e-6)
        assert result.sharpe_ratio > 0

        # MSR은 MVP보다 높은 샤프 비율을 가져야 함
        mvp = optimize_min_variance(mu, cov)
        mvp_sharpe = (mvp.expected_return - rf) / mvp.volatility
        assert result.sharpe_ratio >= mvp_sharpe - 1e-4


class TestEfficientFrontier:
    def test_frontier_shape(self, sample_data):
        mu, cov = sample_data

        frontier = efficient_frontier(mu, cov, n_points=10)

        assert len(frontier.returns) <= 10
        assert len(frontier.returns) == len(frontier.volatilities)
        assert frontier.weights.shape[0] == len(frontier.returns)

    def test_frontier_monotonicity(self, sample_data):
        mu, cov = sample_data

        frontier = efficient_frontier(mu, cov, n_points=20)

        # 수익률은 증가해야 함
        assert np.all(np.diff(frontier.returns) >= -1e-6)


class TestCovariance:
    def test_sample_covariance(self):
        np.random.seed(42)
        returns = np.random.randn(100, 3) * 0.01  # 100일, 3자산

        cov = sample_covariance(returns)

        assert cov.shape == (3, 3)
        # 대칭 행렬
        assert np.allclose(cov, cov.T)
        # 양정치
        assert np.all(np.linalg.eigvalsh(cov) > 0)

    def test_shrinkage_covariance(self):
        np.random.seed(42)
        returns = np.random.randn(50, 10) * 0.01  # N > T/2 상황

        cov = shrinkage_covariance(returns)

        assert cov.shape == (10, 10)
        assert np.allclose(cov, cov.T)
        assert np.all(np.linalg.eigvalsh(cov) > 0)

    def test_annualize(self):
        daily_cov = np.array([[0.0001, 0.00005], [0.00005, 0.0002]])

        annual_cov = annualize(daily_cov, trading_days=252)

        assert np.allclose(annual_cov, daily_cov * 252)


class TestCovarianceValidation:
    """공분산 행렬 검증 테스트"""

    def test_valid_covariance(self, sample_data):
        """정상적인 공분산 행렬"""
        _, cov = sample_data

        result = validate_covariance_matrix(cov)

        assert result.is_valid
        assert len(result.issues) == 0
        assert result.condition_number > 0
        assert result.min_eigenvalue > 0

    def test_non_symmetric_matrix(self):
        """비대칭 행렬 탐지"""
        cov = np.array([
            [0.04, 0.01, 0.02],
            [0.015, 0.09, 0.03],  # (0,1) != (1,0)
            [0.02, 0.03, 0.0625]
        ])

        result = validate_covariance_matrix(cov)

        assert not result.is_valid
        assert any("symmetric" in issue.lower() for issue in result.issues)

    def test_negative_eigenvalue(self):
        """음의 고유값 탐지"""
        # 의도적으로 non-PSD 행렬 생성
        cov = np.array([
            [1, 2, 0],
            [2, 1, 0],
            [0, 0, 1]
        ])

        result = validate_covariance_matrix(cov)

        assert not result.is_valid
        assert result.min_eigenvalue < 0

    def test_near_perfect_correlation(self):
        """완전 상관(ρ≈1) 탐지"""
        # 두 자산이 거의 완전 상관 (ρ = 0.9999)
        # σ1=0.2, σ2=0.3, cov12 = ρ * σ1 * σ2 = 0.9999 * 0.2 * 0.3 = 0.05999
        cov = np.array([
            [0.04, 0.05999, 0.01],   # σ1=0.2
            [0.05999, 0.09, 0.015],  # σ2=0.3
            [0.01, 0.015, 0.0625]    # σ3=0.25
        ])

        result = validate_covariance_matrix(cov)

        assert not result.is_valid
        assert result.max_correlation > 0.999
        assert any("correlation" in issue.lower() for issue in result.issues)

    def test_ill_conditioned_matrix(self):
        """조건수가 매우 큰 행렬 탐지"""
        # 매우 다른 규모의 분산
        cov = np.array([
            [1e-10, 0],
            [0, 1e10]
        ])

        result = validate_covariance_matrix(cov, max_condition_number=1e12)

        assert not result.is_valid
        assert result.condition_number > 1e12


class TestCovarianceRegularization:
    """공분산 행렬 정규화 테스트"""

    def test_regularize_non_psd(self):
        """non-PSD 행렬 정규화"""
        # 음의 고유값을 가진 행렬
        cov = np.array([
            [1, 2, 0],
            [2, 1, 0],
            [0, 0, 1]
        ])

        validation = validate_covariance_matrix(cov)
        assert not validation.is_valid

        cov_reg, new_validation = regularize_covariance(cov, validation)

        # 정규화 후 양정치
        assert new_validation.min_eigenvalue >= 0
        assert new_validation.was_regularized

    def test_regularize_ill_conditioned(self):
        """조건수 개선"""
        cov = np.array([
            [1e-10, 0],
            [0, 1]
        ])

        validation = validate_covariance_matrix(cov)
        cov_reg, new_validation = regularize_covariance(
            cov, validation, target_condition_number=1e6
        )

        # 조건수 개선 확인
        assert new_validation.condition_number < validation.condition_number

    def test_regularization_preserves_symmetry(self):
        """정규화 후 대칭성 유지"""
        cov = np.array([
            [1, 2, 0],
            [2, 1, 0],
            [0, 0, 1]
        ])

        validation = validate_covariance_matrix(cov)
        cov_reg, _ = regularize_covariance(cov, validation)

        assert np.allclose(cov_reg, cov_reg.T)


class TestOptimizationWithBadCovariance:
    """문제 있는 공분산으로 최적화 테스트"""

    def test_auto_regularize_on_invalid_cov(self):
        """자동 정규화로 최적화 성공"""
        mu = np.array([0.10, 0.15, 0.12])
        # near-perfect correlation (ρ > 0.999)
        cov = np.array([
            [0.04, 0.05999, 0.01],
            [0.05999, 0.09, 0.015],
            [0.01, 0.015, 0.0625]
        ])

        # auto_regularize=True (기본값)이면 정규화 후 최적화
        result = optimize_min_variance(mu, cov, auto_regularize=True)

        assert np.isclose(np.sum(result.weights), 1.0)
        assert np.all(result.weights >= -1e-6)

    def test_error_when_auto_regularize_disabled(self):
        """자동 정규화 비활성화 시 에러"""
        mu = np.array([0.10, 0.15, 0.12])
        # near-perfect correlation (ρ > 0.999)
        cov = np.array([
            [0.04, 0.05999, 0.01],
            [0.05999, 0.09, 0.015],
            [0.01, 0.015, 0.0625]
        ])

        with pytest.raises(ValueError, match="Invalid covariance"):
            optimize_min_variance(mu, cov, auto_regularize=False)

    def test_max_sharpe_with_bad_cov(self):
        """max_sharpe도 자동 정규화 동작"""
        mu = np.array([0.10, 0.15, 0.12])
        # near-perfect correlation (ρ > 0.999)
        cov = np.array([
            [0.04, 0.05999, 0.01],
            [0.05999, 0.09, 0.015],
            [0.01, 0.015, 0.0625]
        ])

        result = optimize_max_sharpe(mu, cov, rf=0.02, auto_regularize=True)

        assert np.isclose(np.sum(result.weights), 1.0)
        assert result.sharpe_ratio > 0


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_two_assets(self):
        """2개 자산 최적화"""
        mu = np.array([0.10, 0.15])
        cov = np.array([
            [0.04, 0.01],
            [0.01, 0.09]
        ])

        result = optimize_min_variance(mu, cov)

        assert np.isclose(np.sum(result.weights), 1.0)
        assert len(result.weights) == 2

    def test_identical_assets(self):
        """동일 자산(같은 수익률/변동성) 최적화"""
        mu = np.array([0.10, 0.10, 0.10])
        cov = np.array([
            [0.04, 0.02, 0.02],
            [0.02, 0.04, 0.02],
            [0.02, 0.02, 0.04]
        ])

        result = optimize_min_variance(mu, cov)

        # 동일 자산이면 동일 비중에 가까워야 함
        assert np.isclose(np.sum(result.weights), 1.0)
        # 각 비중이 크게 다르지 않아야 함 (완전 동일일 필요는 없음)
        assert np.std(result.weights) < 0.3


class TestOptimizationWithDiagnostics:
    """진단 정보 포함 최적화 테스트"""

    def test_min_variance_with_diagnostics(self, sample_data):
        """min_variance 진단 정보 확인"""
        mu, cov = sample_data

        result = optimize_min_variance_with_diagnostics(mu, cov)

        # OptimizationResult 타입 확인
        assert isinstance(result, OptimizationResult)
        assert isinstance(result.metrics.weights, np.ndarray)
        assert isinstance(result.diagnostics, OptimizationDiagnostics)

        # metrics 검증
        assert np.isclose(np.sum(result.metrics.weights), 1.0)
        assert result.metrics.volatility > 0

        # diagnostics 검증 (np.bool_ 호환)
        assert result.diagnostics.converged == True
        assert result.diagnostics.iterations > 0
        assert result.diagnostics.condition_number > 0
        assert result.diagnostics.covariance_validation is not None
        assert result.diagnostics.covariance_validation.is_valid

    def test_max_sharpe_with_diagnostics(self, sample_data):
        """max_sharpe 진단 정보 확인"""
        mu, cov = sample_data
        rf = 0.02

        result = optimize_max_sharpe_with_diagnostics(mu, cov, rf)

        # OptimizationResult 타입 확인
        assert isinstance(result, OptimizationResult)

        # metrics 검증
        assert np.isclose(np.sum(result.metrics.weights), 1.0)
        assert result.metrics.sharpe_ratio > 0

        # diagnostics 검증 (np.bool_ 호환)
        assert result.diagnostics.converged == True
        assert result.diagnostics.iterations > 0
        assert len(result.diagnostics.solver_message) > 0

    def test_diagnostics_with_bad_covariance(self):
        """문제 있는 공분산에서 진단 정보 확인"""
        mu = np.array([0.10, 0.15, 0.12])
        # near-perfect correlation
        cov = np.array([
            [0.04, 0.05999, 0.01],
            [0.05999, 0.09, 0.015],
            [0.01, 0.015, 0.0625]
        ])

        result = optimize_min_variance_with_diagnostics(mu, cov, auto_regularize=True)

        # 정규화 적용 확인 (was_regularized 속성 사용)
        assert result.diagnostics.covariance_validation.was_regularized == True
        assert result.diagnostics.converged == True

    def test_diagnostics_gradient_norm(self, sample_data):
        """gradient norm 값 확인"""
        mu, cov = sample_data

        result = optimize_min_variance_with_diagnostics(mu, cov)

        # gradient_norm은 수렴 시 작은 값이어야 함
        if result.diagnostics.gradient_norm is not None:
            assert result.diagnostics.gradient_norm >= 0

    def test_diagnostics_objective_value(self, sample_data):
        """목적 함수 값 확인"""
        mu, cov = sample_data

        result = optimize_min_variance_with_diagnostics(mu, cov)

        # 최소 분산의 목적함수는 분산 값
        # w @ cov @ w 는 양수여야 함
        assert result.diagnostics.final_objective > 0
        # 계산된 분산과 일치해야 함
        expected_var = result.metrics.weights @ cov @ result.metrics.weights
        assert np.isclose(result.diagnostics.final_objective, expected_var, rtol=1e-4)

    def test_diagnostics_matches_original_result(self, sample_data):
        """진단 버전과 기존 버전의 결과 일치 확인"""
        mu, cov = sample_data
        rf = 0.02

        # 기존 방식
        original = optimize_min_variance(mu, cov)

        # 진단 정보 포함 방식
        with_diag = optimize_min_variance_with_diagnostics(mu, cov)

        # 결과 일치 확인
        assert np.allclose(original.weights, with_diag.metrics.weights, atol=1e-6)
        assert np.isclose(original.volatility, with_diag.metrics.volatility, atol=1e-6)
        assert np.isclose(original.expected_return, with_diag.metrics.expected_return, atol=1e-6)

    def test_max_sharpe_diagnostics_matches(self, sample_data):
        """max_sharpe 진단 버전과 기존 버전의 결과 일치 확인"""
        mu, cov = sample_data
        rf = 0.02

        original = optimize_max_sharpe(mu, cov, rf)
        with_diag = optimize_max_sharpe_with_diagnostics(mu, cov, rf)

        assert np.allclose(original.weights, with_diag.metrics.weights, atol=1e-6)
        assert np.isclose(original.sharpe_ratio, with_diag.metrics.sharpe_ratio, atol=1e-4)
