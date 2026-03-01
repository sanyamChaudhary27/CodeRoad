"""
Simple API testing script
Tests basic backend connectivity and endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_auth_register():
    """Test user registration"""
    print("\n=== Testing Auth Register ===")
    try:
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 201, 409]  # 409 if user exists
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_auth_login():
    """Test user login"""
    print("\n=== Testing Auth Login ===")
    try:
        payload = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
            return True, data.get('access_token')
        else:
            print(f"Response: {response.json()}")
            return False, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, None

def test_challenge_generate(token):
    """Test challenge generation"""
    print("\n=== Testing Challenge Generation ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "difficulty": "intermediate",
            "domain": "arrays"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/challenges/generate",
            json=payload,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Challenge: {data.get('title', 'N/A')}")
            print(f"Difficulty: {data.get('difficulty', 'N/A')}")
            print(f"Test Cases: {len(data.get('test_cases', []))}")
            return True
        else:
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CODE ROAD API TESTING")
    print("=" * 60)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test root
    results.append(("Root Endpoint", test_root()))
    
    # Test auth register
    results.append(("Auth Register", test_auth_register()))
    
    # Test auth login
    login_ok, token = test_auth_login()
    results.append(("Auth Login", login_ok))
    
    # Test challenge generation (if logged in)
    if token:
        results.append(("Challenge Generation", test_challenge_generate(token)))
    else:
        print("\n⚠ Skipping challenge generation test (no token)")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
