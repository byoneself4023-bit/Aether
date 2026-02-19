"""백테스트 API 라우터"""

from fastapi import APIRouter, HTTPException

from app.schemas.portfolio import (
    BacktestRequest,
    BacktestResponse,
    PerformanceMetricsResponse,
    RebalanceRecordResponse,
)
from app.services.data import fetch_returns, validate_tickers
from app.services.backtest import walk_forward_backtest

router = APIRouter(prefix="/api", tags=["backtest"])


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Walk-forward 백테스트 실행

    시간순 분리 백테스트를 수행하여 미래 정보 사용을 방지합니다.
    - 학습 기간(train_window) 데이터로 최적화
    - 주기적(rebalance_every) 리밸런싱
    - 거래비용 반영
    """
    tickers = request.tickers

    # 티커 검증
    valid_tickers, invalid_tickers = validate_tickers(tickers)
    if invalid_tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tickers: {invalid_tickers}"
        )

    if len(valid_tickers) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 valid tickers are required"
        )

    try:
        # 수익률 데이터 수집
        returns_df = fetch_returns(
            tickers=valid_tickers,
            period=request.period or "5y",
            start_date=request.start_date,
            end_date=request.end_date,
        )

        # 데이터 충분성 검증
        min_required = request.train_window + request.rebalance_every * 2
        if len(returns_df) < min_required:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data: need at least {min_required} days, got {len(returns_df)}"
            )

        # 백테스트 실행
        result = walk_forward_backtest(
            returns_df=returns_df,
            strategy=request.strategy,
            train_window=request.train_window,
            rebalance_every=request.rebalance_every,
            transaction_cost=request.transaction_cost,
            use_shrinkage=request.use_shrinkage
        )

        # 포트폴리오 가치 시계열 변환
        portfolio_values = [
            {"date": date.strftime("%Y-%m-%d"), "value": round(float(value), 6)}
            for date, value in result.portfolio_values.items()
        ]

        # 리밸런싱 기록 변환
        rebalance_history = [
            RebalanceRecordResponse(
                date=record.date.strftime("%Y-%m-%d"),
                weights={
                    ticker: round(float(w), 4)
                    for ticker, w in zip(valid_tickers, record.weights)
                },
                turnover=round(record.turnover, 4)
            )
            for record in result.rebalance_history
        ]

        # 최종 비중
        final_weights = {}
        if result.weights_history is not None and len(result.weights_history) > 0:
            last_row = result.weights_history.iloc[-1]
            final_weights = {
                ticker: round(float(last_row[ticker]), 4)
                for ticker in valid_tickers
            }

        return BacktestResponse(
            metrics=PerformanceMetricsResponse(
                total_return=round(result.metrics.total_return, 6),
                annual_return=round(result.metrics.annual_return, 6),
                annual_volatility=round(result.metrics.annual_volatility, 6),
                sharpe_ratio=round(result.metrics.sharpe_ratio, 4),
                max_drawdown=round(result.metrics.max_drawdown, 6),
                calmar_ratio=round(result.metrics.calmar_ratio, 4),
                avg_turnover=round(result.metrics.avg_turnover, 4),
                win_rate=round(result.metrics.win_rate, 4)
            ),
            portfolio_values=portfolio_values,
            rebalance_count=result.metrics.n_rebalances,
            rebalance_history=rebalance_history,
            strategy=result.strategy,
            tickers=valid_tickers,
            final_weights=final_weights
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Backtest failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )
