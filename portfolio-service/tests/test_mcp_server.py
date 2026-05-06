"""MCP 서버 통합 테스트 — in-SDK stdio_client (T-2)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT = str(Path(__file__).resolve().parent.parent)


def _params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server"],
        cwd=PROJECT,
        env={**os.environ, "PYTHONPATH": PROJECT},
    )


@pytest.mark.asyncio
async def test_list_tools_returns_4() -> None:
    async with stdio_client(_params()) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.list_tools()
            assert {t.name for t in result.tools} == {
                "analyze_portfolio",
                "compute_risk",
                "run_backtest",
                "get_recommendation",
            }


@pytest.mark.asyncio
async def test_call_compute_risk_success() -> None:
    np.random.seed(42)
    n_assets = 4
    weights = [0.25] * n_assets
    mu = np.random.normal(0.0008, 0.0002, n_assets).tolist()
    cov = (np.eye(n_assets) * 0.0001).tolist()
    async with stdio_client(_params()) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool(
                "compute_risk",
                {"weights": weights, "mu": mu, "cov": cov, "n_simulations": 1000},
            )
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert "var_95_parametric" in data
            assert "cvar_95" in data
            assert "expected_return" in data


@pytest.mark.asyncio
async def test_call_unknown_tool_returns_error() -> None:
    async with stdio_client(_params()) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool("nonexistent_tool", {})
            assert result.isError


@pytest.mark.asyncio
async def test_call_invalid_schema_returns_error() -> None:
    async with stdio_client(_params()) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool("analyze_portfolio", {"cov": [[0.01]]})
            assert result.isError
