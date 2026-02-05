"""
RAG 기반 답변 생성 API 엔드포인트
"""
from fastapi import APIRouter

from app.api.schemas.generate import GenerateRequest, GenerateResponse
from app.api.controllers.generate_controller import GenerateController

router = APIRouter()
controller = GenerateController()


@router.post("/", response_model=GenerateResponse)
async def generate_answer(request: GenerateRequest):
    """RAG 기반 답변을 생성합니다."""
    return controller.generate(request.query, request.context, request.max_tokens)
