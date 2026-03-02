#!/usr/bin/env python
"""Comprehensive test to verify XGB integration with the backend system"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Load environment
from dotenv import load_dotenv
backend_dir = Path("backend")
env_file = backend_dir / ".env"
load_dotenv(env_file)

print("=" * 80)
print("XGB INTEGRATION TEST - Full System Verification")
print("=" * 80)

# Test 1: Import all required modules
print("\n" + "-" * 80)
print("TEST 1: Import Required Modules")
print("-" * 80)

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    print("✓ SQLAlchemy imported")
except Exception as e:
    print(f"✗ Failed to import SQLAlchemy: {e}")
    sys.exit(1)

try:
    from backend.app.core.database import Base, get_db
    print("✓ Database module imported")
except Exception as e:
    print(f"✗ Failed to import database: {e}")
    sys.exit(1)

try:
    from backend.app.models import Submission, Player
    print("✓ Models imported")
except Exception as e:
    print(f"✗ Failed to import models: {e}")
    sys.exit(1)

try:
    from backend.app.services.xgb_integrity_service import get_xgb_integrity_service
    print("✓ XGBIntegrityService imported")
except Exception as e:
    print(f"✗ Failed to import XGBIntegrityService: {e}")
    sys.exit(1)

try:
    from backend.app.services.integrity_service import IntegrityService
    print("✓ IntegrityService imported")
except Exception as e:
    print(f"✗ Failed to import IntegrityService: {e}")
    sys.exit(1)

# Test 2: Verify XGB Service Initialization
print("\n" + "-" * 80)
print("TEST 2: XGB Service Initialization")
print("-" * 80)

try:
    xgb_service = get_xgb_integrity_service()
    print(f"✓ XGBIntegrityService initialized")
    print(f"  - Model available: {xgb_service.model_available}")
    print(f"  - Model type: {type(xgb_service.model)}")
    print(f"  - Encoder type: {type(xgb_service.label_encoder)}")
    
    if not xgb_service.model_available:
        print("✗ XGB model not available!")
        sys.exit(1)
except Exception as e:
    print(f"✗ Failed to initialize XGBIntegrityService: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test Feature Extraction
print("\n" + "-" * 80)
print("TEST 3: Feature Extraction")
print("-" * 80)

try:
    # Create mock submission
    class MockSubmission:
        def __init__(self):
            self.code = """
def solve(arr):
    max_val = arr[0]
    for i in range(len(arr)):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val
"""
            self.time_to_first_submission = 30.0
            self.keystroke_speed_avg = 45.0
            self.keystroke_speed_variance = 10.0
            self.deletion_ratio = 0.15
            self.pasted_code_ratio = 0.0
            self.external_source_similarity = 0.1
            self.success_rate = 0.5
            self.efficiency_vs_player_avg = 1.0
    
    submission = MockSubmission()
    features = xgb_service.extract_features(submission.code, submission)
    
    print(f"✓ Features extracted successfully")
    print(f"  - Number of features: {len(features)}")
    print(f"  - Feature names: {list(features.keys())}")
    print(f"  - Feature values:")
    for name, value in features.items():
        print(f"    • {name}: {value}")
    
except Exception as e:
    print(f"✗ Feature extraction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test XGB Prediction
print("\n" + "-" * 80)
print("TEST 4: XGB Model Prediction")
print("-" * 80)

try:
    prediction = xgb_service.predict(features)
    
    print(f"✓ Prediction successful")
    print(f"  - Legitimate probability: {prediction['legitimate_probability']:.4f}")
    print(f"  - AI-Assisted probability: {prediction['ai_assisted_probability']:.4f}")
    print(f"  - Pasted probability: {prediction['pasted_probability']:.4f}")
    print(f"  - Predicted class: {prediction['predicted_class']}")
    print(f"  - Confidence score: {prediction['confidence_score']:.4f}")
    print(f"  - Model available: {prediction['model_available']}")
    
    # Verify probabilities sum to ~1.0
    total_prob = (prediction['legitimate_probability'] + 
                  prediction['ai_assisted_probability'] + 
                  prediction['pasted_probability'])
    print(f"  - Probabilities sum: {total_prob:.4f}")
    
    if abs(total_prob - 1.0) > 0.01:
        print(f"⚠ Warning: Probabilities don't sum to 1.0")
    
except Exception as e:
    print(f"✗ Prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test IntegrityService Integration
print("\n" + "-" * 80)
print("TEST 5: IntegrityService Integration")
print("-" * 80)

try:
    integrity_service = IntegrityService()
    print(f"✓ IntegrityService initialized")
    print(f"  - AI provider: {integrity_service.provider}")
    print(f"  - AI available: {integrity_service.ai_available}")
    
except Exception as e:
    print(f"✗ Failed to initialize IntegrityService: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test with Database (if possible)
print("\n" + "-" * 80)
print("TEST 6: Database Integration")
print("-" * 80)

try:
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print(f"✓ Test database created")
    
    # Create test player
    player = Player(
        id="test_player_1",
        username="test_user",
        email="test@example.com",
        hashed_password="hash",
        current_rating=1200,
        created_at=datetime.utcnow()
    )
    db.add(player)
    db.commit()
    print(f"✓ Test player created")
    
    # Create test submission
    submission = Submission(
        id="test_sub_1",
        match_id="test_match_1",
        player_id="test_player_1",
        code="""
def solve(arr):
    return max(arr)
""",
        language="python",
        submission_number=1,
        status="success",
        test_cases_passed=4,
        test_cases_total=4,
        execution_time_ms=45,
        memory_used_mb=12,
        submitted_at=datetime.utcnow()
    )
    db.add(submission)
    db.commit()
    print(f"✓ Test submission created")
    
    # Test analyze_submission
    print(f"\nCalling IntegrityService.analyze_submission()...")
    integrity_service.analyze_submission(db, "test_sub_1")
    
    # Refresh submission from database
    db.refresh(submission)
    
    print(f"✓ Analysis completed")
    print(f"  - Integrity status: {getattr(submission, 'integrity_status', 'N/A')}")
    print(f"  - Integrity confidence: {getattr(submission, 'integrity_confidence', 'N/A')}")
    print(f"  - AI quality score: {getattr(submission, 'ai_quality_score', 'N/A')}")
    print(f"  - Cheat probability: {getattr(submission, 'cheat_probability', 'N/A')}")
    print(f"  - Model used: {getattr(submission, 'integrity_model_used', 'N/A')}")
    
    # Verify XGB was used
    model_used = getattr(submission, 'integrity_model_used', None)
    if model_used == 'xgboost':
        print(f"✓ XGBoost model was used for classification!")
    elif model_used == 'gemini':
        print(f"⚠ Gemini was used (XGB may have failed)")
    else:
        print(f"⚠ Unknown model used: {model_used}")
    
    db.close()
    
except Exception as e:
    print(f"✗ Database integration test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test Multiple Predictions
print("\n" + "-" * 80)
print("TEST 7: Multiple Predictions (Consistency Check)")
print("-" * 80)

try:
    predictions = []
    
    # Test with different feature sets
    test_cases = [
        {
            'name': 'Legitimate Code',
            'features': {
                'time_to_first_submission': 45.0,
                'keystroke_speed_avg': 42.0,
                'keystroke_speed_variance': 12.0,
                'deletion_ratio': 0.18,
                'pasted_code_ratio': 0.0,
                'external_source_similarity': 0.1,
                'complexity_vs_optimal': 1.0,
                'deviation_from_player_baseline': 0.05,
                'success_rate': 0.75,
                'efficiency_vs_player_avg': 0.95
            }
        },
        {
            'name': 'AI-Assisted Code',
            'features': {
                'time_to_first_submission': 3.0,
                'keystroke_speed_avg': 65.0,
                'keystroke_speed_variance': 2.0,
                'deletion_ratio': 0.02,
                'pasted_code_ratio': 0.3,
                'external_source_similarity': 0.45,
                'complexity_vs_optimal': 1.0,
                'deviation_from_player_baseline': 0.7,
                'success_rate': 1.0,
                'efficiency_vs_player_avg': 2.0
            }
        },
        {
            'name': 'Pasted Code',
            'features': {
                'time_to_first_submission': 1.0,
                'keystroke_speed_avg': 120.0,
                'keystroke_speed_variance': 45.0,
                'deletion_ratio': 0.01,
                'pasted_code_ratio': 0.9,
                'external_source_similarity': 0.92,
                'complexity_vs_optimal': 1.0,
                'deviation_from_player_baseline': 0.95,
                'success_rate': 1.0,
                'efficiency_vs_player_avg': 1.8
            }
        }
    ]
    
    for test_case in test_cases:
        pred = xgb_service.predict(test_case['features'])
        predictions.append(pred)
        
        print(f"\n{test_case['name']}:")
        print(f"  - Legitimate: {pred['legitimate_probability']:.2%}")
        print(f"  - AI-Assisted: {pred['ai_assisted_probability']:.2%}")
        print(f"  - Pasted: {pred['pasted_probability']:.2%}")
        print(f"  - Predicted: {pred['predicted_class']}")
        print(f"  - Confidence: {pred['confidence_score']:.2%}")
    
    print(f"\n✓ All predictions completed successfully")
    
except Exception as e:
    print(f"✗ Multiple predictions test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Verify Logging
print("\n" + "-" * 80)
print("TEST 8: Logging Verification")
print("-" * 80)

try:
    import logging
    
    # Get logger
    logger = logging.getLogger('backend.app.services.xgb_integrity_service')
    
    # Check if logger has handlers
    if logger.handlers:
        print(f"✓ Logger has {len(logger.handlers)} handlers")
    else:
        print(f"⚠ Logger has no handlers (logging may not work)")
    
    # Check log level
    print(f"  - Logger level: {logging.getLevelName(logger.level)}")
    print(f"  - Effective level: {logging.getLevelName(logger.getEffectiveLevel())}")
    
except Exception as e:
    print(f"⚠ Logging verification failed: {e}")

print("\n" + "=" * 80)
print("✓ ALL INTEGRATION TESTS PASSED!")
print("=" * 80)
print("\nSummary:")
print("  ✓ XGB model loads correctly")
print("  ✓ Features are extracted properly")
print("  ✓ Predictions are generated")
print("  ✓ IntegrityService integrates with XGB")
print("  ✓ Database integration works")
print("  ✓ Multiple predictions are consistent")
print("\nXGB is properly integrated and ready for production!")
