"""
검색 서비스 — 벡터 유사도 검색 (도메인 필터링 지원)
"""
from typing import Optional
from loguru import logger

from app.resources.registry import registry
from app.core.exceptions import SearchError


class SearchService:
    def search_similar(
        self, query: str, top_k: int = 5, domain: Optional[str] = None
    ) -> list[dict]:
        """유사 민원 검색 (도메인 필터링 선택)"""
        try:
            results = registry.vector_store.search(query=query, top_k=top_k, domain=domain)
            return results
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            raise SearchError(f"검색 중 오류 발생: {str(e)}")
