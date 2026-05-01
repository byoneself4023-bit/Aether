"""RAG API 라우터 - 금융 지식 검색 및 질문 답변"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import verify_jwt
from app.schemas.chat import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGInitRequest,
    RAGStatusResponse,
    SourceInfo,
)
from app.services.rag import (
    init_vectorstore,
    get_vectorstore_status,
    query,
    query_with_llm,
    list_documents,
    LLMError,
)
from app.services.guardrails import sanitize_user_input, wrap_user_input

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    request: RAGQueryRequest,
    user: dict = Depends(verify_jwt),
) -> RAGQueryResponse:
    """
    RAG 기반 금융 질문 답변

    금융 지식베이스에서 관련 문서를 검색하고
    LLM이 답변을 생성합니다.
    """
    question = request.question
    k = request.k

    # 입력 정제 및 인젝션 방어
    sanitized_question, input_warnings = sanitize_user_input(question)
    if input_warnings:
        logger.warning(f"RAG input warnings: {input_warnings}")

    wrapped_question = wrap_user_input(sanitized_question)

    logger.info(f"RAG query: {sanitized_question[:50]}...")

    try:
        # RAG 검색 + LLM 답변
        result = query_with_llm(
            question=wrapped_question,
            k=k,
            include_sources=True,
        )

        # 출처 정보 변환
        sources = [
            SourceInfo(
                title=s["title"],
                source=s["source"],
                relevance=s.get("relevance", 0),
            )
            for s in result.get("sources", [])
        ]

        # 신뢰도 계산 (평균 relevance)
        confidence = 0.0
        if sources:
            relevances = [s.relevance for s in sources if s.relevance is not None]
            if relevances:
                confidence = sum(relevances) / len(relevances)

        return RAGQueryResponse(
            answer=result["answer"],
            sources=sources,
            confidence=round(confidence, 3),
        )

    except LLMError as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {e}"
        )


@router.post("/search")
async def rag_search(
    request: RAGQueryRequest,
    user: dict = Depends(verify_jwt),
):
    """
    RAG 문서 검색 (LLM 없이)

    관련 문서만 검색하여 반환합니다.
    """
    question = request.question
    k = request.k
    filter_source = request.filter_source

    logger.info(f"RAG search: {question[:50]}...")

    try:
        # 벡터 검색만 수행
        documents = query(
            question=question,
            k=k,
            filter_source=filter_source,
        )

        return {
            "question": question,
            "results": [
                {
                    "id": doc["id"],
                    "title": doc["metadata"].get("title", "Unknown"),
                    "source": doc["metadata"].get("source", "Unknown"),
                    "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"],
                    "distance": round(doc["distance"], 4),
                    "relevance": round(1 - doc["distance"], 4),
                }
                for doc in documents
            ],
            "total": len(documents),
        }

    except LLMError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {e}"
        )


@router.post("/init")
async def rag_init(
    request: RAGInitRequest,
    user: dict = Depends(verify_jwt),
):
    """
    벡터스토어 초기화

    금융 지식베이스를 로드하고 임베딩을 생성합니다.
    """
    force_reload = request.force_reload

    logger.info(f"RAG init: force_reload={force_reload}")

    try:
        success = init_vectorstore(force_reload=force_reload)

        if success:
            status = get_vectorstore_status()
            return {
                "status": "success",
                "message": "Vectorstore initialized successfully",
                "document_count": status["document_count"],
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize vectorstore"
            )

    except Exception as e:
        logger.error(f"RAG init failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Initialization failed: {e}"
        )


@router.get("/status", response_model=RAGStatusResponse)
async def rag_status(
    user: dict = Depends(verify_jwt),
) -> RAGStatusResponse:
    """
    벡터스토어 상태 확인
    """
    status = get_vectorstore_status()

    # 사용 가능한 소스 목록
    available_sources = None
    if status["initialized"]:
        try:
            docs = list_documents(limit=100)
            sources = set(d["metadata"].get("source") for d in docs if d.get("metadata"))
            available_sources = sorted(sources) if sources else None
        except Exception:
            pass

    return RAGStatusResponse(
        initialized=status["initialized"],
        document_count=status["document_count"],
        persist_dir=status.get("persist_dir"),
        available_sources=available_sources,
    )


@router.get("/documents")
async def rag_documents(
    limit: int = 50,
    user: dict = Depends(verify_jwt),
):
    """
    저장된 문서 목록 조회
    """
    try:
        documents = list_documents(limit=limit)

        # 소스별 그룹핑
        by_source = {}
        for doc in documents:
            source = doc["metadata"].get("source", "unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append({
                "id": doc["id"],
                "title": doc["metadata"].get("title", "Unknown"),
            })

        return {
            "total": len(documents),
            "by_source": by_source,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {e}"
        )


@router.get("/sources")
async def rag_sources(
    user: dict = Depends(verify_jwt),
):
    """
    사용 가능한 문서 소스 목록
    """
    sources_info = {
        "portfolio_theory": {
            "name": "포트폴리오 이론",
            "description": "현대 포트폴리오 이론, 효율적 프론티어, 샤프 비율",
            "topics": ["MPT", "Efficient Frontier", "Sharpe Ratio", "Shrinkage"],
        },
        "risk_management": {
            "name": "리스크 관리",
            "description": "VaR, CVaR, 몬테카를로 시뮬레이션, MDD",
            "topics": ["VaR", "CVaR", "Monte Carlo", "Maximum Drawdown"],
        },
        "sector_analysis": {
            "name": "섹터 분석",
            "description": "S&P 500 섹터별 특성, 경기 사이클",
            "topics": ["GICS Sectors", "Sector Rotation", "Business Cycle"],
        },
        "investment_strategies": {
            "name": "투자 전략",
            "description": "MVP, MSR, 1/N, 리밸런싱 전략",
            "topics": ["MVP", "MSR", "Equal Weight", "Rebalancing"],
        },
    }

    # 실제 로드된 문서 수 추가
    try:
        docs = list_documents(limit=200)
        for source_key in sources_info:
            count = sum(1 for d in docs if d["metadata"].get("source") == source_key)
            sources_info[source_key]["document_count"] = count
    except Exception:
        pass

    return {
        "sources": sources_info,
        "total_sources": len(sources_info),
    }
