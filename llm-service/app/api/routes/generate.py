from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.chains.rag_chain import RAGChain
from app.utils.answer_cleaner import clean_answer

router = APIRouter()
rag_chain = RAGChain()

class GenerateRequest(BaseModel):
    query: str
    context: Optional[str] = None
    max_tokens: int = 1024

class GenerateResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]

@router.post("/", response_model=GenerateResponse)
async def generate_answer(request: GenerateRequest):
    """RAG 기반 답변 생성 API"""
    try:
        result = rag_chain.generate(
            query=request.query,
            context=request.context,
            max_tokens=request.max_tokens
        )
        
        # 도메인 추출 (sources에서)
        domain = "해당 기관"
        if result.get("sources"):
            first_source = result["sources"][0]
            if ":" in first_source:
                domain = first_source.split(":")[0]
        
        # 답변 후처리
        cleaned_answer = clean_answer(result["answer"], domain)
        
        return GenerateResponse(
            query=request.query,
            answer=cleaned_answer,
            sources=result.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
