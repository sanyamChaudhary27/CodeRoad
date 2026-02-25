# Import all models for easier access
from .player import Player, Badge
from .match import Match, MatchQueue, Tournament, MatchStatus, MatchFormat
from .submission import Submission, Challenge, TestCase, SubmissionStatus, ProgrammingLanguage
from .integrity import IntegrityAnalysis, PlayerIntegrityProfile, IntegrityAuditLog
from .rating import Rating, RatingHistory

# Re-export for easier imports
__all__ = [
    # Player models
    'Player', 'Badge',
    # Match models
    'Match', 'MatchQueue', 'Tournament', 'MatchStatus', 'MatchFormat',
    # Submission models
    'Submission', 'Challenge', 'TestCase', 'SubmissionStatus', 'ProgrammingLanguage',
    # Integrity models
    'IntegrityAnalysis', 'PlayerIntegrityProfile', 'IntegrityAuditLog',
    # Rating models
    'Rating', 'RatingHistory'
]