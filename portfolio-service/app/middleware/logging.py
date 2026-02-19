"""Structured Logging + Request ID 미들웨어"""

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Request ID를 저장하는 context variable (스레드/코루틴 안전)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """현재 요청의 Request ID 반환"""
    return request_id_ctx.get()


class StructuredLogger:
    """
    JSON 형식의 구조화된 로거

    새벽 3시 장애 시 로그 검색을 위해:
    - request_id로 요청 추적
    - 타임스탬프 ISO 8601 형식
    - 컨텍스트 정보 (티커, 파라미터 등) 포함
    """

    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 기존 핸들러 제거 (중복 방지)
        self.logger.handlers.clear()

        # JSON 출력 핸들러
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

        # 상위 로거 전파 방지
        self.logger.propagate = False

    def _format_log(
        self,
        level: str,
        message: str,
        **kwargs: Any
    ) -> str:
        """로그 엔트리를 JSON으로 포맷"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "request_id": get_request_id() or "no-request",
            "message": message,
        }

        # 추가 컨텍스트 병합
        if kwargs:
            log_entry["context"] = kwargs

        return json.dumps(log_entry, ensure_ascii=False, default=str)

    def info(self, message: str, **kwargs: Any) -> None:
        """INFO 레벨 로그"""
        self.logger.info(self._format_log("INFO", message, **kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        """ERROR 레벨 로그"""
        self.logger.error(self._format_log("ERROR", message, **kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        """WARNING 레벨 로그"""
        self.logger.warning(self._format_log("WARNING", message, **kwargs))

    def debug(self, message: str, **kwargs: Any) -> None:
        """DEBUG 레벨 로그"""
        self.logger.debug(self._format_log("DEBUG", message, **kwargs))


# 전역 로거 인스턴스
logger = StructuredLogger("portfolio-service")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 요청/응답 로깅 미들웨어

    기능:
    - 각 요청에 고유 Request ID 부여
    - 요청 시작/완료/실패 로깅
    - 응답 헤더에 X-Request-ID 추가
    - 처리 시간 측정
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list[str]] = None
    ):
        super().__init__(app)
        # 로깅에서 제외할 경로 (헬스체크 등)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Request ID 생성 (8자리 UUID prefix)
        request_id = str(uuid.uuid4())[:8]
        request_id_ctx.set(request_id)

        # 제외 경로는 로깅 스킵
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        start_time = time.perf_counter()

        # 요청 시작 로깅 (body는 로깅하지 않음 - BaseHTTPMiddleware stream 충돌 방지)
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None
        )

        try:
            response = await call_next(request)

            duration_ms = (time.perf_counter() - start_time) * 1000

            # 요청 완료 로깅
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )

            # 응답 헤더에 Request ID 추가
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # 에러 로깅 (스택트레이스 포함)
            logger.error(
                "request_failed",
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2)
            )

            raise


def log_optimization_context(
    tickers: list[str],
    strategy: str,
    period: str,
    **extra: Any
) -> None:
    """최적화 요청 컨텍스트 로깅 헬퍼"""
    logger.info(
        "optimization_context",
        tickers=tickers,
        n_tickers=len(tickers),
        strategy=strategy,
        period=period,
        **extra
    )


def log_error_with_context(
    error: Exception,
    operation: str,
    **context: Any
) -> None:
    """에러 + 컨텍스트 로깅 헬퍼"""
    logger.error(
        f"{operation}_failed",
        error_type=type(error).__name__,
        error_message=str(error),
        **context
    )
