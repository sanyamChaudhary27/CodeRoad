# Code Road Backend - API Guide for Frontend Developers

## Overview

This guide provides complete API documentation for the Code Road backend. All endpoints are RESTful and return JSON responses.

**Base URL**: `http://localhost:8000` (development) or your production URL

## Table of Contents

1. [Authentication](#authentication)
2. [Leaderboard](#leaderboard)
3. [Matchmaking](#matchmaking)
4. [Challenges](#challenges)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Authentication

### Register Player

Create a new player account.

```
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "string (3-50 chars, alphanumeric + underscore)",
  "email": "string (valid email)",
  "password": "string (min 8 chars, uppercase, lowercase, number, special char)"
}
```

**Response (201 Created)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "player": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "current_rating": 1200,
    "created_at": "2026-03-01T10:00:00Z"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input, weak password, or user already exists
- `422 Unprocessable Entity`: Validation error

---

### Login

Authenticate and get access token.

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "player": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "current_rating": 1200
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `404 Not Found`: User not found

---

### Get Current Player

Get authenticated player's profile.

```
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "current_rating": 1200,
  "matches_played": 10,
  "wins": 6,
  "losses": 4,
  "created_at": "2026-03-01T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

---

## Leaderboard

### Get Global Leaderboard

Retrieve top players ranked by ELO rating.

```
GET /api/v1/leaderboard/global?limit=100&offset=0
```

**Query Parameters**:
- `limit`: Number of players (default: 100, max: 1000)
- `offset`: Pagination offset (default: 0)

**Response (200 OK)**:
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "player_id": "uuid",
      "username": "string",
      "current_rating": 1850,
      "wins": 45,
      "losses": 5,
      "win_rate": 0.90,
      "matches_played": 50,
      "rating_confidence": 95.5,
      "badges": ["badge1", "badge2"]
    },
    ...
  ],
  "total_players": 1000,
  "limit": 100,
  "offset": 0
}
```

---

### Get Player Statistics

Get detailed stats for a specific player.

```
GET /api/v1/leaderboard/player/{player_id}
```

**Response (200 OK)**:
```json
{
  "player_id": "uuid",
  "username": "string",
  "current_rating": 1200,
  "rank": 150,
  "matches_played": 25,
  "wins": 15,
  "losses": 10,
  "win_rate": 0.60,
  "rating_confidence": 85.0,
  "highest_rating": 1350,
  "badges": ["First Win", "10 Wins"],
  "match_history": [
    {
      "match_id": "uuid",
      "opponent_id": "uuid",
      "opponent_name": "string",
      "result": "win",
      "player_score": 85,
      "opponent_score": 60,
      "rating_change": 15,
      "timestamp": "2026-03-01T10:00:00Z"
    }
  ]
}
```

**Error Responses**:
- `404 Not Found`: Player not found

---

### Get My Statistics

Get authenticated player's detailed statistics.

```
GET /api/v1/leaderboard/me/stats
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "player_id": "uuid",
  "username": "string",
  "current_rating": 1200,
  "rank": 150,
  "matches_played": 25,
  "wins": 15,
  "losses": 10,
  "win_rate": 0.60,
  "rating_confidence": 85.0,
  "highest_rating": 1350,
  "badges": ["First Win", "10 Wins"],
  "recent_matches": [...]
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

---

## Matchmaking

### Join Queue

Enter matchmaking queue to find an opponent.

```
POST /api/v1/matches/queue/join
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "preferred_format": "1v1",
  "min_rating": 1000,
  "max_rating": 1400
}
```

**Request Parameters**:
- `preferred_format`: "1v1" or "battle_royale" (default: "1v1")
- `min_rating`: Minimum opponent rating (optional)
- `max_rating`: Maximum opponent rating (optional)

**Response (200 OK)**:
```json
{
  "status": "joined_queue",
  "queue_id": "uuid",
  "player_id": "uuid",
  "player_rating": 1200,
  "joined_at": "2026-03-01T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `400 Bad Request`: Already in queue

---

### Leave Queue

Exit matchmaking queue.

```
POST /api/v1/matches/queue/leave
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "status": "left_queue",
  "player_id": "uuid",
  "queue_id": "uuid"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Not in queue

---

### Get Queue Status

Check current queue status.

```
GET /api/v1/matches/queue/status
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "in_queue": true,
  "queue_id": "uuid",
  "joined_at": "2026-03-01T10:00:00Z",
  "wait_time_seconds": 45,
  "estimated_wait_seconds": 30
}
```

---

## Challenges

### Generate Challenge

Generate a new AI-powered coding challenge.

```
POST /api/v1/challenges/generate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "difficulty": "intermediate",
  "domain": "arrays"
}
```

**Request Parameters**:
- `difficulty`: "beginner", "intermediate", or "advanced" (optional, auto-detected from rating)
- `domain`: "arrays", "strings", "linked_lists", "trees", "graphs", "dynamic_programming", "sorting", "searching" (optional)

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "title": "Two Sum Problem",
  "description": "Given an array of integers and a target sum, find two numbers that add up to the target...",
  "difficulty": "intermediate",
  "domain": "arrays",
  "constraints": [
    "2 ≤ n ≤ 1000",
    "-10^9 ≤ each element ≤ 10^9",
    "Time limit: 90 seconds",
    "Memory limit: 256MB"
  ],
  "input_format": "First line: integer n (array size)\nSecond line: n space-separated integers\nThird line: target sum",
  "output_format": "Two space-separated integers: indices of the two numbers",
  "example_input": "4\n2 7 11 15\n9",
  "example_output": "0 1",
  "time_limit_seconds": 90,
  "test_cases": [
    {
      "id": "tc_001",
      "input": "4\n2 7 11 15\n9",
      "expected_output": "0 1",
      "category": "basic",
      "description": "Standard case",
      "is_hidden": false
    },
    {
      "id": "tc_002",
      "input": "2\n3 3\n6",
      "expected_output": "0 1",
      "category": "edge_case",
      "description": "Duplicate elements",
      "is_hidden": true
    }
  ],
  "coverage_metrics": {
    "total_test_cases": 8,
    "categories": {
      "basic": 2,
      "edge_case": 3,
      "boundary": 2,
      "mixed": 1
    },
    "coverage_score": 0.95
  },
  "difficulty_score": 2.5,
  "estimated_success_rate": 0.55,
  "generated_at": "2026-03-01T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Challenge generation failed (fallback test case provided)

---

### Get Challenge

Retrieve a previously generated challenge.

```
GET /api/v1/challenges/{challenge_id}
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "title": "...",
  "description": "...",
  ...
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Challenge not found

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400,
  "error_code": "INVALID_INPUT"
}
```

### Common HTTP Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input, check request body |
| 401 | Unauthorized | Missing or invalid token, login required |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error in request |
| 429 | Too Many Requests | Rate limit exceeded, wait before retrying |
| 500 | Internal Server Error | Server error, try again later |

---

## Examples

### Complete Authentication Flow

```javascript
// 1. Register
const registerResponse = await fetch('http://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'player123',
    email: 'player@example.com',
    password: 'SecurePass123!'
  })
});

const { access_token } = await registerResponse.json();

// 2. Get current player
const meResponse = await fetch('http://localhost:8000/api/v1/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

const player = await meResponse.json();
console.log(`Welcome, ${player.username}! Rating: ${player.current_rating}`);
```

### Generate Challenge and Submit

```javascript
// 1. Generate challenge
const challengeResponse = await fetch('http://localhost:8000/api/v1/challenges/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    difficulty: 'intermediate',
    domain: 'arrays'
  })
});

const challenge = await challengeResponse.json();
console.log(`Challenge: ${challenge.title}`);
console.log(`Test cases: ${challenge.test_cases.length}`);

// 2. Display visible test cases only
const visibleTests = challenge.test_cases.filter(tc => !tc.is_hidden);
visibleTests.forEach(tc => {
  console.log(`Input: ${tc.input}`);
  console.log(`Expected: ${tc.expected_output}`);
});
```

### Matchmaking Flow

```javascript
// 1. Join queue
const joinResponse = await fetch('http://localhost:8000/api/v1/matches/queue/join', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    preferred_format: '1v1'
  })
});

const queueStatus = await joinResponse.json();
console.log('Joined queue, waiting for opponent...');

// 2. Poll for match status
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch('http://localhost:8000/api/v1/matches/queue/status', {
    headers: { 'Authorization': `Bearer ${access_token}` }
  });
  
  const status = await statusResponse.json();
  if (status.match_found) {
    clearInterval(pollInterval);
    console.log('Match found!');
  }
}, 1000);

// 3. Leave queue if needed
const leaveResponse = await fetch('http://localhost:8000/api/v1/matches/queue/leave', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### Get Leaderboard

```javascript
// Get top 10 players
const leaderboardResponse = await fetch(
  'http://localhost:8000/api/v1/leaderboard/global?limit=10&offset=0'
);

const { leaderboard } = await leaderboardResponse.json();

leaderboard.forEach((player, index) => {
  console.log(`${player.rank}. ${player.username} - Rating: ${player.current_rating}`);
  console.log(`   Wins: ${player.wins}, Losses: ${player.losses}, Win Rate: ${(player.win_rate * 100).toFixed(1)}%`);
});
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Limit**: 100 requests per 60 seconds per IP
- **Headers**: 
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

When rate limited, you'll receive a `429 Too Many Requests` response.

---

## WebSocket (Real-Time Updates)

For real-time match updates, connect to WebSocket:

```
WS /ws/match/{match_id}?token={access_token}
```

**Messages**:
- `challenge_assigned`: Challenge sent to players
- `opponent_submitted`: Opponent submitted code
- `match_concluded`: Match ended with results
- `rating_updated`: Rating change applied

---

## Best Practices

1. **Always include Authorization header** for authenticated endpoints
2. **Handle errors gracefully** - check status codes and error messages
3. **Implement exponential backoff** for retries
4. **Cache leaderboard data** - it doesn't change frequently
5. **Use WebSocket** for real-time updates instead of polling
6. **Validate input** before sending to API
7. **Store access token securely** (not in localStorage for sensitive apps)
8. **Refresh token** when it expires (implement token refresh flow)

---

## Support

For issues or questions:
1. Check this guide
2. Review error messages
3. Check backend logs
4. Contact backend team

---

**Last Updated**: March 1, 2026  
**API Version**: 1.0  
**Status**: Production Ready
