"""
파이프라인 스키마 (Claro 특화)
"""
from pydantic import BaseModel
from typing import Optional


class PipelineRequest(BaseModel):
    query: str
    compare_mode: bool = False
    max_tokens: int = 1024
