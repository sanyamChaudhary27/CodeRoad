"""
Data migration endpoint - accepts JSON data and inserts into PostgreSQL
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from typing import List, Dict, Any
import logging

from ..core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/migrate", tags=["migration"])
logger = logging.getLogger(__name__)

@router.post("/table")
async def migrate_table(
    table_name: str,
    data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Migrate data for a specific table
    
    Args:
        table_name: Name of the table
        data: List of row dictionaries
    """
    if not data:
        return {"status": "success", "message": "No data to migrate", "migrated": 0}
    
    try:
        migrated_count = 0
        errors = []
        
        # Get column names from first row
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join([f':{col}' for col in columns])
        
        # Insert query with conflict handling
        insert_query = text(f"""
            INSERT INTO {table_name} ({columns_str}) 
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """)
        
        for row in data:
            try:
                db.execute(insert_query, row)
                migrated_count += 1
            except Exception as e:
                errors.append(str(e))
                logger.error(f"Error inserting row into {table_name}: {e}")
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "table": table_name,
            "total_rows": len(data),
            "migrated": migrated_count,
            "errors": len(errors),
            "sample_errors": errors[:3] if errors else []
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Migration failed for {table_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@router.get("/status")
async def migration_status():
    """Check migration endpoint status"""
    return {
        "status": "ready",
        "message": "Migration endpoint is active"
    }
