"""Major #5: 구조화된 로깅 테스트"""

import json
import logging
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.logging import (
    StructuredLogFormatter,
    RequestLoggingMiddleware,
    request_id_var,
    setup_structured_logging,
)


client = TestClient(app)


class TestRequestIdGeneration:
    """X-Request-ID 생성 테스트"""

    def test_response_has_request_id(self):
        """응답에 X-Request-ID 헤더가 포함되는지 확인"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_custom_request_id_preserved(self):
        """요청에 X-Request-ID를 보내면 그대로 사용"""
        custom_id = "test-request-12345"
        response = client.get(
            "/health",
            headers={"X-Request-ID": custom_id},
        )
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

    def test_unique_request_ids(self):
        """각 요청마다 고유한 ID 생성"""
        ids = set()
        for _ in range(5):
            response = client.get("/health")
            ids.add(response.headers["X-Request-ID"])
        assert len(ids) == 5


class TestStructuredLogFormatter:
    """JSON 로그 포매터 테스트"""

    def test_log_format_is_json(self):
        """로그 출력이 유효한 JSON인지 확인"""
        formatter = StructuredLogFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed

    def test_log_includes_request_id(self):
        """request_id가 로그에 포함되는지 확인"""
        formatter = StructuredLogFormatter()
        token = request_id_var.set("test-req-id")

        try:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg="Test",
                args=(),
                exc_info=None,
            )
            output = formatter.format(record)
            parsed = json.loads(output)
            assert parsed["request_id"] == "test-req-id"
        finally:
            request_id_var.reset(token)

    def test_log_includes_extra_fields(self):
        """extra 필드가 포함되는지 확인"""
        formatter = StructuredLogFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Request",
            args=(),
            exc_info=None,
        )
        record.method = "GET"
        record.path = "/health"
        record.status_code = 200
        record.duration_ms = 12.5

        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["method"] == "GET"
        assert parsed["path"] == "/health"
        assert parsed["status_code"] == 200
        assert parsed["duration_ms"] == 12.5


class TestRequestResponseLogging:
    """요청/응답 로그 동작 테스트"""

    def test_existing_endpoints_work(self):
        """기존 엔드포인트가 미들웨어 추가 후에도 정상 동작"""
        response = client.get("/health")
        assert response.status_code == 200

        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data


class TestSetupStructuredLogging:
    """setup_structured_logging 테스트"""

    def test_setup_configures_handler(self):
        """핸들러가 StructuredLogFormatter를 사용하는지 확인"""
        setup_structured_logging(debug=False)
        root = logging.getLogger()
        assert len(root.handlers) > 0
        assert isinstance(root.handlers[0].formatter, StructuredLogFormatter)

    def test_setup_debug_level(self):
        """debug=True일 때 DEBUG 레벨 설정"""
        setup_structured_logging(debug=True)
        root = logging.getLogger()
        assert root.level == logging.DEBUG
        # 원래대로 복원
        setup_structured_logging(debug=False)
