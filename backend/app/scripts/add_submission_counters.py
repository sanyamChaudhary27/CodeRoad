import sqlite3
import os

def migrate():
    db_path = os.path.join(os.getcwd(), 'coderoad.db')
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    print(f"Migrating database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(matches)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'player1_submissions' not in columns:
            print("Adding player1_submissions column...")
            cursor.execute("ALTER TABLE matches ADD COLUMN player1_submissions INTEGER DEFAULT 0 NOT NULL")
        else:
            print("player1_submissions column already exists.")

        if 'player2_submissions' not in columns:
            print("Adding player2_submissions column...")
            cursor.execute("ALTER TABLE matches ADD COLUMN player2_submissions INTEGER DEFAULT 0 NOT NULL")
        else:
            print("player2_submissions column already exists.")

        conn.commit()
        print("Migration successful!")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
