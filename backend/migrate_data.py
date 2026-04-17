#!/usr/bin/env python3
"""
Data migration script to run on Render after deployment
This script reads from the SQLite backup and writes to PostgreSQL
"""
import sys
import os
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_data(sqlite_path: str, postgres_url: str):
    """Migrate data from SQLite to PostgreSQL"""
    
    logger.info(f"Connecting to SQLite: {sqlite_path}")
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SQLiteSession()
    
    logger.info(f"Connecting to PostgreSQL...")
    postgres_engine = create_engine(postgres_url)
    PostgresSession = sessionmaker(bind=postgres_engine)
    postgres_session = PostgresSession()
    
    try:
        # Get all table names from SQLite
        result = sqlite_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ))
        tables = [row[0] for row in result.fetchall()]
        
        logger.info(f"Found {len(tables)} tables to migrate: {tables}")
        
        for table in tables:
            logger.info(f"\nMigrating table: {table}")
            
            # Get all rows from SQLite
            rows = sqlite_session.execute(text(f"SELECT * FROM {table}")).fetchall()
            
            if not rows:
                logger.info(f"  No data in {table}")
                continue
            
            # Get column names
            columns = rows[0]._mapping.keys()
            columns_str = ', '.join(columns)
            placeholders = ', '.join([f':{col}' for col in columns])
            
            logger.info(f"  Found {len(rows)} rows with columns: {list(columns)}")
            
            # Insert into PostgreSQL
            insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
            migrated_count = 0
            for row in rows:
                try:
                    row_dict = dict(row._mapping)
                    postgres_session.execute(text(insert_query), row_dict)
                    migrated_count += 1
                except Exception as e:
                    logger.warning(f"  Error inserting row: {e}")
                    continue
            
            postgres_session.commit()
            logger.info(f"  ✅ Migrated {migrated_count}/{len(rows)} rows")
        
        logger.info("\n✅ Migration complete!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        postgres_session.rollback()
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate_data.py <sqlite_path> <postgres_url>")
        print("Example: python migrate_data.py coderoad.db $DATABASE_URL")
        sys.exit(1)
    
    sqlite_path = sys.argv[1]
    postgres_url = sys.argv[2]
    
    migrate_data(sqlite_path, postgres_url)
