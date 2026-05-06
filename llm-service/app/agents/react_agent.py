"""ReAct 에이전트 - LangGraph create_react_agent 기반, BaseAgent 구현체"""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from app.agents.base import BaseAgent
from app.agents.tools import get_tool_registry
from app.config import get_settings
from app.services.prompt_registry import get_registry

logger = logging.getLogger(__name__)

_TOOL_NAME_TO_FIELD: dict[str, str] = {
    "analyze_portfolio_tool": "portfolio_analysis",
    "explain_risk_tool": "risk_analysis",
    "summarize_backtest_tool": "backtest_analysis",
    "get_recommendation_tool": "recommendation",
    "search_knowledge_base": "knowledge_sources",  # D-5 / ADR 0018
}


class ReActAgent(BaseAgent):
    """4 도메인 도구를 자율 호출하는 ReAct 에이전트."""

    def __init__(self) -> None:
        settings = get_settings()
        tool_reg = get_tool_registry()
        prompt_reg = get_registry()
        self._model = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=settings.llm_temperature,
        )
        self._agent = create_react_agent(
            model=self._model,
            tools=tool_reg.list_all(),
            prompt=prompt_reg.get("react_system_prompt", "1.1").template,
        )

    async def run(self, user_input: str, context: dict | None = None) -> dict[str, Any]:
        """ReAct 루프 실행 - 모델이 도구 호출 순서를 자율 판단. 4 키 dict 반환."""
        full_input = self._build_input(user_input, context or {})
        result = await self._agent.ainvoke({"messages": [("user", full_input)]})
        return self._extract_tool_results(result)

    def _build_input(self, user_input: str, context: dict) -> str:
        ctx_json = json.dumps(context, ensure_ascii=False, default=str)
        return f"{user_input}\n\nContext (JSON):\n{ctx_json}"

    def _extract_tool_results(self, react_result: dict) -> dict[str, Any]:
        """ReAct 메시지 흐름에서 도구 호출 결과 추출 → AnalysisResponse 필드명 dict."""
        results: dict[str, Any] = {}
        for message in react_result.get("messages", []):
            tool_name = getattr(message, "name", None)
            if tool_name not in _TOOL_NAME_TO_FIELD:
                continue
            field = _TOOL_NAME_TO_FIELD[tool_name]
            content = message.content
            if isinstance(content, str):
                try:
                    results[field] = json.loads(content)
                except json.JSONDecodeError:
                    results[field] = {"summary": content}
            else:
                results[field] = content
        return results
