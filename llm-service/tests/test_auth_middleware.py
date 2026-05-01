"""verify_jwt dependency 단위 테스트 - 헤더 누락/만료/위조 시 401"""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.middleware.auth import verify_jwt


@pytest.fixture
def auth_app() -> FastAPI:
    """verify_jwt만 검증할 최소 FastAPI 앱"""
    app = FastAPI()

    @app.get("/protected")
    async def protected(user: dict = Depends(verify_jwt)) -> dict:
        return {"sub": user.get("sub")}

    return app


@pytest.fixture
def auth_client(auth_app: FastAPI) -> TestClient:
    return TestClient(auth_app)


@pytest.mark.no_jwt_bypass
class TestVerifyJwt:
    def test_missing_authorization_header_returns_401(self, auth_client: TestClient):
        response = auth_client.get("/protected")
        assert response.status_code == 401
        assert "Bearer token" in response.json()["detail"]

    def test_wrong_scheme_returns_401(self, auth_client: TestClient):
        response = auth_client.get("/protected", headers={"Authorization": "Basic abc"})
        assert response.status_code == 401

    def test_malformed_token_returns_401(self, auth_client: TestClient):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_expired_token_returns_401(self, auth_client: TestClient, expired_token: str):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_wrong_signature_returns_401(self, auth_client: TestClient, wrong_signature_token: str):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {wrong_signature_token}"},
        )
        assert response.status_code == 401

    def test_valid_token_returns_200(self, auth_client: TestClient, valid_token: str):
        response = auth_client.get(
            "/protected",
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"sub": "1"}

    def test_valid_token_sets_auth_token_var(self, valid_token: str):
        """verify_jwt 통과 시 auth_token_var에 토큰이 설정돼 httpx forward에 사용됨"""
        from app.services.http_context import auth_token_var

        captured: dict[str, str] = {}

        probe_app = FastAPI()

        @probe_app.get("/probe")
        async def probe(user: dict = Depends(verify_jwt)) -> dict:
            captured["token"] = auth_token_var.get("")
            return {}

        with TestClient(probe_app) as probe_client:
            probe_client.get(
                "/probe",
                headers={"Authorization": f"Bearer {valid_token}"},
            )
        assert captured["token"] == valid_token
