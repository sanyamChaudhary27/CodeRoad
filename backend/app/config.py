from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(env_file)

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Code Road"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/coderoad"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    # Match settings
    MATCHMAKING_TIMEOUT_SECONDS: int = 60
    MATCH_DURATION_MIN_SECONDS: int = 30
    MATCH_DURATION_MAX_SECONDS: int = 120
    ELO_MATCHING_RANGE: int = 200
    ELO_K_FACTOR: int = 32
    INITIAL_ELO_RATING: int = 1200
    
    # Code execution
    CODE_EXECUTION_TIMEOUT_SECONDS: int = 5
    CODE_MEMORY_LIMIT_MB: int = 256
    CODE_CPU_LIMIT: int = 1
    
    # ML Service URLs (Gajendra's team)
    CHALLENGE_SERVICE_URL: str = os.getenv("CHALLENGE_SERVICE_URL", "http://localhost:8001")
    JUDGE_SERVICE_URL: str = os.getenv("JUDGE_SERVICE_URL", "http://localhost:8002")
    INTEGRITY_SERVICE_URL: str = os.getenv("INTEGRITY_SERVICE_URL", "http://localhost:8003")
    
    # WebSocket
    WEBSOCKET_PING_INTERVAL: int = 20
    WEBSOCKET_PING_TIMEOUT: int = 40
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD_SECONDS: int = 60
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Create settings instance
settings = Settings()