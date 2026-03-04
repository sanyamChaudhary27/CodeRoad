"""
Test script to verify debug rating separation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config import settings

def check_recent_matches():
    """Check recent matches and their challenge types"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Get recent matches
        result = conn.execute(text("""
            SELECT 
                id,
                challenge_type,
                player1_id,
                player2_id,
                status,
                player1_rating_change,
                player2_rating_change,
                created_at
            FROM matches
            ORDER BY created_at DESC
            LIMIT 10
        """))
        
        print("\n=== Recent Matches ===")
        for row in result:
            print(f"\nMatch ID: {row[0]}")
            print(f"  Challenge Type: {row[1]}")
            print(f"  Player 1: {row[2]}")
            print(f"  Player 2: {row[3]}")
            print(f"  Status: {row[4]}")
            print(f"  P1 Rating Change: {row[5]}")
            print(f"  P2 Rating Change: {row[6]}")
            print(f"  Created: {row[7]}")
        
        # Get player ratings
        result = conn.execute(text("""
            SELECT 
                id,
                username,
                current_rating,
                debug_rating,
                matches_played,
                debug_matches_played
            FROM players
            ORDER BY created_at DESC
            LIMIT 5
        """))
        
        print("\n\n=== Recent Players ===")
        for row in result:
            print(f"\nPlayer: {row[1]} ({row[0]})")
            print(f"  DSA Rating: {row[2]}")
            print(f"  Debug Rating: {row[3]}")
            print(f"  DSA Matches: {row[4]}")
            print(f"  Debug Matches: {row[5]}")

if __name__ == "__main__":
    check_recent_matches()
