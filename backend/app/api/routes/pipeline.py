"""
파이프라인 SSE 엔드포인트 (Claro 특화)
"""
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.schemas.pipeline import PipelineRequest
from app.api.controllers.pipeline_controller import PipelineController

router = APIRouter()
controller = PipelineController()


@router.post("/process")
async def process_complaint(request: PipelineRequest):
    """SSE 스트리밍으로 파이프라인 실행 (classify → search → generate)"""

    async def event_stream():
        async for step in controller.execute(request.query, request.compare_mode):
            payload = json.dumps(step.to_dict(), ensure_ascii=False)
            yield f"data: {payload}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
