"""LLM 응답 캐시 - In-memory LRU"""

import hashlib
import logging
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DEFAULT_MAX_SIZE = 1000
DEFAULT_TTL_SECONDS = 3600  # 1시간


@dataclass
class CacheEntry:
    """캐시 엔트리"""
    value: str | dict
    created_at: float
    ttl: float


def _make_key(prompt: str, system_prompt: str | None = None, **kwargs) -> str:
    """
    캐시 키 생성.

    prompt + system_prompt + kwargs를 해시하여 일관된 키 생성.
    """
    parts = [prompt]
    if system_prompt:
        parts.append(system_prompt)
    for k in sorted(kwargs.keys()):
        v = kwargs[k]
        if v is not None:
            parts.append(f"{k}={v}")
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class LLMCache:
    """
    스레드 안전 LRU 캐시.

    - In-memory OrderedDict 기반
    - max_size 초과 시 가장 오래된 항목 제거 (LRU)
    - TTL 기반 만료
    """

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE, ttl: float = DEFAULT_TTL_SECONDS):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> str | dict | None:
        """
        캐시에서 값 조회.

        Returns:
            캐시된 값 또는 None (미스/만료)
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            # TTL 만료 확인
            if time.time() - entry.created_at > entry.ttl:
                del self._cache[key]
                self._misses += 1
                return None

            # LRU: 최근 사용으로 이동
            self._cache.move_to_end(key)
            self._hits += 1
            logger.debug(f"Cache hit: {key[:16]}...")
            return entry.value

    def set(self, key: str, value: str | dict, ttl: float | None = None) -> None:
        """
        캐시에 값 저장.
        """
        with self._lock:
            # 이미 존재하면 업데이트
            if key in self._cache:
                self._cache.move_to_end(key)

            self._cache[key] = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl if ttl is not None else self._ttl,
            )

            # max_size 초과 시 LRU 제거
            while len(self._cache) > self._max_size:
                removed_key, _ = self._cache.popitem(last=False)
                logger.debug(f"Cache evicted: {removed_key[:16]}...")

    def clear(self) -> None:
        """캐시 전체 삭제"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> dict:
        """캐시 통계"""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total, 3) if total > 0 else 0.0,
            }


# 글로벌 캐시 인스턴스
_llm_cache: LLMCache | None = None


def get_llm_cache() -> LLMCache:
    """글로벌 LLMCache 인스턴스 반환"""
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = LLMCache()
    return _llm_cache
