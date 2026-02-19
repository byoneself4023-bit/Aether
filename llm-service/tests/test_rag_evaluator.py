"""Major #9: RAG Retrieval 품질 평가 테스트"""

import pytest
from app.services.rag_evaluator import (
    EvalQuery,
    EvalResult,
    EvalSummary,
    evaluate_single_query,
    evaluate_retrieval,
)


def make_mock_query_fn(results: list[dict]):
    """mock query 함수 생성"""
    def query_fn(query: str, k: int) -> list[dict]:
        return results[:k]
    return query_fn


class TestEvaluateSingleQuery:
    """단일 쿼리 평가 테스트"""

    def test_perfect_match(self):
        """완벽한 매칭"""
        eq = EvalQuery(
            query="샤프 비율이란?",
            expected_sources=["portfolio_theory"],
            expected_keywords=["샤프", "수익률"],
        )
        results = [
            {"content": "샤프 비율은 수익률을 변동성으로 나눈 값", "metadata": {"source": "portfolio_theory"}},
            {"content": "투자 수익률 분석", "metadata": {"source": "portfolio_theory"}},
            {"content": "다른 내용", "metadata": {"source": "risk_management"}},
        ]
        query_fn = make_mock_query_fn(results)

        result = evaluate_single_query(eq, query_fn, k=3)

        assert result.precision_at_k > 0
        assert result.keyword_coverage == 1.0
        assert "portfolio_theory" in result.matched_sources
        assert "샤프" in result.matched_keywords
        assert "수익률" in result.matched_keywords

    def test_no_match(self):
        """매칭 없음"""
        eq = EvalQuery(
            query="VaR란?",
            expected_sources=["risk_management"],
            expected_keywords=["VaR", "손실"],
        )
        results = [
            {"content": "완전히 무관한 내용", "metadata": {"source": "unrelated"}},
        ]
        query_fn = make_mock_query_fn(results)

        result = evaluate_single_query(eq, query_fn, k=3)

        assert result.precision_at_k == 0.0
        assert result.keyword_coverage == 0.0
        assert result.matched_sources == []

    def test_partial_keyword_coverage(self):
        """부분 키워드 매칭"""
        eq = EvalQuery(
            query="효율적 프론티어",
            expected_sources=["portfolio_theory"],
            expected_keywords=["효율적", "프론티어", "최적화"],
        )
        results = [
            {"content": "효율적 프론티어 설명", "metadata": {"source": "portfolio_theory"}},
        ]
        query_fn = make_mock_query_fn(results)

        result = evaluate_single_query(eq, query_fn, k=3)

        # "효율적", "프론티어" 매칭, "최적화"는 없음
        assert result.keyword_coverage == pytest.approx(2 / 3, abs=0.01)

    def test_source_accuracy(self):
        """소스 매칭 정확도"""
        eq = EvalQuery(
            query="test",
            expected_sources=["source_a", "source_b"],
            expected_keywords=[],
        )
        results = [
            {"content": "내용", "metadata": {"source": "source_a"}},
            {"content": "내용", "metadata": {"source": "source_c"}},
            {"content": "내용", "metadata": {"source": "source_b"}},
        ]
        query_fn = make_mock_query_fn(results)

        result = evaluate_single_query(eq, query_fn, k=3)

        assert len(result.matched_sources) == 2


class TestEvaluateRetrieval:
    """전체 평가 함수 테스트"""

    def test_evaluate_with_dataset(self):
        """평가 데이터셋으로 평가"""
        dataset = [
            EvalQuery("q1", ["src_a"], ["k1", "k2"]),
            EvalQuery("q2", ["src_b"], ["k3"]),
        ]
        results = [
            {"content": "k1 k2 content", "metadata": {"source": "src_a"}},
            {"content": "other", "metadata": {"source": "src_a"}},
        ]
        query_fn = make_mock_query_fn(results)

        summary = evaluate_retrieval(query_fn, dataset=dataset, k=2)

        assert summary.total_queries == 2
        assert summary.avg_precision_at_k >= 0
        assert summary.avg_keyword_coverage >= 0
        assert summary.source_accuracy >= 0
        assert len(summary.results) == 2

    def test_empty_dataset(self):
        """빈 데이터셋 처리"""
        query_fn = make_mock_query_fn([])

        summary = evaluate_retrieval(query_fn, dataset=[], k=3)

        assert summary.total_queries == 0
        assert summary.avg_precision_at_k == 0.0
        assert summary.avg_keyword_coverage == 0.0
        assert summary.source_accuracy == 0.0

    def test_empty_results(self):
        """검색 결과 없음"""
        dataset = [
            EvalQuery("q1", ["src"], ["keyword"]),
        ]
        query_fn = make_mock_query_fn([])

        summary = evaluate_retrieval(query_fn, dataset=dataset, k=3)

        assert summary.total_queries == 1
        assert summary.avg_precision_at_k == 0.0
        assert summary.avg_keyword_coverage == 0.0

    def test_source_accuracy_calculation(self):
        """소스 매칭 정확도 계산"""
        dataset = [
            EvalQuery("q1", ["src_a"], ["k1"]),
            EvalQuery("q2", ["src_b"], ["k2"]),
            EvalQuery("q3", ["src_a"], ["k3"]),
        ]

        # q1은 매칭, q2는 불매칭, q3는 매칭
        call_count = [0]
        def query_fn(query, k):
            call_count[0] += 1
            if call_count[0] in (1, 3):
                return [{"content": "k1 k3", "metadata": {"source": "src_a"}}]
            return [{"content": "other", "metadata": {"source": "unrelated"}}]

        summary = evaluate_retrieval(query_fn, dataset=dataset, k=1)

        # 2/3 매칭
        assert summary.source_accuracy == pytest.approx(2 / 3, abs=0.01)

    def test_keyword_coverage_calculation(self):
        """키워드 커버리지 계산"""
        dataset = [
            EvalQuery("q1", ["src"], ["alpha", "beta", "gamma", "delta"]),
        ]
        results = [
            {"content": "alpha and beta are here", "metadata": {"source": "src"}},
        ]
        query_fn = make_mock_query_fn(results)

        summary = evaluate_retrieval(query_fn, dataset=dataset, k=3)

        # 2/4 키워드 매칭 (alpha, beta)
        assert summary.avg_keyword_coverage == 0.5

    def test_query_fn_exception_handled(self):
        """query 함수 예외 처리"""
        dataset = [
            EvalQuery("q1", ["src"], ["keyword"]),
        ]

        def failing_query_fn(query, k):
            raise RuntimeError("search failed")

        summary = evaluate_retrieval(failing_query_fn, dataset=dataset, k=3)

        assert summary.total_queries == 1
        assert summary.avg_precision_at_k == 0.0
