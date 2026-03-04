# Final Fixes: Opponent Display and Rating Updates

## Issues Fixed

### Issue 1: Opponent Showing "OPPONENT 1200" Instead of Actual Data
**Problem**: Arena header was showing generic "OPPONENT" and "1200" instead of the actual opponent's username and rating.

**Root Cause**: 
- Arena initialization was trying to access nested objects (`matchDetails.player2.username`)
- Backend returns flat fields (`matchDetails.player2_username`, `matchDetails.player2_rating`)
- Mismatch caused fallback to default values

**Solution**:
Updated Arena initialization to use flat fields from backend:
```typescript
localOpponent = {
  player_id: isUserPlayer1 ? matchDetails.player2_id : matchDetails.player1_id,
  username: isUserPlayer1 ? (matchDetails.player2_username || 'Opponent') : (matchDetails.player1_username || 'Opponent'),
  current_rating: isUserPlayer1 ? (matchDetails.player2_rating || 1200) : (matchDetails.player1_rating || 1200),
  submissions_count: isUserPlayer1 ? (matchDetails.player2_submissions || 0) : (matchDetails.player1_submissions || 0),
  is_done: isUserPlayer1 ? (matchDetails.player2_done || false) : (matchDetails.player1_done || false)
};
```

### Issue 2: Dashboard Card Still Showing "300 ELO" After Matches
**Problem**: Debug Arena card on Dashboard always showed "300 ELO" even after rating changed.

**Root Cause**: 
- Backend `/auth/me` endpoint was NOT returning `debug_rating` field
- Frontend was using fallback value: `{user.debug_rating || 300}`
- Since `debug_rating` was undefined, it always showed 300

**Solution**:
1. **Backend Fix**: Added debug fields to `/auth/me` response in `backend/app/api/auth.py`:
```python
return {
    "id": player.id,
    "username": player.username,
    "email": player.email,
    "current_rating": player.current_rating,
    # ... other fields ...
    "debug_rating": player.debug_rating,
    "debug_matches_played": player.debug_matches_played,
    "debug_wins": player.debug_wins,
    "debug_losses": player.debug_losses
}
```

2. **Frontend Fix**: Changed Dashboard useEffect dependency from `[location]` to `[location.pathname]` for more reliable refresh

## Files Modified

### Backend
- `backend/app/api/auth.py`
  - Added `debug_rating`, `debug_matches_played`, `debug_wins`, `debug_losses` to `/auth/me` response

### Frontend
- `frontend/src/pages/Arena.tsx`
  - Fixed opponent initialization to use flat fields from backend
  - Now correctly reads `player2_username`, `player2_rating`, etc.

- `frontend/src/pages/Dashboard.tsx`
  - Changed useEffect dependency to `[location.pathname]` for better refresh behavior

## Testing Steps

1. **Restart Backend Server** (REQUIRED for auth.py changes to take effect)
   ```bash
   # Stop current server (Ctrl+C)
   # Restart
   python -m uvicorn backend.app.app:app --reload
   ```

2. **Clear Browser Cache** or Hard Refresh (Ctrl+Shift+R)

3. **Test Opponent Display**:
   - Start a 1v1 match (DSA or Debug)
   - Check header shows actual opponent username (not "OPPONENT")
   - Check header shows actual opponent rating (not "1200")

4. **Test Dashboard Rating Update**:
   - Note your current debug rating on Dashboard
   - Play a debug match (solo or 1v1)
   - Return to Dashboard
   - Verify debug rating card shows updated value

## Expected Behavior

### Arena Header (1v1 Mode)
```
┌─────────────────────────────────────────┐
│ Left: Your username + Your rating      │
│ Center: [You: 3] [Timer] [Opp: 2]     │
│ Right: OPPONENT_USERNAME + Their rating│
└─────────────────────────────────────────┘
```

### Dashboard Cards
- **DSA Arena Card**: Shows `current_rating` (updates after DSA matches)
- **Debug Arena Card**: Shows `debug_rating` (updates after Debug matches)
- Both update immediately when navigating back from Arena

## Common Issues

### If opponent still shows "OPPONENT 1200":
- Backend might not be returning flat fields
- Check backend logs for match data structure
- Verify `get_match()` in `match_service.py` is enriching data

### If Dashboard still shows "300":
- Backend server not restarted (changes in auth.py require restart)
- Browser cache not cleared
- Check browser console for API response from `/auth/me`
- Verify response includes `debug_rating` field

## API Response Examples

### /auth/me (After Fix)
```json
{
  "id": "player_123",
  "username": "SANYAM27",
  "current_rating": 1289,
  "debug_rating": 315,
  "debug_matches_played": 5,
  "debug_wins": 3,
  "debug_losses": 2
}
```

### /matches/{match_id} (Flat Fields)
```json
{
  "match_id": "match_123",
  "player1_id": "player_123",
  "player1_username": "SANYAM27",
  "player1_rating": 1289,
  "player2_id": "player_456",
  "player2_username": "Opponent",
  "player2_rating": 305,
  "player2_submissions": 2
}
```

## Notes

- All changes are backward compatible
- No database migrations required
- Frontend changes are hot-reloaded automatically
- Backend changes require server restart
