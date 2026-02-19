"""LLM 서비스 - Provider 추상화를 통한 LLM 호출"""

import json
import logging
import re
from typing import Any

from app.config import get_settings
from app.services.prompts import (
    portfolio_analysis_prompt,
    risk_explanation_prompt,
    backtest_summary_prompt,
    recommendation_prompt,
    get_system_prompt,
)
from app.services.validators import (
    validate_portfolio_analysis,
    validate_risk_analysis,
)
from app.services.llm_provider import (
    get_llm_provider,
    LLMError,
    JSONParseError,
    _extract_json,
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
    """
    LLM 호출 (Provider 경유)

    Args:
        prompt: 사용자 프롬프트
        system_prompt: 시스템 프롬프트 (None이면 기본값 사용)
        temperature: 온도 (None이면 설정값 사용)
        max_tokens: 최대 토큰 (None이면 설정값 사용)

    Returns:
        LLM 응답 텍스트

    Raises:
        LLMError: LLM 호출 실패
    """
    provider = get_llm_provider()
    return provider.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def call_llm_json(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float | None = None,
) -> dict:
    """
    JSON 응답을 강제하는 LLM 호출 (Provider 경유)

    Args:
        prompt: 사용자 프롬프트 (JSON 스키마 포함 권장)
        system_prompt: 시스템 프롬프트
        temperature: 온도 (JSON 파싱 안정성을 위해 낮은 값 권장)

    Returns:
        파싱된 JSON 딕셔너리

    Raises:
        JSONParseError: JSON 파싱 실패 (재시도 후에도)
        LLMError: LLM 호출 실패
    """
    provider = get_llm_provider()
    return provider.generate_json(
        prompt=prompt,
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
    """
    포트폴리오 분석 수행

    Args:
        weights: 종목별 비중 {"AAPL": 0.3, "GOOGL": 0.2, ...}
        metrics: 성과 지표 {
            "expected_return": 0.15,
            "volatility": 0.18,
            "sharpe_ratio": 0.83
        }
        tickers_info: 종목 정보 (선택)

    Returns:
        구조화된 분석 결과 딕셔너리
    """
    prompt = portfolio_analysis_prompt(
        weights=weights,
        metrics=metrics,
        tickers_info=tickers_info,
    )

    result = call_llm_json(
        prompt=prompt,
        system_prompt=get_system_prompt(),
    )

    # 입력 데이터도 결과에 포함
    result["_input"] = {
        "weights": weights,
        "metrics": metrics,
    }

    # Hallucination 검증
    validation = validate_portfolio_analysis(result, weights, metrics)
    if not validation.is_valid:
        logger.warning(f"Portfolio analysis validation failed: {validation.violations}")
        result["_warnings"] = validation.violations

    return result


def explain_risk(
    risk_data: dict[str, float],
    investment_amount: float | None = None,
) -> dict[str, Any]:
    """
    리스크 데이터를 비전문가 언어로 설명

    Args:
        risk_data: 리스크 지표 {
            "volatility": 0.18,
            "var_95_parametric": 0.018,
            "var_99_parametric": 0.026,
            "var_95_montecarlo": 0.019,
            "var_99_montecarlo": 0.027,
            "cvar_95": 0.024,
            "cvar_99": 0.035,
            "max_loss_1d": 0.045
        }
        investment_amount: 투자 금액 (원화)

    Returns:
        구조화된 리스크 설명 딕셔너리
    """
    prompt = risk_explanation_prompt(
        risk_data=risk_data,
        investment_amount=investment_amount,
    )

    result = call_llm_json(
        prompt=prompt,
        system_prompt=get_system_prompt(),
    )

    # 입력 데이터도 결과에 포함
    result["_input"] = {
        "risk_data": risk_data,
        "investment_amount": investment_amount,
    }

    # Hallucination 검증
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
    """
    백테스트 결과 요약 + 인사이트

    Args:
        metrics: 성과 지표
        strategy: 전략명
        period: 테스트 기간
        tickers: 종목 리스트
        rebalance_history: 리밸런싱 기록 (선택)
        final_weights: 최종 비중 (선택)

    Returns:
        구조화된 백테스트 요약 딕셔너리
    """
    prompt = backtest_summary_prompt(
        metrics=metrics,
        strategy=strategy,
        period=period,
        tickers=tickers,
        rebalance_history=rebalance_history,
        final_weights=final_weights,
    )

    result = call_llm_json(
        prompt=prompt,
        system_prompt=get_system_prompt(),
    )

    # 입력 데이터도 결과에 포함
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
    """
    포트폴리오 개선 제안

    Args:
        current_portfolio: 현재 종목별 비중
        tickers_info: 종목 정보
        metrics: 현재 성과 지표
        risk_data: 현재 리스크 지표
        market_context: 시장 상황 설명
        investor_profile: 투자자 프로필

    Returns:
        구조화된 추천 딕셔너리
    """
    prompt = recommendation_prompt(
        current_portfolio=current_portfolio,
        tickers_info=tickers_info,
        metrics=metrics,
        risk_data=risk_data,
        market_context=market_context,
        investor_profile=investor_profile,
    )

    result = call_llm_json(
        prompt=prompt,
        system_prompt=get_system_prompt(),
    )

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
