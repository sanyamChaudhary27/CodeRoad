# Debug Arena - Implementation Tasks

## Phase 1: Database & Models

### Task 1.1: Update Challenge Model
- [ ] Add `challenge_type` field to Challenge model (enum: "dsa", "debug")
- [ ] Add `broken_code` field to store the buggy code
- [ ] Add `bug_count` field to track number of bugs
- [ ] Add `bug_types` field (JSON) to store bug categories
- [ ] Update database migration script
- [ ] Test model changes

**Files to modify:**
- `backend/app/models/match.py` (Challenge model)
- Create migration script

**Estimated time:** 1 hour

---

### Task 1.2: Add Debug Arena Rating System
- [ ] Add `debug_rating` field to Player model
- [ ] Add `debug_matches_played` field to Player model
- [ ] Add `debug_wins` field to Player model
- [ ] Update Rating model to support challenge_type
- [ ] Set default debug_rating to 300
- [ ] Update database migration script
- [ ] Test rating fields

**Files to modify:**
- `backend/app/models/player.py`
- `backend/app/models/rating.py`
- Create migration script

**Estimated time:** 1 hour

---

## Phase 2: Backend - Challenge Generation

### Task 2.1: Create Debug Challenge Templates
- [ ] Create fallback templates for debug challenges
- [ ] Include broken code examples for each difficulty
- [ ] Add bug descriptions and solutions
- [ ] Support multiple programming languages
- [ ] Add to extended_templates.py

**Files to modify:**
- `backend/app/services/extended_templates.py`

**Estimated time:** 2 hours

---

### Task 2.2: Implement Debug Challenge AI Prompt
- [ ] Create AI prompt for generating broken code
- [ ] Include instructions for bug injection
- [ ] Specify bug types and difficulty levels
- [ ] Add examples of good debug challenges
- [ ] Include correct solution generation
- [ ] Test with Groq API

**Files to modify:**
- `backend/app/services/challenge_service.py`

**Estimated time:** 2 hours

---

### Task 2.3: Add Debug Challenge Generation Logic
- [ ] Create `generate_debug_challenge()` method
- [ ] Implement bug injection logic
- [ ] Parse AI response for broken code
- [ ] Validate generated challenge structure
- [ ] Add personalization based on player history
- [ ] Add diversity tracking for debug challenges
- [ ] Handle fallback to templates
- [ ] Test challenge generation

**Files to modify:**
- `backend/app/services/challenge_service.py`

**Estimated time:** 3 hours

---

## Phase 3: Backend - API Endpoints

### Task 3.1: Update Challenge API
- [ ] Add `challenge_type` parameter to generate endpoint
- [ ] Create `/challenges/debug/generate` endpoint
- [ ] Update challenge retrieval to filter by type
- [ ] Add validation for challenge_type
- [ ] Test API endpoints

**Files to modify:**
- `backend/app/api/challenge.py`

**Estimated time:** 1 hour

---

### Task 3.2: Update Match Service for Debug Arena
- [ ] Add `challenge_type` parameter to match creation
- [ ] Update `create_solo_match()` for debug challenges
- [ ] Update `create_1v1_match()` for debug challenges
- [ ] Update matchmaking to separate debug from DSA
- [ ] Add time limits (300s solo, 150s 1v1)
- [ ] Test match creation

**Files to modify:**
- `backend/app/services/match_service.py`

**Estimated time:** 2 hours

---

### Task 3.3: Update Match API Endpoints
- [ ] Add `/matches/debug/practice` endpoint
- [ ] Add `/matches/debug/competitive` endpoint
- [ ] Update matchmaking endpoint with challenge_type
- [ ] Add challenge_type filter to match history
- [ ] Test API endpoints

**Files to modify:**
- `backend/app/api/match.py`

**Estimated time:** 1.5 hours

---

## Phase 4: Backend - Rating & Leaderboard

### Task 4.1: Update Rating Service
- [ ] Add `challenge_type` parameter to rating methods
- [ ] Separate debug rating calculations
- [ ] Update `update_ratings()` to handle debug matches
- [ ] Ensure rating floor of 100 for debug
- [ ] Test rating updates

**Files to modify:**
- `backend/app/services/rating_service.py`

**Estimated time:** 1.5 hours

---

### Task 4.2: Update Leaderboard API
- [ ] Add `challenge_type` filter to leaderboard
- [ ] Create separate debug leaderboard endpoint
- [ ] Update leaderboard queries
- [ ] Add debug statistics
- [ ] Test leaderboard filtering

**Files to modify:**
- `backend/app/api/leaderboard.py`

**Estimated time:** 1 hour

---

## Phase 5: Frontend - UI Components

### Task 5.1: Create Debug Arena Page
- [ ] Create `DebugArena.tsx` page component
- [ ] Copy structure from `Arena.tsx`
- [ ] Update styling for debug theme
- [ ] Add mode selection (Solo/1v1)
- [ ] Add challenge type indicator
- [ ] Test page rendering

**Files to create:**
- `frontend/src/pages/DebugArena.tsx`

**Estimated time:** 2 hours

---

### Task 5.2: Update Dashboard for Debug Arena
- [ ] Add "Debug Arena" card/button
- [ ] Add debug arena statistics
- [ ] Add navigation to debug arena
- [ ] Update dashboard layout
- [ ] Test navigation

**Files to modify:**
- `frontend/src/pages/Dashboard.tsx`

**Estimated time:** 1 hour

---

### Task 5.3: Update Header Navigation
- [ ] Add "Debug Arena" link to header
- [ ] Update active state handling
- [ ] Test navigation
- [ ] Ensure responsive design

**Files to modify:**
- `frontend/src/components/Header.tsx`

**Estimated time:** 30 minutes

---

## Phase 6: Frontend - Services

### Task 6.1: Create Debug Challenge Service
- [ ] Create `debugChallengeService.ts`
- [ ] Add `generateDebugChallenge()` method
- [ ] Add `getDebugChallenge()` method
- [ ] Add error handling
- [ ] Test service methods

**Files to create:**
- `frontend/src/services/debugChallengeService.ts`

**Estimated time:** 1 hour

---

### Task 6.2: Update Matchmaking Service
- [ ] Add `challenge_type` parameter to matchmaking
- [ ] Create `startDebugSoloMatch()` method
- [ ] Create `startDebug1v1Match()` method
- [ ] Update polling logic for debug matches
- [ ] Test service methods

**Files to modify:**
- `frontend/src/services/matchmakingService.ts`

**Estimated time:** 1 hour

---

### Task 6.3: Update Submission Service
- [ ] Ensure submission service works with debug challenges
- [ ] Add challenge_type to submission metadata
- [ ] Test submission flow
- [ ] Verify judging works correctly

**Files to modify:**
- `frontend/src/services/submissionService.ts`

**Estimated time:** 30 minutes

---

## Phase 7: Frontend - Leaderboard & Profile

### Task 7.1: Update Leaderboard Page
- [ ] Add tab/toggle for Debug Arena leaderboard
- [ ] Create separate debug leaderboard view
- [ ] Update API calls with challenge_type filter
- [ ] Add debug statistics display
- [ ] Test leaderboard switching

**Files to modify:**
- `frontend/src/pages/Leaderboard.tsx`

**Estimated time:** 1.5 hours

---

### Task 7.2: Update Profile Page
- [ ] Add debug arena statistics section
- [ ] Display debug rating separately
- [ ] Show debug match history
- [ ] Add debug arena achievements
- [ ] Test profile updates

**Files to modify:**
- `frontend/src/pages/Profile.tsx`

**Estimated time:** 1.5 hours

---

### Task 7.3: Update Match History Component
- [ ] Add challenge_type filter
- [ ] Display debug matches separately
- [ ] Add visual indicator for debug matches
- [ ] Update recode functionality for debug
- [ ] Test match history filtering

**Files to modify:**
- `frontend/src/components/MatchHistory.tsx`

**Estimated time:** 1 hour

---

## Phase 8: Configuration & Settings

### Task 8.1: Update Config
- [ ] Add DEBUG_SOLO_TIME_LIMIT = 300
- [ ] Add DEBUG_1V1_TIME_LIMIT = 150
- [ ] Add DEBUG_INITIAL_RATING = 300
- [ ] Add challenge type constants
- [ ] Test configuration loading

**Files to modify:**
- `backend/app/config.py`

**Estimated time:** 15 minutes

---

### Task 8.2: Update Schemas
- [ ] Add challenge_type to match schemas
- [ ] Add broken_code to challenge schemas
- [ ] Add bug_count and bug_types fields
- [ ] Update validation rules
- [ ] Test schema validation

**Files to modify:**
- `backend/app/schemas/match_schema.py`

**Estimated time:** 30 minutes

---

## Phase 9: Testing & Validation

### Task 9.1: Backend Testing
- [ ] Test debug challenge generation
- [ ] Test match creation for debug arena
- [ ] Test rating updates for debug matches
- [ ] Test leaderboard filtering
- [ ] Test API endpoints
- [ ] Test error handling

**Estimated time:** 2 hours

---

### Task 9.2: Frontend Testing
- [ ] Test debug arena page rendering
- [ ] Test mode selection
- [ ] Test challenge display
- [ ] Test submission flow
- [ ] Test leaderboard switching
- [ ] Test profile statistics
- [ ] Test navigation

**Estimated time:** 2 hours

---

### Task 9.3: Integration Testing
- [ ] Test end-to-end solo match flow
- [ ] Test end-to-end 1v1 match flow
- [ ] Test WebSocket synchronization
- [ ] Test rating calculations
- [ ] Test match history
- [ ] Test recode functionality

**Estimated time:** 2 hours

---

## Phase 10: Documentation & Polish

### Task 10.1: Update Documentation
- [ ] Update README with debug arena info
- [ ] Document API endpoints
- [ ] Add debug challenge examples
- [ ] Update deployment guide
- [ ] Create user guide

**Estimated time:** 1 hour

---

### Task 10.2: UI Polish
- [ ] Add loading states
- [ ] Add error messages
- [ ] Add success notifications
- [ ] Improve animations
- [ ] Test responsive design
- [ ] Add tooltips and help text

**Estimated time:** 1.5 hours

---

## Summary

**Total Tasks:** 32
**Estimated Total Time:** 38-40 hours

### Priority Order:
1. **Phase 1:** Database & Models (2 hours)
2. **Phase 2:** Challenge Generation (7 hours)
3. **Phase 3:** Backend APIs (4.5 hours)
4. **Phase 4:** Rating & Leaderboard (2.5 hours)
5. **Phase 5:** Frontend UI (3.5 hours)
6. **Phase 6:** Frontend Services (2.5 hours)
7. **Phase 7:** Leaderboard & Profile (4 hours)
8. **Phase 8:** Configuration (45 minutes)
9. **Phase 9:** Testing (6 hours)
10. **Phase 10:** Documentation & Polish (2.5 hours)

### Quick Start Path (MVP):
For fastest implementation, focus on:
1. Task 1.1, 1.2 (Database)
2. Task 2.1, 2.2, 2.3 (Challenge Generation)
3. Task 3.1, 3.2, 3.3 (Backend APIs)
4. Task 5.1, 5.2 (Frontend Pages)
5. Task 6.1, 6.2 (Frontend Services)
6. Task 9.3 (Integration Testing)

This gives you a working debug arena in ~20 hours.
