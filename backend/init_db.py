#!/usr/bin/env python3
"""
Initialize database tables for Render deployment
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, engine
from app.models import *  # Import all models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Creating database tables...")
        init_db()
        logger.info("✅ Database tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Created tables: {tables}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        sys.exit(1)
