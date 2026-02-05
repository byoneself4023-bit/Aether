"""
파이프라인 실행 엔진 (Claro 특화)
classify → search → generate 순차 실행, 각 스텝을 yield
분류 결과의 도메인을 검색·생성에 전달하여 품질 향상
"""
import time
from typing import AsyncGenerator
from loguru import logger

from app.services.classify_service import ClassifyService
from app.services.search_service import SearchService
from app.services.generate_service import GenerateService
from app.services.compare_service import CompareService
from app.services.feedback_service import FeedbackService
from app.pipeline.steps import PipelineStep


class PipelineOrchestrator:
    def __init__(
        self,
        classify_svc: ClassifyService,
        search_svc: SearchService,
        generate_svc: GenerateService,
        compare_svc: CompareService,
    ):
        self.classify_svc = classify_svc
        self.search_svc = search_svc
        self.generate_svc = generate_svc
        self.compare_svc = compare_svc
        self.feedback_svc = FeedbackService()

    async def execute(
        self, query: str, compare_mode: bool = False
    ) -> AsyncGenerator[PipelineStep, None]:
        """파이프라인 실행 — 각 스텝 완료 시 yield"""
        pipeline_start = time.time()

        # Step 1: Classify
        yield PipelineStep(name="classify", status="running")
        classification = None
        domain = None
        try:
            classification = self.classify_svc.classify_full(query)
            domain = classification.get("domain")
            yield PipelineStep(name="classify", status="done", result=classification)
        except Exception as e:
            logger.error(f"파이프라인 분류 실패: {e}")
            yield PipelineStep(name="classify", status="error", error=str(e))
            return

        # Step 2: Search (도메인 필터링 적용)
        yield PipelineStep(name="search", status="running")
        try:
            similar = self.search_svc.search_similar(query, top_k=5, domain=domain)
            yield PipelineStep(name="search", status="done", result=similar)
        except Exception as e:
            logger.error(f"파이프라인 검색 실패: {e}")
            yield PipelineStep(name="search", status="error", error=str(e))
            return

        # Step 3: Generate (or Compare) — 도메인 전달
        yield PipelineStep(name="generate", status="running")
        try:
            if compare_mode:
                result = self.compare_svc.compare(query)
            else:
                result = self.generate_svc.generate_answer(query, domain=domain)
            yield PipelineStep(name="generate", status="done", result=result)
        except Exception as e:
            logger.error(f"파이프라인 생성 실패: {e}")
            yield PipelineStep(name="generate", status="error", error=str(e))

        # 쿼리 이력 로깅 (비동기, 실패해도 무시)
        elapsed_ms = int((time.time() - pipeline_start) * 1000)
        try:
            await self.feedback_svc.log_query(
                query=query,
                domain=classification.get("domain") if classification else None,
                category=classification.get("category") if classification else None,
                domain_confidence=classification.get("confidence") if classification else None,
                model_name="compare" if compare_mode else "ollama",
                response_time_ms=elapsed_ms,
                compare_mode=compare_mode,
            )
        except Exception as e:
            logger.debug(f"쿼리 로깅 실패: {e}")
