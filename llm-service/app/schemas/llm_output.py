"""LLM 도메인 응답 Pydantic 모델 — Gemini response_schema 강제 출력용 (H-6)."""

from __future__ import annotations

from pydantic import BaseModel


class Composition(BaseModel):
    description: str
    top_holdings: list[str]
    sector_concentration: str


class MetricsInterpretation(BaseModel):
    return_analysis: str
    risk_analysis: str
    sharpe_analysis: str


class PortfolioAnalysisResponse(BaseModel):
    summary: str
    composition: Composition
    metrics_interpretation: MetricsInterpretation
    strengths: list[str]
    weaknesses: list[str]
    diversification_score: str
    investor_profile: str


class VarExplanation(BaseModel):
    simple_explanation: str
    technical_detail: str
    example_scenario: str


class CvarExplanation(BaseModel):
    simple_explanation: str
    worst_case_scenario: str


class RiskAnalysisResponse(BaseModel):
    summary: str
    var_explanation: VarExplanation
    cvar_explanation: CvarExplanation
    risk_level: str
    risk_factors: list[str]
    hedging_suggestions: list[str]


class PerformanceHighlights(BaseModel):
    total_return: str
    annual_return: str
    volatility: str
    sharpe_ratio: str


class DrawdownAnalysis(BaseModel):
    max_drawdown: str
    recovery_insight: str


class RebalancingAnalysis(BaseModel):
    frequency: str
    turnover_impact: str


class BacktestSummaryResponse(BaseModel):
    summary: str
    performance_highlights: PerformanceHighlights
    drawdown_analysis: DrawdownAnalysis
    rebalancing_analysis: RebalancingAnalysis
    period_breakdown: list[str]
    strategy_effectiveness: str
    forward_outlook: str


class RecommendationItem(BaseModel):
    action: str
    target: str
    rationale: str
    priority: str


class SectorRebalancing(BaseModel):
    overweight: list[str]
    underweight: list[str]


class RecommendationResponse(BaseModel):
    summary: str
    current_assessment: str
    recommendations: list[RecommendationItem]
    risk_adjustments: list[str]
    sector_rebalancing: SectorRebalancing
    action_timeline: str
    caveats: list[str]
