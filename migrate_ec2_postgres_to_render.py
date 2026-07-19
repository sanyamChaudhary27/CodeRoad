#!/usr/bin/env python3
"""
Migrate data from EC2 PostgreSQL to Render PostgreSQL
Connects to both databases and copies all data
"""
import psycopg2
from psycopg2.extras import execute_values
import sys
import os

EC2_DB_URL = os.getenv("SOURCE_DATABASE_URL")
RENDER_DB_URL = os.getenv("TARGET_DATABASE_URL")

def migrate_postgres_to_postgres():
    """Migrate data from EC2 PostgreSQL to Render PostgreSQL"""
    if not EC2_DB_URL or not RENDER_DB_URL:
        raise RuntimeError("Set SOURCE_DATABASE_URL and TARGET_DATABASE_URL before migrating")
    
    print("Connecting to EC2 PostgreSQL...")
    try:
        ec2_conn = psycopg2.connect(EC2_DB_URL)
        ec2_cur = ec2_conn.cursor()
        print("✅ Connected to EC2 PostgreSQL\n")
    except Exception as e:
        print(f"❌ Failed to connect to EC2: {e}")
        return
    
    print("Connecting to Render PostgreSQL...")
    try:
        render_conn = psycopg2.connect(RENDER_DB_URL)
        render_cur = render_conn.cursor()
        print("✅ Connected to Render PostgreSQL\n")
    except Exception as e:
        print(f"❌ Failed to connect to Render: {e}")
        return
    
    # Get all tables from EC2
    ec2_cur.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = [row[0] for row in ec2_cur.fetchall()]
    
    print(f"Found {len(tables)} tables: {tables}\n")
    
    total_migrated = 0
    
    for table in tables:
        print(f"Migrating table: {table}")
        
        # Get all rows from EC2
        try:
            ec2_cur.execute(f"SELECT * FROM {table}")
            rows = ec2_cur.fetchall()
            
            if not rows:
                print(f"  No data in {table}\n")
                continue
            
            # Get column names
            columns = [desc[0] for desc in ec2_cur.description]
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            
            # Insert into Render
            try:
                execute_values(
                    render_cur,
                    f"INSERT INTO {table} ({columns_str}) VALUES %s ON CONFLICT DO NOTHING",
                    rows,
                    template=f"({placeholders})"
                )
                render_conn.commit()
                total_migrated += len(rows)
                print(f"  ✅ Migrated {len(rows)} rows\n")
            except Exception as e:
                print(f"  ❌ Error migrating {table}: {e}\n")
                render_conn.rollback()
                
        except Exception as e:
            print(f"  ❌ Error reading {table}: {e}\n")
    
    # Close connections
    ec2_conn.close()
    render_conn.close()
    
    print(f"✅ Migration complete! Total rows migrated: {total_migrated}")

if __name__ == "__main__":
    migrate_postgres_to_postgres()
