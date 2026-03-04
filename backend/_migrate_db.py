"""
Database migration script for sanyam-frontend branch.
Adds all missing columns to existing SQLite database.
"""
import sqlite3

DB_PATH = 'd:/CodeRoad/backend/coderoad.db'

def get_existing_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}

def add_column(cursor, table, col_name, col_type, default=None):
    existing = get_existing_columns(cursor, table)
    if col_name in existing:
        return False
    if default is not None:
        sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type} DEFAULT {default}"
    else:
        sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
    cursor.execute(sql)
    return True

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    changes = []
    
    # matches table - add challenge_type
    if add_column(cursor, 'matches', 'challenge_type', "VARCHAR(20) NOT NULL", "'dsa'"):
        changes.append("matches.challenge_type")
    
    # match_queue table - add challenge_type
    if add_column(cursor, 'match_queue', 'challenge_type', "VARCHAR(20) NOT NULL", "'dsa'"):
        changes.append("match_queue.challenge_type")
    
    # challenges table - add challenge_type
    if add_column(cursor, 'challenges', 'challenge_type', "VARCHAR(20) NOT NULL", "'dsa'"):
        changes.append("challenges.challenge_type")
    
    # ratings table - add challenge_type
    if add_column(cursor, 'ratings', 'challenge_type', "VARCHAR(20) NOT NULL", "'dsa'"):
        changes.append("ratings.challenge_type")
    
    # submissions - pasted_code_ratio, external_source_similarity, integrity_status, integrity_confidence, integrity_model_used
    # (these likely already exist from the schema, but just in case)
    submission_cols = [
        ('integrity_status', 'VARCHAR(50)', None),
        ('integrity_confidence', 'FLOAT', None),
        ('integrity_model_used', 'VARCHAR(50)', None),
        ('pasted_code_ratio', 'FLOAT', None),
        ('external_source_similarity', 'FLOAT', None),
        ('success_rate', 'FLOAT', None),
        ('efficiency_vs_player_avg', 'FLOAT', None),
    ]
    for col_name, col_type, default in submission_cols:
        if add_column(cursor, 'submissions', col_name, col_type, default):
            changes.append(f"submissions.{col_name}")
    
    conn.commit()
    conn.close()
    
    if changes:
        print(f"Migration complete! Added {len(changes)} columns:")
        for c in changes:
            print(f"  + {c}")
    else:
        print("No migration needed - all columns already exist.")

if __name__ == "__main__":
    migrate()
