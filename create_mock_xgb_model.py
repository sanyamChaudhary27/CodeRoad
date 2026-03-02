#!/usr/bin/env python
"""Create a mock XGBoost model for testing"""

import pickle
import numpy as np
from pathlib import Path

try:
    import xgboost as xgb
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "xgboost", "scikit-learn"])
    import xgboost as xgb
    from sklearn.preprocessing import LabelEncoder

print("Creating mock XGBoost model...")

# Create dummy training data
np.random.seed(42)
n_samples = 100
n_features = 10

X = np.random.randn(n_samples, n_features)
y_labels = np.random.choice(['legitimate', 'ai_assisted', 'pasted'], n_samples)

# Encode labels
encoder = LabelEncoder()
y = encoder.fit_transform(y_labels)

# Create and train model
model = xgb.XGBClassifier(
    n_estimators=10,
    max_depth=3,
    learning_rate=0.1,
    random_state=42,
    verbosity=0
)
model.fit(X, y)

# Save model
model_path = Path("ml/training_data/classification_model/cheat_detection_model.pkl")
encoder_path = Path("ml/training_data/classification_model/label_encoder.pkl")

model_path.parent.mkdir(parents=True, exist_ok=True)

with open(model_path, 'wb') as f:
    pickle.dump(model, f)

with open(encoder_path, 'wb') as f:
    pickle.dump(encoder, f)

print(f"✓ Model saved to {model_path}")
print(f"✓ Encoder saved to {encoder_path}")

# Test loading
with open(model_path, 'rb') as f:
    loaded_model = pickle.load(f)

with open(encoder_path, 'rb') as f:
    loaded_encoder = pickle.load(f)

print("✓ Model and encoder loaded successfully")

# Test prediction
test_features = np.random.randn(1, n_features)
predictions = loaded_model.predict_proba(test_features)
print(f"✓ Test prediction: {predictions[0]}")
print(f"✓ Classes: {loaded_encoder.classes_}")
