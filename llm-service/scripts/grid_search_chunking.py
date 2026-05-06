"""D-7 Chunking 자동 grid search — Auto Research 본능 (ADR 0017).

subprocess 격리 본능: env 주입 + seed_qdrant + eval_rag 별도 프로세스 호출
(lru_cache settings stale 회피).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from itertools import product
from pathlib import Path
from typing import Any


SIZES_FULL = [500, 1000, 1500]
OVERLAPS_FULL = [100, 200, 300]
SIZES_QUICK = [500, 1500]
OVERLAPS_QUICK = [100, 300]


def generate_combinations(quick: bool = False) -> list[tuple[int, int]]:
    sizes = SIZES_QUICK if quick else SIZES_FULL
    overlaps = OVERLAPS_QUICK if quick else OVERLAPS_FULL
    return list(product(sizes, overlaps))


def run_combination(
    chunk_size: int,
    chunk_overlap: int,
    top_k: int,
    timeout: int = 180,
    runner=subprocess.run,
) -> dict[str, Any]:
    """1 조합 실험: env 주입 + seed_qdrant + eval_rag → JSON 파싱."""
    env = os.environ.copy()
    env["RAG_CHUNK_SIZE"] = str(chunk_size)
    env["RAG_CHUNK_OVERLAP"] = str(chunk_overlap)
    env.setdefault("VECTOR_STORE", "qdrant")

    seed_proc = runner(
        [sys.executable, "-m", "scripts.seed_qdrant", "--sample-query", "warmup"],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if seed_proc.returncode != 0:
        return {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "error": f"seed failed (returncode={seed_proc.returncode}): {seed_proc.stderr[-300:]}",
        }

    eval_proc = runner(
        [
            sys.executable,
            "-m",
            "scripts.eval_rag",
            "--ground-truth",
            "data/eval_rag_ground_truth.json",
            "--top-k",
            str(top_k),
            "--json",
            "--no-llm-judge",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if eval_proc.returncode != 0:
        return {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "error": f"eval failed (returncode={eval_proc.returncode}): {eval_proc.stderr[-300:]}",
        }

    try:
        data = json.loads(eval_proc.stdout)
    except json.JSONDecodeError as e:
        return {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "error": f"JSON parse error: {e}",
        }

    agg = data.get("aggregate", {})
    return {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "recall_at_k": agg.get("recall_at_k"),
        "relevance_at_k": agg.get("relevance_at_k"),
    }


def select_best(results: list[dict]) -> dict | None:
    """recall@k >= 1.0 유지 + relevance@k 최대."""
    valid = [
        r for r in results
        if r.get("recall_at_k") is not None and r["recall_at_k"] >= 1.0
        and r.get("relevance_at_k") is not None
    ]
    if not valid:
        return None
    return max(valid, key=lambda r: r["relevance_at_k"])


def format_markdown(results: list[dict], best: dict | None, top_k: int) -> str:
    lines = [
        "# RAG Chunking Grid Search Results (D-7 / ADR 0017)",
        "",
        f"- 조합 수: {len(results)}",
        f"- top-k: {top_k}",
        f"- 선정 룰: recall@k >= 1.0 유지 + relevance@k 최대",
        "",
        "## 9 조합 결과",
        "| chunk_size | overlap | recall@k | relevance@k | error |",
        "|---|---|---|---|---|",
    ]

    def _fmt(v):
        return f"{v:.4f}" if isinstance(v, (int, float)) else "N/A"

    for r in sorted(results, key=lambda x: (x["chunk_size"], x["chunk_overlap"])):
        recall = _fmt(r.get("recall_at_k"))
        relevance = _fmt(r.get("relevance_at_k"))
        err = r.get("error", "-")
        if err != "-" and len(err) > 60:
            err = err[:57] + "..."
        lines.append(
            f"| {r['chunk_size']} | {r['chunk_overlap']} | {recall} | {relevance} | {err} |"
        )

    lines.append("")
    lines.append("## 최적 조합")
    if best:
        lines.append(
            f"- **chunk_size = {best['chunk_size']} / overlap = {best['chunk_overlap']}**"
        )
        lines.append(f"- recall@k = {best['recall_at_k']:.4f}")
        lines.append(f"- relevance@k = {best['relevance_at_k']:.4f}")
    else:
        lines.append("- 적합 조합 부재 (모든 조합 recall@k < 1.0 또는 error)")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="D-7 Chunking 자동 grid search (ADR 0017)")
    parser.add_argument("--output", default=None, help="markdown 출력 경로 (default stdout)")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--quick", action="store_true", help="4 조합만 (디버깅용)")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    combos = generate_combinations(quick=args.quick)
    print(f"[grid] 조합 {len(combos)}건 시작 (top-k={args.top_k}, quick={args.quick})", file=sys.stderr)

    results: list[dict] = []
    for size, overlap in combos:
        print(f"[grid] chunk_size={size} overlap={overlap} ...", file=sys.stderr)
        result = run_combination(size, overlap, args.top_k, timeout=args.timeout)
        recall = result.get("recall_at_k")
        relevance = result.get("relevance_at_k")
        err = result.get("error")
        if err:
            print(f"  → ERROR: {err[:100]}", file=sys.stderr)
        else:
            print(f"  → recall={recall:.4f} relevance={relevance:.4f}", file=sys.stderr)
        results.append(result)

    best = select_best(results)
    output = format_markdown(results, best, args.top_k)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"[grid] DONE — written to {args.output}", file=sys.stderr)
    else:
        print(output)

    if best:
        print(
            f"[grid] BEST: chunk_size={best['chunk_size']} overlap={best['chunk_overlap']} "
            f"relevance@k={best['relevance_at_k']:.4f}",
            file=sys.stderr,
        )
        return 0
    print("[grid] no valid combination found", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
