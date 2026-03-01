from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..core.security import get_current_player
from ..models import Submission, Match, MatchStatus, SubmissionStatus
from ..schemas.submission_schema import (
    CodeSubmissionRequest,
    SubmissionResponse,
    SubmissionDetailResponse,
    SubmissionListResponse
)
from ..services.judge_service import JudgeService
from ..services.integrity_service import IntegrityService

logger = logging.getLogger(__name__)
router = APIRouter()

judge_service = JudgeService()
integrity_service = IntegrityService()

def process_submission_background(submission_id: str):
    """Background task to judge code and run integrity checks."""
    from ..core.database import SessionLocal
    db = SessionLocal()
    try:
        judge_service.evaluate_submission(db, submission_id)
        integrity_service.analyze_submission(db, submission_id)
    finally:
        db.close()

def _submission_to_dict(s: Submission) -> dict:
    """Convert a Submission model to a response dict safely."""
    return {
        "submission_id": s.id,
        "match_id": s.match_id,
        "player_id": s.player_id,
        "code": s.code,
        "language": s.language.value if hasattr(s.language, 'value') else s.language,
        "status": s.status.value if hasattr(s.status, 'value') else s.status,
        "test_cases_passed": s.test_cases_passed,
        "total_test_cases": s.test_cases_total,
        "execution_time_ms": s.execution_time_ms,
        "memory_used_mb": s.memory_used_mb,
        "ai_quality_score": s.ai_quality_score,
        "complexity_score": s.complexity_score,
        "ai_assisted_probability": s.cheat_probability,
        "score": 0,  # Placeholder for Elo impact, to be implemented after match resolution
        "created_at": s.submitted_at,
        "completed_at": s.completed_at,
    }

@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_code(
    request: CodeSubmissionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Submit code for a match."""
    
    match = db.query(Match).filter(Match.id == request.match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    if match.player1_id != current_user["id"] and match.player2_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this match")
    
    if match.status != MatchStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match is not active (status: {match.status.value})"
        )
    
    existing_submissions = db.query(Submission).filter(
        Submission.match_id == request.match_id,
        Submission.player_id == current_user["id"]
    ).count()

    submission = Submission(
        match_id=request.match_id,
        player_id=current_user["id"],
        code=request.code,
        language=request.language,
        status=SubmissionStatus.PENDING,
        submission_number=existing_submissions + 1,
        test_cases_passed=0,
        test_cases_total=0
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    background_tasks.add_task(process_submission_background, submission.id)
    logger.info(f"Submission created: {submission.id} for player {current_user['id']}")
    
    return _submission_to_dict(submission)

@router.get("/{submission_id}", response_model=SubmissionDetailResponse)
async def get_submission(
    submission_id: str,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get submission details."""
    
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    
    if submission.player_id != current_user["id"]:
        match = db.query(Match).filter(Match.id == submission.match_id).first()
        if not match or (match.player1_id != current_user["id"] and match.player2_id != current_user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this submission")
    
    result = _submission_to_dict(submission)
    result["test_case_results"] = []
    result["error_details"] = submission.error_message
    return result

@router.get("/match/{match_id}", response_model=SubmissionListResponse)
async def get_match_submissions(
    match_id: str,
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """Get all submissions for a match."""
    
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    if match.player1_id != current_user["id"] and match.player2_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this match")
    
    submissions = db.query(Submission).filter(Submission.match_id == match_id).all()
    
    return {
        "submissions": [_submission_to_dict(s) for s in submissions],
        "total_count": len(submissions)
    }