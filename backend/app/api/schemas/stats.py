"""통계/대시보드 스키마"""
from typing import List, Optional
from pydantic import BaseModel


class ModelStats(BaseModel):
    model_name: str
    total_queries: int
    avg_response_time_ms: float
    helpful_rate: Optional[float] = None  # 0.0 ~ 1.0
    total_feedback: int


class DailyCount(BaseModel):
    date: str
    count: int


class DomainCount(BaseModel):
    domain: str
    count: int


class FeedbackSummary(BaseModel):
    id: int
    query: str
    answer: str
    model_name: str
    domain: Optional[str] = None
    rating: int
    created_at: str


class StatsOverviewResponse(BaseModel):
    models: List[ModelStats]


class DailyQueryResponse(BaseModel):
    daily: List[DailyCount]


class DomainBreakdownResponse(BaseModel):
    domains: List[DomainCount]


class FeedbackListResponse(BaseModel):
    feedback: List[FeedbackSummary]
