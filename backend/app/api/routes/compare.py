"""
LLM 비교 API 엔드포인트
"""
from fastapi import APIRouter

from app.api.schemas.compare import CompareRequest, CompareResponse
from app.api.controllers.compare_controller import CompareController

router = APIRouter()
controller = CompareController()


@router.post("/", response_model=CompareResponse)
async def compare_llms(request: CompareRequest):
    """Ollama vs Gemini 동시 비교"""
    return controller.compare(request.query, request.max_tokens)
