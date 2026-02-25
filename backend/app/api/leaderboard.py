from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..core.security import get_current_player
from ..models import Player
from ..schemas.player_schema import (
    PlayerLeaderboardEntry,
    PlayerStatsResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/global")
async def get_global_leaderboard(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get global leaderboard sorted by rating."""
    
    if limit > 1000:
        limit = 1000
    if offset < 0:
        offset = 0
    
    players = db.query(Player).order_by(Player.current_rating.desc()).limit(limit).offset(offset).all()
    
    leaderboard = []
    for rank, player in enumerate(players, offset + 1):
        leaderboard.append({
            "rank": rank,
            "player_id": player.id,
            "username": player.username,
            "current_rating": player.current_rating,
            "matches_played": player.matches_played,
            "wins": player.wins,
            "win_rate": round(player.win_rate, 2) if player.win_rate else 0.0
        })
    
    return {
        "leaderboard": leaderboard,
        "total": len(leaderboard),
        "limit": limit,
        "offset": offset
    }

@router.get("/player/{player_id}")
async def get_player_stats(
    player_id: str,
    db: Session = Depends(get_db)
):
    """Get player statistics."""
    
    player = db.query(Player).filter(Player.id == player_id).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    return {
        "player_id": player.id,
        "username": player.username,
        "current_rating": player.current_rating,
        "rating_confidence": player.rating_confidence,
        "matches_played": player.matches_played,
        "wins": player.wins,
        "losses": player.losses,
        "win_rate": round(player.win_rate, 2) if player.win_rate else 0.0,
        "average_match_duration_seconds": 0,  # TODO: Calculate from match history
        "badges_earned": len(player.badges) if player.badges else 0,
        "tournaments_participated": 0,  # TODO: Calculate from tournament history
        "best_rating": player.current_rating,  # TODO: Track best rating
        "worst_rating": player.current_rating,  # TODO: Track worst rating
        "created_at": player.created_at
    }

@router.get("/me/stats")
async def get_my_stats(
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get current player's statistics."""
    
    player = db.query(Player).filter(Player.id == current_user["id"]).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Get player rank
    rank = db.query(Player).filter(Player.current_rating > player.current_rating).count() + 1
    
    return {
        "rank": rank,
        "player_id": player.id,
        "username": player.username,
        "current_rating": player.current_rating,
        "rating_confidence": player.rating_confidence,
        "matches_played": player.matches_played,
        "wins": player.wins,
        "losses": player.losses,
        "win_rate": round(player.win_rate, 2) if player.win_rate else 0.0,
        "badges_earned": len(player.badges) if player.badges else 0,
        "created_at": player.created_at
    }