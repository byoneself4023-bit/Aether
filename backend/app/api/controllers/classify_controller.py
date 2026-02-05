"""
분류 컨트롤러 — 요청 검증 → 서비스 호출 → 응답 변환
"""
from app.services.classify_service import ClassifyService
from app.api.schemas.classify import (
    ClassifyResponse,
    BatchClassifyResponse,
    ClassifyCategoryResponse,
)

classify_service = ClassifyService()


class ClassifyController:
    def classify(self, text: str) -> ClassifyResponse:
        result = classify_service.classify_domain(text)
        return ClassifyResponse(**result)

    def classify_batch(self, texts: list[str]) -> BatchClassifyResponse:
        results = classify_service.classify_batch(texts)
        return BatchClassifyResponse(
            results=[ClassifyResponse(**r) for r in results],
            count=len(results),
        )

    def get_labels(self) -> dict:
        return classify_service.get_domain_labels()

    def classify_category(self, text: str) -> ClassifyCategoryResponse:
        result = classify_service.classify_category(text)
        return ClassifyCategoryResponse(**result)

    def get_category_labels(self) -> dict:
        return classify_service.get_category_labels()
