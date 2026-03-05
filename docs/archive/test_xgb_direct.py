#!/usr/bin/env python
"""Direct test of XGB service without IntegrityService wrapper"""

import os
import sys
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
print("DIRECT XGB SERVICE TEST")
print("=" * 80)

# Import required modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.models import Submission, Player
from backend.app.services.xgb_integrity_service import get_xgb_integrity_service

# Create in-memory database
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db = Session()

print("\n1. Creating test player...")
player = Player(
    id="test_player_1",
    username="test_user",
    email="test@example.com",
    hashed_password="hash",
    current_rating=1200
)
db.add(player)
db.commit()
print("   ✓ Player created")

print("\n2. Creating test submission...")
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
    memory_used_mb=12
)
db.add(submission)
db.commit()
print("   ✓ Submission created")

print("\n3. Getting XGB service...")
xgb_service = get_xgb_integrity_service()
print(f"   ✓ XGB service initialized")
print(f"   - Model available: {xgb_service.model_available}")

print("\n4. Calling XGB analyze_submission directly...")
try:
    xgb_service.analyze_submission(db, "test_sub_1")
    print("   ✓ XGB analysis completed")
except Exception as e:
    print(f"   ✗ XGB analysis failed: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Checking submission fields...")
db.refresh(submission)
print(f"   - integrity_status: {submission.integrity_status}")
print(f"   - integrity_confidence: {submission.integrity_confidence}")
print(f"   - integrity_model_used: {submission.integrity_model_used}")
print(f"   - ai_quality_score: {submission.ai_quality_score}")
print(f"   - cheat_probability: {submission.cheat_probability}")

if submission.integrity_model_used == 'xgboost':
    print("\n✓ SUCCESS: XGB model was used!")
else:
    print(f"\n✗ FAILED: Expected 'xgboost' but got '{submission.integrity_model_used}'")

db.close()
