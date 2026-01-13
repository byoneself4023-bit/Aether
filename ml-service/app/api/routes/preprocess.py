from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.preprocessor import Preprocessor

router = APIRouter()
preprocessor = Preprocessor()


class PreprocessRequest(BaseModel):
    text: str


class PreprocessResponse(BaseModel):
    original_text: str
    processed_text: str


@router.post("/", response_model=PreprocessResponse)
async def preprocess_text(request: PreprocessRequest):
    """텍스트 전처리 API"""
    try:
        processed = preprocessor.process(request.text)
        return PreprocessResponse(
            original_text=request.text,
            processed_text=processed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
