"""
Test script to verify AI debug challenge generation is working
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.challenge_service import get_challenge_service
from app.core.database import get_db

def test_ai_generation():
    """Test AI debug challenge generation"""
    service = get_challenge_service()
    
    print("\n=== Challenge Service Status ===")
    print(f"AI Available: {service.ai_available}")
    print(f"Groq Clients: {len(service.groq_clients)}")
    print(f"Templates Loaded: {len(service.templates)}")
    
    if not service.ai_available:
        print("\n❌ AI is NOT available!")
        print("Reason: Groq clients not initialized")
        return
    
    print("\n✅ AI is available!")
    print("\n=== Testing Debug Challenge Generation ===")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test with AI enabled
        print("\n1. Testing with AI enabled (use_ai=True)...")
        challenge = service.generate_debug_challenge(
            db=db,
            difficulty='intermediate',
            player_rating=300,
            use_ai=True,
            player_id=None
        )
        
        print(f"✅ Generated: {challenge['title']}")
        print(f"   Method: {challenge.get('generation_method', 'unknown')}")
        print(f"   Difficulty: {challenge['difficulty']}")
        print(f"   Bug Count: {challenge.get('bug_count', 0)}")
        print(f"   Bug Types: {challenge.get('bug_types', [])}")
        
        # Test with AI disabled
        print("\n2. Testing with AI disabled (use_ai=False)...")
        challenge2 = service.generate_debug_challenge(
            db=db,
            difficulty='beginner',
            player_rating=300,
            use_ai=False,
            player_id=None
        )
        
        print(f"✅ Generated: {challenge2['title']}")
        print(f"   Method: {challenge2.get('generation_method', 'unknown')}")
        print(f"   Difficulty: {challenge2['difficulty']}")
        
        print("\n=== Test Complete ===")
        print("✅ AI debug generation is working!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_ai_generation()
