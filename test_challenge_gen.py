#!/usr/bin/env python3
"""Test challenge generation to trigger logging"""
import requests
import json

# You'll need to get a valid token first by logging in
# For now, let's just check if the endpoint exists

url = "https://coderoad.online/api/v1/challenges/generate"
headers = {"Content-Type": "application/json"}
data = {
    "difficulty": "beginner",
    "challenge_type": "debug",
    "domain": "arrays"
}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
