
import sqlite3
import json

def check_recent_matches():
    conn = sqlite3.connect('backend/coderoad.db')
    cursor = conn.cursor()
    
    # Get last 5 matches
    cursor.execute("""
        SELECT id, player1_id, player2_id, status, match_format, winner_id, 
               player1_score, player2_score, player1_rating_change, player2_rating_change, result
        FROM matches 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    print("Recent Matches:")
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"  Players: {row[1]} vs {row[2]}")
        print(f"  Status: {row[3]}, Format: {row[4]}")
        print(f"  Scores: P1={row[6]}, P2={row[7]}")
        print(f"  Rating Changes: P1={row[8]}, P2={row[9]}")
        print(f"  Winner: {row[5]}, Result: {row[10]}")
        print("-" * 20)
        
        # Check submissions for this match
        cursor.execute("SELECT player_id, test_cases_passed, test_cases_total, status FROM submissions WHERE match_id = ?", (row[0],))
        subs = cursor.fetchall()
        print(f"  Submissions for {row[0]}:")
        for sub in subs:
            print(f"    Player {sub[0]}: {sub[1]}/{sub[2]} ({sub[3]})")
        print("=" * 40)
        
    conn.close()

if __name__ == "__main__":
    check_recent_matches()
