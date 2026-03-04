"""
Test Groq integration in challenge service
"""
import sys
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv()
load_dotenv('backend/.env')

from app.services.challenge_service import get_challenge_service
from app.core.database import SessionLocal

print("🔍 Testing Groq Integration in Challenge Service\n")

# Get service
service = get_challenge_service()

print(f"✓ Groq available: {service.groq_client is not None}")
print(f"✓ Gemini available: {service.gemini_model is not None}")
print(f"✓ AI available: {service.ai_available}")
print()

# Test generation
db = SessionLocal()
try:
    print("🚀 Generating challenge with AI (should use Groq)...\n")
    
    import time
    start = time.time()
    
    challenge = service.generate_challenge(
        db=db,
        difficulty='intermediate',
        domain='arrays',
        use_ai=True  # Enable AI
    )
    
    elapsed = time.time() - start
    
    print(f"✅ SUCCESS in {elapsed:.2f}s!")
    print(f"\n📋 Challenge Details:")
    print(f"   Title: {challenge['title']}")
    print(f"   Method: {challenge.get('generation_method', 'unknown')}")
    print(f"   Description: {challenge['description'][:100]}...")
    print(f"   Test cases: {len(challenge.get('test_cases', []))}")
    print(f"   Domain: {challenge['domain']}")
    print(f"   Difficulty: {challenge['difficulty']}")
    
    if challenge.get('generation_method') == 'groq_ai':
        print(f"\n🎉 Groq AI is working perfectly!")
    elif challenge.get('generation_method') == 'gemini_ai':
        print(f"\n⚠️  Fell back to Gemini")
    else:
        print(f"\n⚠️  Used templates (AI failed)")
        
finally:
    db.close()
