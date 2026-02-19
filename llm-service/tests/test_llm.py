"""LLM 서비스 테스트 - Mock으로 API 호출 없이 테스트"""

import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.llm import (
    call_llm,
    call_llm_json,
    analyze_portfolio,
    explain_risk,
    summarize_backtest,
    get_recommendation,
    check_api_key,
    get_model_info,
    LLMError,
    JSONParseError,
)
from app.services.llm_provider import _extract_json


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_weights():
    return {
        "LLY": 0.45,
        "NVDA": 0.21,
        "AAPL": 0.18,
        "MSFT": 0.16,
    }


@pytest.fixture
def sample_metrics():
    return {
        "expected_return": 0.326,
        "volatility": 0.224,
        "sharpe_ratio": 2.09,
        "max_drawdown": 0.136,
    }


@pytest.fixture
def sample_tickers_info():
    return {
        "LLY": {"name": "Eli Lilly", "sector": "Healthcare"},
        "NVDA": {"name": "NVIDIA", "sector": "Technology"},
        "AAPL": {"name": "Apple", "sector": "Technology"},
        "MSFT": {"name": "Microsoft", "sector": "Technology"},
    }


@pytest.fixture
def sample_risk_data():
    return {
        "volatility": 0.224,
        "var_95_parametric": 0.018,
        "var_99_parametric": 0.026,
        "var_95_montecarlo": 0.019,
        "var_99_montecarlo": 0.027,
        "cvar_95": 0.024,
        "cvar_99": 0.035,
        "max_loss_1d": 0.045,
    }


@pytest.fixture
def sample_backtest_metrics():
    return {
        "total_return": 1.28,
        "annual_return": 0.426,
        "annual_volatility": 0.22,
        "sharpe_ratio": 1.94,
        "max_drawdown": 0.136,
        "calmar_ratio": 3.13,
        "avg_turnover": 0.15,
        "win_rate": 0.54,
        "n_rebalances": 12,
    }


@pytest.fixture
def mock_portfolio_analysis_response():
    return json.dumps({
        "summary": "이 포트폴리오는 헬스케어와 기술주 중심으로 구성되어 있습니다.",
        "composition": {
            "description": "LLY 45%, NVDA 21%, AAPL 18%, MSFT 16%로 구성",
            "top_holdings": ["Eli Lilly가 최대 비중"],
            "sector_concentration": "기술주 55% 집중"
        },
        "metrics_interpretation": {
            "return_analysis": "연 32.6% 기대 수익률은 매우 높은 수준",
            "risk_analysis": "22.4% 변동성은 보통 수준",
            "sharpe_analysis": "샤프 2.09는 우수한 위험조정수익률"
        },
        "strengths": ["높은 샤프 비율", "분산 투자"],
        "weaknesses": ["기술주 집중 리스크"],
        "diversification_score": "중",
        "investor_profile": "공격적 투자자"
    })


@pytest.fixture
def mock_risk_explanation_response():
    return json.dumps({
        "summary": "이 포트폴리오는 중간 수준의 리스크를 가지고 있습니다.",
        "var_explanation": {
            "simple_explanation": "100일 중 5일은 1.9% 이상 손실이 발생할 수 있습니다",
            "technical_detail": "95% 신뢰수준 VaR 1.9%",
            "example_scenario": "1억 투자 시 190만원 손실 가능"
        },
        "cvar_explanation": {
            "simple_explanation": "최악의 5% 상황에서 평균 2.4% 손실",
            "worst_case_scenario": "극단적 상황에서 4.5% 손실 가능"
        },
        "risk_level": "보통",
        "risk_factors": ["기술주 변동성", "금리 리스크"],
        "hedging_suggestions": ["채권 비중 추가", "섹터 분산"]
    })


@pytest.fixture
def mock_backtest_summary_response():
    return json.dumps({
        "summary": "3년간 연 42.6% 수익, 최대 낙폭 13.6%",
        "performance_highlights": {
            "total_return": "128% 누적 수익률 달성",
            "annual_return": "연 42.6%로 시장 대비 우수",
            "volatility": "22% 변동성은 적정 수준",
            "sharpe_ratio": "1.94는 매우 우수"
        },
        "drawdown_analysis": {
            "max_drawdown": "13.6% 최대 낙폭은 관리 가능한 수준",
            "recovery_insight": "낙폭 후 빠른 회복"
        },
        "rebalancing_analysis": {
            "frequency": "분기별 리밸런싱 적정",
            "turnover_impact": "15% 턴오버로 거래비용 최소화"
        },
        "period_breakdown": ["2023년 AI 랠리 수혜"],
        "strategy_effectiveness": "MSR 전략이 효과적으로 작동",
        "forward_outlook": "지속 가능한 성과 기대"
    })


# ============================================================
# _extract_json 테스트
# ============================================================

class TestExtractJson:
    def test_plain_json(self):
        text = '{"key": "value"}'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_json_with_markdown_block(self):
        text = '```json\n{"key": "value"}\n```'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_json_with_surrounding_text(self):
        text = 'Here is the result:\n{"key": "value"}\nEnd of response.'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_nested_json(self):
        text = '{"outer": {"inner": "value"}}'
        result = _extract_json(text)
        assert result == {"outer": {"inner": "value"}}

    def test_invalid_json_raises(self):
        text = "not valid json"
        with pytest.raises(json.JSONDecodeError):
            _extract_json(text)


# ============================================================
# call_llm 테스트
# ============================================================

class TestCallLLM:
    @patch("app.services.llm.get_llm_provider")
    def test_call_llm_success(self, mock_get_provider):
        # Setup
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "Hello, world!"
        mock_get_provider.return_value = mock_provider

        # Execute
        result = call_llm("Test prompt")

        # Assert
        assert result == "Hello, world!"
        mock_provider.generate.assert_called_once()

    @patch("app.services.llm.get_llm_provider")
    def test_call_llm_no_api_key(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.generate.side_effect = LLMError("GOOGLE_API_KEY not configured")
        mock_get_provider.return_value = mock_provider

        with pytest.raises(LLMError, match="GOOGLE_API_KEY not configured"):
            call_llm("Test prompt")

    @patch("app.services.llm.get_llm_provider")
    def test_call_llm_with_system_prompt(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "Response"
        mock_get_provider.return_value = mock_provider

        call_llm("User prompt", system_prompt="System prompt")

        # Verify system prompt is passed to provider
        call_args = mock_provider.generate.call_args
        assert call_args.kwargs["system_prompt"] == "System prompt"
        assert call_args.kwargs["prompt"] == "User prompt"


# ============================================================
# call_llm_json 테스트
# ============================================================

class TestCallLLMJson:
    @patch("app.services.llm.get_llm_provider")
    def test_call_llm_json_success(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.generate_json.return_value = {"result": "success"}
        mock_get_provider.return_value = mock_provider

        result = call_llm_json("Test prompt")

        assert result == {"result": "success"}

    @patch("app.services.llm.get_llm_provider")
    def test_call_llm_json_with_markdown(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.generate_json.return_value = {"result": "success"}
        mock_get_provider.return_value = mock_provider

        result = call_llm_json("Test prompt")

        assert result == {"result": "success"}

    @patch("app.services.llm.get_llm_provider")
    def test_call_llm_json_parse_error_propagates(self, mock_get_provider):
        """Provider에서 JSONParseError가 발생하면 전파"""
        mock_provider = MagicMock()
        mock_provider.generate_json.side_effect = JSONParseError("parse error")
        mock_get_provider.return_value = mock_provider

        with pytest.raises(JSONParseError):
            call_llm_json("Test prompt")


# ============================================================
# 고수준 분석 함수 테스트
# ============================================================

class TestAnalyzePortfolio:
    @patch("app.services.llm.call_llm_json")
    def test_analyze_portfolio_success(
        self,
        mock_call_llm_json,
        sample_weights,
        sample_metrics,
        sample_tickers_info,
        mock_portfolio_analysis_response,
    ):
        mock_call_llm_json.return_value = json.loads(mock_portfolio_analysis_response)

        result = analyze_portfolio(
            weights=sample_weights,
            metrics=sample_metrics,
            tickers_info=sample_tickers_info,
        )

        assert "summary" in result
        assert "composition" in result
        assert "strengths" in result
        assert "_input" in result
        assert result["_input"]["weights"] == sample_weights

    @patch("app.services.llm.call_llm_json")
    def test_analyze_portfolio_without_tickers_info(
        self,
        mock_call_llm_json,
        sample_weights,
        sample_metrics,
        mock_portfolio_analysis_response,
    ):
        mock_call_llm_json.return_value = json.loads(mock_portfolio_analysis_response)

        result = analyze_portfolio(
            weights=sample_weights,
            metrics=sample_metrics,
        )

        assert "summary" in result
        mock_call_llm_json.assert_called_once()


class TestExplainRisk:
    @patch("app.services.llm.call_llm_json")
    def test_explain_risk_success(
        self,
        mock_call_llm_json,
        sample_risk_data,
        mock_risk_explanation_response,
    ):
        mock_call_llm_json.return_value = json.loads(mock_risk_explanation_response)

        result = explain_risk(
            risk_data=sample_risk_data,
            investment_amount=100000000,
        )

        assert "summary" in result
        assert "var_explanation" in result
        assert "risk_level" in result
        assert result["_input"]["investment_amount"] == 100000000

    @patch("app.services.llm.call_llm_json")
    def test_explain_risk_without_amount(
        self,
        mock_call_llm_json,
        sample_risk_data,
        mock_risk_explanation_response,
    ):
        mock_call_llm_json.return_value = json.loads(mock_risk_explanation_response)

        result = explain_risk(risk_data=sample_risk_data)

        assert "summary" in result
        assert result["_input"]["investment_amount"] is None


class TestSummarizeBacktest:
    @patch("app.services.llm.call_llm_json")
    def test_summarize_backtest_success(
        self,
        mock_call_llm_json,
        sample_backtest_metrics,
        mock_backtest_summary_response,
    ):
        mock_call_llm_json.return_value = json.loads(mock_backtest_summary_response)

        result = summarize_backtest(
            metrics=sample_backtest_metrics,
            strategy="max_sharpe",
            period="3y",
            tickers=["LLY", "NVDA", "AAPL", "MSFT"],
        )

        assert "summary" in result
        assert "performance_highlights" in result
        assert result["_input"]["strategy"] == "max_sharpe"

    @patch("app.services.llm.call_llm_json")
    def test_summarize_backtest_with_history(
        self,
        mock_call_llm_json,
        sample_backtest_metrics,
        mock_backtest_summary_response,
    ):
        mock_call_llm_json.return_value = json.loads(mock_backtest_summary_response)

        rebalance_history = [
            {"date": "2023-01-15", "turnover": 0.08},
            {"date": "2023-04-15", "turnover": 0.12},
        ]

        result = summarize_backtest(
            metrics=sample_backtest_metrics,
            strategy="max_sharpe",
            period="3y",
            tickers=["LLY", "NVDA"],
            rebalance_history=rebalance_history,
            final_weights={"LLY": 0.5, "NVDA": 0.5},
        )

        assert "summary" in result


class TestGetRecommendation:
    @patch("app.services.llm.call_llm_json")
    def test_get_recommendation_success(
        self,
        mock_call_llm_json,
        sample_weights,
    ):
        mock_response = {
            "summary": "포트폴리오 조정이 필요합니다",
            "current_assessment": "기술주 집중",
            "recommendations": [
                {
                    "action": "매도",
                    "target": "기술주",
                    "rationale": "집중도 완화",
                    "priority": "중"
                }
            ],
            "risk_adjustments": ["채권 추가"],
            "sector_rebalancing": {
                "overweight": ["헬스케어"],
                "underweight": ["기술"]
            },
            "action_timeline": "단기 조정 권장",
            "caveats": ["시장 상황에 따라 변동"]
        }
        mock_call_llm_json.return_value = mock_response

        result = get_recommendation(
            current_portfolio=sample_weights,
            market_context="금리 인상 국면",
            investor_profile={
                "risk_tolerance": "중립",
                "investment_horizon": "3-5년",
                "investment_goal": "자산 증식"
            }
        )

        assert "summary" in result
        assert "recommendations" in result


# ============================================================
# 유틸리티 함수 테스트
# ============================================================

class TestUtilityFunctions:
    @patch("app.services.llm.settings")
    def test_check_api_key_configured(self, mock_settings):
        mock_settings.google_api_key = "test-key"
        assert check_api_key() is True

    @patch("app.services.llm.settings")
    def test_check_api_key_not_configured(self, mock_settings):
        mock_settings.google_api_key = ""
        assert check_api_key() is False

    @patch("app.services.llm.settings")
    def test_get_model_info(self, mock_settings):
        mock_settings.llm_model = "gemini-2.5-flash"
        mock_settings.llm_temperature = 0.7
        mock_settings.llm_max_tokens = 2048
        mock_settings.llm_timeout = 30
        mock_settings.google_api_key = "test-key"

        info = get_model_info()

        assert info["model"] == "gemini-2.5-flash"
        assert info["temperature"] == 0.7
        assert info["api_key_configured"] is True
