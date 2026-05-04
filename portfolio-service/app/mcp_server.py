"""MCP 서버 — portfolio-service 4 도메인 도구 외부 노출 (T-2)."""

from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
import uuid
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from app.middleware.logging import request_id_ctx
from app.services.backtest import walk_forward_backtest
from app.services.drift_detector import analyze_drift
from app.services.optimizer import optimize_max_sharpe
from app.services.risk import risk_summary

logger = logging.getLogger(__name__)


class AnalyzePortfolioInput(BaseModel):
    mu: list[float] = Field(..., description="기대수익률 벡터 (N,)")
    cov: list[list[float]] = Field(..., description="공분산 행렬 (N x N)")
    rf: float = Field(0.0, description="무위험 이자율 (연율)")


class ComputeRiskInput(BaseModel):
    weights: list[float] = Field(..., description="자산 비중 (N,)")
    mu: list[float] = Field(..., description="일간 기대수익률 (N,)")
    cov: list[list[float]] = Field(..., description="일간 공분산 (N x N)")
    n_simulations: int = Field(10000, description="몬테카를로 시뮬레이션 횟수")


class RunBacktestInput(BaseModel):
    returns: list[list[float]] = Field(..., description="일별 수익률 (T x N)")
    asset_names: list[str] = Field(..., description="자산 이름 (N,)")
    dates: list[str] = Field(..., description="ISO 8601 날짜 (T,)")
    strategy: str = Field("max_sharpe", description="max_sharpe / min_variance / equal_weight")


class GetRecommendationInput(BaseModel):
    recent_returns: list[list[float]] = Field(..., description="최근 수익률 (T_recent x N)")
    historical_returns: list[list[float]] = Field(..., description="과거 수익률 (T_hist x N)")
    asset_names: list[str] | None = Field(None, description="자산 이름 (선택)")


def _call_optimize(args: dict[str, Any]) -> Any:
    mu = np.asarray(args["mu"])
    cov = np.asarray(args["cov"])
    return optimize_max_sharpe(mu, cov, rf=args.get("rf", 0.0))


def _call_risk(args: dict[str, Any]) -> Any:
    return risk_summary(
        np.asarray(args["weights"]),
        np.asarray(args["mu"]),
        np.asarray(args["cov"]),
        n_simulations=args.get("n_simulations", 10000),
    )


def _call_backtest(args: dict[str, Any]) -> Any:
    df = pd.DataFrame(
        args["returns"],
        index=pd.to_datetime(args["dates"]),
        columns=args["asset_names"],
    )
    return walk_forward_backtest(df, strategy=args.get("strategy", "max_sharpe"))


def _call_drift(args: dict[str, Any]) -> Any:
    return analyze_drift(
        np.asarray(args["recent_returns"]),
        np.asarray(args["historical_returns"]),
        asset_names=args.get("asset_names"),
    )


_TOOLS: dict[str, tuple[type[BaseModel], Any, str]] = {
    "analyze_portfolio": (
        AnalyzePortfolioInput,
        _call_optimize,
        "포트폴리오 최적화 (mean-variance, max sharpe)",
    ),
    "compute_risk": (
        ComputeRiskInput,
        _call_risk,
        "VaR/CVaR/리스크 요약 (parametric + Monte Carlo)",
    ),
    "run_backtest": (
        RunBacktestInput,
        _call_backtest,
        "walk-forward 백테스트 (rolling window)",
    ),
    "get_recommendation": (
        GetRecommendationInput,
        _call_drift,
        "포트폴리오 드리프트 분석 + 개선 제안",
    ),
}


server: Server = Server("aether-portfolio")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [Tool(name=n, description=d, inputSchema=s.model_json_schema()) for n, (s, _func, d) in _TOOLS.items()]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    request_id = arguments.pop("_request_id", None) or str(uuid.uuid4())[:8]
    token = request_id_ctx.set(request_id)
    try:
        if name not in _TOOLS:
            raise ValueError(f"Unknown tool: {name}")
        schema_cls, func, _desc = _TOOLS[name]
        validated = schema_cls(**arguments)
        result = await asyncio.to_thread(func, validated.model_dump())
        return [TextContent(type="text", text=json.dumps(_serialize(result), ensure_ascii=False))]
    finally:
        request_id_ctx.reset(token)


def _serialize(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _serialize(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, pd.Series):
        return {str(k): _serialize(v) for k, v in obj.items()}
    if isinstance(obj, pd.DataFrame):
        return obj.reset_index().to_dict(orient="records")
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    return obj


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
