"""
유사 민원 검색 API 엔드포인트
"""
from fastapi import APIRouter

from app.api.schemas.search import SearchRequest, SearchResponse
from app.api.controllers.search_controller import SearchController

router = APIRouter()
controller = SearchController()


@router.post("/similar", response_model=SearchResponse)
async def search_similar(request: SearchRequest):
    """유사 민원을 검색합니다."""
    return controller.search_similar(request.query, request.top_k)
