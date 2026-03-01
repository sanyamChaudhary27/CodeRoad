"""
Backend import and connectivity test
Tests that all backend modules can be imported and are properly connected
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test all backend imports"""
    print("\n=== Testing Backend Imports ===")
    
    tests = []
    
    # Test core imports
    try:
        from app.core.database import engine, Base, get_db
        print("[PASS] Database module")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Database module: {e}")
        tests.append(False)
    
    # Test security
    try:
        from app.core.security import verify_token, get_current_player
        print("[PASS] Security module")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Security module: {e}")
        tests.append(False)
    
    # Test config
    try:
        from app.config import settings
        print("[PASS] Config module")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Config module: {e}")
        tests.append(False)
    
    # Test models
    try:
        from app.models.player import Player
        from app.models.match import Match
        from app.models.submission import Submission
        print("[PASS] Models module")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Models module: {e}")
        tests.append(False)
    
    # Test services
    try:
        from app.services.challenge_service_fixed import get_challenge_service
        print("[PASS] Challenge service (robust)")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] Challenge service: {e}")
        tests.append(False)
    
    # Test API routers
    try:
        from app.api import auth, match, submission, leaderboard, websocket, challenge
        print("[PASS] API routers")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] API routers: {e}")
        tests.append(False)
    
    # Test app
    try:
        from app.app import app
        print("[PASS] FastAPI app")
        tests.append(True)
    except Exception as e:
        print(f"[FAIL] FastAPI app: {e}")
        tests.append(False)
    
    return tests

def test_challenge_service():
    """Test challenge service functionality"""
    print("\n=== Testing Challenge Service ===")
    
    try:
        from app.services.challenge_service_fixed import ChallengeService
        
        # Create service
        service = ChallengeService()
        print("[PASS] Service initialized")
        
        # Check status
        status = service.get_status()
        print(f"[PASS] Service status: {status['status']}")
        print(f"  - ML Available: {status['ml_available']}")
        print(f"  - Templates Available: {status['templates_available']}")
        
        # Generate challenge
        challenge = service.generate_challenge(
            difficulty="intermediate",
            player_rating=1200,
            use_ai=False  # Use templates
        )
        print(f"[PASS] Challenge generated: {challenge['title']}")
        print(f"  - ID: {challenge['id']}")
        print(f"  - Test cases: {len(challenge['test_cases'])}")
        print(f"  - Generation method: {challenge['generation_method']}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Challenge service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_generators():
    """Test ML generators availability"""
    print("\n=== Testing ML Generators ===")
    
    try:
        from ml.challenge_generation import TestCaseGenerator, ProblemStatementGenerator
        print("[PASS] ML generators imported")
        
        # Check if API key is available
        import os
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            print("[PASS] API key found")
            return True
        else:
            print("[WARN] API key not found (ML generation will use fallback)")
            return True
    except ImportError as e:
        print(f"[WARN] ML generators not available: {e}")
        print("  (This is OK - service will use templates)")
        return True
    except Exception as e:
        print(f"[FAIL] ML error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("BACKEND CONNECTIVITY TEST")
    print("=" * 60)
    
    # Test imports
    import_results = test_imports()
    
    # Test challenge service
    service_ok = test_challenge_service()
    
    # Test ML generators
    ml_ok = test_ml_generators()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    import_passed = sum(import_results)
    import_total = len(import_results)
    
    print(f"\nImports: {import_passed}/{import_total} passed")
    print(f"Challenge Service: {'[PASS] PASS' if service_ok else '[FAIL] FAIL'}")
    print(f"ML Generators: {'[PASS] OK' if ml_ok else '[FAIL] FAIL'}")
    
    all_passed = all(import_results) and service_ok and ml_ok
    
    if all_passed:
        print("\n[PASS] All backend connectivity tests passed!")
        print("[PASS] Backend is ready for deployment")
        return 0
    else:
        print("\n[WARN] Some tests failed - check errors above")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
