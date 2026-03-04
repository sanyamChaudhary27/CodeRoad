"""
Migration script to add Debug Arena columns to existing database
Run this script to update your database schema for Debug Arena feature
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
    """Add Debug Arena columns to existing tables"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    migrations = [
        # Add challenge_type to challenges table
        """
        ALTER TABLE challenges 
        ADD COLUMN IF NOT EXISTS challenge_type VARCHAR(20) DEFAULT 'dsa' NOT NULL;
        """,
        
        # Add debug-specific columns to challenges table
        """
        ALTER TABLE challenges 
        ADD COLUMN IF NOT EXISTS broken_code TEXT,
        ADD COLUMN IF NOT EXISTS bug_count INTEGER,
        ADD COLUMN IF NOT EXISTS bug_types TEXT;
        """,
        
        # Add debug rating columns to players table
        """
        ALTER TABLE players 
        ADD COLUMN IF NOT EXISTS debug_rating INTEGER DEFAULT 300 NOT NULL,
        ADD COLUMN IF NOT EXISTS debug_rating_confidence FLOAT DEFAULT 100.0 NOT NULL,
        ADD COLUMN IF NOT EXISTS debug_matches_played INTEGER DEFAULT 0 NOT NULL,
        ADD COLUMN IF NOT EXISTS debug_wins INTEGER DEFAULT 0 NOT NULL,
        ADD COLUMN IF NOT EXISTS debug_losses INTEGER DEFAULT 0 NOT NULL,
        ADD COLUMN IF NOT EXISTS debug_draws INTEGER DEFAULT 0 NOT NULL;
        """,
        
        # Add challenge_type to ratings table and remove unique constraint
        """
        ALTER TABLE ratings 
        DROP CONSTRAINT IF EXISTS ratings_player_id_key;
        """,
        
        """
        ALTER TABLE ratings 
        ADD COLUMN IF NOT EXISTS challenge_type VARCHAR(20) DEFAULT 'dsa' NOT NULL;
        """,
        
        # Add challenge_type to matches table
        """
        ALTER TABLE matches 
        ADD COLUMN IF NOT EXISTS challenge_type VARCHAR(20) DEFAULT 'dsa' NOT NULL;
        """,
    ]
    
    try:
        with engine.connect() as conn:
            for i, migration in enumerate(migrations, 1):
                try:
                    logger.info(f"Running migration {i}/{len(migrations)}...")
                    conn.execute(text(migration))
                    conn.commit()
                    logger.info(f"Migration {i} completed successfully")
                except Exception as e:
                    logger.error(f"Migration {i} failed: {e}")
                    # Continue with other migrations
                    continue
        
        logger.info("All migrations completed!")
        logger.info("\nDebug Arena database schema updated successfully!")
        logger.info("You can now use the Debug Arena feature.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    logger.info("Starting Debug Arena database migration...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    response = input("\nThis will modify your database schema. Continue? (yes/no): ")
    if response.lower() == 'yes':
        migrate_database()
    else:
        logger.info("Migration cancelled")
