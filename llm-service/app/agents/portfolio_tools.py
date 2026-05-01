"""4 도메인 함수 @tool 래퍼 - services/llm.py 원본을 0 변경 호출"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from app.services.llm import (
    analyze_portfolio,
    explain_risk,
    get_recommendation,
    summarize_backtest,
)


@tool
def analyze_portfolio_tool(
    weights: dict[str, float],
    metrics: dict[str, float],
    tickers_info: dict[str, dict] | None = None,
) -> dict[str, Any]:
    """포트폴리오 가중치·지표를 분석해 요약·강점·약점·해석을 반환."""
    return analyze_portfolio(weights, metrics, tickers_info)


@tool
def explain_risk_tool(
    risk_data: dict[str, float],
    investment_amount: float | None = None,
) -> dict[str, Any]:
    """VaR·CVaR 등 리스크 데이터를 비전문가 언어로 설명."""
    return explain_risk(risk_data, investment_amount)


@tool
def summarize_backtest_tool(
    metrics: dict[str, float],
    strategy: str,
    period: str,
    tickers: list[str],
    rebalance_history: list[dict] | None = None,
    final_weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """백테스트 성과 지표를 자연어로 요약하고 인사이트를 추출."""
    return summarize_backtest(metrics, strategy, period, tickers, rebalance_history, final_weights)


@tool
def get_recommendation_tool(
    current_portfolio: dict[str, float],
    tickers_info: dict[str, dict] | None = None,
    metrics: dict[str, float] | None = None,
    risk_data: dict[str, float] | None = None,
    market_context: str | None = None,
    investor_profile: dict[str, str] | None = None,
) -> dict[str, Any]:
    """현재 포트폴리오에 대한 개선 제안 생성."""
    return get_recommendation(
        current_portfolio,
        tickers_info,
        metrics,
        risk_data,
        market_context,
        investor_profile,
    )
