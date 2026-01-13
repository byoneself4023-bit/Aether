"""민원 분류 모델 학습 스크립트"""

import argparse
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from datasets import load_dataset
import mlflow


def main(args):
    # MLflow 설정
    mlflow.set_experiment("complaint-classifier")

    # 토크나이저 및 모델 로드
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=args.num_labels
    )

    # 데이터 로드
    # dataset = load_dataset('json', data_files=args.data_path)

    # 학습 설정
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=100,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    # Trainer 생성
    trainer = Trainer(
        model=model,
        args=training_args,
        # train_dataset=dataset['train'],
        # eval_dataset=dataset['validation'],
    )

    # 학습 실행
    with mlflow.start_run():
        mlflow.log_params({
            "model_name": args.model_name,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
        })

        # trainer.train()

        print("Training completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", default="klue/bert-base")
    parser.add_argument("--data_path", default="./data/processed/train.json")
    parser.add_argument("--output_dir", default="./models/classifier")
    parser.add_argument("--num_labels", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=16)

    args = parser.parse_args()
    main(args)
