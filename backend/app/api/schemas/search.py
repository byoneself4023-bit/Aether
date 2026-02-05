"""
검색 스키마
"""
from pydantic import BaseModel
from typing import List


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResultItem(BaseModel):
    question: str
    answer: str
    domain: str
    category: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
