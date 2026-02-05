"""
피드백 스키마
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FeedbackRequest(BaseModel):
    query: str
    answer: str
    model_name: str = "ollama"
    domain: Optional[str] = None
    category: Optional[str] = None
    rating: int  # 1=helpful, 0=not helpful
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    message: str


class FeedbackItem(BaseModel):
    id: int
    query: str
    answer: str
    model_name: str
    domain: Optional[str]
    category: Optional[str]
    rating: int
    comment: Optional[str]
    created_at: str


class FeedbackListResponse(BaseModel):
    items: List[FeedbackItem]
    total: int
