"""Read-only public product statistics backed by the application database."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models import Challenge, Match, MatchStatus, Player

router = APIRouter()


@router.get("/stats")
async def public_stats(db: Session = Depends(get_db)):
    """Return exact counters; the landing page never invents adoption data."""

    return {
        "players": db.query(Player).count(),
        "battles": db.query(Match).filter(Match.status == MatchStatus.CONCLUDED).count(),
        "challenges": db.query(Challenge).count(),
        "active_battles": db.query(Match).filter(Match.status == MatchStatus.ACTIVE).count(),
    }
