"""Initialize database on first run"""
from app.core.database import engine, Base
from app.models import Player, Match, Challenge, Submission, MatchQueue

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")
