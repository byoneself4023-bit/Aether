"""에이전트 추상 - T-1b ReAct 구현, T-3 Multi-Agent 시 확장 (YAGNI)"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """LangGraph 에이전트의 최소 추상 인터페이스."""

    @abstractmethod
    async def run(self, user_input: str, context: dict | None = None) -> dict:
        """사용자 입력을 받아 도구 호출 결과를 종합해 반환."""
        ...
