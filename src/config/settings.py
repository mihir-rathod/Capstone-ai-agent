from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Pydantic settings class for environment variables and configuration"""
    # Database configs
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "capstone"
    MYSQL_PASSWORD: str 
    MYSQL_DATABASE: str = "capstone"

    # MongoDB configs
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "capstone_reports"
    
    # API Keys
    GOOGLE_API_KEY: str
    OLLAMA_API_KEY: str
    
    # API Endpoints
    OLLAMA_API_URL: str = "http://localhost:11434"
    
    # Model Settings
    MAX_RETRIES: int = 3
    PARALLEL_GENERATION: bool = True
    GENERATION_TIMEOUT: int = 30
    
    # AWS Settings (for S3 only)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: Optional[str] = "us-east-2"
    
    # Email Settings (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SENDER_EMAIL: Optional[str] = "noreply@example.com"

    # Validation Settings
    MIN_CONSISTENCY_SCORE: float = 0.8
    REQUIRE_DUAL_VALIDATION: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
