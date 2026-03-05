import logging
import os
import re
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import Submission, Player
from .xgb_integrity_service import get_xgb_integrity_service

logger = logging.getLogger(__name__)

class IntegrityService:
    """Service for analyzing submission integrity using XGBoost model."""
    
    def __init__(self):
        # Use XGBoost model only (no AI providers)
        self.xgb_service = get_xgb_integrity_service()
        logger.info("IntegrityService initialized with XGBoost model")

    def analyze_submission(self, db: Session, submission_id: str) -> None:
        """
        Analyze a submission using XGBoost model only.
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
        
        # 2. Use XGBoost Model
        if self.xgb_service.model_available:
            try:
                logger.info(f"Using XGBoost model for {submission_id}")
                self.xgb_service.analyze_submission(db, submission_id)
                logger.info(f"XGBoost analysis successful for {submission_id}")
            except Exception as e:
                logger.warning(f"XGBoost analysis failed: {e}")
                # Set default values if XGBoost fails
                submission.ai_assisted_probability = 0.0
        else:
            logger.warning("XGBoost model not available, using default values")
            submission.cheat_probability = 0.0
        
        # Use paste probability as the main indicator
        # (XGBoost model already provides cheat detection)
        paste_prob = submission.code_paste_probability or 0.0
        xgb_prob = submission.cheat_probability or 0.0
        
        # Combine paste detection with XGBoost analysis
        overall = max(paste_prob, xgb_prob)  # Use the higher probability
        submission.cheat_probability = min(100.0, overall)
        submission.integrity_model_used = 'xgboost'
        
        db.commit()
        logger.info(f"Integrity analysis complete for {submission_id} (Cheat Prob: {overall:.1f}%)")