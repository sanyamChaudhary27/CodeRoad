#!/usr/bin/env python
"""Check available Gemini models and quota status"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Load environment
from dotenv import load_dotenv
backend_dir = Path("backend")
env_file = backend_dir / ".env"
load_dotenv(env_file)

print("=" * 80)
print("GEMINI MODELS AND QUOTA DIAGNOSTIC")
print("=" * 80)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("✗ GEMINI_API_KEY not found")
    sys.exit(1)
print(f"✓ GEMINI_API_KEY found: {api_key[:10]}...")

# Import Gemini
try:
    import google.generativeai as genai
    print("✓ google-generativeai imported")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

try:
    genai.configure(api_key=api_key)
    print("✓ Gemini configured")
except Exception as e:
    print(f"✗ Failed to configure: {e}")
    sys.exit(1)

# List available models
print("\n" + "-" * 80)
print("AVAILABLE MODELS")
print("-" * 80)

try:
    models = genai.list_models()
    print(f"Found {len(list(models))} models\n")
    
    # Reset and list again
    models = genai.list_models()
    for model in models:
        print(f"  • {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            methods = model.supported_generation_methods
            print(f"    Methods: {', '.join(methods)}")
except Exception as e:
    print(f"✗ Failed to list models: {e}")

# Test quota with a simple request
print("\n" + "-" * 80)
print("QUOTA TEST")
print("-" * 80)

try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    print("Testing with gemini-2.0-flash...")
    response = model.generate_content("Say 'OK'", request_options={"timeout": 5.0})
    print(f"✓ Request successful: {response.text}")
except Exception as e:
    error_msg = str(e)
    if "429" in error_msg or "quota" in error_msg.lower():
        print(f"✗ QUOTA EXCEEDED: {error_msg[:200]}")
        print("\nRECOMMENDATION:")
        print("  1. The free tier quota has been exhausted")
        print("  2. You need to either:")
        print("     a) Wait for the quota to reset (usually daily)")
        print("     b) Upgrade to a paid plan")
        print("     c) Use a different API key with available quota")
    elif "404" in error_msg or "not found" in error_msg.lower():
        print(f"✗ MODEL NOT FOUND: {error_msg[:200]}")
    else:
        print(f"✗ Error: {error_msg[:200]}")

print("\n" + "=" * 80)
