#!/usr/bin/env python3
"""
Comprehensive API test script for Code Road Backend.
Tests all endpoints with proper authentication flow.
"""

import httpx
import json
import time
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=TIMEOUT)
        self.access_token: Optional[str] = None
        self.player_id: Optional[str] = None
        self.match_id: Optional[str] = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        print(f"[{level}] {message}")
    
    def test_health(self) -> bool:
        """Test health endpoint."""
        self.log("Testing health endpoint...")
        try:
            response = self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log("✅ Health check passed", "SUCCESS")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Health check error: {e}", "ERROR")
            return False
    
    def test_root(self) -> bool:
        """Test root endpoint."""
        self.log("Testing root endpoint...")
        try:
            response = self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Root endpoint passed: {data.get('message')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Root endpoint failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Root endpoint error: {e}", "ERROR")
            return False
    
    def test_register(self, username: str = "testuser", email: str = "test@example.com", password: str = "TestPass123!") -> bool:
        """Test player registration."""
        self.log(f"Testing registration for {username}...")
        try:
            payload = {
                "username": username,
                "email": email,
                "password": password
            }
            response = self.client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=payload
            )
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get("access_token")
                self.player_id = data.get("player", {}).get("id")
                self.log(f"✅ Registration successful: {self.player_id}", "SUCCESS")
                return True
            elif response.status_code == 400:
                self.log(f"⚠️  Registration failed (user may exist): {response.json().get('detail')}", "WARNING")
                # Try login instead
                return self.test_login(email, password)
            else:
                self.log(f"❌ Registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Registration error: {e}", "ERROR")
            return False
    
    def test_login(self, email: str = "test@example.com", password: str = "TestPass123!") -> bool:
        """Test player login."""
        self.log(f"Testing login for {email}...")
        try:
            payload = {
                "email": email,
                "password": password
            }
            response = self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.player_id = data.get("player", {}).get("id")
                self.log(f"✅ Login successful: {self.player_id}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Login error: {e}", "ERROR")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def test_get_me(self) -> bool:
        """Test get current player endpoint."""
        self.log("Testing GET /me endpoint...")
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ GET /me successful: {data.get('username')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ GET /me failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ GET /me error: {e}", "ERROR")
            return False
    
    def test_join_queue(self) -> bool:
        """Test join matchmaking queue."""
        self.log("Testing join queue endpoint...")
        try:
            payload = {"preferred_format": "1v1"}
            response = self.client.post(
                f"{self.base_url}/api/v1/matches/queue/join",
                json=payload,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Join queue successful: in_queue={data.get('in_queue')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Join queue failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Join queue error: {e}", "ERROR")
            return False
    
    def test_leave_queue(self) -> bool:
        """Test leave matchmaking queue."""
        self.log("Testing leave queue endpoint...")
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/matches/queue/leave",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Leave queue successful: {data.get('status')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Leave queue failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Leave queue error: {e}", "ERROR")
            return False
    
    def test_get_leaderboard(self) -> bool:
        """Test get global leaderboard."""
        self.log("Testing global leaderboard endpoint...")
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/leaderboard/global?limit=10"
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("leaderboard", []))
                self.log(f"✅ Leaderboard retrieved: {count} players", "SUCCESS")
                return True
            else:
                self.log(f"❌ Leaderboard failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Leaderboard error: {e}", "ERROR")
            return False
    
    def test_get_player_stats(self) -> bool:
        """Test get player statistics."""
        if not self.player_id:
            self.log("⚠️  Skipping player stats test (no player_id)", "WARNING")
            return True
        
        self.log(f"Testing player stats endpoint for {self.player_id}...")
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/leaderboard/player/{self.player_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Player stats retrieved: rating={data.get('current_rating')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Player stats failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Player stats error: {e}", "ERROR")
            return False
    
    def test_get_my_stats(self) -> bool:
        """Test get current player stats."""
        self.log("Testing GET /me/stats endpoint...")
        try:
            response = self.client.get(
                f"{self.base_url}/api/v1/leaderboard/me/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ My stats retrieved: rank={data.get('rank')}, rating={data.get('current_rating')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ My stats failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ My stats error: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        self.log("=" * 60)
        self.log("Code Road Backend - Comprehensive API Test Suite")
        self.log("=" * 60)
        
        results = {
            "Health Check": self.test_health(),
            "Root Endpoint": self.test_root(),
            "Register": self.test_register(),
            "Get Me": self.test_get_me(),
            "Join Queue": self.test_join_queue(),
            "Leave Queue": self.test_leave_queue(),
            "Global Leaderboard": self.test_get_leaderboard(),
            "Player Stats": self.test_get_player_stats(),
            "My Stats": self.test_get_my_stats(),
        }
        
        self.log("=" * 60)
        self.log("Test Results Summary")
        self.log("=" * 60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        self.log("=" * 60)
        self.log(f"Total: {passed}/{total} tests passed", "INFO")
        self.log("=" * 60)
        
        return passed == total

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
