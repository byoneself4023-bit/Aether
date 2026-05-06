from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import field_validator


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
    llm_max_tokens: int = 4096
    llm_timeout: int = 30

    # RAG 설정
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "models/gemini-embedding-001"
    rag_top_k: int = 5
    # D-7 / ADR 0017: grid search 9 조합 결과 — chunk_size=500/overlap=300이 relevance@k 0.7413 (1000/200 baseline 0.7222 대비 +0.0191 향상)
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 300

    # T-6: 벡터 DB 토글 (chromadb | qdrant). T-6b 머지로 default qdrant 정착 (ADR 0016).
    vector_store: str = "qdrant"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "aether_knowledge"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # 외부 서비스
    portfolio_service_url: str = "http://localhost:8001"

    # 인증 (auth-service와 동일 HS512 비밀키 - F-1a / ADR 0004 v2)
    jwt_secret: str = ""

    # T-1b: ReAct 토글 (USE_REACT_AGENT=false면 절차적 호출 fallback)
    use_react_agent: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("google_api_key")
    @classmethod
    def google_api_key_must_be_present(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "GOOGLE_API_KEY is required (set GEMINI_API_KEY env var). "
                "See .env.example. D-2 / ADR 0012 lifespan + config 이중 검증."
            )
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
