"""IP 기반 Rate Limiting 미들웨어"""

import time
import threading
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    IP 기반 분당 요청 제한 미들웨어.

    제한 초과 시 429 Too Many Requests 반환.
    """

    def __init__(self, app, requests_per_minute: int | None = None):
        super().__init__(app)
        settings = get_settings()
        self.requests_per_minute = requests_per_minute or settings.rate_limit_per_minute
        self._lock = threading.Lock()
        # IP -> list of request timestamps
        self._request_log: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 추출"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        """요청 제한 초과 여부 확인 및 기록"""
        now = time.time()
        window_start = now - 60.0

        with self._lock:
            # 만료된 요청 제거
            timestamps = self._request_log[client_ip]
            self._request_log[client_ip] = [
                ts for ts in timestamps if ts > window_start
            ]

            if len(self._request_log[client_ip]) >= self.requests_per_minute:
                return True

            self._request_log[client_ip].append(now)
            return False

    async def dispatch(self, request: Request, call_next) -> Response:
        # health check는 rate limit 제외
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after_seconds": 60,
                },
                headers={"Retry-After": "60"},
            )

        return await call_next(request)
