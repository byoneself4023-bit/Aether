"""Routers 테스트 - Mock으로 API 호출 없이 테스트"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ============================================================
# Chat Router 테스트
# ============================================================

class TestChatRouter:
    @patch("app.routers.chat.is_available")
    @patch("app.routers.chat.get_optimization")
    @patch("app.routers.chat.get_risk_analysis")
    @patch("app.routers.chat.get_backtest")
    @patch("app.routers.chat.analyze_portfolio")
    def test_chat_with_tickers(
        self,
        mock_analyze,
        mock_backtest,
        mock_risk,
        mock_opt,
        mock_available,
    ):
        mock_available.return_value = True
        mock_opt.return_value = {
            "weights": {"AAPL": 0.5, "GOOGL": 0.5},
            "metrics": {
                "expected_return": 0.15,
                "volatility": 0.18,
                "sharpe_ratio": 0.83,
            },
        }
        mock_risk.return_value = {
            "risk_summary": {"var_95_montecarlo": 0.02},
        }
        mock_backtest.return_value = {
            "metrics": {"total_return": 0.5},
        }
        mock_analyze.return_value = {
            "summary": "포트폴리오 분석 완료",
            "composition": {"description": "AAPL과 GOOGL로 구성"},
        }

        response = client.post(
            "/api/chat",
            json={
                "message": "AAPL, GOOGL 분석해줘",
                "tickers": ["AAPL", "GOOGL"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "portfolio_data" in data

    @patch("app.routers.chat.query_with_llm")
    def test_chat_without_tickers_uses_rag(self, mock_rag):
        mock_rag.return_value = {
            "answer": "샤프 비율은 위험조정수익률입니다.",
            "sources": [
                {"title": "샤프 비율", "source": "portfolio_theory", "relevance": 0.9}
            ],
        }

        response = client.post(
            "/api/chat",
            json={"message": "샤프 비율이 뭐야?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        mock_rag.assert_called_once()

    @patch("app.routers.chat.is_available")
    def test_chat_service_unavailable(self, mock_available):
        mock_available.return_value = False

        response = client.post(
            "/api/chat",
            json={
                "message": "AAPL, GOOGL 분석해줘",
                "tickers": ["AAPL", "GOOGL"],
            },
        )

        assert response.status_code == 503

    @patch("app.routers.chat.is_available")
    @patch("app.routers.chat.get_full_analysis")
    @patch("app.routers.chat.analyze_portfolio")
    @patch("app.routers.chat.explain_risk")
    @patch("app.routers.chat.summarize_backtest")
    @patch("app.routers.chat.get_recommendation")
    def test_analyze_endpoint(
        self,
        mock_recommend,
        mock_bt_summary,
        mock_risk_explain,
        mock_analyze,
        mock_full,
        mock_available,
    ):
        mock_available.return_value = True
        mock_full.return_value = {
            "optimization": {
                "weights": {"AAPL": 0.5, "GOOGL": 0.5},
                "metrics": {
                    "expected_return": 0.15,
                    "volatility": 0.18,
                    "sharpe_ratio": 0.83,
                },
            },
            "risk": {
                "risk_summary": {
                    "var_95_montecarlo": 0.02,
                    "cvar_99": 0.03,
                },
            },
            "backtest": {
                "metrics": {
                    "total_return": 0.5,
                    "annual_return": 0.2,
                    "sharpe_ratio": 1.5,
                    "max_drawdown": 0.1,
                },
                "final_weights": {"AAPL": 0.5, "GOOGL": 0.5},
            },
            "summary": {},
        }
        mock_analyze.return_value = {"summary": "분석 완료"}
        mock_risk_explain.return_value = {"summary": "리스크 설명"}
        mock_bt_summary.return_value = {"summary": "백테스트 요약"}
        mock_recommend.return_value = {"summary": "추천"}

        response = client.post(
            "/api/chat/analyze",
            json={
                "tickers": ["AAPL", "GOOGL"],
                "strategy": "max_sharpe",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "portfolio_analysis" in data
        assert "risk_analysis" in data
        assert "backtest_analysis" in data
        assert "portfolio_data" in data

    @patch("app.routers.chat.is_available")
    def test_chat_health(self, mock_available):
        mock_available.return_value = True

        response = client.get("/api/chat/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["portfolio_service"] == "connected"


# ============================================================
# RAG Router 테스트
# ============================================================

class TestRAGRouter:
    @patch("app.routers.rag.query_with_llm")
    def test_rag_query(self, mock_query):
        mock_query.return_value = {
            "answer": "VaR는 Value at Risk의 약자입니다.",
            "sources": [
                {"title": "VaR 설명", "source": "risk_management", "relevance": 0.85}
            ],
        }

        response = client.post(
            "/api/rag/query",
            json={"question": "VaR가 뭐야?", "k": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert data["confidence"] == 0.85

    @patch("app.routers.rag.query")
    def test_rag_search(self, mock_query):
        mock_query.return_value = [
            {
                "id": "doc_1",
                "content": "샤프 비율은...",
                "metadata": {"title": "샤프 비율", "source": "portfolio_theory"},
                "distance": 0.1,
            }
        ]

        response = client.post(
            "/api/rag/search",
            json={"question": "샤프 비율", "k": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["relevance"] == 0.9  # 1 - 0.1

    @patch("app.routers.rag.init_vectorstore")
    @patch("app.routers.rag.get_vectorstore_status")
    def test_rag_init(self, mock_status, mock_init):
        mock_init.return_value = True
        mock_status.return_value = {
            "initialized": True,
            "document_count": 50,
        }

        response = client.post(
            "/api/rag/init",
            json={"force_reload": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["document_count"] == 50

    @patch("app.routers.rag.get_vectorstore_status")
    @patch("app.routers.rag.list_documents")
    def test_rag_status(self, mock_list, mock_status):
        mock_status.return_value = {
            "initialized": True,
            "document_count": 50,
            "persist_dir": "./data/chroma",
        }
        mock_list.return_value = [
            {"metadata": {"source": "portfolio_theory"}},
            {"metadata": {"source": "risk_management"}},
        ]

        response = client.get("/api/rag/status")

        assert response.status_code == 200
        data = response.json()
        assert data["initialized"] is True
        assert data["document_count"] == 50
        assert "available_sources" in data

    def test_rag_sources(self):
        response = client.get("/api/rag/sources")

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "portfolio_theory" in data["sources"]
        assert "risk_management" in data["sources"]


# ============================================================
# 기본 엔드포인트 테스트
# ============================================================

class TestBasicEndpoints:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert "checks" in data
        assert "timestamp" in data

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "endpoints" in data
        assert "chat" in data["endpoints"]
        assert "rag" in data["endpoints"]


# ============================================================
# 유틸리티 함수 테스트
# ============================================================

class TestUtilityFunctions:
    def test_extract_tickers(self):
        from app.routers.chat import extract_tickers

        # 기본 케이스
        assert extract_tickers("AAPL, GOOGL 분석해줘") == ["AAPL", "GOOGL"]

        # 대소문자 혼합
        assert extract_tickers("aapl, googl, NVDA") == ["AAPL", "GOOGL", "NVDA"]

        # 중복 제거
        assert extract_tickers("AAPL AAPL GOOGL") == ["AAPL", "GOOGL"]

        # 일반 단어 제외
        assert extract_tickers("I want to analyze AAPL") == ["AAPL"]

        # 티커 없음
        assert extract_tickers("포트폴리오 분석해줘") == []

    def test_detect_intent(self):
        from app.routers.chat import detect_intent

        assert detect_intent("포트폴리오 분석해줘") == "analyze"
        assert detect_intent("VaR 리스크 알려줘") == "risk"
        assert detect_intent("백테스트 결과 보여줘") == "backtest"
        assert detect_intent("샤프 비율이 뭐야?") == "question"
        assert detect_intent("안녕하세요") == "unknown"


# ============================================================
# 에러 핸들링 테스트
# ============================================================

class TestErrorHandling:
    def test_chat_invalid_request(self):
        response = client.post(
            "/api/chat",
            json={"message": ""},  # 빈 메시지
        )
        assert response.status_code == 422

    def test_analyze_invalid_tickers(self):
        response = client.post(
            "/api/chat/analyze",
            json={
                "tickers": ["AAPL"],  # 최소 2개 필요
                "strategy": "max_sharpe",
            },
        )
        assert response.status_code == 422

    def test_rag_query_invalid_k(self):
        response = client.post(
            "/api/rag/query",
            json={"question": "테스트", "k": 100},  # 최대 10
        )
        assert response.status_code == 422
