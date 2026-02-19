"""RAG Retrieval 품질 평가"""

import logging
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class EvalQuery:
    """평가 쿼리"""
    query: str
    expected_sources: list[str]
    expected_keywords: list[str]


@dataclass
class EvalResult:
    """단일 쿼리 평가 결과"""
    query: str
    precision_at_k: float
    keyword_coverage: float
    retrieved_sources: list[str]
    matched_sources: list[str]
    matched_keywords: list[str]


@dataclass
class EvalSummary:
    """전체 평가 요약"""
    total_queries: int
    avg_precision_at_k: float
    avg_keyword_coverage: float
    source_accuracy: float
    results: list[EvalResult] = field(default_factory=list)


# 평가 데이터셋
EVAL_DATASET: list[EvalQuery] = [
    EvalQuery(
        query="샤프 비율이란 무엇인가요?",
        expected_sources=["portfolio_theory"],
        expected_keywords=["샤프", "수익률", "변동성", "위험"],
    ),
    EvalQuery(
        query="VaR과 CVaR의 차이점은?",
        expected_sources=["risk_management"],
        expected_keywords=["VaR", "CVaR", "손실", "리스크"],
    ),
    EvalQuery(
        query="효율적 프론티어란?",
        expected_sources=["portfolio_theory"],
        expected_keywords=["효율적 프론티어", "포트폴리오", "최적"],
    ),
    EvalQuery(
        query="섹터 분산 투자 전략",
        expected_sources=["sector_analysis", "investment_strategies"],
        expected_keywords=["섹터", "분산", "투자"],
    ),
    EvalQuery(
        query="리밸런싱 전략의 종류",
        expected_sources=["investment_strategies"],
        expected_keywords=["리밸런싱", "전략"],
    ),
    EvalQuery(
        query="몬테카를로 시뮬레이션이란?",
        expected_sources=["risk_management"],
        expected_keywords=["몬테카를로", "시뮬레이션"],
    ),
]


def evaluate_single_query(
    eval_query: EvalQuery,
    query_fn: Callable[[str, int], list[dict]],
    k: int = 3,
) -> EvalResult:
    """
    단일 쿼리 평가.

    Args:
        eval_query: 평가 쿼리
        query_fn: RAG 검색 함수 (query, k) -> [{"content": ..., "metadata": {"source": ...}}]
        k: 상위 K개 결과

    Returns:
        EvalResult
    """
    results = query_fn(eval_query.query, k)

    # 검색된 소스 추출
    retrieved_sources = [
        r["metadata"].get("source", "") for r in results
    ]

    # Precision@K: 기대 소스와 매칭된 비율
    matched_sources = [
        s for s in retrieved_sources
        if s in eval_query.expected_sources
    ]
    precision = len(matched_sources) / k if k > 0 else 0.0

    # 키워드 커버리지: 검색 결과에 기대 키워드가 포함된 비율
    all_content = " ".join(r.get("content", "") for r in results)
    matched_keywords = [
        kw for kw in eval_query.expected_keywords
        if kw.lower() in all_content.lower()
    ]
    keyword_coverage = (
        len(matched_keywords) / len(eval_query.expected_keywords)
        if eval_query.expected_keywords
        else 0.0
    )

    return EvalResult(
        query=eval_query.query,
        precision_at_k=round(precision, 3),
        keyword_coverage=round(keyword_coverage, 3),
        retrieved_sources=retrieved_sources,
        matched_sources=matched_sources,
        matched_keywords=matched_keywords,
    )


def evaluate_retrieval(
    query_fn: Callable[[str, int], list[dict]],
    dataset: list[EvalQuery] | None = None,
    k: int = 3,
) -> EvalSummary:
    """
    전체 평가 데이터셋으로 RAG retrieval 품질 평가.

    Args:
        query_fn: RAG 검색 함수
        dataset: 평가 데이터셋 (None이면 기본 데이터셋 사용)
        k: 상위 K개 결과

    Returns:
        EvalSummary
    """
    if dataset is None:
        dataset = EVAL_DATASET

    if not dataset:
        return EvalSummary(
            total_queries=0,
            avg_precision_at_k=0.0,
            avg_keyword_coverage=0.0,
            source_accuracy=0.0,
        )

    results = []
    for eq in dataset:
        try:
            result = evaluate_single_query(eq, query_fn, k=k)
            results.append(result)
        except Exception as e:
            logger.warning(f"Evaluation failed for query '{eq.query}': {e}")

    if not results:
        return EvalSummary(
            total_queries=len(dataset),
            avg_precision_at_k=0.0,
            avg_keyword_coverage=0.0,
            source_accuracy=0.0,
        )

    avg_precision = sum(r.precision_at_k for r in results) / len(results)
    avg_keyword_cov = sum(r.keyword_coverage for r in results) / len(results)

    # Source accuracy: 최소 1개의 기대 소스가 매칭된 쿼리 비율
    source_hits = sum(1 for r in results if len(r.matched_sources) > 0)
    source_accuracy = source_hits / len(results)

    return EvalSummary(
        total_queries=len(results),
        avg_precision_at_k=round(avg_precision, 3),
        avg_keyword_coverage=round(avg_keyword_cov, 3),
        source_accuracy=round(source_accuracy, 3),
        results=results,
    )
