from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
import time

from app.vectorstore.faiss_store import FAISSStore
from app.llm.ollama import OllamaLLM
from app.llm.gemini import GeminiLLM

router = APIRouter()
vector_store = FAISSStore()
ollama_llm = OllamaLLM()
gemini_llm = GeminiLLM()

PROMPT_TEMPLATE = """당신은 친절하고 전문적인 공공기관 민원 상담 AI입니다.

## 참고 정보
{context}

## 민원 질문
{question}

## 답변 지침
- 참고 정보가 부족하더라도, 일반적인 지식을 활용하여 상세하게 답변하세요
- 반드시 3문장 이상으로 답변하세요
- 먼저 인사와 공감으로 시작하세요
- 구체적인 해결 방법이나 절차를 안내하세요
- 추가 문의처(전화번호, 웹사이트 등)를 안내하세요
- 따뜻하고 친절한 말투를 사용하세요

## 답변"""


class CompareRequest(BaseModel):
    query: str
    max_tokens: int = 512


class LLMResult(BaseModel):
    answer: str
    elapsed_time: float
    model_name: str


class CompareResponse(BaseModel):
    query: str
    ollama: LLMResult
    gemini: LLMResult
    sources: list[str]


def build_prompt(query: str) -> tuple[str, list[str]]:
    """RAG 컨텍스트로 프롬프트 구성"""
    similar_docs = vector_store.search(query, top_k=3)
    
    context_parts = []
    for doc in similar_docs:
        context_parts.append(
            f"[{doc['domain']} - {doc['category']}]\n질문: {doc['question']}\n답변: {doc['answer']}"
        )
    context = "\n\n".join(context_parts) if context_parts else "참고할 유사 사례가 없습니다."
    
    sources = [
        f"{doc['domain']}: {doc['question'][:50]}..."
        for doc in similar_docs
    ]
    
    prompt = PROMPT_TEMPLATE.format(context=context, question=query)
    return prompt, sources


@router.post("/", response_model=CompareResponse)
async def compare_llms(request: CompareRequest):
    """Ollama vs Gemini 동시 비교"""
    try:
        prompt, sources = build_prompt(request.query)
        
        # Ollama 호출
        ollama_start = time.time()
        ollama_answer = ollama_llm.generate(prompt, max_tokens=request.max_tokens)
        ollama_time = time.time() - ollama_start
        
        # Gemini 호출
        gemini_start = time.time()
        gemini_answer = gemini_llm.generate(prompt, max_tokens=request.max_tokens)
        gemini_time = time.time() - gemini_start
        
        return CompareResponse(
            query=request.query,
            ollama=LLMResult(
                answer=ollama_answer,
                elapsed_time=round(ollama_time, 2),
                model_name="Gemma 2B (로컬)"
            ),
            gemini=LLMResult(
                answer=gemini_answer,
                elapsed_time=round(gemini_time, 2),
                model_name="Gemini 1.5 Flash (API)"
            ),
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
