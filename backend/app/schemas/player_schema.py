from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class PlayerRegister(BaseModel):
    """Request model for player registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Strong password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "coder_pro",
                "email": "[email]",
                "password": "SecurePass123!"
            }
        }

class PlayerLogin(BaseModel):
    """Request model for player login."""
    email: EmailStr = Field(..., description="Registered email")
    password: str = Field(..., description="Account password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "[email]",
                "password": "SecurePass123!"
            }
        }

class PlayerResponse(BaseModel):
    """Response model for player information."""
    id: str
    username: str
    email: str
    current_rating: int
    rating_confidence: float
    matches_played: int
    wins: int
    losses: int
    badges_earned: int
    created_at: datetime
    last_match_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Response model for authentication."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    player: PlayerResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "player": {
                    "id": "player_123",
                    "username": "coder_pro",
                    "email": "[email]",
                    "current_rating": 1200,
                    "rating_confidence": 100.0,
                    "matches_played": 5,
                    "wins": 3,
                    "losses": 2,
                    "badges_earned": 2,
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_match_at": "2024-01-20T15:45:00Z"
                }
            }
        }

class PlayerStatsResponse(BaseModel):
    """Detailed player statistics."""
    player_id: str
    username: str
    current_rating: int
    rating_confidence: float
    matches_played: int
    wins: int
    losses: int
    win_rate: float
    average_match_duration_seconds: int
    badges_earned: int
    tournaments_participated: int
    best_rating: int
    worst_rating: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlayerLeaderboardEntry(BaseModel):
    """Player entry in leaderboard."""
    rank: int
    player_id: str
    username: str
    current_rating: int
    matches_played: int
    wins: int
    win_rate: float
    
    class Config:
        from_attributes = True
