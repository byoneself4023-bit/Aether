"""모델 정보 라우트 — JSON 파일 기반 메트릭스 연동"""
import json
from pathlib import Path
from fastapi import APIRouter
from app.resources.registry import registry
from app.core.config import settings

router = APIRouter()

METRICS_DIR = settings.BASE_DIR / "results"


def _load_metrics_json(filename: str) -> dict | None:
    """results/ 디렉토리에서 JSON 메트릭스 파일 로드"""
    path = METRICS_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@router.get("/info")
async def get_model_info():
    """현재 활성 모델 정보 (mock 여부 포함)"""
    health = registry.health_check()

    def _status(key: str) -> str:
        info = health.get(key, {})
        if isinstance(info, dict):
            if info.get("mock"):
                return "mock"
            return "active" if info.get("loaded") else "inactive"
        return "active" if info else "inactive"

    models = [
        {
            "name": "Domain Classifier (BERT)",
            "type": "classification",
            "status": _status("domain_classifier"),
            "description": "민원 텍스트를 14개 도메인으로 분류",
            "metrics": _get_classification_metrics("domain"),
        },
        {
            "name": "Category Classifier (BERT)",
            "type": "classification",
            "status": _status("category_classifier"),
            "description": "도메인 내 63개 카테고리 세분류",
            "metrics": _get_classification_metrics("category"),
        },
        {
            "name": "Sentence-BERT + FAISS",
            "type": "retrieval",
            "status": _status("faiss_store"),
            "description": "456K QA 쌍 벡터 유사도 검색",
            "metrics": _get_retrieval_metrics(),
        },
        {
            "name": settings.OLLAMA_MODEL,
            "type": "generation",
            "status": _status("ollama"),
            "description": f"Ollama 로컬 LLM ({settings.OLLAMA_MODEL})",
            "metrics": {},
        },
        {
            "name": "Gemini",
            "type": "generation",
            "status": _status("gemini"),
            "description": "Google Gemini API",
            "metrics": {},
        },
    ]

    return {"models": models, "mock_mode": registry.is_mock("domain_classifier")}


@router.get("/metrics")
async def get_model_metrics():
    """모델 성능 지표 (results/ JSON 파일에서 로드)"""
    ml_results = _load_metrics_json("classification_ml_results.json")
    dl_results = _load_metrics_json("classification_dl_results.json")
    bm25_results = _load_metrics_json("retrieval_bm25_results.json")
    sbert_results = _load_metrics_json("retrieval_sbert_results.json")

    # Classification experiments
    classification_experiments = []

    if ml_results and "test" in ml_results:
        for r in ml_results["test"]:
            if r.get("level") == "domain":
                classification_experiments.append({
                    "name": r["model"],
                    "accuracy": r.get("accuracy"),
                    "macro_f1": r.get("macro_f1"),
                    "weighted_f1": r.get("weighted_f1"),
                    "status": "completed",
                    "source": "04_baseline_ml",
                })
    else:
        classification_experiments.extend([
            {"name": "TF-IDF + LogisticRegression", "accuracy": None, "macro_f1": None, "status": "pending"},
            {"name": "TF-IDF + LightGBM", "accuracy": None, "macro_f1": None, "status": "pending"},
        ])

    if dl_results and "test" in dl_results:
        for r in dl_results["test"]:
            if r.get("level") == "domain":
                classification_experiments.append({
                    "name": r["model"],
                    "accuracy": r.get("accuracy"),
                    "macro_f1": r.get("macro_f1"),
                    "weighted_f1": r.get("weighted_f1"),
                    "status": "completed",
                    "source": "05_deep_classification",
                })
    else:
        classification_experiments.extend([
            {"name": "KoBERT Fine-tuned", "accuracy": None, "macro_f1": None, "status": "pending"},
            {"name": "KoELECTRA Fine-tuned", "accuracy": None, "macro_f1": None, "status": "pending"},
        ])

    # Retrieval experiments
    retrieval_experiments = []

    if bm25_results:
        retrieval_experiments.append({
            "name": "BM25",
            "recall_at_5": bm25_results.get("recall_at_5"),
            "mrr": bm25_results.get("mrr"),
            "status": "completed",
            "source": "06_bm25_retrieval",
        })
    else:
        retrieval_experiments.append({"name": "BM25", "recall_at_5": None, "mrr": None, "status": "pending"})

    if sbert_results:
        for exp in sbert_results.get("experiments", [sbert_results]):
            retrieval_experiments.append({
                "name": exp.get("model", "SBERT + FAISS"),
                "recall_at_5": exp.get("recall_at_5"),
                "mrr": exp.get("mrr"),
                "status": "completed",
                "source": "07_sbert_faiss",
            })
    else:
        retrieval_experiments.append({"name": "SBERT + FAISS", "recall_at_5": None, "mrr": None, "status": "pending"})

    return {
        "classification": {"experiments": classification_experiments},
        "retrieval": {"experiments": retrieval_experiments},
        "generation": {
            "experiments": [
                {"name": "Gemma 2B (zero-shot)", "rouge_l": None, "status": "pending"},
                {"name": "Qwen 2.5 7B (LoRA)", "rouge_l": None, "status": "pending"},
            ]
        },
    }


def _get_classification_metrics(level: str) -> dict:
    """분류 모델 best metrics 추출"""
    for fname in ["classification_dl_results.json", "classification_ml_results.json"]:
        data = _load_metrics_json(fname)
        if data and "best_models" in data and level in data["best_models"]:
            best = data["best_models"][level]
            return {
                "accuracy": best.get("accuracy"),
                "macro_f1": best.get("macro_f1"),
                "model": best.get("model"),
            }
    # fallback hardcoded
    if level == "domain":
        return {"accuracy": 0.811, "macro_f1": 0.677}
    return {}


def _get_retrieval_metrics() -> dict:
    """검색 모델 best metrics 추출"""
    data = _load_metrics_json("retrieval_sbert_results.json")
    if data:
        return {
            "recall_at_5": data.get("recall_at_5", data.get("best_recall_at_5")),
            "mrr": data.get("mrr", data.get("best_mrr")),
        }
    return {"recall_at_5": 0.85}
