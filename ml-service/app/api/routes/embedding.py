from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.embedder import Embedder

router = APIRouter()
embedder = Embedder()


class EmbeddingRequest(BaseModel):
    texts: List[str]


class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]


@router.post("/", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """텍스트 임베딩 생성 API"""
    try:
        embeddings = embedder.embed(request.texts)
        return EmbeddingResponse(embeddings=embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
