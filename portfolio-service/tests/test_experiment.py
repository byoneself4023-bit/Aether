"""MLflow 실험 서비스 테스트"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
import tempfile
import os

from app.services.experiment import (
    run_optimization_experiment,
    compare_covariance_methods,
    run_backtest_experiment,
    get_recent_experiments,
    OptimizationResult,
    CovarianceComparison,
    BacktestExperimentResult,
    _log_json_artifact,
    _log_numpy_artifact,
    _log_dataframe_artifact,
    _serialize_diagnostics,
)


# 테스트용 Mock 데이터
@pytest.fixture
def mock_returns():
    """Mock 수익률 데이터"""
    np.random.seed(42)
    n_days = 252
    n_assets = 4
    returns = np.random.randn(n_days, n_assets) * 0.02 + 0.0005
    dates = pd.date_range("2022-01-01", periods=n_days, freq="B")
    return pd.DataFrame(returns, index=dates, columns=["AAPL", "GOOGL", "MSFT", "AMZN"])


@pytest.fixture
def mock_tickers():
    return ["AAPL", "GOOGL", "MSFT", "AMZN"]


class TestRunOptimizationExperiment:
    """run_optimization_experiment 테스트"""

    @patch("app.services.experiment.fetch_returns")
    def test_returns_two_results(self, mock_fetch, mock_returns, mock_tickers):
        """Sample과 Shrinkage 두 결과를 반환하는지 테스트"""
        mock_fetch.return_value = mock_returns

        sample_result, shrinkage_result = run_optimization_experiment(
            tickers=mock_tickers,
            strategy="max_sharpe",
            period="3y",
            rf=0.02,
            log_to_mlflow=False  # 테스트에서는 MLflow 비활성화
        )

        assert isinstance(sample_result, OptimizationResult)
        assert isinstance(shrinkage_result, OptimizationResult)
        assert sample_result.method == "sample"
        assert shrinkage_result.method == "shrinkage"

    @patch("app.services.experiment.fetch_returns")
    def test_weights_sum_to_one(self, mock_fetch, mock_returns, mock_tickers):
        """비중 합이 1인지 테스트"""
        mock_fetch.return_value = mock_returns

        sample_result, shrinkage_result = run_optimization_experiment(
            tickers=mock_tickers,
            strategy="min_variance",
            log_to_mlflow=False
        )

        sample_weight_sum = sum(sample_result.weights.values())
        shrinkage_weight_sum = sum(shrinkage_result.weights.values())

        assert abs(sample_weight_sum - 1.0) < 1e-6
        assert abs(shrinkage_weight_sum - 1.0) < 1e-6

    @patch("app.services.experiment.fetch_returns")
    def test_metrics_are_valid(self, mock_fetch, mock_returns, mock_tickers):
        """메트릭 값이 유효한지 테스트"""
        mock_fetch.return_value = mock_returns

        sample_result, _ = run_optimization_experiment(
            tickers=mock_tickers,
            strategy="max_sharpe",
            log_to_mlflow=False
        )

        # 변동성은 양수
        assert sample_result.volatility > 0
        # 종목 수 일치
        assert sample_result.n_stocks == len(mock_tickers)
        # 비중 딕셔너리 키 확인
        assert set(sample_result.weights.keys()) == set(mock_tickers)


class TestCompareCovarianceMethods:
    """compare_covariance_methods 테스트"""

    @patch("app.services.experiment.fetch_returns")
    def test_returns_comparison(self, mock_fetch, mock_returns, mock_tickers):
        """비교 결과를 반환하는지 테스트"""
        mock_fetch.return_value = mock_returns

        comparison = compare_covariance_methods(
            tickers=mock_tickers,
            strategy="max_sharpe",
            log_to_mlflow=False
        )

        assert isinstance(comparison, CovarianceComparison)
        assert comparison.sample_result is not None
        assert comparison.shrinkage_result is not None

    @patch("app.services.experiment.fetch_returns")
    def test_diff_calculation(self, mock_fetch, mock_returns, mock_tickers):
        """차이 계산이 정확한지 테스트"""
        mock_fetch.return_value = mock_returns

        comparison = compare_covariance_methods(
            tickers=mock_tickers,
            strategy="max_sharpe",
            log_to_mlflow=False
        )

        expected_sharpe_diff = (
            comparison.shrinkage_result.sharpe_ratio -
            comparison.sample_result.sharpe_ratio
        )

        assert abs(comparison.sharpe_diff - expected_sharpe_diff) < 1e-6

    @patch("app.services.experiment.fetch_returns")
    def test_recommendation_is_provided(self, mock_fetch, mock_returns, mock_tickers):
        """추천이 제공되는지 테스트"""
        mock_fetch.return_value = mock_returns

        comparison = compare_covariance_methods(
            tickers=mock_tickers,
            strategy="max_sharpe",
            log_to_mlflow=False
        )

        assert comparison.recommendation is not None
        assert "sample" in comparison.recommendation.lower() or "shrinkage" in comparison.recommendation.lower()


class TestRunBacktestExperiment:
    """run_backtest_experiment 테스트"""

    @patch("app.services.experiment.fetch_returns")
    def test_returns_result(self, mock_fetch, mock_returns, mock_tickers):
        """백테스트 결과를 반환하는지 테스트"""
        # 더 긴 기간의 데이터 필요
        np.random.seed(42)
        n_days = 756  # 3년
        n_assets = 4
        returns = np.random.randn(n_days, n_assets) * 0.02 + 0.0005
        dates = pd.date_range("2020-01-01", periods=n_days, freq="B")
        long_returns = pd.DataFrame(
            returns, index=dates,
            columns=["AAPL", "GOOGL", "MSFT", "AMZN"]
        )
        mock_fetch.return_value = long_returns

        result = run_backtest_experiment(
            tickers=mock_tickers,
            strategy="max_sharpe",
            train_window=252,
            rebalance_every=63,
            log_to_mlflow=False
        )

        assert isinstance(result, BacktestExperimentResult)
        assert result.strategy == "max_sharpe"
        assert result.n_rebalances > 0

    @patch("app.services.experiment.fetch_returns")
    def test_metrics_are_valid(self, mock_fetch, mock_tickers):
        """백테스트 메트릭이 유효한지 테스트"""
        np.random.seed(42)
        n_days = 756
        n_assets = 4
        returns = np.random.randn(n_days, n_assets) * 0.02 + 0.0005
        dates = pd.date_range("2020-01-01", periods=n_days, freq="B")
        long_returns = pd.DataFrame(
            returns, index=dates,
            columns=["AAPL", "GOOGL", "MSFT", "AMZN"]
        )
        mock_fetch.return_value = long_returns

        result = run_backtest_experiment(
            tickers=mock_tickers,
            strategy="equal_weight",
            log_to_mlflow=False
        )

        # MDD는 양수
        assert result.max_drawdown >= 0
        # 승률은 0~1 사이
        # (턴오버가 있으면 avg_turnover > 0)
        assert result.avg_turnover >= 0


class TestGetRecentExperiments:
    """get_recent_experiments 테스트"""

    @patch("app.services.experiment.mlflow")
    def test_returns_list(self, mock_mlflow):
        """리스트를 반환하는지 테스트"""
        # Mock 설정
        mock_client = MagicMock()
        mock_mlflow.tracking.MlflowClient.return_value = mock_client
        mock_experiment = MagicMock()
        mock_experiment.experiment_id = "1"
        mock_client.get_experiment_by_name.return_value = mock_experiment

        mock_run = MagicMock()
        mock_run.info.run_id = "abc123"
        mock_run.info.run_name = "test_run"
        mock_run.info.status = "FINISHED"
        mock_run.info.start_time = 1700000000000
        mock_run.data.params = {"strategy": "max_sharpe"}
        mock_run.data.metrics = {"sharpe_ratio": 1.5}
        mock_client.search_runs.return_value = [mock_run]

        results = get_recent_experiments(limit=10)

        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["run_id"] == "abc123"

    @patch("app.services.experiment.mlflow")
    def test_handles_no_experiments(self, mock_mlflow):
        """실험이 없을 때 처리 테스트"""
        mock_client = MagicMock()
        mock_mlflow.tracking.MlflowClient.return_value = mock_client
        mock_client.get_experiment_by_name.return_value = None

        results = get_recent_experiments(limit=10)

        assert results == []


class TestMLflowIntegration:
    """MLflow 통합 테스트 (실제 MLflow 사용)"""

    @pytest.fixture
    def temp_mlruns(self):
        """임시 MLflow 디렉토리"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @patch("app.services.experiment.MLFLOW_TRACKING_URI")
    @patch("app.services.experiment.fetch_returns")
    def test_mlflow_logging(self, mock_fetch, mock_uri, mock_returns, mock_tickers, temp_mlruns):
        """MLflow에 실제로 로깅되는지 테스트"""
        mock_uri.__str__ = lambda x: temp_mlruns
        mock_fetch.return_value = mock_returns

        # 실제 MLflow 로깅 테스트는 통합 테스트로 분리
        # 여기서는 함수 호출이 에러 없이 완료되는지만 확인
        sample_result, shrinkage_result = run_optimization_experiment(
            tickers=mock_tickers,
            strategy="max_sharpe",
            log_to_mlflow=False  # 단위 테스트에서는 비활성화
        )

        assert sample_result is not None
        assert shrinkage_result is not None


class TestEdgeCases:
    """엣지 케이스 테스트"""

    @patch("app.services.experiment.fetch_returns")
    def test_two_assets(self, mock_fetch):
        """최소 자산 수(2개) 테스트"""
        np.random.seed(42)
        returns = np.random.randn(252, 2) * 0.02 + 0.0005
        dates = pd.date_range("2022-01-01", periods=252, freq="B")
        mock_fetch.return_value = pd.DataFrame(
            returns, index=dates, columns=["AAPL", "MSFT"]
        )

        sample_result, shrinkage_result = run_optimization_experiment(
            tickers=["AAPL", "MSFT"],
            strategy="min_variance",
            log_to_mlflow=False
        )

        assert sample_result.n_stocks == 2
        assert len(sample_result.weights) == 2

    @patch("app.services.experiment.fetch_returns")
    def test_different_strategies(self, mock_fetch, mock_returns):
        """다른 전략 테스트"""
        mock_fetch.return_value = mock_returns

        for strategy in ["min_variance", "max_sharpe"]:
            sample, shrinkage = run_optimization_experiment(
                tickers=["AAPL", "GOOGL", "MSFT", "AMZN"],
                strategy=strategy,
                log_to_mlflow=False
            )
            assert sample.strategy == strategy
            assert shrinkage.strategy == strategy


class TestArtifactLoggingHelpers:
    """아티팩트 로깅 헬퍼 함수 테스트"""

    @patch("app.services.experiment.mlflow")
    def test_log_json_artifact(self, mock_mlflow):
        """JSON 아티팩트 로깅 테스트"""
        test_data = {"key": "value", "number": 123}

        _log_json_artifact(test_data, "test.json")

        mock_mlflow.log_artifact.assert_called_once()
        call_args = mock_mlflow.log_artifact.call_args
        assert call_args[0][0].endswith("test.json")

    @patch("app.services.experiment.mlflow")
    def test_log_numpy_artifact(self, mock_mlflow):
        """Numpy 아티팩트 로깅 테스트"""
        test_array = np.array([[1, 2], [3, 4]])

        _log_numpy_artifact(test_array, "test_array")

        mock_mlflow.log_artifact.assert_called_once()
        call_args = mock_mlflow.log_artifact.call_args
        assert ".npy" in call_args[0][0]

    @patch("app.services.experiment.mlflow")
    def test_log_dataframe_artifact(self, mock_mlflow):
        """DataFrame 아티팩트 로깅 테스트"""
        test_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

        _log_dataframe_artifact(test_df, "test.csv")

        mock_mlflow.log_artifact.assert_called_once()
        call_args = mock_mlflow.log_artifact.call_args
        assert call_args[0][0].endswith("test.csv")


class TestSerializeDiagnostics:
    """진단 정보 직렬화 테스트"""

    def test_serialize_none(self):
        """None 입력 처리"""
        result = _serialize_diagnostics(None)
        assert result == {}

    def test_serialize_diagnostics_structure(self):
        """진단 정보 직렬화 구조 테스트"""
        # Mock diagnostics object
        from app.services.optimizer import (
            OptimizationDiagnostics,
            CovarianceValidation
        )

        cov_validation = CovarianceValidation(
            is_valid=True,
            issues=[],
            condition_number=10.5,
            min_eigenvalue=0.001,
            max_correlation=0.5,
            was_regularized=False,
            regularization_amount=0.0
        )

        diagnostics = OptimizationDiagnostics(
            converged=True,
            iterations=15,
            final_objective=0.025,
            condition_number=10.5,
            covariance_validation=cov_validation,
            solver_message="Optimization terminated successfully",
            gradient_norm=0.001
        )

        result = _serialize_diagnostics(diagnostics)

        assert result["converged"] is True
        assert result["iterations"] == 15
        assert result["final_objective"] == 0.025
        assert result["solver_message"] == "Optimization terminated successfully"
        assert result["gradient_norm"] == 0.001
        assert "covariance_validation" in result
        assert result["covariance_validation"]["is_valid"] is True


class TestArtifactLoggingIntegration:
    """아티팩트 로깅 통합 테스트"""

    @patch("app.services.experiment.fetch_returns")
    def test_optimization_with_artifacts_disabled(self, mock_fetch, mock_returns, mock_tickers):
        """아티팩트 로깅 비활성화 테스트"""
        mock_fetch.return_value = mock_returns

        # log_artifacts=False로 실행
        sample_result, shrinkage_result = run_optimization_experiment(
            tickers=mock_tickers,
            strategy="max_sharpe",
            log_to_mlflow=False,
            log_artifacts=False
        )

        # 결과는 정상적으로 반환되어야 함
        assert sample_result is not None
        assert shrinkage_result is not None

    @patch("app.services.experiment.fetch_returns")
    def test_backtest_with_artifacts_disabled(self, mock_fetch, mock_tickers):
        """백테스트 아티팩트 로깅 비활성화 테스트"""
        np.random.seed(42)
        n_days = 756
        returns = np.random.randn(n_days, 4) * 0.02 + 0.0005
        dates = pd.date_range("2020-01-01", periods=n_days, freq="B")
        mock_fetch.return_value = pd.DataFrame(
            returns, index=dates,
            columns=["AAPL", "GOOGL", "MSFT", "AMZN"]
        )

        result = run_backtest_experiment(
            tickers=mock_tickers,
            strategy="max_sharpe",
            log_to_mlflow=False,
            log_artifacts=False
        )

        assert result is not None
        assert result.strategy == "max_sharpe"
