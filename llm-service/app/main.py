from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.routers import chat, rag, metrics
from app.services.rag import init_vectorstore
from app.services.portfolio_client import is_available as portfolio_is_available
from app.middleware.logging import RequestLoggingMiddleware, setup_structured_logging
from app.middleware.rate_limit import RateLimitMiddleware

settings = get_settings()

setup_structured_logging(debug=settings.debug)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"LLM Model: {settings.llm_model}")

    # API 키 존재 검증
    if not settings.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. "
            "Please set the GOOGLE_API_KEY environment variable or add it to your .env file. "
            "See .env.example for reference."
        )

    # 벡터스토어 초기화
    try:
        init_vectorstore()
        logger.info("Vectorstore initialized")
    except Exception as e:
        logger.warning(f"Vectorstore init failed: {e}")

    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="포트폴리오 분석 결과를 자연어로 해석하고 RAG로 금융 지식을 제공하는 서비스",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# 라우터 등록
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(metrics.router)


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트 - 의존성 상태 포함"""
    from datetime import datetime, timezone
    from app.services.rag import get_vectorstore_status

    checks = {}

    # 1. API 키 확인
    checks["api_key"] = "ok" if settings.google_api_key else "missing"

    # 2. 벡터스토어 상태
    try:
        vs_status = get_vectorstore_status()
        checks["vectorstore"] = "ok" if vs_status.get("initialized") else "not_initialized"
    except Exception:
        checks["vectorstore"] = "error"

    # 3. Portfolio-service 연결
    try:
        portfolio_ok = await portfolio_is_available()
        checks["portfolio_service"] = "ok" if portfolio_ok else "unavailable"
    except Exception:
        checks["portfolio_service"] = "unavailable"

    # 전체 상태 결정
    all_ok = all(v == "ok" for v in checks.values())
    status = "healthy" if all_ok else "degraded"

    return {
        "status": status,
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "chat": {
                "POST /api/chat": "자연어 포트폴리오 분석",
                "POST /api/chat/analyze": "상세 포트폴리오 분석",
                "GET /api/chat/health": "채팅 서비스 헬스체크",
            },
            "rag": {
                "POST /api/rag/query": "RAG 기반 금융 질문 답변",
                "POST /api/rag/search": "RAG 문서 검색",
                "POST /api/rag/init": "벡터스토어 초기화",
                "GET /api/rag/status": "벡터스토어 상태",
                "GET /api/rag/sources": "문서 소스 목록",
            },
            "metrics": {
                "GET /api/metrics/tokens": "토큰 사용량 및 비용 메트릭스",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
