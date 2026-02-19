"""Critical #3: Hallucination 검증 테스트"""

import pytest

from app.services.validators import (
    ValidationResult,
    validate_portfolio_analysis,
    validate_risk_analysis,
    extract_percentages,
    extract_tickers,
)


class TestExtractPercentages:
    def test_basic_percentages(self):
        assert extract_percentages("수익률 32.6%입니다") == [32.6]

    def test_multiple_percentages(self):
        result = extract_percentages("수익률 32.6%, 변동성 22.4%")
        assert result == [32.6, 22.4]

    def test_negative_percentage(self):
        assert extract_percentages("손실 -5.2%") == [-5.2]

    def test_no_percentages(self):
        assert extract_percentages("샤프 비율 2.09") == []


class TestExtractTickers:
    def test_basic_tickers(self):
        result = extract_tickers("AAPL과 GOOGL이 주요 종목")
        assert "AAPL" in result
        assert "GOOGL" in result

    def test_filters_common_words(self):
        result = extract_tickers("THE AAPL IS GOOD")
        assert "AAPL" in result
        assert "THE" not in result
        assert "IS" not in result


class TestValidatePortfolioAnalysis:
    """포트폴리오 분석 검증 테스트"""

    def test_valid_response_passes(self):
        """정상 응답은 통과"""
        response = {
            "summary": "LLY, NVDA, AAPL, MSFT로 구성된 포트폴리오",
            "metrics_interpretation": {
                "return_analysis": "연 32.6% 기대 수익률",
                "risk_analysis": "22.4% 변동성",
                "sharpe_analysis": "샤프 2.09는 우수",
            },
            "strengths": ["높은 수익률"],
        }
        weights = {"LLY": 0.45, "NVDA": 0.21, "AAPL": 0.18, "MSFT": 0.16}
        metrics = {"expected_return": 0.326, "volatility": 0.224, "sharpe_ratio": 2.09}

        result = validate_portfolio_analysis(response, weights, metrics)
        assert result.is_valid is True
        assert result.violations == []

    def test_wrong_return_detected(self):
        """수치 불일치 감지 (10% 초과 오차)"""
        response = {
            "summary": "포트폴리오 분석",
            "metrics_interpretation": {
                "return_analysis": "연 50.0% 기대 수익률은 매우 높은 수준",
                "sharpe_analysis": "샤프 2.09",
            },
        }
        weights = {"AAPL": 0.5, "GOOGL": 0.5}
        metrics = {"expected_return": 0.326, "volatility": 0.224, "sharpe_ratio": 2.09}

        result = validate_portfolio_analysis(response, weights, metrics)
        assert result.is_valid is False
        assert any("Expected return" in v for v in result.violations)

    def test_unknown_ticker_detected(self):
        """존재하지 않는 티커 감지"""
        response = {
            "summary": "TSLA를 추가하면 좋겠습니다",
        }
        weights = {"AAPL": 0.5, "GOOGL": 0.5}
        metrics = {"expected_return": 0.15, "volatility": 0.18, "sharpe_ratio": 0.83}

        result = validate_portfolio_analysis(response, weights, metrics)
        assert result.is_valid is False
        assert any("TSLA" in v for v in result.violations)

    def test_abnormal_sharpe_ratio_detected(self):
        """비정상 샤프 비율 감지"""
        response = {"summary": "분석 완료"}
        weights = {"AAPL": 0.5, "GOOGL": 0.5}
        metrics = {"expected_return": 0.15, "volatility": 0.01, "sharpe_ratio": 15.0}

        result = validate_portfolio_analysis(response, weights, metrics)
        assert result.is_valid is False
        assert any("Sharpe ratio out of normal range" in v for v in result.violations)

    def test_wrong_sharpe_in_response(self):
        """LLM이 잘못된 샤프 비율을 응답한 경우"""
        response = {
            "summary": "분석 완료",
            "metrics_interpretation": {
                "return_analysis": "수익률 분석",
                "sharpe_analysis": "샤프 5.0은 매우 우수한 수준입니다",
            },
        }
        weights = {"AAPL": 0.5, "GOOGL": 0.5}
        metrics = {"expected_return": 0.15, "volatility": 0.18, "sharpe_ratio": 2.09}

        result = validate_portfolio_analysis(response, weights, metrics)
        assert result.is_valid is False
        assert any("Sharpe ratio" in v for v in result.violations)

    def test_multiple_violations(self):
        """복합 violation 감지"""
        response = {
            "summary": "TSLA과 AMZN이 포함된 포트폴리오",
            "metrics_interpretation": {
                "return_analysis": "연 80.0% 기대 수익률",
                "sharpe_analysis": "샤프 2.09",
            },
        }
        weights = {"AAPL": 0.5, "GOOGL": 0.5}
        metrics = {"expected_return": 0.326, "volatility": 0.224, "sharpe_ratio": 2.09}

        result = validate_portfolio_analysis(response, weights, metrics)
        assert result.is_valid is False
        assert len(result.violations) >= 2  # unknown tickers + wrong return


class TestValidateRiskAnalysis:
    """리스크 분석 검증 테스트"""

    def test_valid_risk_passes(self):
        """정상 리스크 데이터는 통과"""
        response = {
            "summary": "중간 수준의 리스크",
            "var_explanation": {
                "simple_explanation": "100일 중 5일은 1.9% 이상 손실 가능",
                "technical_detail": "95% VaR 1.9%",
            },
        }
        risk_data = {
            "volatility": 0.224,
            "var_95_parametric": 0.018,
            "var_95_montecarlo": 0.019,
            "var_99_parametric": 0.026,
            "var_99_montecarlo": 0.027,
            "cvar_95": 0.024,
            "cvar_99": 0.035,
        }

        result = validate_risk_analysis(response, risk_data)
        assert result.is_valid is True

    def test_invalid_var_range(self):
        """VaR 범위 초과 감지"""
        response = {"summary": "리스크 분석"}
        risk_data = {
            "volatility": 0.224,
            "var_95_parametric": 1.5,  # 범위 초과
            "var_95_montecarlo": 0.019,
            "cvar_95": 0.024,
            "cvar_99": 0.035,
        }

        result = validate_risk_analysis(response, risk_data)
        assert result.is_valid is False
        assert any("out of range" in v for v in result.violations)

    def test_invalid_cvar_range(self):
        """CVaR 범위 초과 감지"""
        response = {"summary": "리스크 분석"}
        risk_data = {
            "volatility": 0.224,
            "cvar_95": 1.5,  # 범위 초과
            "cvar_99": 0.035,
        }

        result = validate_risk_analysis(response, risk_data)
        assert result.is_valid is False
        assert any("CVaR" in v for v in result.violations)
