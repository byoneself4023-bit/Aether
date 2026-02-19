from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """LLM Service 설정"""

    # 서비스 설정
    app_name: str = "llm-service"
    app_version: str = "1.0.0"
    debug: bool = False

    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8002

    # LLM 설정
    google_api_key: str = ""
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_timeout: int = 30

    # RAG 설정
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "models/gemini-embedding-001"
    rag_top_k: int = 5
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 200

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # 외부 서비스
    portfolio_service_url: str = "http://localhost:8001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
