from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base

class Player(Base):
    """Player model representing a user in the system."""
    
    __tablename__ = "players"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # DSA Rating information
    current_rating = Column(Integer, default=300, nullable=False)
    rating_confidence = Column(Float, default=100.0, nullable=False)  # 0-100%
    
    # DSA Statistics
    matches_played = Column(Integer, default=0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    draws = Column(Integer, default=0, nullable=False)
    
    # Debug Arena Rating & Statistics
    debug_rating = Column(Integer, default=300, nullable=False)
    debug_rating_confidence = Column(Float, default=100.0, nullable=False)
    debug_matches_played = Column(Integer, default=0, nullable=False)
    debug_wins = Column(Integer, default=0, nullable=False)
    debug_losses = Column(Integer, default=0, nullable=False)
    debug_draws = Column(Integer, default=0, nullable=False)
    
    # Profile customization
    profile_picture = Column(Text, nullable=True)  # URL or base64 data
    
    # Win rate calculated property
    @property
    def win_rate(self) -> float:
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100
    
    @property
    def debug_win_rate(self) -> float:
        if self.debug_matches_played == 0:
            return 0.0
        return (self.debug_wins / self.debug_matches_played) * 100
    
    @property
    def badges_earned(self) -> int:
        return len(self.badges) if self.badges else 0
    
    # Integrity tracking
    suspicious_matches = Column(Integer, default=0, nullable=False)
    clean_matches = Column(Integer, default=0, nullable=False)
    last_flagged_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_match_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    matches_as_player1 = relationship("Match", foreign_keys="Match.player1_id", back_populates="player1")
    matches_as_player2 = relationship("Match", foreign_keys="Match.player2_id", back_populates="player2")
    submissions = relationship("Submission", back_populates="player")
    badges = relationship("Badge", back_populates="player")
    
    def __repr__(self):
        return f"<Player(id={self.id}, username={self.username}, rating={self.current_rating})>"
    
    def to_dict(self):
        """Convert player to dictionary for API responses."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "current_rating": self.current_rating,
            "rating_confidence": self.rating_confidence,
            "matches_played": self.matches_played,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "win_rate": self.win_rate,
            "suspicious_matches": self.suspicious_matches,
            "clean_matches": self.clean_matches,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_match_at": self.last_match_at.isoformat() if self.last_match_at else None,
        }

class Badge(Base):
    """Badges earned by players for achievements."""
    
    __tablename__ = "badges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False, index=True)
    
    # Badge details
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(String(255), nullable=True)
    badge_type = Column(String(50), nullable=False)  # "rating", "win_streak", "tournament", etc.
    
    # Achievement criteria
    criteria_met = Column(Text, nullable=True)  # JSON string of criteria
    
    # Timestamps
    awarded_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    player = relationship("Player", back_populates="badges")
    
    def __repr__(self):
        return f"<Badge(player={self.player_id}, name={self.name})>"