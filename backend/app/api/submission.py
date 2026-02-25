from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_player
from ..models import Submission, Match, Player
from ..schemas.submission_schema import (
    CodeSubmissionRequest,
    SubmissionResponse,
    SubmissionDetailResponse,
    SubmissionListResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_code(
    request: CodeSubmissionRequest,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Submit code for a match."""
    
    # Verify match exists and player is in it
    match = db.query(Match).filter(Match.id == request.match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify player is in the match
    if match.player1_id != current_user["id"] and match.player2_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this match"
        )
    
    # Verify match is active
    if match.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match is not active (status: {match.status})"
        )
    
    # Create submission
    submission = Submission(
        match_id=request.match_id,
        player_id=current_user["id"],
        code=request.code,
        language=request.language,
        status="pending",
        test_cases_passed=0,
        total_test_cases=0
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    logger.info(f"Submission created: {submission.id} for player {current_user['id']}")
    
    return {
        "submission_id": submission.id,
        "match_id": submission.match_id,
        "player_id": submission.player_id,
        "code": submission.code,
        "language": submission.language,
        "status": submission.status,
        "test_cases_passed": submission.test_cases_passed,
        "total_test_cases": submission.total_test_cases,
        "execution_time_ms": submission.execution_time_ms,
        "memory_used_mb": submission.memory_used_mb,
        "ai_quality_score": submission.ai_quality_score,
        "complexity_score": submission.complexity_score,
        "created_at": submission.created_at,
        "completed_at": submission.completed_at
    }

@router.get("/{submission_id}", response_model=SubmissionDetailResponse)
async def get_submission(
    submission_id: str,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get submission details."""
    
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Verify user has access to this submission
    if submission.player_id != current_user["id"]:
        # Check if user is opponent in the match
        match = db.query(Match).filter(Match.id == submission.match_id).first()
        if not match or (match.player1_id != current_user["id"] and match.player2_id != current_user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this submission"
            )
    
    return {
        "submission_id": submission.id,
        "match_id": submission.match_id,
        "player_id": submission.player_id,
        "code": submission.code,
        "language": submission.language,
        "status": submission.status,
        "test_cases_passed": submission.test_cases_passed,
        "total_test_cases": submission.total_test_cases,
        "execution_time_ms": submission.execution_time_ms,
        "memory_used_mb": submission.memory_used_mb,
        "ai_quality_score": submission.ai_quality_score,
        "complexity_score": submission.complexity_score,
        "created_at": submission.created_at,
        "completed_at": submission.completed_at,
        "test_case_results": [],
        "error_details": submission.error_details
    }

@router.get("/match/{match_id}", response_model=SubmissionListResponse)
async def get_match_submissions(
    match_id: str,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get all submissions for a match."""
    
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
    
    submissions = db.query(Submission).filter(Submission.match_id == match_id).all()
    
    return {
        "submissions": [
            {
                "submission_id": s.id,
                "match_id": s.match_id,
                "player_id": s.player_id,
                "code": s.code,
                "language": s.language,
                "status": s.status,
                "test_cases_passed": s.test_cases_passed,
                "total_test_cases": s.total_test_cases,
                "execution_time_ms": s.execution_time_ms,
                "memory_used_mb": s.memory_used_mb,
                "ai_quality_score": s.ai_quality_score,
                "complexity_score": s.complexity_score,
                "created_at": s.created_at,
                "completed_at": s.completed_at
            }
            for s in submissions
        ],
        "total_count": len(submissions)
    }