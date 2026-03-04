import sqlite3

conn = sqlite3.connect('d:/CodeRoad/backend/coderoad.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)

# Show columns for each table
for t in tables:
    cursor.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cursor.fetchall()]
    print(f"\n{t}: {cols}")

conn.close()
