# Personalized Challenge Generation Feature

## Overview

The challenge generation system now learns from each player's recent match history to generate personalized problems that match their skill level and interests, while ensuring variety.

## How It Works

### 1. Player History Analysis
When generating a new challenge, the system:
- Fetches the player's last 5 completed matches
- Analyzes the challenges they played
- Extracts key information:
  - Challenge title
  - Difficulty level
  - Problem domain (arrays, strings, etc.)
  - Player's success rate on each challenge

### 2. AI Learning Prompt
The player's history is added to the AI prompt:

```
PLAYER'S RECENT MATCH HISTORY (Learn from these but generate something NEW):
1. "Find the Maximum Subarray Sum" (intermediate, arrays) - Success: 75%
2. "Count Inversions in Array" (intermediate, arrays) - Success: 50%
3. "Longest Palindromic Substring" (intermediate, strings) - Success: 25%
4. "Two Sum Problem" (beginner, arrays) - Success: 100%
5. "Valid Parentheses" (beginner, strings) - Success: 100%

GENERATE a problem SIMILAR in style/difficulty to these, but with a DIFFERENT concept/algorithm. 
DO NOT repeat any of these exact problems!
```

### 3. Smart Generation
The AI uses this information to:
- ✅ Generate problems at the right difficulty level
- ✅ Focus on domains the player has experience with
- ✅ Create variations of problem types they've seen
- ✅ Avoid exact repetition
- ✅ Maintain appropriate challenge level

## Benefits

### For Players
1. **Personalized Learning Path**: Problems adapt to what you've practiced
2. **Progressive Difficulty**: Builds on concepts you've already encountered
3. **Variety with Familiarity**: New problems feel related but not repetitive
4. **Better Engagement**: Challenges match your interests and skill level

### For the Platform
1. **Higher Retention**: Players get problems suited to their level
2. **Better Learning Outcomes**: Gradual skill progression
3. **Reduced Frustration**: No more "too easy" or "too hard" problems
4. **Data-Driven**: Uses actual performance data

## Example Scenarios

### Scenario 1: Beginner Player
**History**: Mostly solved simple array problems (sum, max, min)
**Generated**: "Find Second Largest Element" - Similar concept, slightly harder

### Scenario 2: Intermediate Player
**History**: Mix of array and string problems, 50-75% success rate
**Generated**: "Merge Overlapping Intervals" - Combines array manipulation with logic

### Scenario 3: Advanced Player
**History**: Complex DP and graph problems, high success rate
**Generated**: "Longest Increasing Subsequence with K Constraint" - Advanced DP variant

## Technical Implementation

### Code Flow

```python
# 1. Fetch player history
recent_matches = db.query(Match).filter(
    or_(Match.player1_id == player_id, Match.player2_id == player_id),
    Match.status == 'concluded'
).order_by(desc(Match.concluded_at)).limit(5).all()

# 2. Extract challenge information
for match in recent_matches:
    challenge = db.query(Challenge).filter(Challenge.id == match.challenge_id).first()
    player_score = match.player1_score if match.player1_id == player_id else match.player2_score
    success_rate = (player_score / max_score * 100)
    
    history_challenges.append({
        'title': challenge.title,
        'difficulty': challenge.difficulty,
        'domain': challenge.domain,
        'success_rate': f"{success_rate:.0f}%"
    })

# 3. Add to AI prompt
player_history = "\n\nPLAYER'S RECENT MATCH HISTORY...\n"
for i, ch in enumerate(history_challenges, 1):
    player_history += f"{i}. \"{ch['title']}\" ({ch['difficulty']}, {ch['domain']}) - Success: {ch['success_rate']}\n"

# 4. Generate with personalization
challenge = groq_client.chat.completions.create(
    messages=[{"role": "user", "content": prompt + player_history}],
    temperature=1.0
)
```

### Key Files Modified

1. **backend/app/services/challenge_service.py**
   - Added `player_id` parameter to `generate_challenge()`
   - Added `_generate_groq_challenge()` player history logic
   - Fetches last 5 matches and extracts challenge info

2. **backend/app/services/match_service.py**
   - Updated `create_solo_match()` to pass `player_id`
   - Updated `get_queue_status_with_matchmaking()` to pass `player_id`

3. **backend/app/api/challenge.py**
   - Updated `/generate` endpoint to pass `player_id`

## Privacy & Performance

### Privacy
- Only uses player's own match history
- No cross-player data sharing
- History is used only for AI prompt, not stored separately

### Performance
- Minimal overhead: Single database query (5 matches)
- Cached in memory during generation
- Falls back gracefully if history unavailable

## Future Enhancements

### Phase 1 (Current)
- ✅ Use last 5 matches
- ✅ Extract title, difficulty, domain, success rate
- ✅ Add to AI prompt

### Phase 2 (Planned)
- [ ] Track problem concepts/algorithms (not just titles)
- [ ] Weight recent matches more heavily
- [ ] Consider time spent on each problem
- [ ] Track which problems player struggled with

### Phase 3 (Future)
- [ ] Collaborative filtering (similar players)
- [ ] Skill gap analysis
- [ ] Adaptive difficulty curves
- [ ] Learning path recommendations

## Testing

### Manual Testing
1. Create a new player account
2. Complete 5 different challenges
3. Request a new challenge
4. Verify the generated problem is related but different

### Expected Behavior
- First challenge (no history): Random appropriate problem
- After 1-2 matches: Some influence from history
- After 5+ matches: Strong personalization

### Logs to Check
```
INFO:app.services.challenge_service:Using player history: 5 recent challenges for personalization
INFO:app.services.challenge_service:Attempting Groq AI generation for intermediate challenge (rating: 798)
```

## Configuration

### Adjustable Parameters

```python
# Number of recent matches to consider
HISTORY_LIMIT = 5  # Can be changed to 3-10

# Time window for recent matches
HISTORY_HOURS = 24 * 7  # Last 7 days (optional filter)

# Success rate calculation
MAX_TEST_CASES = 4  # Adjust based on your test case count
```

## Troubleshooting

### Issue: No personalization happening
**Check**: 
- Player has completed matches
- Matches have `concluded` status
- Challenges exist in database
- Logs show "Using player history"

### Issue: Same problems still generated
**Check**:
- AI temperature is 1.0 (not 0.8)
- Recent challenges are being excluded
- Player history is being passed correctly

### Issue: Problems too hard/easy
**Check**:
- Player rating is accurate
- Success rates are calculated correctly
- Difficulty mapping is appropriate

## Metrics to Monitor

1. **Challenge Diversity**: Unique problems per 10 generations
2. **Player Satisfaction**: Completion rates after personalization
3. **Difficulty Accuracy**: Success rate distribution (target: 50-75%)
4. **Engagement**: Time spent per challenge

---

**Status**: ✅ Implemented and Ready for Testing  
**Version**: 1.0  
**Last Updated**: March 4, 2026  
**Impact**: High - Significantly improves player experience
