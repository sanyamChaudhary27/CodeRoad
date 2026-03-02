from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class QueueJoinRequest(BaseModel):
    """Request to join matchmaking queue."""
    preferred_format: str = Field(default="1v1", description="Match format (1v1, 2v2, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "preferred_format": "1v1"
            }
        }

class QueueStatusResponse(BaseModel):
    """Response for queue status."""
    player_id: str
    in_queue: bool
    queue_position: Optional[int] = None
    wait_time_seconds: Optional[int] = None
    estimated_opponent_rating: Optional[int] = None
    match_id: Optional[str] = None

class PlayerMatchInfo(BaseModel):
    """Information about a player in a match."""
    player_id: str
    username: str
    current_rating: int
    submissions_count: int
    is_done: bool
    
    class Config:
        from_attributes = True

class RatingUpdateDetail(BaseModel):
    """Details of a single player's rating update."""
    rating_change: Optional[int] = None
    new_rating: Optional[int] = None

class RatingUpdates(BaseModel):
    """Rating updates for both players in a match."""
    player1: RatingUpdateDetail
    player2: Optional[RatingUpdateDetail] = None

class MatchResponse(BaseModel):
    """Response model for match details."""
    match_id: str
    status: str  # waiting, active, concluded
    format: str  # 1v1, 2v2, etc.
    player1: PlayerMatchInfo
    player2: Optional[PlayerMatchInfo] = None
    challenge_id: Optional[str] = None
    challenge_title: Optional[str] = None
    challenge_description: Optional[str] = None
    difficulty_level: Optional[str] = None  # easy, medium, hard
    time_limit_seconds: int = 120
    created_at: datetime
    started_at: Optional[datetime] = None
    concluded_at: Optional[datetime] = None
    winner_id: Optional[str] = None
    player1_score: Optional[float] = None
    player2_score: Optional[float] = None
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None
    result: Optional[str] = None
    rating_updates: Optional[RatingUpdates] = None
    
    class Config:
        from_attributes = True

class MatchListResponse(BaseModel):
    """List of matches for a player."""
    matches: List[MatchResponse]
    total_count: int
    
    class Config:
        from_attributes = True

class PlayerDoneRequest(BaseModel):
    """Request to signal player is done with submission."""
    match_id: str = Field(..., description="ID of the match")
    
    class Config:
        json_schema_extra = {
            "example": {
                "match_id": "match_123"
            }
        }

class MatchConclusionResponse(BaseModel):
    """Response when match concludes."""
    match_id: str
    status: str
    winner_id: Optional[str]
    player1_id: str
    player1_score: float
    player1_rating_change: int
    player2_id: str
    player2_score: float
    player2_rating_change: int
    result: Optional[str] = None
    concluded_at: datetime
    
    class Config:
        from_attributes = True
