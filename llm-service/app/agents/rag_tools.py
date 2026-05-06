"""D-5 RAG 도구 — ReAct agent 5번째 도구 (ADR 0018).

도메인 분리 본능: portfolio_tools.py (수치 분석 4종) ↔ rag_tools.py (지식 검색 1종).
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from app.services.rag import query_with_llm


@tool
def search_knowledge_base(question: str) -> dict[str, Any]:
    """투자 도메인 지식 검색 (포트폴리오 이론 / 리스크 관리 / 투자 전략 / 섹터 분석).

    질문에 대한 답변 + 참조 sources를 반환. 도메인 정의 / 개념 설명 질문에 사용.
    예시: "샤프 비율이란?", "VaR 계산 방법?", "동일 비중 전략 장점?".

    포트폴리오 분석 (티커 / weights / metrics 제공) 질문에는 analyze_portfolio_tool 우선 사용.
    리스크 데이터 (VaR / CVaR 수치) 해석에는 explain_risk_tool 우선 사용.
    """
    result = query_with_llm(question=question, k=3, include_sources=True)
    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
    }
