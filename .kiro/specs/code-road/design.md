# Code Road Design Document

## Overview

Code Road is a real-time competitive coding platform that combines AI-generated micro challenges with multiplayer battle mechanics and skill-based ranking. The system architecture is designed to handle concurrent matches, provide fair judging through isolated code execution, and maintain responsive real-time interactions. The platform uses an ELO rating system to match players of similar skill levels and adapts challenge difficulty based on player performance. All components are designed to scale horizontally and maintain low-latency responses for competitive gameplay.

## High-Level Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  (Web/Mobile UI - Match Interface, Leaderboards, Profiles)      │
└────────────────────────┬────────────────────────────────────────┘
                         │ WebSocket / REST API
┌────────────────────────▼────────────────────────────────────────┐
│                    API Gateway Layer                             │
│  (Request routing, authentication, rate limiting)               │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────────┐
│  Match       │  │  Challenge  │  │  Rating &      │
│  Service     │  │  Service    │  │  Leaderboard   │
│              │  │             │  │  Service       │
└───────┬──────┘  └──────┬──────┘  └─────┬──────────┘
        │                │               │
        └────────────────┼───────────────┘
                         │
        ┌────────────────┼────────────────┬──────────────┬──────────────────┐
        │                │                │              │                  │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────────┐  ┌─▼──────────────┐  ┌─▼──────────────────┐
│  Code        │  │  Judge      │  │  Data          │  │  AI Code       │  │  Integrity         │
│  Sandbox     │  │  Service    │  │  Persistence   │  │  Review        │  │  Verification      │
│  (Isolated)  │  │             │  │  Layer         │  │  Service       │  │  Service (AI)      │
└──────────────┘  └─────────────┘  └────────────────┘  └────────────────┘  └────────────────────┘
```

### Architectural Principles

- **Microservices**: Independent services for matches, challenges, judging, and ratings
- **Real-Time Communication**: WebSocket connections for live match updates
- **Isolation**: Code execution in sandboxed environments to prevent security issues
- **Scalability**: Stateless services that can be horizontally scaled
- **Eventual Consistency**: Rating updates and leaderboard changes propagate asynchronously
- **Fault Tolerance**: Graceful degradation when services fail

## Major Components

### 1. Match Service

**Responsibility**: Orchestrate real-time competitive matches between players

**Key Functions**:
- Matchmaking: Find opponents within skill range (±200 ELO)
- Match Lifecycle: Create, manage, and conclude matches
- Real-Time Updates: Broadcast match state to connected players
- Time Management: Enforce submission deadlines
- Submission Tracking: Accept multiple submissions per player until match ends
- Match Conclusion: End match when time expires OR both players signal completion

**Data Structures**:
```
Match {
  id: UUID
  player1_id: UUID
  player2_id: UUID
  challenge_id: UUID
  status: "waiting" | "active" | "concluded"
  start_time: Timestamp
  end_time: Timestamp
  time_limit_seconds: Integer (30-120)
  player1_submissions: CodeSubmission[]  // All submissions from player 1
  player2_submissions: CodeSubmission[]  // All submissions from player 2
  player1_done: Boolean  // Player 1 signals completion
  player2_done: Boolean  // Player 2 signals completion
  player1_final_submission: CodeSubmission  // Last submission before match ends
  player2_final_submission: CodeSubmission  // Last submission before match ends
  player1_score: Integer
  player2_score: Integer
  player1_ai_quality_score: Float (0-100)
  player2_ai_quality_score: Float (0-100)
  player1_complexity_score: Float (0-100)
  player2_complexity_score: Float (0-100)
  winner_id: UUID | null
  created_at: Timestamp
}

CodeSubmission {
  id: UUID
  player_id: UUID
  code: String
  language: String
  submitted_at: Timestamp
  execution_result: ExecutionResult
  is_final: Boolean  // True if this is the final submission used for scoring
}

ExecutionResult {
  status: "success" | "timeout" | "error"
  test_cases_passed: Integer
  test_cases_total: Integer
  error_message: String | null
  execution_time_ms: Integer
}
```

**Match Lifecycle**:
1. Match created when two players matched
2. Challenge assigned and sent to both players
3. Timer starts (30–120 seconds)
4. Players submit code multiple times
5. Each submission is evaluated immediately
6. Match ends when: (a) timer expires, OR (b) both players click "Done"
7. Final submission from each player is used for scoring
8. Evaluation begins: test cases → AI quality → complexity analysis
9. Winner determined and ratings updated

**Interactions**:
- Receives challenge from Challenge Service
- Sends submissions to Judge Service
- Receives evaluation results from Judge Service
- Updates ratings via Rating Service
- Broadcasts updates via WebSocket

### 2. Challenge Service

**Responsibility**: Generate and manage AI-created coding challenges

**Key Functions**:
- AI Challenge Generation: Use LLM to generate problem statements from templates
- Problem Statement Creation: AI generates unique, contextually relevant problem descriptions
- Test Case Generation: AI creates valid test cases with expected outputs
- Difficulty Assignment: Assign difficulty levels (beginner, intermediate, advanced)
- Challenge Validation: Ensure test cases are valid and executable
- Domain Variety: Distribute challenges across multiple domains

**Challenge Template Structure**:
```
ChallengeTemplate {
  id: UUID
  name: String
  domain: String (e.g., "algorithms", "data_structures", "strings")
  difficulty_level: "beginner" | "intermediate" | "advanced"
  description: String  // AI-generated problem statement
  input_specification: String
  output_specification: String
  example_input: String
  example_output: String
  test_cases: TestCase[]
  time_limit_seconds: Integer (30-120)
  created_at: Timestamp
  generated_by_ai: Boolean
}

TestCase {
  id: UUID
  input: String
  expected_output: String
  is_hidden: Boolean
}
```

**AI Generation Algorithm**:
1. Select random challenge template from database
2. Apply parameter variations (input size, complexity)
3. Use LLM to generate unique problem statement based on template
4. Use LLM to generate diverse test cases with expected outputs
5. Validate all test cases are executable and deterministic
6. Assign difficulty based on template and parameters
7. Store generated challenge for reuse and calibration

**Interactions**:
- Provides AI-generated challenges to Match Service
- Receives difficulty feedback from Rating Service
- Logs challenge usage for calibration and AI model improvement

### 3. Judge Service

**Responsibility**: Execute code and evaluate submissions using multi-metric scoring

**Key Functions**:
- Code Execution: Run submissions in isolated sandbox
- Test Case Evaluation: Compare output against all test cases
- AI Quality Assessment: Evaluate code for style, efficiency, and best practices
- Complexity Analysis: Analyze time and space complexity
- Scoring: Calculate final score based on three metrics in priority order
- Error Handling: Gracefully handle execution failures

**Scoring Algorithm** (Priority Order):
```
evaluate_submission(submission, challenge):
  1. Execute code in Sandbox
  2. Evaluate test cases:
     - test_case_score = (passing_tests / total_tests) * 100
  
  3. AI Quality Assessment:
     - Analyze code for: readability, efficiency, best practices
     - ai_quality_score = 0-100 (higher is better)
  
  4. Complexity Analysis:
     - Estimate time complexity (O(n), O(n²), etc.)
     - Estimate space complexity
     - complexity_score = 0-100 (higher is better for efficiency)
  
  5. Determine Winner:
     - Compare test_case_score first (highest wins)
     - If tied: Compare ai_quality_score
     - If tied: Compare complexity_score
     - If all tied: Earlier submission wins (by timestamp)
  
  return {
    test_case_score,
    ai_quality_score,
    complexity_score,
    final_score,
    winner_indicator
  }
```

**Interactions**:
- Receives submissions from Match Service
- Executes code in Sandbox Service
- Returns results to Match Service
- Logs execution metrics for performance monitoring

### 4. AI Code Review Service

**Responsibility**: Provide post-match AI-powered code analysis and feedback

**Key Functions**:
- Code Analysis: Analyze submitted code for quality and efficiency
- Feedback Generation: Generate actionable improvement suggestions
- Learning Support: Help players understand optimization opportunities
- Non-Competitive: Reviews do not affect match outcomes or ratings

**Review Metrics**:
```
CodeReview {
  submission_id: UUID
  player_id: UUID
  code: String
  language: String
  
  analysis: {
    correctness_feedback: String
    efficiency_feedback: String
    style_feedback: String
    best_practices: String[]
    optimization_suggestions: String[]
    time_complexity_explanation: String
    space_complexity_explanation: String
  }
  
  generated_at: Timestamp
}
```

**Review Generation Algorithm**:
1. Receive code submission request
2. Parse code and identify patterns
3. Compare against test cases (if available)
4. Analyze for common inefficiencies
5. Generate specific, actionable feedback
6. Return review to player

**Interactions**:
- Receives code review requests from Match Service
- Analyzes code submissions
- Returns feedback to players
- Does not affect match scoring or ratings

### 5. AI-Assisted Integrity Verification Service

**Responsibility**: Analyze final submissions for potential AI-assisted code generation and ensure fair competition in ranked matches without unjust penalization

**Key Functions**:
- Stylometric Analysis: Compare current submission against player's historical coding style
- LLM Probability Classification: Use transformer-based classifier to estimate likelihood of AI-generated code
- Behavioral Anomaly Detection: Identify sudden complexity improvements, unnatural optimality, and abnormal submission timing
- Cheating Probability Aggregation: Combine multiple signals into a single probability score (0–100%)
- Rating Confidence Adjustment: Adjust player rating confidence score based on integrity signals
- Audit Logging: Maintain review logs for transparency

**Data Structures**:
```
IntegrityAnalysis {
  id: UUID
  submission_id: UUID
  player_id: UUID
  stylometry_score: Float (0-100)
  llm_probability_score: Float (0-100)
  behavioral_anomaly_score: Float (0-100)
  overall_cheat_probability: Float (0-100)
  flagged: Boolean
  reviewed: Boolean
  created_at: Timestamp
}

PlayerIntegrityProfile {
  player_id: UUID
  rating_confidence: Float (0-100)
  suspicious_matches: Integer
  clean_matches: Integer
  last_flagged_at: Timestamp | null
}
```

**Detection Pipeline**:
```
analyze_submission(submission, player_profile):
  1. Extract code features:
     - Token frequency
     - Indentation style
     - Variable naming patterns
     - Comment density
     - Structural patterns
  
  2. Stylometric Comparison:
     - Compare against historical embedding profile
     - stylometry_score = deviation_score (0-100)
  
  3. Transformer Classification:
     - Run submission through trained AI-vs-human classifier
     - llm_probability_score = predicted_probability (0-100)
  
  4. Behavioral Analysis:
     - Compare solve time vs historical median
     - Compare complexity vs previous 10 matches
     - Detect unnatural improvement spikes
     - behavioral_anomaly_score computed
  
  5. Aggregate:
     overall_cheat_probability =
       weighted_average(
         stylometry_score,
         llm_probability_score,
         behavioral_anomaly_score
       )
  
  6. If probability > threshold (e.g., 85%):
     flag submission
     notify Rating Service
  
  return IntegrityAnalysis
```

**Integrity Threshold Policy**:
- Probability < 70%: No action
- Probability 70–85%: Soft flag (monitor only)
- Probability ≥ 85%: Rating freeze pending review
- No automatic bans occur solely from AI detection

**Interactions**:
- Receives final submissions from Judge Service
- Analyzes code against player history
- Returns integrity analysis to Rating Service
- Updates player integrity profile
- Maintains audit logs for transparency

### 6. Code Sandbox Service

**Responsibility**: Safely execute untrusted code in isolated environments

**Key Functions**:
- Process Isolation: Run each submission in separate process
- Resource Limits: Enforce CPU, memory, and time limits
- Security: Prevent access to file system and network
- Timeout Handling: Kill processes that exceed time limits

**Execution Environment**:
- Docker containers or similar isolation mechanism
- Language-specific runtimes (Python, JavaScript, Java, etc.)
- Read-only file system for test data
- Network access disabled
- CPU limit: 1 core per submission
- Memory limit: 256MB per submission
- Time limit: 5 seconds per test case

**Interactions**:
- Receives execution requests from Judge Service
- Returns execution results with output and status
- Logs resource usage for monitoring

### 7. Data Persistence Layer

**Responsibility**: Store and retrieve all system data

**Key Functions**:
- Player Data: Store user accounts, ratings, profiles
- Match Data: Persist match results and submissions
- Challenge Data: Store challenge templates and usage
- Leaderboard Data: Maintain ranking snapshots
- Integrity Data: Store integrity analysis and audit logs

**Database Schema Overview**:
```
Tables:
  - players (id, username, email, created_at)
  - player_ratings (player_id, current_rating, matches_played, wins, losses)
  - player_integrity_profiles (player_id, rating_confidence, suspicious_matches, clean_matches)
  - matches (id, player1_id, player2_id, challenge_id, status, result)
  - submissions (id, match_id, player_id, code, language, score, is_final)
  - integrity_analysis (id, submission_id, player_id, cheat_probability, flagged, reviewed)
  - challenges (id, name, domain, difficulty, description, test_cases)
  - leaderboard (player_id, rank, rating, wins, losses, updated_at)
  - badges (id, player_id, badge_type, awarded_at)
  - tournaments (id, name, format, status, bracket_data)
  - match_history (player_id, match_id, opponent_id, result, rating_change)
  - code_reviews (id, submission_id, player_id, feedback, generated_at)
  - integrity_audit_logs (id, player_id, action, details, timestamp)
```

**Interactions**:
- All services read/write through this layer
- Supports transactions for atomic operations
- Provides query optimization for leaderboard and history

### 8. Rating Service

**Responsibility**: Calculate and maintain player skill ratings with integrity-aware confidence scoring

**Key Functions**:
- Rating Initialization: Assign 1200 ELO to new players
- Rating Updates: Adjust ratings after each match
- Rating Confidence Management: Track and adjust rating confidence based on integrity signals
- Rating Decay: Apply decay to inactive players
- Leaderboard Maintenance: Update player rankings

**ELO Calculation Algorithm**:
```
calculate_rating_change(player_rating, opponent_rating, match_result):
  K = 32  // Rating volatility factor
  expected_score = 1 / (1 + 10^((opponent_rating - player_rating) / 400))
  
  if match_result == "win":
    actual_score = 1
  else if match_result == "loss":
    actual_score = 0
  else:
    actual_score = 0.5
  
  rating_change = K * (actual_score - expected_score)
  return round(rating_change)
```

**Rating Confidence System**:
```
update_rating_confidence(player_id, integrity_probability):
  current_confidence = get_player_confidence(player_id)
  
  if integrity_probability < 70%:
    // Clean match
    new_confidence = min(current_confidence + 1, 100)
  else if integrity_probability >= 70% and < 85%:
    // Soft flag
    new_confidence = current_confidence - 2
  else:
    // Hard flag
    new_confidence = current_confidence - 5
  
  return max(new_confidence, 0)
```

**Data Structures**:
```
PlayerRating {
  player_id: UUID
  current_rating: Integer (default: 1200)
  rating_confidence: Float (0-100, default: 100)
  rating_history: RatingChange[]
  matches_played: Integer
  wins: Integer
  losses: Integer
  last_match_date: Timestamp
  last_decay_date: Timestamp
}

RatingChange {
  match_id: UUID
  opponent_id: UUID
  old_rating: Integer
  new_rating: Integer
  change: Integer
  match_result: "win" | "loss" | "draw"
  integrity_status: "clean" | "flagged" | "frozen"
  timestamp: Timestamp
}
```

**Rating Freeze Logic**:
- If integrity probability ≥ 85%: Rating update temporarily frozen
- Freeze remains until integrity review completes
- Freeze is reversible if review clears the player
- No permanent penalties without multi-signal confirmation

**Interactions**:
- Receives match results from Match Service
- Receives integrity analysis from Integrity Verification Service
- Updates Leaderboard Service
- Provides ratings to Matchmaker for pairing
- Maintains audit trail of all rating changes

### 9. Leaderboard Service

**Responsibility**: Maintain and serve player rankings with integrity-aware weighting

**Key Functions**:
- Ranking Calculation: Sort players by ELO rating, weighted by confidence
- Leaderboard Updates: Reflect rating changes in real-time
- Player Statistics: Calculate win rates and metrics
- Historical Data: Maintain match history
- Integrity Visibility: Display rating confidence on profiles

**Data Structures**:
```
Leaderboard {
  id: UUID
  player_id: UUID
  rank: Integer
  rating: Integer
  rating_confidence: Float (0-100)
  wins: Integer
  losses: Integer
  win_rate: Float
  matches_played: Integer
  badges: Badge[]
  last_updated: Timestamp
}

PlayerStatistics {
  player_id: UUID
  total_matches: Integer
  total_wins: Integer
  total_losses: Integer
  win_rate: Float
  average_rating_change: Float
  highest_rating: Integer
  current_rating: Integer
  rating_confidence: Float
  badges_earned: Badge[]
  match_history: MatchRecord[]
  integrity_status: "clean" | "under_review" | "flagged"
}

MatchRecord {
  match_id: UUID
  opponent_id: UUID
  opponent_name: String
  result: "win" | "loss"
  player_score: Integer
  opponent_score: Integer
  rating_change: Integer
  integrity_status: "clean" | "flagged" | "frozen"
  challenge_domain: String
  timestamp: Timestamp
}
```

**Interactions**:
- Receives rating updates from Rating Service
- Serves leaderboard queries to clients
- Provides player statistics for profiles
- Displays rating confidence and integrity status

### 10. Badge Service

**Responsibility**: Award and manage player achievements

**Key Functions**:
- Badge Awarding: Grant badges for specific accomplishments
- Badge Tracking: Maintain player badge inventory
- Badge Display: Serve badge information to profiles

**Badge Types**:
```
Badge {
  id: UUID
  name: String
  description: String
  icon_url: String
  criteria: BadgeCriteria
  awarded_date: Timestamp
}

BadgeCriteria:
  - TournamentWinner: Win a tournament
  - RatingMilestone: Reach rating thresholds (1500, 1800, 2000, 2200)
  - PerfectMatch: Win with 100% test case pass rate
  - ConsecutiveWins: Win 5+ matches in a row
  - DomainMastery: Win 10+ matches in a specific domain
  - SpeedDemon: Win a match in under 30 seconds
  - FairPlayChampion: Maintain 95%+ rating confidence over 50 matches
```

**Interactions**:
- Receives match results from Match Service
- Receives tournament results from Tournament Service
- Updates player profiles with badge information

### 11. Tournament Service

**Responsibility**: Organize and manage tournament competitions with integrity verification

**Key Functions**:
- Bracket Creation: Generate knockout or battle royale brackets
- Match Scheduling: Automatically schedule matches between qualified players
- Bracket Progression: Advance winners and eliminate losers
- Tournament Conclusion: Determine final standings
- Integrity Monitoring: Track integrity status during tournament

**Tournament Data Structures**:
```
Tournament {
  id: UUID
  name: String
  format: "knockout" | "battle_royale"
  status: "scheduled" | "active" | "concluded"
  start_time: Timestamp
  end_time: Timestamp
  max_players: Integer
  registered_players: UUID[]
  bracket: Bracket
  final_standings: PlayerStanding[]
  integrity_flags: IntegrityFlag[]
}

Bracket {
  id: UUID
  rounds: Round[]
  current_round: Integer
}

Round {
  round_number: Integer
  matches: UUID[]  // Match IDs
  status: "pending" | "active" | "concluded"
}

PlayerStanding {
  player_id: UUID
  final_rank: Integer
  matches_won: Integer
  matches_lost: Integer
  final_rating_change: Integer
  integrity_status: "clean" | "flagged"
}
```

**Bracket Progression Logic**:
- Knockout: Losers eliminated, winners advance
- Battle Royale: Top N performers advance each round
- Automatic match scheduling between qualified players
- Rating adjustments applied after each match
- Integrity flags tracked throughout tournament

**Interactions**:
- Creates matches via Match Service
- Receives match results to determine advancement
- Receives integrity analysis from Integrity Verification Service
- Awards badges via Badge Service
- Updates ratings via Rating Service

## System & User Flows

### Flow 1: Player Registration and Initialization

```
1. Player visits platform
2. Player creates account (username, email, password)
3. System creates player record with initial ELO rating of 1200
4. System initializes empty match history and badge list
5. Player is added to leaderboard at rank based on initial rating
6. Player can now enter matchmaking queue
```

### Flow 2: Matchmaking and Match Execution

```
1. Player clicks "Find Match"
2. Matchmaker searches for opponent within ±200 ELO range
3. When opponent found:
   a. Match record created
   b. Challenge selected based on average player skill
   c. Challenge sent to both players
   d. 120-second timer starts
4. Players write and submit code (unlimited submissions allowed):
   a. Each submission is timestamped
   b. Submission is sent to Judge Service
   c. Judge evaluates against test cases
   d. Results returned to player in real-time
   e. Player can submit again or click "Done"
5. Match ends when: (a) timer expires, OR (b) both players click "Done"
6. Final submission from each player is selected for scoring
7. Evaluation begins:
   a. Test case correctness (primary metric)
   b. AI quality assessment (secondary metric)
   c. Complexity analysis (tertiary metric)
8. Integrity Verification begins:
   a. Final submissions sent to Integrity Verification Service
   b. Stylometric analysis performed
   c. LLM probability classification computed
   d. Behavioral anomaly detection executed
   e. Overall cheat probability aggregated
   f. If probability < 70%: Proceed to rating update
   g. If probability 70–85%: Soft flag, monitor, proceed with rating
   h. If probability ≥ 85%: Hard flag, freeze rating pending review
9. Winner determined based on scoring priority
10. Ratings updated via Rating Service (or frozen if flagged)
11. Rating confidence adjusted based on integrity analysis
12. Match result displayed to both players
13. Match added to player histories
14. Leaderboard updated
15. Players can request AI code review (optional, non-competitive)
```

### Flow 6: Integrity Verification During Ranked Match

```
1. Match concludes normally
2. Final submissions selected
3. Judge Service evaluates scoring metrics
4. Integrity Verification Service analyzes final submissions:
   a. Extract code stylometric features
   b. Compare against player's historical code profile
   c. Run through transformer-based AI classifier
   d. Analyze behavioral anomalies (complexity jumps, timing patterns)
   e. Aggregate signals into overall cheat probability
5. If cheat probability < 70%:
   a. Rating update proceeds normally
   b. Player integrity profile updated (clean match)
   c. Rating confidence increased by 1 point
6. If cheat probability 70–85%:
   a. Match marked as "Soft Flag"
   b. Rating update proceeds with caution
   c. Player integrity profile updated
   d. Rating confidence decreased by 2 points
   e. Match logged for monitoring
7. If cheat probability ≥ 85%:
   a. Match marked as "Under Integrity Review"
   b. Rating update temporarily frozen
   c. Player notified of review status
   d. Player integrity profile updated
   e. Rating confidence decreased by 5 points
   f. Audit log created for manual review
8. Rating confirmation finalized after integrity logic
9. Player can appeal integrity decision through support
```

```
1. Player registers for tournament
2. Tournament starts at scheduled time
3. Initial bracket generated with all registered players
4. Round 1 matches scheduled automatically
5. Players compete in matches
6. Winners advance, losers eliminated (knockout) or ranked (battle royale)
7. Subsequent rounds scheduled based on advancement
8. Final match determines tournament winner
9. Winner awarded tournament badge
10. All participants receive rating adjustments
11. Final standings recorded
```

### Flow 4: Leaderboard and Profile Viewing

```
1. Player views leaderboard
2. System retrieves top 100 players sorted by ELO rating
3. Player's current rank and position displayed
4. Player clicks on profile
5. System displays:
   - Current ELO rating
   - Win/loss record
   - Win rate percentage
   - Recent match history (last 10 matches)
   - Earned badges
   - Rating progression chart
6. Player can view opponent profiles from match history
```

### Flow 5: Challenge Generation and Difficulty Adaptation

```
1. Challenge Service triggered to generate new challenge
2. Random template selected from database
3. Parameters applied based on difficulty level
4. Test cases generated and validated
5. Challenge stored in database
6. When challenge assigned to match:
   a. Player skill levels considered
   b. Challenge difficulty adjusted if needed
   c. Challenge sent to both players
7. After match:
   a. Success rate tracked
   b. If success rate too high/low, difficulty flagged for review
   c. Future challenges adjusted based on feedback
```

## AWS Integration

### Recommended AWS Services

**Compute**:
- **ECS (Elastic Container Service)**: Run microservices in containers
  - Match Service: 2-4 instances
  - Challenge Service: 1-2 instances
  - Judge Service: 4-8 instances (scales with load)
  - Integrity Verification Service: 2-4 instances (scales with submission volume)
  - Rating Service: 1-2 instances
  - Leaderboard Service: 1-2 instances
  - Badge Service: 1 instance
  - Tournament Service: 1-2 instances

**Data Storage**:
- **RDS (Relational Database Service)**: PostgreSQL for persistent data
  - Player accounts and ratings
  - Match history
  - Challenge templates
  - Leaderboard snapshots
  - Tournament data
  - Integrity analysis records
  - Audit logs

- **ElastiCache (Redis)**: In-memory cache for performance
  - Active match state
  - Leaderboard cache (updated every 5 minutes)
  - Player rating cache
  - Player integrity profile cache
  - Challenge pool cache

- **S3 (Simple Storage Service)**: Store challenge templates, badge icons, and ML models
  - Challenge definitions (JSON)
  - Badge images
  - Tournament bracket snapshots
  - Anonymized code embeddings for model training
  - Trained AI classifier model for integrity verification

**Networking**:
- **API Gateway**: REST API endpoint for client requests
  - Rate limiting per player
  - Request validation
  - Authentication token verification

- **WebSocket API**: Real-time match updates
  - Live score updates
  - Opponent submission notifications
  - Match conclusion broadcasts
  - Integrity status notifications

**Monitoring and Logging**:
- **CloudWatch**: Monitor service health and performance
  - CPU, memory, network metrics
  - Request latency
  - Error rates
  - Integrity analysis latency
  - Flagging rate and false positive trends

- **CloudWatch Logs**: Centralized logging
  - Service logs
  - Execution logs from Sandbox
  - Integrity verification logs
  - Audit trail for all rating changes
  - Error tracking

**Security**:
- **IAM (Identity and Access Management)**: Service-to-service authentication
  - Each service has minimal required permissions
  - Sandbox service isolated with restricted permissions
  - Integrity Verification Service has read-only access to player history

- **Secrets Manager**: Store sensitive configuration
  - Database credentials
  - API keys
  - JWT signing keys
  - ML model credentials

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CloudFront (CDN)                      │
│              (Serve static assets globally)              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              API Gateway + WebSocket API                 │
│         (Route requests, handle real-time updates)       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼────────┐ ┌─▼──────────┐
│ ECS Cluster  │ │ ElastiCache│ │ RDS        │
│ (Services)   │ │ (Redis)    │ │ (Database) │
└──────────────┘ └────────────┘ └────────────┘
        │
┌───────▼──────────────────────────────────────┐
│  Sandbox Service (Isolated Execution)        │
│  (Docker containers for code execution)      │
└────────────────────────────────────────────┘
```

### Scaling Strategy

**Horizontal Scaling**:
- Judge Service: Scale based on submission queue depth
- Match Service: Scale based on active match count
- Challenge Service: Scale based on generation requests

**Vertical Scaling**:
- RDS: Increase instance size for database performance
- ElastiCache: Increase node size for cache performance

**Auto-Scaling Policies**:
- Judge Service: Scale up when CPU > 70%, scale down when CPU < 30%
- Match Service: Scale up when active matches > 1000, scale down when < 500
- Challenge Service: Scale up when generation queue > 100, scale down when < 20

## Technical Logic

### Challenge Difficulty Calibration

**Difficulty Levels**:
- Beginner: Solvable by most players within time limit (target success rate: 70-80%)
- Intermediate: Requires solid understanding (target success rate: 50-60%)
- Advanced: Requires deep knowledge (target success rate: 30-40%)

**Calibration Process**:
1. Track success rate for each challenge
2. If success rate > target + 10%: Increase difficulty
3. If success rate < target - 10%: Decrease difficulty
4. Adjust future challenge generation parameters accordingly
5. Flag challenges with extreme success rates for manual review

### Matchmaking Algorithm

```
find_opponent(player_rating):
  1. Search for opponent within ±200 ELO range
  2. If found within 10 seconds: Match players
  3. If not found:
     a. Expand search range by ±50 ELO
     b. Wait another 10 seconds
     c. Repeat until opponent found or timeout (60 seconds)
  4. If timeout: Offer single-player challenge or queue for next round
  5. Return matched opponent or null
```

### Code Execution Safety

**Sandbox Isolation**:
1. Each submission runs in separate Docker container
2. Container has read-only access to test data
3. No network access allowed
4. No file system write access
5. CPU limited to 1 core
6. Memory limited to 256MB
7. Process killed if exceeds 5-second timeout

**Execution Flow**:
```
1. Receive submission (code + language)
2. Create isolated container
3. Copy test data into container
4. Execute code with first test input
5. Capture output and execution time
6. Compare with expected output
7. Repeat for all test cases
8. Destroy container
9. Return results
```

### Real-Time Match Updates

**WebSocket Message Flow**:
```
Client connects to WebSocket
  ↓
Server sends: { type: "match_started", challenge: {...} }
  ↓
Player submits code
  ↓
Server sends: { type: "submission_received", player: "you" }
  ↓
Opponent submits code
  ↓
Server sends: { type: "opponent_submitted" }
  ↓
Judge completes evaluation
  ↓
Server sends: { type: "match_concluded", winner: "...", scores: {...} }
  ↓
Server sends: { type: "rating_updated", old_rating: 1200, new_rating: 1215 }
  ↓
Client disconnects
```

### Performance Optimization

**Caching Strategy**:
- Leaderboard cached for 5 minutes (updated after each rating change)
- Challenge pool cached for 1 hour (refreshed periodically)
- Player ratings cached for 1 minute (updated after each match)
- Player integrity profiles cached for 5 minutes
- Badge definitions cached indefinitely (rarely change)

**Database Optimization**:
- Indexes on player_id, match_id, rating for fast queries
- Indexes on integrity_analysis for flagged match lookups
- Partitioning match history by date for faster historical queries
- Materialized views for leaderboard rankings

**API Optimization**:
- Pagination for leaderboard queries (100 players per page)
- Compression for large responses
- Connection pooling for database connections

### Integrity Verification Logic

**Stylometric Analysis**:
1. Extract code features from submission:
   - Token frequency distribution
   - Indentation patterns (spaces vs tabs, depth)
   - Variable naming conventions (camelCase, snake_case, etc.)
   - Comment density and style
   - Structural patterns (loop types, conditionals, etc.)
2. Compare against player's historical code embedding profile
3. Calculate deviation score (0–100, where 100 = maximum deviation)
4. Stylometry score = deviation score

**LLM Probability Classification**:
1. Tokenize submission code
2. Run through trained transformer-based classifier
3. Classifier outputs probability that code was AI-generated (0–100)
4. LLM probability score = classifier output

**Behavioral Anomaly Detection**:
1. Compare solve time against player's historical median
2. Compare code complexity against previous 10 matches
3. Detect unnatural improvement spikes (e.g., sudden O(n) → O(1) solution)
4. Analyze submission timing patterns (multiple rapid submissions vs single submission)
5. Behavioral anomaly score = aggregated deviation (0–100)

**Probability Aggregation**:
```
overall_cheat_probability = 
  0.4 * stylometry_score +
  0.4 * llm_probability_score +
  0.2 * behavioral_anomaly_score
```

**Rating Confidence System**:
- New players start with 100% confidence
- Clean match: +1 confidence (max 100%)
- Soft flag (70–85%): -2 confidence
- Hard flag (≥85%): -5 confidence
- Repeated flags: progressive penalty
- Confidence recovery: +0.5 per clean match after flagging
- Minimum confidence: 0% (player may be restricted from ranked play)

**False Positive Minimization**:
- Multi-signal weighted aggregation (not single metric)
- Historical consistency checks (compare against player baseline)
- Confidence decay recovery for clean behavior
- Continuous model calibration using audit feedback
- Target: <5% false positive rate over rolling 1000-match window

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property-Based Testing Overview

Property-based testing validates software correctness by testing universal properties across many generated inputs. Each property is a formal specification that should hold for all valid inputs.

### Core Principles

1. **Universal Quantification**: Every property should hold for all valid inputs
2. **Determinism**: Properties must be reproducible and verifiable
3. **Fairness**: Properties ensure competitive integrity and player protection

### Integrity Properties

**Integrity Property 1: Rating Update Atomicity**
```
For all ranked matches:
  Rating updates must not finalize before integrity verification completes.
  If integrity verification flags a match, rating update must be frozen.
  Frozen ratings must be reversible upon successful appeal.
```

**Integrity Property 2: No Unjust Permanent Penalties**
```
For all players:
  No player shall be permanently penalized solely based on a single AI probability output.
  Multi-signal confirmation required for any rating restriction.
  All penalties must be appealable and reversible.
```

**Integrity Property 3: False Positive Rate Bound**
```
For all rolling 1000-match windows:
  False positive rate (flagged clean matches) must remain < 5%.
  Model calibration must continuously improve this metric.
  Audit feedback must inform model retraining.
```

**Integrity Property 4: Rating Confidence Monotonicity**
```
For all players:
  Clean matches must increase or maintain rating confidence.
  Flagged matches must decrease rating confidence.
  Confidence must never increase due to flagged matches.
```

**Integrity Property 5: Transparency and Auditability**
```
For all integrity decisions:
  Every flagging decision must be logged with full reasoning.
  Players must be able to view their integrity analysis.
  Audit logs must be immutable and timestamped.
``` 