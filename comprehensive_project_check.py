#!/usr/bin/env python
"""Comprehensive end-to-end project analysis"""

import os
import sys
from pathlib import Path

# Fix Unicode on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 80)
print("COMPREHENSIVE PROJECT ANALYSIS")
print("=" * 80)

issues = []
warnings = []

# 1. Check Environment Configuration
print("\n1. ENVIRONMENT CONFIGURATION")
print("-" * 80)

from dotenv import load_dotenv
backend_env = Path("backend/.env")
root_env = Path(".env")

if backend_env.exists():
    load_dotenv(backend_env)
    print("✓ backend/.env exists")
    
    # Check critical env vars
    critical_vars = ["DATABASE_URL", "SECRET_KEY", "AI_PROVIDER"]
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: {value[:20]}..." if len(value) > 20 else f"  ✓ {var}: {value}")
        else:
            issues.append(f"Missing {var} in backend/.env")
            print(f"  ✗ {var}: NOT SET")
    
    # Check optional vars
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"  ✓ GEMINI_API_KEY: {gemini_key[:10]}...")
    else:
        warnings.append("GEMINI_API_KEY not set (Gemini features disabled)")
        print(f"  ⚠ GEMINI_API_KEY: NOT SET")
else:
    issues.append("backend/.env file not found")
    print("✗ backend/.env NOT FOUND")

# 2. Check Dependencies
print("\n2. DEPENDENCIES")
print("-" * 80)

required_packages = [
    "fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-dotenv",
    "xgboost", "numpy", "google-generativeai"
]

for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"  ✓ {package}")
    except ImportError:
        issues.append(f"Missing package: {package}")
        print(f"  ✗ {package}")

# 3. Check Database Models
print("\n3. DATABASE MODELS")
print("-" * 80)

try:
    from app.models import Player, Match, Submission, Challenge
    print("  ✓ All models imported successfully")
    
    # Check Submission model has new fields
    from sqlalchemy import inspect
    from app.models.submission import Submission
    
    mapper = inspect(Submission)
    columns = [c.key for c in mapper.columns]
    
    required_fields = [
        'integrity_status', 'integrity_confidence', 'integrity_model_used',
        'pasted_code_ratio', 'external_source_similarity', 
        'success_rate', 'efficiency_vs_player_avg'
    ]
    
    for field in required_fields:
        if field in columns:
            print(f"  ✓ Submission.{field}")
        else:
            issues.append(f"Missing field: Submission.{field}")
            print(f"  ✗ Submission.{field}")
            
except Exception as e:
    issues.append(f"Model import failed: {e}")
    print(f"  ✗ Model import failed: {e}")

# 4. Check Services
print("\n4. SERVICES")
print("-" * 80)

try:
    from app.services.xgb_integrity_service import get_xgb_integrity_service
    xgb_service = get_xgb_integrity_service()
    
    if xgb_service.model_available:
        print("  ✓ XGBIntegrityService (model loaded)")
    else:
        warnings.append("XGB model not available")
        print("  ⚠ XGBIntegrityService (model NOT loaded)")
        
except Exception as e:
    issues.append(f"XGBIntegrityService failed: {e}")
    print(f"  ✗ XGBIntegrityService: {e}")

try:
    from app.services.integrity_service import IntegrityService
    integrity_service = IntegrityService()
    print(f"  ✓ IntegrityService (provider: {integrity_service.provider})")
except Exception as e:
    issues.append(f"IntegrityService failed: {e}")
    print(f"  ✗ IntegrityService: {e}")

try:
    from app.services.challenge_service import get_challenge_service
    challenge_service = get_challenge_service()
    status = challenge_service.get_status()
    print(f"  ✓ ChallengeService (AI: {status['ai_available']}, Templates: {status['templates_available']})")
except Exception as e:
    issues.append(f"ChallengeService failed: {e}")
    print(f"  ✗ ChallengeService: {e}")

# 5. Check API Endpoints
print("\n5. API ENDPOINTS")
print("-" * 80)

try:
    from app.api import auth, match, submission, leaderboard, challenge, websocket
    print("  ✓ auth router")
    print("  ✓ match router")
    print("  ✓ submission router")
    print("  ✓ leaderboard router")
    print("  ✓ challenge router")
    print("  ✓ websocket router")
except Exception as e:
    issues.append(f"API router import failed: {e}")
    print(f"  ✗ API routers: {e}")

# 6. Check Database Connection
print("\n6. DATABASE")
print("-" * 80)

try:
    from sqlalchemy import create_engine
    from app.core.database import Base
    
    # Test with in-memory database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"  ✓ Database schema valid ({len(tables)} tables)")
    
    expected_tables = ['players', 'matches', 'submissions', 'challenges']
    for table in expected_tables:
        if table in tables:
            print(f"  ✓ {table} table")
        else:
            issues.append(f"Missing table: {table}")
            print(f"  ✗ {table} table")
            
except Exception as e:
    issues.append(f"Database test failed: {e}")
    print(f"  ✗ Database: {e}")

# 7. Check XGB Model Files
print("\n7. XGB MODEL FILES")
print("-" * 80)

model_path = Path("ml/training_data/classification_model/cheat_detection_model.pkl")
encoder_path = Path("ml/training_data/classification_model/label_encoder.pkl")

if model_path.exists():
    size_mb = model_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ Model file ({size_mb:.2f} MB)")
else:
    warnings.append("XGB model file not found")
    print(f"  ⚠ Model file NOT FOUND")

if encoder_path.exists():
    print(f"  ✓ Encoder file")
else:
    warnings.append("Label encoder file not found")
    print(f"  ⚠ Encoder file NOT FOUND")

# 8. Check FastAPI App
print("\n8. FASTAPI APPLICATION")
print("-" * 80)

try:
    from app.app import create_app
    app = create_app()
    
    print(f"  ✓ App created successfully")
    print(f"  ✓ Title: {app.title}")
    print(f"  ✓ Version: {app.version}")
    
    # Check routes
    routes = [route.path for route in app.routes]
    critical_routes = ['/health', '/api/v1/auth', '/api/v1/matches', '/api/v1/challenges']
    
    for route in critical_routes:
        matching = [r for r in routes if route in r]
        if matching:
            print(f"  ✓ {route} routes")
        else:
            warnings.append(f"No routes found for {route}")
            print(f"  ⚠ {route} routes")
            
except Exception as e:
    issues.append(f"FastAPI app creation failed: {e}")
    print(f"  ✗ App creation: {e}")
    import traceback
    traceback.print_exc()

# 9. Check Frontend Integration
print("\n9. FRONTEND")
print("-" * 80)

frontend_path = Path("frontend")
if frontend_path.exists():
    print(f"  ✓ Frontend directory exists")
    
    package_json = frontend_path / "package.json"
    if package_json.exists():
        print(f"  ✓ package.json exists")
    else:
        warnings.append("Frontend package.json not found")
        print(f"  ⚠ package.json NOT FOUND")
        
    src_path = frontend_path / "src"
    if src_path.exists():
        print(f"  ✓ src directory exists")
    else:
        warnings.append("Frontend src directory not found")
        print(f"  ⚠ src directory NOT FOUND")
else:
    warnings.append("Frontend directory not found")
    print(f"  ⚠ Frontend directory NOT FOUND")

# 10. Summary
print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)

if not issues and not warnings:
    print("\n✓ PROJECT IS COMPLETELY HEALTHY!")
    print("\nAll systems operational:")
    print("  • Environment configured correctly")
    print("  • All dependencies installed")
    print("  • Database models valid")
    print("  • Services initialized")
    print("  • API endpoints ready")
    print("  • XGB model integrated")
    print("\nReady for production!")
    sys.exit(0)
else:
    if issues:
        print(f"\n✗ CRITICAL ISSUES FOUND: {len(issues)}")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    if warnings:
        print(f"\n⚠ WARNINGS: {len(warnings)}")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if issues:
        print("\n✗ PROJECT HAS CRITICAL ISSUES - NEEDS FIXING")
        sys.exit(1)
    else:
        print("\n⚠ PROJECT IS FUNCTIONAL BUT HAS WARNINGS")
        print("These warnings won't prevent the server from starting.")
        sys.exit(0)
