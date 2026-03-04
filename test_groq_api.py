"""
Test Groq API - Fast, free, reliable alternative to Gemini
Get API key from: https://console.groq.com/
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        print("Get free API key from: https://console.groq.com/")
        exit(1)
    
    print(f"✓ API Key found: {api_key[:10]}...")
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    # Test with Llama 3.1 70B (best quality)
    models_to_try = [
        'llama-3.1-70b-versatile',  # Best quality
        'llama-3.1-8b-instant',     # Fastest
        'mixtral-8x7b-32768',       # Good alternative
    ]
    
    for model_name in models_to_try:
        print(f"\n🔍 Testing {model_name}...")
        try:
            prompt = """Generate a coding challenge for competitive programming.

Difficulty: intermediate
Domain: arrays

CRITICAL: Return ONLY valid, complete JSON. No markdown, no explanations.

{
  "title": "Short problem title",
  "description": "Clear problem description (2-3 sentences)",
  "domain": "arrays",
  "input_format": "Brief input description",
  "output_format": "Brief output description",
  "constraints": {"input_size": "1 <= n <= 1000"},
  "boilerplate_code": "def solve(arr):\\n    return 0",
  "test_cases": [
    {"input": "1 2 3", "expected_output": "6", "category": "basic", "description": "Basic"},
    {"input": "0", "expected_output": "0", "category": "edge", "description": "Zero"},
    {"input": "-1 -2", "expected_output": "-3", "category": "edge", "description": "Negative"},
    {"input": "100 200", "expected_output": "300", "category": "boundary", "description": "Large"}
  ]
}

Generate complete JSON now:"""
            
            import time
            start = time.time()
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a coding challenge generator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            elapsed = time.time() - start
            
            text = response.choices[0].message.content.strip()
            print(f"✓ Response received in {elapsed:.2f}s ({len(text)} chars)")
            
            # Clean up markdown if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Extract JSON
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                text = text[start_idx:end_idx+1]
            
            # Check completeness
            if text.count('{') != text.count('}'):
                print(f"❌ Incomplete JSON - unbalanced braces")
                continue
            
            data = json.loads(text)
            print(f"✓ Valid JSON parsed!")
            print(f"✓ Title: {data.get('title')}")
            print(f"✓ Description: {data.get('description', '')[:80]}...")
            print(f"✓ Test cases: {len(data.get('test_cases', []))}")
            print(f"\n✅ SUCCESS: {model_name} is working! ({elapsed:.2f}s)")
            print(f"\n🚀 Groq is MUCH faster than Gemini and more reliable!")
            break
            
        except Exception as e:
            print(f"❌ {model_name} failed: {e}")
            continue
    else:
        print("\n❌ All models failed")
        
except ImportError:
    print("❌ groq package not installed")
    print("Run: pip install groq")
    print("Get API key from: https://console.groq.com/")
