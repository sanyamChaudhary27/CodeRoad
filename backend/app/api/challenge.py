"""
Challenge API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..core.database import get_db
from ..core.security import get_current_player
from ..models.player import Player
from ..services.challenge_service import get_challenge_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/challenges", tags=["challenges"])


class ChallengeRequest(BaseModel):
    """Request model for challenge generation"""
    difficulty: Optional[str] = "intermediate"
    domain: Optional[str] = None


class ChallengeResponse(BaseModel):
    """Response model for challenge"""
    id: str
    title: str
    description: str
    difficulty: str
    domain: str
    constraints: dict
    input_format: str
    output_format: str
    example_input: Optional[str]
    example_output: Optional[str]
    time_limit_seconds: int
    boilerplate_code: str
    test_cases: list
    coverage_metrics: Optional[dict]
    generated_at: str


@router.post("/generate", response_model=ChallengeResponse)
async def generate_challenge(
    request: ChallengeRequest,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Generate a new AI-powered coding challenge
    
    - Generates challenge based on player rating and difficulty
    - Creates comprehensive test cases using AI
    - Returns challenge with test cases (some hidden)
    """
    
    try:
        challenge_service = get_challenge_service()
        
        # Get player rating for adaptive difficulty
        player_rating = current_user.get("rating", 1200) if isinstance(current_user, dict) else 1200
        player_id = current_user.get("id") if isinstance(current_user, dict) else None
        
        # Generate challenge and persist to DB
        challenge = challenge_service.generate_challenge(
            db=db,
            difficulty=request.difficulty,
            player_rating=player_rating,
            domain=request.domain,
            player_id=player_id
        )
        
        logger.info(f"Generated challenge {challenge['id']} for player {current_user.get('id', 'unknown')}")
        
        return challenge
        
    except Exception as e:
        logger.error(f"Failed to generate challenge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate challenge: {str(e)}"
        )


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: str,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    Retrieve a challenge by ID
    
    - Returns challenge details
    - Hides some test cases for fairness
    """
    
    try:
        challenge_service = get_challenge_service()
        challenge = challenge_service.get_challenge_by_id(challenge_id, db)
        
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Challenge {challenge_id} not found"
            )
        
        return challenge
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve challenge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve challenge: {str(e)}"
        )


@router.get("/", response_model=list[ChallengeResponse])
async def list_challenges(
    difficulty: Optional[str] = None,
    domain: Optional[str] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    List available challenges
    
    - Filter by difficulty and domain
    - Returns paginated results
    """
    
    # TODO: Implement database query when Challenge model is created
    logger.warning("Challenge listing not yet implemented")
    return []
