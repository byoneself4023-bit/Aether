"""Minor #12: Health Check 강화 테스트"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthCheckStructure:
    """응답 구조 테스트"""

    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_checks_field(self):
        """checks 딕셔너리 존재 확인"""
        response = client.get("/health")
        data = response.json()
        assert "checks" in data
        assert "api_key" in data["checks"]
        assert "vectorstore" in data["checks"]
        assert "portfolio_service" in data["checks"]

    def test_health_has_timestamp(self):
        """timestamp 필드 존재 확인"""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data

    def test_health_has_service_info(self):
        """서비스 정보 존재"""
        response = client.get("/health")
        data = response.json()
        assert "service" in data
        assert "version" in data


class TestHealthCheckHealthy:
    """전부 정상 시 healthy 테스트"""

    @patch("app.main.portfolio_is_available", new_callable=AsyncMock, return_value=True)
    @patch("app.services.rag.get_vectorstore_status", return_value={"initialized": True, "document_count": 50})
    def test_all_ok_returns_healthy(self, mock_vs, mock_portfolio):
        response = client.get("/health")
        data = response.json()

        assert data["checks"]["portfolio_service"] == "ok"
        assert data["checks"]["vectorstore"] == "ok"
        # api_key는 실행 환경에 따라 다를 수 있으므로 구조만 확인
        assert "api_key" in data["checks"]


class TestHealthCheckDegraded:
    """일부 실패 시 degraded 테스트"""

    @patch("app.main.portfolio_is_available", new_callable=AsyncMock, return_value=False)
    def test_portfolio_unavailable_returns_degraded(self, mock_portfolio):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["portfolio_service"] == "unavailable"

    @patch("app.main.portfolio_is_available", new_callable=AsyncMock, side_effect=Exception("conn error"))
    def test_portfolio_error_returns_degraded(self, mock_portfolio):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["portfolio_service"] == "unavailable"

    def test_vectorstore_not_initialized(self):
        """벡터스토어 미초기화 시 not_initialized"""
        import app.services.rag as rag_module
        original = rag_module._initialized

        rag_module._initialized = False
        try:
            response = client.get("/health")
            data = response.json()
            assert data["checks"]["vectorstore"] == "not_initialized"
        finally:
            rag_module._initialized = original
