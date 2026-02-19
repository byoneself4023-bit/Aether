"""Prometheus 메트릭 정의"""

from prometheus_client import Counter, Histogram, Gauge, REGISTRY
from prometheus_client.exposition import generate_latest
import time
from functools import wraps
from typing import Callable, Any


# ============================================================
# Optimization Metrics
# ============================================================

# 최적화 요청 카운터 (전략/상태별)
optimization_requests_total = Counter(
    "portfolio_optimization_requests_total",
    "Total number of optimization requests",
    ["strategy", "status"]
)

# 최적화 소요시간 히스토그램
optimization_duration_seconds = Histogram(
    "portfolio_optimization_duration_seconds",
    "Time spent on optimization",
    ["strategy"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# 공분산 행렬 조건수 히스토그램
covariance_condition_number = Histogram(
    "portfolio_covariance_condition_number",
    "Condition number of covariance matrix",
    buckets=(1, 10, 100, 1000, 10000, 100000, 1000000, 10000000)
)


# ============================================================
# Cache Metrics
# ============================================================

# 캐시 히트/미스 카운터
cache_hits_total = Counter(
    "portfolio_cache_hits_total",
    "Total number of cache hits",
    ["cache_type"]
)

cache_misses_total = Counter(
    "portfolio_cache_misses_total",
    "Total number of cache misses",
    ["cache_type"]
)


# ============================================================
# Data Fetch Metrics
# ============================================================

# 데이터 수집 소요시간 히스토그램
data_fetch_duration_seconds = Histogram(
    "portfolio_data_fetch_duration_seconds",
    "Time spent fetching market data",
    ["operation"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0)
)

# 활성 티커 게이지 (현재 처리 중인 티커 수)
active_tickers_gauge = Gauge(
    "portfolio_active_tickers",
    "Number of tickers currently being processed"
)


# ============================================================
# Risk Metrics
# ============================================================

# 리스크 계산 요청 카운터
risk_requests_total = Counter(
    "portfolio_risk_requests_total",
    "Total number of risk calculation requests",
    ["status"]
)


# ============================================================
# Backtest Metrics
# ============================================================

# 백테스트 요청 카운터
backtest_requests_total = Counter(
    "portfolio_backtest_requests_total",
    "Total number of backtest requests",
    ["strategy", "window_type", "status"]
)


# ============================================================
# Helper Functions
# ============================================================

def get_metrics() -> bytes:
    """
    Prometheus 포맷의 메트릭 데이터 반환

    Returns:
        Prometheus exposition format bytes
    """
    return generate_latest(REGISTRY)


def track_optimization_time(strategy: str):
    """
    최적화 시간 측정 데코레이터

    Args:
        strategy: 최적화 전략 이름
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with optimization_duration_seconds.labels(strategy=strategy).time():
                return func(*args, **kwargs)
        return wrapper
    return decorator


def track_data_fetch_time(operation: str):
    """
    데이터 수집 시간 측정 데코레이터

    Args:
        operation: 작업 이름 (예: "fetch_prices", "fetch_returns")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with data_fetch_duration_seconds.labels(operation=operation).time():
                return func(*args, **kwargs)
        return wrapper
    return decorator


class OptimizationMetricsContext:
    """최적화 메트릭 수집을 위한 컨텍스트 매니저"""

    def __init__(self, strategy: str):
        self.strategy = strategy
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        # 소요시간 기록
        optimization_duration_seconds.labels(strategy=self.strategy).observe(duration)

        # 상태별 요청 카운터
        if exc_type is None:
            optimization_requests_total.labels(strategy=self.strategy, status="success").inc()
        else:
            optimization_requests_total.labels(strategy=self.strategy, status="error").inc()

        return False  # 예외 전파


class DataFetchMetricsContext:
    """데이터 수집 메트릭 수집을 위한 컨텍스트 매니저"""

    def __init__(self, operation: str, n_tickers: int = 0):
        self.operation = operation
        self.n_tickers = n_tickers
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        if self.n_tickers > 0:
            active_tickers_gauge.inc(self.n_tickers)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        data_fetch_duration_seconds.labels(operation=self.operation).observe(duration)

        if self.n_tickers > 0:
            active_tickers_gauge.dec(self.n_tickers)

        return False


def record_cache_hit(cache_type: str):
    """캐시 히트 기록"""
    cache_hits_total.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """캐시 미스 기록"""
    cache_misses_total.labels(cache_type=cache_type).inc()


def record_condition_number(condition_number: float):
    """공분산 행렬 조건수 기록"""
    covariance_condition_number.observe(condition_number)


def record_risk_request(status: str = "success"):
    """리스크 계산 요청 기록"""
    risk_requests_total.labels(status=status).inc()


def record_backtest_request(strategy: str, window_type: str, status: str = "success"):
    """백테스트 요청 기록"""
    backtest_requests_total.labels(
        strategy=strategy,
        window_type=window_type,
        status=status
    ).inc()
