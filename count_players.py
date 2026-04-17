import sqlite3

conn = sqlite3.connect('backend/coderoad.db')
cur = conn.cursor()

# Count players
cur.execute("SELECT COUNT(*) FROM players")
count = cur.fetchone()[0]
print(f"Total players in SQLite: {count}")

# Show all players
cur.execute("SELECT username, email FROM players")
rows = cur.fetchall()

print("\nAll players:")
for i, row in enumerate(rows, 1):
    print(f"{i}. Username: {row[0]}, Email: {row[1]}")

conn.close()
