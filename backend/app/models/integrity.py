from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base

class IntegrityAnalysis(Base):
    """AI-assisted integrity analysis for submissions."""
    
    __tablename__ = "integrity_analysis"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String(36), ForeignKey("submissions.id"), nullable=False, unique=True, index=True)
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False, index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False, index=True)
    
    # Analysis scores (0-100)
    stylometry_score = Column(Float, nullable=True)  # Deviation from player's style
    llm_probability_score = Column(Float, nullable=True)  # AI-generated probability
    behavioral_anomaly_score = Column(Float, nullable=True)  # Behavioral deviation
    
    # Aggregated score
    overall_cheat_probability = Column(Float, nullable=False)  # 0-100%
    
    # Threshold-based flags
    flagged = Column(Boolean, default=False, nullable=False)
    threshold_level = Column(String(20), nullable=True)  # "soft" (70-85%), "hard" (≥85%)
    
    # Review status
    reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(String(36), nullable=True)  # Admin ID
    review_notes = Column(Text, nullable=True)
    
    # Analysis details (stored as JSON)
    feature_extraction = Column(Text, nullable=True)  # Extracted code features
    comparison_data = Column(Text, nullable=True)  # Comparison with historical data
    anomaly_details = Column(Text, nullable=True)  # Specific anomalies detected
    
    # Model metadata
    model_version = Column(String(50), nullable=True)
    analysis_duration_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    submission = relationship("Submission", foreign_keys=[submission_id])
    player = relationship("Player", foreign_keys=[player_id])
    match = relationship("Match", foreign_keys=[match_id])
    
    def __repr__(self):
        return f"<IntegrityAnalysis(submission={self.submission_id}, probability={self.overall_cheat_probability}%, flagged={self.flagged})>"
    
    def to_dict(self):
        """Convert integrity analysis to dictionary for API responses."""
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "player_id": self.player_id,
            "match_id": self.match_id,
            "stylometry_score": self.stylometry_score,
            "llm_probability_score": self.llm_probability_score,
            "behavioral_anomaly_score": self.behavioral_anomaly_score,
            "overall_cheat_probability": self.overall_cheat_probability,
            "flagged": self.flagged,
            "threshold_level": self.threshold_level,
            "reviewed": self.reviewed,
            "reviewed_by": self.reviewed_by,
            "review_notes": self.review_notes,
            "model_version": self.model_version,
            "analysis_duration_ms": self.analysis_duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }

class PlayerIntegrityProfile(Base):
    """Integrity profile for each player."""
    
    __tablename__ = "player_integrity_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False, unique=True, index=True)
    
    # Confidence metrics
    rating_confidence = Column(Float, default=100.0, nullable=False)  # 0-100%
    style_consistency = Column(Float, default=100.0, nullable=False)  # 0-100%
    
    # Statistics
    total_submissions = Column(Integer, default=0, nullable=False)
    flagged_submissions = Column(Integer, default=0, nullable=False)
    clean_submissions = Column(Integer, default=0, nullable=False)
    
    # Historical data (stored as JSON)
    style_embeddings = Column(Text, nullable=True)  # Player's coding style embeddings
    behavioral_patterns = Column(Text, nullable=True)  # Behavioral patterns
    complexity_history = Column(Text, nullable=True)  # Historical complexity scores
    solve_time_history = Column(Text, nullable=True)  # Historical solve times
    
    # Flags and restrictions
    is_restricted = Column(Boolean, default=False, nullable=False)
    restriction_reason = Column(String(200), nullable=True)
    restriction_ends_at = Column(DateTime, nullable=True)
    
    # Appeal information
    appeals_filed = Column(Integer, default=0, nullable=False)
    appeals_successful = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_flagged_at = Column(DateTime, nullable=True)
    last_clean_at = Column(DateTime, nullable=True)
    
    # Relationships
    player = relationship("Player")
    
    def __repr__(self):
        return f"<PlayerIntegrityProfile(player={self.player_id}, confidence={self.rating_confidence}%)>"
    
    def to_dict(self):
        """Convert integrity profile to dictionary for API responses."""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "rating_confidence": self.rating_confidence,
            "style_consistency": self.style_consistency,
            "total_submissions": self.total_submissions,
            "flagged_submissions": self.flagged_submissions,
            "clean_submissions": self.clean_submissions,
            "is_restricted": self.is_restricted,
            "restriction_reason": self.restriction_reason,
            "restriction_ends_at": self.restriction_ends_at.isoformat() if self.restriction_ends_at else None,
            "appeals_filed": self.appeals_filed,
            "appeals_successful": self.appeals_successful,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_flagged_at": self.last_flagged_at.isoformat() if self.last_flagged_at else None,
            "last_clean_at": self.last_clean_at.isoformat() if self.last_clean_at else None,
        }

class IntegrityAuditLog(Base):
    """Audit log for all integrity-related actions."""
    
    __tablename__ = "integrity_audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Action details
    action_type = Column(String(50), nullable=False)  # "flag", "review", "appeal", "restriction"
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False, index=True)
    submission_id = Column(String(36), ForeignKey("submissions.id"), nullable=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=True)
    
    # Performed by
    performed_by = Column(String(36), nullable=True)  # "system" or admin ID
    performed_by_type = Column(String(20), nullable=False)  # "system", "admin", "player"
    
    # Action data (stored as JSON)
    action_data = Column(Text, nullable=False)  # Full action details
    previous_state = Column(Text, nullable=True)  # Previous state before action
    new_state = Column(Text, nullable=True)  # New state after action
    
    # Result
    result = Column(String(50), nullable=True)  # "success", "failure", "pending"
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    player = relationship("Player", foreign_keys=[player_id])
    submission = relationship("Submission", foreign_keys=[submission_id])
    match = relationship("Match", foreign_keys=[match_id])
    
    def __repr__(self):
        return f"<IntegrityAuditLog(action={self.action_type}, player={self.player_id}, result={self.result})>"
    
    def to_dict(self):
        """Convert audit log to dictionary for API responses."""
        return {
            "id": self.id,
            "action_type": self.action_type,
            "player_id": self.player_id,
            "submission_id": self.submission_id,
            "match_id": self.match_id,
            "performed_by": self.performed_by,
            "performed_by_type": self.performed_by_type,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }