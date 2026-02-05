"""
파이프라인 컨트롤러 (Claro 특화) — SSE 오케스트레이션
"""
from typing import AsyncGenerator

from app.pipeline.orchestrator import PipelineOrchestrator
from app.services.classify_service import ClassifyService
from app.services.search_service import SearchService
from app.services.generate_service import GenerateService
from app.services.compare_service import CompareService
from app.pipeline.steps import PipelineStep

orchestrator = PipelineOrchestrator(
    classify_svc=ClassifyService(),
    search_svc=SearchService(),
    generate_svc=GenerateService(),
    compare_svc=CompareService(),
)


class PipelineController:
    async def execute(self, query: str, compare_mode: bool = False) -> AsyncGenerator[PipelineStep, None]:
        async for step in orchestrator.execute(query, compare_mode):
            yield step
