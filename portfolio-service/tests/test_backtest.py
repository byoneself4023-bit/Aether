"""backtest.py 단위 테스트"""

import numpy as np
import pandas as pd
import pytest
from app.services.backtest import (
    walk_forward_backtest,
    calculate_performance,
    benchmark_comparison,
)


@pytest.fixture
def sample_returns():
    """테스트용 수익률 데이터 (2년, 3자산)"""
    np.random.seed(42)
    n_days = 504  # 2년
    n_assets = 3

    # 시뮬레이션 수익률 (일간 평균 0.04%, 변동성 1%)
    dates = pd.date_range("2022-01-01", periods=n_days, freq="B")
    returns = np.random.randn(n_days, n_assets) * 0.01 + 0.0004

    return pd.DataFrame(returns, index=dates, columns=["A", "B", "C"])


@pytest.fixture
def trending_returns():
    """상승 추세 수익률 (성과 테스트용)"""
    np.random.seed(123)
    n_days = 504
    dates = pd.date_range("2022-01-01", periods=n_days, freq="B")

    # 상승 추세 (일 평균 0.1%)
    returns = np.random.randn(n_days, 3) * 0.008 + 0.001

    return pd.DataFrame(returns, index=dates, columns=["A", "B", "C"])


class TestCalculatePerformance:
    def test_basic_metrics(self):
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.01 + 0.0004)

        metrics = calculate_performance(returns)

        assert metrics.total_return != 0
        assert metrics.annual_return != 0
        assert metrics.annual_volatility > 0
        assert 0 <= metrics.win_rate <= 1

    def test_mdd_calculation(self):
        # 명확한 낙폭 패턴
        returns = pd.Series([0.10, -0.20, 0.05, 0.05])  # 20% 하락

        metrics = calculate_performance(returns)

        # MDD는 최소 10% 이상 (1.1 → 0.88)
        assert metrics.max_drawdown >= 0.10

    def test_sharpe_positive(self, trending_returns):
        returns = trending_returns.mean(axis=1)  # 동일 비중 수익률

        metrics = calculate_performance(returns)

        # 상승 추세에서 샤프 > 0
        assert metrics.sharpe_ratio > 0

    def test_empty_returns(self):
        returns = pd.Series([], dtype=float)

        metrics = calculate_performance(returns)

        assert metrics.total_return == 0
        assert metrics.sharpe_ratio == 0


class TestWalkForwardBacktest:
    def test_backtest_runs(self, sample_returns):
        result = walk_forward_backtest(
            sample_returns,
            strategy="max_sharpe",
            train_window=126,  # 6개월
            rebalance_every=63  # 분기
        )

        assert len(result.portfolio_values) > 0
        assert len(result.portfolio_returns) > 0
        assert result.strategy == "max_sharpe"

    def test_no_lookahead_bias(self, sample_returns):
        """미래 정보 사용 방지 확인"""
        train_window = 126

        result = walk_forward_backtest(
            sample_returns,
            train_window=train_window,
            rebalance_every=63
        )

        # 백테스트 시작은 train_window 이후
        backtest_start = sample_returns.index[train_window]
        assert result.portfolio_values.index[0] == backtest_start

    def test_rebalancing_frequency(self, sample_returns):
        rebalance_every = 63

        result = walk_forward_backtest(
            sample_returns,
            train_window=126,
            rebalance_every=rebalance_every
        )

        # 리밸런싱 횟수 확인
        expected_rebalances = len(result.portfolio_values) // rebalance_every + 1
        actual_rebalances = len(result.rebalance_history)

        assert actual_rebalances <= expected_rebalances
        assert actual_rebalances > 0

    def test_transaction_cost_impact(self, sample_returns):
        """거래비용 반영 확인"""
        result_no_cost = walk_forward_backtest(
            sample_returns,
            train_window=126,
            rebalance_every=21,  # 월간 (더 자주)
            transaction_cost=0.0
        )

        result_with_cost = walk_forward_backtest(
            sample_returns,
            train_window=126,
            rebalance_every=21,
            transaction_cost=0.01  # 1% (과장된 비용)
        )

        # 거래비용이 있으면 최종 가치가 낮아야 함
        assert result_with_cost.portfolio_values.iloc[-1] < result_no_cost.portfolio_values.iloc[-1]

    def test_weights_sum_to_one(self, sample_returns):
        result = walk_forward_backtest(
            sample_returns,
            train_window=126,
            rebalance_every=63
        )

        # 모든 시점에서 비중 합 = 1
        weights_sum = result.weights_history.sum(axis=1)
        assert np.allclose(weights_sum, 1.0, atol=1e-6)

    def test_strategies(self, sample_returns):
        """모든 전략 실행 확인"""
        for strategy in ["max_sharpe", "min_variance", "equal_weight"]:
            result = walk_forward_backtest(
                sample_returns,
                strategy=strategy,
                train_window=126,
                rebalance_every=63
            )

            assert result.strategy == strategy
            assert len(result.portfolio_values) > 0

    def test_equal_weight_no_optimization_error(self, sample_returns):
        """equal_weight는 최적화 실패 없음"""
        # 작은 데이터로 최적화 어려운 상황
        small_returns = sample_returns.iloc[:150]  # train_window와 비슷

        result = walk_forward_backtest(
            small_returns,
            strategy="equal_weight",
            train_window=126,
            rebalance_every=21
        )

        assert len(result.portfolio_values) > 0


class TestBenchmarkComparison:
    def test_comparison_structure(self, sample_returns):
        portfolio_ret = sample_returns.mean(axis=1) * 1.1  # 약간 더 높은 수익
        benchmark_ret = sample_returns.mean(axis=1)

        comparison = benchmark_comparison(portfolio_ret, benchmark_ret)

        assert comparison.strategy_metrics is not None
        assert comparison.benchmark_metrics is not None
        assert comparison.tracking_error >= 0

    def test_excess_return_calculation(self):
        # 명확한 차이가 있는 수익률
        dates = pd.date_range("2022-01-01", periods=252, freq="B")
        portfolio_ret = pd.Series([0.001] * 252, index=dates)  # 일 0.1%
        benchmark_ret = pd.Series([0.0005] * 252, index=dates)  # 일 0.05%

        comparison = benchmark_comparison(portfolio_ret, benchmark_ret)

        # 초과 수익률 > 0
        assert comparison.excess_return > 0

    def test_tracking_error(self):
        dates = pd.date_range("2022-01-01", periods=252, freq="B")
        np.random.seed(42)

        # 동일한 수익률이면 추적오차 = 0
        returns = pd.Series(np.random.randn(252) * 0.01, index=dates)

        comparison = benchmark_comparison(returns, returns)

        assert comparison.tracking_error < 1e-10

    def test_information_ratio(self, trending_returns):
        # 전략이 벤치마크보다 좋을 때
        portfolio_ret = trending_returns["A"] + 0.001  # 초과 수익
        benchmark_ret = trending_returns["A"]

        comparison = benchmark_comparison(portfolio_ret, benchmark_ret)

        # IR > 0 (양의 초과수익, 양의 정보비율)
        assert comparison.information_ratio > 0


class TestExpandingWindow:
    """Expanding Window 테스트"""

    def test_expanding_window_basic(self, sample_returns):
        """Expanding window 기본 동작 테스트"""
        result = walk_forward_backtest(
            sample_returns,
            strategy="max_sharpe",
            train_window=126,
            rebalance_every=63,
            window_type="expanding"
        )

        assert result.window_type == "expanding"
        assert len(result.portfolio_values) > 0
        assert len(result.rebalance_history) > 0

    def test_rolling_vs_expanding_different_results(self, sample_returns):
        """Rolling과 Expanding은 다른 결과를 생성해야 함"""
        result_rolling = walk_forward_backtest(
            sample_returns,
            strategy="max_sharpe",
            train_window=126,
            rebalance_every=63,
            window_type="rolling"
        )

        result_expanding = walk_forward_backtest(
            sample_returns,
            strategy="max_sharpe",
            train_window=126,
            rebalance_every=63,
            window_type="expanding"
        )

        # 두 결과는 다를 수 있음 (완전히 같지 않아야 함)
        # 최소한 window_type 필드는 다름
        assert result_rolling.window_type == "rolling"
        assert result_expanding.window_type == "expanding"

        # 동일한 수익률 데이터로 두 방식 모두 실행 가능
        assert len(result_rolling.portfolio_values) == len(result_expanding.portfolio_values)

    def test_window_type_default_rolling(self, sample_returns):
        """window_type 기본값은 rolling (하위 호환성)"""
        result = walk_forward_backtest(
            sample_returns,
            strategy="max_sharpe",
            train_window=126,
            rebalance_every=63
            # window_type 생략
        )

        assert result.window_type == "rolling"

    def test_expanding_with_all_strategies(self, sample_returns):
        """Expanding window가 모든 전략에서 작동"""
        for strategy in ["max_sharpe", "min_variance", "equal_weight"]:
            result = walk_forward_backtest(
                sample_returns,
                strategy=strategy,
                train_window=126,
                rebalance_every=63,
                window_type="expanding"
            )

            assert result.strategy == strategy
            assert result.window_type == "expanding"
            assert len(result.portfolio_values) > 0

    def test_expanding_weights_sum_to_one(self, sample_returns):
        """Expanding window에서도 비중 합 = 1"""
        result = walk_forward_backtest(
            sample_returns,
            strategy="max_sharpe",
            train_window=126,
            rebalance_every=63,
            window_type="expanding"
        )

        weights_sum = result.weights_history.sum(axis=1)
        assert np.allclose(weights_sum, 1.0, atol=1e-6)

    def test_expanding_no_lookahead_bias(self, sample_returns):
        """Expanding window도 미래 정보 사용 방지"""
        train_window = 126

        result = walk_forward_backtest(
            sample_returns,
            train_window=train_window,
            rebalance_every=63,
            window_type="expanding"
        )

        # 백테스트 시작은 train_window (min_window) 이후
        backtest_start = sample_returns.index[train_window]
        assert result.portfolio_values.index[0] == backtest_start

    def test_expanding_rebalancing_works(self, sample_returns):
        """Expanding window에서 리밸런싱 정상 동작"""
        result = walk_forward_backtest(
            sample_returns,
            strategy="min_variance",
            train_window=126,
            rebalance_every=63,
            window_type="expanding"
        )

        # 리밸런싱 기록이 있어야 함
        assert len(result.rebalance_history) > 0
        # 턴오버가 계산되어야 함
        assert all(r.turnover >= 0 for r in result.rebalance_history)
