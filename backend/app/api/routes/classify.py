"""
민원 분류 API 엔드포인트 — 얇은 HTTP 레이어
"""
from fastapi import APIRouter

from app.api.schemas.classify import (
    ClassifyRequest,
    ClassifyResponse,
    BatchClassifyRequest,
    BatchClassifyResponse,
    ClassifyCategoryResponse,
)
from app.api.controllers.classify_controller import ClassifyController

router = APIRouter(prefix="/classify", tags=["분류"])
controller = ClassifyController()


@router.post("", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest):
    """민원 텍스트를 도메인으로 분류합니다."""
    return controller.classify(request.text)


@router.post("/batch", response_model=BatchClassifyResponse)
async def classify_batch(request: BatchClassifyRequest):
    """여러 민원 텍스트를 한 번에 분류합니다."""
    return controller.classify_batch(request.texts)


@router.get("/labels")
async def get_labels():
    """사용 가능한 도메인 레이블 목록을 반환합니다."""
    return controller.get_labels()


@router.post("/category", response_model=ClassifyCategoryResponse)
async def classify_category(request: ClassifyRequest):
    """민원 텍스트를 카테고리로 분류합니다."""
    return controller.classify_category(request.text)


@router.get("/category/labels")
async def get_category_labels():
    """사용 가능한 카테고리 레이블 목록을 반환합니다."""
    return controller.get_category_labels()
