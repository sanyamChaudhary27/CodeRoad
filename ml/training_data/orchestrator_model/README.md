# Orchestrator Model - Training Data

## Overview
Training data for the orchestrator model that coordinates the entire match lifecycle. The orchestrator manages:
- Challenge selection based on player skill
- Submission evaluation pipeline
- Integrity verification
- Rating updates
- Real-time updates to players

## Data Format

Each training example contains:
- **input**: Match state and player information
- **output**: Orchestration decisions and actions
- **metadata**: Decision quality and feedback

## Example Logs

### Example 1: Match Orchestration - Beginner Level

**Input:**
```json
{
  "match_id": "match_001",
  "player1": {
    "player_id": "p_001",
    "username": "beginner_coder",
    "current_rating": 1150,
    "rating_confidence": 100,
    "recent_success_rate": 0.72
  },
  "player2": {
    "player_id": "p_002",
    "username": "learning_dev",
    "current_rating": 1180,
    "rating_confidence": 98,
    "recent_success_rate": 0.68
  },
  "average_rating": 1165,
  "difficulty_level": "beginner"
}
```

**Output:**
```json
{
  "orchestration_id": "orch_001",
  "match_id": "match_001",
  "decisions": {
    "challenge_selection": {
      "challenge_id": "prob_001",
      "title": "Find the Sum of Array Elements",
      "domain": "arrays",
      "difficulty_level": "beginner",
      "estimated_success_rate": 0.70,
      "time_limit_seconds": 60,
      "reason": "Appropriate difficulty for average rating 1165"
    },
    "evaluation_pipeline": [
      "test_case_evaluation",
      "ai_quality_assessment",
      "complexity_analysis"
    ],
    "integrity_verification": {
      "enabled": true,
      "threshold": 0.85,
      "soft_flag_threshold": 0.70,
      "reason": "Standard integrity check for ranked match"
    },
    "rating_update_strategy": {
      "k_factor": 32,
      "confidence_adjustment": true,
      "reason": "Standard ELO with confidence tracking"
    }
  },
  "expected_outcomes": {
    "player1_win_probability": 0.48,
    "player2_win_probability": 0.52,
    "expected_rating_change_winner": 8,
    "expected_rating_change_loser": -8
  },
  "orchestration_quality_score": 0.94,
  "created_at": "2026-02-25T19:15:00Z"
}
```

**Metadata:**
```json
{
  "match_type": "ranked_1v1",
  "skill_gap": 30,
  "confidence_average": 99,
  "decision_rationale": "Beginner-level challenge appropriate for both players",
  "feedback": "Good match pairing with appropriate difficulty"
}
```

---

### Example 2: Match Orchestration - Intermediate Level

**Input:**
```json
{
  "match_id": "match_002",
  "player1": {
    "player_id": "p_003",
    "username": "intermediate_pro",
    "current_rating": 1420,
    "rating_confidence": 95,
    "recent_success_rate": 0.58,
    "recent_integrity_flags": 0
  },
  "player2": {
    "player_id": "p_004",
    "username": "algo_master",
    "current_rating": 1380,
    "rating_confidence": 92,
    "recent_success_rate": 0.62,
    "recent_integrity_flags": 0
  },
  "average_rating": 1400,
  "difficulty_level": "intermediate"
}
```

**Output:**
```json
{
  "orchestration_id": "orch_002",
  "match_id": "match_002",
  "decisions": {
    "challenge_selection": {
      "challenge_id": "prob_002",
      "title": "Longest Palindromic Substring",
      "domain": "strings",
      "difficulty_level": "intermediate",
      "estimated_success_rate": 0.55,
      "time_limit_seconds": 90,
      "reason": "String algorithm challenge for intermediate players"
    },
    "evaluation_pipeline": [
      "test_case_evaluation",
      "ai_quality_assessment",
      "complexity_analysis",
      "optimization_feedback"
    ],
    "integrity_verification": {
      "enabled": true,
      "threshold": 0.85,
      "soft_flag_threshold": 0.70,
      "enhanced_monitoring": true,
      "reason": "Standard integrity check with enhanced monitoring"
    },
    "rating_update_strategy": {
      "k_factor": 32,
      "confidence_adjustment": true,
      "reason": "Standard ELO with confidence tracking"
    }
  },
  "expected_outcomes": {
    "player1_win_probability": 0.52,
    "player2_win_probability": 0.48,
    "expected_rating_change_winner": 6,
    "expected_rating_change_loser": -6
  },
  "orchestration_quality_score": 0.91,
  "created_at": "2026-02-25T19:20:00Z"
}
```

**Metadata:**
```json
{
  "match_type": "ranked_1v1",
  "skill_gap": 40,
  "confidence_average": 93.5,
  "decision_rationale": "Intermediate string algorithm challenge for competitive match",
  "feedback": "Well-matched players with appropriate challenge difficulty"
}
```

---

### Example 3: Match Orchestration - Advanced Level with Integrity Concerns

**Input:**
```json
{
  "match_id": "match_003",
  "player1": {
    "player_id": "p_005",
    "username": "expert_coder",
    "current_rating": 1750,
    "rating_confidence": 88,
    "recent_success_rate": 0.42,
    "recent_integrity_flags": 1,
    "last_flagged_match": "2026-02-24T10:00:00Z"
  },
  "player2": {
    "player_id": "p_006",
    "username": "dp_specialist",
    "current_rating": 1720,
    "rating_confidence": 96,
    "recent_success_rate": 0.38,
    "recent_integrity_flags": 0
  },
  "average_rating": 1735,
  "difficulty_level": "advanced"
}
```

**Output:**
```json
{
  "orchestration_id": "orch_003",
  "match_id": "match_003",
  "decisions": {
    "challenge_selection": {
      "challenge_id": "prob_003",
      "title": "Edit Distance (Levenshtein Distance)",
      "domain": "dynamic_programming",
      "difficulty_level": "advanced",
      "estimated_success_rate": 0.35,
      "time_limit_seconds": 120,
      "reason": "Advanced DP challenge for expert-level players"
    },
    "evaluation_pipeline": [
      "test_case_evaluation",
      "ai_quality_assessment",
      "complexity_analysis",
      "optimization_feedback",
      "enhanced_integrity_verification"
    ],
    "integrity_verification": {
      "enabled": true,
      "threshold": 0.85,
      "soft_flag_threshold": 0.70,
      "enhanced_monitoring": true,
      "player1_enhanced_scrutiny": true,
      "reason": "Player1 has recent integrity flag - enhanced monitoring enabled"
    },
    "rating_update_strategy": {
      "k_factor": 32,
      "confidence_adjustment": true,
      "player1_confidence_penalty": true,
      "reason": "Standard ELO with confidence tracking and player1 penalty"
    }
  },
  "expected_outcomes": {
    "player1_win_probability": 0.51,
    "player2_win_probability": 0.49,
    "expected_rating_change_winner": 4,
    "expected_rating_change_loser": -4,
    "player1_confidence_change_if_win": -2,
    "player1_confidence_change_if_loss": -5
  },
  "orchestration_quality_score": 0.87,
  "risk_assessment": {
    "integrity_risk": "medium",
    "rating_confidence_risk": "medium",
    "recommendation": "Proceed with enhanced monitoring"
  },
  "created_at": "2026-02-25T19:25:00Z"
}
```

**Metadata:**
```json
{
  "match_type": "ranked_1v1_with_monitoring",
  "skill_gap": 30,
  "confidence_average": 92,
  "player1_integrity_status": "under_monitoring",
  "decision_rationale": "Advanced DP challenge with enhanced integrity monitoring for player1",
  "feedback": "Appropriate challenge with necessary integrity safeguards"
}
```

---

## Orchestration Decision Points

### 1. Challenge Selection
- **Input**: Average player rating, recent success rates, domain preferences
- **Output**: Challenge ID, difficulty level, time limit
- **Logic**: Select challenge that matches average skill level

### 2. Evaluation Pipeline
- **Input**: Challenge type, player skill levels
- **Output**: Sequence of evaluation steps
- **Logic**: Determine which evaluation metrics to apply

### 3. Integrity Verification
- **Input**: Player history, recent flags, confidence scores
- **Output**: Verification level, thresholds, monitoring flags
- **Logic**: Determine integrity verification intensity

### 4. Rating Update Strategy
- **Input**: Match outcome, player confidence, integrity status
- **Output**: K-factor, confidence adjustments, rating freeze flags
- **Logic**: Calculate rating changes with integrity considerations

## Quality Metrics

- **Challenge Appropriateness**: Does challenge match player skill?
- **Fairness Score**: Are both players equally matched?
- **Integrity Confidence**: How confident in integrity verification?
- **Overall Orchestration Quality**: Weighted average of all metrics

## Next Steps

- Collect more orchestration examples across all skill levels
- Train reinforcement learning model for optimal challenge selection
- Implement dynamic difficulty adjustment based on match progression
- Build feedback loop to improve orchestration decisions
- Create A/B testing framework for orchestration strategies
