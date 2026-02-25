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
        
        # Ensure rating doesn't go below minimum
        new_rating = max(800, new_rating)
        
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
        player1_ai_score: Optional[float] = None,
        player2_ai_score: Optional[float] = None,
        player1_complexity_score: Optional[float] = None,
        player2_complexity_score: Optional[float] = None
    ) -> Tuple[str, str, str]:
        """
        Calculate match result based on scoring metrics.
        
        Priority order:
        1. Test case score
        2. AI quality score
        3. Complexity score
        4. Submission time (earlier wins)
        
        Args:
            player1_score: Player 1's test case score (0-100)
            player2_score: Player 2's test case score (0-100)
            player1_ai_score: Player 1's AI quality score (0-100)
            player2_ai_score: Player 2's AI quality score (0-100)
            player1_complexity_score: Player 1's complexity score (0-100)
            player2_complexity_score: Player 2's complexity score (0-100)
        
        Returns:
            Tuple[str, str, str]: (player1_result, player2_result, winner_id)
        """
        # Compare test case scores first
        if player1_score > player2_score:
            return "win", "loss", "player1"
        elif player2_score > player1_score:
            return "loss", "win", "player2"
        
        # Test case scores are tied, compare AI quality scores
        if player1_ai_score is not None and player2_ai_score is not None:
            if player1_ai_score > player2_ai_score:
                return "win", "loss", "player1"
            elif player2_ai_score > player1_ai_score:
                return "loss", "win", "player2"
        
        # AI quality scores are tied or not available, compare complexity scores
        if player1_complexity_score is not None and player2_complexity_score is not None:
            if player1_complexity_score > player2_complexity_score:
                return "win", "loss", "player1"
            elif player2_complexity_score > player1_complexity_score:
                return "loss", "win", "player2"
        
        # All scores are tied - it's a draw
        return "draw", "draw", None