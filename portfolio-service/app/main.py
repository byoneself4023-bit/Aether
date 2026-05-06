import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import optimize, risk, backtest, metrics
from app.middleware.logging import RequestLoggingMiddleware, logger

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Portfolio optimization, risk analysis, and backtesting API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Request Logging 미들웨어 (가장 먼저 추가 - 모든 요청 추적)
app.add_middleware(RequestLoggingMiddleware)

# CORS 설정
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# 애플리케이션 시작 로그
logger.info("application_started", version=settings.app_version)

# 라우터 등록
app.include_router(optimize.router)
app.include_router(risk.router)
app.include_router(backtest.router)
app.include_router(metrics.router)


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    from app.middleware.logging import get_request_id
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "request_id": get_request_id(),
    }


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "endpoints": {
            "optimize": "POST /api/optimize",
            "risk": "POST /api/risk",
            "backtest": "POST /api/backtest",
        }
    }
