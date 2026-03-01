from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..models import Match, MatchQueue, Player, Challenge, MatchStatus, MatchFormat, Submission
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
        Consolidated logic for joining and match cleanup.
        """
        # 1. ALWAYS cancel any existing WAITING or ACTIVE matches for this player to ensure fresh start
        existing_matches = self.db.query(Match).filter(
            and_(
                or_(Match.player1_id == player_id, Match.player2_id == player_id),
                Match.status.in_([MatchStatus.WAITING, MatchStatus.ACTIVE])
            )
        ).all()
        for m in existing_matches:
            m.status = MatchStatus.CANCELLED
            logger.info(f"S5: Cancelled existing match {m.id} for player {player_id} before joining queue")
        
        if existing_matches:
            self.db.commit()

        # 2. Check if player's queue entry exists (active or inactive)
        existing_queue = self.db.query(MatchQueue).filter(MatchQueue.player_id == player_id).first()
        
        # 3. Get player's current rating for fresh accuracy
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"error": "Player not found"}

        if existing_queue:
            # Update existing queue entry to refresh metadata
            existing_queue.last_ping = datetime.utcnow()
            existing_queue.is_active = True
            existing_queue.player_rating = player.current_rating
            existing_queue.preferred_format = MatchFormat(preferred_format)
            existing_queue.joined_at = datetime.utcnow() # Treat as a fresh join
            self.db.commit()
            
            logger.info(f"S5: Refreshed queue entry for player {player_id}")
            return {
                "status": "joined_queue",
                "queue_id": existing_queue.id,
                "player_id": player_id,
                "player_rating": player.current_rating,
                "preferred_format": preferred_format,
                "joined_at": existing_queue.joined_at.isoformat()
            }
        
        # 4. Create new queue entry if none exists
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
        
        logger.info(f"S5: New queue entry for player {player_id}")
        
        return {
            "status": "joined_queue",
            "queue_id": queue_entry.id,
            "player_id": player_id,
            "player_rating": player.current_rating,
            "preferred_format": preferred_format,
            "joined_at": queue_entry.joined_at.isoformat()
        }
    
    def get_queue_status_with_matchmaking(self, player_id: str) -> Dict:
        """
        Get queue status and attempt matchmaking if not yet matched.
        Prioritizes existing matches over queue status.
        """
        # 1. ALWAYS check if we are already in an active/waiting match first
        # Cleanup stale matches (older than 2 minutes and still WAITING/ACTIVE)
        stale_threshold = datetime.utcnow() - timedelta(minutes=2)
        stale_matches = self.db.query(Match).filter(
            and_(
                or_(Match.player1_id == player_id, Match.player2_id == player_id),
                Match.status.in_([MatchStatus.WAITING, MatchStatus.ACTIVE]),
                Match.created_at < stale_threshold
            )
        ).all()
        
        for m in stale_matches:
            m.status = MatchStatus.CANCELLED
            logger.info(f"Auto-cancelled stale match {m.id} for player {player_id}")
        
        if stale_matches:
            self.db.commit()

        recent_match = self.db.query(Match).filter(
            and_(
                or_(Match.player1_id == player_id, Match.player2_id == player_id),
                Match.status.in_([MatchStatus.WAITING, MatchStatus.ACTIVE])
            )
        ).order_by(desc(Match.created_at)).first()
        
        if recent_match:
            # If we found a match, make sure to remove from queue if still there
            self.db.query(MatchQueue).filter(MatchQueue.player_id == player_id).delete()
            self.db.commit()
            
            logger.info(f"S5: Match {recent_match.id} detected for player {player_id}. Transitioning.")
            return {
                "player_id": player_id,
                "in_queue": False,
                "match_id": recent_match.id
            }

        # 2. Check if the player is in the queue
        queue_entry = self.db.query(MatchQueue).filter(
            and_(
                MatchQueue.player_id == player_id,
                MatchQueue.is_active == True
            )
        ).first()
        
        if not queue_entry:
            return {"player_id": player_id, "in_queue": False}
            
        # Update last_ping to keep queue entry alive
        queue_entry.last_ping = datetime.utcnow()
        self.db.commit()
        
        # 3. Try to find a match we can lead
        opponent_info = self.find_opponent(player_id)
        if opponent_info:
            opponent_id = opponent_info["opponent_id"]
            
            # Leader-based creation (alphabetical order check)
            if player_id < opponent_id:
                from .challenge_service import get_challenge_service
                challenge_service = get_challenge_service()
                challenge = challenge_service.generate_challenge(db=self.db, difficulty="intermediate")
                
                match_data = self.create_match(
                    player1_id=player_id,
                    player2_id=opponent_id,
                    challenge_id=challenge["id"]
                )
                
                # Automatically start competitive matches
                self.start_match(match_data["match_id"])
                
                return {
                    "player_id": player_id,
                    "in_queue": False,
                    "match_id": match_data["match_id"]
                }
            
        return {
            "player_id": player_id,
            "in_queue": True,
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
        
        # Relaxed range: Find potential opponents who have pinged in the last 60 seconds
        ping_threshold = datetime.utcnow() - timedelta(seconds=60)
        
        potential_opponents = self.db.query(MatchQueue).filter(
            and_(
                MatchQueue.player_id != player_id,
                MatchQueue.is_active == True,
                MatchQueue.last_ping >= ping_threshold,
                MatchQueue.player_rating >= min_rating,
                MatchQueue.player_rating <= max_rating,
                MatchQueue.preferred_format == preferred_format
            )
        ).all()
        
        if not potential_opponents:
            return None
        
        # Select the best match (closest rating)
        # Also consider longevity in queue? 
        best_match = min(
            potential_opponents,
            key=lambda x: abs(x.player_rating - player_rating)
        )
        
        return {
            "opponent_id": best_match.player_id,
            "opponent_rating": best_match.player_rating,
            "rating_difference": abs(best_match.player_rating - player_rating),
            "preferred_format": preferred_format.value,
            "opponent_queued_at": best_match.joined_at.isoformat()
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

    def create_solo_match(
        self,
        player_id: str,
        difficulty: str = "intermediate"
    ) -> Dict:
        """
        Create a solo practice match for a player.
        """
        from .challenge_service import get_challenge_service
        challenge_service = get_challenge_service()
        
        # Generate a challenge
        player = self.db.query(Player).filter(Player.id == player_id).first()
        player_rating = player.current_rating if player else 1200
        
        challenge_data = challenge_service.generate_challenge(
            db=self.db,
            difficulty=difficulty,
            player_rating=player_rating
        )
        
        # Create WebSocket room ID
        websocket_room = f"match_solo_{uuid.uuid4().hex[:16]}"
        
        # Create match
        match = Match(
            player1_id=player_id,
            player2_id=None, # Solo
            challenge_id=challenge_data['id'],
            match_format=MatchFormat.ONE_VS_ONE,
            status=MatchStatus.ACTIVE, # Start immediately
            time_limit_seconds=challenge_data.get('time_limit_seconds', 120),
            websocket_room=websocket_room,
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow()
        )
        
        self.db.add(match)
        self.db.commit()
        
        logger.info(f"Created solo match {match.id} for player {player_id}")
        
        return {
            "match_id": match.id,
            "player1_id": player_id,
            "challenge_id": challenge_data['id'],
            "challenge": challenge_data,
            "status": match.status.value,
            "websocket_room": websocket_room
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
        Get match information with enriched player data.
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            return None
        
        data = match.to_dict()
        
        # Enrich with player data and submission counts
        if match.player1_id:
            p1 = match.player1
            if p1:
                data["player1_username"] = p1.username
                data["player1_rating"] = p1.current_rating
                data["player1_submissions"] = self.db.query(Submission).filter(
                    Submission.match_id == match_id,
                    Submission.player_id == match.player1_id
                ).count()
            
        if match.player2_id:
            p2 = match.player2
            if p2:
                data["player2_username"] = p2.username
                data["player2_rating"] = p2.current_rating
                data["player2_submissions"] = self.db.query(Submission).filter(
                    Submission.match_id == match_id,
                    Submission.player_id == match.player2_id
                ).count()
            
        return data
    
    def get_player_matches(self, player_id: str, limit: int = 50) -> List[Dict]:
        """
        Get player's recent matches with enriched data.
        """
        matches = self.db.query(Match).filter(
            or_(
                Match.player1_id == player_id,
                Match.player2_id == player_id
            )
        ).order_by(desc(Match.created_at)).limit(limit).all()
        
        result = []
        for m in matches:
            d = m.to_dict()
            if m.player1:
                d["player1_username"] = m.player1.username
                d["player1_rating"] = m.player1.current_rating
            if m.player2:
                d["player2_username"] = m.player2.username
                d["player2_rating"] = m.player2.current_rating
            result.append(d)
            
        return result
    
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