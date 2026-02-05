"""
추상 LLM 인터페이스
"""
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """LLM 공통 인터페이스"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        ...
