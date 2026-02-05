"""
피드백 컨트롤러
"""
from app.services.feedback_service import FeedbackService
from app.api.schemas.feedback import FeedbackRequest, FeedbackResponse, FeedbackItem, FeedbackListResponse

feedback_service = FeedbackService()


class FeedbackController:
    async def submit_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        feedback_id = await feedback_service.save_feedback(
            query=request.query,
            answer=request.answer,
            rating=request.rating,
            model_name=request.model_name,
            domain=request.domain,
            category=request.category,
            comment=request.comment,
        )
        return FeedbackResponse(id=feedback_id, message="피드백이 저장되었습니다.")

    async def get_recent(self, limit: int = 20) -> FeedbackListResponse:
        items = await feedback_service.get_recent(limit)
        return FeedbackListResponse(
            items=[FeedbackItem(**item) for item in items],
            total=len(items),
        )
