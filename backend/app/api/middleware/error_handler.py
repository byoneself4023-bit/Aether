"""
글로벌 예외 핸들러
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import ClaroError


async def claro_error_handler(request: Request, exc: ClaroError) -> JSONResponse:
    """ClaroError 계열 예외를 표준 JSON 응답으로 변환"""
    logger.error(f"[{exc.status_code}] {exc.message} — {request.method} {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "error": exc.message},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """처리되지 않은 예외를 500으로 변환"""
    logger.exception(f"Unhandled error — {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "data": None, "error": "내부 서버 오류가 발생했습니다."},
    )
