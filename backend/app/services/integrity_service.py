import logging
import os
import re
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import Submission, Player
# from .xgb_integrity_service import get_xgb_integrity_service

logger = logging.getLogger(__name__)

class IntegrityService:
    """Record inspectable behavioral signals without claiming AI detection."""
    
    def __init__(self):
        self.xgb_service = None
        logger.info("IntegrityService initialized with behavioral signals only")

    def analyze_submission(self, db: Session, submission_id: str) -> None:
        """
        Calculate simple, disclosed behavioral signals.
        """
        logger.info(f"Running integrity analysis on {submission_id}")
        
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return

        code = submission.code
        
        # 1. Behavioral Heuristics (Basic calculation)
        submission.code_length = len(code)
        submission.code_lines = len(code.split('\n'))
        submission.memory_used_mb = 0.1 + (len(code) / 10000.0)

        # Time Complexity Heuristic (Nested loops detection)
        loops = len(re.findall(r'\b(for|while)\b', code))
        nested_loops = len(re.findall(r'(\bfor\b|\bwhile\b).*\n\s+(\bfor\b|\bwhile\b)', code))
        recursion = 1 if re.search(r'def\s+(\w+)\(.*\).* \1\(', code, re.DOTALL) else 0
        
        complexity_impact = (loops * 10) + (nested_loops * 20) + (recursion * 30)
        submission.complexity_score = max(0, min(100, 100 - complexity_impact))

        if submission.copy_paste_events > 0:
            submission.code_paste_probability = min(100.0, submission.copy_paste_events * 25.0)
        
        # Paste events are the only integrity signal currently collected. This
        # is deliberately not described as cheating or AI-use detection.
        paste_prob = submission.code_paste_probability or 0.0
        overall = paste_prob
        submission.cheat_probability = min(100.0, overall)
        submission.integrity_model_used = 'behavioral_signals_v1'
        
        db.commit()
        logger.info(
            "Behavioral signal analysis complete for %s (paste signal: %.1f%%)",
            submission_id,
            overall,
        )
