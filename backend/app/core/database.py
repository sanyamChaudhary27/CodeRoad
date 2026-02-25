from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from ..config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with SQLite support for local development
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=30,
        pool_recycle=3600,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Database session closed")
        db.close()

def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This should be called during application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def drop_db() -> None:
    """
    Drop all database tables.
    
    Warning: This will delete all data!
    Only use for development/testing.
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("Database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

# Import all models to ensure they are registered with Base
from ..models import *  # noqa

# Create tables on import if in debug mode
if settings.DEBUG:
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Could not initialize database: {e}")