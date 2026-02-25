from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..models import Match, MatchQueue, Player, Challenge, MatchStatus, MatchFormat
from ..config import settings
from .rating_service import RatingService

logger = logging.getLogger(__name__)

class MatchService:
    """Service for handling match lifecycle and matchmaking."""
    
    def __init__(self, db: Session):
        self.db = db
        self.rating_service = RatingService(db)
    
    def join_match_queue(
        self,
        player_id: str,
        preferred_format: str = "1v1",
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None
    ) -> Dict:
        """
        Add player to matchmaking queue.
        
        Args:
            player_id: ID of the player
            preferred_format: Preferred match format ("1v1", "battle_royale")
            min_rating: Minimum opponent rating
            max_rating: Maximum opponent rating
        
        Returns:
            Dict: Queue join information
        """
        # Check if player is already in queue
        existing = self.db.query(MatchQueue).filter(MatchQueue.player_id == player_id).first()
        
        if existing:
            # Update existing queue entry
            existing.last_ping = datetime.utcnow()
            existing.is_active = True
            self.db.commit()
            
            return {
                "status": "already_in_queue",
                "queue_id": existing.id,
                "player_id": player_id,
                "joined_at": existing.joined_at.isoformat()
            }
        
        # Get player's current rating
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"error": "Player not found"}
        
        # Create queue entry
        queue_entry = MatchQueue(
            player_id=player_id,
            player_rating=player.current_rating,
            preferred_format=MatchFormat(preferred_format),
            min_rating=min_rating,
            max_rating=max_rating,
            joined_at=datetime.utcnow(),
            last_ping=datetime.utcnow(),
            is_active=True
        )
        
        self.db.add(queue_entry)
        self.db.commit()
        
        logger.info(f"Player {player_id} joined match queue")
        
        return {
            "status": "joined_queue",
            "queue_id": queue_entry.id,
            "player_id": player_id,
            "player_rating": player.current_rating,
            "preferred_format": preferred_format,
            "joined_at": queue_entry.joined_at.isoformat()
        }
    
    def leave_match_queue(self, player_id: str) -> Dict:
        """
        Remove player from matchmaking queue.
        
        Args:
            player_id: ID of the player
        
        Returns:
            Dict: Queue leave information
        """
        queue_entry = self.db.query(MatchQueue).filter(MatchQueue.player_id == player_id).first()
        
        if not queue_entry:
            return {"error": "Player not in queue"}
        
        queue_entry.is_active = False
        self.db.commit()
        
        logger.info(f"Player {player_id} left match queue")
        
        return {
            "status": "left_queue",
            "player_id": player_id,
            "queue_id": queue_entry.id
        }
    
    def find_opponent(self, player_id: str, timeout_seconds: int = 60) -> Optional[Dict]:
        """
        Find an opponent for a player in the queue.
        
        Args:
            player_id: ID of the player
            timeout_seconds: Maximum time to search for opponent
        
        Returns:
            Optional[Dict]: Opponent information if found
        """
        # Get player's queue entry
        player_queue = self.db.query(MatchQueue).filter(
            and_(
                MatchQueue.player_id == player_id,
                MatchQueue.is_active == True
            )
        ).first()
        
        if not player_queue:
            return None
        
        player_rating = player_queue.player_rating
        preferred_format = player_queue.preferred_format
        
        # Calculate search range
        min_rating = player_rating - settings.ELO_MATCHING_RANGE
        max_rating = player_rating + settings.ELO_MATCHING_RANGE
        
        # Apply player's custom rating limits if specified
        if player_queue.min_rating:
            min_rating = max(min_rating, player_queue.min_rating)
        if player_queue.max_rating:
            max_rating = min(max_rating, player_queue.max_rating)
        
        # Find potential opponents
        potential_opponents = self.db.query(MatchQueue).filter(
            and_(
                MatchQueue.player_id != player_id,
                MatchQueue.is_active == True,
                MatchQueue.player_rating >= min_rating,
                MatchQueue.player_rating <= max_rating,
                MatchQueue.preferred_format == preferred_format
            )
        ).all()
        
        if not potential_opponents:
            return None
        
        # Select the best match (closest rating)
        best_match = min(
            potential_opponents,
            key=lambda x: abs(x.player_rating - player_rating)
        )
        
        return {
            "opponent_id": best_match.player_id,
            "opponent_rating": best_match.player_rating,
            "rating_difference": abs(best_match.player_rating - player_rating),
            "preferred_format": preferred_format.value
        }
    
    def create_match(
        self,
        player1_id: str,
        player2_id: str,
        challenge_id: str,
        match_format: str = "1v1",
        time_limit_seconds: int = 120
    ) -> Dict:
        """
        Create a new match between two players.
        
        Args:
            player1_id: ID of player 1
            player2_id: ID of player 2
            challenge_id: ID of the challenge
            match_format: Match format ("1v1", "battle_royale")
            time_limit_seconds: Time limit for the match
        
        Returns:
            Dict: Match creation information
        """
        # Validate time limit
        time_limit_seconds = max(
            settings.MATCH_DURATION_MIN_SECONDS,
            min(time_limit_seconds, settings.MATCH_DURATION_MAX_SECONDS)
        )
        
        # Create WebSocket room ID
        websocket_room = f"match_{uuid.uuid4().hex[:16]}"
        
        # Create match
        match = Match(
            player1_id=player1_id,
            player2_id=player2_id,
            challenge_id=challenge_id,
            match_format=MatchFormat(match_format),
            status=MatchStatus.WAITING,
            time_limit_seconds=time_limit_seconds,
            websocket_room=websocket_room,
            created_at=datetime.utcnow()
        )
        
        self.db.add(match)
        
        # Remove players from queue
        self.db.query(MatchQueue).filter(
            MatchQueue.player_id.in_([player1_id, player2_id])
        ).delete(synchronize_session=False)
        
        self.db.commit()
        
        logger.info(f"Created match {match.id} between {player1_id} and {player2_id}")
        
        return {
            "match_id": match.id,
            "player1_id": player1_id,
            "player2_id": player2_id,
            "challenge_id": challenge_id,
            "match_format": match_format,
            "time_limit_seconds": time_limit_seconds,
            "websocket_room": websocket_room,
            "status": match.status.value,
            "created_at": match.created_at.isoformat()
        }
    
    def start_match(self, match_id: str) -> Dict:
        """
        Start a match (begin timer).
        
        Args:
            match_id: ID of the match
        
        Returns:
            Dict: Match start information
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            return {"error": "Match not found"}
        
        if match.status != MatchStatus.WAITING:
            return {"error": f"Match is not in waiting state (current: {match.status.value})"}
        
        match.status = MatchStatus.ACTIVE
        match.started_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Started match {match_id}")
        
        return {
            "match_id": match_id,
            "status": match.status.value,
            "started_at": match.started_at.isoformat(),
            "time_limit_seconds": match.time_limit_seconds,
            "time_remaining": match.time_remaining
        }
    
    def player_done(self, match_id: str, player_id: str) -> Dict:
        """
        Mark a player as done submitting in a match.
        
        Args:
            match_id: ID of the match
            player_id: ID of the player
        
        Returns:
            Dict: Player done information
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            return {"error": "Match not found"}
        
        if match.status != MatchStatus.ACTIVE:
            return {"error": f"Match is not active (current: {match.status.value})"}
        
        # Mark player as done
        if player_id == match.player1_id:
            match.player1_done = True
        elif player_id == match.player2_id:
            match.player2_done = True
        else:
            return {"error": "Player not in this match"}
        
        # Check if match should end (all players done)
        if match.all_players_done:
            match.status = MatchStatus.CONCLUDED
            match.ended_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Player {player_id} marked as done in match {match_id}")
        
        return {
            "match_id": match_id,
            "player_id": player_id,
            "player_done": True,
            "all_players_done": match.all_players_done,
            "match_status": match.status.value
        }
    
    def check_match_timeout(self, match_id: str) -> bool:
        """
        Check if a match has timed out and update status if needed.
        
        Args:
            match_id: ID of the match
        
        Returns:
            bool: True if match timed out, False otherwise
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            return False
        
        if match.status != MatchStatus.ACTIVE:
            return False
        
        # Check if time has expired
        if match.time_remaining <= 0:
            match.status = MatchStatus.CONCLUDED
            match.ended_at = datetime.utcnow()
            match.result = "timeout"
            self.db.commit()
            
            logger.info(f"Match {match_id} timed out")
            return True
        
        return False
    
    def conclude_match(
        self,
        match_id: str,
        player1_score: float,
        player2_score: float,
        player1_ai_score: Optional[float] = None,
        player2_ai_score: Optional[float] = None,
        player1_complexity_score: Optional[float] = None,
        player2_complexity_score: Optional[float] = None,
        cheat_probability: Optional[float] = None
    ) -> Dict:
        """
        Conclude a match with final scores.
        
        Args:
            match_id: ID of the match
            player1_score: Player 1's test case score
            player2_score: Player 2's test case score
            player1_ai_score: Player 1's AI quality score
            player2_ai_score: Player 2's AI quality score
            player1_complexity_score: Player 1's complexity score
            player2_complexity_score: Player 2's complexity score
            cheat_probability: Overall cheat probability for the match
        
        Returns:
            Dict: Match conclusion information
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            return {"error": "Match not found"}
        
        if match.status == MatchStatus.CONCLUDED:
            return {"error": "Match already concluded"}
        
        # Update match scores
        match.player1_score = player1_score
        match.player2_score = player2_score
        match.player1_ai_quality_score = player1_ai_score
        match.player2_ai_quality_score = player2_ai_score
        match.player1_complexity_score = player1_complexity_score
        match.player2_complexity_score = player2_complexity_score
        match.cheat_probability = cheat_probability
        
        # Calculate match result
        player1_result, player2_result, winner = self.rating_service.calculate_match_result(
            player1_score=player1_score,
            player2_score=player2_score,
            player1_ai_score=player1_ai_score,
            player2_ai_score=player2_ai_score,
            player1_complexity_score=player1_complexity_score,
            player2_complexity_score=player2_complexity_score
        )
        
        # Update match result
        match.result = f"{player1_result}_{player2_result}"
        if winner == "player1":
            match.winner_id = match.player1_id
        elif winner == "player2":
            match.winner_id = match.player2_id
        
        # Update integrity status
        if cheat_probability is not None:
            if cheat_probability >= 85:
                match.integrity_status = "flagged"
                match.rating_frozen = True
            elif cheat_probability >= 70:
                match.integrity_status = "flagged"
            else:
                match.integrity_status = "clean"
        
        # Conclude match
        match.status = MatchStatus.CONCLUDED
        if not match.ended_at:
            match.ended_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Concluded match {match_id}: {match.result}")
        
        return {
            "match_id": match_id,
            "status": match.status.value,
            "player1_score": player1_score,
            "player2_score": player2_score,
            "player1_result": player1_result,
            "player2_result": player2_result,
            "winner_id": match.winner_id,
            "result": match.result,
            "integrity_status": match.integrity_status,
            "rating_frozen": match.rating_frozen,
            "ended_at": match.ended_at.isoformat() if match.ended_at else None
        }
    
    def get_match(self, match_id: str) -> Optional[Dict]:
        """
        Get match information.
        
        Args:
            match_id: ID of the match
        
        Returns:
            Optional[Dict]: Match information
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            return None
        
        return match.to_dict()
    
    def get_player_matches(self, player_id: str, limit: int = 50) -> List[Dict]:
        """
        Get player's recent matches.
        
        Args:
            player_id: ID of the player
            limit: Maximum number of matches to return
        
        Returns:
            List[Dict]: List of match information
        """
        matches = self.db.query(Match).filter(
            or_(
                Match.player1_id == player_id,
                Match.player2_id == player_id
            )
        ).order_by(desc(Match.created_at)).limit(limit).all()
        
        return [match.to_dict() for match in matches]
    
    def cleanup_inactive_queue(self, timeout_minutes: int = 5) -> int:
        """
        Clean up inactive queue entries.
        
        Args:
            timeout_minutes: Minutes since last ping to consider inactive
        
        Returns:
            int: Number of entries cleaned up
        """
        timeout_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        # Mark inactive entries
        result = self.db.query(MatchQueue).filter(
            and_(
                MatchQueue.is_active == True,
                MatchQueue.last_ping < timeout_time
            )
        ).update({"is_active": False})
        
        self.db.commit()
        
        if result > 0:
            logger.info(f"Cleaned up {result} inactive queue entries")
        
        return result