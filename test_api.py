#!/usr/bin/env python
"""Test script for Code Road API endpoints."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_health():
    """Test health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_root():
    """Test root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_register():
    """Test player registration."""
    print("\n=== Testing Player Registration ===")
    payload = {
        "username": "testplayer",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    return response.json()

def test_login():
    """Test player login."""
    print("\n=== Testing Player Login ===")
    payload = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    return response.json()

def test_leaderboard():
    """Test leaderboard endpoint."""
    print("\n=== Testing Leaderboard ===")
    response = client.get("/api/v1/leaderboard/global")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_invalid_password():
    """Test registration with weak password."""
    print("\n=== Testing Invalid Password ===")
    payload = {
        "username": "testplayer2",
        "email": "test2@example.com",
        "password": "weak"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 400

def test_duplicate_username():
    """Test registration with duplicate username."""
    print("\n=== Testing Duplicate Username ===")
    payload = {
        "username": "testplayer",
        "email": "test3@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 400

if __name__ == "__main__":
    print("=" * 60)
    print("Code Road API Test Suite")
    print("=" * 60)
    
    try:
        test_health()
        test_root()
        test_register()
        test_login()
        test_leaderboard()
        test_invalid_password()
        test_duplicate_username()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)