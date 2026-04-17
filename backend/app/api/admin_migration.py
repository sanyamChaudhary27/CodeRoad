"""
Temporary admin endpoint for data migration
DELETE THIS FILE AFTER MIGRATION IS COMPLETE
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import tempfile
import os
import logging

from ..config import settings
from ..core.security import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

# SECURITY: Only enable in production for migration, then remove
MIGRATION_ENABLED = os.getenv("ENABLE_MIGRATION", "false").lower() == "true"

@router.post("/migrate-database")
async def migrate_database(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload SQLite database and migrate to PostgreSQL
    
    SECURITY: This endpoint should be removed after migration
    """
    if not MIGRATION_ENABLED:
        raise HTTPException(status_code=403, detail="Migration endpoint is disabled")
    
    # Additional security: check if user is admin (you can add admin field to user model)
    # For now, just log who's doing the migration
    logger.warning(f"Migration initiated by user: {current_user.get('username')}")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        logger.info(f"SQLite file saved to: {tmp_file_path}")
        
        # Connect to SQLite
        sqlite_engine = create_engine(f"sqlite:///{tmp_file_path}")
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        
        # Connect to PostgreSQL
        postgres_engine = create_engine(settings.DATABASE_URL)
        PostgresSession = sessionmaker(bind=postgres_engine)
        postgres_session = PostgresSession()
        
        migration_results = {}
        
        # Get all table names from SQLite
        result = sqlite_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ))
        tables = [row[0] for row in result.fetchall()]
        
        logger.info(f"Found {len(tables)} tables to migrate: {tables}")
        
        for table in tables:
            logger.info(f"Migrating table: {table}")
            
            # Get all rows from SQLite
            rows = sqlite_session.execute(text(f"SELECT * FROM {table}")).fetchall()
            
            if not rows:
                migration_results[table] = {"status": "empty", "rows": 0}
                continue
            
            # Get column names
            columns = rows[0]._mapping.keys()
            columns_str = ', '.join(columns)
            placeholders = ', '.join([f':{col}' for col in columns])
            
            # Insert into PostgreSQL
            insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
            migrated_count = 0
            errors = []
            
            for row in rows:
                try:
                    row_dict = dict(row._mapping)
                    postgres_session.execute(text(insert_query), row_dict)
                    migrated_count += 1
                except Exception as e:
                    errors.append(str(e))
                    continue
            
            postgres_session.commit()
            
            migration_results[table] = {
                "status": "success",
                "total_rows": len(rows),
                "migrated_rows": migrated_count,
                "errors": len(errors),
                "sample_errors": errors[:3] if errors else []
            }
            
            logger.info(f"Migrated {migrated_count}/{len(rows)} rows from {table}")
        
        # Cleanup
        sqlite_session.close()
        postgres_session.close()
        os.unlink(tmp_file_path)
        
        return {
            "status": "success",
            "message": "Database migration completed",
            "results": migration_results
        }
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@router.get("/migration-status")
async def migration_status():
    """Check if migration endpoint is enabled"""
    return {
        "migration_enabled": MIGRATION_ENABLED,
        "database_type": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
    }
