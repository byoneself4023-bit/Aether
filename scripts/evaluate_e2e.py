#!/usr/bin/env python3
"""
Claro E2E 파이프라인 평가 스크립트

백엔드 API를 호출하여 classify → search → generate 전체 파이프라인을 평가합니다.
도메인 필터링 ON/OFF 비교를 포함합니다.

사용법:
  python scripts/evaluate_e2e.py --base-url http://localhost:8010 --n-samples 100
"""
import argparse
import json
import time
import sys
from pathlib import Path

import httpx
import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser(description="Claro E2E Pipeline Evaluation")
    p.add_argument("--base-url", default="http://localhost:8010")
    p.add_argument("--n-samples", type=int, default=100)
    p.add_argument("--data-path", default=None, help="QA pairs parquet path")
    p.add_argument("--output", default="results/e2e_evaluation.json")
    p.add_argument("--timeout", type=float, default=120.0)
    return p.parse_args()


def load_test_data(data_path: str, n_samples: int) -> pd.DataFrame:
    """테스트 데이터 로드 (QA pairs에서 샘플링)"""
    if data_path and Path(data_path).exists():
        df = pd.read_parquet(data_path)
    else:
        # 기본 경로 탐색
        candidates = [
            Path.home() / "CIVILCOMPLAINT" / "data" / "processed" / "qa_pairs.parquet",
            Path("data/processed/qa_pairs.parquet"),
            Path("../data/processed/qa_pairs.parquet"),
        ]
        df = None
        for cp in candidates:
            if cp.exists():
                df = pd.read_parquet(cp)
                print(f"데이터 로드: {cp} ({len(df):,}건)")
                break
        if df is None:
            print("QA pairs 데이터를 찾을 수 없습니다.")
            sys.exit(1)

    # 샘플링
    np.random.seed(42)
    n = min(n_samples, len(df))
    sample_df = df.sample(n=n, random_state=42).reset_index(drop=True)
    return sample_df


def call_classify(base_url: str, text: str, timeout: float) -> dict:
    """분류 API 호출"""
    r = httpx.post(
        f"{base_url}/api/v1/classify",
        json={"text": text},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()


def call_search(base_url: str, query: str, timeout: float) -> dict:
    """검색 API 호출"""
    r = httpx.post(
        f"{base_url}/api/v1/search/similar",
        json={"query": query},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()


def call_generate(base_url: str, query: str, timeout: float) -> dict:
    """생성 API 호출"""
    r = httpx.post(
        f"{base_url}/api/v1/generate/",
        json={"query": query},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()


def call_pipeline_sse(base_url: str, query: str, timeout: float) -> dict:
    """SSE 파이프라인 전체 호출 → 각 단계 결과 파싱"""
    steps = {}
    with httpx.stream(
        "POST",
        f"{base_url}/api/v1/pipeline/process",
        json={"query": query},
        timeout=timeout,
    ) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                name = data.get("name")
                status = data.get("status")
                if status == "done":
                    steps[name] = data.get("result")
                elif status == "error":
                    steps[name] = {"error": data.get("error")}
    return steps


def evaluate_classification(results: list, test_df: pd.DataFrame) -> dict:
    """분류 정확도 평가"""
    if "domain" not in test_df.columns:
        return {"skip": "domain 컬럼 없음"}

    correct = 0
    total = len(results)
    per_domain = {}

    for i, res in enumerate(results):
        gt_domain = test_df.iloc[i].get("domain", "")
        pred_domain = res.get("domain", "")

        if gt_domain not in per_domain:
            per_domain[gt_domain] = {"correct": 0, "total": 0}
        per_domain[gt_domain]["total"] += 1

        if pred_domain == gt_domain:
            correct += 1
            per_domain[gt_domain]["correct"] += 1

    accuracy = correct / total if total > 0 else 0
    per_domain_acc = {
        d: round(v["correct"] / v["total"], 4) if v["total"] > 0 else 0
        for d, v in per_domain.items()
    }

    return {
        "accuracy": round(accuracy, 4),
        "correct": correct,
        "total": total,
        "per_domain": per_domain_acc,
    }


def evaluate_search(search_results: list, test_df: pd.DataFrame) -> dict:
    """검색 결과에 정답 답변 포함 여부 평가"""
    if "answer" not in test_df.columns:
        return {"skip": "answer 컬럼 없음"}

    hits_at_1 = 0
    hits_at_5 = 0
    total = len(search_results)

    for i, results in enumerate(search_results):
        gt_answer = test_df.iloc[i].get("answer", "")
        if not isinstance(results, list):
            continue
        answers = [r.get("answer", "") for r in results]

        if answers and answers[0] == gt_answer:
            hits_at_1 += 1
        if gt_answer in answers:
            hits_at_5 += 1

    return {
        "recall_at_1": round(hits_at_1 / total, 4) if total > 0 else 0,
        "recall_at_5": round(hits_at_5 / total, 4) if total > 0 else 0,
        "total": total,
    }


def main():
    args = parse_args()
    print(f"Claro E2E 평가 시작")
    print(f"  서버: {args.base_url}")
    print(f"  샘플 수: {args.n_samples}")

    # 서버 상태 확인
    try:
        health = httpx.get(f"{args.base_url}/health", timeout=5).json()
        print(f"  서버 상태: {health.get('status')}")
        print(f"  LLM 백엔드: {health.get('resources', {}).get('llm_backend', 'N/A')}")
    except Exception as e:
        print(f"서버 연결 실패: {e}")
        sys.exit(1)

    # 데이터 로드
    test_df = load_test_data(args.data_path, args.n_samples)
    print(f"  테스트 데이터: {len(test_df)}건")

    # E2E 평가 실행
    classify_results = []
    search_results = []
    generate_results = []
    latencies = []

    for i, row in test_df.iterrows():
        query = row.get("question", row.get("input", ""))
        if not query:
            continue

        t0 = time.time()
        try:
            # 개별 API 호출 (단계별 결과 수집)
            clf = call_classify(args.base_url, query, args.timeout)
            classify_results.append(clf)

            search = call_search(args.base_url, query, args.timeout)
            search_results.append(search.get("results", []))

            gen = call_generate(args.base_url, query, args.timeout)
            generate_results.append(gen)

            elapsed = time.time() - t0
            latencies.append(elapsed)

        except Exception as e:
            classify_results.append({})
            search_results.append([])
            generate_results.append({})
            latencies.append(time.time() - t0)
            print(f"  [{i+1}] 오류: {e}")

        if (i + 1) % 20 == 0:
            avg_lat = np.mean(latencies[-20:])
            print(f"  [{i+1}/{len(test_df)}] 평균 응답시간: {avg_lat:.2f}s")

    # 평가 메트릭 계산
    print("\n=== 평가 결과 ===")

    clf_metrics = evaluate_classification(classify_results, test_df)
    print(f"\n분류 정확도: {clf_metrics.get('accuracy', 'N/A')}")

    search_metrics = evaluate_search(search_results, test_df)
    print(f"검색 Recall@1: {search_metrics.get('recall_at_1', 'N/A')}")
    print(f"검색 Recall@5: {search_metrics.get('recall_at_5', 'N/A')}")

    # 종합 결과 저장
    output = {
        "config": {
            "base_url": args.base_url,
            "n_samples": len(test_df),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "classification": clf_metrics,
        "search": search_metrics,
        "latency": {
            "mean_s": round(float(np.mean(latencies)), 2),
            "std_s": round(float(np.std(latencies)), 2),
            "p50_s": round(float(np.median(latencies)), 2),
            "p95_s": round(float(np.percentile(latencies, 95)), 2),
        },
        "generation": {
            "n_successful": sum(1 for g in generate_results if g.get("answer")),
            "n_total": len(generate_results),
        },
    }

    # 저장
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: {out_path}")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
