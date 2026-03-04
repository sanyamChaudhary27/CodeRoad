from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base

class Rating(Base):
    """Rating model for tracking player ratings with confidence."""
    
    __tablename__ = "ratings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False, index=True)
    challenge_type = Column(String(20), default="dsa", nullable=False)  # "dsa" or "debug"
    
    # Current rating
    current_rating = Column(Integer, default=300, nullable=False)
    rating_confidence = Column(Float, default=100.0, nullable=False)  # 0-100%
    
    # Statistics
    matches_played = Column(Integer, default=0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    draws = Column(Integer, default=0, nullable=False)
    
    # Rating volatility
    rating_deviation = Column(Float, default=350.0, nullable=False)  # Glicko RD
    volatility = Column(Float, default=0.06, nullable=False)  # Glicko volatility
    
    # Peak rating
    peak_rating = Column(Integer, default=300, nullable=False)
    peak_rating_date = Column(DateTime, nullable=True)
    
    # Rating decay
    last_activity_date = Column(DateTime, default=func.now(), nullable=False)
    decay_applied = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    player = relationship("Player")
    history = relationship("RatingHistory", back_populates="rating")
    
    def __repr__(self):
        return f"<Rating(player={self.player_id}, rating={self.current_rating}, confidence={self.rating_confidence}%)>"
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100
    
    @property
    def is_active(self) -> bool:
        """Check if player is active (played within last 30 days)."""
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        return self.last_activity_date >= thirty_days_ago
    
    def to_dict(self):
        """Convert rating to dictionary for API responses."""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "current_rating": self.current_rating,
            "rating_confidence": self.rating_confidence,
            "matches_played": self.matches_played,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "win_rate": self.win_rate,
            "rating_deviation": self.rating_deviation,
            "volatility": self.volatility,
            "peak_rating": self.peak_rating,
            "peak_rating_date": self.peak_rating_date.isoformat() if self.peak_rating_date else None,
            "last_activity_date": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "decay_applied": self.decay_applied,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class RatingHistory(Base):
    """Historical rating changes with integrity tracking."""
    
    __tablename__ = "rating_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rating_id = Column(String(36), ForeignKey("ratings.id"), nullable=False, index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=True, index=True)
    
    # Rating change
    old_rating = Column(Integer, nullable=False)
    new_rating = Column(Integer, nullable=False)
    rating_change = Column(Integer, nullable=False)
    
    # Match details
    opponent_id = Column(String(36), nullable=True)
    opponent_rating = Column(Integer, nullable=True)
    match_result = Column(String(10), nullable=False)  # "win", "loss", "draw"
    
    # ELO calculation parameters
    k_factor = Column(Integer, default=32, nullable=False)
    expected_score = Column(Float, nullable=True)
    actual_score = Column(Float, nullable=True)
    
    # Integrity status
    integrity_status = Column(String(20), default="clean", nullable=False)  # "clean", "flagged", "frozen"
    cheat_probability = Column(Float, nullable=True)  # 0-100%
    rating_frozen = Column(Boolean, default=False, nullable=False)
    
    # Confidence impact
    confidence_before = Column(Float, nullable=True)
    confidence_after = Column(Float, nullable=True)
    confidence_change = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    rating = relationship("Rating", back_populates="history")
    match = relationship("Match", foreign_keys=[match_id])
    
    def __repr__(self):
        return f"<RatingHistory(rating={self.rating_id}, change={self.rating_change}, result={self.match_result})>"
    
    def to_dict(self):
        """Convert rating history to dictionary for API responses."""
        return {
            "id": self.id,
            "rating_id": self.rating_id,
            "match_id": self.match_id,
            "old_rating": self.old_rating,
            "new_rating": self.new_rating,
            "rating_change": self.rating_change,
            "opponent_id": self.opponent_id,
            "opponent_rating": self.opponent_rating,
            "match_result": self.match_result,
            "k_factor": self.k_factor,
            "expected_score": self.expected_score,
            "actual_score": self.actual_score,
            "integrity_status": self.integrity_status,
            "cheat_probability": self.cheat_probability,
            "rating_frozen": self.rating_frozen,
            "confidence_before": self.confidence_before,
            "confidence_after": self.confidence_after,
            "confidence_change": self.confidence_change,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Leaderboard(Base):
    """Leaderboard snapshot for caching."""
    
    __tablename__ = "leaderboard_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Leaderboard type
    leaderboard_type = Column(String(50), nullable=False, index=True)  # "global", "weekly", "monthly", "domain"
    
    # Domain-specific (if applicable)
    domain = Column(String(50), nullable=True, index=True)  # "algorithms", "data_structures", etc.
    
    # Snapshot data (stored as JSON)
    rankings = Column(Text, nullable=False)  # JSON array of player rankings
    snapshot_date = Column(DateTime, default=func.now(), nullable=False)
    
    # Statistics
    total_players = Column(Integer, default=0, nullable=False)
    average_rating = Column(Float, default=0.0, nullable=False)
    median_rating = Column(Integer, default=0, nullable=False)
    
    # Cache validity
    is_valid = Column(Boolean, default=True, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Leaderboard(type={self.leaderboard_type}, players={self.total_players}, date={self.snapshot_date})>"
    
    def to_dict(self):
        """Convert leaderboard to dictionary for API responses."""
        return {
            "id": self.id,
            "leaderboard_type": self.leaderboard_type,
            "domain": self.domain,
            "snapshot_date": self.snapshot_date.isoformat() if self.snapshot_date else None,
            "total_players": self.total_players,
            "average_rating": self.average_rating,
            "median_rating": self.median_rating,
            "is_valid": self.is_valid,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
        }