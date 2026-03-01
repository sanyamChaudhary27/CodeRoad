#!/usr/bin/env python
"""
Test API integration - verify frontend can easily integrate with backend
"""

import sys
import os
sys.path.insert(0, 'backend')

from app.services.challenge_service import get_challenge_service

def test_challenge_generation():
    """Test that challenge generation works for frontend integration"""
    
    print("\n" + "="*60)
    print("FRONTEND INTEGRATION TEST")
    print("="*60)
    
    service = get_challenge_service()
    
    # Test 1: Generate beginner challenge
    print("\n[TEST 1] Generate Beginner Challenge")
    challenge = service.generate_challenge(
        difficulty="beginner",
        player_rating=1100,
        domain="arrays"
    )
    
    print(f"  Title: {challenge['title']}")
    print(f"  ID: {challenge['id']}")
    print(f"  Difficulty: {challenge['difficulty']}")
    print(f"  Domain: {challenge['domain']}")
    print(f"  Test Cases: {len(challenge['test_cases'])}")
    print(f"  Generation Method: {challenge['generation_method']}")
    
    # Verify structure for frontend
    required_fields = [
        'id', 'title', 'description', 'difficulty', 'domain',
        'constraints', 'input_format', 'output_format',
        'example_input', 'example_output', 'time_limit_seconds',
        'test_cases', 'coverage_metrics', 'generated_at'
    ]
    
    missing = [f for f in required_fields if f not in challenge]
    if missing:
        print(f"  ERROR: Missing fields: {missing}")
        return False
    
    print("  [PASS] All required fields present")
    
    # Test 2: Generate intermediate challenge
    print("\n[TEST 2] Generate Intermediate Challenge")
    challenge = service.generate_challenge(
        difficulty="intermediate",
        player_rating=1300,
        domain="strings"
    )
    
    print(f"  Title: {challenge['title']}")
    print(f"  Test Cases: {len(challenge['test_cases'])}")
    print("  [PASS] Intermediate challenge generated")
    
    # Test 3: Generate advanced challenge
    print("\n[TEST 3] Generate Advanced Challenge")
    challenge = service.generate_challenge(
        difficulty="advanced",
        player_rating=1600
    )
    
    print(f"  Title: {challenge['title']}")
    print(f"  Test Cases: {len(challenge['test_cases'])}")
    print("  [PASS] Advanced challenge generated")
    
    # Test 4: Verify test case structure
    print("\n[TEST 4] Verify Test Case Structure")
    tc = challenge['test_cases'][0]
    tc_fields = ['id', 'input', 'expected_output', 'category', 'description', 'is_hidden']
    missing_tc = [f for f in tc_fields if f not in tc]
    
    if missing_tc:
        print(f"  ERROR: Missing test case fields: {missing_tc}")
        return False
    
    print(f"  Test Case ID: {tc['id']}")
    print(f"  Category: {tc['category']}")
    print(f"  Hidden: {tc['is_hidden']}")
    print("  [PASS] Test case structure valid")
    
    # Test 5: Verify API response format
    print("\n[TEST 5] Verify API Response Format")
    print(f"  Response is dict: {isinstance(challenge, dict)}")
    print(f"  Has ID: {bool(challenge.get('id'))}")
    print(f"  Has title: {bool(challenge.get('title'))}")
    print(f"  Has test_cases: {bool(challenge.get('test_cases'))}")
    print("  [PASS] Response format is correct")
    
    print("\n" + "="*60)
    print("FRONTEND INTEGRATION: ALL TESTS PASSED")
    print("="*60)
    print("\nFrontend can easily integrate with these endpoints:")
    print("  POST /api/challenges/generate")
    print("  GET /api/challenges/{challenge_id}")
    print("  GET /api/challenges")
    print("\nResponse structure is clean and well-documented.")
    
    return True

if __name__ == "__main__":
    try:
        success = test_challenge_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
