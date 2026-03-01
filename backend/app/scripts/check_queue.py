import sqlite3
import os

def check():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "coderoad.db")
    if not os.path.exists(db_path):
        print("Database not found")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM match_queue")
    for row in cursor.fetchall():
        print(row)
    conn.close()

if __name__ == "__main__":
    check()
