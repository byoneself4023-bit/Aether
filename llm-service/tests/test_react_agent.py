"""ReActAgent 단위 테스트 - _extract_tool_results 어댑터 + run() mock"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest


def _tool_msg(name: str, content):
    """ToolMessage 흉내 - getattr(message, 'name')과 .content 속성 보유."""
    return SimpleNamespace(name=name, content=content)


def _human_msg(text: str):
    """HumanMessage 흉내 - name 속성 없음."""
    return SimpleNamespace(content=text)


class TestExtractToolResults:
    def _make_agent_no_init(self):
        """create_react_agent 호출을 우회하고 _extract_tool_results만 검증."""
        from app.agents.react_agent import ReActAgent

        agent = ReActAgent.__new__(ReActAgent)
        return agent

    def test_extract_all_4_tools(self):
        agent = self._make_agent_no_init()
        result = {
            "messages": [
                _human_msg("input"),
                _tool_msg("analyze_portfolio_tool", json.dumps({"summary": "PA"})),
                _tool_msg("explain_risk_tool", json.dumps({"summary": "RA"})),
                _tool_msg("summarize_backtest_tool", json.dumps({"summary": "BA"})),
                _tool_msg("get_recommendation_tool", json.dumps({"summary": "REC"})),
            ]
        }
        out = agent._extract_tool_results(result)
        assert out["portfolio_analysis"] == {"summary": "PA"}
        assert out["risk_analysis"] == {"summary": "RA"}
        assert out["backtest_analysis"] == {"summary": "BA"}
        assert out["recommendation"] == {"summary": "REC"}

    def test_extract_partial_tools(self):
        agent = self._make_agent_no_init()
        result = {
            "messages": [
                _tool_msg("analyze_portfolio_tool", json.dumps({"summary": "PA"})),
                _tool_msg("explain_risk_tool", json.dumps({"summary": "RA"})),
            ]
        }
        out = agent._extract_tool_results(result)
        assert "portfolio_analysis" in out
        assert "risk_analysis" in out
        assert "backtest_analysis" not in out
        assert "recommendation" not in out

    def test_extract_dict_content_passthrough(self):
        agent = self._make_agent_no_init()
        result = {
            "messages": [
                _tool_msg("analyze_portfolio_tool", {"summary": "already dict"}),
            ]
        }
        out = agent._extract_tool_results(result)
        assert out["portfolio_analysis"] == {"summary": "already dict"}

    def test_extract_non_json_string_wraps_in_summary(self):
        agent = self._make_agent_no_init()
        result = {
            "messages": [
                _tool_msg("analyze_portfolio_tool", "plain text not json"),
            ]
        }
        out = agent._extract_tool_results(result)
        assert out["portfolio_analysis"] == {"summary": "plain text not json"}

    def test_extract_unknown_tool_ignored(self):
        agent = self._make_agent_no_init()
        result = {
            "messages": [
                _tool_msg("unknown_tool", json.dumps({"summary": "X"})),
            ]
        }
        out = agent._extract_tool_results(result)
        assert out == {}

    def test_extract_empty_messages(self):
        agent = self._make_agent_no_init()
        out = agent._extract_tool_results({"messages": []})
        assert out == {}


class TestBuildInput:
    def test_build_input_includes_context_json(self):
        from app.agents.react_agent import ReActAgent

        agent = ReActAgent.__new__(ReActAgent)
        out = agent._build_input(
            "analyze",
            {"weights": {"AAPL": 0.5}, "metrics": {"sharpe": 1.0}},
        )
        assert "analyze" in out
        assert "Context (JSON):" in out
        assert "AAPL" in out
        assert "sharpe" in out


class TestReActAgentRun:
    @pytest.mark.asyncio
    async def test_run_calls_ainvoke_and_returns_4_field_dict(self):
        from app.agents.react_agent import ReActAgent

        with (
            patch("app.agents.react_agent.ChatGoogleGenerativeAI"),
            patch("app.agents.react_agent.create_react_agent") as mock_create,
        ):
            mock_compiled = SimpleNamespace(
                ainvoke=AsyncMock(
                    return_value={
                        "messages": [
                            _tool_msg(
                                "analyze_portfolio_tool",
                                json.dumps({"summary": "PA"}),
                            ),
                        ]
                    }
                )
            )
            mock_create.return_value = mock_compiled
            agent = ReActAgent()
            out = await agent.run("input", context={"weights": {"AAPL": 1.0}})
            mock_compiled.ainvoke.assert_awaited_once()
            assert out["portfolio_analysis"] == {"summary": "PA"}
