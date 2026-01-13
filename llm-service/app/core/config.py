from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "LLM Service"
    DEBUG: bool = True
    
    BASE_DIR: Path = Path.home() / "CIVILCOMPLAINT"
    EMBEDDING_MODEL_PATH: str = str(Path.home() / "CIVILCOMPLAINT" / "models" / "embedding")
    VECTOR_DB_PATH: str = str(Path.home() / "CIVILCOMPLAINT" / "data" / "vectordb" / "faiss_index")
    
    GOOGLE_API_KEY: str = ""  # 여기에 API 키 입력 또는 .env 파일 사용
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma2:2b"
    
    class Config:
        env_file = ".env"

settings = Settings()
