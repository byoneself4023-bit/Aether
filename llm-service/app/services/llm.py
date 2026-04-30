"""LLM 서비스 - Provider 추상화를 통한 LLM 호출"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

from app.config import get_settings
from app.schemas.llm_output import (
    BacktestSummaryResponse,
    PortfolioAnalysisResponse,
    RecommendationResponse,
    RiskAnalysisResponse,
)
from app.services.llm_provider import (
    LLMError,
    LLMResponseError,
    get_llm_provider,
)
from app.services.prompts import (
    backtest_summary_prompt,
    get_system_prompt,
    portfolio_analysis_prompt,
    recommendation_prompt,
    risk_explanation_prompt,
)
from app.services.validators import (
    validate_portfolio_analysis,
    validate_risk_analysis,
)

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================
# 하위호환 함수 - Provider를 경유하는 래퍼
# ============================================================


def call_llm(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """LLM 호출 (Provider 경유)."""
    provider = get_llm_provider()
    return provider.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def call_llm_structured(
    prompt: str,
    response_model: type[BaseModel],
    system_prompt: str | None = None,
    temperature: float | None = None,
) -> BaseModel:
    """Pydantic 모델 강제 출력 LLM 호출 (Provider 경유, H-6)."""
    provider = get_llm_provider()
    return provider.generate_structured(
        prompt=prompt,
        response_model=response_model,
        system_prompt=system_prompt,
        temperature=temperature,
    )


# ============================================================
# 고수준 분석 함수
# ============================================================


def analyze_portfolio(
    weights: dict[str, float],
    metrics: dict[str, float],
    tickers_info: dict[str, dict] | None = None,
) -> dict[str, Any]:
    """포트폴리오 분석 수행."""
    prompt = portfolio_analysis_prompt(
        weights=weights,
        metrics=metrics,
        tickers_info=tickers_info,
    )

    response = call_llm_structured(
        prompt=prompt,
        response_model=PortfolioAnalysisResponse,
        system_prompt=get_system_prompt(),
    )
    result: dict[str, Any] = response.model_dump()

    result["_input"] = {
        "weights": weights,
        "metrics": metrics,
    }

    validation = validate_portfolio_analysis(result, weights, metrics)
    if not validation.is_valid:
        logger.warning(f"Portfolio analysis validation failed: {validation.violations}")
        result["_warnings"] = validation.violations

    return result


def explain_risk(
    risk_data: dict[str, float],
    investment_amount: float | None = None,
) -> dict[str, Any]:
    """리스크 데이터를 비전문가 언어로 설명."""
    prompt = risk_explanation_prompt(
        risk_data=risk_data,
        investment_amount=investment_amount,
    )

    response = call_llm_structured(
        prompt=prompt,
        response_model=RiskAnalysisResponse,
        system_prompt=get_system_prompt(),
    )
    result: dict[str, Any] = response.model_dump()

    result["_input"] = {
        "risk_data": risk_data,
        "investment_amount": investment_amount,
    }

    validation = validate_risk_analysis(result, risk_data)
    if not validation.is_valid:
        logger.warning(f"Risk analysis validation failed: {validation.violations}")
        result["_warnings"] = validation.violations

    return result


def summarize_backtest(
    metrics: dict[str, float],
    strategy: str,
    period: str,
    tickers: list[str],
    rebalance_history: list[dict] | None = None,
    final_weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """백테스트 결과 요약 + 인사이트."""
    prompt = backtest_summary_prompt(
        metrics=metrics,
        strategy=strategy,
        period=period,
        tickers=tickers,
        rebalance_history=rebalance_history,
        final_weights=final_weights,
    )

    response = call_llm_structured(
        prompt=prompt,
        response_model=BacktestSummaryResponse,
        system_prompt=get_system_prompt(),
    )
    result: dict[str, Any] = response.model_dump()

    result["_input"] = {
        "strategy": strategy,
        "period": period,
        "tickers": tickers,
    }

    return result


def get_recommendation(
    current_portfolio: dict[str, float],
    tickers_info: dict[str, dict] | None = None,
    metrics: dict[str, float] | None = None,
    risk_data: dict[str, float] | None = None,
    market_context: str | None = None,
    investor_profile: dict[str, str] | None = None,
) -> dict[str, Any]:
    """포트폴리오 개선 제안."""
    prompt = recommendation_prompt(
        current_portfolio=current_portfolio,
        tickers_info=tickers_info,
        metrics=metrics,
        risk_data=risk_data,
        market_context=market_context,
        investor_profile=investor_profile,
    )

    response = call_llm_structured(
        prompt=prompt,
        response_model=RecommendationResponse,
        system_prompt=get_system_prompt(),
    )
    result: dict[str, Any] = response.model_dump()

    return result


# ============================================================
# 유틸리티 함수
# ============================================================


def check_api_key() -> bool:
    """API 키 설정 여부 확인"""
    return bool(settings.google_api_key)


def get_model_info() -> dict:
    """현재 모델 정보 반환"""
    return {
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
        "timeout": settings.llm_timeout,
        "api_key_configured": check_api_key(),
    }


# 하위호환을 위한 재export
__all__ = [
    "call_llm",
    "call_llm_structured",
    "analyze_portfolio",
    "explain_risk",
    "summarize_backtest",
    "get_recommendation",
    "check_api_key",
    "get_model_info",
    "LLMError",
    "LLMResponseError",
]
