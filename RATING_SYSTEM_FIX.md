# Rating System Bug Fix

## Problem Identified

User reported critical bugs in 1v1 match rating system:

1. **Both players jumped from 300 to 800 rating** (500 point increase!)
2. **Loser gained points instead of losing points**
3. **Neither player passed any tests** (both 0/4), yet both gained massive rating

## Root Cause

Found in `backend/app/services/rating_service.py` line 125:

```python
# Ensure rating doesn't go below minimum
new_rating = max(800, new_rating)
```

This **rating floor of 800** was forcing all ratings up to 800 minimum, even when players should lose points.

### What Happened in User's Match:

1. Both players: 300 rating, 0/4 tests passed
2. Winner determined by complexity tiebreaker (correct behavior)
3. ELO calculation with K_FACTOR=32:
   - Winner: 300 + 16 = 316 → **forced to 800** by floor
   - Loser: 300 - 16 = 284 → **forced to 800** by floor
4. Result: Both players gained 500 points!

## Solution

Changed rating floor from 800 to 100:

```python
# Ensure rating doesn't go below minimum (100 is the floor)
new_rating = max(100, new_rating)
```

## Additional Fixes

Fixed inconsistent default ratings throughout the codebase:

1. **Player model** - Changed default from 1200 to 300
2. **Rating model** - Changed default from 1200 to 300
3. **Rating model peak_rating** - Changed default from 1200 to 300
4. **auth.py registration** - Changed hardcoded 1200 to use `settings.INITIAL_ELO_RATING` (300)

All new players now start at 300 rating consistently.

## Verification

Created `test_rating_fix.py` to verify:

- ✓ Winner gains points (+16)
- ✓ Loser loses points (-16)
- ✓ Rating changes are reasonable (~16-32 points with K_FACTOR=32)
- ✓ Ratings can go below 800 (floor is now 100)

## Winner Determination Logic (Already Correct)

The system correctly prioritizes:

1. **Test case score** (Accuracy) - PRIMARY
2. Execution time (Speed; ±3s tolerance)
3. Complexity score (Efficiency)
4. Memory usage (Space)
5. AI assistance probability (Integrity)

The user's concern about "winner based on complexity" was actually correct behavior - when both players score 0/4 tests, the tiebreaker is complexity. This is fair.

## Files Modified

- `backend/app/services/rating_service.py` - Changed rating floor from 800 to 100
- `backend/app/models/player.py` - Changed default rating from 1200 to 300
- `backend/app/models/rating.py` - Changed default rating and peak_rating from 1200 to 300
- `backend/app/api/auth.py` - Changed hardcoded 1200 to use settings.INITIAL_ELO_RATING

## Impact

- Players can now have ratings below 800 (down to 100 minimum)
- Losers will properly lose rating points
- Winners will gain reasonable amounts (~16-32 points per match)
- Initial rating of 300 now makes sense (was being forced to 800 immediately)
- All new registrations start at 300 consistently
