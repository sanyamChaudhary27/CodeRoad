"""XGBoost-based integrity service for AI/Paste detection"""

import logging
import os
import pickle
import re
import numpy as np
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional, List

from ..models import Submission, Player

logger = logging.getLogger(__name__)

# Try to import XGBoost
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    logger.warning("XGBoost not installed - XGB classification disabled")


class XGBIntegrityService:
    """Service for analyzing submission integrity using XGBoost model"""
    
    def __init__(self):
        """Initialize XGBoost model and label encoder"""
        self.model = None
        self.label_encoder = None
        self.model_available = False
        self.feature_names = [
            'time_to_first_submission',
            'keystroke_speed_avg',
            'keystroke_speed_variance',
            'deletion_ratio',
            'pasted_code_ratio',
            'external_source_similarity',
            'complexity_vs_optimal',
            'deviation_from_player_baseline',
            'success_rate',
            'efficiency_vs_player_avg'
        ]
        
        if XGB_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load XGBoost model and label encoder from disk"""
        try:
            # Try multiple possible paths
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '../../ml/training_data/classification_model/cheat_detection_model.pkl'),
                os.path.join(os.path.dirname(__file__), '../../../ml/training_data/classification_model/cheat_detection_model.pkl'),
                'ml/training_data/classification_model/cheat_detection_model.pkl',
            ]
            
            model_path = None
            encoder_path = None
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    encoder_path = path.replace('cheat_detection_model.pkl', 'label_encoder.pkl')
                    break
            
            if not model_path or not os.path.exists(encoder_path):
                logger.warning(f"Model files not found. Tried: {possible_paths}")
                return
            
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            self.model_available = True
            logger.info(f"XGBoost model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load XGBoost model: {e}")
    
    def extract_features(self, code: str, submission: Submission, player: Optional[Player] = None) -> Dict[str, float]:
        """Extract features from code and submission data"""
        features = {}
        
        # 1. Temporal Features
        features['time_to_first_submission'] = submission.time_to_first_submission or 30.0
        features['keystroke_speed_avg'] = submission.keystroke_speed_avg or 45.0
        features['keystroke_speed_variance'] = submission.keystroke_speed_variance or 10.0
        
        # 2. Keystroke Dynamics
        features['deletion_ratio'] = submission.deletion_ratio or 0.15
        features['pasted_code_ratio'] = submission.pasted_code_ratio or 0.0
        
        # 3. Paste Detection
        features['external_source_similarity'] = submission.external_source_similarity or 0.1
        
        # 4. Code Complexity
        features['complexity_vs_optimal'] = self._estimate_complexity(code)
        
        # 5. Player Baseline Deviation
        if player:
            features['deviation_from_player_baseline'] = self._calculate_deviation(submission, player)
        else:
            features['deviation_from_player_baseline'] = 0.0
        
        # 6. Success Rate
        features['success_rate'] = submission.success_rate or 0.5
        
        # 7. Efficiency
        features['efficiency_vs_player_avg'] = submission.efficiency_vs_player_avg or 1.0
        
        return features
    
    def _estimate_complexity(self, code: str) -> float:
        """Estimate code complexity vs optimal"""
        try:
            # Count loops and nested structures
            loops = len(re.findall(r'\b(for|while)\b', code))
            nested_loops = len(re.findall(r'(\bfor\b|\bwhile\b).*\n\s+(\bfor\b|\bwhile\b)', code))
            recursion = 1 if re.search(r'def\s+(\w+)\(.*\).* \1\(', code, re.DOTALL) else 0
            
            # Simple heuristic: optimal is 1.0, more complex is > 1.0
            complexity = 1.0 + (loops * 0.1) + (nested_loops * 0.2) + (recursion * 0.3)
            return min(complexity, 3.0)  # Cap at 3.0
        except Exception as e:
            logger.warning(f"Failed to estimate complexity: {e}")
            return 1.0
    
    def _calculate_deviation(self, submission: Submission, player: Player) -> float:
        """Calculate deviation from player's baseline"""
        try:
            # This would require historical data from player's previous submissions
            # For now, use a simple heuristic based on available data
            if not hasattr(player, 'avg_keystroke_speed'):
                return 0.0
            
            player_avg_speed = getattr(player, 'avg_keystroke_speed', 45.0)
            submission_speed = submission.keystroke_speed_avg or 45.0
            
            # Calculate normalized deviation
            deviation = abs(submission_speed - player_avg_speed) / max(player_avg_speed, 1.0)
            return min(deviation, 1.0)
        except Exception as e:
            logger.warning(f"Failed to calculate deviation: {e}")
            return 0.0
    
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict classification using XGBoost model"""
        if not self.model_available or self.model is None:
            logger.warning("XGBoost model not available, returning default prediction")
            return {
                'legitimate_probability': 0.7,
                'ai_assisted_probability': 0.2,
                'pasted_probability': 0.1,
                'predicted_class': 'legitimate',
                'confidence_score': 0.7,
                'model_available': False
            }
        
        try:
            # Prepare feature vector in correct order
            feature_vector = np.array([[
                features.get(name, 0.0) for name in self.feature_names
            ]])
            
            # Get predictions
            predictions = self.model.predict_proba(feature_vector)[0]
            predicted_class_idx = np.argmax(predictions)
            
            # Decode class label
            class_labels = ['legitimate', 'ai_assisted', 'pasted']
            if hasattr(self.label_encoder, 'classes_'):
                class_labels = self.label_encoder.classes_.tolist()
            
            predicted_class = class_labels[predicted_class_idx]
            confidence = float(predictions[predicted_class_idx])
            
            return {
                'legitimate_probability': float(predictions[0]) if len(predictions) > 0 else 0.0,
                'ai_assisted_probability': float(predictions[1]) if len(predictions) > 1 else 0.0,
                'pasted_probability': float(predictions[2]) if len(predictions) > 2 else 0.0,
                'predicted_class': predicted_class,
                'confidence_score': confidence,
                'model_available': True
            }
        except Exception as e:
            logger.error(f"XGBoost prediction failed: {e}")
            return {
                'legitimate_probability': 0.7,
                'ai_assisted_probability': 0.2,
                'pasted_probability': 0.1,
                'predicted_class': 'legitimate',
                'confidence_score': 0.7,
                'model_available': False,
                'error': str(e)
            }
    
    def analyze_submission(self, db: Session, submission_id: str) -> None:
        """
        Analyze a submission using XGBoost model
        """
        logger.info(f"Running XGBoost integrity analysis on {submission_id}")
        
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            logger.warning(f"Submission {submission_id} not found")
            return
        
        code = submission.code
        
        # Get player for baseline comparison
        player = None
        if hasattr(submission, 'player_id'):
            player = db.query(Player).filter(Player.id == submission.player_id).first()
        
        # 1. Extract features
        features = self.extract_features(code, submission, player)
        
        # 2. Get predictions
        prediction = self.predict(features)
        
        # 3. Store results in submission
        submission.ai_quality_score = prediction['ai_assisted_probability'] * 100
        submission.cheat_probability = prediction['pasted_probability'] * 100
        
        # Store classification result
        if prediction['predicted_class'] == 'legitimate':
            submission.integrity_status = 'legitimate'
        elif prediction['predicted_class'] == 'ai_assisted':
            submission.integrity_status = 'ai_assisted'
        else:
            submission.integrity_status = 'pasted'
        
        submission.integrity_confidence = prediction['confidence_score']
        submission.integrity_model_used = 'xgboost'
        
        db.commit()
        logger.info(
            f"XGBoost analysis complete for {submission_id}: "
            f"{prediction['predicted_class']} (confidence: {prediction['confidence_score']:.2f})"
        )


# Singleton instance
_xgb_service_instance = None

def get_xgb_integrity_service() -> XGBIntegrityService:
    """Get or create singleton instance of XGBIntegrityService"""
    global _xgb_service_instance
    if _xgb_service_instance is None:
        _xgb_service_instance = XGBIntegrityService()
    return _xgb_service_instance
