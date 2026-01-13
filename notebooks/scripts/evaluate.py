"""모델 평가 스크립트"""

import argparse
import json
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report
)
import mlflow


def evaluate_classifier(predictions, labels):
    """분류 모델 평가"""
    accuracy = accuracy_score(labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average='weighted'
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def evaluate_retrieval(queries, retrieved_docs, relevant_docs):
    """검색 모델 평가"""
    # Precision@K, Recall@K, MRR 계산
    pass


def main(args):
    # 평가 데이터 로드
    # with open(args.predictions_path, 'r') as f:
    #     predictions = json.load(f)

    # 평가 실행
    with mlflow.start_run():
        # metrics = evaluate_classifier(predictions, labels)
        # mlflow.log_metrics(metrics)

        print("Evaluation completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions_path", default="./results/predictions.json")
    parser.add_argument("--labels_path", default="./data/processed/test.json")
    parser.add_argument("--model_type", choices=["classifier", "retrieval"], default="classifier")

    args = parser.parse_args()
    main(args)
