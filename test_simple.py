"""
Simple backend connectivity test
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("BACKEND CONNECTIVITY TEST - SIMPLE")
print("=" * 60)

# Test 1: Import app
print("\n1. Testing app import...")
try:
    from app.app import app
    print("   ✓ FastAPI app imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 2: Check routes
print("\n2. Checking registered routes...")
try:
    routes = [route.path for route in app.routes]
    print(f"   ✓ Found {len(routes)} routes")
    
    # Check key routes
    key_routes = [
        "/health",
        "/api/v1/auth/register",
        "/api/v1/challenges/generate",
        "/api/v1/matches/",
        "/api/v1/leaderboard/"
    ]
    
    for route in key_routes:
        if any(route in r for r in routes):
            print(f"   ✓ {route}")
        else:
            print(f"   ⚠ {route} not found")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 3: Test challenge service
print("\n3. Testing challenge service...")
try:
    from app.services.challenge_service import get_challenge_service
    service = get_challenge_service()
    print("   ✓ Challenge service initialized")
    
    # Get status
    status = service.get_status()
    print(f"   ✓ Service status: {status['status']}")
    print(f"     - ML Available: {status['ml_available']}")
    print(f"     - Templates: {status['templates_available']}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Generate challenge
print("\n4. Testing challenge generation...")
try:
    challenge = service.generate_challenge(
        difficulty="intermediate",
        player_rating=1200,
        use_ai=False
    )
    print(f"   ✓ Challenge generated: {challenge['title']}")
    print(f"     - ID: {challenge['id']}")
    print(f"     - Test cases: {len(challenge['test_cases'])}")
    print(f"     - Method: {challenge['generation_method']}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - BACKEND IS READY")
print("=" * 60)
