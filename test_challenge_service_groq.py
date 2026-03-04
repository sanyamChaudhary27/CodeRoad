"""Test script to verify Groq challenge generation is working"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.challenge_service import get_challenge_service

def test_groq_setup():
    """Test that Groq is properly initialized"""
    service = get_challenge_service()
    
    print("=" * 60)
    print("GROQ CHALLENGE SERVICE TEST")
    print("=" * 60)
    
    print(f"\nAI Available: {service.ai_available}")
    print(f"Groq Clients: {len(service.groq_clients)}")
    print(f"Templates Available: {len(service.templates)}")
    
    if service.groq_clients:
        print(f"\n✓ Groq is initialized with {len(service.groq_clients)} API keys")
    else:
        print("\n✗ Groq is NOT initialized")
        print("\nChecking environment variables:")
        for i in range(1, 6):
            key_name = f"GROQ_API_KEY_{i}" if i > 1 else "GROQ_API_KEY"
            key_value = os.getenv(key_name)
            if key_value:
                print(f"  {key_name}: {key_value[:20]}... (found)")
            else:
                print(f"  {key_name}: NOT FOUND")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_groq_setup()
