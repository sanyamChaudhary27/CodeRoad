from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from ..core.database import Base

class MatchStatus(str, enum.Enum):
    """Match status enumeration."""
    WAITING = "waiting"  # Waiting for opponent
    ACTIVE = "active"    # Match in progress
    CONCLUDED = "concluded"  # Match completed
    CANCELLED = "cancelled"  # Match cancelled
    TIMEOUT = "timeout"  # Match timed out

class MatchFormat(str, enum.Enum):
    """Match format enumeration."""
    ONE_VS_ONE = "1v1"
    BATTLE_ROYALE = "battle_royale"
    TOURNAMENT = "tournament"

class Match(Base):
    """Match model representing a competitive coding match."""
    
    __tablename__ = "matches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Players
    player1_id = Column(String(36), ForeignKey("players.id"), nullable=False, index=True)
    player2_id = Column(String(36), ForeignKey("players.id"), nullable=True, index=True)
    
    # For battle royale/tournament matches
    player_ids = Column(Text, nullable=True)  # JSON array of player IDs for >2 players
    
    # Match details
    challenge_id = Column(String(36), nullable=False, index=True)
    match_format = Column(Enum(MatchFormat), default=MatchFormat.ONE_VS_ONE, nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.WAITING, nullable=False, index=True)
    
    # Timing
    created_at = Column(DateTime, default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    time_limit_seconds = Column(Integer, default=120, nullable=False)  # 30-120 seconds
    
    # Player states
    player1_done = Column(Boolean, default=False, nullable=False)
    player2_done = Column(Boolean, default=False, nullable=False)
    
    # Submission counters
    player1_submissions = Column(Integer, default=0, nullable=False)
    player2_submissions = Column(Integer, default=0, nullable=False)
    
    # For battle royale
    players_done = Column(Text, nullable=True)  # JSON array of player IDs who are done
    
    # Scoring
    player1_score = Column(Float, default=0.0, nullable=False)
    player2_score = Column(Float, default=0.0, nullable=False)
    
    # Rating changes
    player1_rating_change = Column(Integer, nullable=True)
    player2_rating_change = Column(Integer, nullable=True)
    
    # AI evaluation metrics
    player1_ai_quality_score = Column(Float, nullable=True)
    player2_ai_quality_score = Column(Float, nullable=True)
    player1_complexity_score = Column(Float, nullable=True)
    player2_complexity_score = Column(Float, nullable=True)
    
    # Result
    winner_id = Column(String(36), nullable=True, index=True)
    result = Column(String(20), nullable=True)  # "player1_win", "player2_win", "draw", "timeout"
    
    # Integrity
    integrity_status = Column(String(20), default="pending", nullable=False)  # "pending", "clean", "flagged", "frozen"
    cheat_probability = Column(Float, nullable=True)  # Overall cheat probability for the match
    rating_frozen = Column(Boolean, default=False, nullable=False)
    
    # WebSocket room
    websocket_room = Column(String(100), nullable=True, unique=True, index=True)
    
    # Relationships
    player1 = relationship("Player", foreign_keys=[player1_id], back_populates="matches_as_player1")
    player2 = relationship("Player", foreign_keys=[player2_id], back_populates="matches_as_player2")
    submissions = relationship("Submission", back_populates="match")
    
    def __repr__(self):
        return f"<Match(id={self.id}, status={self.status}, players={self.player1_id}-{self.player2_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if match is currently active."""
        return self.status == MatchStatus.ACTIVE
    
    @property
    def is_concluded(self) -> bool:
        """Check if match has concluded."""
        return self.status == MatchStatus.CONCLUDED
    
    @property
    def time_remaining(self) -> int:
        """Calculate time remaining in seconds."""
        if not self.started_at:
            return self.time_limit_seconds
        
        if self.ended_at or self.status in [MatchStatus.CONCLUDED, MatchStatus.TIMEOUT]:
            return 0
        
        from datetime import datetime
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        remaining = max(0, self.time_limit_seconds - int(elapsed))
        return remaining
    
    @property
    def all_players_done(self) -> bool:
        """Check if all players have signaled they are done."""
        if self.match_format == MatchFormat.ONE_VS_ONE:
            if self.player2_id is None:
                return self.player1_done
            return self.player1_done and self.player2_done
        else:
            # For battle royale, check if all players in player_ids are done
            # This would require parsing the JSON array
            return False  # Simplified for now
    
    def to_dict(self):
        """Convert match to dictionary for API responses."""
        return {
            "id": self.id,
            "player1_id": self.player1_id,
            "player2_id": self.player2_id,
            "player_ids": self.player_ids,
            "challenge_id": self.challenge_id,
            "match_format": self.match_format.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "time_limit_seconds": self.time_limit_seconds,
            "time_remaining": self.time_remaining,
            "player1_done": self.player1_done,
            "player2_done": self.player2_done,
            "player1_score": self.player1_score,
            "player2_score": self.player2_score,
            "player1_submissions": self.player1_submissions,
            "player2_submissions": self.player2_submissions,
            "winner_id": self.winner_id,
            "result": self.result,
            "integrity_status": self.integrity_status,
            "rating_frozen": self.rating_frozen,
            "player1_rating_change": self.player1_rating_change,
            "player2_rating_change": self.player2_rating_change,
            "websocket_room": self.websocket_room,
        }

class MatchQueue(Base):
    """Queue for matchmaking."""
    
    __tablename__ = "match_queue"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False, unique=True, index=True)
    
    # Player's current rating for matchmaking
    player_rating = Column(Integer, nullable=False)
    
    # Match preferences
    preferred_format = Column(Enum(MatchFormat), default=MatchFormat.ONE_VS_ONE, nullable=False)
    min_rating = Column(Integer, nullable=True)
    max_rating = Column(Integer, nullable=True)
    
    # Queue timing
    joined_at = Column(DateTime, default=func.now(), nullable=False)
    last_ping = Column(DateTime, default=func.now(), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    player = relationship("Player")
    
    def __repr__(self):
        return f"<MatchQueue(player={self.player_id}, rating={self.player_rating})>"

class Tournament(Base):
    """Tournament model for organized competitions."""
    
    __tablename__ = "tournaments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Tournament format
    format = Column(String(20), nullable=False)  # "knockout", "battle_royale", "swiss"
    max_players = Column(Integer, nullable=False)
    current_round = Column(Integer, default=1, nullable=False)
    
    # Status
    status = Column(String(20), default="scheduled", nullable=False)  # "scheduled", "active", "concluded"
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Bracket data (JSON)
    bracket_data = Column(Text, nullable=True)
    registered_players = Column(Text, nullable=True)  # JSON array of player IDs
    final_standings = Column(Text, nullable=True)  # JSON array of standings
    
    # Integrity tracking
    integrity_flags = Column(Text, nullable=True)  # JSON array of integrity flags
    
    def __repr__(self):
        return f"<Tournament(id={self.id}, name={self.name}, status={self.status})>"