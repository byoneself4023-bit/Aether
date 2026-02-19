"""포트폴리오 최적화 API 라우터"""

from fastapi import APIRouter, HTTPException
import numpy as np

from app.schemas.portfolio import (
    OptimizeRequest,
    OptimizeResponse,
    PortfolioMetricsResponse,
    FrontierPoint,
    DriftWarning,
    DriftMetrics,
    OptimizationDiagnosticsResponse,
    CovarianceValidationResponse,
    WeightComparisonResponse,
    WeightChangeAlertResponse,
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
from app.services.drift_detector import (
    analyze_drift,
    create_drift_report,
    DriftSeverity,
)
from app.utils.covariance import annualize, annualize_returns
from app.middleware.logging import logger, log_optimization_context
from app.services.weight_monitor import compare_weights
from app.metrics import (
    OptimizationMetricsContext,
    record_condition_number,
)

router = APIRouter(prefix="/api", tags=["optimize"])

# 드리프트 탐지를 위한 최근 기간 (거래일)
DRIFT_RECENT_DAYS = 20


@router.post("/optimize", response_model=OptimizeResponse)
def optimize_portfolio(request: OptimizeRequest) -> OptimizeResponse:
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

            # 드리프트 탐지 (최근 20일 vs 나머지)
            drift_warning = None
            if len(returns_df) > DRIFT_RECENT_DAYS + 60:  # 충분한 데이터가 있을 때만
                recent_returns = returns_df.iloc[-DRIFT_RECENT_DAYS:].values
                historical_returns = returns_df.iloc[:-DRIFT_RECENT_DAYS].values

                drift_analysis = analyze_drift(
                    recent_returns=recent_returns,
                    historical_returns=historical_returns,
                    asset_names=valid_tickers
                )

                # 드리프트 감지 시 경고 포함
                if drift_analysis.overall_drift:
                    drift_report = create_drift_report(drift_analysis, valid_tickers)

                    drift_warning = DriftWarning(
                        has_drift=drift_report.has_drift,
                        drift_type=drift_report.drift_type,
                        severity=drift_report.severity.value,
                        recommendation=drift_report.recommendation,
                        affected_assets=drift_report.affected_assets,
                        metrics=DriftMetrics(
                            volatility=drift_report.metrics["volatility"],
                            correlation=drift_report.metrics["correlation"],
                            market_regime=drift_report.metrics["market_regime"]
                        )
                    )

                    logger.warning(
                        "drift_warning_included_in_response",
                        drift_type=drift_report.drift_type,
                        severity=drift_report.severity.value
                    )

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

            # 비중 변화 알림 (previous_weights 제공 시)
            weight_alerts_response = None
            if request.previous_weights:
                comparison = compare_weights(
                    old_weights=request.previous_weights,
                    new_weights=weights_dict,
                    threshold=request.weight_change_threshold
                )

                weight_alerts_response = WeightComparisonResponse(
                    total_turnover=comparison.total_turnover,
                    alerts=[
                        WeightChangeAlertResponse(
                            asset=alert.asset,
                            old_weight=alert.old_weight,
                            new_weight=alert.new_weight,
                            change_pct=alert.change_pct,
                            change_direction=alert.change_direction
                        )
                        for alert in comparison.alerts
                    ],
                    max_change_asset=comparison.max_change_asset,
                    max_change_pct=comparison.max_change_pct
                )

                # 큰 비중 변화 시 경고 로깅
                if comparison.alerts:
                    logger.warning(
                        "significant_weight_changes",
                        total_turnover=comparison.total_turnover,
                        n_alerts=len(comparison.alerts),
                        max_change_asset=comparison.max_change_asset,
                        max_change_pct=comparison.max_change_pct
                    )

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
                drift_warning=drift_warning,
                diagnostics=diagnostics_response,
                weight_alerts=weight_alerts_response,
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
