
import sqlite3
import json
import os

def check_latest_match():
    # Use absolute path for the DB file
    db_path = 'c:/Users/HP/OneDrive/CodeRoad/backend/coderoad.db'
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get latest concluded match
    c.execute("SELECT * FROM matches WHERE status='concluded' ORDER BY ended_at DESC LIMIT 1")
    match = c.fetchone()
    if not match:
        print("No concluded matches found")
        # Try any match
        c.execute("SELECT * FROM matches ORDER BY created_at DESC LIMIT 1")
        match = c.fetchone()
        if not match:
            print("No matches at all found")
            return
        print("--- LATEST MATCH (ANY STATUS) ---")
    else:
        print("--- LATEST CONCLUDED MATCH ---")

    print(f"ID: {match['id']}")
    print(f"Status: {match['status']}")
    print(f"Format: {match['match_format']}")
    print(f"Result: {match['result']}")
    print(f"Winner ID: {match['winner_id']}")
    print(f"P1 Score: {match['player1_score']}, P1 Rating Change: {match['player1_rating_change']}")
    print(f"P2 Score: {match['player2_score']}, P2 Rating Change: {match['player2_rating_change']}")
    print(f"P1 ID: {match['player1_id']}")
    print(f"P2 ID: {match['player2_id']}")
    
    match_id = match['id']
    
    # Check submissions for this match
    c.execute("SELECT * FROM submissions WHERE match_id = ?", (match_id,))
    subs = c.fetchall()
    print(f"\n--- SUBMISSIONS FOR MATCH {match_id} ({len(subs)} found) ---")
    for sub in subs:
        print(f"  Player: {sub['player_id']}")
        print(f"    Status: {sub['status']}")
        print(f"    Passed: {sub['test_cases_passed']}/{sub['test_cases_total']}")
        print(f"    Accuracy: {(sub['test_cases_passed']/sub['test_cases_total']*100) if sub['test_cases_total'] > 0 else 0}%")
        print(f"    Execution time: {sub['execution_time_ms']}ms")
    
    conn.close()

if __name__ == "__main__":
    check_latest_match()
