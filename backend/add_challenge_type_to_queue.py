"""
Migration script to add challenge_type column to match_queue table
Run this script to enable Debug Arena 1v1 matchmaking
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add challenge_type column to match_queue table"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    migration = """
    ALTER TABLE match_queue 
    ADD COLUMN challenge_type VARCHAR(20) DEFAULT 'dsa' NOT NULL;
    """
    
    try:
        with engine.connect() as conn:
            try:
                logger.info("Adding challenge_type column to match_queue table...")
                conn.execute(text(migration))
                conn.commit()
                logger.info("Migration completed successfully!")
                logger.info("\nDebug Arena 1v1 matchmaking is now enabled!")
            except Exception as e:
                # Check if column already exists
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info("Migration skipped - column already exists")
                else:
                    logger.error(f"Migration failed: {e}")
                    raise
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    logger.info("Starting match_queue migration...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    response = input("\nThis will modify your database schema. Continue? (yes/no): ")
    if response.lower() == 'yes':
        migrate_database()
    else:
        logger.info("Migration cancelled")
