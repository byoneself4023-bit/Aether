"""MLflow 실험 추적 서비스"""

import mlflow
import numpy as np
import pandas as pd
import json
import tempfile
import os
from dataclasses import dataclass, asdict
from typing import Optional, Literal, Any
from datetime import datetime

from app.services.data import fetch_returns, get_returns_and_covariance
from app.services.optimizer import (
    optimize_min_variance,
    optimize_max_sharpe,
    optimize_min_variance_with_diagnostics,
    optimize_max_sharpe_with_diagnostics,
    efficient_frontier,
)
from app.services.backtest import walk_forward_backtest
from app.utils.covariance import shrinkage_covariance, sample_covariance
from app.config import get_settings
from app.middleware.logging import logger

settings = get_settings()

# MLflow 설정
MLFLOW_TRACKING_URI = settings.mlflow_tracking_uri
EXPERIMENT_NAME = settings.mlflow_experiment_name


def _init_mlflow():
    """MLflow 초기화"""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)


def _log_json_artifact(data: dict, filename: str, artifact_path: str = ""):
    """JSON 아티팩트 로깅"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        mlflow.log_artifact(filepath, artifact_path)


def _log_numpy_artifact(arr: np.ndarray, filename: str, artifact_path: str = ""):
    """Numpy 배열 아티팩트 로깅"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        np.save(filepath, arr)
        mlflow.log_artifact(filepath + ".npy" if not filepath.endswith(".npy") else filepath, artifact_path)


def _log_dataframe_artifact(df: pd.DataFrame, filename: str, artifact_path: str = ""):
    """DataFrame 아티팩트 로깅 (CSV)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        df.to_csv(filepath, index=True)
        mlflow.log_artifact(filepath, artifact_path)


def _serialize_diagnostics(diagnostics) -> dict:
    """OptimizationDiagnostics를 직렬화 가능한 딕셔너리로 변환"""
    if diagnostics is None:
        return {}

    return {
        "converged": bool(diagnostics.converged),
        "iterations": int(diagnostics.iterations),
        "final_objective": float(diagnostics.final_objective),
        "condition_number": float(diagnostics.condition_number),
        "solver_message": str(diagnostics.solver_message),
        "gradient_norm": float(diagnostics.gradient_norm) if diagnostics.gradient_norm else None,
        "covariance_validation": {
            "is_valid": bool(diagnostics.covariance_validation.is_valid),
            "condition_number": float(diagnostics.covariance_validation.condition_number),
            "min_eigenvalue": float(diagnostics.covariance_validation.min_eigenvalue),
            "max_correlation": float(diagnostics.covariance_validation.max_correlation),
            "issues": list(diagnostics.covariance_validation.issues),
            "was_regularized": bool(diagnostics.covariance_validation.was_regularized),
            "regularization_amount": float(diagnostics.covariance_validation.regularization_amount)
        }
    }


@dataclass
class OptimizationResult:
    """최적화 결과"""
    method: str  # "sample" or "shrinkage"
    strategy: str
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    n_stocks: int
    run_id: Optional[str] = None


@dataclass
class CovarianceComparison:
    """Sample vs Shrinkage 비교 결과"""
    sample_result: OptimizationResult
    shrinkage_result: OptimizationResult
    sharpe_diff: float  # shrinkage - sample
    volatility_diff: float
    return_diff: float
    recommendation: str
    run_id: Optional[str] = None


@dataclass
class BacktestExperimentResult:
    """백테스트 실험 결과"""
    strategy: str
    use_shrinkage: bool
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    avg_turnover: float
    n_rebalances: int
    run_id: Optional[str] = None


def run_optimization_experiment(
    tickers: list[str],
    strategy: Literal["min_variance", "max_sharpe"] = "max_sharpe",
    period: str = "3y",
    rf: float = 0.02,
    log_to_mlflow: bool = True,
    log_artifacts: bool = True
) -> tuple[OptimizationResult, OptimizationResult]:
    """
    Sample vs Shrinkage 공분산으로 최적화 실험 실행

    Args:
        tickers: 종목 티커 리스트
        strategy: 최적화 전략
        period: 데이터 기간
        rf: 무위험 이자율
        log_to_mlflow: MLflow 로깅 여부
        log_artifacts: 아티팩트 로깅 여부 (weights.json, covariance.npy, 등)

    Returns:
        (sample_result, shrinkage_result) 튜플
    """
    if log_to_mlflow:
        _init_mlflow()

    # 수익률 데이터 수집
    returns_df = fetch_returns(tickers, period)
    returns = returns_df.values
    mu = np.mean(returns, axis=0)
    daily_rf = rf / 252

    results = []

    for method in ["sample", "shrinkage"]:
        # 공분산 계산
        if method == "sample":
            cov = sample_covariance(returns)
        else:
            cov = shrinkage_covariance(returns)

        # 최적화 (진단 정보 포함)
        if strategy == "min_variance":
            full_result = optimize_min_variance_with_diagnostics(mu, cov)
        else:
            full_result = optimize_max_sharpe_with_diagnostics(mu, cov, daily_rf)

        opt_result = full_result.metrics
        diagnostics = full_result.diagnostics

        # 연율화 메트릭
        annual_return = float(opt_result.expected_return * 252)
        annual_vol = float(opt_result.volatility * np.sqrt(252))
        sharpe = (annual_return - rf) / annual_vol if annual_vol > 0 else 0

        # 비중 딕셔너리
        weights_dict = {
            ticker: round(float(w), 6)
            for ticker, w in zip(tickers, opt_result.weights)
        }

        run_id = None
        if log_to_mlflow:
            with mlflow.start_run(run_name=f"{strategy}_{method}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # 파라미터 로깅
                mlflow.log_param("method", method)
                mlflow.log_param("strategy", strategy)
                mlflow.log_param("period", period)
                mlflow.log_param("n_stocks", len(tickers))
                mlflow.log_param("tickers", ",".join(tickers))
                mlflow.log_param("rf", rf)

                # 메트릭 로깅
                mlflow.log_metric("expected_return", annual_return)
                mlflow.log_metric("volatility", annual_vol)
                mlflow.log_metric("sharpe_ratio", sharpe)

                # 진단 메트릭 로깅
                mlflow.log_metric("converged", 1 if diagnostics.converged else 0)
                mlflow.log_metric("iterations", diagnostics.iterations)
                mlflow.log_metric("condition_number", diagnostics.condition_number)

                # 비중 로깅 (상위 5개)
                sorted_weights = sorted(weights_dict.items(), key=lambda x: x[1], reverse=True)
                for i, (ticker, weight) in enumerate(sorted_weights[:5]):
                    mlflow.log_metric(f"weight_{ticker}", weight)

                # 아티팩트 로깅
                if log_artifacts:
                    # 1. 입력 파라미터 (input_params.json)
                    input_params = {
                        "tickers": tickers,
                        "strategy": strategy,
                        "method": method,
                        "period": period,
                        "rf": rf,
                        "n_stocks": len(tickers),
                        "timestamp": datetime.now().isoformat()
                    }
                    _log_json_artifact(input_params, "input_params.json")

                    # 2. 최적화 비중 (weights.json)
                    _log_json_artifact(weights_dict, "weights.json")

                    # 3. 공분산 행렬 (covariance.npy)
                    _log_numpy_artifact(cov, "covariance")

                    # 4. 기대수익률 벡터 (expected_returns.npy)
                    _log_numpy_artifact(mu, "expected_returns")

                    # 5. 진단 정보 (diagnostics.json)
                    diagnostics_dict = _serialize_diagnostics(diagnostics)
                    _log_json_artifact(diagnostics_dict, "diagnostics.json")

                    # 6. 수익률 데이터 (returns.csv)
                    _log_dataframe_artifact(returns_df, "returns.csv")

                    logger.info(
                        "mlflow_artifacts_logged",
                        run_id=mlflow.active_run().info.run_id,
                        artifacts=["input_params.json", "weights.json", "covariance.npy",
                                   "expected_returns.npy", "diagnostics.json", "returns.csv"]
                    )

                run_id = mlflow.active_run().info.run_id

        results.append(OptimizationResult(
            method=method,
            strategy=strategy,
            weights=weights_dict,
            expected_return=annual_return,
            volatility=annual_vol,
            sharpe_ratio=sharpe,
            n_stocks=len(tickers),
            run_id=run_id
        ))

    return results[0], results[1]  # sample, shrinkage


def compare_covariance_methods(
    tickers: list[str],
    strategy: Literal["min_variance", "max_sharpe"] = "max_sharpe",
    period: str = "3y",
    rf: float = 0.02,
    log_to_mlflow: bool = True
) -> CovarianceComparison:
    """
    Sample vs Shrinkage 공분산 비교

    Args:
        tickers: 종목 티커 리스트
        strategy: 최적화 전략
        period: 데이터 기간
        rf: 무위험 이자율
        log_to_mlflow: MLflow 로깅 여부

    Returns:
        CovarianceComparison 결과
    """
    sample_result, shrinkage_result = run_optimization_experiment(
        tickers=tickers,
        strategy=strategy,
        period=period,
        rf=rf,
        log_to_mlflow=log_to_mlflow
    )

    sharpe_diff = shrinkage_result.sharpe_ratio - sample_result.sharpe_ratio
    volatility_diff = shrinkage_result.volatility - sample_result.volatility
    return_diff = shrinkage_result.expected_return - sample_result.expected_return

    # 추천 결정
    if sharpe_diff > 0.05:
        recommendation = "shrinkage"
        reason = f"Shrinkage has {sharpe_diff:.4f} higher Sharpe ratio"
    elif sharpe_diff < -0.05:
        recommendation = "sample"
        reason = f"Sample has {-sharpe_diff:.4f} higher Sharpe ratio"
    else:
        # 비슷하면 변동성이 낮은 쪽
        if volatility_diff < 0:
            recommendation = "shrinkage"
            reason = f"Similar Sharpe, but Shrinkage has {-volatility_diff:.4f} lower volatility"
        else:
            recommendation = "sample"
            reason = f"Similar Sharpe, but Sample has {volatility_diff:.4f} lower volatility"

    run_id = None
    if log_to_mlflow:
        _init_mlflow()
        with mlflow.start_run(run_name=f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_param("comparison_type", "sample_vs_shrinkage")
            mlflow.log_param("strategy", strategy)
            mlflow.log_param("n_stocks", len(tickers))
            mlflow.log_param("recommendation", recommendation)

            mlflow.log_metric("sharpe_diff", sharpe_diff)
            mlflow.log_metric("volatility_diff", volatility_diff)
            mlflow.log_metric("return_diff", return_diff)
            mlflow.log_metric("sample_sharpe", sample_result.sharpe_ratio)
            mlflow.log_metric("shrinkage_sharpe", shrinkage_result.sharpe_ratio)

            run_id = mlflow.active_run().info.run_id

    return CovarianceComparison(
        sample_result=sample_result,
        shrinkage_result=shrinkage_result,
        sharpe_diff=sharpe_diff,
        volatility_diff=volatility_diff,
        return_diff=return_diff,
        recommendation=f"{recommendation}: {reason}",
        run_id=run_id
    )


def run_backtest_experiment(
    tickers: list[str],
    strategy: Literal["min_variance", "max_sharpe", "equal_weight"] = "max_sharpe",
    train_window: int = 252,
    rebalance_every: int = 63,
    transaction_cost: float = 0.001,
    period: str = "5y",
    use_shrinkage: bool = True,
    window_type: Literal["rolling", "expanding"] = "rolling",
    log_to_mlflow: bool = True,
    log_artifacts: bool = True
) -> BacktestExperimentResult:
    """
    백테스트 실험 실행 및 MLflow 기록

    Args:
        tickers: 종목 티커 리스트
        strategy: 최적화 전략
        train_window: 학습 기간 (거래일)
        rebalance_every: 리밸런싱 주기 (거래일)
        transaction_cost: 거래비용
        period: 백테스트 기간
        use_shrinkage: Shrinkage 공분산 사용
        window_type: 윈도우 타입 ("rolling" 또는 "expanding")
        log_to_mlflow: MLflow 로깅 여부
        log_artifacts: 아티팩트 로깅 여부

    Returns:
        BacktestExperimentResult 결과
    """
    if log_to_mlflow:
        _init_mlflow()

    # 수익률 데이터 수집
    returns_df = fetch_returns(tickers, period)

    # 백테스트 실행
    result = walk_forward_backtest(
        returns_df=returns_df,
        strategy=strategy,
        train_window=train_window,
        rebalance_every=rebalance_every,
        transaction_cost=transaction_cost,
        use_shrinkage=use_shrinkage,
        window_type=window_type
    )

    metrics = result.metrics

    run_id = None
    if log_to_mlflow:
        with mlflow.start_run(run_name=f"backtest_{strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # 파라미터 로깅
            mlflow.log_param("strategy", strategy)
            mlflow.log_param("train_window", train_window)
            mlflow.log_param("rebalance_every", rebalance_every)
            mlflow.log_param("transaction_cost", transaction_cost)
            mlflow.log_param("use_shrinkage", use_shrinkage)
            mlflow.log_param("window_type", window_type)
            mlflow.log_param("period", period)
            mlflow.log_param("n_stocks", len(tickers))
            mlflow.log_param("tickers", ",".join(tickers))

            # 메트릭 로깅
            mlflow.log_metric("total_return", metrics.total_return)
            mlflow.log_metric("annual_return", metrics.annual_return)
            mlflow.log_metric("annual_volatility", metrics.annual_volatility)
            mlflow.log_metric("sharpe_ratio", metrics.sharpe_ratio)
            mlflow.log_metric("max_drawdown", metrics.max_drawdown)
            mlflow.log_metric("calmar_ratio", metrics.calmar_ratio)
            mlflow.log_metric("avg_turnover", metrics.avg_turnover)
            mlflow.log_metric("win_rate", metrics.win_rate)
            mlflow.log_metric("n_rebalances", metrics.n_rebalances)

            # 아티팩트 로깅
            if log_artifacts:
                # 1. 입력 파라미터
                input_params = {
                    "tickers": tickers,
                    "strategy": strategy,
                    "train_window": train_window,
                    "rebalance_every": rebalance_every,
                    "transaction_cost": transaction_cost,
                    "use_shrinkage": use_shrinkage,
                    "period": period,
                    "n_stocks": len(tickers),
                    "timestamp": datetime.now().isoformat()
                }
                _log_json_artifact(input_params, "input_params.json")

                # 2. 최종 비중 (weights_history의 마지막 행 사용)
                final_weights = {}
                if result.weights_history is not None and len(result.weights_history) > 0:
                    last_row = result.weights_history.iloc[-1]
                    final_weights = {
                        ticker: round(float(last_row[ticker]), 6)
                        for ticker in tickers
                        if ticker in last_row.index
                    }
                _log_json_artifact(final_weights, "final_weights.json")

                # 3. 리밸런싱 히스토리 (weights는 numpy array → zip으로 변환)
                rebalance_history = [
                    {
                        "date": str(record.date),
                        "weights": {
                            ticker: round(float(w), 6)
                            for ticker, w in zip(tickers, record.weights)
                        },
                        "turnover": round(float(record.turnover), 6)
                    }
                    for record in result.rebalance_history
                ]
                _log_json_artifact(rebalance_history, "rebalance_history.json")

                # 4. 포트폴리오 가치 시계열
                portfolio_values_df = pd.DataFrame(result.portfolio_values)
                _log_dataframe_artifact(portfolio_values_df, "portfolio_values.csv")

                # 5. 성과 메트릭 요약
                metrics_dict = {
                    "total_return": float(metrics.total_return),
                    "annual_return": float(metrics.annual_return),
                    "annual_volatility": float(metrics.annual_volatility),
                    "sharpe_ratio": float(metrics.sharpe_ratio),
                    "max_drawdown": float(metrics.max_drawdown),
                    "calmar_ratio": float(metrics.calmar_ratio),
                    "avg_turnover": float(metrics.avg_turnover),
                    "win_rate": float(metrics.win_rate),
                    "n_rebalances": int(metrics.n_rebalances)
                }
                _log_json_artifact(metrics_dict, "backtest_metrics.json")

                logger.info(
                    "mlflow_backtest_artifacts_logged",
                    run_id=mlflow.active_run().info.run_id,
                    artifacts=["input_params.json", "final_weights.json",
                               "rebalance_history.json", "portfolio_values.csv",
                               "backtest_metrics.json"]
                )

            run_id = mlflow.active_run().info.run_id

    return BacktestExperimentResult(
        strategy=strategy,
        use_shrinkage=use_shrinkage,
        total_return=metrics.total_return,
        annual_return=metrics.annual_return,
        sharpe_ratio=metrics.sharpe_ratio,
        max_drawdown=metrics.max_drawdown,
        avg_turnover=metrics.avg_turnover,
        n_rebalances=metrics.n_rebalances,
        run_id=run_id
    )


def get_recent_experiments(limit: int = 10) -> list[dict]:
    """
    최근 실험 결과 조회

    Args:
        limit: 조회할 실험 수

    Returns:
        실험 결과 리스트
    """
    _init_mlflow()

    client = mlflow.tracking.MlflowClient()

    try:
        experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
        if experiment is None:
            return []

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=limit
        )

        results = []
        for run in runs:
            results.append({
                "run_id": run.info.run_id,
                "run_name": run.info.run_name,
                "status": run.info.status,
                "start_time": datetime.fromtimestamp(
                    run.info.start_time / 1000
                ).isoformat() if run.info.start_time else None,
                "params": dict(run.data.params),
                "metrics": dict(run.data.metrics),
            })

        return results

    except Exception as e:
        return [{"error": str(e)}]


def get_best_run(metric: str = "sharpe_ratio") -> Optional[dict]:
    """
    특정 메트릭 기준 최고 성능 실험 조회

    Args:
        metric: 기준 메트릭

    Returns:
        최고 성능 실험 정보
    """
    _init_mlflow()

    client = mlflow.tracking.MlflowClient()

    try:
        experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
        if experiment is None:
            return None

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=f"metrics.{metric} > 0",
            order_by=[f"metrics.{metric} DESC"],
            max_results=1
        )

        if not runs:
            return None

        run = runs[0]
        return {
            "run_id": run.info.run_id,
            "run_name": run.info.run_name,
            f"best_{metric}": run.data.metrics.get(metric),
            "params": dict(run.data.params),
            "metrics": dict(run.data.metrics),
        }

    except Exception as e:
        return {"error": str(e)}
