from pydantic_settings import BaseSettings, SettingsConfigDict
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

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = "Code Road"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./coderoad.db"
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
        "https://coderoad.online",
        "https://www.coderoad.online",
        "http://coderoad.online",
        "http://www.coderoad.online",
        "https://code-road-7mvbpv7st-sanyamchaudhary27s-projects.vercel.app",
        "https://code-road-inline-vercel.app",
        "https://coderoad-gmq6.onrender.com",
    ]
    
    # Match settings
    MATCHMAKING_TIMEOUT_SECONDS: int = 60
    MATCH_DURATION_MIN_SECONDS: int = 30
    MATCH_DURATION_MAX_SECONDS: int = 120
    ELO_MATCHING_RANGE: int = 200
    ELO_K_FACTOR: int = 32
    INITIAL_ELO_RATING: int = 300
    
    # Debug Arena settings
    DEBUG_SOLO_TIME_LIMIT: int = 300  # 5 minutes
    DEBUG_1V1_TIME_LIMIT: int = 150  # 2.5 minutes
    DEBUG_INITIAL_RATING: int = 300
    
    # Code execution
    CODE_EXECUTION_TIMEOUT_SECONDS: int = 5
    CODE_MEMORY_LIMIT_MB: int = 256
    CODE_CPU_LIMIT: int = 1

    # Isolated code execution. CodeRoad never executes player code in the API
    # process. Configure a separately hosted Judge0 instance for submissions.
    JUDGE0_API_URL: str = (
        os.getenv("JUDGE0_API_URL") or "https://ce.judge0.com"
    ).rstrip("/")
    JUDGE0_AUTH_TOKEN: Optional[str] = os.getenv("JUDGE0_AUTH_TOKEN") or None
    JUDGE0_AUTH_HEADER: str = os.getenv("JUDGE0_AUTH_HEADER", "X-Auth-Token")
    JUDGE0_PYTHON_LANGUAGE_ID: int = int(os.getenv("JUDGE0_PYTHON_LANGUAGE_ID", "71"))

    # NVIDIA NIM powers optional hypothesis generation. Candidate
    # counterexamples still have to pass deterministic validation and isolated
    # execution.
    NVIDIA_NIM_KEY: Optional[str] = os.getenv("NVIDIA_NIM_KEY") or None
    NVIDIA_NIM_BASE_URL: str = os.getenv(
        "NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"
    ).rstrip("/")
    NVIDIA_NIM_MODEL: str = os.getenv(
        "NVIDIA_NIM_MODEL", "deepseek-ai/deepseek-v4-pro"
    )
    NVIDIA_NIM_TIMEOUT_SECONDS: float = float(
        os.getenv("NVIDIA_NIM_TIMEOUT_SECONDS", "20")
    )
    NVIDIA_NIM_CACHE_MAX_ENTRIES: int = int(
        os.getenv("NVIDIA_NIM_CACHE_MAX_ENTRIES", "128")
    )
    ATTACK_ROUND_MAX_CANDIDATES: int = int(os.getenv("ATTACK_ROUND_MAX_CANDIDATES", "12"))
    ATTACK_ROUND_EXECUTION_WORKERS: int = int(os.getenv("ATTACK_ROUND_EXECUTION_WORKERS", "4"))
    
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
    
# Create settings instance
settings = Settings()
