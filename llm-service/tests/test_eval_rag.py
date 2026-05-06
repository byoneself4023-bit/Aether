"""D-8 RAG 평가 스크립트 단위 테스트 (ADR 0015)"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.eval_rag import (
    EvalCase,
    aggregate,
    calculate_recall_at_k,
    calculate_relevance_at_k,
    format_markdown,
    is_llm_judge_enabled,
    llm_judge_faithfulness,
    llm_judge_quality,
    load_ground_truth,
)


@pytest.fixture
def sample_sources():
    return [
        {"source": "portfolio_theory", "title": "샤프 비율", "relevance": 0.92},
        {"source": "risk_management", "title": "VaR", "relevance": 0.71},
        {"source": "portfolio_theory", "title": "효율적 프론티어", "relevance": 0.65},
    ]


@pytest.fixture
def valid_ground_truth(tmp_path):
    data = [
        {
            "question": "샤프 비율이란?",
            "expected_source": "portfolio_theory",
            "expected_title": "샤프 비율",
            "expected_keywords": ["Sharpe", "변동성"],
        }
    ]
    path = tmp_path / "gt.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestLoadGroundTruth:
    def test_load_valid_returns_eval_cases(self, valid_ground_truth):
        cases = load_ground_truth(valid_ground_truth)
        assert len(cases) == 1
        assert cases[0].question == "샤프 비율이란?"
        assert cases[0].expected_source == "portfolio_theory"
        assert cases[0].expected_keywords == ["Sharpe", "변동성"]

    def test_load_invalid_schema_raises_validation_error(self, tmp_path):
        path = tmp_path / "invalid.json"
        path.write_text(json.dumps([{"question": "Q1"}]), encoding="utf-8")
        with pytest.raises(ValidationError):
            load_ground_truth(path)

    def test_load_non_list_raises_value_error(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"q": "Q1"}), encoding="utf-8")
        with pytest.raises(ValueError, match="JSON list"):
            load_ground_truth(path)


class TestRelevanceAtK:
    def test_normal_returns_mean(self, sample_sources):
        result = calculate_relevance_at_k(sample_sources)
        assert abs(result - (0.92 + 0.71 + 0.65) / 3) < 1e-6

    def test_empty_returns_zero(self):
        assert calculate_relevance_at_k([]) == 0.0

    def test_missing_relevance_treated_as_zero(self):
        sources = [{"source": "x"}, {"source": "y", "relevance": 0.5}]
        assert calculate_relevance_at_k(sources) == 0.25


class TestRecallAtK:
    def test_full_match_returns_one(self, sample_sources):
        assert calculate_recall_at_k(sample_sources, "portfolio_theory") == 1.0

    def test_partial_match_returns_one(self, sample_sources):
        assert calculate_recall_at_k(sample_sources, "risk_management") == 1.0

    def test_no_match_returns_zero(self, sample_sources):
        assert calculate_recall_at_k(sample_sources, "sector_analysis") == 0.0

    def test_empty_returns_zero(self):
        assert calculate_recall_at_k([], "portfolio_theory") == 0.0


class TestLlmJudgeToggle:
    def test_enabled_by_default(self, monkeypatch):
        monkeypatch.delenv("EVAL_LLM_JUDGE_ENABLED", raising=False)
        assert is_llm_judge_enabled(False) is True

    def test_disabled_by_cli_flag(self):
        assert is_llm_judge_enabled(True) is False

    def test_disabled_by_env_false(self, monkeypatch):
        monkeypatch.setenv("EVAL_LLM_JUDGE_ENABLED", "false")
        assert is_llm_judge_enabled(False) is False

    def test_disabled_by_env_zero(self, monkeypatch):
        monkeypatch.setenv("EVAL_LLM_JUDGE_ENABLED", "0")
        assert is_llm_judge_enabled(False) is False


class TestLlmJudgeFunctions:
    def test_quality_parses_valid_score(self):
        def mock_call(prompt: str) -> str:
            return '{"score": 4, "reason": "정확하고 완성도 높음"}'

        score, reason = llm_judge_quality("Q", "A", ["k1"], mock_call)
        assert score == 4.0
        assert "정확" in reason

    def test_quality_handles_markdown_code_fence(self):
        def mock_call(prompt: str) -> str:
            return '```json\n{"score": 5, "reason": "완벽"}\n```'

        score, _ = llm_judge_quality("Q", "A", [], mock_call)
        assert score == 5.0

    def test_quality_handles_invalid_json(self):
        def mock_call(prompt: str) -> str:
            return "not json"

        score, reason = llm_judge_quality("Q", "A", [], mock_call)
        assert score is None
        assert "parse error" in reason

    def test_quality_handles_llm_exception(self):
        def mock_call(prompt: str) -> str:
            raise RuntimeError("API down")

        score, reason = llm_judge_quality("Q", "A", [], mock_call)
        assert score is None
        assert "llm error" in reason

    def test_faithfulness_parses_valid_score(self, sample_sources):
        def mock_call(prompt: str) -> str:
            return '{"score": 0.85, "reason": "대부분 sources에 근거"}'

        score, _ = llm_judge_faithfulness("answer", sample_sources, mock_call)
        assert score == 0.85


class TestAggregate:
    def test_handles_empty_results(self):
        agg = aggregate([])
        assert agg["relevance_at_k"] is None
        assert agg["recall_at_k"] is None
        assert agg["quality"] is None
        assert agg["faithfulness"] is None

    def test_excludes_none_quality_from_mean(self):
        results = [
            {"relevance_at_k": 0.8, "recall_at_k": 1.0, "quality": 4.0, "faithfulness": 0.9},
            {"relevance_at_k": 0.6, "recall_at_k": 0.0, "quality": None, "faithfulness": None},
        ]
        agg = aggregate(results)
        assert abs(agg["relevance_at_k"] - 0.7) < 1e-6
        assert agg["recall_at_k"] == 0.5
        assert agg["quality"] == 4.0
        assert agg["faithfulness"] == 0.9


class TestFormatMarkdown:
    def test_includes_all_metrics_when_judge_enabled(self):
        agg = {"relevance_at_k": 0.8, "recall_at_k": 0.9, "quality": 4.2, "faithfulness": 0.85}
        per_q = [{"question": "Q1", "relevance_at_k": 0.8, "recall_at_k": 1.0, "quality": 4.2, "faithfulness": 0.85}]
        out = format_markdown(agg, per_q, judge_enabled=True, k=3)
        assert "relevance@k" in out
        assert "recall@k" in out
        assert "quality" in out
        assert "faithfulness" in out
        assert "enabled" in out

    def test_marks_skipped_when_judge_disabled(self):
        agg = {"relevance_at_k": 0.8, "recall_at_k": 0.9, "quality": None, "faithfulness": None}
        per_q = [{"question": "Q1", "relevance_at_k": 0.8, "recall_at_k": 1.0, "quality": None, "faithfulness": None}]
        out = format_markdown(agg, per_q, judge_enabled=False, k=3)
        assert "skipped" in out
        assert "N/A" in out

    def test_includes_per_question_table(self):
        agg = {"relevance_at_k": 0.8, "recall_at_k": 0.9, "quality": 4.2, "faithfulness": 0.85}
        per_q = [
            {"question": "Q1", "relevance_at_k": 0.8, "recall_at_k": 1.0, "quality": 4.2, "faithfulness": 0.85},
            {"question": "Q2", "relevance_at_k": 0.7, "recall_at_k": 0.0, "quality": 3.0, "faithfulness": 0.6},
        ]
        out = format_markdown(agg, per_q, judge_enabled=True, k=3)
        assert "| 1 | Q1" in out
        assert "| 2 | Q2" in out


class TestEvalCase:
    def test_requires_question(self):
        with pytest.raises(ValidationError):
            EvalCase(expected_source="x", expected_title="t")

    def test_default_keywords_empty_list(self):
        case = EvalCase(question="Q", expected_source="x", expected_title="t")
        assert case.expected_keywords == []
