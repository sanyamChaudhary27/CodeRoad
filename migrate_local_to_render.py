#!/usr/bin/env python3
"""
Migrate SQLite database to Render PostgreSQL via API
Works from local Windows machine
"""
import sqlite3
import requests
import json
import sys

def migrate_via_api(sqlite_path, backend_url):
    """Migrate data by sending it via API to Render backend"""
    
    print(f"Reading SQLite database: {sqlite_path}\n")
    
    # Connect to SQLite
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]
    
    print(f"Found {len(tables)} tables: {tables}\n")
    
    # Check if migration endpoint is ready
    try:
        status_response = requests.get(f"{backend_url}/api/v1/migrate/status")
        if status_response.status_code == 200:
            print("✅ Migration endpoint is ready\n")
        else:
            print(f"⚠️  Migration endpoint returned: {status_response.status_code}\n")
    except Exception as e:
        print(f"❌ Cannot reach migration endpoint: {e}\n")
        return
    
    # Migrate each table
    total_migrated = 0
    for table in tables:
        print(f"Migrating table: {table}")
        
        # Get all rows
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        
        if not rows:
            print(f"  No data in {table}\n")
            continue
        
        # Get column names
        columns = [description[0] for description in cur.description]
        
        # Convert rows to list of dicts
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        # Send to backend
        try:
            response = requests.post(
                f"{backend_url}/api/v1/migrate/table",
                params={"table_name": table},
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                migrated = result.get('migrated', 0)
                total_migrated += migrated
                print(f"  ✅ Migrated {migrated}/{len(data)} rows")
                if result.get('errors', 0) > 0:
                    print(f"  ⚠️  {result['errors']} errors occurred")
                    if result.get('sample_errors'):
                        print(f"  Sample errors: {result['sample_errors'][:2]}")
                print()
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    conn.close()
    print(f"✅ Migration complete! Total rows migrated: {total_migrated}")

if __name__ == "__main__":
    # Configuration
    SQLITE_PATH = "backend/coderoad.db"
    BACKEND_URL = "https://coderoad-gmq6.onrender.com"
    
    if len(sys.argv) > 1:
        SQLITE_PATH = sys.argv[1]
    
    if len(sys.argv) > 2:
        BACKEND_URL = sys.argv[2]
    
    print(f"SQLite: {SQLITE_PATH}")
    print(f"Backend: {BACKEND_URL}\n")
    
    migrate_via_api(SQLITE_PATH, BACKEND_URL)
