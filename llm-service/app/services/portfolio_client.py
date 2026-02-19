"""Portfolio Service 클라이언트 - portfolio-service(8001) API 호출"""

import asyncio
import logging
from typing import Any, Literal

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PortfolioServiceError(Exception):
    """Portfolio Service 호출 에러"""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PortfolioServiceUnavailable(PortfolioServiceError):
    """Portfolio Service 연결 불가"""
    pass


# ============================================================
# HTTP 클라이언트 설정
# ============================================================

def _get_client() -> httpx.AsyncClient:
    """AsyncClient 인스턴스 생성"""
    return httpx.AsyncClient(
        base_url=settings.portfolio_service_url,
        timeout=httpx.Timeout(60.0),  # 백테스트가 오래 걸릴 수 있음
        headers={"Content-Type": "application/json"},
    )


async def _make_request(
    method: str,
    endpoint: str,
    json_data: dict | None = None,
) -> dict:
    """
    HTTP 요청 실행

    Args:
        method: HTTP 메서드 ("GET", "POST", ...)
        endpoint: API 엔드포인트 ("/api/optimize")
        json_data: 요청 바디

    Returns:
        응답 JSON

    Raises:
        PortfolioServiceUnavailable: 연결 실패
        PortfolioServiceError: API 에러
    """
    async with _get_client() as client:
        try:
            response = await client.request(
                method=method,
                url=endpoint,
                json=json_data,
            )

            # 성공 응답
            if response.status_code == 200:
                return response.json()

            # 에러 응답
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except Exception:
                error_detail = response.text or "Unknown error"

            raise PortfolioServiceError(
                message=f"Portfolio service error: {error_detail}",
                status_code=response.status_code,
            )

        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to portfolio-service: {e}")
            raise PortfolioServiceUnavailable(
                message=f"Portfolio service unavailable at {settings.portfolio_service_url}"
            )

        except httpx.TimeoutException as e:
            logger.error(f"Portfolio service timeout: {e}")
            raise PortfolioServiceError(
                message="Portfolio service request timeout (60s exceeded)"
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise PortfolioServiceError(message=f"HTTP error: {e}")


# ============================================================
# API 호출 함수
# ============================================================

async def get_optimization(
    tickers: list[str],
    strategy: Literal["min_variance", "max_sharpe"] = "max_sharpe",
    period: Literal["1y", "3y", "5y"] = "3y",
    rf: float = 0.02,
    include_frontier: bool = False,
) -> dict[str, Any]:
    """
    포트폴리오 최적화 API 호출

    Args:
        tickers: 종목 리스트 ["AAPL", "GOOGL", ...]
        strategy: "min_variance" 또는 "max_sharpe"
        period: 데이터 기간
        rf: 무위험 이자율
        include_frontier: 효율적 프론티어 포함 여부

    Returns:
        {
            "weights": {"AAPL": 0.3, ...},
            "metrics": {
                "expected_return": 0.15,
                "volatility": 0.18,
                "sharpe_ratio": 0.83
            },
            "n_stocks": 5,
            "strategy": "max_sharpe",
            "period": "3y",
            "frontier": [...] (include_frontier=True일 때)
        }
    """
    logger.info(f"Calling optimization API: {tickers}, strategy={strategy}")

    response = await _make_request(
        method="POST",
        endpoint="/api/optimize",
        json_data={
            "tickers": tickers,
            "strategy": strategy,
            "period": period,
            "rf": rf,
            "include_frontier": include_frontier,
        },
    )

    return response


async def get_risk_analysis(
    tickers: list[str],
    weights: dict[str, float],
    confidence: float = 0.95,
    period: Literal["1y", "3y", "5y"] = "3y",
    n_simulations: int = 10000,
) -> dict[str, Any]:
    """
    리스크 분석 API 호출

    Args:
        tickers: 종목 리스트
        weights: 종목별 비중 {"AAPL": 0.3, ...}
        confidence: VaR 신뢰수준
        period: 데이터 기간
        n_simulations: 몬테카를로 시뮬레이션 횟수

    Returns:
        {
            "parametric_var": {"value": 0.018, "confidence": 0.95, ...},
            "monte_carlo_var": {"value": 0.019, ...},
            "cvar": 0.024,
            "risk_summary": {
                "volatility": 0.18,
                "var_95_parametric": 0.018,
                ...
            }
        }
    """
    logger.info(f"Calling risk analysis API: {tickers}")

    response = await _make_request(
        method="POST",
        endpoint="/api/risk",
        json_data={
            "tickers": tickers,
            "weights": weights,
            "confidence": confidence,
            "period": period,
            "n_simulations": n_simulations,
        },
    )

    return response


async def get_backtest(
    tickers: list[str],
    strategy: Literal["min_variance", "max_sharpe", "equal_weight"] = "max_sharpe",
    period: Literal["3y", "5y", "10y"] = "5y",
    train_window: int = 252,
    rebalance_every: int = 63,
    transaction_cost: float = 0.001,
    use_shrinkage: bool = True,
) -> dict[str, Any]:
    """
    백테스트 API 호출

    Args:
        tickers: 종목 리스트
        strategy: 최적화 전략
        period: 백테스트 기간
        train_window: 학습 기간 (거래일)
        rebalance_every: 리밸런싱 주기 (거래일)
        transaction_cost: 거래비용
        use_shrinkage: Shrinkage 공분산 사용 여부

    Returns:
        {
            "metrics": {
                "total_return": 1.28,
                "annual_return": 0.426,
                "sharpe_ratio": 1.94,
                "max_drawdown": 0.136,
                ...
            },
            "portfolio_values": [...],
            "rebalance_count": 12,
            "rebalance_history": [...],
            "strategy": "max_sharpe",
            "tickers": ["AAPL", ...],
            "final_weights": {...}
        }
    """
    logger.info(f"Calling backtest API: {tickers}, strategy={strategy}")

    response = await _make_request(
        method="POST",
        endpoint="/api/backtest",
        json_data={
            "tickers": tickers,
            "strategy": strategy,
            "period": period,
            "train_window": train_window,
            "rebalance_every": rebalance_every,
            "transaction_cost": transaction_cost,
            "use_shrinkage": use_shrinkage,
        },
    )

    return response


async def get_full_analysis(
    tickers: list[str],
    strategy: Literal["min_variance", "max_sharpe"] = "max_sharpe",
    period: Literal["1y", "3y", "5y"] = "3y",
    backtest_period: Literal["3y", "5y", "10y"] = "5y",
    rf: float = 0.02,
) -> dict[str, Any]:
    """
    전체 분석 (최적화 + 리스크 + 백테스트) 동시 호출

    Args:
        tickers: 종목 리스트
        strategy: 최적화 전략
        period: 최적화/리스크 데이터 기간
        backtest_period: 백테스트 기간
        rf: 무위험 이자율

    Returns:
        {
            "optimization": {...},
            "risk": {...},
            "backtest": {...},
            "summary": {
                "tickers": [...],
                "strategy": "max_sharpe",
                "weights": {...},
                "expected_return": 0.15,
                "volatility": 0.18,
                "sharpe_ratio": 0.83,
                "var_95": 0.018,
                "backtest_return": 0.426,
                "max_drawdown": 0.136
            }
        }
    """
    logger.info(f"Calling full analysis: {tickers}, strategy={strategy}")

    # 1. 최적화 먼저 (비중 필요)
    optimization = await get_optimization(
        tickers=tickers,
        strategy=strategy,
        period=period,
        rf=rf,
        include_frontier=True,
    )

    weights = optimization["weights"]

    # 2. 리스크 분석과 백테스트 병렬 실행
    risk_task = get_risk_analysis(
        tickers=tickers,
        weights=weights,
        period=period,
    )

    backtest_task = get_backtest(
        tickers=tickers,
        strategy=strategy,
        period=backtest_period,
    )

    risk, backtest = await asyncio.gather(risk_task, backtest_task)

    # 3. 요약 정보 생성
    summary = {
        "tickers": tickers,
        "strategy": strategy,
        "weights": weights,
        "expected_return": optimization["metrics"]["expected_return"],
        "volatility": optimization["metrics"]["volatility"],
        "sharpe_ratio": optimization["metrics"]["sharpe_ratio"],
        "var_95": risk["risk_summary"]["var_95_montecarlo"],
        "cvar_95": risk["risk_summary"]["cvar_95"],
        "backtest_total_return": backtest["metrics"]["total_return"],
        "backtest_annual_return": backtest["metrics"]["annual_return"],
        "backtest_sharpe": backtest["metrics"]["sharpe_ratio"],
        "max_drawdown": backtest["metrics"]["max_drawdown"],
    }

    return {
        "optimization": optimization,
        "risk": risk,
        "backtest": backtest,
        "summary": summary,
    }


# ============================================================
# 헬스체크 및 유틸리티
# ============================================================

async def check_health() -> dict[str, Any]:
    """
    Portfolio Service 헬스체크

    Returns:
        {"status": "healthy", "service": "portfolio-service", ...}
        또는 에러 시 {"status": "unhealthy", "error": "..."}
    """
    try:
        async with _get_client() as client:
            response = await client.get("/health")
            if response.status_code == 200:
                return response.json()
            return {"status": "unhealthy", "error": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def is_available() -> bool:
    """Portfolio Service 사용 가능 여부"""
    health = await check_health()
    return health.get("status") == "healthy"


def get_service_url() -> str:
    """Portfolio Service URL 반환"""
    return settings.portfolio_service_url
