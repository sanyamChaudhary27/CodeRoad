"""
Test all 5 Groq API keys
"""
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv('backend/.env')

try:
    from groq import Groq
    
    print("🔍 Testing All Groq API Keys\n")
    
    # Load all keys
    keys = []
    for i in range(1, 11):
        key_name = f"GROQ_API_KEY_{i}" if i > 1 else "GROQ_API_KEY"
        api_key = os.getenv(key_name)
        if api_key:
            keys.append((key_name, api_key))
    
    print(f"Found {len(keys)} Groq API keys\n")
    
    # Test each key
    working_keys = 0
    for key_name, api_key in keys:
        try:
            print(f"Testing {key_name}...")
            client = Groq(api_key=api_key)
            
            # Simple test
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": "Say 'OK' if you're working"}
                ],
                max_tokens=10,
            )
            
            result = response.choices[0].message.content.strip()
            print(f"  ✅ {key_name}: Working! Response: {result}")
            working_keys += 1
            
        except Exception as e:
            print(f"  ❌ {key_name}: Failed - {str(e)[:100]}")
    
    print(f"\n{'='*50}")
    print(f"Summary: {working_keys}/{len(keys)} keys working")
    print(f"{'='*50}")
    
    if working_keys >= 3:
        print(f"\n🎉 Excellent! {working_keys} keys working - more than enough for hackathon!")
    elif working_keys >= 1:
        print(f"\n✅ Good! {working_keys} keys working - should be sufficient")
    else:
        print(f"\n⚠️  Warning: No keys working - check API keys")
        
except ImportError:
    print("❌ groq package not installed")
    print("Run: pip install groq")
