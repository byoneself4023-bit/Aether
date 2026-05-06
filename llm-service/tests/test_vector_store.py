"""벡터 DB 어댑터 테스트 (T-6).

- ChromaDBStore: chromadb.PersistentClient mock 통한 단위 테스트
- QdrantStore: in-memory mode(`:memory:`)로 실제 통합 테스트
- get_vector_store(): VECTOR_STORE 환경변수 토글 검증
- distance/score 변환: 양쪽 백엔드 응답 형식 동등성
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from app.services.vector_store import (
    ChromaDBStore,
    QdrantStore,
    VectorStore,
    _string_to_qdrant_id,
    get_vector_store,
    reset_vector_store,
)

# ============================================================
# get_vector_store() 환경변수 토글
# ============================================================


class TestGetVectorStore:
    def setup_method(self):
        reset_vector_store()

    def teardown_method(self):
        reset_vector_store()
        os.environ.pop("VECTOR_STORE", None)

    @patch("app.services.vector_store.QdrantStore.__init__", return_value=None)
    def test_default_qdrant(self, mock_init):
        # T-6b / ADR 0016: default qdrant 정착 (실 클라이언트 생성 회피)
        os.environ.pop("VECTOR_STORE", None)
        store = get_vector_store()
        assert isinstance(store, QdrantStore)

    @patch("app.services.vector_store.QdrantStore.__init__", return_value=None)
    def test_env_qdrant(self, mock_init):
        os.environ["VECTOR_STORE"] = "qdrant"
        store = get_vector_store()
        assert isinstance(store, QdrantStore)

    def test_env_chromadb_explicit(self):
        os.environ["VECTOR_STORE"] = "chromadb"
        store = get_vector_store()
        assert isinstance(store, ChromaDBStore)

    def test_unknown_falls_back_to_chromadb(self):
        os.environ["VECTOR_STORE"] = "unknown_backend"
        store = get_vector_store()
        assert isinstance(store, ChromaDBStore)

    def test_singleton_caches_instance(self):
        os.environ["VECTOR_STORE"] = "qdrant"
        s1 = get_vector_store()
        s2 = get_vector_store()
        assert s1 is s2


# ============================================================
# _string_to_qdrant_id (안정성 검증)
# ============================================================


class TestStringToQdrantId:
    def test_stable(self):
        assert _string_to_qdrant_id("doc_1") == _string_to_qdrant_id("doc_1")

    def test_different_input_different_output(self):
        assert _string_to_qdrant_id("doc_1") != _string_to_qdrant_id("doc_2")

    def test_returns_int_in_uint64_range(self):
        i = _string_to_qdrant_id("any_id")
        assert isinstance(i, int)
        assert 0 <= i < 2**64


# ============================================================
# ChromaDBStore (mock 기반)
# ============================================================


class TestChromaDBStore:
    @patch("app.services.vector_store.chromadb.PersistentClient")
    def test_init_creates_collection(self, mock_client_class):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        store = ChromaDBStore()
        store.init()

        mock_client.get_or_create_collection.assert_called_once()

    @patch("app.services.vector_store.chromadb.PersistentClient")
    def test_query_returns_normalized_format(self, mock_client_class):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["d1"]],
            "documents": [["content1"]],
            "metadatas": [[{"source": "test"}]],
            "distances": [[0.42]],
        }
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        store = ChromaDBStore()
        store.init()
        results = store.query(embedding=[0.1] * 3072, k=1)

        assert len(results) == 1
        assert results[0] == {
            "id": "d1",
            "content": "content1",
            "metadata": {"source": "test"},
            "distance": 0.42,
        }


# ============================================================
# QdrantStore (in-memory 통합 테스트)
# ============================================================


@pytest.fixture
def qdrant_store(monkeypatch):
    """QdrantStore in-memory 모드로 실제 통합 테스트."""
    from app.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("QDRANT_URL", ":memory:")
    monkeypatch.setenv("QDRANT_COLLECTION", "test_aether")
    store = QdrantStore()
    store.init(force_reload=True)
    yield store
    get_settings.cache_clear()


class TestQdrantStoreIntegration:
    def test_count_zero_after_init(self, qdrant_store):
        assert qdrant_store.count() == 0

    def test_add_and_query_roundtrip(self, qdrant_store):
        qdrant_store.add(
            ids=["doc_a", "doc_b"],
            embeddings=[[0.1] * 3072, [0.2] * 3072],
            documents=["문서 A", "문서 B"],
            metadatas=[{"source": "a"}, {"source": "b"}],
        )
        assert qdrant_store.count() == 2

        results = qdrant_store.query(embedding=[0.1] * 3072, k=2)
        assert len(results) == 2
        ids = {r["id"] for r in results}
        assert ids == {"doc_a", "doc_b"}
        for r in results:
            assert "content" in r
            assert "metadata" in r
            assert "distance" in r
            # 코사인 score → distance = 1 - score, 0~2 범위
            assert 0.0 <= r["distance"] <= 2.0

    def test_query_with_where_filter(self, qdrant_store):
        qdrant_store.add(
            ids=["doc_a", "doc_b"],
            embeddings=[[0.1] * 3072, [0.2] * 3072],
            documents=["A 내용", "B 내용"],
            metadatas=[{"source": "alpha"}, {"source": "beta"}],
        )
        results = qdrant_store.query(embedding=[0.1] * 3072, k=10, where={"source": "alpha"})
        assert len(results) == 1
        assert results[0]["id"] == "doc_a"

    def test_delete_removes_point(self, qdrant_store):
        qdrant_store.add(
            ids=["doc_a", "doc_b"],
            embeddings=[[0.1] * 3072, [0.2] * 3072],
            documents=["A", "B"],
            metadatas=[{}, {}],
        )
        qdrant_store.delete(["doc_a"])
        assert qdrant_store.count() == 1

    def test_list_all_returns_metadata(self, qdrant_store):
        qdrant_store.add(
            ids=["doc_a"],
            embeddings=[[0.1] * 3072],
            documents=["내용"],
            metadatas=[{"source": "test", "title": "제목"}],
        )
        docs = qdrant_store.list_all(limit=10)
        assert len(docs) == 1
        assert docs[0]["id"] == "doc_a"
        assert docs[0]["metadata"] == {"source": "test", "title": "제목"}


# ============================================================
# 백엔드 동등성 — VectorStore 추상 인터페이스 준수
# ============================================================


class TestInterfaceCompliance:
    def test_chromadb_implements_interface(self):
        store = ChromaDBStore()
        assert isinstance(store, VectorStore)

    def test_qdrant_implements_interface(self):
        store = QdrantStore()
        assert isinstance(store, VectorStore)
