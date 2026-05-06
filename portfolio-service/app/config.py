from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Portfolio Service"
    app_version: str = "0.1.0"
    debug: bool = False

    # API 설정
    api_prefix: str = "/api"

    # 데이터 설정
    default_risk_free_rate: float = 0.02  # 연 2%
    default_trading_days: int = 252

    # 리스크 계산 설정
    default_confidence_level: float = 0.95
    monte_carlo_simulations: int = 10000

    # 백테스트 설정
    default_transaction_cost: float = 0.001  # 0.1%

    # MLflow 설정
    mlflow_tracking_uri: str = "./mlruns"
    mlflow_experiment_name: str = "aether-portfolio-optimization"

    # 캐시 설정
    redis_url: Optional[str] = None  # None이면 인메모리 캐시 사용
    cache_ttl_prices: int = 3600  # 1시간
    cache_maxsize: int = 1000  # 인메모리 LRU 캐시 최대 항목 수 (D-2 / ADR 0012)

    # 데이터 제공자 설정
    data_provider: str = "yfinance"  # 지원: "yfinance"

    # 인증 (auth-service와 동일 HS256 비밀키 - 256bit 이상)
    jwt_secret: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
