# Challenge Diversity Improvement Plan

## Current Issue
The same problem ("Find the Maximum Subarray Sum") is being generated repeatedly (5/6 times), reducing variety for players.

## Root Causes
1. **In-Memory Tracking Only**: `_recently_used_titles` resets on server restart
2. **Title-Based Exclusion**: AI can generate similar problems with different titles
3. **No Database History Check**: System doesn't check what challenges were recently generated
4. **Limited Temperature**: Current temperature (0.8) might not provide enough randomness

## Proposed Solutions

### Solution 1: Database-Based Recent Challenge Tracking (Recommended)

Update the challenge service to check the database for recently generated challenges:

```python
# backend/app/services/challenge_service.py

def _get_recent_challenge_titles(self, db: Session, hours: int = 24, limit: int = 20) -> List[str]:
    """Get titles of recently generated challenges from database"""
    from datetime import datetime, timedelta
    from ..models import Challenge
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    recent_challenges = db.query(Challenge).filter(
        Challenge.created_at >= cutoff_time
    ).order_by(desc(Challenge.created_at)).limit(limit).all()
    
    return [c.title for c in recent_challenges]

def generate_challenge(self, db: Session, difficulty: str = "intermediate", ...):
    """Generate a challenge with database-backed diversity"""
    
    # Get recent challenges from database
    recent_titles = self._get_recent_challenge_titles(db, hours=24, limit=20)
    self._recently_used_titles.update(recent_titles)
    
    # Rest of the generation logic...
```

### Solution 2: Increase AI Temperature for More Variety

```python
# In _generate_groq_challenge method
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    temperature=1.0,  # Increase from 0.8 to 1.0 for more creativity
    max_tokens=2500,
)
```

### Solution 3: Add Domain Rotation

Force different problem domains to ensure variety:

```python
# backend/app/services/challenge_service.py

class ChallengeService:
    def __init__(self):
        # ... existing init code ...
        self._domain_rotation = ['arrays', 'strings', 'math', 'sorting', 'dynamic_programming']
        self._current_domain_index = 0
    
    def generate_challenge(self, db: Session, difficulty: str = "intermediate", ...):
        # Rotate through domains if not specified
        if not domain:
            domain = self._domain_rotation[self._current_domain_index]
            self._current_domain_index = (self._current_domain_index + 1) % len(self._domain_rotation)
            logger.info(f"Using rotated domain: {domain}")
        
        # Rest of generation logic...
```

### Solution 4: Add Problem Concept Tracking

Track not just titles, but problem concepts:

```python
# Add to prompt
recent_concepts = ["maximum subarray", "kadane's algorithm", "dynamic programming"]
concept_exclusion = f"\n\nAVOID THESE CONCEPTS: {', '.join(recent_concepts)}"

prompt = f"""Generate a coding challenge...
{concept_exclusion}
..."""
```

### Solution 5: Implement Challenge Pool System

Pre-generate a pool of diverse challenges:

```python
# backend/app/services/challenge_pool.py

class ChallengePool:
    """Maintains a pool of pre-generated diverse challenges"""
    
    def __init__(self, db: Session, pool_size: int = 50):
        self.db = db
        self.pool_size = pool_size
        self.min_pool_size = 10
        
    def get_challenge(self, difficulty: str, domain: Optional[str] = None) -> Challenge:
        """Get a challenge from the pool, refill if needed"""
        # Query unused challenges from pool
        query = self.db.query(Challenge).filter(
            Challenge.difficulty == difficulty,
            Challenge.times_used == 0  # Unused challenges
        )
        
        if domain:
            query = query.filter(Challenge.domain == domain)
        
        challenges = query.limit(self.min_pool_size).all()
        
        # Refill pool if running low
        if len(challenges) < self.min_pool_size:
            self._refill_pool(difficulty, domain)
            challenges = query.limit(self.min_pool_size).all()
        
        # Select random challenge
        if challenges:
            challenge = random.choice(challenges)
            challenge.times_used += 1
            self.db.commit()
            return challenge
        
        # Fallback: generate new challenge
        return None
    
    def _refill_pool(self, difficulty: str, domain: Optional[str]):
        """Generate new challenges to refill the pool"""
        from .challenge_service import get_challenge_service
        service = get_challenge_service()
        
        # Generate multiple challenges with different domains
        domains = ['arrays', 'strings', 'math', 'sorting', 'dynamic_programming']
        for d in domains:
            try:
                service.generate_challenge(
                    db=self.db,
                    difficulty=difficulty,
                    domain=d,
                    use_ai=True
                )
            except Exception as e:
                logger.warning(f"Failed to generate challenge for domain {d}: {e}")
```

## Implementation Priority

### Phase 1: Quick Wins (Immediate)
1. ✅ Increase AI temperature to 1.0
2. ✅ Add database-based recent challenge tracking
3. ✅ Improve exclusion prompt with more context

### Phase 2: Medium Term (This Week)
1. Implement domain rotation
2. Add problem concept tracking
3. Improve AI prompt with more specific exclusions

### Phase 3: Long Term (Next Sprint)
1. Implement challenge pool system
2. Add challenge quality scoring
3. Implement player feedback loop

## Quick Fix Implementation

Here's the immediate fix you can apply:

```python
# backend/app/services/challenge_service.py

def generate_challenge(self, db: Session, difficulty: str = "intermediate", 
                      player_rating: int = 300, domain: Optional[str] = None, 
                      use_ai: bool = True) -> Dict[str, Any]:
    """Generate a challenge with improved diversity"""
    
    # QUICK FIX: Check database for recent challenges
    try:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = db.query(Challenge).filter(
            Challenge.created_at >= cutoff,
            Challenge.difficulty == difficulty
        ).order_by(desc(Challenge.created_at)).limit(15).all()
        
        for c in recent:
            self._recently_used_titles.add(c.title)
        
        logger.info(f"Loaded {len(recent)} recent challenges to avoid repetition")
    except Exception as e:
        logger.warning(f"Could not load recent challenges: {e}")
    
    # Rest of existing code...
```

And update the temperature:

```python
# In _generate_groq_challenge method, line ~340
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    temperature=1.0,  # Changed from 0.8
    max_tokens=2500,
)
```

## Testing the Fix

After implementing:
1. Generate 10 consecutive challenges
2. Verify at least 7-8 are unique
3. Check that problem concepts vary (not just titles)
4. Monitor logs for "AVOID THESE PROBLEMS" messages

## Expected Results

- **Before**: 5/6 same problem
- **After**: 8/10 unique problems (80% diversity)
- **Long-term goal**: 9/10 unique problems (90% diversity)

---

**Status**: Ready for Implementation  
**Priority**: Medium (affects user experience but not critical)  
**Effort**: 30 minutes for quick fix, 2-3 hours for full solution
