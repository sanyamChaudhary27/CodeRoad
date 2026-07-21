from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from typing import Optional, List
import json
from fastapi.responses import JSONResponse

from .core.database import engine, Base, get_db
from .core.security import verify_token
from .api import auth, match, submission, leaderboard, websocket, challenge, attack_round, public
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting Code Road Backend...")
    
    if not settings.DEBUG and settings.SECRET_KEY == "your-secret-key-change-in-production":
        raise RuntimeError("SECRET_KEY must be configured outside development")

    # Schema creation is intentionally the only automatic database mutation.
    # Production data must be migrated through an authenticated, reviewed job.
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    if settings.NVIDIA_NIM_KEY:
        from .services.challenge_service import get_challenge_service

        challenge_service = get_challenge_service()
        for challenge_type in ("dsa", "debug"):
            challenge_service.prewarm_challenge(challenge_type, "beginner")
        logger.info("Scheduled NVIDIA NIM challenge prewarming")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Code Road Backend...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Code Road API",
        description="Real-time coding competition with deterministically verified adversarial tests",
        version="2.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Configure CORS - Harden for DEBUG mode
    origins = settings.CORS_ORIGINS
    if settings.DEBUG:
        origins = ["*"]
        logger.info("DEBUG mode: Allowing all origins for CORS")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Exception Handler for JSON responses
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global error: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    
    # Dependency to get current user from token
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """Validate JWT token and return user data."""
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(match.router, prefix="/api/v1/matches", tags=["Matches"])
    app.include_router(submission.router, prefix="/api/v1/submissions", tags=["Submissions"])
    app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["Leaderboard"])
    app.include_router(challenge.router, prefix="/api/v1", tags=["Challenges"])
    app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
    app.include_router(public.router, prefix="/api/v1", tags=["Public"])
    app.include_router(
        attack_round.router,
        prefix="/api/v1/attack-rounds",
        tags=["Adversarial Test Arena"],
    )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    @app.get("/api/v1/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "code-road-backend",
            "version": "2.0.0"
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to Code Road API",
            "version": "2.0.0",
            "docs": "/docs" if settings.DEBUG else None,
            "endpoints": {
                "auth": "/api/v1/auth",
                "matches": "/api/v1/matches",
                "submissions": "/api/v1/submissions",
                "leaderboard": "/api/v1/leaderboard",
                "challenges": "/api/v1/challenges",
                "attack_rounds": "/api/v1/attack-rounds",
                "websocket": "/ws"
            }
        }
    
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
