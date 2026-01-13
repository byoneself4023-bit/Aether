"""
ML Service - FastAPI 메인 앱
민원 분류, 의도 분석 API 서비스
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api.routes import classify
from app.models.classifier import get_classifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    # 시작 시: 모델 로드
    logger.info("🚀 ML Service 시작...")
    try:
        get_classifier()  # 모델 미리 로드
        logger.info("✅ 모델 로드 완료!")
    except Exception as e:
        logger.warning(f"⚠️ 모델 로드 실패 (나중에 다시 시도): {e}")
    
    yield
    
    # 종료 시
    logger.info("👋 ML Service 종료")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 민원 AI 어시스턴트 - ML Service

민원 텍스트 분류 및 의도 분석 API

### 주요 기능
- 🏷️ **도메인 분류**: 민원 → 담당 부서 자동 분류
- 🎯 **의도 분석**: 민원 의도 파악 (예정)
- 📊 **배치 처리**: 여러 민원 한 번에 분류
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용, 운영에서는 특정 도메인만
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(
    classify.router,
    prefix=settings.API_V1_PREFIX
)


# ============ 기본 엔드포인트 ============

@app.get("/")
async def root():
    """서비스 정보"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


# ============ 실행 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
