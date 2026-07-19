#!/usr/bin/env python3
"""
Migrate SQLite database to PostgreSQL for Render deployment
Works without SSL from Windows
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import sys
import os

def migrate_sqlite_to_postgres(sqlite_path, postgres_url):
    """Migrate data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    print(f"Connecting to SQLite: {sqlite_path}")
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()
    
    # Require encrypted transport by default. Override only for an explicitly
    # local development database.
    print(f"Connecting to PostgreSQL...")
    pg_conn = psycopg2.connect(
        postgres_url,
        sslmode=os.getenv("POSTGRES_SSLMODE", "require"),
    )
    
    print("✅ Connected to PostgreSQL")
    pg_cur = pg_conn.cursor()
    
    # Get all tables
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in sqlite_cur.fetchall()]
    
    print(f"\nFound {len(tables)} tables to migrate: {tables}\n")
    
    for table in tables:
        print(f"Migrating table: {table}")
        
        # Get all rows from SQLite
        sqlite_cur.execute(f"SELECT * FROM {table}")
        rows = sqlite_cur.fetchall()
        
        if not rows:
            print(f"  No data in {table}\n")
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
            print(f"  ✅ Migrated {len(data)} rows\n")
        except Exception as e:
            print(f"  ❌ Error migrating {table}: {e}\n")
            pg_conn.rollback()
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print("✅ Migration complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres.py <sqlite_path> [postgres_url]")
        print("\nIf postgres_url is omitted, set TARGET_DATABASE_URL.")
        print("\nExample:")
        print("  python migrate_to_postgres.py backend/coderoad.db")
        print("  TARGET_DATABASE_URL='<provider connection string>' python migrate_to_postgres.py backend/coderoad.db")
        sys.exit(1)
    
    sqlite_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        postgres_url = sys.argv[2]
    else:
        postgres_url = os.getenv("TARGET_DATABASE_URL")
        if not postgres_url:
            print("TARGET_DATABASE_URL is required when no URL argument is supplied")
            sys.exit(1)
        print("Using TARGET_DATABASE_URL from the environment\n")
    
    migrate_sqlite_to_postgres(sqlite_path, postgres_url)
