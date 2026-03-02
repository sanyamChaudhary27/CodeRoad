from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..core.security import get_current_player
from ..services.match_service import MatchService
from ..models import Match
from ..schemas.match_schema import (
    QueueJoinRequest,
    QueueStatusResponse,
    MatchResponse,
    MatchListResponse,
    PlayerDoneRequest,
    MatchConclusionResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/queue/join", response_model=QueueStatusResponse)
async def join_queue(
    request: QueueJoinRequest,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Join matchmaking queue."""
    
    match_service = MatchService(db)
    result = match_service.join_match_queue(current_user["id"], request.preferred_format)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    logger.info(f"Player {current_user['id']} joined queue")
    
    return {
        "player_id": current_user["id"],
        "in_queue": result.get("in_queue", True),
        "queue_position": result.get("queue_position"),
        "wait_time_seconds": result.get("wait_time_seconds"),
        "estimated_opponent_rating": result.get("estimated_opponent_rating")
    }

@router.post("/queue/leave", response_model=dict)
async def leave_queue(
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Leave matchmaking queue."""
    
    match_service = MatchService(db)
    result = match_service.leave_match_queue(current_user["id"])
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    logger.info(f"Player {current_user['id']} left queue")
    
    return {
        "status": "left_queue",
        "message": "Successfully left matchmaking queue"
    }

@router.get("/queue/status", response_model=QueueStatusResponse)
async def get_queue_status(
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get matchmaking queue status."""
    
    match_service = MatchService(db)
    result = match_service.get_queue_status_with_matchmaking(current_user["id"])
    
    return result

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get match details."""
    
    match_service = MatchService(db)
    match_data = match_service.get_match(match_id)
    
    if not match_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify user is part of the match
    if match_data.get("player1_id") != current_user["id"] and match_data.get("player2_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this match"
        )
    
    return {
        "match_id": match_data.get("id"),
        "status": match_data.get("status"),
        "format": match_data.get("match_format", "1v1"),
        "player1": {
            "player_id": match_data.get("player1_id"),
            "username": match_data.get("player1_username", "Unknown"),
            "current_rating": match_data.get("player1_rating", 1200),
            "submissions_count": match_data.get("player1_submissions", 0),
            "is_done": match_data.get("player1_done", False)
        },
        "player2": {
            "player_id": match_data.get("player2_id"),
            "username": match_data.get("player2_username", "Unknown"),
            "current_rating": match_data.get("player2_rating", 1200),
            "submissions_count": match_data.get("player2_submissions", 0),
            "is_done": match_data.get("player2_done", False)
        } if match_data.get("player2_id") else None,
        "challenge_id": match_data.get("challenge_id"),
        "challenge_title": match_data.get("challenge_title"),
        "challenge_description": match_data.get("challenge_description"),
        "difficulty_level": match_data.get("difficulty_level"),
        "time_limit_seconds": match_data.get("time_limit_seconds", 120),
        "time_remaining": match_data.get("time_remaining", 120),
        "created_at": match_data.get("created_at"),
        "started_at": match_data.get("started_at"),
        "concluded_at": match_data.get("ended_at"),
        "winner_id": match_data.get("winner_id"),
        "player1_score": match_data.get("player1_score"),
        "player2_score": match_data.get("player2_score"),
        "result": match_data.get("result")
    }

@router.get("/player/history", response_model=MatchListResponse)
async def get_player_matches(
    limit: int = 50,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get player's match history."""
    
    match_service = MatchService(db)
    matches_data = match_service.get_player_matches(current_user["id"], limit)
    
    matches = []
    for match_data in matches_data:
        matches.append({
            "match_id": match_data.get("id"),
            "status": match_data.get("status"),
            "format": match_data.get("format", "1v1"),
            "player1": {
                "player_id": match_data.get("player1_id"),
                "username": match_data.get("player1_username", "Unknown"),
                "current_rating": match_data.get("player1_rating", 1200),
                "submissions_count": match_data.get("player1_submissions", 0),
                "is_done": match_data.get("player1_done", False)
            },
            "player2": {
                "player_id": match_data.get("player2_id"),
                "username": match_data.get("player2_username", "Unknown"),
                "current_rating": match_data.get("player2_rating", 1200),
                "submissions_count": match_data.get("player2_submissions", 0),
                "is_done": match_data.get("player2_done", False)
            } if match_data.get("player2_id") else None,
            "challenge_id": match_data.get("challenge_id"),
            "challenge_title": match_data.get("challenge_title"),
            "challenge_description": match_data.get("challenge_description"),
            "difficulty_level": match_data.get("difficulty_level"),
            "time_limit_seconds": match_data.get("time_limit_seconds", 120),
            "time_remaining": match_data.get("time_remaining", 120),
            "created_at": match_data.get("created_at"),
            "started_at": match_data.get("started_at"),
            "concluded_at": match_data.get("concluded_at"),
            "winner_id": match_data.get("winner_id"),
            "player1_score": match_data.get("player1_score"),
            "player2_score": match_data.get("player2_score"),
            "result": match_data.get("result")
        })
    
    return {
        "matches": matches,
        "total_count": len(matches)
    }

@router.post("/{match_id}/done", response_model=dict)
async def player_done(
    match_id: str,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Signal that player is done with submissions."""
    
    # Verify match exists and user is in it
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    if match.player1_id != current_user["id"] and match.player2_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this match"
        )
    
    match_service = MatchService(db)
    result = match_service.player_done(match_id, current_user["id"])
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    logger.info(f"Player {current_user['id']} marked done in match {match_id}")
    
    return {
        "status": "done_recorded",
        "match_status": result.get("match_status"),
        "message": "Your done status has been recorded"
    }

@router.post("/practice", response_model=dict)
async def practice_match(
    difficulty: str = "intermediate",
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Create a solo practice match."""
    match_service = MatchService(db)
    result = match_service.create_solo_match(current_user["id"], difficulty)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result