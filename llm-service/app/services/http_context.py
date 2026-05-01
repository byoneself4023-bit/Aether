"""httpx forward용 ContextVar - verify_jwt가 토큰을 set, portfolio_client event_hook이 read"""

from __future__ import annotations

from contextvars import ContextVar

# 현재 요청의 Authorization Bearer 토큰. verify_jwt가 set, httpx event_hook이 forward.
auth_token_var: ContextVar[str] = ContextVar("auth_token", default="")
