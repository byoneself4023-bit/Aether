"""임베딩 모델 학습 스크립트"""

import argparse
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import mlflow


def main(args):
    # MLflow 설정
    mlflow.set_experiment("complaint-embeddings")

    # 모델 로드
    model = SentenceTransformer(args.model_name)

    # 학습 데이터 준비
    # train_examples = [
    #     InputExample(texts=['text1', 'text2'], label=0.8),
    # ]

    # train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=args.batch_size)
    # train_loss = losses.CosineSimilarityLoss(model)

    # 학습 실행
    with mlflow.start_run():
        mlflow.log_params({
            "model_name": args.model_name,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
        })

        # model.fit(
        #     train_objectives=[(train_dataloader, train_loss)],
        #     epochs=args.epochs,
        #     warmup_steps=100,
        # )

        # 모델 저장
        model.save(args.output_dir)

        print("Training completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    parser.add_argument("--data_path", default="./data/processed/pairs.json")
    parser.add_argument("--output_dir", default="./models/embeddings")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=16)

    args = parser.parse_args()
    main(args)
