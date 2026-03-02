from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from ..core.database import Base

class SubmissionStatus(str, enum.Enum):
    """Submission status enumeration."""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    COMPILE_ERROR = "compile_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    SECURITY_VIOLATION = "security_violation"

class ProgrammingLanguage(str, enum.Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    # Add more languages as needed

class Submission(Base):
    """Code submission model."""
    
    __tablename__ = "submissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False, index=True)
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False, index=True)
    
    # Submission details
    code = Column(Text, nullable=False)
    language = Column(Enum(ProgrammingLanguage), nullable=False)
    submission_number = Column(Integer, nullable=False)  # 1st, 2nd, 3rd submission in this match
    
    # Status and results
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    is_final = Column(Boolean, default=False, nullable=False)  # Final submission used for scoring
    
    # Test case results
    test_cases_passed = Column(Integer, default=0, nullable=False)
    test_cases_total = Column(Integer, default=0, nullable=False)
    
    @property
    def test_case_score(self) -> float:
        """Calculate test case score percentage."""
        if self.test_cases_total == 0:
            return 0.0
        return (self.test_cases_passed / self.test_cases_total) * 100
    
    # Execution metrics
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    cpu_time_ms = Column(Integer, nullable=True)
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_type = Column(String(50), nullable=True)
    
    # AI evaluation
    ai_quality_score = Column(Float, nullable=True)  # 0-100
    complexity_score = Column(Float, nullable=True)  # 0-100
    ai_feedback = Column(Text, nullable=True)
    
    # Integrity analysis
    integrity_analysis_id = Column(String(36), ForeignKey("integrity_analysis.id"), nullable=True, index=True)
    cheat_probability = Column(Float, nullable=True)  # 0-100%
    integrity_status = Column(String(50), nullable=True)  # 'legitimate', 'ai_assisted', 'pasted'
    integrity_confidence = Column(Float, nullable=True)  # 0-1.0 confidence score
    integrity_model_used = Column(String(50), nullable=True)  # 'xgboost', 'gemini', etc.
    
    # Behavioral metrics for AI detection
    time_to_first_submission = Column(Integer, nullable=True)  # Seconds from match start to first submission
    time_between_submissions = Column(Integer, nullable=True)  # Average seconds between submissions
    total_submission_time = Column(Integer, nullable=True)  # Total time spent on submissions
    code_paste_probability = Column(Float, nullable=True)  # 0-100% probability of paste detection
    
    # Code characteristics for classification
    code_length = Column(Integer, nullable=True)  # Number of characters in code
    code_lines = Column(Integer, nullable=True)  # Number of lines in code
    unique_tokens = Column(Integer, nullable=True)  # Number of unique tokens
    comment_ratio = Column(Float, nullable=True)  # Ratio of comments to code
    indentation_consistency = Column(Float, nullable=True)  # 0-100% consistency score
    variable_naming_style = Column(String(50), nullable=True)  # "camelCase", "snake_case", "mixed"
    
    # Keystroke dynamics (for paste detection)
    keystroke_speed_avg = Column(Float, nullable=True)  # Average characters per second
    keystroke_speed_variance = Column(Float, nullable=True)  # Variance in keystroke speed
    copy_paste_events = Column(Integer, default=0, nullable=False)  # Number of detected copy/paste events
    deletion_ratio = Column(Float, nullable=True)  # Ratio of deletions to total keystrokes
    pasted_code_ratio = Column(Float, nullable=True)  # Estimated ratio of pasted vs typed code
    external_source_similarity = Column(Float, nullable=True)  # Similarity to known online solutions
    
    # Performance metrics
    success_rate = Column(Float, nullable=True)  # Ratio of successful to total submissions
    efficiency_vs_player_avg = Column(Float, nullable=True)  # Efficiency compared to player average
    
    # Submission pattern metrics
    submission_count_in_match = Column(Integer, default=1, nullable=False)  # How many times submitted
    time_to_solve = Column(Integer, nullable=True)  # Time from match start to final submission
    iterations_to_solution = Column(Integer, nullable=True)  # Number of attempts before correct solution
    
    # Timestamps
    submitted_at = Column(DateTime, default=func.now(), nullable=False)
    executed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="submissions")
    player = relationship("Player", back_populates="submissions")
    
    def __repr__(self):
        return f"<Submission(id={self.id}, match={self.match_id}, player={self.player_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert submission to dictionary for API responses."""
        return {
            "id": self.id,
            "match_id": self.match_id,
            "player_id": self.player_id,
            "code": self.code,
            "language": self.language.value,
            "submission_number": self.submission_number,
            "status": self.status.value,
            "is_final": self.is_final,
            "test_cases_passed": self.test_cases_passed,
            "test_cases_total": self.test_cases_total,
            "test_case_score": self.test_case_score,
            "execution_time_ms": self.execution_time_ms,
            "memory_used_mb": self.memory_used_mb,
            "cpu_time_ms": self.cpu_time_ms,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "ai_quality_score": self.ai_quality_score,
            "complexity_score": self.complexity_score,
            "ai_feedback": self.ai_feedback,
            "cheat_probability": self.cheat_probability,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

class Challenge(Base):
    """Challenge model (provided by ML team)."""
    
    __tablename__ = "challenges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Challenge details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)  # Problem statement
    difficulty = Column(String(20), nullable=False)  # "beginner", "intermediate", "advanced"
    domain = Column(String(50), nullable=False)  # "algorithms", "arrays", "strings", etc.
    
    # Input/output formats
    input_format = Column(Text, nullable=False)
    output_format = Column(Text, nullable=False)
    example_input = Column(Text, nullable=True)
    example_output = Column(Text, nullable=True)
    
    # Constraints & Time
    constraints = Column(Text, nullable=False)  # JSON string of dict
    time_limit_seconds = Column(Integer, default=5, nullable=False)
    memory_limit_mb = Column(Integer, default=256, nullable=False)
    
    # Boilerplate & Tests
    boilerplate_code = Column(Text, nullable=True)
    test_cases = Column(Text, nullable=False)  # JSON string of list
    
    # AI generation metadata
    generated_by_ai = Column(Boolean, default=True, nullable=False)
    coverage_metrics = Column(Text, nullable=True) # JSON string
    
    # Usage statistics
    times_used = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Challenge(id={self.id}, title={self.title}, difficulty={self.difficulty})>"
    
    def to_dict(self):
        """Convert challenge to dictionary for API responses."""
        import json
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "domain": self.domain,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "example_input": self.example_input,
            "example_output": self.example_output,
            "constraints": json.loads(self.constraints) if self.constraints else {},
            "time_limit_seconds": self.time_limit_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "boilerplate_code": self.boilerplate_code,
            "test_cases": json.loads(self.test_cases) if self.test_cases else [],
            "coverage_metrics": json.loads(self.coverage_metrics) if self.coverage_metrics else {},
            "generated_at": self.created_at.isoformat() if self.created_at else None,
        }

class TestCase(Base):
    """Individual test case for challenges."""
    
    __tablename__ = "test_cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String(36), ForeignKey("challenges.id"), nullable=False, index=True)
    
    # Test case data
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    
    # Metadata
    is_hidden = Column(Boolean, default=False, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)  # Weight for scoring
    description = Column(String(200), nullable=True)
    
    # Relationships
    challenge = relationship("Challenge")
    
    def __repr__(self):
        return f"<TestCase(id={self.id}, challenge={self.challenge_id}, hidden={self.is_hidden})>"