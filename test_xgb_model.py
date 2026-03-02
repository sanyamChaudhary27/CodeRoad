#!/usr/bin/env python
"""Test script to verify XGBoost model is working"""

import os
import sys
import pickle
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 80)
print("XGBoost Model Test")
print("=" * 80)

# Test 1: Check if model files exist
model_path = Path("ml/training_data/classification_model/cheat_detection_model.pkl")
encoder_path = Path("ml/training_data/classification_model/label_encoder.pkl")

print(f"\n✓ Model file exists: {model_path.exists()}")
print(f"✓ Encoder file exists: {encoder_path.exists()}")

if not model_path.exists() or not encoder_path.exists():
    print("✗ Model files not found!")
    sys.exit(1)

# Test 2: Load model
try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    sys.exit(1)

# Test 3: Load encoder
try:
    with open(encoder_path, 'rb') as f:
        encoder = pickle.load(f)
    print("✓ Label encoder loaded successfully")
except Exception as e:
    print(f"✗ Failed to load encoder: {e}")
    sys.exit(1)

# Test 4: Check model type
print(f"\nModel type: {type(model)}")
print(f"Encoder type: {type(encoder)}")

# Test 5: Try to make a prediction
try:
    import numpy as np
    
    # Create dummy feature vector (10 features as per the model)
    dummy_features = np.array([[
        30.0,  # time_to_first_submission
        45.0,  # keystroke_speed_avg
        10.0,  # keystroke_speed_variance
        0.15,  # deletion_ratio
        0.0,   # pasted_code_ratio
        0.1,   # external_source_similarity
        1.0,   # complexity_vs_optimal
        0.0,   # deviation_from_player_baseline
        0.5,   # success_rate
        1.0    # efficiency_vs_player_avg
    ]])
    
    predictions = model.predict_proba(dummy_features)
    predicted_class = model.predict(dummy_features)
    
    print(f"\n✓ Prediction successful!")
    print(f"  Probabilities: {predictions[0]}")
    print(f"  Predicted class: {predicted_class[0]}")
    
    if hasattr(encoder, 'classes_'):
        print(f"  Class labels: {encoder.classes_}")
    
except Exception as e:
    print(f"✗ Prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test XGBIntegrityService
print("\n" + "-" * 80)
print("Testing XGBIntegrityService")
print("-" * 80)

try:
    from backend.app.services.xgb_integrity_service import XGBIntegrityService
    
    service = XGBIntegrityService()
    print(f"✓ XGBIntegrityService initialized")
    print(f"  Model available: {service.model_available}")
    
    if service.model_available:
        # Test feature extraction
        dummy_code = """
def solve(arr):
    max_val = arr[0]
    for i in range(len(arr)):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val
"""
        
        # Create a mock submission object
        class MockSubmission:
            def __init__(self):
                self.code = dummy_code
                self.time_to_first_submission = 30.0
                self.keystroke_speed_avg = 45.0
                self.keystroke_speed_variance = 10.0
                self.deletion_ratio = 0.15
                self.pasted_code_ratio = 0.0
                self.external_source_similarity = 0.1
                self.success_rate = 0.5
                self.efficiency_vs_player_avg = 1.0
        
        submission = MockSubmission()
        features = service.extract_features(dummy_code, submission)
        print(f"✓ Features extracted: {len(features)} features")
        
        # Test prediction
        prediction = service.predict(features)
        print(f"✓ Prediction made:")
        print(f"  Legitimate: {prediction['legitimate_probability']:.2%}")
        print(f"  AI-Assisted: {prediction['ai_assisted_probability']:.2%}")
        print(f"  Pasted: {prediction['pasted_probability']:.2%}")
        print(f"  Predicted: {prediction['predicted_class']}")
        print(f"  Confidence: {prediction['confidence_score']:.2%}")
    
except Exception as e:
    print(f"✗ XGBIntegrityService test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED - XGBoost Model is Working!")
print("=" * 80)
