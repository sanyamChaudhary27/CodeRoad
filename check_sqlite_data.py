import sqlite3

conn = sqlite3.connect('backend/coderoad.db')
cur = conn.cursor()

# Check players table
cur.execute("SELECT id, username, email, hashed_password FROM players LIMIT 3")
rows = cur.fetchall()

print("Players in SQLite:")
for row in rows:
    print(f"ID: {row[0]}")
    print(f"Username: {row[1]}")
    print(f"Email: {row[2]}")
    print(f"Hashed Password (first 50 chars): {row[3][:50] if row[3] else 'None'}")
    print()

conn.close()
