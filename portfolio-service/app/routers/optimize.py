"""포트폴리오 최적화 API 라우터"""

from fastapi import APIRouter, Depends, HTTPException
import numpy as np

from app.middleware.auth import verify_jwt
from app.schemas.portfolio import (
    OptimizeRequest,
    OptimizeResponse,
    PortfolioMetricsResponse,
    FrontierPoint,
    OptimizationDiagnosticsResponse,
    CovarianceValidationResponse,
)
from app.services.data import (
    get_returns_and_covariance,
    get_returns_and_covariance_resilient,
    validate_tickers,
    fetch_returns,
)
from app.services.optimizer import (
    optimize_min_variance,
    optimize_max_sharpe,
    optimize_min_variance_with_diagnostics,
    optimize_max_sharpe_with_diagnostics,
    efficient_frontier,
)
from app.utils.covariance import annualize, annualize_returns
from app.middleware.logging import logger, log_optimization_context
from app.metrics import (
    OptimizationMetricsContext,
    record_condition_number,
)

router = APIRouter(prefix="/api", tags=["optimize"])


@router.post("/optimize", response_model=OptimizeResponse)
def optimize_portfolio(
    request: OptimizeRequest,
    user: dict = Depends(verify_jwt),
) -> OptimizeResponse:
    """
    포트폴리오 최적화 수행 (부분 실패 허용)

    주어진 종목들에 대해 최적 비중을 계산합니다.
    - min_variance: 최소 분산 포트폴리오 (MVP)
    - max_sharpe: 최대 샤프 비율 포트폴리오 (MSR)

    부분 실패:
    - 일부 티커가 실패해도 나머지로 최적화 수행
    - 응답에 failed_tickers, warnings 포함

    드리프트 탐지:
    - 최근 20일 vs 과거 데이터 비교
    - 변동성/상관관계 급변 시 경고 포함
    """
    tickers = request.tickers

    # 컨텍스트 로깅
    log_optimization_context(
        tickers=tickers,
        strategy=request.strategy,
        period=request.period,
        rf=request.rf
    )

    # 메트릭 수집을 위한 컨텍스트
    with OptimizationMetricsContext(strategy=request.strategy):
        try:
            # 부분 실패 허용 데이터 수집
            data_result = get_returns_and_covariance_resilient(
                tickers=tickers,
                period=request.period or "3y",
                use_shrinkage=True,
                min_tickers=2,
                start_date=request.start_date,
                end_date=request.end_date,
            )

            mu = data_result.mu
            cov = data_result.cov
            returns_df = data_result.returns_df
            valid_tickers = data_result.successful_tickers
            failed_tickers = data_result.failed_tickers
            all_warnings = list(data_result.warnings)  # 복사본 생성

            # 공분산 행렬 조건수 메트릭 기록
            from numpy.linalg import cond
            record_condition_number(cond(cov))

            # 일간 무위험 이자율
            daily_rf = request.rf / 252

            # 최적화 수행 (진단 정보 포함 여부에 따라 분기)
            diagnostics_response = None

            if request.include_diagnostics:
                # 진단 정보 포함 최적화
                if request.strategy == "min_variance":
                    opt_result = optimize_min_variance_with_diagnostics(mu, cov)
                else:  # max_sharpe
                    opt_result = optimize_max_sharpe_with_diagnostics(mu, cov, daily_rf)

                result = opt_result.metrics
                diag = opt_result.diagnostics

                # 진단 정보를 응답 스키마로 변환
                diagnostics_response = OptimizationDiagnosticsResponse(
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
                        regularized=diag.covariance_validation.was_regularized
                    )
                )
            else:
                # 기존 방식 (진단 정보 없이)
                if request.strategy == "min_variance":
                    result = optimize_min_variance(mu, cov)
                else:  # max_sharpe
                    result = optimize_max_sharpe(mu, cov, daily_rf)

            # 연율화 메트릭
            annual_return = float(result.expected_return * 252)
            annual_vol = float(result.volatility * np.sqrt(252))
            sharpe = (annual_return - request.rf) / annual_vol if annual_vol > 0 else 0

            # 비중 딕셔너리 생성
            weights_dict = {
                ticker: round(float(w), 6)
                for ticker, w in zip(valid_tickers, result.weights)
            }

            # 효율적 프론티어 (요청 시)
            frontier_points = None
            if request.include_frontier:
                frontier = efficient_frontier(mu, cov, n_points=20, rf=daily_rf)
                frontier_points = [
                    FrontierPoint(
                        expected_return=round(float(ret * 252), 6),
                        volatility=round(float(vol * np.sqrt(252)), 6),
                        weights={
                            ticker: round(float(w), 4)
                            for ticker, w in zip(valid_tickers, weights)
                        }
                    )
                    for ret, vol, weights in zip(
                        frontier.returns,
                        frontier.volatilities,
                        frontier.weights
                    )
                ]

            # 부분 실패 시 경고 메시지 추가
            if failed_tickers:
                all_warnings.insert(
                    0,
                    f"Partial success: {len(failed_tickers)} ticker(s) failed, "
                    f"optimization performed with {len(valid_tickers)} tickers"
                )

            return OptimizeResponse(
                weights=weights_dict,
                metrics=PortfolioMetricsResponse(
                    expected_return=round(annual_return, 6),
                    volatility=round(annual_vol, 6),
                    sharpe_ratio=round(sharpe, 4)
                ),
                n_stocks=len(valid_tickers),
                strategy=request.strategy,
                period=(f"{request.start_date}~{request.end_date}"
                        if request.start_date and request.end_date
                        else request.period or "3y"),
                frontier=frontier_points,
                diagnostics=diagnostics_response,
                failed_tickers=failed_tickers if failed_tickers else None,
                warnings=all_warnings if all_warnings else None
            )

        except ValueError as e:
            logger.error(
                "optimization_value_error",
                error=str(e),
                tickers=tickers,
                strategy=request.strategy
            )
            raise HTTPException(
                status_code=422,
                detail=f"Optimization failed: {str(e)}"
            )
        except Exception as e:
            logger.error(
                "optimization_unexpected_error",
                error=str(e),
                error_type=type(e).__name__,
                tickers=tickers
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal error: {str(e)}"
            )
