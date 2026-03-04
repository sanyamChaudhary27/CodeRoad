"""
One-time script to reset all player ratings to 300.
Run this once to reset existing players to the new initial rating.
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory for database access
os.chdir(backend_path)

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.player import Player
from app.models.rating import Rating
from app.config import settings

def reset_all_ratings():
    """Reset all player ratings to 300 (new initial rating)."""
    db: Session = SessionLocal()
    
    try:
        # Get all players
        all_players = db.query(Player).all()
        
        if not all_players:
            print("No players found in database.")
            return
        
        print(f"Found {len(all_players)} players to reset.")
        print(f"Resetting all ratings to {settings.INITIAL_ELO_RATING}...")
        
        # Reset each player's rating
        for player in all_players:
            old_rating = player.current_rating
            player.current_rating = settings.INITIAL_ELO_RATING
            player.rating_confidence = 100.0  # Reset confidence
            
            print(f"  {player.username} (ID: {player.id[:8]}...): {old_rating} -> {settings.INITIAL_ELO_RATING}")
        
        # Also reset ratings in the ratings table if they exist
        all_ratings = db.query(Rating).all()
        if all_ratings:
            print(f"\nAlso resetting {len(all_ratings)} entries in ratings table...")
            for rating in all_ratings:
                rating.current_rating = settings.INITIAL_ELO_RATING
                rating.peak_rating = settings.INITIAL_ELO_RATING
                rating.rating_deviation = 350.0
                rating.volatility = 0.06
                rating.rating_confidence = 100.0
        
        # Commit changes
        db.commit()
        print(f"\n✓ Successfully reset {len(all_players)} player ratings to {settings.INITIAL_ELO_RATING}!")
        print("\nNote: Rating history is preserved. Only current ratings were reset.")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error resetting ratings: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("RESET ALL PLAYER RATINGS TO 300")
    print("=" * 60)
    print("\nThis will reset all current player ratings to 300.")
    print("Rating history will be preserved.")
    
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        reset_all_ratings()
    else:
        print("\nOperation cancelled.")
