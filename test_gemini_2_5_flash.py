"""
Test Gemini 2.5 Flash API - Quick verification
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        exit(1)
    
    print(f"✓ API Key found: {api_key[:10]}...")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Try gemini-2.5-flash first (primary)
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash-exp']
    
    for model_name in models_to_try:
        print(f"\n🔍 Testing {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            
            # Simplified test prompt (matches actual service)
            prompt = """Generate a coding challenge for competitive programming.

Difficulty: intermediate
Domain: arrays

CRITICAL: Return ONLY valid, complete JSON. No markdown, no explanations, no code blocks.

Required format:
{
  "title": "Short problem title",
  "description": "Clear problem description (2-3 sentences max)",
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
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=3000,  # Increased to ensure complete response
                ),
                request_options={"timeout": 25.0}  # Longer timeout
            )
            
            text = response.text.strip()
            print(f"✓ Response received ({len(text)} chars)")
            print(f"First 200 chars: {text[:200]}")
            
            # Try to parse as JSON
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
            else:
                print(f"❌ No complete JSON object found")
                continue
            
            # Check for balanced braces
            if text.count('{') != text.count('}'):
                print(f"❌ Incomplete JSON - unbalanced braces")
                print(f"   Opening braces: {text.count('{')}, Closing braces: {text.count('}')}")
                continue
            
            data = json.loads(text)
            print(f"✓ Valid JSON parsed!")
            print(f"✓ Title: {data.get('title')}")
            print(f"✓ Domain: {data.get('domain')}")
            print(f"\n✅ SUCCESS: {model_name} is working!")
            break
            
        except Exception as e:
            print(f"❌ {model_name} failed: {e}")
            if "quota" in str(e).lower():
                print("⚠️  Quota exceeded - wait for reset or try later")
            continue
    else:
        print("\n❌ All models failed")
        
except ImportError:
    print("❌ google-generativeai not installed")
    print("Run: pip install google-generativeai")
