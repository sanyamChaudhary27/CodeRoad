
import sqlite3
import json
import os

def check_recent_matches():
    db_path = 'backend/coderoad.db'
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get last 5 matches
    cursor.execute("""
        SELECT id, player1_id, player2_id, status, match_format, winner_id, 
               player1_score, player2_score, player1_rating_change, player2_rating_change, result, challenge_id
        FROM matches 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    print(f"--- RECENT MATCHES (Last 5) ---")
    for row in rows:
        match_id = row[0]
        print(f"ID: {match_id}")
        print(f"  Players: P1={row[1]} | P2={row[2]}")
        print(f"  Status: {row[3]} | Format: {row[4]}")
        print(f"  Scores: P1={row[6]}% | P2={row[7]}%")
        print(f"  Winner: {row[5]} | Result: {row[10]}")
        print(f"  Rating Changes: P1={row[8]} | P2={row[9]}")
        
        # Check submissions for this match
        cursor.execute("""
            SELECT id, player_id, test_cases_passed, test_cases_total, status, execution_time_ms, submitted_at 
            FROM submissions 
            WHERE match_id = ? 
            ORDER BY submitted_at ASC
        """, (match_id,))
        subs = cursor.fetchall()
        print(f"  Submissions ({len(subs)} total):")
        for sub in subs:
            print(f"    SubID: {sub[0]}")
            print(f"    Player: {sub[1]}")
            print(f"    Passed: {sub[2]}/{sub[3]} | Status: {sub[4]} | Time: {sub[5]}ms | at: {sub[6]}")
        print("-" * 30)
        
    conn.close()

if __name__ == "__main__":
    check_recent_matches()
