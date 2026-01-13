from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.vectorstore.faiss_store import FAISSStore

router = APIRouter()
vector_store = FAISSStore()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    question: str
    answer: str
    domain: str
    category: str
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

@router.post("/similar", response_model=SearchResponse)
async def search_similar(request: SearchRequest):
    try:
        results = vector_store.search(
            query=request.query,
            top_k=request.top_k
        )
        return SearchResponse(
            query=request.query,
            results=[
                SearchResult(
                    question=r.get("question", ""),
                    answer=r.get("answer", ""),
                    domain=r.get("domain", ""),
                    category=r.get("category", ""),
                    score=r["score"]
                )
                for r in results
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))