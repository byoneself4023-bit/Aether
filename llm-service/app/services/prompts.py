"""프롬프트 템플릿 - 포트폴리오 분석 결과를 자연어로 해석"""

from jinja2 import Template
from typing import Any


# ============================================================
# JSON 응답 스키마 정의
# ============================================================

PORTFOLIO_ANALYSIS_SCHEMA = """{
  "summary": "한 문장 요약",
  "composition": {
    "description": "포트폴리오 구성 설명",
    "top_holdings": ["상위 종목 설명"],
    "sector_concentration": "섹터 집중도 분석"
  },
  "metrics_interpretation": {
    "return_analysis": "수익률 해석",
    "risk_analysis": "변동성/리스크 해석",
    "sharpe_analysis": "샤프 비율 해석"
  },
  "strengths": ["강점 1", "강점 2"],
  "weaknesses": ["약점 1", "약점 2"],
  "diversification_score": "상/중/하",
  "investor_profile": "적합한 투자자 유형"
}"""

RISK_EXPLANATION_SCHEMA = """{
  "summary": "한 문장 요약",
  "var_explanation": {
    "simple_explanation": "비전문가용 VaR 설명",
    "technical_detail": "기술적 상세 설명",
    "example_scenario": "구체적 시나리오 예시"
  },
  "cvar_explanation": {
    "simple_explanation": "비전문가용 CVaR 설명",
    "worst_case_scenario": "최악의 경우 시나리오"
  },
  "risk_level": "매우낮음/낮음/보통/높음/매우높음",
  "risk_factors": ["주요 리스크 요인"],
  "hedging_suggestions": ["리스크 완화 제안"]
}"""

BACKTEST_SUMMARY_SCHEMA = """{
  "summary": "한 문장 요약",
  "performance_highlights": {
    "total_return": "총 수익률 해석",
    "annual_return": "연환산 수익률 해석",
    "volatility": "변동성 해석",
    "sharpe_ratio": "샤프 비율 해석"
  },
  "drawdown_analysis": {
    "max_drawdown": "최대 낙폭 해석",
    "recovery_insight": "회복 관련 인사이트"
  },
  "rebalancing_analysis": {
    "frequency": "리밸런싱 빈도 평가",
    "turnover_impact": "거래비용 영향 분석"
  },
  "period_breakdown": ["기간별 주요 이벤트"],
  "strategy_effectiveness": "전략 효과성 평가",
  "forward_outlook": "향후 전망"
}"""

RECOMMENDATION_SCHEMA = """{
  "summary": "한 문장 요약",
  "current_assessment": "현재 포트폴리오 평가",
  "recommendations": [
    {
      "action": "매수/매도/유지/리밸런싱",
      "target": "대상 종목/섹터",
      "rationale": "근거",
      "priority": "상/중/하"
    }
  ],
  "risk_adjustments": ["리스크 조정 제안"],
  "sector_rebalancing": {
    "overweight": ["비중 확대 섹터"],
    "underweight": ["비중 축소 섹터"]
  },
  "action_timeline": "단기/중기/장기 액션 플랜",
  "caveats": ["주의사항/한계"]
}"""


# ============================================================
# 프롬프트 템플릿
# ============================================================

PORTFOLIO_ANALYSIS_TEMPLATE = Template("""당신은 전문 포트폴리오 분석가입니다. 주어진 포트폴리오 데이터를 분석하여 투자자가 이해하기 쉬운 한국어로 설명해주세요.

## 포트폴리오 구성
{% for ticker, weight in weights.items() %}
- {{ ticker }}: {{ "%.1f"|format(weight * 100) }}%{% if tickers_info and ticker in tickers_info %} ({{ tickers_info[ticker].get('name', '') }}, {{ tickers_info[ticker].get('sector', '') }}){% endif %}
{% endfor %}

## 성과 지표
- 기대 수익률 (연율): {{ "%.2f"|format(metrics.expected_return * 100) }}%
- 변동성 (연율): {{ "%.2f"|format(metrics.volatility * 100) }}%
- 샤프 비율: {{ "%.2f"|format(metrics.sharpe_ratio) }}
{% if metrics.get('max_drawdown') %}
- 최대 낙폭: {{ "%.2f"|format(metrics.max_drawdown * 100) }}%
{% endif %}

## 분석 요청
1. 포트폴리오 구성을 자연스러운 문장으로 설명하세요
2. 섹터 집중도와 분산 수준을 평가하세요
3. 성과 지표를 비전문가도 이해할 수 있게 해석하세요
4. 이 포트폴리오의 강점과 약점을 분석하세요
5. 적합한 투자자 유형을 제안하세요

## 응답 형식
반드시 아래 JSON 스키마에 맞춰 응답하세요. JSON만 출력하고 다른 텍스트는 포함하지 마세요.

{{ schema }}
""")


RISK_EXPLANATION_TEMPLATE = Template("""당신은 리스크 관리 전문가입니다. 주어진 리스크 분석 결과를 투자 경험이 없는 일반인도 이해할 수 있도록 쉽게 설명해주세요.

## 리스크 분석 결과
- 포트폴리오 변동성 (연율): {{ "%.2f"|format(risk_data.volatility * 100) }}%

### Parametric VaR (정규분포 가정)
- 95% VaR (1일): {{ "%.2f"|format(risk_data.var_95_parametric * 100) }}%
- 99% VaR (1일): {{ "%.2f"|format(risk_data.var_99_parametric * 100) }}%

### Monte Carlo VaR (시뮬레이션 기반)
- 95% VaR (1일): {{ "%.2f"|format(risk_data.var_95_montecarlo * 100) }}%
- 99% VaR (1일): {{ "%.2f"|format(risk_data.var_99_montecarlo * 100) }}%

### CVaR (Expected Shortfall)
- 95% CVaR: {{ "%.2f"|format(risk_data.cvar_95 * 100) }}%
- 99% CVaR: {{ "%.2f"|format(risk_data.cvar_99 * 100) }}%

### 최대 예상 손실
- 1일 최대 예상 손실 (99.9%): {{ "%.2f"|format(risk_data.max_loss_1d * 100) }}%

{% if investment_amount %}
## 투자 금액 기준 분석
- 투자 금액: {{ "{:,.0f}".format(investment_amount) }}원
- 95% VaR 손실 금액: {{ "{:,.0f}".format(investment_amount * risk_data.var_95_montecarlo) }}원
- 99% VaR 손실 금액: {{ "{:,.0f}".format(investment_amount * risk_data.var_99_montecarlo) }}원
{% endif %}

## 설명 요청
1. VaR를 "100일 중 X일은 Y% 이상 손실이 발생할 수 있습니다" 형식으로 설명하세요
2. CVaR(Expected Shortfall)이 왜 VaR보다 보수적인 지표인지 설명하세요
3. 이 포트폴리오의 리스크 수준을 5단계로 평가하세요
4. 주요 리스크 요인과 완화 방안을 제시하세요

## 응답 형식
반드시 아래 JSON 스키마에 맞춰 응답하세요. JSON만 출력하고 다른 텍스트는 포함하지 마세요.

{{ schema }}
""")


BACKTEST_SUMMARY_TEMPLATE = Template("""당신은 퀀트 전략 분석가입니다. 백테스트 결과를 분석하여 전략의 성과와 특성을 명확하게 설명해주세요.

## 백테스트 개요
- 전략: {{ strategy }}
- 테스트 기간: {{ period }}
- 종목: {{ tickers | join(', ') }}
- 리밸런싱 횟수: {{ metrics.n_rebalances }}회

## 성과 지표
- 누적 수익률: {{ "%.1f"|format(metrics.total_return * 100) }}%
- 연환산 수익률 (CAGR): {{ "%.1f"|format(metrics.annual_return * 100) }}%
- 연환산 변동성: {{ "%.1f"|format(metrics.annual_volatility * 100) }}%
- 샤프 비율: {{ "%.2f"|format(metrics.sharpe_ratio) }}
- 최대 낙폭 (MDD): {{ "%.1f"|format(metrics.max_drawdown * 100) }}%
- 칼마 비율: {{ "%.2f"|format(metrics.calmar_ratio) }}
- 평균 턴오버: {{ "%.1f"|format(metrics.avg_turnover * 100) }}%
- 승률: {{ "%.1f"|format(metrics.win_rate * 100) }}%

{% if rebalance_history %}
## 최근 리밸런싱 기록
{% for record in rebalance_history[-5:] %}
- {{ record.date }}: 턴오버 {{ "%.1f"|format(record.turnover * 100) }}%
{% endfor %}
{% endif %}

{% if final_weights %}
## 최종 비중
{% for ticker, weight in final_weights.items() %}
- {{ ticker }}: {{ "%.1f"|format(weight * 100) }}%
{% endfor %}
{% endif %}

## 분석 요청
1. 백테스트 결과를 한 문장으로 요약하세요 (예: "3년간 연 42.6% 수익, 최대 낙폭 13.6%")
2. 각 성과 지표가 의미하는 바를 해석하세요
3. 최대 낙폭 시점과 회복에 대한 인사이트를 제공하세요
4. 리밸런싱 전략의 효과성을 평가하세요
5. 이 전략의 향후 전망을 제시하세요

## 응답 형식
반드시 아래 JSON 스키마에 맞춰 응답하세요. JSON만 출력하고 다른 텍스트는 포함하지 마세요.

{{ schema }}
""")


RECOMMENDATION_TEMPLATE = Template("""당신은 자산배분 전문 어드바이저입니다. 현재 포트폴리오와 시장 상황을 분석하여 구체적인 개선 제안을 해주세요.

## 현재 포트폴리오
{% for ticker, weight in current_portfolio.items() %}
- {{ ticker }}: {{ "%.1f"|format(weight * 100) }}%{% if tickers_info and ticker in tickers_info %} ({{ tickers_info[ticker].get('sector', '') }}){% endif %}
{% endfor %}

## 현재 성과 지표
{% if metrics %}
- 기대 수익률: {{ "%.2f"|format(metrics.expected_return * 100) }}%
- 변동성: {{ "%.2f"|format(metrics.volatility * 100) }}%
- 샤프 비율: {{ "%.2f"|format(metrics.sharpe_ratio) }}
{% endif %}

{% if risk_data %}
## 리스크 현황
- 95% VaR: {{ "%.2f"|format(risk_data.var_95 * 100) }}%
- 99% CVaR: {{ "%.2f"|format(risk_data.cvar_99 * 100) }}%
{% endif %}

{% if market_context %}
## 시장 상황
{{ market_context }}
{% endif %}

{% if investor_profile %}
## 투자자 프로필
- 투자 성향: {{ investor_profile.risk_tolerance }}
- 투자 기간: {{ investor_profile.investment_horizon }}
- 투자 목표: {{ investor_profile.investment_goal }}
{% endif %}

## 분석 요청
1. 현재 포트폴리오의 전반적인 상태를 평가하세요
2. 구체적인 리밸런싱 제안을 우선순위와 함께 제시하세요
3. 섹터별 비중 조정 방향을 제안하세요
4. 리스크 관리를 위한 조정 사항을 제시하세요
5. 단기/중기/장기 액션 플랜을 제안하세요

## 주의사항
- 모든 제안은 근거와 함께 제시하세요
- 투자 결정은 개인의 판단이며, 이 분석은 참고용임을 명시하세요

## 응답 형식
반드시 아래 JSON 스키마에 맞춰 응답하세요. JSON만 출력하고 다른 텍스트는 포함하지 마세요.

{{ schema }}
""")


# ============================================================
# 프롬프트 생성 함수
# ============================================================

def portfolio_analysis_prompt(
    weights: dict[str, float],
    metrics: dict[str, float],
    tickers_info: dict[str, dict] | None = None
) -> str:
    """
    포트폴리오 분석 프롬프트 생성

    Args:
        weights: 종목별 비중 {"AAPL": 0.3, "GOOGL": 0.2, ...}
        metrics: 성과 지표 {
            "expected_return": 0.15,
            "volatility": 0.18,
            "sharpe_ratio": 0.83,
            "max_drawdown": 0.12  # optional
        }
        tickers_info: 종목 정보 {
            "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
            ...
        }

    Returns:
        렌더링된 프롬프트 문자열
    """
    return PORTFOLIO_ANALYSIS_TEMPLATE.render(
        weights=weights,
        metrics=metrics,
        tickers_info=tickers_info or {},
        schema=PORTFOLIO_ANALYSIS_SCHEMA
    )


def risk_explanation_prompt(
    risk_data: dict[str, float],
    investment_amount: float | None = None
) -> str:
    """
    리스크 설명 프롬프트 생성

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
        렌더링된 프롬프트 문자열
    """
    # dict를 객체처럼 접근할 수 있도록 변환
    class RiskDataWrapper:
        def __init__(self, data: dict):
            for key, value in data.items():
                setattr(self, key, value)

    return RISK_EXPLANATION_TEMPLATE.render(
        risk_data=RiskDataWrapper(risk_data),
        investment_amount=investment_amount,
        schema=RISK_EXPLANATION_SCHEMA
    )


def backtest_summary_prompt(
    metrics: dict[str, float],
    strategy: str,
    period: str,
    tickers: list[str],
    rebalance_history: list[dict] | None = None,
    final_weights: dict[str, float] | None = None
) -> str:
    """
    백테스트 요약 프롬프트 생성

    Args:
        metrics: 성과 지표 {
            "total_return": 1.28,
            "annual_return": 0.426,
            "annual_volatility": 0.22,
            "sharpe_ratio": 1.94,
            "max_drawdown": 0.136,
            "calmar_ratio": 3.13,
            "avg_turnover": 0.15,
            "win_rate": 0.54,
            "n_rebalances": 12
        }
        strategy: 전략명 ("max_sharpe", "min_variance", "equal_weight")
        period: 테스트 기간 ("3y", "5y", ...)
        tickers: 종목 리스트
        rebalance_history: 리밸런싱 기록 [{"date": "2023-01-15", "turnover": 0.08}, ...]
        final_weights: 최종 비중

    Returns:
        렌더링된 프롬프트 문자열
    """
    # dict를 객체처럼 접근할 수 있도록 변환
    class MetricsWrapper:
        def __init__(self, data: dict):
            for key, value in data.items():
                setattr(self, key, value)

    strategy_names = {
        "max_sharpe": "최대 샤프 비율 (MSR)",
        "min_variance": "최소 분산 (MVP)",
        "equal_weight": "동일 비중"
    }

    return BACKTEST_SUMMARY_TEMPLATE.render(
        metrics=MetricsWrapper(metrics),
        strategy=strategy_names.get(strategy, strategy),
        period=period,
        tickers=tickers,
        rebalance_history=rebalance_history,
        final_weights=final_weights,
        schema=BACKTEST_SUMMARY_SCHEMA
    )


def recommendation_prompt(
    current_portfolio: dict[str, float],
    tickers_info: dict[str, dict] | None = None,
    metrics: dict[str, float] | None = None,
    risk_data: dict[str, float] | None = None,
    market_context: str | None = None,
    investor_profile: dict[str, str] | None = None
) -> str:
    """
    포트폴리오 개선 제안 프롬프트 생성

    Args:
        current_portfolio: 현재 종목별 비중
        tickers_info: 종목 정보
        metrics: 현재 성과 지표
        risk_data: 현재 리스크 지표
        market_context: 시장 상황 설명 (텍스트)
        investor_profile: 투자자 프로필 {
            "risk_tolerance": "중립",
            "investment_horizon": "3-5년",
            "investment_goal": "자산 증식"
        }

    Returns:
        렌더링된 프롬프트 문자열
    """
    # dict를 객체처럼 접근할 수 있도록 변환
    class DictWrapper:
        def __init__(self, data: dict):
            for key, value in data.items():
                setattr(self, key, value)

    return RECOMMENDATION_TEMPLATE.render(
        current_portfolio=current_portfolio,
        tickers_info=tickers_info or {},
        metrics=DictWrapper(metrics) if metrics else None,
        risk_data=DictWrapper(risk_data) if risk_data else None,
        market_context=market_context,
        investor_profile=DictWrapper(investor_profile) if investor_profile else None,
        schema=RECOMMENDATION_SCHEMA
    )


# ============================================================
# 시스템 프롬프트
# ============================================================

SYSTEM_PROMPT = """당신은 Aether 포트폴리오 분석 AI입니다.

역할:
- 포트폴리오 최적화 결과를 자연어로 해석
- 리스크 지표를 비전문가도 이해할 수 있게 설명
- 백테스트 결과 분석 및 전략 평가
- 데이터 기반 투자 제안

원칙:
1. 항상 한국어로 응답합니다
2. 전문 용어는 쉬운 설명을 함께 제공합니다
3. 수치는 맥락과 함께 해석합니다
4. 모든 분석은 근거를 명시합니다
5. 투자 결정은 개인의 책임임을 상기시킵니다

응답 형식:
- 요청된 JSON 스키마를 정확히 따릅니다
- JSON 외의 텍스트는 출력하지 않습니다
- 모든 숫자는 적절한 정밀도로 표시합니다
"""


def get_system_prompt(version: str | None = None) -> str:
    """
    시스템 프롬프트 반환.

    레지스트리에 등록된 버전이 있으면 사용, 없으면 기본값 반환.

    Args:
        version: 특정 버전 (None이면 최신)

    Returns:
        시스템 프롬프트 문자열
    """
    try:
        from app.services.prompt_registry import get_registry
        registry = get_registry()
        prompt = registry.get("system_prompt", version=version)
        return prompt.template
    except (KeyError, ImportError):
        return SYSTEM_PROMPT
