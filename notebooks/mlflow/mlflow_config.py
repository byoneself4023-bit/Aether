"""MLflow 설정 및 유틸리티"""

import mlflow
from mlflow.tracking import MlflowClient


def setup_mlflow(
    tracking_uri: str = "http://localhost:5000",
    experiment_name: str = "civil-complaint"
):
    """MLflow 초기화"""
    mlflow.set_tracking_uri(tracking_uri)

    # 실험 생성 또는 가져오기
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)

    if experiment is None:
        experiment_id = client.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id

    mlflow.set_experiment(experiment_name)

    return experiment_id


def log_model_artifacts(model, model_name: str, metrics: dict):
    """모델 및 메트릭 로깅"""
    with mlflow.start_run():
        # 메트릭 로깅
        mlflow.log_metrics(metrics)

        # 모델 저장
        mlflow.pytorch.log_model(model, model_name)


def get_best_model(experiment_name: str, metric: str = "f1"):
    """최적 모델 가져오기"""
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{metric} DESC"],
        max_results=1
    )

    if runs:
        return runs[0]
    return None
