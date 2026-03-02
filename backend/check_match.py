
import sqlite3
import json
import os

def check_latest_match():
    db_path = 'c:/Users/HP/OneDrive/CodeRoad/backend/coderoad.db'
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get latest match
    c.execute("SELECT * FROM matches ORDER BY created_at DESC LIMIT 1")
    match = c.fetchone()
    if not match:
        print("No matches found")
        return

    print("--- LATEST MATCH ---")
    print(f"ID: {match['id']}")
    print(f"Status: {match['status']}")
    print(f"Format: {match['match_format']}")
    print(f"Result: {match['result']}")
    print(f"Winner ID: {match['winner_id']}")
    print(f"P1 Score: {match['player1_score']}, P1 Rating Change: {match['player1_rating_change']}")
    print(f"P2 Score: {match['player2_score']}, P2 Rating Change: {match['player2_rating_change']}")
    print(f"P1 ID: {match['player1_id']}")
    print(f"P2 ID: {match['player1_id']}")
    print(f"P2 ID: {match['player2_id']}")
    
    match_id = match['id']
    
    # Check submissions for this match
    c.execute("SELECT * FROM submissions WHERE match_id = ?", (match_id,))
    subs = c.fetchall()
    print("\n--- SUBMISSIONS FOR THIS MATCH ---")
    for sub in subs:
        print(f"Player: {sub['player_id']}")
        print(f"  Status: {sub['status']}")
        print(f"  Test Cases Passed/Total: {sub['test_cases_passed']}/{sub['test_cases_total']}")
        print(f"  Submission Number: {sub['submission_number']}")
        print(f"  Execution time: {sub['execution_time_ms']}ms")
        print(f"  AI Score: {sub['ai_quality_score']}")
        print(f"  Complexity: {sub['complexity_score']}")
        print(f"  Accuracy Propertity: {(sub['test_cases_passed']/sub['test_cases_total']*100) if sub['test_cases_total'] > 0 else 0}%")
    
    conn.close()

if __name__ == "__main__":
    check_latest_match()
