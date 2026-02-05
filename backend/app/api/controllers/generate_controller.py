"""
생성 컨트롤러
"""
from typing import Optional

from app.services.generate_service import GenerateService
from app.api.schemas.generate import GenerateResponse

generate_service = GenerateService()


class GenerateController:
    def generate(self, query: str, context: Optional[str] = None, max_tokens: int = 1024) -> GenerateResponse:
        result = generate_service.generate_answer(query, context, max_tokens)
        return GenerateResponse(**result)
