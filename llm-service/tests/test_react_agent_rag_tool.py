"""D-5 ReAct agent + RAG 도구 통합 단위 테스트 (ADR 0018)"""

from __future__ import annotations

from unittest.mock import patch

import pytest


class TestRagToolDefinition:
    def test_search_knowledge_base_is_langchain_tool(self):
        from langchain_core.tools import BaseTool

        from app.agents.rag_tools import search_knowledge_base

        assert isinstance(search_knowledge_base, BaseTool)
        assert search_knowledge_base.name == "search_knowledge_base"

    def test_tool_description_mentions_domain(self):
        from app.agents.rag_tools import search_knowledge_base

        desc = (search_knowledge_base.description or "").lower()
        assert "도메인" in desc or "knowledge" in desc or "지식" in desc

    def test_tool_invokes_query_with_llm(self):
        from app.agents.rag_tools import search_knowledge_base

        with patch("app.agents.rag_tools.query_with_llm") as mock_q:
            mock_q.return_value = {
                "answer": "샤프 비율은 위험조정수익률입니다.",
                "sources": [{"title": "샤프 비율", "source": "portfolio_theory", "relevance": 0.85}],
            }
            result = search_knowledge_base.invoke({"question": "샤프 비율?"})
            assert result["answer"] == "샤프 비율은 위험조정수익률입니다."
            assert len(result["sources"]) == 1
            mock_q.assert_called_once_with(question="샤프 비율?", k=3, include_sources=True)


class TestToolRegistry:
    def test_registry_lists_5_tools(self):
        from app.agents.tools import get_tool_registry

        registry = get_tool_registry()
        tools = registry.list_all()
        names = {t.name for t in tools}
        assert "search_knowledge_base" in names
        assert len(tools) >= 5

    def test_registry_includes_existing_4_tools(self):
        from app.agents.tools import get_tool_registry

        registry = get_tool_registry()
        names = {t.name for t in registry.list_all()}
        for expected in [
            "analyze_portfolio_tool",
            "explain_risk_tool",
            "summarize_backtest_tool",
            "get_recommendation_tool",
        ]:
            assert expected in names


class TestReactAgentMapping:
    def test_tool_name_to_field_includes_search_knowledge_base(self):
        from app.agents.react_agent import _TOOL_NAME_TO_FIELD

        assert "search_knowledge_base" in _TOOL_NAME_TO_FIELD
        assert _TOOL_NAME_TO_FIELD["search_knowledge_base"] == "knowledge_sources"

    def test_existing_4_mappings_preserved(self):
        from app.agents.react_agent import _TOOL_NAME_TO_FIELD

        assert _TOOL_NAME_TO_FIELD["analyze_portfolio_tool"] == "portfolio_analysis"
        assert _TOOL_NAME_TO_FIELD["explain_risk_tool"] == "risk_analysis"
        assert _TOOL_NAME_TO_FIELD["summarize_backtest_tool"] == "backtest_analysis"
        assert _TOOL_NAME_TO_FIELD["get_recommendation_tool"] == "recommendation"


class TestPromptRegistryV1_1:
    def test_react_system_prompt_v1_1_registered(self):
        from app.services.prompt_registry import get_registry

        registry = get_registry()
        prompt = registry.get("react_system_prompt", "1.1")
        assert prompt is not None
        assert "5 도구" in prompt.template or "5종" in prompt.template
        assert "search_knowledge_base" in prompt.template

    def test_react_system_prompt_v1_0_still_available(self):
        from app.services.prompt_registry import get_registry

        registry = get_registry()
        prompt_v1 = registry.get("react_system_prompt", "1.0")
        assert prompt_v1 is not None
        assert "4종" in prompt_v1.template


class TestAnalysisResponseSchema:
    def test_knowledge_sources_field_added(self):
        from app.schemas.chat import AnalysisResponse, PortfolioData

        response = AnalysisResponse(
            summary="test",
            portfolio_analysis={},
            portfolio_data=PortfolioData(weights={"AAPL": 1.0}, metrics={"sharpe_ratio": 1.0}),
            knowledge_sources={"answer": "샤프", "sources": []},
        )
        assert response.knowledge_sources == {"answer": "샤프", "sources": []}

    def test_knowledge_sources_optional_default_none(self):
        from app.schemas.chat import AnalysisResponse, PortfolioData

        response = AnalysisResponse(
            summary="test",
            portfolio_analysis={},
            portfolio_data=PortfolioData(weights={"AAPL": 1.0}, metrics={"sharpe_ratio": 1.0}),
        )
        assert response.knowledge_sources is None
