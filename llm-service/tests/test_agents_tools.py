"""tool_registry 등록·조회·시그니처 검증 + autouse reset fixture"""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _reset_tool_registry():
    """테스트 간 _tool_registry 상태 공유 차단 (lazy init reset)."""
    import app.agents.tools as tools_mod

    tools_mod._tool_registry = None
    yield
    tools_mod._tool_registry = None


class TestToolRegistry:
    def test_register_success(self):
        from app.agents.portfolio_tools import analyze_portfolio_tool
        from app.agents.tools import ToolRegistry

        reg = ToolRegistry()
        reg.register("foo", analyze_portfolio_tool)
        assert reg.get("foo") is analyze_portfolio_tool

    def test_register_duplicate_raises(self):
        from app.agents.portfolio_tools import analyze_portfolio_tool
        from app.agents.tools import ToolRegistry

        reg = ToolRegistry()
        reg.register("foo", analyze_portfolio_tool)
        with pytest.raises(ValueError, match="already registered"):
            reg.register("foo", analyze_portfolio_tool)

    def test_get_not_found_raises(self):
        from app.agents.tools import ToolRegistry

        reg = ToolRegistry()
        with pytest.raises(KeyError, match="not found"):
            reg.get("missing")

    def test_list_all_empty(self):
        from app.agents.tools import ToolRegistry

        assert ToolRegistry().list_all() == []


class TestGetToolRegistry:
    def test_lazy_init_creates_singleton(self):
        from app.agents.tools import get_tool_registry

        reg1 = get_tool_registry()
        reg2 = get_tool_registry()
        assert reg1 is reg2

    def test_default_registers_5_tools(self):
        # D-5 / ADR 0018: search_knowledge_base 추가 (4 → 5)
        from app.agents.tools import get_tool_registry

        reg = get_tool_registry()
        names = {t.name for t in reg.list_all()}
        assert len(reg.list_all()) == 5
        assert "analyze_portfolio_tool" in names
        assert "explain_risk_tool" in names
        assert "summarize_backtest_tool" in names
        assert "get_recommendation_tool" in names
        assert "search_knowledge_base" in names


class TestPortfolioTools:
    def test_analyze_portfolio_tool_invokes_original(self):
        from app.agents.portfolio_tools import analyze_portfolio_tool

        with patch("app.agents.portfolio_tools.analyze_portfolio") as mock_orig:
            mock_orig.return_value = {"summary": "ok"}
            result = analyze_portfolio_tool.invoke(
                {
                    "weights": {"AAPL": 0.5, "GOOGL": 0.5},
                    "metrics": {"sharpe_ratio": 1.0},
                }
            )
            mock_orig.assert_called_once()
            assert result == {"summary": "ok"}

    def test_explain_risk_tool_invokes_original(self):
        from app.agents.portfolio_tools import explain_risk_tool

        with patch("app.agents.portfolio_tools.explain_risk") as mock_orig:
            mock_orig.return_value = {"explanation": "ok"}
            result = explain_risk_tool.invoke({"risk_data": {"var": 0.05}})
            mock_orig.assert_called_once()
            assert result == {"explanation": "ok"}

    def test_summarize_backtest_tool_invokes_original(self):
        from app.agents.portfolio_tools import summarize_backtest_tool

        with patch("app.agents.portfolio_tools.summarize_backtest") as mock_orig:
            mock_orig.return_value = {"summary": "ok"}
            result = summarize_backtest_tool.invoke(
                {
                    "metrics": {"sharpe": 1.0},
                    "strategy": "max_sharpe",
                    "period": "5y",
                    "tickers": ["AAPL"],
                }
            )
            mock_orig.assert_called_once()
            assert result == {"summary": "ok"}

    def test_get_recommendation_tool_invokes_original(self):
        from app.agents.portfolio_tools import get_recommendation_tool

        with patch("app.agents.portfolio_tools.get_recommendation") as mock_orig:
            mock_orig.return_value = {"recommendations": []}
            result = get_recommendation_tool.invoke({"current_portfolio": {"AAPL": 1.0}})
            mock_orig.assert_called_once()
            assert result == {"recommendations": []}
