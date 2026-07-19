#!/usr/bin/env python3
"""
Run this script on EC2 to export all database data to JSON
"""
import psycopg2
import json
import sys
import os

DB_URL = os.getenv("SOURCE_DATABASE_URL")

def export_database():
    """Export all database tables to JSON"""
    if not DB_URL:
        raise RuntimeError("Set SOURCE_DATABASE_URL before running this export")
    
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    print("Connected!\n")
    
    # Get all tables
    cur.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    print(f"Found {len(tables)} tables: {tables}\n")
    
    export_data = {}
    
    for table in tables:
        print(f"Exporting {table}...")
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        export_data[table] = {
            "columns": columns,
            "rows": [list(row) for row in rows]
        }
        print(f"  {len(rows)} rows\n")
    
    # Save to file
    with open('/tmp/coderoad_export.json', 'w') as f:
        json.dump(export_data, f, default=str, indent=2)
    
    conn.close()
    print("✅ Export complete! Saved to /tmp/coderoad_export.json")

if __name__ == "__main__":
    export_database()
