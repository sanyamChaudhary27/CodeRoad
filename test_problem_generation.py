#!/usr/bin/env python3
"""
Test actual problem generation through the challenge service API
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv("backend/.env")

# Import after path is set
from app.services.challenge_service import ChallengeService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

print("=" * 80)
print("🧪 Testing Problem Generation with Gemini AI")
print("=" * 80)

# Create in-memory database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Initialize service
print("\n📦 Initializing Challenge Service...")
service = ChallengeService()

if service.ai_available:
    print(f"✅ AI Available: Using {service.gemini_model._model_name if hasattr(service.gemini_model, '_model_name') else 'Gemini'}")
else:
    print("⚠️  AI Not Available: Will use templates")

print("\n" + "=" * 80)
print("🎯 Generating Problems")
print("=" * 80)

difficulties = ['beginner', 'intermediate', 'advanced']
domains = ['arrays', 'strings', 'math']

generated_problems = []

for difficulty in difficulties:
    for domain in domains:
        print(f"\n📝 Generating {difficulty.upper()} problem in {domain}...")
        try:
            problem = service.generate_challenge(
                db=db,
                difficulty=difficulty,
                player_rating=1200,
                domain=domain,
                use_ai=True
            )
            
            if problem:
                print(f"✅ Generated: {problem['title']}")
                print(f"   Method: {problem.get('generation_method', 'unknown')}")
                print(f"   Domain: {problem['domain']}")
                print(f"   Test Cases: {len(problem['test_cases'])}")
                print(f"   Description: {problem['description'][:80]}...")
                
                generated_problems.append({
                    'difficulty': difficulty,
                    'domain': domain,
                    'title': problem['title'],
                    'method': problem.get('generation_method', 'unknown'),
                    'test_cases': len(problem['test_cases'])
                })
            else:
                print(f"❌ Failed to generate problem")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")

print("\n" + "=" * 80)
print("📊 Generation Summary")
print("=" * 80)

ai_count = sum(1 for p in generated_problems if p['method'] == 'ai')
template_count = sum(1 for p in generated_problems if p['method'] == 'template')
minimal_count = sum(1 for p in generated_problems if p['method'] == 'minimal')

print(f"\nTotal Problems Generated: {len(generated_problems)}")
print(f"  - AI Generated: {ai_count}")
print(f"  - Template Based: {template_count}")
print(f"  - Minimal Fallback: {minimal_count}")

if generated_problems:
    print("\n📋 Generated Problems List:")
    print("-" * 80)
    for i, p in enumerate(generated_problems, 1):
        print(f"{i}. [{p['difficulty'].upper()}] {p['title']}")
        print(f"   Domain: {p['domain']} | Method: {p['method']} | Tests: {p['test_cases']}")

print("\n" + "=" * 80)

if ai_count > 0:
    print("✅ SUCCESS: AI problem generation is working!")
    print(f"   Generated {ai_count} unique problems using Gemini AI")
elif template_count > 0:
    print("⚠️  WARNING: Using template fallback (AI not available)")
    print(f"   Generated {template_count} problems from templates")
else:
    print("❌ ERROR: Problem generation not working properly")

print("=" * 80)

# Show one complete problem example
if generated_problems:
    print("\n" + "=" * 80)
    print("📄 Sample Generated Problem (Full Details)")
    print("=" * 80)
    
    # Get the first AI-generated problem or any problem
    sample = None
    for p in generated_problems:
        if p['method'] == 'ai':
            sample = p
            break
    
    if not sample:
        sample = generated_problems[0]
    
    # Regenerate to get full details
    try:
        problem = service.generate_challenge(
            db=db,
            difficulty=sample['difficulty'],
            player_rating=1200,
            domain=sample['domain'],
            use_ai=True
        )
        
        print(f"\nTitle: {problem['title']}")
        print(f"Difficulty: {problem['difficulty']}")
        print(f"Domain: {problem['domain']}")
        print(f"\nDescription:")
        print(problem['description'])
        print(f"\nInput Format: {problem['input_format']}")
        print(f"Output Format: {problem['output_format']}")
        print(f"\nConstraints: {problem['constraints']}")
        print(f"\nBoilerplate Code:")
        print(problem['boilerplate_code'])
        print(f"\nTest Cases:")
        for tc in problem['test_cases']:
            visibility = "Hidden" if tc['is_hidden'] else "Visible"
            print(f"  [{visibility}] {tc['description']}")
            print(f"    Input: {tc['input']}")
            print(f"    Expected: {tc['expected_output']}")
        
    except Exception as e:
        print(f"Could not regenerate sample: {e}")

print("\n" + "=" * 80)
print("✅ Test Complete!")
print("=" * 80)

db.close()
