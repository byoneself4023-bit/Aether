"""
Claro Backend 설정
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """앱 설정"""

    # 앱 정보
    APP_NAME: str = "Claro Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 경로 설정
    BASE_DIR: Path = Path.home() / "CIVILCOMPLAINT"
    MODEL_DIR: Path = BASE_DIR / "models"
    DATA_DIR: Path = BASE_DIR / "data"

    # ML 모델 경로
    DOMAIN_CLASSIFIER_PATH: Path = MODEL_DIR / "domain_classifier"
    CATEGORY_CLASSIFIER_PATH: Path = MODEL_DIR / "category_classifier"
    EMBEDDING_MODEL_PATH: str = str(Path.home() / "CIVILCOMPLAINT" / "models" / "embedding")
    VECTOR_DB_PATH: str = str(Path.home() / "CIVILCOMPLAINT" / "data" / "vectordb" / "faiss_index")

    # 모델 설정
    MAX_LENGTH: int = 128
    DEVICE: str = "cpu"

    # LLM 설정
    LLM_BACKEND: str = "ollama"  # ollama / gguf / gemini
    GOOGLE_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma2:2b"
    GGUF_MODEL_PATH: str = str(Path.home() / "CIVILCOMPLAINT" / "models" / "gguf" / "model-q4-k-m.gguf")
    GGUF_N_CTX: int = 1024

    # API 설정
    API_V1_PREFIX: str = "/api/v1"

    # Stats 캐시 TTL (초)
    STATS_CACHE_TTL: int = 60

    class Config:
        env_file = ".env"
        extra = "allow"


# 싱글톤 인스턴스
settings = Settings()
