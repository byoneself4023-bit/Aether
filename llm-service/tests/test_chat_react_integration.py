"""chat.py:331-356 통합 테스트 - ReAct 경로 (opt-in) vs fallback (autouse 기본)"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _full_analysis_mock_data() -> dict:
    return {
        "optimization": {
            "weights": {"AAPL": 0.5, "GOOGL": 0.5},
            "metrics": {
                "expected_return": 0.15,
                "volatility": 0.18,
                "sharpe_ratio": 0.83,
            },
        },
        "risk": {
            "risk_summary": {
                "var_95_montecarlo": 0.02,
                "cvar_99": 0.03,
            },
        },
        "backtest": {
            "metrics": {
                "total_return": 0.5,
                "annual_return": 0.2,
                "sharpe_ratio": 1.5,
                "max_drawdown": 0.1,
            },
            "final_weights": {"AAPL": 0.5, "GOOGL": 0.5},
        },
        "summary": {},
    }


@pytest.mark.use_react_agent
class TestChatReActIntegration:
    @patch("app.routers.chat.ReActAgent")
    @patch("app.routers.chat.is_available")
    @patch("app.routers.chat.get_full_analysis")
    def test_react_path_returns_analysis_response(self, mock_full, mock_avail, mock_react_cls):
        mock_avail.return_value = True
        mock_full.return_value = _full_analysis_mock_data()
        mock_instance = mock_react_cls.return_value
        mock_instance.run = AsyncMock(
            return_value={
                "portfolio_analysis": {"summary": "ReAct PA"},
                "risk_analysis": {"summary": "ReAct RA"},
                "backtest_analysis": {"summary": "ReAct BA"},
                "recommendation": {"summary": "ReAct REC"},
            }
        )

        response = client.post(
            "/api/chat/analyze",
            json={"tickers": ["AAPL", "GOOGL"], "strategy": "max_sharpe"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["portfolio_analysis"] == {"summary": "ReAct PA"}
        assert data["risk_analysis"] == {"summary": "ReAct RA"}
        assert data["backtest_analysis"] == {"summary": "ReAct BA"}
        assert data["recommendation"] == {"summary": "ReAct REC"}
        assert "portfolio_data" in data

    @patch("app.routers.chat.ReActAgent")
    @patch("app.routers.chat.is_available")
    @patch("app.routers.chat.get_full_analysis")
    def test_react_path_calls_react_agent_run(self, mock_full, mock_avail, mock_react_cls):
        mock_avail.return_value = True
        mock_full.return_value = _full_analysis_mock_data()
        mock_instance = mock_react_cls.return_value
        mock_instance.run = AsyncMock(return_value={})

        client.post(
            "/api/chat/analyze",
            json={"tickers": ["AAPL", "GOOGL"], "strategy": "max_sharpe"},
        )

        mock_react_cls.assert_called_once()
        mock_instance.run.assert_awaited_once()

    @patch("app.routers.chat.get_recommendation")
    @patch("app.routers.chat.summarize_backtest")
    @patch("app.routers.chat.explain_risk")
    @patch("app.routers.chat.analyze_portfolio")
    @patch("app.routers.chat.ReActAgent")
    @patch("app.routers.chat.is_available")
    @patch("app.routers.chat.get_full_analysis")
    def test_react_path_does_not_call_procedural_funcs(
        self,
        mock_full,
        mock_avail,
        mock_react_cls,
        mock_analyze,
        mock_risk,
        mock_bt,
        mock_rec,
    ):
        mock_avail.return_value = True
        mock_full.return_value = _full_analysis_mock_data()
        mock_react_cls.return_value.run = AsyncMock(return_value={})

        client.post(
            "/api/chat/analyze",
            json={"tickers": ["AAPL", "GOOGL"], "strategy": "max_sharpe"},
        )

        mock_analyze.assert_not_called()
        mock_risk.assert_not_called()
        mock_bt.assert_not_called()
        mock_rec.assert_not_called()


class TestChatFallback:
    @patch("app.routers.chat.get_recommendation")
    @patch("app.routers.chat.summarize_backtest")
    @patch("app.routers.chat.explain_risk")
    @patch("app.routers.chat.analyze_portfolio")
    @patch("app.routers.chat.is_available")
    @patch("app.routers.chat.get_full_analysis")
    def test_fallback_calls_4_procedural_funcs(
        self,
        mock_full,
        mock_avail,
        mock_analyze,
        mock_risk,
        mock_bt,
        mock_rec,
    ):
        """USE_REACT_AGENT=False (autouse 기본) - 기존 4 함수 호출."""
        mock_avail.return_value = True
        mock_full.return_value = _full_analysis_mock_data()
        mock_analyze.return_value = {"summary": "fallback PA"}
        mock_risk.return_value = {"summary": "fallback RA"}
        mock_bt.return_value = {"summary": "fallback BA"}
        mock_rec.return_value = {"summary": "fallback REC"}

        response = client.post(
            "/api/chat/analyze",
            json={"tickers": ["AAPL", "GOOGL"], "strategy": "max_sharpe"},
        )

        assert response.status_code == 200
        mock_analyze.assert_called_once()
        mock_risk.assert_called_once()
        mock_bt.assert_called_once()
        mock_rec.assert_called_once()
        data = response.json()
        assert data["portfolio_analysis"] == {"summary": "fallback PA"}
