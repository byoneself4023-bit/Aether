"""Minor #13: Context Window 최적화 테스트"""

import pytest

from app.services.rag import (
    extract_relevant_paragraphs,
    build_optimized_context,
)


class TestExtractRelevantParagraphs:
    """쿼리 관련 문단 추출 테스트"""

    def test_extracts_relevant_paragraphs(self):
        """관련 문단을 우선 추출"""
        text = (
            "첫 문단: 날씨가 좋습니다.\n\n"
            "둘째 문단: 샤프 비율은 수익률을 변동성으로 나눈 지표입니다.\n\n"
            "셋째 문단: 오늘 점심은 맛있었습니다."
        )
        result = extract_relevant_paragraphs(text, ["샤프", "비율", "수익률"], max_chars=1000)
        # 샤프/비율/수익률이 포함된 둘째 문단이 가장 먼저
        assert "샤프 비율" in result

    def test_respects_max_chars(self):
        """max_chars 제한 준수"""
        paragraphs = [f"문단{i}: " + "내용 " * 50 for i in range(10)]
        text = "\n\n".join(paragraphs)

        result = extract_relevant_paragraphs(text, ["문단0"], max_chars=200)
        assert len(result) <= 300  # 약간의 여유

    def test_empty_query_words(self):
        """빈 쿼리 단어"""
        text = "일부 텍스트입니다."
        result = extract_relevant_paragraphs(text, [], max_chars=100)
        assert result == text

    def test_empty_text(self):
        """빈 텍스트"""
        result = extract_relevant_paragraphs("", ["쿼리"], max_chars=100)
        assert result == ""

    def test_single_paragraph(self):
        """단일 문단"""
        text = "샤프 비율은 중요한 투자 지표입니다."
        result = extract_relevant_paragraphs(text, ["샤프"], max_chars=1000)
        assert "샤프" in result

    def test_multiple_relevant_paragraphs(self):
        """여러 관련 문단"""
        text = (
            "VaR는 Value at Risk입니다.\n\n"
            "CVaR는 Conditional VaR입니다.\n\n"
            "날씨가 좋습니다.\n\n"
            "VaR는 리스크 측정에 사용됩니다."
        )
        result = extract_relevant_paragraphs(text, ["VaR", "리스크"], max_chars=2000)
        # VaR 관련 문단이 먼저 포함
        assert "VaR" in result


class TestBuildOptimizedContext:
    """최적화된 컨텍스트 빌드 테스트"""

    def test_builds_context_within_limit(self):
        """max_context_chars 이내로 빌드"""
        documents = [
            {
                "content": "내용 " * 100,
                "metadata": {"title": "문서1", "source": "src1"},
                "distance": 0.1,
            },
            {
                "content": "내용 " * 100,
                "metadata": {"title": "문서2", "source": "src2"},
                "distance": 0.2,
            },
        ]
        context, sources = build_optimized_context(documents, "쿼리", max_context_chars=3000)

        assert len(context) <= 3100  # 헤더/구분자 포함 약간의 여유
        assert len(sources) == 2

    def test_returns_sources(self):
        """소스 정보 반환"""
        documents = [
            {
                "content": "샤프 비율 설명",
                "metadata": {"title": "샤프 비율", "source": "portfolio_theory"},
                "distance": 0.1,
            },
        ]
        context, sources = build_optimized_context(documents, "샤프", max_context_chars=3000)

        assert len(sources) == 1
        assert sources[0]["title"] == "샤프 비율"
        assert sources[0]["source"] == "portfolio_theory"
        assert sources[0]["relevance"] == pytest.approx(0.9, abs=0.01)

    def test_empty_documents(self):
        """빈 문서 리스트"""
        context, sources = build_optimized_context([], "쿼리", max_context_chars=3000)
        assert context == ""
        assert sources == []

    def test_short_documents_not_truncated(self):
        """짧은 문서는 잘리지 않음"""
        documents = [
            {
                "content": "짧은 내용",
                "metadata": {"title": "제목", "source": "src"},
                "distance": 0.1,
            },
        ]
        context, sources = build_optimized_context(documents, "쿼리", max_context_chars=3000)
        assert "짧은 내용" in context

    def test_long_document_truncated(self):
        """긴 문서는 관련 문단만 추출"""
        long_content = (
            "관련 없는 문단입니다. " * 50 + "\n\n"
            "VaR는 Value at Risk로 리스크를 측정합니다. " * 10 + "\n\n"
            "또 다른 관련 없는 문단. " * 50
        )
        documents = [
            {
                "content": long_content,
                "metadata": {"title": "리스크", "source": "risk"},
                "distance": 0.1,
            },
        ]
        context, sources = build_optimized_context(documents, "VaR 리스크", max_context_chars=500)

        # 전체 보다 훨씬 짧아야 함
        assert len(context) < len(long_content)
        # VaR 관련 내용은 포함
        assert "VaR" in context

    def test_multiple_documents_budget_allocation(self):
        """여러 문서에 균등하게 예산 분배"""
        documents = [
            {
                "content": "문서A 내용 " * 50,
                "metadata": {"title": "A", "source": "src"},
                "distance": 0.1,
            },
            {
                "content": "문서B 내용 " * 50,
                "metadata": {"title": "B", "source": "src"},
                "distance": 0.2,
            },
        ]
        context, sources = build_optimized_context(documents, "내용", max_context_chars=3000)

        assert len(sources) == 2
        # 두 문서 모두 포함
        assert "### A" in context
        assert "### B" in context
