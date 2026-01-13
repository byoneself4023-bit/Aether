"""
ML Service 설정
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """앱 설정"""
    
    # 앱 정보
    APP_NAME: str = "ML Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 경로 설정
    BASE_DIR: Path = Path.home() / "CIVILCOMPLAINT"
    MODEL_DIR: Path = BASE_DIR / "models"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # 모델 경로
    DOMAIN_CLASSIFIER_PATH: Path = MODEL_DIR / "domain_classifier"
    CATEGORY_CLASSIFIER_PATH: Path = MODEL_DIR / "category_classifier"
    EMBEDDING_MODEL_PATH: Path = MODEL_DIR / "embedding_model"
    
    # 모델 설정
    MAX_LENGTH: int = 128
    DEVICE: str = "cpu"  # 또는 "cuda"
    
    # API 설정
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        extra = "allow"


# 싱글톤 인스턴스
settings = Settings()
