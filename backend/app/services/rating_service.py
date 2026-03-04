from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math
import logging
from sqlalchemy.orm import Session

from ..models import Rating, RatingHistory, Player, Match, Submission
from ..config import settings

logger = logging.getLogger(__name__)

class RatingService:
    """Service for handling ELO rating calculations and updates."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_expected_score(self, player_rating: int, opponent_rating: int) -> float:
        """
        Calculate expected score using standard ELO formula.
        
        Args:
            player_rating: Player's current rating
            opponent_rating: Opponent's current rating
        
        Returns:
            float: Expected score (0-1)
        """
        return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
    
    def calculate_rating_change(
        self,
        player_rating: int,
        opponent_rating: int,
        match_result: str,  # "win", "loss", "draw"
        k_factor: int = settings.ELO_K_FACTOR
    ) -> Tuple[int, float, float]:
        """
        Calculate rating change using ELO system.
        
        Args:
            player_rating: Player's current rating
            opponent_rating: Opponent's current rating
            match_result: Result of the match
            k_factor: Rating volatility factor
        
        Returns:
            Tuple[int, float, float]: (rating_change, expected_score, actual_score)
        """
        # Calculate expected score
        expected_score = self.calculate_expected_score(player_rating, opponent_rating)
        
        # Determine actual score based on match result
        if match_result == "win":
            actual_score = 1.0
        elif match_result == "loss":
            actual_score = 0.0
        elif match_result == "draw":
            actual_score = 0.5
        else:
            raise ValueError(f"Invalid match result: {match_result}")
        
        # Calculate rating change
        rating_change = round(k_factor * (actual_score - expected_score))
        
        return rating_change, expected_score, actual_score
    
    def update_player_rating(
        self,
        player_id: str,
        opponent_id: str,
        match_id: str,
        match_result: str,
        opponent_rating: int,
        cheat_probability: Optional[float] = None
    ) -> Dict:
        """
        Update player rating after a match.
        
        Args:
            player_id: ID of the player to update
            opponent_id: ID of the opponent
            match_id: ID of the match
            match_result: Result of the match ("win", "loss", "draw")
            opponent_rating: Opponent's rating at match time
            cheat_probability: Cheat probability from integrity analysis (0-100%)
        
        Returns:
            Dict: Rating update information
        """
        # Get player's current rating
        rating = self.db.query(Rating).filter(Rating.player_id == player_id).first()
        
        if not rating:
            # Create new rating if it doesn't exist
            rating = Rating(
                player_id=player_id,
                current_rating=settings.INITIAL_ELO_RATING,
                rating_confidence=100.0
            )
            self.db.add(rating)
            self.db.flush()
        
        old_rating = rating.current_rating
        
        # Calculate rating change
        rating_change, expected_score, actual_score = self.calculate_rating_change(
            player_rating=old_rating,
            opponent_rating=opponent_rating,
            match_result=match_result
        )
        
        # Adjust rating change based on confidence
        confidence_multiplier = rating.rating_confidence / 100.0
        adjusted_rating_change = round(rating_change * confidence_multiplier)
        
        # Update rating
        new_rating = old_rating + adjusted_rating_change
        
        # Ensure rating doesn't go below minimum (100 is the floor)
        new_rating = max(100, new_rating)
        
        # Update peak rating if applicable
        if new_rating > rating.peak_rating:
            rating.peak_rating = new_rating
            rating.peak_rating_date = datetime.utcnow()
        
        rating.current_rating = new_rating
        
        # Update statistics
        rating.matches_played += 1
        if match_result == "win":
            rating.wins += 1
        elif match_result == "loss":
            rating.losses += 1
        elif match_result == "draw":
            rating.draws += 1
        
        # Update last activity
        rating.last_activity_date = datetime.utcnow()
        rating.updated_at = datetime.utcnow()
        
        # Create rating history record
        history = RatingHistory(
            rating_id=rating.id,
            match_id=match_id,
            old_rating=old_rating,
            new_rating=new_rating,
            rating_change=adjusted_rating_change,
            opponent_id=opponent_id,
            opponent_rating=opponent_rating,
            match_result=match_result,
            k_factor=settings.ELO_K_FACTOR,
            expected_score=expected_score,
            actual_score=actual_score,
            integrity_status="clean" if cheat_probability is None or cheat_probability < 70 else "flagged",
            cheat_probability=cheat_probability,
            rating_frozen=cheat_probability is not None and cheat_probability >= 85,
            confidence_before=rating.rating_confidence,
            confidence_after=rating.rating_confidence,  # Will be updated by integrity service
            confidence_change=0  # Will be updated by integrity service
        )
        self.db.add(history)
        
        # Update player's match statistics
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if player:
            player.current_rating = new_rating
            player.matches_played += 1
            if match_result == "win":
                player.wins += 1
            elif match_result == "loss":
                player.losses += 1
            elif match_result == "draw":
                player.draws += 1
            player.last_match_at = datetime.utcnow()
            player.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "player_id": player_id,
            "old_rating": old_rating,
            "new_rating": new_rating,
            "rating_change": adjusted_rating_change,
            "opponent_id": opponent_id,
            "opponent_rating": opponent_rating,
            "match_result": match_result,
            "expected_score": expected_score,
            "actual_score": actual_score,
            "cheat_probability": cheat_probability,
            "rating_frozen": cheat_probability is not None and cheat_probability >= 85
        }
    
    def update_rating_confidence(
        self,
        player_id: str,
        cheat_probability: Optional[float]
    ) -> Dict:
        """
        Update player's rating confidence based on integrity analysis.
        
        Args:
            player_id: ID of the player
            cheat_probability: Cheat probability from integrity analysis (0-100%)
        
        Returns:
            Dict: Confidence update information
        """
        rating = self.db.query(Rating).filter(Rating.player_id == player_id).first()
        
        if not rating:
            return {"error": "Rating not found"}
        
        old_confidence = rating.rating_confidence
        
        if cheat_probability is None or cheat_probability < 70:
            # Clean match - increase confidence
            new_confidence = min(old_confidence + 1.0, 100.0)
            confidence_change = 1.0
        elif cheat_probability >= 70 and cheat_probability < 85:
            # Soft flag - decrease confidence moderately
            new_confidence = max(old_confidence - 2.0, 0.0)
            confidence_change = -2.0
        else:  # cheat_probability >= 85
            # Hard flag - decrease confidence significantly
            new_confidence = max(old_confidence - 5.0, 0.0)
            confidence_change = -5.0
        
        rating.rating_confidence = new_confidence
        rating.updated_at = datetime.utcnow()
        
        # Update player's rating confidence
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if player:
            player.rating_confidence = new_confidence
            if cheat_probability is None or cheat_probability < 70:
                player.clean_matches += 1
            else:
                player.suspicious_matches += 1
                player.last_flagged_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "player_id": player_id,
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "confidence_change": confidence_change,
            "cheat_probability": cheat_probability
        }
    
    def apply_rating_decay(self, player_id: str) -> Dict:
        """
        Apply rating decay for inactive players.
        
        Args:
            player_id: ID of the player
        
        Returns:
            Dict: Decay application information
        """
        rating = self.db.query(Rating).filter(Rating.player_id == player_id).first()
        
        if not rating:
            return {"error": "Rating not found"}
        
        # Check if player is inactive (no activity for 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        if rating.last_activity_date < thirty_days_ago and not rating.decay_applied:
            # Apply decay: 10 points per week of inactivity
            weeks_inactive = (datetime.utcnow() - rating.last_activity_date).days // 7
            decay_amount = weeks_inactive * 10
            
            old_rating = rating.current_rating
            new_rating = max(800, old_rating - decay_amount)
            
            rating.current_rating = new_rating
            rating.decay_applied = True
            rating.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "player_id": player_id,
                "old_rating": old_rating,
                "new_rating": new_rating,
                "decay_amount": decay_amount,
                "weeks_inactive": weeks_inactive
            }
        
        return {
            "player_id": player_id,
            "decay_applied": False,
            "reason": "Player is active or decay already applied"
        }
    
    def get_player_rating(self, player_id: str) -> Optional[Dict]:
        """
        Get player's current rating information.
        
        Args:
            player_id: ID of the player
        
        Returns:
            Optional[Dict]: Rating information
        """
        rating = self.db.query(Rating).filter(Rating.player_id == player_id).first()
        
        if not rating:
            return None
        
        return rating.to_dict()
    
    def get_rating_history(self, player_id: str, limit: int = 50) -> List[Dict]:
        """
        Get player's rating history.
        
        Args:
            player_id: ID of the player
            limit: Maximum number of history records to return
        
        Returns:
            List[Dict]: Rating history records
        """
        rating = self.db.query(Rating).filter(Rating.player_id == player_id).first()
        
        if not rating:
            return []
        
        history = self.db.query(RatingHistory)\
            .filter(RatingHistory.rating_id == rating.id)\
            .order_by(RatingHistory.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [record.to_dict() for record in history]
    
    def calculate_match_result(
        self,
        player1_score: float,
        player2_score: float,
        player1_time: Optional[float] = None,
        player2_time: Optional[float] = None,
        player1_ai_score: Optional[float] = None,
        player2_ai_score: Optional[float] = None,
        player1_complexity_score: Optional[float] = None,
        player2_complexity_score: Optional[float] = None,
        player1_memory: Optional[float] = None,
        player2_memory: Optional[float] = None,
        player1_ai_prob: Optional[float] = None,
        player2_ai_prob: Optional[float] = None
    ) -> Tuple[str, str, Optional[str]]:
        """
        Calculate match result based on scoring metrics with priority.
        
        Priority order:
        1. Test case score (Accuracy)
        2. Execution time (Speed; ±3000ms considered equal)
        3. Complexity score (Efficiency)
        4. Memory usage (Space; Lower is better)
        5. AI assistance probability (Integrity; Lower is better)
        
        Returns:
            Tuple[str, str, str]: (player1_result, player2_result, winner_id)
        """
        # 1. Compare Accuracy (Test case scores)
        if player1_score > player2_score:
            return "win", "loss", "player1"
        elif player2_score > player1_score:
            return "loss", "win", "player2"
        
        # 2. Compare Speed (Execution Time) - ±3s tolerance
        if player1_time is not None and player2_time is not None:
            # Check if time difference is greater than 3 seconds (3000ms)
            if abs(player1_time - player2_time) > 3000:
                if player1_time < player2_time:
                    return "win", "loss", "player1"
                else:
                    return "loss", "win", "player2"
        
        # 3. Compare Time Complexity (Efficiency score)
        if player1_complexity_score is not None and player2_complexity_score is not None:
            if player1_complexity_score > player2_complexity_score:
                return "win", "loss", "player1"
            elif player2_complexity_score > player1_complexity_score:
                return "loss", "win", "player2"
        
        # 4. Compare Space Complexity (Memory used) - Lower is better
        if player1_memory is not None and player2_memory is not None:
            if player1_memory < player2_memory:
                return "win", "loss", "player1"
            elif player2_memory < player1_memory:
                return "loss", "win", "player2"

        # 5. Compare AI Integrity (AI probability) - Lower is better
        p1_prob = player1_ai_prob if player1_ai_prob is not None else 0.0
        p2_prob = player2_ai_prob if player2_ai_prob is not None else 0.0
        if p1_prob < p2_prob:
            return "win", "loss", "player1"
        elif p2_prob < p1_prob:
            return "loss", "win", "player2"
        
        # All scores are tied - it's a draw
        return "draw", "draw", None
