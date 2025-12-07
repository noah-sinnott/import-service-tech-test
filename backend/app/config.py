from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    database_url: str = "sqlite:///./import_service.db"
    postgres_url: Optional[str] = None
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # External API
    dummyjson_base_url: str = "https://dummyjson.com"
    
    # Simulation settings
    simulate_delay_seconds: float = 2.0
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
