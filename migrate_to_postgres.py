#!/usr/bin/env python3
"""
Migrate SQLite database to PostgreSQL for Render deployment
Works without SSL from Windows
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import sys

def migrate_sqlite_to_postgres(sqlite_path, postgres_url):
    """Migrate data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    print(f"Connecting to SQLite: {sqlite_path}")
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()
    
    # Connect to PostgreSQL without SSL (try both ways)
    print(f"Connecting to PostgreSQL...")
    try:
        # Try without SSL first
        pg_conn = psycopg2.connect(postgres_url, sslmode='disable')
    except:
        try:
            # Try with SSL but don't verify
            pg_conn = psycopg2.connect(postgres_url, sslmode='require')
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            print("\nTrying alternative connection method...")
            # Parse URL and connect with individual parameters
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):?(\d+)?/(.+)', postgres_url)
            if match:
                user, password, host, port, dbname = match.groups()
                port = port or '5432'
                pg_conn = psycopg2.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    dbname=dbname,
                    sslmode='prefer'
                )
            else:
                raise e
    
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
        print("\nIf postgres_url is not provided, will use the one from DEPLOYMENT_SECRETS.md")
        print("\nExample:")
        print("  python migrate_to_postgres.py backend/coderoad.db")
        print("  python migrate_to_postgres.py backend/coderoad.db 'postgresql://user:pass@host:5432/dbname'")
        sys.exit(1)
    
    sqlite_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        postgres_url = sys.argv[2]
    else:
        # Default PostgreSQL URL from Render
        postgres_url = "postgresql://coderoad:sx24AaBRZyLk5LmPLx1000xxrqd8l1LBb@dpg-d7h3b4eqvct57bts8hg-a.oregon-postgres.render.com/coderoad"
        print(f"Using default PostgreSQL URL from Render\n")
    
    migrate_sqlite_to_postgres(sqlite_path, postgres_url)
