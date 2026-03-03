#!/usr/bin/env python3
"""
Simple test to generate 3 problems with AI
"""

import sys
import os
from pathlib import Path
import time

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv("backend/.env")

from app.services.challenge_service import ChallengeService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

print("=" * 80)
print("🧪 Simple AI Problem Generation Test")
print("=" * 80)

# Create in-memory database
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Initialize service
print("\n📦 Initializing Challenge Service...")
service = ChallengeService()

if service.ai_available:
    print(f"✅ AI Available!")
else:
    print("❌ AI Not Available")
    sys.exit(1)

# Generate 3 problems
test_cases = [
    ('beginner', 'arrays'),
    ('intermediate', 'strings'),
    ('advanced', 'math')
]

print("\n" + "=" * 80)
print("🎯 Generating 3 Problems")
print("=" * 80)

for i, (difficulty, domain) in enumerate(test_cases, 1):
    print(f"\n{i}. Generating {difficulty.upper()} problem in {domain}...")
    start_time = time.time()
    
    try:
        problem = service.generate_challenge(
            db=db,
            difficulty=difficulty,
            player_rating=1200,
            domain=domain,
            use_ai=True
        )
        
        elapsed = time.time() - start_time
        
        if problem and problem.get('generation_method') == 'ai':
            print(f"   ✅ SUCCESS ({elapsed:.1f}s)")
            print(f"   Title: {problem['title']}")
            print(f"   Domain: {problem['domain']}")
            print(f"   Test Cases: {len(problem['test_cases'])}")
            print(f"   Description: {problem['description'][:100]}...")
            
            # Show full problem details
            print(f"\n   📄 Full Problem Details:")
            print(f"   " + "-" * 76)
            print(f"   {problem['description']}")
            print(f"\n   Input: {problem['input_format']}")
            print(f"   Output: {problem['output_format']}")
            print(f"   Constraints: {problem['constraints']}")
            print(f"\n   Boilerplate:")
            for line in problem['boilerplate_code'].split('\n'):
                print(f"   {line}")
            print(f"\n   Test Cases:")
            for tc in problem['test_cases'][:2]:  # Show first 2
                print(f"     • {tc['description']}: {tc['input']} → {tc['expected_output']}")
            
        else:
            print(f"   ⚠️  FALLBACK ({elapsed:.1f}s) - Used template")
            print(f"   Title: {problem['title']}")
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ ERROR ({elapsed:.1f}s): {str(e)[:100]}")

print("\n" + "=" * 80)
print("✅ Test Complete!")
print("=" * 80)

db.close()
