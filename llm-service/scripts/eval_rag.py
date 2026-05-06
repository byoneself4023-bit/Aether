"""D-8 RAG 평가 스크립트 — 자체 4 메트릭 + ad-hoc CLI (ADR 0015)"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class EvalCase(BaseModel):
    question: str = Field(..., min_length=1)
    expected_source: str = Field(..., min_length=1)
    expected_title: str = Field(..., min_length=1)
    expected_keywords: list[str] = Field(default_factory=list)


def load_ground_truth(path: Path) -> list[EvalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"ground truth must be a JSON list, got {type(raw).__name__}")
    return [EvalCase(**item) for item in raw]


def calculate_relevance_at_k(sources: list[dict[str, Any]]) -> float:
    if not sources:
        return 0.0
    scores = [float(s.get("relevance", 0.0)) for s in sources]
    return statistics.mean(scores)


def calculate_recall_at_k(sources: list[dict[str, Any]], expected_source: str) -> float:
    if not sources:
        return 0.0
    actual = {s.get("source", "") for s in sources}
    return 1.0 if expected_source in actual else 0.0


def is_llm_judge_enabled(no_llm_judge_flag: bool) -> bool:
    if no_llm_judge_flag:
        return False
    env = os.getenv("EVAL_LLM_JUDGE_ENABLED", "true").lower()
    return env not in ("false", "0", "no")


def _build_judge_quality_prompt(question: str, answer: str, keywords: list[str]) -> str:
    kw = ", ".join(keywords) if keywords else "(없음)"
    return (
        f"질문: {question}\n생성 답: {answer}\n참조 키워드: {kw}\n\n"
        "생성 답의 정확성과 완성도를 1-5 정수로 평가하세요. "
        'JSON 응답: {"score": int, "reason": str}'
    )


def _build_judge_faithfulness_prompt(answer: str, sources: list[dict[str, Any]]) -> str:
    titles = "; ".join(s.get("title", "Unknown") for s in sources)
    return (
        f"답변: {answer}\n참조 sources: {titles}\n\n"
        "답변의 모든 주장이 sources에 근거하는지 0-1 비율로 평가하세요. "
        'JSON 응답: {"score": float, "reason": str}'
    )


def _parse_judge_score(response: str) -> tuple[float | None, str]:
    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        data = json.loads(cleaned)
        score = data.get("score")
        reason = data.get("reason", "")
        return (float(score), str(reason)) if score is not None else (None, "no score")
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return None, f"parse error: {e}"


def llm_judge_quality(question: str, answer: str, keywords: list[str], call_llm) -> tuple[float | None, str]:
    prompt = _build_judge_quality_prompt(question, answer, keywords)
    try:
        response = call_llm(prompt)
        return _parse_judge_score(response)
    except Exception as e:
        return None, f"llm error: {e}"


def llm_judge_faithfulness(answer: str, sources: list[dict[str, Any]], call_llm) -> tuple[float | None, str]:
    prompt = _build_judge_faithfulness_prompt(answer, sources)
    try:
        response = call_llm(prompt)
        return _parse_judge_score(response)
    except Exception as e:
        return None, f"llm error: {e}"


async def eval_one(
    case: EvalCase,
    k: int,
    judge_enabled: bool,
    query_with_llm,
    call_llm,
) -> dict[str, Any]:
    rag_result = query_with_llm(question=case.question, k=k, include_sources=True)
    answer = rag_result.get("answer", "")
    sources = rag_result.get("sources", [])

    relevance = calculate_relevance_at_k(sources)
    recall = calculate_recall_at_k(sources, case.expected_source)

    quality_score: float | None = None
    quality_reason = "skipped"
    faithfulness_score: float | None = None
    faithfulness_reason = "skipped"

    if judge_enabled:
        quality_score, quality_reason = llm_judge_quality(
            case.question, answer, case.expected_keywords, call_llm
        )
        faithfulness_score, faithfulness_reason = llm_judge_faithfulness(
            answer, sources, call_llm
        )

    return {
        "question": case.question,
        "answer": answer,
        "expected_source": case.expected_source,
        "actual_sources": [s.get("source", "") for s in sources],
        "relevance_at_k": relevance,
        "recall_at_k": recall,
        "quality": quality_score,
        "quality_reason": quality_reason,
        "faithfulness": faithfulness_score,
        "faithfulness_reason": faithfulness_reason,
    }


def aggregate(results: list[dict[str, Any]]) -> dict[str, float | None]:
    if not results:
        return {"relevance_at_k": None, "recall_at_k": None, "quality": None, "faithfulness": None}

    def _mean(key: str) -> float | None:
        values = [r[key] for r in results if r.get(key) is not None]
        return statistics.mean(values) if values else None

    return {
        "relevance_at_k": _mean("relevance_at_k"),
        "recall_at_k": _mean("recall_at_k"),
        "quality": _mean("quality"),
        "faithfulness": _mean("faithfulness"),
    }


def format_markdown(agg: dict[str, float | None], per_question: list[dict[str, Any]], judge_enabled: bool, k: int) -> str:
    lines: list[str] = []
    lines.append("# RAG Evaluation Report (D-8 / ADR 0015)\n")
    lines.append(f"- 질문 수: {len(per_question)}")
    lines.append(f"- top-k: {k}")
    lines.append(f"- LLM-as-judge: {'enabled' if judge_enabled else 'skipped (--no-llm-judge or env)'}\n")

    lines.append("## 집계 메트릭")

    def _fmt(v: float | None, scale: int = 4) -> str:
        return f"{v:.{scale}f}" if v is not None else "N/A"

    lines.append(f"- 평균 relevance@k: {_fmt(agg['relevance_at_k'])}")
    lines.append(f"- 평균 recall@k: {_fmt(agg['recall_at_k'])}")
    lines.append(f"- 평균 LLM-judge quality (1-5): {_fmt(agg['quality'], 2)}")
    lines.append(f"- 평균 faithfulness (0-1): {_fmt(agg['faithfulness'])}")
    lines.append("")

    lines.append("## 질문별 결과")
    lines.append("| # | 질문 | relevance@k | recall@k | quality | faithfulness |")
    lines.append("|---|---|---|---|---|---|")
    for i, r in enumerate(per_question, start=1):
        q = r["question"]
        if len(q) > 40:
            q = q[:37] + "..."
        lines.append(
            f"| {i} | {q} | {r['relevance_at_k']:.4f} | {r['recall_at_k']:.4f} | "
            f"{_fmt(r.get('quality'), 2)} | {_fmt(r.get('faithfulness'))} |"
        )
    lines.append("")

    return "\n".join(lines)


async def eval_main(args: argparse.Namespace) -> int:
    from app.services.rag import init_vectorstore, query_with_llm, get_vectorstore_status
    from app.services.llm import call_llm

    init_vectorstore()
    status = get_vectorstore_status()
    if not status.get("initialized") or status.get("document_count", 0) == 0:
        print("ERROR: vectorstore is empty or not initialized", file=sys.stderr)
        return 2

    cases = load_ground_truth(Path(args.ground_truth))
    judge_enabled = is_llm_judge_enabled(args.no_llm_judge)

    results: list[dict[str, Any]] = []
    for case in cases:
        result = await eval_one(case, args.top_k, judge_enabled, query_with_llm, call_llm)
        results.append(result)

    agg = aggregate(results)

    if args.json:
        output = json.dumps({"aggregate": agg, "per_question": results}, ensure_ascii=False, indent=2)
    else:
        output = format_markdown(agg, results, judge_enabled, args.top_k)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="D-8 RAG 평가 (자체 4 메트릭 / ADR 0015)")
    parser.add_argument("--ground-truth", default="data/eval_rag_ground_truth.json", help="ground truth JSON 파일")
    parser.add_argument("--top-k", type=int, default=3, help="검색 top-k (default 3)")
    parser.add_argument("--output", default=None, help="output path (default stdout)")
    parser.add_argument("--json", action="store_true", help="markdown 대신 JSON 출력")
    parser.add_argument("--no-llm-judge", action="store_true", help="LLM-judge 2 메트릭 skip (Gemini quota 회피)")
    args = parser.parse_args()
    return asyncio.run(eval_main(args))


if __name__ == "__main__":
    sys.exit(main())
