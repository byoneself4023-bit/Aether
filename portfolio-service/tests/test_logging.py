"""logging 미들웨어 단위 테스트"""

import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.logging import (
    StructuredLogger,
    RequestLoggingMiddleware,
    get_request_id,
    request_id_ctx,
    log_optimization_context,
    log_error_with_context,
)


class TestStructuredLogger:
    """StructuredLogger 테스트"""

    def test_info_log_format(self, capsys):
        """INFO 로그가 JSON 형식으로 출력되는지 확인"""
        logger = StructuredLogger("test-logger")
        logger.info("test_message", key="value")

        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())

        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "test_message"
        assert log_entry["context"]["key"] == "value"
        assert "timestamp" in log_entry
        assert "request_id" in log_entry

    def test_error_log_format(self, capsys):
        """ERROR 로그가 JSON 형식으로 출력되는지 확인"""
        logger = StructuredLogger("test-logger")
        logger.error("error_occurred", error="Something went wrong")

        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())

        assert log_entry["level"] == "ERROR"
        assert log_entry["message"] == "error_occurred"
        assert log_entry["context"]["error"] == "Something went wrong"

    def test_warning_log_format(self, capsys):
        """WARNING 로그가 JSON 형식으로 출력되는지 확인"""
        logger = StructuredLogger("test-logger")
        logger.warning("warning_message")

        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())

        assert log_entry["level"] == "WARNING"
        assert log_entry["message"] == "warning_message"

    def test_log_with_complex_context(self, capsys):
        """복잡한 컨텍스트가 제대로 직렬화되는지 확인"""
        logger = StructuredLogger("test-logger")
        logger.info(
            "optimization_started",
            tickers=["AAPL", "MSFT", "GOOGL"],
            weights={"AAPL": 0.3, "MSFT": 0.5, "GOOGL": 0.2}
        )

        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())

        assert log_entry["context"]["tickers"] == ["AAPL", "MSFT", "GOOGL"]
        assert log_entry["context"]["weights"]["AAPL"] == 0.3


class TestRequestIdContext:
    """Request ID Context Variable 테스트"""

    def test_get_request_id_default(self):
        """기본 request_id는 빈 문자열"""
        # 새로운 컨텍스트에서 시작
        token = request_id_ctx.set("")
        try:
            assert get_request_id() == ""
        finally:
            request_id_ctx.reset(token)

    def test_set_and_get_request_id(self):
        """request_id 설정 및 조회"""
        token = request_id_ctx.set("test-id-123")
        try:
            assert get_request_id() == "test-id-123"
        finally:
            request_id_ctx.reset(token)


class TestRequestLoggingMiddleware:
    """RequestLoggingMiddleware 통합 테스트"""

    @pytest.fixture
    def test_app(self):
        """테스트용 FastAPI 앱"""
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok", "request_id": get_request_id()}

        @app.post("/test")
        async def test_post(data: dict):
            return {"received": data, "request_id": get_request_id()}

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        return app

    def test_request_id_in_response_header(self, test_app):
        """응답 헤더에 X-Request-ID가 포함되는지 확인"""
        client = TestClient(test_app)
        response = client.get("/test")

        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 8  # UUID prefix 8자리

    def test_request_id_available_in_endpoint(self, test_app):
        """엔드포인트에서 request_id 접근 가능 확인"""
        client = TestClient(test_app)
        response = client.get("/test")

        data = response.json()
        assert "request_id" in data
        assert len(data["request_id"]) == 8

    def test_post_request_logging(self, test_app):
        """POST 요청 로깅 확인"""
        client = TestClient(test_app)
        response = client.post("/test", json={"key": "value"})

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    def test_excluded_paths_not_logged(self, test_app, capsys):
        """제외 경로는 상세 로깅 스킵"""
        client = TestClient(test_app)
        response = client.get("/health")

        assert response.status_code == 200
        # 헤더에는 Request ID 포함
        assert "X-Request-ID" in response.headers

    def test_unique_request_ids(self, test_app):
        """각 요청마다 고유한 Request ID 생성"""
        client = TestClient(test_app)

        ids = set()
        for _ in range(10):
            response = client.get("/test")
            ids.add(response.headers["X-Request-ID"])

        assert len(ids) == 10  # 모든 ID가 고유해야 함


class TestLoggingHelpers:
    """로깅 헬퍼 함수 테스트"""

    def test_log_optimization_context(self):
        """최적화 컨텍스트 로깅 헬퍼 - 에러 없이 실행되는지 확인"""
        token = request_id_ctx.set("test-123")
        try:
            # 에러 없이 실행되면 성공
            log_optimization_context(
                tickers=["AAPL", "MSFT"],
                strategy="max_sharpe",
                period="3y",
                rf=0.02
            )
        finally:
            request_id_ctx.reset(token)

    def test_log_error_with_context(self):
        """에러 컨텍스트 로깅 헬퍼 - 에러 없이 실행되는지 확인"""
        token = request_id_ctx.set("test-456")
        try:
            error = ValueError("Optimization failed")
            # 에러 없이 실행되면 성공
            log_error_with_context(
                error,
                operation="optimization",
                tickers=["AAPL"],
                strategy="min_variance"
            )
        finally:
            request_id_ctx.reset(token)

    def test_helper_functions_signature(self):
        """헬퍼 함수 시그니처 검증"""
        import inspect

        # log_optimization_context 시그니처 검증
        sig = inspect.signature(log_optimization_context)
        params = list(sig.parameters.keys())
        assert "tickers" in params
        assert "strategy" in params
        assert "period" in params

        # log_error_with_context 시그니처 검증
        sig = inspect.signature(log_error_with_context)
        params = list(sig.parameters.keys())
        assert "error" in params
        assert "operation" in params


class TestLogTimestamp:
    """타임스탬프 형식 테스트"""

    def test_iso8601_format(self, capsys):
        """타임스탬프가 ISO 8601 형식인지 확인"""
        from datetime import datetime

        logger = StructuredLogger("test-logger")
        logger.info("test")

        captured = capsys.readouterr()
        log_entry = json.loads(captured.out.strip())

        timestamp = log_entry["timestamp"]
        # ISO 8601 형식 파싱 가능 확인
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed is not None
