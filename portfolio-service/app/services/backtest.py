"""Walk-forward 백테스트 서비스"""

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from dataclasses import dataclass, field
from typing import Literal, List
from app.services.optimizer import optimize_min_variance, optimize_max_sharpe
from app.utils.covariance import shrinkage_covariance


@dataclass
class PerformanceMetrics:
    """성과 메트릭"""
    total_return: float  # 누적 수익률
    annual_return: float  # 연환산 수익률 (CAGR)
    annual_volatility: float  # 연환산 변동성
    sharpe_ratio: float  # 샤프 비율
    max_drawdown: float  # 최대 낙폭 (MDD)
    calmar_ratio: float  # 칼마 비율 (CAGR / MDD)
    avg_turnover: float  # 평균 턴오버
    win_rate: float  # 승률 (양수 수익 일수 비율)
    n_rebalances: int  # 리밸런싱 횟수


@dataclass
class RebalanceRecord:
    """리밸런싱 기록"""
    date: pd.Timestamp
    weights: NDArray[np.float64]
    turnover: float


@dataclass
class BacktestResult:
    """백테스트 결과"""
    portfolio_values: pd.Series  # 일별 포트폴리오 가치
    portfolio_returns: pd.Series  # 일별 수익률
    rebalance_history: List[RebalanceRecord]  # 리밸런싱 기록
    metrics: PerformanceMetrics  # 성과 메트릭
    strategy: str
    weights_history: pd.DataFrame  # 시점별 비중 (date x asset)
    window_type: str = "rolling"  # "rolling" or "expanding"


@dataclass
class BenchmarkComparison:
    """벤치마크 비교 결과"""
    strategy_metrics: PerformanceMetrics
    benchmark_metrics: PerformanceMetrics
    excess_return: float  # 초과 수익률
    tracking_error: float  # 추적 오차
    information_ratio: float  # 정보 비율


def calculate_performance(
    portfolio_returns: pd.Series,
    rebalance_turnovers: List[float] = None,
    rf: float = 0.0,
    trading_days: int = 252
) -> PerformanceMetrics:
    """
    포트폴리오 성과 메트릭 계산

    Args:
        portfolio_returns: 일별 수익률 시리즈
        rebalance_turnovers: 리밸런싱별 턴오버 리스트
        rf: 무위험 이자율 (연율)
        trading_days: 연간 거래일 수

    Returns:
        PerformanceMetrics 객체
    """
    returns = portfolio_returns.dropna()
    n_days = len(returns)

    if n_days == 0:
        return PerformanceMetrics(
            total_return=0, annual_return=0, annual_volatility=0,
            sharpe_ratio=0, max_drawdown=0, calmar_ratio=0,
            avg_turnover=0, win_rate=0, n_rebalances=0
        )

    # 누적 수익률
    cumulative = (1 + returns).cumprod()
    total_return = float(cumulative.iloc[-1] - 1)

    # 연환산 수익률 (CAGR)
    n_years = n_days / trading_days
    annual_return = float((1 + total_return) ** (1 / n_years) - 1) if n_years > 0 else 0

    # 연환산 변동성
    annual_volatility = float(returns.std() * np.sqrt(trading_days))

    # 샤프 비율
    excess_return = annual_return - rf
    sharpe_ratio = excess_return / annual_volatility if annual_volatility > 0 else 0

    # 최대 낙폭 (MDD)
    rolling_max = cumulative.expanding().max()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = float(abs(drawdown.min()))

    # 칼마 비율
    calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0

    # 턴오버
    avg_turnover = float(np.mean(rebalance_turnovers)) if rebalance_turnovers else 0
    n_rebalances = len(rebalance_turnovers) if rebalance_turnovers else 0

    # 승률
    win_rate = float((returns > 0).sum() / n_days) if n_days > 0 else 0

    return PerformanceMetrics(
        total_return=total_return,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        calmar_ratio=calmar_ratio,
        avg_turnover=avg_turnover,
        win_rate=win_rate,
        n_rebalances=n_rebalances
    )


def walk_forward_backtest(
    returns_df: pd.DataFrame,
    strategy: Literal["max_sharpe", "min_variance", "equal_weight"] = "max_sharpe",
    train_window: int = 252,
    rebalance_every: int = 63,
    transaction_cost: float = 0.001,
    rf: float = 0.02,
    use_shrinkage: bool = True,
    window_type: Literal["rolling", "expanding"] = "rolling"
) -> BacktestResult:
    """
    Walk-forward 백테스트 실행

    미래 정보 사용을 방지하는 시간순 분리 백테스트.
    train_window로 학습 후 rebalance_every 주기로 리밸런싱.

    Args:
        returns_df: 일별 수익률 DataFrame (date x assets)
        strategy: 최적화 전략 ("max_sharpe", "min_variance", "equal_weight")
        train_window: 학습 기간 (거래일) - rolling 모드에서는 윈도우 크기, expanding 모드에서는 최소 크기
        rebalance_every: 리밸런싱 주기 (거래일)
        transaction_cost: 편도 거래비용 (0.001 = 0.1%)
        rf: 무위험 이자율 (연율)
        use_shrinkage: Shrinkage 공분산 사용 여부
        window_type: 윈도우 타입
            - "rolling": 고정 크기 윈도우 (기본값, 하위 호환성)
            - "expanding": 시작점 고정, 끝점만 확장 (학습 데이터 누적)

    Returns:
        BacktestResult 객체
    """
    returns_df = returns_df.copy()
    n_assets = returns_df.shape[1]
    assets = returns_df.columns.tolist()

    # 결과 저장
    portfolio_values = []
    portfolio_returns = []
    rebalance_history = []
    weights_records = []

    # 초기 상태
    current_weights = np.ones(n_assets) / n_assets  # 동일 비중 시작
    portfolio_value = 1.0

    # 일별 무위험 이자율
    daily_rf = rf / 252

    # 백테스트 시작점 (train_window 이후)
    start_idx = train_window
    dates = returns_df.index[start_idx:]

    for i, date in enumerate(dates):
        current_idx = start_idx + i

        # 리밸런싱 시점 체크
        should_rebalance = (i % rebalance_every == 0)

        if should_rebalance:
            # 학습 데이터 추출
            if window_type == "expanding":
                # Expanding: 처음부터 현재까지 (min_window=train_window 보장됨)
                train_returns = returns_df.iloc[:current_idx].values
            else:
                # Rolling: 고정 크기 윈도우 (기본)
                train_start = current_idx - train_window
                train_returns = returns_df.iloc[train_start:current_idx].values

            # 기대수익률 & 공분산 추정
            mu = np.mean(train_returns, axis=0)
            if use_shrinkage:
                cov = shrinkage_covariance(train_returns)
            else:
                cov = np.cov(train_returns, rowvar=False)

            # 최적화
            try:
                if strategy == "max_sharpe":
                    result = optimize_max_sharpe(mu, cov, daily_rf)
                    new_weights = result.weights
                elif strategy == "min_variance":
                    result = optimize_min_variance(mu, cov)
                    new_weights = result.weights
                else:  # equal_weight
                    new_weights = np.ones(n_assets) / n_assets
            except ValueError:
                # 최적화 실패 시 이전 비중 유지
                new_weights = current_weights

            # 턴오버 계산 (비중 변화의 절대값 합)
            turnover = float(np.sum(np.abs(new_weights - current_weights)))

            # 거래비용 차감 (양방향)
            cost = turnover * transaction_cost
            portfolio_value *= (1 - cost)

            # 리밸런싱 기록
            rebalance_history.append(RebalanceRecord(
                date=date,
                weights=new_weights.copy(),
                turnover=turnover
            ))

            current_weights = new_weights

        # 비중 기록
        weights_records.append({
            "date": date,
            **{asset: w for asset, w in zip(assets, current_weights)}
        })

        # 일별 수익률 계산
        daily_returns = returns_df.loc[date].values
        portfolio_daily_return = float(current_weights @ daily_returns)

        # 포트폴리오 가치 업데이트
        portfolio_value *= (1 + portfolio_daily_return)

        # 드리프트로 인한 비중 변화 반영
        asset_values = current_weights * (1 + daily_returns)
        current_weights = asset_values / asset_values.sum()

        portfolio_values.append(portfolio_value)
        portfolio_returns.append(portfolio_daily_return)

    # 결과 정리
    portfolio_values_series = pd.Series(portfolio_values, index=dates, name="portfolio_value")
    portfolio_returns_series = pd.Series(portfolio_returns, index=dates, name="portfolio_return")
    weights_df = pd.DataFrame(weights_records).set_index("date")

    # 성과 계산
    turnovers = [r.turnover for r in rebalance_history]
    metrics = calculate_performance(portfolio_returns_series, turnovers, rf)

    return BacktestResult(
        portfolio_values=portfolio_values_series,
        portfolio_returns=portfolio_returns_series,
        rebalance_history=rebalance_history,
        metrics=metrics,
        strategy=strategy,
        weights_history=weights_df,
        window_type=window_type
    )


def benchmark_comparison(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    rf: float = 0.02
) -> BenchmarkComparison:
    """
    전략 vs 벤치마크 비교 분석

    Args:
        portfolio_returns: 전략 일별 수익률
        benchmark_returns: 벤치마크 일별 수익률
        rf: 무위험 이자율 (연율)

    Returns:
        BenchmarkComparison 객체
    """
    # 공통 기간 추출
    common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
    port_ret = portfolio_returns.loc[common_idx]
    bench_ret = benchmark_returns.loc[common_idx]

    # 각각의 성과 메트릭
    strategy_metrics = calculate_performance(port_ret, rf=rf)
    benchmark_metrics = calculate_performance(bench_ret, rf=rf)

    # 초과 수익률
    excess_return = strategy_metrics.annual_return - benchmark_metrics.annual_return

    # 추적 오차 (Tracking Error)
    active_returns = port_ret - bench_ret
    tracking_error = float(active_returns.std() * np.sqrt(252))

    # 정보 비율 (Information Ratio)
    information_ratio = excess_return / tracking_error if tracking_error > 0 else 0

    return BenchmarkComparison(
        strategy_metrics=strategy_metrics,
        benchmark_metrics=benchmark_metrics,
        excess_return=excess_return,
        tracking_error=tracking_error,
        information_ratio=information_ratio
    )
