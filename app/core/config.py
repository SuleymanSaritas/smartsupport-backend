"""Application configuration and settings."""
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_KEY: str = "CHANGE_ME_IN_PRODUCTION"  # Default for Cloud Run - MUST be set in production
    API_V1_PREFIX: str = "/api/v1"
    
    # Redis Configuration
    REDIS_HOST: str = "redis"  # Default for local Docker Compose
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
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables to prevent crashes
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Warn if using default API_KEY (security risk in production)
        if self.API_KEY == "CHANGE_ME_IN_PRODUCTION":
            logger.warning(
                "⚠️  WARNING: Using default API_KEY. This is INSECURE for production! "
                "Please set API_KEY environment variable in Cloud Run."
            )
        
        # Auto-generate Celery URLs if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Initialize settings - will not crash if environment variables are missing
try:
    settings = Settings()
    logger.info("Settings loaded successfully")
except Exception as e:
    logger.error(f"Failed to load settings: {str(e)}")
    # Create settings with all defaults as fallback
    settings = Settings(
        API_KEY="CHANGE_ME_IN_PRODUCTION",
        REDIS_HOST="redis",
        REDIS_PORT=6379,
        REDIS_DB=0
    )
    logger.warning("Using fallback default settings")




