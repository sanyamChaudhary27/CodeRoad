from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from typing import Optional

from .core.database import engine, Base, get_db
from .core.security import verify_token
from .api import auth, match, submission, leaderboard, websocket
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
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Code Road Backend...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Code Road API",
        description="Real-time competitive coding platform with AI-generated challenges",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
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
    app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "code-road-backend",
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to Code Road API",
            "version": "1.0.0",
            "docs": "/docs" if settings.DEBUG else None,
            "endpoints": {
                "auth": "/api/v1/auth",
                "matches": "/api/v1/matches",
                "submissions": "/api/v1/submissions",
                "leaderboard": "/api/v1/leaderboard",
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