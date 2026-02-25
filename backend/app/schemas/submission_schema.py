from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CodeSubmissionRequest(BaseModel):
    """Request model for code submission."""
    match_id: str = Field(..., description="ID of the match")
    code: str = Field(..., description="Source code to submit")
    language: str = Field(..., description="Programming language (python, cpp, java, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "match_id": "match_123",
                "code": "def solution(n):\n    return n * 2",
                "language": "python"
            }
        }

class TestCaseResult(BaseModel):
    """Result of a single test case."""
    test_case_id: str
    passed: bool
    expected_output: str
    actual_output: str
    error_message: Optional[str] = None

class SubmissionResponse(BaseModel):
    """Response model for code submission."""
    submission_id: str
    match_id: str
    player_id: str
    code: str
    language: str
    status: str  # pending, judging, completed, failed
    test_cases_passed: int
    total_test_cases: int
    execution_time_ms: Optional[float] = None
    memory_used_mb: Optional[float] = None
    ai_quality_score: Optional[float] = None  # 0-100
    complexity_score: Optional[float] = None  # 0-100
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SubmissionDetailResponse(SubmissionResponse):
    """Detailed submission response with test case results."""
    test_case_results: List[TestCaseResult] = []
    error_details: Optional[str] = None
    
    class Config:
        from_attributes = True

class SubmissionListResponse(BaseModel):
    """List of submissions for a match."""
    submissions: List[SubmissionResponse]
    total_count: int
    
    class Config:
        from_attributes = True
