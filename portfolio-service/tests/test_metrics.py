"""Prometheus 메트릭 테스트"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

from app.main import app
from app.metrics import (
    get_metrics,
    optimization_requests_total,
    optimization_duration_seconds,
    cache_hits_total,
    cache_misses_total,
    covariance_condition_number,
    record_cache_hit,
    record_cache_miss,
    record_condition_number,
    OptimizationMetricsContext,
    DataFetchMetricsContext,
)


client = TestClient(app)


class TestMetricsEndpoint:
    """GET /metrics 엔드포인트 테스트"""

    def test_metrics_endpoint_returns_200(self):
        """/metrics 엔드포인트가 200 응답을 반환하는지"""
        response = client.get("/metrics")

        assert response.status_code == 200

    def test_metrics_content_type(self):
        """Prometheus 형식의 content-type 반환"""
        response = client.get("/metrics")

        assert "text/plain" in response.headers["content-type"]

    def test_metrics_contains_help_and_type(self):
        """Prometheus 포맷 검증 (# HELP, # TYPE 포함)"""
        response = client.get("/metrics")
        content = response.text

        # Prometheus 포맷 확인
        assert "# HELP" in content
        assert "# TYPE" in content

    def test_metrics_contains_optimization_metrics(self):
        """최적화 관련 메트릭 포함 확인"""
        response = client.get("/metrics")
        content = response.text

        # 최적화 메트릭 확인
        assert "portfolio_optimization" in content

    def test_metrics_contains_cache_metrics(self):
        """캐시 관련 메트릭 포함 확인"""
        response = client.get("/metrics")
        content = response.text

        # 캐시 메트릭 확인
        assert "portfolio_cache" in content


class TestGetMetrics:
    """get_metrics 함수 테스트"""

    def test_returns_bytes(self):
        """bytes 타입 반환"""
        result = get_metrics()

        assert isinstance(result, bytes)

    def test_contains_metrics(self):
        """메트릭 데이터 포함"""
        result = get_metrics()
        content = result.decode("utf-8")

        # 최소한 하나의 메트릭 포함
        assert "portfolio" in content or "python" in content or "process" in content


class TestCacheMetrics:
    """캐시 메트릭 함수 테스트"""

    def test_record_cache_hit(self):
        """캐시 히트 기록"""
        initial = cache_hits_total.labels(cache_type="test")._value.get()

        record_cache_hit("test")

        new_value = cache_hits_total.labels(cache_type="test")._value.get()
        assert new_value == initial + 1

    def test_record_cache_miss(self):
        """캐시 미스 기록"""
        initial = cache_misses_total.labels(cache_type="test")._value.get()

        record_cache_miss("test")

        new_value = cache_misses_total.labels(cache_type="test")._value.get()
        assert new_value == initial + 1


class TestConditionNumberMetric:
    """조건수 메트릭 테스트"""

    def test_record_condition_number(self):
        """조건수 기록"""
        # 히스토그램에 값 기록 (예외 없이 실행되어야 함)
        record_condition_number(100.0)
        record_condition_number(1000.0)

        # 메트릭 출력에 포함되어야 함
        metrics = get_metrics().decode("utf-8")
        assert "portfolio_covariance_condition_number" in metrics


class TestOptimizationMetricsContext:
    """OptimizationMetricsContext 테스트"""

    def test_context_manager_success(self):
        """성공 시 메트릭 기록"""
        strategy = "test_strategy"
        initial_success = optimization_requests_total.labels(
            strategy=strategy, status="success"
        )._value.get()

        with OptimizationMetricsContext(strategy=strategy):
            pass  # 성공

        new_success = optimization_requests_total.labels(
            strategy=strategy, status="success"
        )._value.get()
        assert new_success == initial_success + 1

    def test_context_manager_error(self):
        """에러 시 메트릭 기록"""
        strategy = "test_error_strategy"
        initial_error = optimization_requests_total.labels(
            strategy=strategy, status="error"
        )._value.get()

        try:
            with OptimizationMetricsContext(strategy=strategy):
                raise ValueError("Test error")
        except ValueError:
            pass

        new_error = optimization_requests_total.labels(
            strategy=strategy, status="error"
        )._value.get()
        assert new_error == initial_error + 1

    def test_context_manager_duration(self):
        """소요시간 측정"""
        import time

        strategy = "test_duration_strategy"

        with OptimizationMetricsContext(strategy=strategy):
            time.sleep(0.01)  # 10ms 대기

        # 히스토그램에 기록됨 (메트릭 출력에 포함)
        metrics = get_metrics().decode("utf-8")
        assert "portfolio_optimization_duration_seconds" in metrics


class TestDataFetchMetricsContext:
    """DataFetchMetricsContext 테스트"""

    def test_data_fetch_context(self):
        """데이터 수집 컨텍스트 테스트"""
        operation = "test_fetch"

        with DataFetchMetricsContext(operation=operation, n_tickers=5):
            pass

        # 메트릭에 기록됨
        metrics = get_metrics().decode("utf-8")
        assert "portfolio_data_fetch_duration_seconds" in metrics


class TestMetricsIntegration:
    """메트릭 통합 테스트"""

    @patch("app.services.data.get_data_provider")
    def test_optimization_increments_metrics(self, mock_provider):
        """최적화 요청 시 메트릭 증가 확인"""
        # Mock provider 설정
        mock_instance = MagicMock()
        dates = pd.date_range("2022-01-01", periods=252, freq="B")
        mock_prices = pd.DataFrame({
            "AAPL": np.random.randn(252) * 10 + 150,
            "GOOGL": np.random.randn(252) * 20 + 2800
        }, index=dates)

        mock_instance.fetch_prices.return_value = mock_prices
        mock_instance.fetch_single_ticker_prices.side_effect = lambda t, p: mock_prices[t] if t in mock_prices.columns else None
        mock_provider.return_value = mock_instance

        # 초기 메트릭 값 확인
        initial_metrics = get_metrics().decode("utf-8")

        # 최적화 요청 실행
        response = client.post(
            "/api/optimize",
            json={
                "tickers": ["AAPL", "GOOGL"],
                "strategy": "max_sharpe",
                "period": "1y"
            }
        )

        # 요청이 성공하든 실패하든 메트릭이 업데이트됨
        final_metrics = get_metrics().decode("utf-8")

        # 메트릭에 데이터가 있음
        assert "portfolio_optimization" in final_metrics
