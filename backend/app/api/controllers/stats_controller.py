"""통계 컨트롤러"""
from app.services.stats_service import StatsService
from app.api.schemas.stats import (
    StatsOverviewResponse,
    DailyQueryResponse,
    DomainBreakdownResponse,
    FeedbackListResponse,
    ModelStats,
    DailyCount,
    DomainCount,
    FeedbackSummary,
)


class StatsController:
    def __init__(self):
        self.stats_svc = StatsService()

    async def get_overview(self) -> StatsOverviewResponse:
        raw = await self.stats_svc.get_model_stats()
        models = [ModelStats(**m) for m in raw]
        return StatsOverviewResponse(models=models)

    async def get_daily(self, days: int = 30) -> DailyQueryResponse:
        raw = await self.stats_svc.get_daily_queries(days)
        daily = [DailyCount(**d) for d in raw]
        return DailyQueryResponse(daily=daily)

    async def get_domains(self) -> DomainBreakdownResponse:
        raw = await self.stats_svc.get_domain_breakdown()
        domains = [DomainCount(**d) for d in raw]
        return DomainBreakdownResponse(domains=domains)

    async def get_feedback(self, limit: int = 20) -> FeedbackListResponse:
        raw = await self.stats_svc.get_recent_feedback(limit)
        feedback = [FeedbackSummary(**f) for f in raw]
        return FeedbackListResponse(feedback=feedback)

    async def get_queries(
        self, search: str = "", domain: str = "", limit: int = 50, offset: int = 0
    ) -> dict:
        return await self.stats_svc.get_query_logs(search, domain, limit, offset)
