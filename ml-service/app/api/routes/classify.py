"""
민원 분류 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from app.models.classifier import get_classifier


router = APIRouter(prefix="/classify", tags=["분류"])


# ============ Request/Response 스키마 ============

class ClassifyRequest(BaseModel):
    """분류 요청"""
    text: str = Field(..., min_length=1, max_length=1000, description="분류할 민원 텍스트")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "인터넷뱅킹 로그인이 안돼요"
            }
        }


class ClassifyResponse(BaseModel):
    """분류 응답"""
    domain: str = Field(..., description="분류된 도메인")
    domain_id: int = Field(..., description="도메인 ID")
    confidence: float = Field(..., description="신뢰도 (0~1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "domain": "금융/보험",
                "domain_id": 1,
                "confidence": 0.996
            }
        }


class BatchClassifyRequest(BaseModel):
    """배치 분류 요청"""
    texts: list[str] = Field(..., min_length=1, max_length=100, description="분류할 텍스트 목록")


class BatchClassifyResponse(BaseModel):
    """배치 분류 응답"""
    results: list[ClassifyResponse]
    count: int


# ============ API 엔드포인트 ============

@router.post("", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest):
    """
    민원 텍스트를 도메인으로 분류합니다.
    
    - **text**: 분류할 민원 텍스트 (1~1000자)
    
    Returns:
        - **domain**: 분류된 도메인 (예: "금융/보험", "K쇼핑")
        - **domain_id**: 도메인 ID
        - **confidence**: 신뢰도 (0~1)
    """
    try:
        classifier = get_classifier()
        result = classifier.predict(request.text)
        
        logger.info(f"분류 완료: '{request.text[:30]}...' → {result['domain']} ({result['confidence']:.1%})")
        
        return ClassifyResponse(**result)
        
    except Exception as e:
        logger.error(f"분류 실패: {e}")
        raise HTTPException(status_code=500, detail=f"분류 중 오류 발생: {str(e)}")


@router.post("/batch", response_model=BatchClassifyResponse)
async def classify_batch(request: BatchClassifyRequest):
    """
    여러 민원 텍스트를 한 번에 분류합니다.
    
    - **texts**: 분류할 텍스트 목록 (최대 100개)
    """
    try:
        classifier = get_classifier()
        results = classifier.predict_batch(request.texts)
        
        logger.info(f"배치 분류 완료: {len(results)}건")
        
        return BatchClassifyResponse(
            results=[ClassifyResponse(**r) for r in results],
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"배치 분류 실패: {e}")
        raise HTTPException(status_code=500, detail=f"분류 중 오류 발생: {str(e)}")


@router.get("/labels")
async def get_labels():
    """사용 가능한 도메인 레이블 목록을 반환합니다."""
    try:
        classifier = get_classifier()
        return {
            "labels": classifier.label_mapping,
            "count": len(classifier.label_mapping)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
