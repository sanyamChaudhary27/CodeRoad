# Complete Fix Instructions for challenge_service.py

## Problem
The file `backend/app/services/challenge_service.py` has multiple issues:
1. Still using Gemini (old code)
2. Missing ELO-smart difficulty adjustment
3. Boilerplate code includes solutions

## Solution
The file needs to be completely rewritten with:
1. Groq AI only (5 API keys with rotation)
2. ELO-smart difficulty (beginner < 500, intermediate 500-800, advanced 800+)
3. Boilerplate cleaning to remove solutions

## Status
All my automated attempts to fix the file resulted in corruption or deletion. The committed version in git still has the old Gemini code.

## What Works
- Initial rating is 300 (config.py) ✓
- All players reset to rating 300 ✓
- 5 Groq API keys configured in .env ✓

## What's Missing
The challenge_service.py file needs manual reconstruction with:
1. Remove all Gemini code
2. Add ELO-smart prompt generation based on player_rating
3. Add `_clean_boilerplate()` method
4. Apply boilerplate cleaning after JSON parsing

## Recommendation
Since automated edits keep corrupting the file, I recommend:
1. Manually edit the file in your IDE
2. Or provide the file content and I'll generate a complete corrected version
3. Or use the working version from my earlier successful changes (before corruption)

## Key Code Sections Needed

### 1. ELO-Smart Complexity Guide (in _generate_groq_challenge)
```python
if player_rating < 500:
    complexity_guide = """BEGINNER problems: sum, max, count, reverse"""
elif player_rating < 800:
    complexity_guide = """INTERMEDIATE problems: two pointers, rotation"""
else:
    complexity_guide = """ADVANCED problems: DP, complex algorithms"""
```

### 2. Boilerplate Cleaning Method
```python
def _clean_boilerplate(self, boilerplate: str) -> str:
    lines = boilerplate.split('\n')
    # Find function def
    # Keep only: def solve(...) + comment + return 0
    return clean_code
```

### 3. Apply Cleaning
```python
boilerplate = data.get('boilerplate_code', 'def solve(arr):\n    return 0')
boilerplate = self._clean_boilerplate(boilerplate)
# Use boilerplate in return dict
```

## Files for Reference
- `ELO_SMART_GENERATION.md` - Explains the ELO-smart system
- `BOILERPLATE_FIX.md` - Explains the boilerplate cleaning
- `GROQ_MULTI_KEY_SETUP.md` - Explains the 5-key setup
