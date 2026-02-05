"""
Claro Backend — 통합 FastAPI 앱
민원 분류, 유사 검색, RAG 답변 생성 API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.exceptions import ClaroError
from app.api.middleware.error_handler import claro_error_handler, generic_error_handler
from app.api.routes import classify, generate, search, compare
from app.api.routes.pipeline import router as pipeline_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.stats import router as stats_router
from app.api.routes.models import router as models_router
from app.api.routes.settings import router as settings_router
from app.resources.registry import registry
from app.resources.health import router as health_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 리소스 라이프사이클 관리"""
    logger.info("Claro Backend 시작...")
    await init_db()
    await registry.startup()
    yield
    await registry.shutdown()
    logger.info("Claro Backend 종료")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Claro - 민원 AI 어시스턴트 Backend

### 주요 기능
- **도메인 분류**: 민원 → 담당 부서 자동 분류
- **유사 민원 검색**: FAISS 벡터 유사도 검색
- **답변 생성**: RAG 기반 답변 초안 생성
- **LLM 비교**: 로컬 vs 클라우드 LLM 비교
- **파이프라인**: SSE 기반 실시간 파이프라인 처리
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 글로벌 예외 핸들러
app.add_exception_handler(ClaroError, claro_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010", "http://localhost:3011"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health_router)
app.include_router(classify.router, prefix=settings.API_V1_PREFIX)
app.include_router(generate.router, prefix=f"{settings.API_V1_PREFIX}/generate", tags=["Generate"])
app.include_router(search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["Search"])
app.include_router(compare.router, prefix=f"{settings.API_V1_PREFIX}/compare", tags=["Compare"])
app.include_router(pipeline_router, prefix=f"{settings.API_V1_PREFIX}/pipeline", tags=["Pipeline"])
app.include_router(feedback_router, prefix=f"{settings.API_V1_PREFIX}/feedback", tags=["Feedback"])
app.include_router(stats_router, prefix=f"{settings.API_V1_PREFIX}/stats", tags=["Stats"])
app.include_router(models_router, prefix=f"{settings.API_V1_PREFIX}/models", tags=["Models"])
app.include_router(settings_router, prefix=f"{settings.API_V1_PREFIX}/settings", tags=["Settings"])


@app.get("/")
async def root():
    """서비스 정보"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8010,
        reload=settings.DEBUG,
    )
