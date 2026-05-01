"""LangGraph 도구 레지스트리 - prompt_registry와 동일 lazy init 패턴 (자기 일관성)"""

from __future__ import annotations

import logging

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """도구 레지스트리 - register/get/list_all 3 메서드 (YAGNI)."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, name: str, tool: BaseTool) -> None:
        if name in self._tools:
            raise ValueError(f"Tool {name} already registered")
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def list_all(self) -> list[BaseTool]:
        return list(self._tools.values())


_tool_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """글로벌 ToolRegistry - lazy init (prompt_registry.get_registry 미러)."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
        _register_default_tools(_tool_registry)
    return _tool_registry


def _register_default_tools(registry: ToolRegistry) -> None:
    """기본 도구 4종 등록 (prompt_registry._register_default_prompts 미러)."""
    from app.agents.portfolio_tools import (
        analyze_portfolio_tool,
        explain_risk_tool,
        get_recommendation_tool,
        summarize_backtest_tool,
    )

    registry.register("analyze_portfolio", analyze_portfolio_tool)
    registry.register("explain_risk", explain_risk_tool)
    registry.register("summarize_backtest", summarize_backtest_tool)
    registry.register("get_recommendation", get_recommendation_tool)
