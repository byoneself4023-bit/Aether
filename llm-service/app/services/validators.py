"""LLM 응답 검증 - Hallucination 방지"""

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    corrected_response: dict | None = None
    violations: list[str] = field(default_factory=list)


def extract_percentages(text: str) -> list[float]:
    """텍스트에서 퍼센트 수치 추출"""
    pattern = r'(-?\d+\.?\d*)\s*%'
    matches = re.findall(pattern, str(text))
    return [float(m) for m in matches]


def extract_tickers(text: str) -> list[str]:
    """텍스트에서 티커 심볼 추출 (한국어 혼합 텍스트 지원)"""
    pattern = r'(?<![A-Za-z])([A-Z]{2,5})(?![A-Za-z])'
    common_words = {
        "AN", "THE", "TO", "FOR", "AND", "OR", "BUT", "IS", "IT",
        "IN", "ON", "AT", "BY", "OF", "AS", "IF", "MY", "ME", "WE", "US",
        "JSON", "API", "LLM", "RAG", "MVP", "MSR", "VAR", "ETF", "IPO",
        "MDD", "CAGR", "DO", "BE", "HAS", "HAD", "CAN",
    }
    matches = re.findall(pattern, str(text))
    return [t for t in matches if t not in common_words]


def _check_numeric_consistency(
    llm_value: float,
    actual_value: float,
    tolerance: float = 0.1,
    label: str = "",
) -> str | None:
    """
    수치 일관성 검사.

    Args:
        llm_value: LLM이 응답한 수치
        actual_value: 실제 입력 데이터 수치
        tolerance: 허용 오차 비율 (기본 10%)
        label: 지표 이름

    Returns:
        violation 메시지 또는 None
    """
    if actual_value == 0:
        if abs(llm_value) > tolerance:
            return f"{label}: LLM responded {llm_value} but actual is 0"
        return None

    error_ratio = abs(llm_value - actual_value) / abs(actual_value)
    if error_ratio > tolerance:
        return (
            f"{label}: LLM responded {llm_value:.4f} but actual is {actual_value:.4f} "
            f"(error: {error_ratio:.1%}, tolerance: {tolerance:.0%})"
        )
    return None


def validate_portfolio_analysis(
    response: dict,
    input_weights: dict[str, float],
    input_metrics: dict[str, float],
) -> ValidationResult:
    """
    포트폴리오 분석 LLM 응답 검증.

    검증 항목:
    - 수익률 수치 일관성 (10% 오차 허용)
    - 존재하지 않는 티커 언급 감지
    - 샤프 비율 범위 검사 (-2 ~ 5)

    Args:
        response: LLM 분석 결과 딕셔너리
        input_weights: 입력된 종목별 비중
        input_metrics: 입력된 성과 지표

    Returns:
        ValidationResult
    """
    violations = []
    known_tickers = set(input_weights.keys())

    # 1. 응답에서 언급된 티커가 실제 입력에 있는지 확인
    response_text = str(response)
    mentioned_tickers = extract_tickers(response_text)
    for ticker in mentioned_tickers:
        if ticker not in known_tickers:
            violations.append(f"Unknown ticker mentioned: {ticker} (known: {', '.join(sorted(known_tickers))})")

    # 2. 응답에서 퍼센트 수치를 추출해서 수익률과 비교
    if "metrics_interpretation" in response:
        interp = response["metrics_interpretation"]
        if isinstance(interp, dict):
            return_text = interp.get("return_analysis", "")
            percentages = extract_percentages(return_text)
            actual_return_pct = input_metrics.get("expected_return", 0) * 100
            for pct in percentages:
                violation = _check_numeric_consistency(
                    pct, actual_return_pct, tolerance=0.1, label="Expected return"
                )
                if violation:
                    violations.append(violation)

    # 3. 샤프 비율 범위 검사
    actual_sharpe = input_metrics.get("sharpe_ratio")
    if actual_sharpe is not None:
        if actual_sharpe < -2 or actual_sharpe > 5:
            violations.append(
                f"Input Sharpe ratio out of normal range: {actual_sharpe:.2f} (expected: -2 ~ 5)"
            )

        # 응답에서 샤프 비율 수치 확인
        sharpe_text = ""
        if "metrics_interpretation" in response and isinstance(response["metrics_interpretation"], dict):
            sharpe_text = response["metrics_interpretation"].get("sharpe_analysis", "")

        sharpe_pattern = r'(?:샤프|sharpe)[^\d]*?(-?\d+\.?\d*)'
        sharpe_matches = re.findall(sharpe_pattern, str(sharpe_text), re.IGNORECASE)
        for match in sharpe_matches:
            llm_sharpe = float(match)
            violation = _check_numeric_consistency(
                llm_sharpe, actual_sharpe, tolerance=0.1, label="Sharpe ratio"
            )
            if violation:
                violations.append(violation)

    if violations:
        logger.warning(f"Portfolio analysis validation violations: {violations}")

    return ValidationResult(
        is_valid=len(violations) == 0,
        corrected_response=response,
        violations=violations,
    )


def validate_risk_analysis(
    response: dict,
    input_risk_data: dict[str, float],
) -> ValidationResult:
    """
    리스크 분석 LLM 응답 검증.

    검증 항목:
    - VaR/CVaR 수치 일관성
    - VaR 범위 검사 (0~1, 즉 0%~100%)

    Args:
        response: LLM 리스크 설명 결과
        input_risk_data: 입력된 리스크 데이터

    Returns:
        ValidationResult
    """
    violations = []

    # VaR 수치 확인
    for key in ["var_95_parametric", "var_95_montecarlo", "var_99_parametric", "var_99_montecarlo"]:
        value = input_risk_data.get(key)
        if value is not None:
            if value < 0 or value > 1:
                violations.append(f"VaR value out of range [0, 1]: {key}={value}")

    # CVaR 수치 확인
    for key in ["cvar_95", "cvar_99"]:
        value = input_risk_data.get(key)
        if value is not None:
            if value < 0 or value > 1:
                violations.append(f"CVaR value out of range [0, 1]: {key}={value}")

    # 응답에서 VaR 퍼센트 수치 추출 및 비교
    if "var_explanation" in response and isinstance(response["var_explanation"], dict):
        var_text = response["var_explanation"].get("simple_explanation", "")
        var_text += " " + response["var_explanation"].get("technical_detail", "")
        percentages = extract_percentages(var_text)

        actual_var_95_pct = input_risk_data.get("var_95_montecarlo", 0) * 100
        for pct in percentages:
            # VaR 퍼센트는 보통 작은 수치 (1~5% 범위)
            if 0 < pct < 50:
                violation = _check_numeric_consistency(
                    pct, actual_var_95_pct, tolerance=0.1, label="VaR 95%"
                )
                if violation:
                    violations.append(violation)

    if violations:
        logger.warning(f"Risk analysis validation violations: {violations}")

    return ValidationResult(
        is_valid=len(violations) == 0,
        corrected_response=response,
        violations=violations,
    )
