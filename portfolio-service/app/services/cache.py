"""시장 데이터 캐시 서비스

트래픽 100배 시 yfinance API 병목을 해결하기 위한 캐시 레이어.
- 인메모리 캐시 (기본, Redis 없이 동작)
- Redis 캐시 (선택, 분산 환경용)
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Any, Optional

import pandas as pd

from app.config import get_settings
from app.middleware.logging import logger


@dataclass
class CacheEntry:
    """캐시 엔트리"""
    data: Any
    created_at: float
    ttl: int  # seconds


class CacheBackend(ABC):
    """캐시 백엔드 인터페이스"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> None:
        """캐시에 값 저장"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """캐시에서 값 삭제"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """캐시 전체 삭제"""
        pass


class InMemoryCache(CacheBackend):
    """
    인메모리 LRU 캐시 (단일 인스턴스용, OrderedDict 기반 O(1) eviction)

    장점:
    - 외부 의존성 없음
    - LRU eviction O(1) (popitem(last=False))
    - get() hit 시 키를 끝으로 이동 (move_to_end)

    단점:
    - 재시작 시 초기화
    - 다중 인스턴스 시 캐시 공유 불가 (시나리오 B 진입 시 RedisCache로 전환)
    """

    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry is None:
            return None

        # TTL 체크
        if time.time() - entry.created_at > entry.ttl:
            del self._cache[key]
            return None

        # LRU: hit 시 키를 끝으로 이동 (가장 최근 사용)
        self._cache.move_to_end(key)
        return entry.data

    def set(self, key: str, value: Any, ttl: int) -> None:
        # 기존 키 갱신 시 끝으로 이동
        if key in self._cache:
            self._cache.move_to_end(key)

        # 캐시 크기 제한 (LRU eviction)
        elif len(self._cache) >= self._max_size:
            self._evict_oldest()

        self._cache[key] = CacheEntry(
            data=value,
            created_at=time.time(),
            ttl=ttl
        )

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    def _evict_oldest(self) -> None:
        """가장 오랫동안 미사용 엔트리 삭제 (LRU, O(1))"""
        if not self._cache:
            return
        self._cache.popitem(last=False)

    @property
    def size(self) -> int:
        """현재 캐시 크기"""
        return len(self._cache)


class RedisCache(CacheBackend):
    """
    Redis 캐시 (분산 환경용)

    환경 변수로 REDIS_URL 설정 필요.
    Redis 연결 실패 시 graceful하게 캐시 미스 처리.
    """

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._client = None
        self._connect()

    def _connect(self) -> None:
        """Redis 연결 (실패해도 에러 안 냄)"""
        try:
            import redis
            self._client = redis.from_url(
                self._redis_url,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # 연결 테스트
            self._client.ping()
            logger.info("redis_connected", url=self._redis_url[:20] + "...")
        except Exception as e:
            logger.warning(
                "redis_connection_failed",
                error=str(e),
                fallback="cache_miss"
            )
            self._client = None

    def get(self, key: str) -> Optional[Any]:
        if self._client is None:
            return None

        try:
            data = self._client.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception as e:
            logger.warning("redis_get_failed", key=key, error=str(e))
            return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        if self._client is None:
            return

        try:
            self._client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.warning("redis_set_failed", key=key, error=str(e))

    def delete(self, key: str) -> None:
        if self._client is None:
            return

        try:
            self._client.delete(key)
        except Exception as e:
            logger.warning("redis_delete_failed", key=key, error=str(e))

    def clear(self) -> None:
        if self._client is None:
            return

        try:
            self._client.flushdb()
        except Exception as e:
            logger.warning("redis_clear_failed", error=str(e))


class MarketDataCache:
    """
    시장 데이터 전용 캐시

    기능:
    - 가격 데이터 캐시 (DataFrame)
    - 수익률 데이터 캐시
    - 공분산 행렬 캐시
    - 티커 검증 결과 캐시
    """

    # 캐시 TTL 설정 (초)
    PRICE_TTL = 3600  # 1시간 (장 중에는 15분으로 조정 가능)
    RETURNS_TTL = 3600
    COVARIANCE_TTL = 3600
    TICKER_VALIDATION_TTL = 86400  # 24시간

    def __init__(self, backend: Optional[CacheBackend] = None):
        """
        Args:
            backend: 캐시 백엔드 (None이면 인메모리 사용)
        """
        self._backend = backend or InMemoryCache()
        self._stats = {
            "hits": 0,
            "misses": 0,
        }

    @staticmethod
    def _generate_key(prefix: str, tickers: list[str], period: str) -> str:
        """캐시 키 생성"""
        sorted_tickers = ",".join(sorted(tickers))
        hash_input = f"{sorted_tickers}:{period}"
        ticker_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        return f"{prefix}:{ticker_hash}"

    def get_prices(
        self,
        tickers: list[str],
        period: str
    ) -> Optional[pd.DataFrame]:
        """가격 데이터 캐시 조회"""
        key = self._generate_key("prices", tickers, period)
        cached = self._backend.get(key)

        if cached is not None:
            self._stats["hits"] += 1
            logger.info(
                "cache_hit",
                cache_type="prices",
                tickers=tickers[:3],  # 로그 크기 제한
                n_tickers=len(tickers)
            )
            # JSON → DataFrame 복원
            return pd.DataFrame(cached["data"], index=pd.to_datetime(cached["index"]))

        self._stats["misses"] += 1
        return None

    def set_prices(
        self,
        tickers: list[str],
        period: str,
        df: pd.DataFrame
    ) -> None:
        """가격 데이터 캐시 저장"""
        key = self._generate_key("prices", tickers, period)

        # DataFrame → JSON 직렬화
        cache_data = {
            "data": df.to_dict(),
            "index": [str(idx) for idx in df.index]
        }

        self._backend.set(key, cache_data, self.PRICE_TTL)
        logger.info(
            "cache_set",
            cache_type="prices",
            n_tickers=len(tickers),
            n_rows=len(df)
        )

    def get_returns(
        self,
        tickers: list[str],
        period: str
    ) -> Optional[pd.DataFrame]:
        """수익률 데이터 캐시 조회"""
        key = self._generate_key("returns", tickers, period)
        cached = self._backend.get(key)

        if cached is not None:
            self._stats["hits"] += 1
            return pd.DataFrame(cached["data"], index=pd.to_datetime(cached["index"]))

        self._stats["misses"] += 1
        return None

    def set_returns(
        self,
        tickers: list[str],
        period: str,
        df: pd.DataFrame
    ) -> None:
        """수익률 데이터 캐시 저장"""
        key = self._generate_key("returns", tickers, period)

        cache_data = {
            "data": df.to_dict(),
            "index": [str(idx) for idx in df.index]
        }

        self._backend.set(key, cache_data, self.RETURNS_TTL)

    def get_ticker_validation(
        self,
        ticker: str
    ) -> Optional[bool]:
        """티커 검증 결과 캐시 조회"""
        key = f"ticker_valid:{ticker}"
        return self._backend.get(key)

    def set_ticker_validation(
        self,
        ticker: str,
        is_valid: bool
    ) -> None:
        """티커 검증 결과 캐시 저장"""
        key = f"ticker_valid:{ticker}"
        self._backend.set(key, is_valid, self.TICKER_VALIDATION_TTL)

    def invalidate(self, tickers: list[str], period: str) -> None:
        """특정 캐시 무효화"""
        for prefix in ["prices", "returns"]:
            key = self._generate_key(prefix, tickers, period)
            self._backend.delete(key)

    def clear(self) -> None:
        """전체 캐시 삭제"""
        self._backend.clear()
        self._stats = {"hits": 0, "misses": 0}

    @property
    def stats(self) -> dict:
        """캐시 통계"""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0
        return {
            **self._stats,
            "hit_rate": round(hit_rate, 4),
            "total_requests": total
        }


# 전역 캐시 인스턴스 (싱글톤)
_cache_instance: Optional[MarketDataCache] = None


def get_cache() -> MarketDataCache:
    """전역 캐시 인스턴스 반환"""
    global _cache_instance

    if _cache_instance is None:
        settings = get_settings()

        # Redis URL이 설정되어 있으면 Redis 사용
        redis_url = getattr(settings, "redis_url", None)
        if redis_url:
            backend = RedisCache(redis_url)
        else:
            backend = InMemoryCache(max_size=settings.cache_maxsize)

        _cache_instance = MarketDataCache(backend)
        logger.info(
            "cache_initialized",
            backend=type(backend).__name__
        )

    return _cache_instance


def reset_cache() -> None:
    """캐시 인스턴스 리셋 (테스트용)"""
    global _cache_instance
    if _cache_instance:
        _cache_instance.clear()
    _cache_instance = None
