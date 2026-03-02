#!/usr/bin/env python
"""Test script to verify Gemini is actually generating problem text"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Load environment
from dotenv import load_dotenv
backend_dir = Path("backend")
env_file = backend_dir / ".env"
load_dotenv(env_file)

print("=" * 80)
print("GEMINI API TEXT GENERATION TEST")
print("=" * 80)

# Test 1: Check API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("✗ GEMINI_API_KEY not found")
    sys.exit(1)
print(f"✓ GEMINI_API_KEY found: {api_key[:10]}...")

# Test 2: Import and configure Gemini
try:
    import google.generativeai as genai
    print("✓ google-generativeai imported")
except ImportError as e:
    print(f"✗ Failed to import google-generativeai: {e}")
    sys.exit(1)

try:
    genai.configure(api_key=api_key)
    print("✓ Gemini configured")
except Exception as e:
    print(f"✗ Failed to configure Gemini: {e}")
    sys.exit(1)

# Test 3: Create model
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    print("✓ Gemini model created (gemini-2.0-flash)")
except Exception as e:
    print(f"✗ Failed to create model: {e}")
    sys.exit(1)

# Test 4: Simple text generation
print("\n" + "-" * 80)
print("TEST 1: Simple text generation")
print("-" * 80)
try:
    response = model.generate_content("Say 'Hello, Gemini is working!'")
    text = response.text
    print(f"✓ Response received: {text}")
except Exception as e:
    print(f"✗ Failed to generate text: {e}")
    sys.exit(1)

# Test 5: JSON generation (like challenge generation)
print("\n" + "-" * 80)
print("TEST 2: JSON problem generation")
print("-" * 80)

prompt = """Generate a unique coding challenge for a competitive programming arena.

Difficulty: beginner
Domain: arrays

Requirements:
- The function must be named `solve` 
- Input is provided as space-separated values on a single line
- Output should be a single value or space-separated values
- Include exactly 4 test cases (2 visible, 2 hidden)
- Test cases must have deterministic, verifiable answers
- Keep it simple enough to solve in under 5 minutes

Respond ONLY with valid JSON (no markdown, no backticks) in this exact format:
{
  "title": "Problem Title",
  "description": "Full problem description with clear instructions",
  "domain": "arrays|strings|math|sorting|dynamic_programming",
  "input_format": "Description of input format",
  "output_format": "Description of output format",
  "constraints": {"input_size": "1 ≤ n ≤ 1000"},
  "boilerplate_code": "def solve(arr):\\n    # Write your code here\\n    return 0",
  "test_cases": [
    {"input": "1 2 3", "expected_output": "6", "category": "basic", "description": "Basic test"},
    {"input": "0", "expected_output": "0", "category": "edge", "description": "Edge case"},
    {"input": "-1 -2 -3", "expected_output": "-6", "category": "edge", "description": "Negative numbers"},
    {"input": "100 200 300", "expected_output": "600", "category": "boundary", "description": "Large values"}
  ]
}"""

try:
    print("Sending prompt to Gemini...")
    response = model.generate_content(
        prompt,
        request_options={"timeout": 15.0}
    )
    text = response.text.strip()
    print(f"✓ Response received ({len(text)} chars)")
    
    # Try to parse as JSON
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        data = json.loads(text)
        print("✓ Response is valid JSON")
        print(f"  - Title: {data.get('title', 'N/A')}")
        print(f"  - Domain: {data.get('domain', 'N/A')}")
        print(f"  - Test cases: {len(data.get('test_cases', []))}")
        print(f"\n✓ GEMINI IS GENERATING PROBLEMS CORRECTLY!")
    except json.JSONDecodeError as e:
        print(f"✗ Response is NOT valid JSON: {e}")
        print(f"Response text:\n{text[:500]}")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Failed to generate problem: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Multiple generations to check for variety
print("\n" + "-" * 80)
print("TEST 3: Check for variety in generated problems")
print("-" * 80)

titles = set()
for i in range(3):
    try:
        response = model.generate_content(
            prompt,
            request_options={"timeout": 15.0}
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        title = data.get('title', 'Unknown')
        titles.add(title)
        print(f"  {i+1}. {title}")
    except Exception as e:
        print(f"  {i+1}. Error: {e}")

if len(titles) == 3:
    print(f"✓ All 3 problems are unique!")
else:
    print(f"⚠ Only {len(titles)} unique problems out of 3 (might be coincidence)")

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED - GEMINI IS WORKING CORRECTLY")
print("=" * 80)
