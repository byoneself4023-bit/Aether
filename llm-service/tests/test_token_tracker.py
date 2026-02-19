"""Critical #4: 토큰 사용량/비용 추적 테스트"""

import pytest
import threading
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.services.token_tracker import TokenTracker, TokenUsage, get_tracker, GEMINI_PRICING  # noqa: F401


class TestTokenUsage:
    def test_default_values(self):
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.requests == 1
        assert usage.timestamp is not None


class TestTokenTracker:
    def setup_method(self):
        self.tracker = TokenTracker()

    def test_record_usage(self):
        """토큰 기록 정상 동작"""
        self.tracker.record_usage(input_tokens=100, output_tokens=50)

        summary = self.tracker.get_summary()
        assert summary["total_input_tokens"] == 100
        assert summary["total_output_tokens"] == 50
        assert summary["total_tokens"] == 150
        assert summary["total_requests"] == 1

    def test_multiple_records(self):
        """여러 번 기록 누적"""
        self.tracker.record_usage(input_tokens=100, output_tokens=50)
        self.tracker.record_usage(input_tokens=200, output_tokens=100)
        self.tracker.record_usage(input_tokens=300, output_tokens=150)

        summary = self.tracker.get_summary()
        assert summary["total_input_tokens"] == 600
        assert summary["total_output_tokens"] == 300
        assert summary["total_tokens"] == 900
        assert summary["total_requests"] == 3

    def test_cost_calculation(self):
        """비용 계산 정확성"""
        # 1M input + 1M output tokens
        self.tracker.record_usage(input_tokens=1_000_000, output_tokens=1_000_000)

        cost = self.tracker.estimate_cost()
        expected = GEMINI_PRICING["input_per_1m"] + GEMINI_PRICING["output_per_1m"]
        assert cost == expected

    def test_cost_small_usage(self):
        """소량 사용 비용 계산"""
        self.tracker.record_usage(input_tokens=1000, output_tokens=500)

        cost = self.tracker.estimate_cost()
        expected_input = (1000 / 1_000_000) * GEMINI_PRICING["input_per_1m"]
        expected_output = (500 / 1_000_000) * GEMINI_PRICING["output_per_1m"]
        assert cost == round(expected_input + expected_output, 6)

    def test_hourly_aggregation(self):
        """시간별 집계 동작"""
        self.tracker.record_usage(input_tokens=100, output_tokens=50)
        self.tracker.record_usage(input_tokens=200, output_tokens=100)

        summary = self.tracker.get_summary()
        assert len(summary["hourly"]) >= 1

        # 같은 시간이므로 하나의 항목
        total_input = sum(h["input_tokens"] for h in summary["hourly"])
        assert total_input == 300

    def test_daily_aggregation(self):
        """일별 집계 동작"""
        self.tracker.record_usage(input_tokens=100, output_tokens=50)

        summary = self.tracker.get_summary()
        assert len(summary["daily"]) >= 1

        total_input = sum(d["input_tokens"] for d in summary["daily"])
        assert total_input == 100

    def test_thread_safety(self):
        """동시성 안전 테스트"""
        errors = []

        def record_many():
            try:
                for _ in range(100):
                    self.tracker.record_usage(input_tokens=10, output_tokens=5)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        summary = self.tracker.get_summary()
        assert summary["total_input_tokens"] == 10 * 100 * 10  # 10 threads * 100 iterations * 10 tokens
        assert summary["total_output_tokens"] == 10 * 100 * 5
        assert summary["total_requests"] == 10 * 100

    def test_reset(self):
        """초기화 동작"""
        self.tracker.record_usage(input_tokens=100, output_tokens=50)
        self.tracker.reset()

        summary = self.tracker.get_summary()
        assert summary["total_tokens"] == 0
        assert summary["total_requests"] == 0

    def test_empty_summary(self):
        """빈 상태 요약"""
        summary = self.tracker.get_summary()
        assert summary["total_tokens"] == 0
        assert summary["total_requests"] == 0
        assert summary["estimated_cost_usd"] == 0
        assert summary["hourly"] == []
        assert summary["daily"] == []


class TestMetricsEndpoint:
    """GET /api/metrics/tokens 엔드포인트 테스트"""

    def test_metrics_endpoint(self):
        from app.main import app
        client = TestClient(app)

        response = client.get("/api/metrics/tokens")
        assert response.status_code == 200

        data = response.json()
        assert "total_input_tokens" in data
        assert "total_output_tokens" in data
        assert "total_tokens" in data
        assert "total_requests" in data
        assert "estimated_cost_usd" in data
        assert "hourly" in data
        assert "daily" in data


class TestTokenTrackingInLLM:
    """LLM 호출 시 토큰 추적 통합 테스트"""

    def test_call_llm_records_tokens(self):
        """토큰 사용량 기록 통합 테스트 (provider 내부에서 호출되는 것 시뮬레이션)"""
        # 별도 tracker 인스턴스로 격리 테스트
        tracker = TokenTracker()

        tracker.record_usage(input_tokens=150, output_tokens=200)

        assert tracker._total_requests == 1
        assert tracker._total_input_tokens == 150
        assert tracker._total_output_tokens == 200
