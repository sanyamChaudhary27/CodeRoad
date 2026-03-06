# Debug Arena 1v1 Matchmaking Implementation

## Issue Fixed
**Problem**: Debug Arena 1v1 matchmaking was failing with database error:
```
sqlite3.OperationalError: no such column: match_queue.challenge_type
```

**Root Cause**: The `match_queue` table was missing the `challenge_type` column needed to separate DSA and Debug matchmaking queues.

## Solution

### Database Migration
Created migration script `backend/add_challenge_type_to_queue.py` to add the missing column:

```sql
ALTER TABLE match_queue 
ADD COLUMN challenge_type VARCHAR(20) DEFAULT 'dsa' NOT NULL;
```

### How to Apply
Run the migration script:
```bash
cd backend
python add_challenge_type_to_queue.py
```

When prompted, type `yes` to confirm the migration.

## Implementation Details

### MatchQueue Model
The `MatchQueue` model in `backend/app/models/match.py` already had the `challenge_type` field defined:

```python
class MatchQueue(Base):
    __tablename__ = "match_queue"
    
    # ... other fields ...
    challenge_type = Column(String(20), default="dsa", nullable=False)
```

### Matchmaking Service
The matchmaking service uses `challenge_type` to:
1. Separate DSA and Debug queues
2. Match players only within the same challenge type
3. Create matches with the correct challenge type

### Frontend Integration
The Dashboard component passes `challenge_type` when joining queue:

```typescript
// Debug Arena 1v1 button
onClick={() => joinDebugQueue()}

// Function
const joinDebugQueue = async () => {
  await matchmakingService.joinQueue('1v1', undefined, undefined, 'debug');
  // ... polling logic
};
```

### API Endpoint
The `/matches/queue/join` endpoint accepts `challenge_type` parameter:

```python
@router.post("/queue/join")
async def join_queue(
    request: QueueJoinRequest,  # Contains challenge_type field
    current_user: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    result = match_service.join_match_queue(
        current_user["id"],
        request.preferred_format,
        request.challenge_type  # Passed to service
    )
```

## Testing

### Test Debug 1v1 Matchmaking
1. Open two browser windows/tabs
2. Log in with different accounts in each
3. Click "1v1 Battle" in Debug Arena on both
4. Both players should be matched within 30 seconds
5. Arena should load with a debug challenge
6. Header should show debug_rating (red badge)

### Expected Behavior
- DSA and Debug queues are completely separate
- Players in DSA queue won't match with Debug queue players
- Debug matches use debug_rating for matchmaking
- Debug matches have 150-second time limit (vs 120 for DSA)

## Files Modified

### Backend
- `backend/add_challenge_type_to_queue.py` - New migration script
- `backend/app/models/match.py` - MatchQueue model (already had field)
- `backend/app/services/match_service.py` - Uses challenge_type for matching
- `backend/app/api/match.py` - Accepts challenge_type parameter

### Frontend
- `frontend/src/pages/Dashboard.tsx` - Debug 1v1 button with queue logic
- `frontend/src/services/matchmakingService.ts` - joinQueue accepts challengeType

## Related Features

### Separate Rating Systems
- DSA: Uses `current_rating` (starts at 1200)
- Debug: Uses `debug_rating` (starts at 300)
- Each has independent win/loss tracking

### Time Limits
- DSA Solo: 120 seconds
- DSA 1v1: 120 seconds
- Debug Solo: 300 seconds (5 minutes)
- Debug 1v1: 150 seconds (2.5 minutes)

### Challenge Generation
- DSA: Uses AI-generated challenges or templates
- Debug: Uses predefined templates with intentional bugs
- Both use same judging infrastructure

## Future Enhancements

1. **Queue Status Display**: Show number of players in each queue
2. **Estimated Wait Time**: Calculate based on queue size and match rate
3. **Rating-Based Matching**: Prefer opponents within ±200 ELO range
4. **Queue Timeout**: Auto-remove players after 5 minutes
5. **Cross-Queue Notification**: Suggest trying other queue if wait is long

## Troubleshooting

### Migration Already Applied
If you see "column already exists" error, the migration was already run. No action needed.

### Database Locked
If you get "database is locked" error:
1. Stop the backend server
2. Run the migration
3. Restart the backend server

### Queue Not Working
If matchmaking still fails:
1. Check backend logs for errors
2. Verify migration completed successfully
3. Restart backend server to reload schema
4. Clear browser cache and reload frontend

## Notes

- Migration is idempotent (safe to run multiple times)
- Existing queue entries will default to 'dsa' challenge_type
- No data loss - only adds a new column
- Compatible with existing DSA matchmaking
