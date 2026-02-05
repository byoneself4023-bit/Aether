"""
비교 스키마
"""
from pydantic import BaseModel
from typing import List


class CompareRequest(BaseModel):
    query: str
    max_tokens: int = 512


class LLMResult(BaseModel):
    answer: str
    elapsed_time: float
    model_name: str


class CompareResponse(BaseModel):
    query: str
    ollama: LLMResult
    gemini: LLMResult
    sources: List[str]
