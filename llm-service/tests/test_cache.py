"""Minor #11: LLM 응답 캐시 테스트"""

import time
import pytest

from app.services.cache import LLMCache, _make_key


class TestMakeKey:
    """캐시 키 생성 테스트"""

    def test_same_inputs_same_key(self):
        """같은 입력 → 같은 키"""
        k1 = _make_key("hello", "system")
        k2 = _make_key("hello", "system")
        assert k1 == k2

    def test_different_inputs_different_key(self):
        """다른 입력 → 다른 키"""
        k1 = _make_key("hello", "system")
        k2 = _make_key("world", "system")
        assert k1 != k2

    def test_kwargs_affect_key(self):
        """kwargs가 키에 영향"""
        k1 = _make_key("hello", temperature=0.7)
        k2 = _make_key("hello", temperature=0.3)
        assert k1 != k2

    def test_none_system_prompt(self):
        """system_prompt=None과 생략은 같은 키"""
        k1 = _make_key("hello", None)
        k2 = _make_key("hello")
        assert k1 == k2

    def test_key_is_consistent_hash(self):
        """키는 일관된 해시 문자열"""
        k = _make_key("test prompt", "system", temperature=0.7)
        assert len(k) == 64  # SHA-256 hex
        assert k.isalnum()


class TestLLMCache:
    """LLMCache 동작 테스트"""

    def setup_method(self):
        self.cache = LLMCache(max_size=5, ttl=10.0)

    def test_cache_miss(self):
        """캐시 미스"""
        result = self.cache.get("nonexistent")
        assert result is None

    def test_cache_hit(self):
        """캐시 히트"""
        self.cache.set("key1", "value1")
        result = self.cache.get("key1")
        assert result == "value1"

    def test_cache_dict_value(self):
        """dict 값 캐싱"""
        data = {"answer": "test", "score": 0.9}
        self.cache.set("key1", data)
        result = self.cache.get("key1")
        assert result == data

    def test_cache_ttl_expiry(self):
        """TTL 만료"""
        cache = LLMCache(max_size=10, ttl=0.1)
        cache.set("key1", "value1")
        time.sleep(0.2)
        result = cache.get("key1")
        assert result is None

    def test_max_size_eviction(self):
        """max_size 초과 시 LRU 제거"""
        for i in range(5):
            self.cache.set(f"key{i}", f"value{i}")

        # 전부 있어야 함
        assert self.cache.get("key0") is not None

        # 6번째 추가 → key0 제거 안 됨 (위에서 get으로 접근했으므로 LRU에서 최근)
        # key1이 가장 오래된 미접근 항목
        self.cache.set("key5", "value5")
        assert self.cache.get("key1") is None  # LRU로 제거됨
        assert self.cache.get("key5") == "value5"

    def test_lru_order(self):
        """LRU 순서 확인: 최근 접근한 항목은 유지"""
        for i in range(5):
            self.cache.set(f"key{i}", f"value{i}")

        # key0을 최근 접근
        self.cache.get("key0")

        # 새 항목 추가 → key1(가장 오래된 미접근)이 제거
        self.cache.set("new", "newval")
        assert self.cache.get("key0") == "value0"  # 유지
        assert self.cache.get("key1") is None  # 제거됨

    def test_clear(self):
        """캐시 초기화"""
        self.cache.set("key1", "value1")
        self.cache.clear()
        assert self.cache.get("key1") is None

    def test_stats(self):
        """캐시 통계"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # hit
        self.cache.get("miss")  # miss

        stats = self.cache.stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_overwrite_existing_key(self):
        """기존 키 덮어쓰기"""
        self.cache.set("key1", "old")
        self.cache.set("key1", "new")
        assert self.cache.get("key1") == "new"

    def test_custom_ttl_per_entry(self):
        """엔트리별 TTL"""
        self.cache.set("short", "val", ttl=0.1)
        self.cache.set("long", "val", ttl=10.0)
        time.sleep(0.2)
        assert self.cache.get("short") is None
        assert self.cache.get("long") == "val"
