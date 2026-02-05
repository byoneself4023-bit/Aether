"""
피드백 API 엔드포인트
"""
from fastapi import APIRouter

from app.api.schemas.feedback import FeedbackRequest, FeedbackResponse, FeedbackListResponse
from app.api.controllers.feedback_controller import FeedbackController

router = APIRouter()
controller = FeedbackController()


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """답변 피드백 저장"""
    return await controller.submit_feedback(request)


@router.get("/recent", response_model=FeedbackListResponse)
async def get_recent_feedback(limit: int = 20):
    """최근 피드백 조회"""
    return await controller.get_recent(limit)
