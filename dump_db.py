import sqlite3, os, json

db_path = os.path.join(os.path.dirname(__file__), 'backend', 'coderoad.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# All matches
c.execute("SELECT id, status, match_format, player1_id, player2_id, player1_score, player2_score, player1_rating_change, player2_rating_change, result, winner_id FROM matches ORDER BY created_at DESC LIMIT 5")
for m in c.fetchall():
    d = dict(m)
    for k,v in d.items():
        print(f"  {k}: {v}")
    print("---")
    # Submissions
    c.execute("SELECT player_id, test_cases_passed, test_cases_total, status, execution_time_ms FROM submissions WHERE match_id=?", (d['id'],))
    for s in c.fetchall():
        sd = dict(s)
        print(f"    SUB: player={sd['player_id'][:8]}.. passed={sd['test_cases_passed']}/{sd['test_cases_total']} status={sd['status']} time={sd['execution_time_ms']}ms")
    print("===")

conn.close()
