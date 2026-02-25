# Code Road API - Quick Reference Guide

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register New Player
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "coder_pro",
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "player": {
    "id": "player_123",
    "username": "coder_pro",
    "email": "user@example.com",
    "current_rating": 1200,
    "rating_confidence": 100.0,
    "matches_played": 0,
    "wins": 0,
    "losses": 0,
    "badges_earned": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "last_match_at": null
  }
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):** Same as register

### Get Current Player
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "player_123",
  "username": "coder_pro",
  "email": "user@example.com",
  "current_rating": 1200,
  "rating_confidence": 100.0,
  "matches_played": 0,
  "wins": 0,
  "losses": 0,
  "badges_earned": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "last_match_at": null
}
```

---

## Match Endpoints

### Join Matchmaking Queue
```http
POST /api/v1/matches/queue/join
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "preferred_format": "1v1"
}
```

**Response (200 OK):**
```json
{
  "player_id": "player_123",
  "in_queue": true,
  "queue_position": 1,
  "wait_time_seconds": 30,
  "estimated_opponent_rating": 1250
}
```

### Leave Matchmaking Queue
```http
POST /api/v1/matches/queue/leave
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "left_queue",
  "message": "Successfully left matchmaking queue"
}
```

### Get Match Details
```http
GET /api/v1/matches/{match_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "match_id": "match_123",
  "status": "active",
  "format": "1v1",
  "player1": {
    "player_id": "player_123",
    "username": "coder_pro",
    "current_rating": 1200,
    "submissions_count": 2,
    "is_done": false
  },
  "player2": {
    "player_id": "player_456",
    "username": "code_ninja",
    "current_rating": 1250,
    "submissions_count": 1,
    "is_done": false
  },
  "challenge_id": "challenge_789",
  "challenge_title": "Two Sum",
  "challenge_description": "Find two numbers that add up to target",
  "difficulty_level": "easy",
  "time_limit_seconds": 120,
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:31:00Z",
  "concluded_at": null,
  "winner_id": null,
  "player1_score": null,
  "player2_score": null
}
```

### Get Player Match History
```http
GET /api/v1/matches/player/history?limit=50
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "matches": [
    {
      "match_id": "match_123",
      "status": "concluded",
      "format": "1v1",
      "player1": {...},
      "player2": {...},
      "challenge_id": "challenge_789",
      "challenge_title": "Two Sum",
      "difficulty_level": "easy",
      "time_limit_seconds": 120,
      "created_at": "2024-01-15T10:30:00Z",
      "started_at": "2024-01-15T10:31:00Z",
      "concluded_at": "2024-01-15T10:33:00Z",
      "winner_id": "player_123",
      "player1_score": 95.5,
      "player2_score": 75.0
    }
  ],
  "total_count": 1
}
```

### Signal Player Done
```http
POST /api/v1/matches/{match_id}/done
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": "done_recorded",
  "match_status": "active",
  "message": "Your done status has been recorded"
}
```

---

## Submission Endpoints

### Submit Code
```http
POST /api/v1/submissions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "match_id": "match_123",
  "code": "def solution(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
  "language": "python"
}
```

**Response (201 Created):**
```json
{
  "submission_id": "sub_123",
  "match_id": "match_123",
  "player_id": "player_123",
  "code": "def solution(nums, target):\n    ...",
  "language": "python",
  "status": "pending",
  "test_cases_passed": 0,
  "total_test_cases": 0,
  "execution_time_ms": null,
  "memory_used_mb": null,
  "ai_quality_score": null,
  "complexity_score": null,
  "created_at": "2024-01-15T10:32:00Z",
  "completed_at": null
}
```

### Get Submission Details
```http
GET /api/v1/submissions/{submission_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "submission_id": "sub_123",
  "match_id": "match_123",
  "player_id": "player_123",
  "code": "def solution(nums, target):\n    ...",
  "language": "python",
  "status": "completed",
  "test_cases_passed": 8,
  "total_test_cases": 10,
  "execution_time_ms": 45.2,
  "memory_used_mb": 12.5,
  "ai_quality_score": 85.0,
  "complexity_score": 90.0,
  "created_at": "2024-01-15T10:32:00Z",
  "completed_at": "2024-01-15T10:32:05Z",
  "test_case_results": [
    {
      "test_case_id": "tc_1",
      "passed": true,
      "expected_output": "[0, 1]",
      "actual_output": "[0, 1]",
      "error_message": null
    }
  ],
  "error_details": null
}
```

### Get Match Submissions
```http
GET /api/v1/submissions/match/{match_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "submissions": [
    {
      "submission_id": "sub_123",
      "match_id": "match_123",
      "player_id": "player_123",
      "code": "...",
      "language": "python",
      "status": "completed",
      "test_cases_passed": 8,
      "total_test_cases": 10,
      "execution_time_ms": 45.2,
      "memory_used_mb": 12.5,
      "ai_quality_score": 85.0,
      "complexity_score": 90.0,
      "created_at": "2024-01-15T10:32:00Z",
      "completed_at": "2024-01-15T10:32:05Z"
    }
  ],
  "total_count": 1
}
```

---

## Leaderboard Endpoints

### Get Global Leaderboard
```http
GET /api/v1/leaderboard/global?limit=100&offset=0
```

**Response (200 OK):**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "player_id": "player_456",
      "username": "code_ninja",
      "current_rating": 1450,
      "matches_played": 25,
      "wins": 20,
      "win_rate": 0.8
    },
    {
      "rank": 2,
      "player_id": "player_123",
      "username": "coder_pro",
      "current_rating": 1250,
      "matches_played": 10,
      "wins": 7,
      "win_rate": 0.7
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

### Get Player Statistics
```http
GET /api/v1/leaderboard/player/{player_id}
```

**Response (200 OK):**
```json
{
  "player_id": "player_123",
  "username": "coder_pro",
  "current_rating": 1250,
  "rating_confidence": 95.5,
  "matches_played": 10,
  "wins": 7,
  "losses": 3,
  "win_rate": 0.7,
  "average_match_duration_seconds": 120,
  "badges_earned": 2,
  "tournaments_participated": 1,
  "best_rating": 1300,
  "worst_rating": 1100,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Current Player Statistics
```http
GET /api/v1/leaderboard/me/stats
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "rank": 2,
  "player_id": "player_123",
  "username": "coder_pro",
  "current_rating": 1250,
  "rating_confidence": 95.5,
  "matches_played": 10,
  "wins": 7,
  "losses": 3,
  "win_rate": 0.7,
  "badges_earned": 2,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Health & Info Endpoints

### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "code-road-backend",
  "version": "1.0.0"
}
```

### API Information
```http
GET /
```

**Response (200 OK):**
```json
{
  "message": "Welcome to Code Road API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "auth": "/api/v1/auth",
    "matches": "/api/v1/matches",
    "submissions": "/api/v1/submissions",
    "leaderboard": "/api/v1/leaderboard",
    "websocket": "/ws"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "You don't have access to this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

---

## Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

---

## Rate Limits
Currently no rate limiting implemented. Will be added in next phase.

---

## WebSocket (Coming Soon)
```
ws://localhost:8000/ws/{match_id}
```

Real-time updates for:
- Match status changes
- Submission notifications
- Player done signals
- Match conclusions

---

## Testing

### Run Comprehensive Tests
```bash
python test_api_complete.py
```

### Manual Testing with cURL
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'

# Get current user (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"
```

---

## Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
