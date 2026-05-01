"""pytest 공통 fixture - JWT 환경 + verify_jwt 우회"""

from __future__ import annotations

import os
import time

os.environ.setdefault("JWT_SECRET", "test-secret-for-pytest-only-must-be-32-bytes-min")

import jwt
import pytest

from app.main import app
from app.middleware.auth import verify_jwt


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "no_jwt_bypass: do not stub verify_jwt for this test (use real verification)",
    )


@pytest.fixture(autouse=True)
def _bypass_jwt(request: pytest.FixtureRequest):
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
        algorithm="HS256",
    )


@pytest.fixture
def expired_token(jwt_secret: str) -> str:
    return jwt.encode(
        {"sub": "1", "exp": int(time.time()) - 60},
        jwt_secret,
        algorithm="HS256",
    )


@pytest.fixture
def wrong_signature_token() -> str:
    return jwt.encode(
        {"sub": "1", "exp": int(time.time()) + 3600},
        "another-secret-that-differs-from-the-real-one",
        algorithm="HS256",
    )
