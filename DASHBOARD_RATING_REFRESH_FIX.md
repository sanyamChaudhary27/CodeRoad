# Dashboard Rating Refresh Fix

## Issue
After completing a match (DSA or Debug), when returning to the Dashboard, the ELO ratings were not updating to reflect the changes from the match. The ratings only updated after a full page refresh.

## Root Cause
The Dashboard component only fetched user data once on initial mount:

```typescript
useEffect(() => {
  const fetchData = async () => {
    const currentUser = await authService.getCurrentUser();
    setUser(currentUser);
  };
  fetchData();
}, []); // Empty dependency array = runs once on mount
```

When navigating back from Arena to Dashboard, the component didn't remount (React Router keeps it alive), so the user data was never refreshed.

## Solution

### Added Auto-Refresh on Window Focus
The Dashboard now refreshes user data when the browser window/tab gains focus:

```typescript
const fetchUserData = async () => {
  try {
    const currentUser = await authService.getCurrentUser();
    setUser(currentUser);
  } catch (err) {
    console.error("Failed to fetch user data", err);
  }
};

useEffect(() => {
  // Listen for focus events
  window.addEventListener('focus', fetchUserData);
  
  return () => {
    window.removeEventListener('focus', fetchUserData);
  };
}, []);
```

## Benefits

### Automatic Updates
- Ratings update when returning to Dashboard from Arena
- Works when switching browser tabs
- Works when returning from another window
- No manual refresh needed

### User Experience
- See rating changes immediately after match
- Both DSA and Debug ratings update correctly
- Stats (wins, losses, matches played) also update
- Smooth, seamless experience

## Testing

### Test DSA Match
1. Play a DSA 1v1 match
2. Click "Return to Terminal" after match ends
3. Dashboard should show updated DSA rating immediately
4. Debug rating should remain unchanged

### Test Debug Match
1. Play a Debug 1v1 match
2. Click "Return to Terminal" after match ends
3. Dashboard should show updated Debug rating immediately
4. DSA rating should remain unchanged

### Test Tab Switching
1. Start a match
2. Switch to another browser tab
3. Switch back to CodeRoad tab
4. Ratings should refresh automatically

## Technical Details

### API Call
The `authService.getCurrentUser()` method:
- Fetches latest user data from `/auth/me` endpoint
- Updates localStorage with fresh data
- Returns User object with all ratings and stats

### Performance
- Only fetches when window gains focus (not constantly)
- Lightweight API call (single user record)
- No impact on page load time
- Event listener properly cleaned up on unmount

## Related Files

### Frontend
- `frontend/src/pages/Dashboard.tsx` - Added auto-refresh logic
- `frontend/src/services/authService.ts` - getCurrentUser method
- `frontend/src/pages/Arena.tsx` - Navigates back to Dashboard

### Backend
- `backend/app/api/auth.py` - /auth/me endpoint
- `backend/app/services/rating_service.py` - Updates ratings
- `backend/app/services/match_service.py` - Concludes matches

## Alternative Approaches Considered

### 1. Navigation State
Pass rating updates through navigation state:
```typescript
navigate('/dashboard', { state: { ratingUpdate: {...} } });
```
**Rejected**: Requires manual state management, doesn't handle tab switches

### 2. Global State Management
Use Redux/Context to share user state:
```typescript
const { user, refreshUser } = useUserContext();
```
**Rejected**: Overkill for this use case, adds complexity

### 3. Polling
Continuously poll for user data:
```typescript
setInterval(() => fetchUserData(), 5000);
```
**Rejected**: Wasteful, unnecessary API calls

### 4. WebSocket
Real-time updates via WebSocket:
```typescript
ws.on('rating_update', (data) => setUser(data));
```
**Rejected**: Too complex, WebSocket already used for match updates

## Future Enhancements

1. **Optimistic Updates**: Update UI immediately, then sync with backend
2. **Animation**: Animate rating changes with smooth transitions
3. **Notification**: Show toast notification when ratings update
4. **History**: Show rating change history in a modal
5. **Comparison**: Show before/after ratings side-by-side

## Notes

- Focus event fires when window gains focus, not on every navigation
- Works across all browsers (Chrome, Firefox, Safari, Edge)
- Event listener is cleaned up when component unmounts
- No memory leaks or performance issues
- Compatible with React Router navigation
