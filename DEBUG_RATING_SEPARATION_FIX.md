# Debug Rating Separation Fix

## Critical Bug Fixed
**Problem**: Debug Arena matches were updating DSA ratings instead of debug ratings, causing incorrect rating changes.

**Impact**: 
- Debug matches affected DSA leaderboard rankings
- Debug rating system was not being used
- Players' DSA ratings changed when playing debug challenges

## Root Cause
The `conclude_match` method in `match_service.py` always called `update_player_rating()` (DSA rating update) regardless of the match's `challenge_type`. It didn't check whether the match was DSA or Debug.

## Solution

### Match Service Update
Modified `backend/app/services/match_service.py` to check `challenge_type` before updating ratings:

```python
# Check challenge type to determine which rating to update
if match.challenge_type == "debug":
    # Update debug ratings
    player1_update = self.rating_service.update_debug_rating(
        player_id=match.player1_id,
        opponent_id=match.player2_id,
        match_id=match_id,
        match_result=player1_result,
        opponent_rating=match.player2.debug_rating if match.player2 else settings.DEBUG_INITIAL_RATING
    )
    # ... same for player2
else:
    # Update DSA ratings
    player1_update = self.rating_service.update_player_rating(
        player_id=match.player1_id,
        opponent_id=match.player2_id,
        match_id=match_id,
        match_result=player1_result,
        opponent_rating=match.player2.current_rating if match.player2 else 1200,
        cheat_probability=cheat_probability
    )
    # ... same for player2
```

### Solo Match Handling
Also updated solo match rating display to show correct rating based on challenge type:

```python
# Get appropriate rating based on challenge type
if match.challenge_type == "debug":
    current_rating = match.player1.debug_rating if match.player1 else settings.DEBUG_INITIAL_RATING
else:
    current_rating = match.player1.current_rating if match.player1 else 1200
```

## Rating Systems Now Properly Separated

### DSA Rating System
- Field: `player.current_rating`
- Initial: 1200 ELO
- Updated by: DSA matches (challenge_type='dsa')
- Tracked in: `ratings` table with challenge_type='dsa'
- Stats: `matches_played`, `wins`, `losses`, `draws`

### Debug Rating System  
- Field: `player.debug_rating`
- Initial: 300 ELO
- Updated by: Debug matches (challenge_type='debug')
- Tracked in: Player model directly (no separate ratings table entry)
- Stats: `debug_matches_played`, `debug_wins`, `debug_losses`, `debug_draws`

## Verification

### Test DSA Match
1. Play DSA solo or 1v1 match
2. Check Dashboard - DSA ELO should change
3. Check Dashboard - Debug ELO should NOT change

### Test Debug Match
1. Play Debug solo or 1v1 match
2. Check Dashboard - Debug ELO should change
3. Check Dashboard - DSA ELO should NOT change

### Check Logs
Backend logs now show:
```
INFO: Checking rating update for {match_id}. Format: 1v1, Player2: {id}, Challenge Type: debug
INFO: Updated debug rating for player {id}: 300 -> 315 (+15)
```

## Related Files

### Backend
- `backend/app/services/match_service.py` - Fixed rating update logic
- `backend/app/services/rating_service.py` - Has both update methods
- `backend/app/models/match.py` - Match model with challenge_type
- `backend/app/models/player.py` - Player model with both rating fields

### Frontend
- `frontend/src/pages/Arena.tsx` - Shows correct rating in header
- `frontend/src/pages/Dashboard.tsx` - Shows both ratings separately
- `frontend/src/services/authService.ts` - User type with both ratings

## Configuration

### Settings (backend/app/config.py)
```python
# DSA Settings
INITIAL_ELO_RATING = 1200
ELO_K_FACTOR = 32

# Debug Settings  
DEBUG_INITIAL_RATING = 300
DEBUG_SOLO_TIME_LIMIT = 300  # 5 minutes
DEBUG_1V1_TIME_LIMIT = 150   # 2.5 minutes
```

## Future Enhancements

1. **Separate Leaderboards**: Create dedicated debug leaderboard endpoint
2. **Rating History**: Track debug rating changes over time
3. **Cross-Arena Stats**: Show combined stats across both arenas
4. **Rating Badges**: Award badges for milestones in each arena
5. **Arena Preferences**: Let users set preferred arena type

## Notes

- Solo matches (practice) don't affect ratings in either system
- Only 1v1 competitive matches update ratings
- Debug rating uses same ELO algorithm as DSA
- Rating confidence system only applies to DSA (not debug yet)
- Integrity checks only apply to DSA matches currently

## Rollback Instructions

If issues occur, revert the changes in `match_service.py`:
```bash
git checkout HEAD -- backend/app/services/match_service.py
```

Then restart the backend server.
