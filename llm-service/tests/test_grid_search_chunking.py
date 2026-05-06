"""D-7 grid_search_chunking 단위 테스트 (ADR 0017)"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from scripts.grid_search_chunking import (
    format_markdown,
    generate_combinations,
    run_combination,
    select_best,
)


class TestGenerateCombinations:
    def test_full_grid_returns_9(self):
        combos = generate_combinations(quick=False)
        assert len(combos) == 9
        assert (500, 100) in combos
        assert (1500, 300) in combos
        assert (1000, 200) in combos

    def test_quick_mode_returns_4(self):
        combos = generate_combinations(quick=True)
        assert len(combos) == 4
        assert (500, 100) in combos
        assert (1500, 300) in combos


class TestSelectBest:
    def test_max_relevance_when_all_recall_one(self):
        results = [
            {"chunk_size": 500, "chunk_overlap": 100, "recall_at_k": 1.0, "relevance_at_k": 0.7},
            {"chunk_size": 1000, "chunk_overlap": 200, "recall_at_k": 1.0, "relevance_at_k": 0.85},
            {"chunk_size": 1500, "chunk_overlap": 300, "recall_at_k": 1.0, "relevance_at_k": 0.6},
        ]
        best = select_best(results)
        assert best["chunk_size"] == 1000
        assert best["relevance_at_k"] == 0.85

    def test_excludes_recall_below_one(self):
        results = [
            {"chunk_size": 500, "chunk_overlap": 100, "recall_at_k": 0.875, "relevance_at_k": 0.95},
            {"chunk_size": 1000, "chunk_overlap": 200, "recall_at_k": 1.0, "relevance_at_k": 0.7},
        ]
        best = select_best(results)
        assert best["chunk_size"] == 1000

    def test_returns_none_when_no_valid(self):
        results = [
            {"chunk_size": 500, "chunk_overlap": 100, "recall_at_k": 0.5, "relevance_at_k": 0.95},
            {"chunk_size": 1000, "chunk_overlap": 200, "error": "seed failed"},
        ]
        assert select_best(results) is None

    def test_handles_none_relevance(self):
        results = [
            {"chunk_size": 500, "chunk_overlap": 100, "recall_at_k": 1.0, "relevance_at_k": None},
            {"chunk_size": 1000, "chunk_overlap": 200, "recall_at_k": 1.0, "relevance_at_k": 0.7},
        ]
        best = select_best(results)
        assert best["chunk_size"] == 1000


class TestFormatMarkdown:
    def test_includes_table_and_best(self):
        results = [
            {"chunk_size": 500, "chunk_overlap": 100, "recall_at_k": 1.0, "relevance_at_k": 0.72},
            {"chunk_size": 1000, "chunk_overlap": 200, "recall_at_k": 1.0, "relevance_at_k": 0.85},
        ]
        best = {"chunk_size": 1000, "chunk_overlap": 200, "recall_at_k": 1.0, "relevance_at_k": 0.85}
        out = format_markdown(results, best, top_k=3)
        assert "RAG Chunking Grid Search" in out
        assert "| 500 | 100 |" in out
        assert "| 1000 | 200 |" in out
        assert "chunk_size = 1000" in out

    def test_marks_no_valid_combination(self):
        results = [{"chunk_size": 500, "chunk_overlap": 100, "error": "seed failed"}]
        out = format_markdown(results, None, top_k=3)
        assert "적합 조합 부재" in out


class TestRunCombination:
    def test_seed_failure_returns_error(self):
        def fake_runner(*args, **kwargs):
            mock = MagicMock()
            mock.returncode = 1
            mock.stderr = "seed went wrong"
            mock.stdout = ""
            return mock

        result = run_combination(500, 100, top_k=3, runner=fake_runner)
        assert "error" in result
        assert "seed failed" in result["error"]

    def test_eval_failure_returns_error(self):
        call_count = {"n": 0}

        def fake_runner(args, **kwargs):
            call_count["n"] += 1
            mock = MagicMock()
            if call_count["n"] == 1:
                mock.returncode = 0
                mock.stdout = "[seed] DONE"
                mock.stderr = ""
            else:
                mock.returncode = 2
                mock.stdout = ""
                mock.stderr = "eval blew up"
            return mock

        result = run_combination(500, 100, top_k=3, runner=fake_runner)
        assert "error" in result
        assert "eval failed" in result["error"]

    def test_success_returns_metrics(self):
        call_count = {"n": 0}

        def fake_runner(args, **kwargs):
            call_count["n"] += 1
            mock = MagicMock()
            if call_count["n"] == 1:
                mock.returncode = 0
                mock.stdout = "[seed] DONE"
                mock.stderr = ""
            else:
                mock.returncode = 0
                mock.stdout = json.dumps({
                    "aggregate": {"recall_at_k": 1.0, "relevance_at_k": 0.78, "quality": None, "faithfulness": None},
                    "per_question": [],
                })
                mock.stderr = ""
            return mock

        result = run_combination(1000, 200, top_k=3, runner=fake_runner)
        assert result["chunk_size"] == 1000
        assert result["chunk_overlap"] == 200
        assert result["recall_at_k"] == 1.0
        assert result["relevance_at_k"] == 0.78
        assert "error" not in result
