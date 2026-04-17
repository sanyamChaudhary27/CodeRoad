"""
Add this endpoint to EC2's backend to export database
Deploy this to EC2, then call the endpoint to get all data
"""

from fastapi import APIRouter
from sqlalchemy import text
from ..core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/all-data")
async def export_all_data(db: Session = Depends(get_db)):
    """Export all database tables as JSON"""
    
    tables = ['players', 'matches', 'submissions', 'challenges', 'ratings', 'rating_history']
    export_data = {}
    
    for table in tables:
        try:
            result = db.execute(text(f"SELECT * FROM {table}"))
            rows = result.fetchall()
            columns = result.keys()
            
            export_data[table] = [
                dict(zip(columns, row)) for row in rows
            ]
        except Exception as e:
            export_data[table] = {"error": str(e)}
    
    return export_data
