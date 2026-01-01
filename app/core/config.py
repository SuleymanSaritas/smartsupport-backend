"""Application configuration and settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_KEY: str
    API_V1_PREFIX: str = "/api/v1"
    
    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Celery Configuration
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Model Configuration
    TURKISH_MODEL: str = "yeniguno/bert-uncased-turkish-intent-classification"  # Not used - translation layer instead
    ENGLISH_MODEL: str = "philschmid/BERT-Banking77"  # Official Banking77 model - correct repository name
    
    # Application Settings
    PROJECT_NAME: str = "SmartSupport Backend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate Celery URLs if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()




