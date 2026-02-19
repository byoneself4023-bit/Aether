"""MLflow 실험 API 라우터"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Literal

from app.services.experiment import (
    run_optimization_experiment,
    compare_covariance_methods,
    run_backtest_experiment,
    get_recent_experiments,
    get_best_run,
)
from app.services.data import validate_tickers

router = APIRouter(prefix="/api/experiment", tags=["experiment"])


# ============================================================
# Request/Response Schemas
# ============================================================

class OptimizeExperimentRequest(BaseModel):
    """최적화 실험 요청"""
    tickers: list[str] = Field(
        ...,
        min_length=2,
        description="종목 티커 리스트"
    )
    strategy: Literal["min_variance", "max_sharpe"] = Field(
        default="max_sharpe",
        description="최적화 전략"
    )
    period: Literal["1y", "3y", "5y"] = Field(
        default="3y",
        description="데이터 기간"
    )
    rf: float = Field(
        default=0.02,
        description="무위험 이자율"
    )


class OptimizationResultResponse(BaseModel):
    """단일 최적화 결과"""
    method: str
    strategy: str
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    n_stocks: int
    run_id: Optional[str] = None


class OptimizeExperimentResponse(BaseModel):
    """최적화 실험 응답"""
    sample_result: OptimizationResultResponse
    shrinkage_result: OptimizationResultResponse
    mlflow_experiment: str


class CompareRequest(BaseModel):
    """비교 실험 요청"""
    tickers: list[str] = Field(
        ...,
        min_length=2,
        description="종목 티커 리스트"
    )
    strategy: Literal["min_variance", "max_sharpe"] = Field(
        default="max_sharpe",
        description="최적화 전략"
    )
    period: Literal["1y", "3y", "5y"] = Field(
        default="3y",
        description="데이터 기간"
    )
    rf: float = Field(default=0.02)


class CompareResponse(BaseModel):
    """비교 실험 응답"""
    sample_result: OptimizationResultResponse
    shrinkage_result: OptimizationResultResponse
    sharpe_diff: float = Field(..., description="Shrinkage - Sample Sharpe 차이")
    volatility_diff: float = Field(..., description="Shrinkage - Sample 변동성 차이")
    return_diff: float = Field(..., description="Shrinkage - Sample 수익률 차이")
    recommendation: str = Field(..., description="추천 방법 및 이유")
    run_id: Optional[str] = None


class BacktestExperimentRequest(BaseModel):
    """백테스트 실험 요청"""
    tickers: list[str] = Field(..., min_length=2)
    strategy: Literal["min_variance", "max_sharpe", "equal_weight"] = "max_sharpe"
    train_window: int = Field(default=252, ge=60)
    rebalance_every: int = Field(default=63, ge=5)
    transaction_cost: float = Field(default=0.001)
    period: Literal["3y", "5y", "10y"] = "5y"
    use_shrinkage: bool = True


class BacktestExperimentResponse(BaseModel):
    """백테스트 실험 응답"""
    strategy: str
    use_shrinkage: bool
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    avg_turnover: float
    n_rebalances: int
    run_id: Optional[str] = None


class ExperimentRunResponse(BaseModel):
    """실험 실행 정보"""
    run_id: str
    run_name: Optional[str] = None
    status: str
    start_time: Optional[str] = None
    params: dict
    metrics: dict


# ============================================================
# Endpoints
# ============================================================

@router.post("/optimize", response_model=OptimizeExperimentResponse)
def run_optimize_experiment(request: OptimizeExperimentRequest):
    """
    최적화 실험 실행

    Sample과 Shrinkage 공분산 두 가지 방법으로 최적화를 수행하고
    MLflow에 결과를 기록합니다.
    """
    tickers = request.tickers

    # 티커 검증
    valid_tickers, invalid_tickers = validate_tickers(tickers)
    if invalid_tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tickers: {invalid_tickers}"
        )

    try:
        sample_result, shrinkage_result = run_optimization_experiment(
            tickers=valid_tickers,
            strategy=request.strategy,
            period=request.period,
            rf=request.rf,
            log_to_mlflow=True
        )

        return OptimizeExperimentResponse(
            sample_result=OptimizationResultResponse(
                method=sample_result.method,
                strategy=sample_result.strategy,
                weights=sample_result.weights,
                expected_return=round(sample_result.expected_return, 6),
                volatility=round(sample_result.volatility, 6),
                sharpe_ratio=round(sample_result.sharpe_ratio, 4),
                n_stocks=sample_result.n_stocks,
                run_id=sample_result.run_id
            ),
            shrinkage_result=OptimizationResultResponse(
                method=shrinkage_result.method,
                strategy=shrinkage_result.strategy,
                weights=shrinkage_result.weights,
                expected_return=round(shrinkage_result.expected_return, 6),
                volatility=round(shrinkage_result.volatility, 6),
                sharpe_ratio=round(shrinkage_result.sharpe_ratio, 4),
                n_stocks=shrinkage_result.n_stocks,
                run_id=shrinkage_result.run_id
            ),
            mlflow_experiment="aether-portfolio-optimization"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Experiment failed: {str(e)}"
        )


@router.post("/compare", response_model=CompareResponse)
def compare_methods(request: CompareRequest):
    """
    Sample vs Shrinkage 공분산 비교

    두 방법의 성과를 비교하고 추천을 제공합니다.
    """
    tickers = request.tickers

    valid_tickers, invalid_tickers = validate_tickers(tickers)
    if invalid_tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tickers: {invalid_tickers}"
        )

    try:
        comparison = compare_covariance_methods(
            tickers=valid_tickers,
            strategy=request.strategy,
            period=request.period,
            rf=request.rf,
            log_to_mlflow=True
        )

        return CompareResponse(
            sample_result=OptimizationResultResponse(
                method=comparison.sample_result.method,
                strategy=comparison.sample_result.strategy,
                weights=comparison.sample_result.weights,
                expected_return=round(comparison.sample_result.expected_return, 6),
                volatility=round(comparison.sample_result.volatility, 6),
                sharpe_ratio=round(comparison.sample_result.sharpe_ratio, 4),
                n_stocks=comparison.sample_result.n_stocks,
                run_id=comparison.sample_result.run_id
            ),
            shrinkage_result=OptimizationResultResponse(
                method=comparison.shrinkage_result.method,
                strategy=comparison.shrinkage_result.strategy,
                weights=comparison.shrinkage_result.weights,
                expected_return=round(comparison.shrinkage_result.expected_return, 6),
                volatility=round(comparison.shrinkage_result.volatility, 6),
                sharpe_ratio=round(comparison.shrinkage_result.sharpe_ratio, 4),
                n_stocks=comparison.shrinkage_result.n_stocks,
                run_id=comparison.shrinkage_result.run_id
            ),
            sharpe_diff=round(comparison.sharpe_diff, 4),
            volatility_diff=round(comparison.volatility_diff, 6),
            return_diff=round(comparison.return_diff, 6),
            recommendation=comparison.recommendation,
            run_id=comparison.run_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


@router.post("/backtest", response_model=BacktestExperimentResponse)
def run_backtest_exp(request: BacktestExperimentRequest):
    """
    백테스트 실험 실행

    Walk-forward 백테스트를 수행하고 MLflow에 기록합니다.
    """
    tickers = request.tickers

    valid_tickers, invalid_tickers = validate_tickers(tickers)
    if invalid_tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tickers: {invalid_tickers}"
        )

    try:
        result = run_backtest_experiment(
            tickers=valid_tickers,
            strategy=request.strategy,
            train_window=request.train_window,
            rebalance_every=request.rebalance_every,
            transaction_cost=request.transaction_cost,
            period=request.period,
            use_shrinkage=request.use_shrinkage,
            log_to_mlflow=True
        )

        return BacktestExperimentResponse(
            strategy=result.strategy,
            use_shrinkage=result.use_shrinkage,
            total_return=round(result.total_return, 6),
            annual_return=round(result.annual_return, 6),
            sharpe_ratio=round(result.sharpe_ratio, 4),
            max_drawdown=round(result.max_drawdown, 6),
            avg_turnover=round(result.avg_turnover, 4),
            n_rebalances=result.n_rebalances,
            run_id=result.run_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest experiment failed: {str(e)}"
        )


@router.get("/results", response_model=list[ExperimentRunResponse])
def get_results(
    limit: int = Query(default=10, ge=1, le=100, description="조회할 실험 수")
):
    """
    최근 실험 결과 조회

    MLflow에 기록된 최근 실험들을 조회합니다.
    """
    try:
        results = get_recent_experiments(limit=limit)

        if results and "error" in results[0]:
            raise HTTPException(
                status_code=500,
                detail=results[0]["error"]
            )

        return [
            ExperimentRunResponse(
                run_id=r["run_id"],
                run_name=r.get("run_name"),
                status=r["status"],
                start_time=r.get("start_time"),
                params=r["params"],
                metrics=r["metrics"]
            )
            for r in results
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch results: {str(e)}"
        )


@router.get("/best")
def get_best(
    metric: str = Query(default="sharpe_ratio", description="기준 메트릭")
):
    """
    최고 성능 실험 조회

    특정 메트릭 기준으로 가장 좋은 성능을 낸 실험을 조회합니다.
    """
    try:
        result = get_best_run(metric=metric)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="No experiments found"
            )

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch best run: {str(e)}"
        )
