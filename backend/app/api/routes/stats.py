"""통계/대시보드 라우트"""
from fastapi import APIRouter, Query
from app.api.controllers.stats_controller import StatsController
from app.api.schemas.stats import (
    StatsOverviewResponse,
    DailyQueryResponse,
    DomainBreakdownResponse,
    FeedbackListResponse,
)

router = APIRouter()
ctrl = StatsController()


@router.get("/overview", response_model=StatsOverviewResponse)
async def get_overview():
    """모델별 종합 통계"""
    return await ctrl.get_overview()


@router.get("/daily", response_model=DailyQueryResponse)
async def get_daily(days: int = Query(default=30, ge=1, le=365)):
    """일별 쿼리 추이"""
    return await ctrl.get_daily(days)


@router.get("/domains", response_model=DomainBreakdownResponse)
async def get_domains():
    """도메인별 분포"""
    return await ctrl.get_domains()


@router.get("/feedback", response_model=FeedbackListResponse)
async def get_feedback(limit: int = Query(default=20, ge=1, le=100)):
    """최근 피드백 목록"""
    return await ctrl.get_feedback(limit)


@router.get("/queries")
async def get_queries(
    search: str = Query(default=""),
    domain: str = Query(default=""),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """쿼리 로그 목록 (히스토리 페이지용)"""
    return await ctrl.get_queries(search, domain, limit, offset)
