"""
검색 컨트롤러
"""
from app.services.search_service import SearchService
from app.api.schemas.search import SearchResultItem, SearchResponse

search_service = SearchService()


class SearchController:
    def search_similar(self, query: str, top_k: int = 5) -> SearchResponse:
        results = search_service.search_similar(query, top_k)
        return SearchResponse(
            query=query,
            results=[
                SearchResultItem(
                    question=r.get("question", ""),
                    answer=r.get("answer", ""),
                    domain=r.get("domain", ""),
                    category=r.get("category", ""),
                    score=r["score"],
                )
                for r in results
            ],
        )
