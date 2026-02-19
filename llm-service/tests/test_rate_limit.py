"""Minor #10: Rate Limiting 테스트"""

import pytest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.rate_limit import RateLimitMiddleware


def _create_test_app(requests_per_minute: int = 5) -> FastAPI:
    """rate limit가 적용된 테스트용 앱 생성"""
    test_app = FastAPI()
    test_app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)

    @test_app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    @test_app.get("/health")
    async def health():
        return {"status": "healthy"}

    return test_app


class TestRateLimitWithinLimit:
    """제한 이내 요청 통과 테스트"""

    def test_requests_within_limit_pass(self):
        """제한 이내 요청은 정상 통과"""
        app = _create_test_app(requests_per_minute=10)
        client = TestClient(app)

        for _ in range(10):
            response = client.get("/test")
            assert response.status_code == 200

    def test_single_request_passes(self):
        """단일 요청은 항상 통과"""
        app = _create_test_app(requests_per_minute=60)
        client = TestClient(app)

        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


class TestRateLimitExceeded:
    """제한 초과 시 429 반환 테스트"""

    def test_returns_429_when_exceeded(self):
        """제한 초과 시 429 반환"""
        app = _create_test_app(requests_per_minute=3)
        client = TestClient(app)

        # 3개는 통과
        for _ in range(3):
            response = client.get("/test")
            assert response.status_code == 200

        # 4번째부터 429
        response = client.get("/test")
        assert response.status_code == 429
        data = response.json()
        assert "Too many requests" in data["detail"]
        assert "Retry-After" in response.headers

    def test_health_exempt_from_rate_limit(self):
        """health 엔드포인트는 rate limit 제외"""
        app = _create_test_app(requests_per_minute=2)
        client = TestClient(app)

        # rate limit 소진
        for _ in range(2):
            client.get("/test")

        # /test는 429
        response = client.get("/test")
        assert response.status_code == 429

        # /health는 여전히 통과
        response = client.get("/health")
        assert response.status_code == 200


class TestRateLimitPerIP:
    """IP별 독립 카운트 테스트"""

    def test_different_ips_independent(self):
        """다른 IP는 독립적으로 카운트"""
        app = _create_test_app(requests_per_minute=2)
        client = TestClient(app)

        # IP-A: 2회 요청
        for _ in range(2):
            response = client.get("/test", headers={"X-Forwarded-For": "1.1.1.1"})
            assert response.status_code == 200

        # IP-A는 이제 제한
        response = client.get("/test", headers={"X-Forwarded-For": "1.1.1.1"})
        assert response.status_code == 429

        # IP-B는 아직 가능
        response = client.get("/test", headers={"X-Forwarded-For": "2.2.2.2"})
        assert response.status_code == 200


class TestExistingEndpoints:
    """기존 엔드포인트 정상 동작 확인"""

    def test_main_app_health_works(self):
        from app.main import app
        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200

    def test_main_app_root_works(self):
        from app.main import app
        client = TestClient(app)

        response = client.get("/")
        assert response.status_code == 200
