"""토큰 사용량 및 비용 추적"""

import threading
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)

# Gemini 2.5 Flash 가격 (USD per 1M tokens, 2025년 기준)
GEMINI_PRICING = {
    "input_per_1m": 0.15,   # $0.15 per 1M input tokens
    "output_per_1m": 0.60,  # $0.60 per 1M output tokens
}


@dataclass
class TokenUsage:
    """단일 요청의 토큰 사용량"""
    input_tokens: int = 0
    output_tokens: int = 0
    requests: int = 1
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TokenTracker:
    """스레드 안전한 토큰 사용량 추적기"""

    def __init__(self):
        self._lock = threading.Lock()
        self._usage_log: list[TokenUsage] = []
        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0
        self._total_requests: int = 0

    def record_usage(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """
        토큰 사용량 기록.

        Args:
            input_tokens: 입력 토큰 수
            output_tokens: 출력 토큰 수
        """
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        with self._lock:
            self._usage_log.append(usage)
            self._total_input_tokens += input_tokens
            self._total_output_tokens += output_tokens
            self._total_requests += 1

        logger.debug(
            f"Token usage recorded: input={input_tokens}, output={output_tokens}, "
            f"total_requests={self._total_requests}"
        )

    def get_summary(self) -> dict:
        """
        사용량 요약 반환.

        Returns:
            {
                "total_input_tokens": int,
                "total_output_tokens": int,
                "total_tokens": int,
                "total_requests": int,
                "estimated_cost_usd": float,
                "hourly": [...],
                "daily": [...],
            }
        """
        with self._lock:
            hourly = self._aggregate_by_hour()
            daily = self._aggregate_by_day()

            return {
                "total_input_tokens": self._total_input_tokens,
                "total_output_tokens": self._total_output_tokens,
                "total_tokens": self._total_input_tokens + self._total_output_tokens,
                "total_requests": self._total_requests,
                "estimated_cost_usd": self.estimate_cost(),
                "hourly": hourly,
                "daily": daily,
            }

    def estimate_cost(self) -> float:
        """
        Gemini 가격 기준 비용 산출 (USD).

        Returns:
            추정 비용 (USD)
        """
        input_cost = (self._total_input_tokens / 1_000_000) * GEMINI_PRICING["input_per_1m"]
        output_cost = (self._total_output_tokens / 1_000_000) * GEMINI_PRICING["output_per_1m"]
        return round(input_cost + output_cost, 6)

    def _aggregate_by_hour(self) -> list[dict]:
        """시간별 집계"""
        hourly: dict[str, dict] = defaultdict(
            lambda: {"input_tokens": 0, "output_tokens": 0, "requests": 0}
        )

        for usage in self._usage_log:
            hour_key = usage.timestamp.strftime("%Y-%m-%dT%H:00:00Z")
            hourly[hour_key]["input_tokens"] += usage.input_tokens
            hourly[hour_key]["output_tokens"] += usage.output_tokens
            hourly[hour_key]["requests"] += usage.requests

        return [
            {"hour": k, **v}
            for k, v in sorted(hourly.items())
        ]

    def _aggregate_by_day(self) -> list[dict]:
        """일별 집계"""
        daily: dict[str, dict] = defaultdict(
            lambda: {"input_tokens": 0, "output_tokens": 0, "requests": 0}
        )

        for usage in self._usage_log:
            day_key = usage.timestamp.strftime("%Y-%m-%d")
            daily[day_key]["input_tokens"] += usage.input_tokens
            daily[day_key]["output_tokens"] += usage.output_tokens
            daily[day_key]["requests"] += usage.requests

        return [
            {"date": k, **v}
            for k, v in sorted(daily.items())
        ]

    def reset(self) -> None:
        """사용량 초기화 (테스트용)"""
        with self._lock:
            self._usage_log.clear()
            self._total_input_tokens = 0
            self._total_output_tokens = 0
            self._total_requests = 0


# 싱글톤 인스턴스
_tracker = TokenTracker()


def get_tracker() -> TokenTracker:
    """글로벌 TokenTracker 인스턴스 반환"""
    return _tracker
