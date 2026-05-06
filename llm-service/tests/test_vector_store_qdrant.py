"""T-6b Qdrant 어댑터 단위 테스트 (in-memory) — ADR 0016."""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture
def qdrant_store():
    """In-memory Qdrant 인스턴스 (test isolation)."""
    from app.services.vector_store import QdrantStore, reset_vector_store

    reset_vector_store()
    store = QdrantStore()
    with patch("app.services.vector_store.get_settings") as mock_settings:
        mock_settings.return_value.qdrant_url = ":memory:"
        mock_settings.return_value.qdrant_collection = "test_collection"
        store.init(force_reload=True)
    yield store
    reset_vector_store()


@pytest.fixture
def sample_data():
    return {
        "ids": ["doc1", "doc2", "doc3"],
        "embeddings": [[0.1] * 3072, [0.2] * 3072, [0.3] * 3072],
        "documents": ["샤프 비율 정의", "VaR 정의", "효율적 프론티어"],
        "metadatas": [
            {"source": "portfolio_theory", "title": "샤프 비율"},
            {"source": "risk_management", "title": "VaR"},
            {"source": "portfolio_theory", "title": "효율적 프론티어"},
        ],
    }


class TestQdrantStore:
    def test_init_creates_collection(self, qdrant_store):
        assert qdrant_store._client is not None
        assert qdrant_store._collection_name == "test_collection"
        assert qdrant_store.count() == 0

    def test_add_and_count(self, qdrant_store, sample_data):
        qdrant_store.add(**sample_data)
        assert qdrant_store.count() == 3

    def test_query_returns_distance_inverted_score(self, qdrant_store, sample_data):
        qdrant_store.add(**sample_data)
        results = qdrant_store.query(embedding=[0.1] * 3072, k=2)
        assert len(results) == 2
        for doc in results:
            assert "id" in doc
            assert "content" in doc
            assert "metadata" in doc
            assert "distance" in doc
            assert 0.0 <= doc["distance"] <= 1.0

    def test_query_with_where_filter(self, qdrant_store, sample_data):
        qdrant_store.add(**sample_data)
        results = qdrant_store.query(
            embedding=[0.1] * 3072,
            k=10,
            where={"source": "portfolio_theory"},
        )
        assert all(d["metadata"].get("source") == "portfolio_theory" for d in results)
        assert len(results) == 2

    def test_delete(self, qdrant_store, sample_data):
        qdrant_store.add(**sample_data)
        qdrant_store.delete(["doc1"])
        assert qdrant_store.count() == 2

    def test_list_all(self, qdrant_store, sample_data):
        qdrant_store.add(**sample_data)
        all_docs = qdrant_store.list_all(limit=10)
        assert len(all_docs) == 3
        ids = {d["id"] for d in all_docs}
        assert ids == {"doc1", "doc2", "doc3"}


class TestStringToQdrantId:
    def test_stable_across_calls(self):
        from app.services.vector_store import _string_to_qdrant_id

        assert _string_to_qdrant_id("portfolio_theory_3") == _string_to_qdrant_id("portfolio_theory_3")

    def test_different_inputs_yield_different_ids(self):
        from app.services.vector_store import _string_to_qdrant_id

        assert _string_to_qdrant_id("doc_a") != _string_to_qdrant_id("doc_b")

    def test_returns_unsigned_int(self):
        from app.services.vector_store import _string_to_qdrant_id

        result = _string_to_qdrant_id("any_id")
        assert isinstance(result, int)
        assert result >= 0
        assert result < 2**64


class TestGetVectorStoreBackendToggle:
    def test_default_qdrant_when_no_env(self, monkeypatch):
        from app.services import vector_store as vs_mod

        monkeypatch.delenv("VECTOR_STORE", raising=False)
        vs_mod.reset_vector_store()
        with patch.object(vs_mod.QdrantStore, "__init__", return_value=None) as mock_init:
            with patch("app.services.vector_store.get_settings") as mock_settings:
                mock_settings.return_value.vector_store = "qdrant"
                vs_mod.get_vector_store()
        mock_init.assert_called_once()
        vs_mod.reset_vector_store()

    def test_env_chromadb_overrides_default(self, monkeypatch):
        from app.services import vector_store as vs_mod

        monkeypatch.setenv("VECTOR_STORE", "chromadb")
        vs_mod.reset_vector_store()
        with patch.object(vs_mod.ChromaDBStore, "__init__", return_value=None) as mock_init:
            with patch("app.services.vector_store.get_settings") as mock_settings:
                mock_settings.return_value.vector_store = "qdrant"
                vs_mod.get_vector_store()
        mock_init.assert_called_once()
        vs_mod.reset_vector_store()
