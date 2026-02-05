"""
분류 스키마
"""
from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="분류할 민원 텍스트")

    class Config:
        json_schema_extra = {"example": {"text": "인터넷뱅킹 로그인이 안돼요"}}


class ClassifyResponse(BaseModel):
    domain: str = Field(..., description="분류된 도메인")
    domain_id: int = Field(..., description="도메인 ID")
    confidence: float = Field(..., description="신뢰도 (0~1)")

    class Config:
        json_schema_extra = {"example": {"domain": "금융/보험", "domain_id": 1, "confidence": 0.996}}


class BatchClassifyRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=100, description="분류할 텍스트 목록")


class BatchClassifyResponse(BaseModel):
    results: list[ClassifyResponse]
    count: int


class ClassifyCategoryResponse(BaseModel):
    category: str = Field(..., description="분류된 카테고리")
    category_id: int = Field(..., description="카테고리 ID")
    confidence: float = Field(..., description="신뢰도 (0~1)")

    class Config:
        json_schema_extra = {"example": {"category": "결제", "category_id": 0, "confidence": 0.95}}
