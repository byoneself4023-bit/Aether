"""pytest 공통 fixture - JWT 환경 + verify_jwt 우회"""

from __future__ import annotations

import os
import time

# JWT_SECRET / GOOGLE_API_KEY가 모듈 로드 전에 set돼야 함 (Settings는 lru_cache + validator)
os.environ.setdefault("JWT_SECRET", "test-secret-for-pytest-only-must-be-32-bytes-min")
os.environ.setdefault("GOOGLE_API_KEY", "test-google-api-key-for-pytest-only")

import jwt
import pytest

from app.main import app
from app.middleware.auth import verify_jwt


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "no_jwt_bypass: do not stub verify_jwt for this test (use real verification)",
    )
    config.addinivalue_line(
        "markers",
        "use_react_agent: enable ReAct path (USE_REACT_AGENT=True) for this test (T-1b)",
    )


@pytest.fixture(autouse=True)
def _bypass_jwt(request: pytest.FixtureRequest):
    """기존 232+ 테스트가 그대로 통과하도록 verify_jwt를 stub. 'no_jwt_bypass' 마커로 opt-out."""
    if "no_jwt_bypass" in request.keywords:
        yield
        return
    app.dependency_overrides[verify_jwt] = lambda: {
        "sub": "1",
        "email": "test@aether.io",
        "role": "USER",
    }
    yield
    app.dependency_overrides.pop(verify_jwt, None)


@pytest.fixture(autouse=True)
def _disable_react_agent(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """기본 use_react_agent=False - 기존 258 mock 테스트 호환. opt-in: 'use_react_agent' marker."""
    from app.config import get_settings

    settings = get_settings()
    if request.node.get_closest_marker("use_react_agent"):
        monkeypatch.setattr(settings, "use_react_agent", True)
    else:
        monkeypatch.setattr(settings, "use_react_agent", False)
    yield


@pytest.fixture
def jwt_secret() -> str:
    return os.environ["JWT_SECRET"]


@pytest.fixture
def valid_token(jwt_secret: str) -> str:
    return jwt.encode(
        {
            "sub": "1",
            "email": "test@aether.io",
            "role": "USER",
            "exp": int(time.time()) + 3600,
        },
        jwt_secret,
        algorithm="HS512",
    )


@pytest.fixture
def expired_token(jwt_secret: str) -> str:
    return jwt.encode(
        {"sub": "1", "exp": int(time.time()) - 60},
        jwt_secret,
        algorithm="HS512",
    )


@pytest.fixture
def wrong_signature_token() -> str:
    return jwt.encode(
        {"sub": "1", "exp": int(time.time()) + 3600},
        "another-secret-that-differs-from-the-real-one",
        algorithm="HS512",
    )
