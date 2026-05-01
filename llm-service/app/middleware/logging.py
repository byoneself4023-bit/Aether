"""구조화된 로깅 미들웨어 - X-Request-ID 및 JSON 로그"""

import json
import logging
import re
import time
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# 요청별 request_id를 저장하는 context variable
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# Authorization Bearer 토큰 마스킹 패턴
_BEARER_TOKEN_RE = re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE)


def _mask_secrets(text: str) -> str:
    """로그 메시지에서 Bearer 토큰을 마스킹"""
    return _BEARER_TOKEN_RE.sub("Bearer ***", text)


logger = logging.getLogger(__name__)


class StructuredLogFormatter(logging.Formatter):
    """JSON 구조화 로그 포매터"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": _mask_secrets(record.getMessage()),
        }

        # request_id가 있으면 추가
        rid = request_id_var.get("")
        if rid:
            log_data["request_id"] = rid

        # 예외 정보가 있으면 추가
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = self.formatException(record.exc_info)

        # extra 필드 추가
        for key in ("method", "path", "status_code", "duration_ms", "client_ip"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        return _mask_secrets(json.dumps(log_data, ensure_ascii=False, default=str))


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어 with X-Request-ID"""

    async def dispatch(self, request: Request, call_next) -> Response:
        # X-Request-ID 생성 또는 기존 값 사용
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)

        start_time = time.time()

        # 요청 로그
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        try:
            response = await call_next(request)
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"Request failed: {e}",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # 응답 로그
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # X-Request-ID를 응답 헤더에 추가
        response.headers["X-Request-ID"] = request_id

        return response


def setup_structured_logging(debug: bool = False) -> None:
    """
    구조화된 로깅 설정.

    기존 logging.basicConfig 대신 사용.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # 기존 핸들러 제거
    root_logger.handlers.clear()

    # 구조화된 포매터로 핸들러 추가
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredLogFormatter())
    root_logger.addHandler(handler)
