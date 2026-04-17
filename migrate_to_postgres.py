#!/usr/bin/env python3
"""
Migrate SQLite database to PostgreSQL for Render deployment
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import sys

def migrate_sqlite_to_postgres(sqlite_path, postgres_url):
    """Migrate data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()
    
    # Connect to PostgreSQL with SSL
    pg_conn = psycopg2.connect(postgres_url, sslmode='require')
    pg_cur = pg_conn.cursor()
    
    # Get all tables
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in sqlite_cur.fetchall()]
    
    print(f"Found {len(tables)} tables to migrate: {tables}")
    
    for table in tables:
        print(f"\nMigrating table: {table}")
        
        # Get all rows from SQLite
        sqlite_cur.execute(f"SELECT * FROM {table}")
        rows = sqlite_cur.fetchall()
        
        if not rows:
            print(f"  No data in {table}")
            continue
            
        # Get column names
        columns = [description[0] for description in sqlite_cur.description]
        
        # Convert rows to tuples
        data = [tuple(row) for row in rows]
        
        # Insert into PostgreSQL
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        
        try:
            execute_values(
                pg_cur,
                f"INSERT INTO {table} ({columns_str}) VALUES %s ON CONFLICT DO NOTHING",
                data,
                template=f"({placeholders})"
            )
            pg_conn.commit()
            print(f"  Migrated {len(data)} rows")
        except Exception as e:
            print(f"  Error migrating {table}: {e}")
            pg_conn.rollback()
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate_to_postgres.py <sqlite_path> <postgres_url>")
        print("Example: python migrate_to_postgres.py backend/coderoad.db 'postgresql://user:pass@host:5432/dbname'")
        sys.exit(1)
    
    sqlite_path = sys.argv[1]
    postgres_url = sys.argv[2]
    
    migrate_sqlite_to_postgres(sqlite_path, postgres_url)
