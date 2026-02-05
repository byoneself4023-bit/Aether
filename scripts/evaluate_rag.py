"""
RAGAS 기반 RAG 품질 평가 스크립트

사용법:
    python scripts/evaluate_rag.py --sample 100
    python scripts/evaluate_rag.py --sample 50 --output data/eval_results/

평가 메트릭:
    - faithfulness: 답변이 컨텍스트에 충실한가
    - answer_relevancy: 답변이 질문에 관련 있는가
    - context_precision: 검색된 문서가 정확한가
    - context_recall: 필요한 문서를 모두 검색했는가

데이터:
    - notebooks/에서 생성된 qa_pairs.parquet → ground truth
    - FAISS 벡터 검색 + LLM 답변 → 평가 대상
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from datasets import Dataset

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


def load_qa_pairs(sample_n: int) -> pd.DataFrame:
    """qa_pairs 데이터 로드 + 샘플링"""
    candidates = [
        PROJECT_ROOT / "data" / "qa_pairs.parquet",
        PROJECT_ROOT / "backend" / "data" / "qa_pairs.parquet",
        PROJECT_ROOT / "notebooks" / "qa_pairs.parquet",
    ]

    qa_path = None
    for p in candidates:
        if p.exists():
            qa_path = p
            break

    if qa_path is None:
        # CSV 폴백
        for p in candidates:
            csv_p = p.with_suffix(".csv")
            if csv_p.exists():
                qa_path = csv_p
                break

    if qa_path is None:
        raise FileNotFoundError(
            "qa_pairs 파일을 찾을 수 없습니다. "
            "notebooks/02_preprocessing.ipynb 를 실행하여 생성하세요."
        )

    print(f"[*] QA 데이터 로드: {qa_path}")
    if qa_path.suffix == ".parquet":
        df = pd.read_parquet(qa_path)
    else:
        df = pd.read_csv(qa_path)

    if sample_n < len(df):
        df = df.sample(n=sample_n, random_state=42)
    print(f"[*] 샘플 수: {len(df)}")
    return df.reset_index(drop=True)


def run_retrieval_and_generation(df: pd.DataFrame) -> dict:
    """각 질문에 대해 FAISS 검색 + LLM 답변 생성"""
    from app.vectorstore.faiss_store import FAISSStore
    from app.llm.ollama import OllamaLLM

    store = FAISSStore()
    llm = OllamaLLM()

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for i, row in df.iterrows():
        question = row.get("question") or row.get("input") or row.get("민원내용", "")
        gt_answer = row.get("answer") or row.get("output") or row.get("답변내용", "")

        if not question:
            continue

        print(f"  [{i+1}/{len(df)}] {question[:50]}...")

        # 검색
        try:
            results = store.search(question, top_k=5)
            ctx = [r.get("answer", r.get("text", "")) for r in results]
        except Exception as e:
            print(f"    검색 실패: {e}")
            ctx = []

        # 생성
        try:
            answer = llm.generate(question)
        except Exception as e:
            print(f"    생성 실패: {e}")
            answer = ""

        questions.append(question)
        answers.append(answer)
        contexts.append(ctx)
        ground_truths.append(gt_answer)

    return {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    }


def evaluate_with_ragas(data: dict) -> dict:
    """RAGAS 평가 실행"""
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )

    dataset = Dataset.from_dict(data)

    print("[*] RAGAS 평가 실행 중...")
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    return {k: round(float(v), 4) for k, v in result.items()}


def main():
    parser = argparse.ArgumentParser(description="RAGAS RAG 품질 평가")
    parser.add_argument("--sample", type=int, default=100, help="평가 샘플 수")
    parser.add_argument(
        "--output",
        type=str,
        default=str(PROJECT_ROOT / "data" / "eval_results"),
        help="결과 저장 디렉토리",
    )
    args = parser.parse_args()

    # 1) QA 데이터 로드
    df = load_qa_pairs(args.sample)

    # 2) 검색 + 생성
    print("[*] FAISS 검색 + LLM 답변 생성 중...")
    data = run_retrieval_and_generation(df)

    if not data["question"]:
        print("[!] 평가할 데이터가 없습니다.")
        return

    # 3) RAGAS 평가
    scores = evaluate_with_ragas(data)

    # 4) 결과 저장
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"ragas_{timestamp}.json"

    result = {
        "timestamp": timestamp,
        "sample_size": len(data["question"]),
        "scores": scores,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"RAGAS 평가 결과")
    print(f"{'='*50}")
    for metric, score in scores.items():
        print(f"  {metric:25s}: {score:.4f}")
    print(f"{'='*50}")
    print(f"결과 저장: {output_path}")


if __name__ == "__main__":
    main()
