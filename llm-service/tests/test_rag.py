"""RAG 파이프라인 테스트 - Mock으로 API 호출 없이 테스트"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from app.services.rag import (
    _split_document,
    _load_knowledge_base,
    init_vectorstore,
    get_vectorstore_status,
    query,
    query_with_llm,
    add_document,
    delete_document,
    list_documents,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_markdown():
    return """# 테스트 문서

## 첫 번째 섹션
이것은 첫 번째 섹션의 내용입니다.
여러 줄로 구성되어 있습니다.
충분한 길이의 텍스트가 있어야 합니다.

## 두 번째 섹션
이것은 두 번째 섹션의 내용입니다.
VaR와 CVaR에 대한 설명이 포함됩니다.
리스크 관리에 대한 중요한 정보입니다.

## 세 번째 섹션
포트폴리오 최적화에 대한 내용입니다.
샤프 비율과 효율적 프론티어를 설명합니다.
"""


@pytest.fixture
def mock_embedding():
    """768차원 더미 임베딩"""
    return [0.1] * 768


@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB Collection — Init 테스트가 PersistentClient mock 통해 사용."""
    collection = MagicMock()
    collection.count.return_value = 10
    collection.query.return_value = {
        "ids": [["doc_1", "doc_2"]],
        "documents": [["문서 1 내용", "문서 2 내용"]],
        "metadatas": [[
            {"source": "portfolio_theory", "title": "효율적 프론티어"},
            {"source": "risk_management", "title": "VaR 설명"},
        ]],
        "distances": [[0.1, 0.2]],
    }
    collection.get.return_value = {
        "ids": ["doc_1", "doc_2"],
        "metadatas": [
            {"source": "portfolio_theory"},
            {"source": "risk_management"},
        ],
    }
    return collection


@pytest.fixture
def mock_store():
    """Mock 벡터 DB 어댑터 — query/add/delete/list_all 등 어댑터 호출 검증용."""
    store = MagicMock()
    store.count.return_value = 10
    store.query.return_value = [
        {
            "id": "doc_1",
            "content": "문서 1 내용",
            "metadata": {"source": "portfolio_theory", "title": "효율적 프론티어"},
            "distance": 0.1,
        },
        {
            "id": "doc_2",
            "content": "문서 2 내용",
            "metadata": {"source": "risk_management", "title": "VaR 설명"},
            "distance": 0.2,
        },
    ]
    store.list_all.return_value = [
        {"id": "doc_1", "metadata": {"source": "portfolio_theory"}},
        {"id": "doc_2", "metadata": {"source": "risk_management"}},
    ]
    return store


# ============================================================
# _split_document 테스트
# ============================================================

class TestSplitDocument:
    def test_split_by_h2(self, sample_markdown):
        sections = _split_document(sample_markdown, "test_doc")

        assert len(sections) == 3
        assert sections[0]["id"] == "test_doc_0"
        assert "첫 번째 섹션" in sections[0]["metadata"]["title"]
        assert sections[1]["id"] == "test_doc_1"
        assert "두 번째 섹션" in sections[1]["metadata"]["title"]

    def test_section_content(self, sample_markdown):
        sections = _split_document(sample_markdown, "test_doc")

        assert "여러 줄로 구성" in sections[0]["content"]
        assert "VaR와 CVaR" in sections[1]["content"]

    def test_metadata(self, sample_markdown):
        sections = _split_document(sample_markdown, "test_doc")

        assert sections[0]["metadata"]["source"] == "test_doc"
        assert sections[0]["metadata"]["section_idx"] == 0

    def test_empty_document(self):
        sections = _split_document("", "empty")
        assert len(sections) == 0

    def test_short_sections_filtered(self):
        short_doc = """## 짧은
짧음

## 충분히 긴 섹션
이 섹션은 충분히 긴 내용을 가지고 있어서 필터링되지 않습니다.
최소 50자 이상의 텍스트가 필요합니다.
"""
        sections = _split_document(short_doc, "short_test")
        assert len(sections) == 1  # 짧은 섹션은 필터링됨


# ============================================================
# _load_knowledge_base 테스트
# ============================================================

class TestLoadKnowledgeBase:
    def test_load_existing_files(self):
        """실제 knowledge_base 파일 로드 테스트"""
        documents = _load_knowledge_base()

        # 4개의 md 파일에서 여러 섹션이 로드되어야 함
        assert len(documents) > 0

        # 문서 구조 확인
        for doc in documents:
            assert "id" in doc
            assert "content" in doc
            assert "metadata" in doc
            assert "source" in doc["metadata"]

    def test_document_sources(self):
        """모든 소스 파일이 로드되었는지 확인"""
        documents = _load_knowledge_base()

        sources = set(doc["metadata"]["source"] for doc in documents)
        expected_sources = {
            "portfolio_theory",
            "risk_management",
            "sector_analysis",
            "investment_strategies",
        }

        assert expected_sources.issubset(sources)


# ============================================================
# init_vectorstore 테스트
# ============================================================

class TestInitVectorstore:
    @patch("app.services.rag._get_embedding")
    @patch("app.services.vector_store.chromadb.PersistentClient")
    @patch("app.services.rag.settings")
    def test_init_vectorstore_success(
        self,
        mock_settings,
        mock_client_class,
        mock_get_embedding,
        mock_embedding,
    ):
        # Setup
        mock_settings.google_api_key = "test-key"
        mock_settings.chroma_persist_dir = "/tmp/test_chroma"
        mock_settings.embedding_model = "models/embedding-001"
        mock_settings.rag_chunk_size = 1000
        mock_settings.rag_chunk_overlap = 200

        mock_collection = MagicMock()
        mock_collection.count.return_value = 0

        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        mock_get_embedding.return_value = mock_embedding

        # Reset global state
        import app.services.rag as rag_module
        from app.services.vector_store import reset_vector_store

        rag_module._initialized = False
        reset_vector_store()

        # Execute
        result = init_vectorstore()

        # Assert
        assert result is True
        mock_client.get_or_create_collection.assert_called_once()

    @patch("app.services.vector_store.chromadb.PersistentClient")
    @patch("app.services.rag.settings")
    def test_init_without_api_key(self, mock_settings, mock_client_class):
        """API 키 없이 초기화 (임베딩 스킵)"""
        mock_settings.google_api_key = ""
        mock_settings.chroma_persist_dir = "/tmp/test_chroma"
        mock_settings.rag_chunk_size = 1000
        mock_settings.rag_chunk_overlap = 200

        mock_collection = MagicMock()
        mock_collection.count.return_value = 0

        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_client_class.return_value = mock_client

        # Reset global state
        import app.services.rag as rag_module
        from app.services.vector_store import reset_vector_store

        rag_module._initialized = False
        reset_vector_store()

        result = init_vectorstore()

        assert result is True


# ============================================================
# query 테스트
# ============================================================

class TestQuery:
    @patch("app.services.rag._get_query_embedding")
    @patch("app.services.rag.get_vector_store")
    @patch("app.services.rag._initialized", True)
    def test_query_success(
        self,
        mock_get_store,
        mock_get_query_embedding,
        mock_embedding,
        mock_store,
    ):
        # Setup
        mock_get_store.return_value = mock_store
        mock_get_query_embedding.return_value = mock_embedding

        # Execute
        results = query("샤프 비율이란?", k=2)

        # Assert
        assert len(results) == 2
        assert results[0]["id"] == "doc_1"
        assert results[0]["content"] == "문서 1 내용"
        assert "distance" in results[0]
        mock_store.query.assert_called_once()

    @patch("app.services.rag._get_query_embedding")
    @patch("app.services.rag.get_vector_store")
    @patch("app.services.rag._initialized", True)
    def test_query_with_filter(
        self,
        mock_get_store,
        mock_get_query_embedding,
        mock_embedding,
        mock_store,
    ):
        mock_get_store.return_value = mock_store
        mock_get_query_embedding.return_value = mock_embedding

        query("VaR란?", k=3, filter_source="risk_management")

        # 필터가 어댑터에 전달되었는지 확인
        call_args = mock_store.query.call_args
        assert call_args.kwargs["where"] == {"source": "risk_management"}

    @patch("app.services.rag.get_vector_store")
    @patch("app.services.rag._initialized", True)
    def test_query_empty_results(self, mock_get_store, mock_store):
        # 빈 결과 반환
        mock_store.query.return_value = []
        mock_get_store.return_value = mock_store

        with patch("app.services.rag._get_query_embedding", return_value=[0.1] * 768):
            results = query("존재하지 않는 주제")

        assert len(results) == 0


# ============================================================
# query_with_llm 테스트
# ============================================================

class TestQueryWithLLM:
    @patch("app.services.rag.call_llm")
    @patch("app.services.rag.query")
    def test_query_with_llm_success(self, mock_query, mock_call_llm):
        # Setup
        mock_query.return_value = [
            {
                "id": "doc_1",
                "content": "샤프 비율은 위험조정수익률입니다.",
                "metadata": {"title": "샤프 비율", "source": "portfolio_theory"},
                "distance": 0.1,
            }
        ]
        mock_call_llm.return_value = "샤프 비율은 수익률을 변동성으로 나눈 지표입니다."

        # Execute
        result = query_with_llm("샤프 비율이란?")

        # Assert
        assert "answer" in result
        assert "sources" in result
        assert len(result["sources"]) == 1
        assert result["sources"][0]["title"] == "샤프 비율"
        mock_call_llm.assert_called_once()

    @patch("app.services.rag.query")
    def test_query_with_llm_no_results(self, mock_query):
        mock_query.return_value = []

        result = query_with_llm("존재하지 않는 주제")

        assert "관련 정보를 찾을 수 없습니다" in result["answer"]
        assert result["sources"] == []

    @patch("app.services.rag.call_llm")
    @patch("app.services.rag.query")
    def test_query_with_llm_without_sources(self, mock_query, mock_call_llm):
        mock_query.return_value = [
            {
                "id": "doc_1",
                "content": "내용",
                "metadata": {"title": "제목", "source": "소스"},
                "distance": 0.1,
            }
        ]
        mock_call_llm.return_value = "답변"

        result = query_with_llm("질문", include_sources=False)

        assert "sources" not in result
        assert "answer" in result


# ============================================================
# 문서 관리 함수 테스트
# ============================================================

class TestDocumentManagement:
    @patch("app.services.rag._get_embedding")
    @patch("app.services.rag.get_vector_store")
    @patch("app.services.rag._initialized", True)
    def test_add_document(
        self, mock_get_store, mock_get_embedding, mock_embedding, mock_store
    ):
        mock_get_store.return_value = mock_store
        mock_get_embedding.return_value = mock_embedding

        result = add_document(
            doc_id="new_doc",
            content="새로운 문서 내용",
            metadata={"source": "custom"},
        )

        assert result is True
        mock_store.add.assert_called_once()

    @patch("app.services.rag.get_vector_store")
    @patch("app.services.rag._initialized", True)
    def test_delete_document(self, mock_get_store, mock_store):
        mock_get_store.return_value = mock_store

        result = delete_document("doc_to_delete")

        assert result is True
        mock_store.delete.assert_called_once_with(["doc_to_delete"])

    @patch("app.services.rag.get_vector_store")
    @patch("app.services.rag._initialized", True)
    def test_list_documents(self, mock_get_store, mock_store):
        mock_get_store.return_value = mock_store

        docs = list_documents(limit=10)

        assert len(docs) == 2
        assert docs[0]["id"] == "doc_1"
        mock_store.list_all.assert_called_once_with(limit=10)


# ============================================================
# get_vectorstore_status 테스트
# ============================================================

class TestVectorstoreStatus:
    @patch("app.services.rag._initialized", False)
    def test_status_not_initialized(self):
        status = get_vectorstore_status()

        assert status["initialized"] is False
        assert status["document_count"] == 0

    @patch("app.services.rag.get_vector_store")
    @patch("app.services.rag._initialized", True)
    def test_status_initialized(self, mock_get_store, mock_store):
        mock_get_store.return_value = mock_store

        status = get_vectorstore_status()

        assert status["initialized"] is True
        assert status["document_count"] == 10


# ============================================================
# Integration-like 테스트 (실제 파일 사용)
# ============================================================

class TestKnowledgeBaseContent:
    def test_portfolio_theory_content(self):
        """portfolio_theory.md 내용 검증"""
        documents = _load_knowledge_base()

        portfolio_docs = [
            d for d in documents
            if d["metadata"]["source"] == "portfolio_theory"
        ]

        assert len(portfolio_docs) > 0

        # 핵심 용어 포함 확인
        all_content = " ".join(d["content"] for d in portfolio_docs)
        assert "효율적 프론티어" in all_content or "Efficient Frontier" in all_content
        assert "샤프" in all_content or "Sharpe" in all_content

    def test_risk_management_content(self):
        """risk_management.md 내용 검증"""
        documents = _load_knowledge_base()

        risk_docs = [
            d for d in documents
            if d["metadata"]["source"] == "risk_management"
        ]

        assert len(risk_docs) > 0

        all_content = " ".join(d["content"] for d in risk_docs)
        assert "VaR" in all_content
        assert "CVaR" in all_content or "Expected Shortfall" in all_content

    def test_sector_analysis_content(self):
        """sector_analysis.md 내용 검증"""
        documents = _load_knowledge_base()

        sector_docs = [
            d for d in documents
            if d["metadata"]["source"] == "sector_analysis"
        ]

        assert len(sector_docs) > 0

        all_content = " ".join(d["content"] for d in sector_docs)
        assert "섹터" in all_content or "Sector" in all_content

    def test_investment_strategies_content(self):
        """investment_strategies.md 내용 검증"""
        documents = _load_knowledge_base()

        strategy_docs = [
            d for d in documents
            if d["metadata"]["source"] == "investment_strategies"
        ]

        assert len(strategy_docs) > 0

        all_content = " ".join(d["content"] for d in strategy_docs)
        assert "MVP" in all_content or "최소 분산" in all_content
        assert "리밸런싱" in all_content or "Rebalancing" in all_content
