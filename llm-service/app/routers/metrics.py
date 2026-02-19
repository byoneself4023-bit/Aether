"""토큰 사용량 메트릭스 API 라우터"""

import logging
from fastapi import APIRouter

from app.services.token_tracker import get_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/tokens")
async def get_token_metrics():
    """
    토큰 사용량 및 비용 메트릭스

    Returns:
        토큰 사용량 요약 (총 토큰, 요청 수, 추정 비용, 시간별/일별 집계)
    """
    tracker = get_tracker()
    return tracker.get_summary()
