"""
생성 스키마
"""
from pydantic import BaseModel
from typing import Optional, List


class GenerateRequest(BaseModel):
    query: str
    context: Optional[str] = None
    max_tokens: int = 1024


class GenerateResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
