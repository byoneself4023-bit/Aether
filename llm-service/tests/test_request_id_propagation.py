"""httpx event_hooks가 X-Request-ID + Authorization을 자동 forward하는지 검증"""

from __future__ import annotations

import httpx
import pytest

from app.middleware.logging import request_id_var
from app.services.http_context import auth_token_var
from app.services.portfolio_client import _forward_headers, _get_client


@pytest.mark.asyncio
async def test_forward_headers_sets_request_id_when_present():
    request_id_var.set("test-rid-12345")
    auth_token_var.set("")
    request = httpx.Request("GET", "http://example.com")

    await _forward_headers(request)

    assert request.headers["X-Request-ID"] == "test-rid-12345"
    assert "Authorization" not in request.headers


@pytest.mark.asyncio
async def test_forward_headers_sets_authorization_when_token_present():
    request_id_var.set("")
    auth_token_var.set("abc.def.ghi")
    request = httpx.Request("POST", "http://example.com")

    await _forward_headers(request)

    assert request.headers["Authorization"] == "Bearer abc.def.ghi"


@pytest.mark.asyncio
async def test_forward_headers_truncates_request_id_at_64_chars():
    long_rid = "x" * 200
    request_id_var.set(long_rid)
    auth_token_var.set("")
    request = httpx.Request("GET", "http://example.com")

    await _forward_headers(request)

    assert len(request.headers["X-Request-ID"]) == 64


@pytest.mark.asyncio
async def test_forward_headers_skips_when_context_empty():
    request_id_var.set("")
    auth_token_var.set("")
    request = httpx.Request("GET", "http://example.com")

    await _forward_headers(request)

    assert "X-Request-ID" not in request.headers
    assert "Authorization" not in request.headers


def test_client_has_event_hook_registered():
    client = _get_client()
    try:
        hooks = client.event_hooks.get("request", [])
        assert _forward_headers in hooks
    finally:
        # AsyncClient는 close가 async지만 contextless 생성됐으니 GC에 맡김
        pass
