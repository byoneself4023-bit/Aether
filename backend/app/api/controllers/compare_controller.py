"""
비교 컨트롤러
"""
from app.services.compare_service import CompareService
from app.api.schemas.compare import CompareResponse, LLMResult

compare_service = CompareService()


class CompareController:
    def compare(self, query: str, max_tokens: int = 512) -> CompareResponse:
        result = compare_service.compare(query, max_tokens)
        return CompareResponse(
            query=result["query"],
            ollama=LLMResult(**result["ollama"]),
            gemini=LLMResult(**result["gemini"]),
            sources=result["sources"],
        )
