"""
Auto-migration script that runs on startup to restore data if database is empty
"""
import logging
import requests
from sqlalchemy.orm import Session
from .database import get_db, engine
from ..models import Player

logger = logging.getLogger(__name__)

MIGRATION_DATA_URL = "https://raw.githubusercontent.com/sanyamChaudhary27/CodeRoad/main/coderoad_production_export.json"

def check_and_migrate():
    """Check if database is empty and restore from backup if needed"""
    try:
        # Check if database has data
        db = next(get_db())
        player_count = db.query(Player).count()
        
        if player_count == 0:
            logger.warning("Database is empty! Attempting auto-restore...")
            restore_from_backup()
        else:
            logger.info(f"Database has {player_count} players - no restore needed")
            
    except Exception as e:
        logger.error(f"Auto-migration check failed: {e}")

def restore_from_backup():
    """Restore database from GitHub backup"""
    try:
        logger.info("Downloading backup data from GitHub...")
        response = requests.get(MIGRATION_DATA_URL, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Failed to download backup: {response.status_code}")
            return
            
        data = response.json()
        logger.info(f"Downloaded {len(data)} tables")
        
        # Import data via migration endpoint
        import os
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        
        total_migrated = 0
        for table, table_data in data.items():
            columns = table_data['columns']
            rows = table_data['rows']
            
            if not rows:
                continue
                
            logger.info(f"Restoring {table}: {len(rows)} rows...")
            
            rows_as_dicts = [dict(zip(columns, row)) for row in rows]
            
            try:
                resp = requests.post(
                    f"{base_url}/api/v1/migrate/table",
                    params={"table_name": table},
                    json=rows_as_dicts,
                    timeout=120
                )
                
                if resp.status_code == 200:
                    result = resp.json()
                    migrated = result.get('migrated', 0)
                    total_migrated += migrated
                    logger.info(f"  ✅ Restored {migrated}/{len(rows)} rows")
                else:
                    logger.error(f"  ❌ Error: {resp.status_code}")
            except Exception as e:
                logger.error(f"  ❌ Error restoring {table}: {e}")
        
        logger.info(f"✅ Auto-restore complete! Total rows: {total_migrated}")
        
    except Exception as e:
        logger.error(f"Auto-restore failed: {e}")
