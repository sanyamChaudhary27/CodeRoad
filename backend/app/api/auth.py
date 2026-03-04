from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..config import settings
from ..core.security import (
    get_password_hash,
    verify_password,
    create_player_token,
    validate_password_strength,
    get_current_player
)
from ..models import Player
from ..schemas.player_schema import (
    PlayerRegister,
    PlayerLogin,
    PlayerResponse,
    TokenResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(player_data: PlayerRegister, db: Session = Depends(get_db)):
    """Register a new player."""
    
    # Validate password strength
    is_valid, message = validate_password_strength(player_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check if username already exists
    existing_user = db.query(Player).filter(Player.username == player_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(Player).filter(Player.email == player_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new player
    hashed_password = get_password_hash(player_data.password)
    new_player = Player(
        username=player_data.username,
        email=player_data.email,
        hashed_password=hashed_password,
        current_rating=settings.INITIAL_ELO_RATING,
        rating_confidence=100.0
    )
    
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    
    logger.info(f"New player registered: {new_player.username}")
    
    # Create token
    token = create_player_token(new_player.id, new_player.username, new_player.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "player": new_player
    }

@router.post("/login", response_model=TokenResponse)
async def login(credentials: PlayerLogin, db: Session = Depends(get_db)):
    """Login a player."""
    
    # Find player by email
    player = db.query(Player).filter(Player.email == credentials.email).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, player.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info(f"Player logged in: {player.username}")
    
    # Create token
    token = create_player_token(player.id, player.username, player.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "player": player
    }

@router.get("/me", response_model=PlayerResponse)
async def get_me(
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get current player information."""
    
    player = db.query(Player).filter(Player.id == current_user["id"]).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    return {
        "id": player.id,
        "username": player.username,
        "email": player.email,
        "current_rating": player.current_rating,
        "rating_confidence": player.rating_confidence,
        "matches_played": player.matches_played,
        "wins": player.wins,
        "losses": player.losses,
        "badges_earned": len(player.badges) if player.badges else 0,
        "created_at": player.created_at,
        "last_match_at": player.last_match_at,
        "profile_picture": player.profile_picture,
        "debug_rating": player.debug_rating,
        "debug_matches_played": player.debug_matches_played,
        "debug_wins": player.debug_wins,
        "debug_losses": player.debug_losses
    }

@router.put("/profile-picture")
async def update_profile_picture(
    data: dict,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Update player profile picture."""
    
    player = db.query(Player).filter(Player.id == current_user["id"]).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    profile_picture = data.get("profile_picture", "")
    
    # Validate profile picture (basic validation for base64 or URL)
    if not profile_picture:
        player.profile_picture = None
    elif len(profile_picture) > 500000:  # 500KB limit for base64
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile picture too large (max 500KB)"
        )
    else:
        player.profile_picture = profile_picture
    
    db.commit()
    db.refresh(player)
    
    logger.info(f"Profile picture updated for player: {player.username}")
    
    return {
        "message": "Profile picture updated successfully",
        "profile_picture": player.profile_picture
    }