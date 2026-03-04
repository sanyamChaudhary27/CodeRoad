"""
Test JSON parsing with the actual response from Gemini
"""
import json

# This is what Gemini returned (from the error log)
text = """{
  "title": "Sum of Strictly Unique Elements",
  "description": "Given a list of integers, calculate the sum of all integers that appear exactly once in the list.\\n\\nFor example, if the list is `[1, 2, 3, 2, 1, 4]`, the numbers 3 and 4 appear exactly once"
}"""

print("Original text:")
print(text[:200])
print()

# Try parsing directly
try:
    data = json.loads(text)
    print("✅ Direct parsing worked!")
    print(f"Title: {data['title']}")
    print(f"Description: {data['description'][:100]}...")
except json.JSONDecodeError as e:
    print(f"❌ Direct parsing failed: {e}")
    print()
    
    # Try with regex extraction
    import re
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
        print("Extracted JSON:")
        print(cleaned[:200])
        print()
        
        try:
            data = json.loads(cleaned)
            print("✅ Regex extraction worked!")
            print(f"Title: {data['title']}")
            print(f"Description: {data['description'][:100]}...")
        except json.JSONDecodeError as e2:
            print(f"❌ Regex extraction also failed: {e2}")
