# AI-Assisted Code & Paste Detection Classification Model

## Overview

This classification model detects whether a code submission was:
1. **Legitimately written** by the player
2. **AI-assisted** (generated or heavily modified by LLM)
3. **Pasted** from external sources (copy-paste detection)

The model uses multiple input features including behavioral metrics, code characteristics, keystroke dynamics, and temporal patterns.

## Input Features

### 1. Temporal Features (Time-Based)

#### 1.1 Submission Timing
```json
{
  "time_to_first_submission": 15,  // Seconds from match start to first submission
  "time_between_submissions": [8, 12, 5, 10],  // Array of times between each submission
  "avg_time_between_submissions": 8.75,  // Average time between submissions
  "total_submission_time": 45,  // Total time spent on submissions
  "time_to_solve": 42,  // Time from match start to final correct submission
  "submission_count": 4,  // Total number of submissions
  "iterations_to_solution": 4  // Number of attempts before correct solution
}
```

**Rationale**: 
- Humans typically take time to think before first submission
- AI-assisted code often appears very quickly (< 5 seconds)
- Pasted code shows sudden jumps in submission speed
- Legitimate solutions show gradual improvement across iterations

#### 1.2 Keystroke Dynamics
```json
{
  "keystroke_speed_avg": 45.2,  // Characters per second (typical: 30-60 for humans)
  "keystroke_speed_variance": 12.5,  // Variance in keystroke speed
  "keystroke_speed_min": 20,  // Minimum keystroke speed
  "keystroke_speed_max": 85,  // Maximum keystroke speed
  "copy_paste_events": 2,  // Number of detected copy/paste operations
  "deletion_ratio": 0.15,  // Ratio of deletions to total keystrokes (typical: 0.1-0.3)
  "pause_frequency": 8,  // Number of pauses > 2 seconds
  "avg_pause_duration": 3.5  // Average pause duration in seconds
}
```

**Rationale**:
- Humans have variable keystroke speed (high variance)
- AI-generated code shows uniform keystroke speed (low variance)
- Pasted code shows sudden speed changes
- Humans frequently pause and delete (high deletion ratio)
- AI code has minimal deletions (low deletion ratio)

### 2. Code Characteristics (Static Analysis)

#### 2.1 Code Structure
```json
{
  "code_length": 245,  // Total characters in code
  "code_lines": 12,  // Number of lines
  "avg_line_length": 20.4,  // Average characters per line
  "unique_tokens": 34,  // Number of unique tokens
  "token_diversity": 0.78,  // Ratio of unique tokens to total tokens
  "cyclomatic_complexity": 3,  // Code complexity metric
  "nesting_depth": 2  // Maximum nesting depth
}
```

**Rationale**:
- AI code tends to be more uniform and optimized
- Human code shows more variation in structure
- Pasted code often has unusual formatting

#### 2.2 Code Quality Metrics
```json
{
  "comment_ratio": 0.08,  // Ratio of comment lines to total lines
  "docstring_present": false,  // Whether docstrings are present
  "variable_naming_style": "snake_case",  // Naming convention used
  "naming_consistency": 0.95,  // Consistency of naming style (0-1)
  "indentation_consistency": 0.98,  // Consistency of indentation (0-1)
  "line_length_variance": 8.5,  // Variance in line lengths
  "blank_line_ratio": 0.12  // Ratio of blank lines to total lines
}
```

**Rationale**:
- AI code often has perfect consistency (suspicious)
- Human code shows natural variation
- Pasted code may have inconsistent formatting
- Comments indicate human understanding

#### 2.3 Language-Specific Features
```json
{
  "language": "python",
  "uses_built_ins": true,  // Whether built-in functions are used
  "uses_libraries": false,  // Whether external libraries are imported
  "function_count": 2,  // Number of functions defined
  "class_count": 0,  // Number of classes defined
  "loop_types": ["for", "while"],  // Types of loops used
  "conditional_types": ["if", "elif"],  // Types of conditionals
  "error_handling": false  // Whether try-except blocks are present
}
```

**Rationale**:
- AI code often uses optimal built-ins
- Human code may use more verbose approaches
- Pasted code may have unusual library imports

### 3. Behavioral Patterns (User Behavior)

#### 3.1 Submission Patterns
```json
{
  "submission_count_in_match": 4,  // Total submissions in this match
  "successful_submissions": 1,  // Number of successful submissions
  "failed_submissions": 3,  // Number of failed submissions
  "success_rate": 0.25,  // Ratio of successful to total submissions
  "improvement_trajectory": [0, 25, 50, 100],  // Test case pass rates over submissions
  "is_monotonic_improvement": true,  // Whether improvement is monotonic
  "sudden_jump_in_score": false  // Whether there's a sudden score jump
}
```

**Rationale**:
- Humans show gradual improvement
- AI-assisted code often shows sudden jumps
- Pasted code may show no improvement pattern

#### 3.2 Player Historical Patterns
```json
{
  "player_avg_submission_time": 35,  // Player's average time to first submission
  "player_avg_iterations": 3.2,  // Player's average iterations to solution
  "player_avg_keystroke_speed": 42,  // Player's average keystroke speed
  "player_code_style_embedding": [0.1, 0.2, 0.3, ...],  // Embedding of player's typical code style
  "deviation_from_player_baseline": 0.45,  // How much this submission deviates from player's norm
  "player_success_rate_on_domain": 0.68,  // Player's historical success rate on this domain
  "player_recent_rating_change": 45,  // Recent rating changes (sudden jumps are suspicious)
  "player_integrity_history": {
    "total_matches": 50,
    "flagged_matches": 2,
    "flag_rate": 0.04
  }
}
```

**Rationale**:
- Deviations from player's baseline are suspicious
- Sudden rating jumps correlate with cheating
- Players with integrity flags need closer monitoring

### 4. Paste Detection Features

#### 4.1 Copy-Paste Indicators
```json
{
  "copy_paste_events": 2,  // Number of detected copy/paste operations
  "clipboard_access_count": 2,  // Number of times clipboard was accessed
  "paste_size_avg": 45,  // Average size of pasted content
  "paste_frequency": 0.5,  // Ratio of paste events to total submissions
  "pasted_code_ratio": 0.35,  // Estimated ratio of pasted vs typed code
  "external_source_similarity": 0.78,  // Similarity to known online solutions
  "github_similarity": 0.82,  // Similarity to GitHub repositories
  "leetcode_similarity": 0.75  // Similarity to LeetCode solutions
}
```

**Rationale**:
- Direct paste detection via clipboard monitoring
- Similarity to known sources indicates paste
- Pasted code shows high external similarity

#### 4.2 Formatting Anomalies
```json
{
  "formatting_matches_template": true,  // Whether formatting matches known templates
  "unusual_whitespace": false,  // Whether whitespace is unusual
  "mixed_line_endings": false,  // Whether line endings are mixed (Windows/Unix)
  "encoding_anomalies": false,  // Whether encoding is unusual
  "hidden_characters": 0  // Number of hidden/special characters
}
```

**Rationale**:
- Pasted code often has formatting inconsistencies
- Templates have recognizable patterns
- Hidden characters indicate copy-paste artifacts

### 5. Complexity & Optimization Features

#### 5.1 Algorithm Complexity
```json
{
  "time_complexity": "O(n)",  // Estimated time complexity
  "space_complexity": "O(1)",  // Estimated space complexity
  "complexity_vs_optimal": 1.0,  // Ratio of actual to optimal complexity
  "is_optimal_solution": true,  // Whether solution is optimal
  "optimization_level": "high"  // "low", "medium", "high"
}
```

**Rationale**:
- AI code often finds optimal solutions
- Human code may use suboptimal approaches
- Sudden optimization jumps are suspicious

#### 5.2 Code Efficiency
```json
{
  "execution_time_ms": 45,  // Actual execution time
  "memory_used_mb": 12,  // Actual memory usage
  "efficiency_vs_player_avg": 1.2,  // Ratio to player's average
  "efficiency_vs_domain_avg": 0.95  // Ratio to domain average
}
```

**Rationale**:
- Sudden efficiency improvements are suspicious
- Deviations from player's typical efficiency matter

## Classification Model Architecture

### Input Vector (Total: 87 Features)

```
[
  // Temporal Features (7)
  time_to_first_submission,
  avg_time_between_submissions,
  total_submission_time,
  time_to_solve,
  submission_count,
  iterations_to_solution,
  keystroke_speed_avg,
  
  // Keystroke Dynamics (8)
  keystroke_speed_variance,
  keystroke_speed_min,
  keystroke_speed_max,
  copy_paste_events,
  deletion_ratio,
  pause_frequency,
  avg_pause_duration,
  clipboard_access_count,
  
  // Code Structure (7)
  code_length,
  code_lines,
  avg_line_length,
  unique_tokens,
  token_diversity,
  cyclomatic_complexity,
  nesting_depth,
  
  // Code Quality (7)
  comment_ratio,
  docstring_present,
  naming_consistency,
  indentation_consistency,
  line_length_variance,
  blank_line_ratio,
  uses_built_ins,
  
  // Behavioral Patterns (8)
  successful_submissions,
  failed_submissions,
  success_rate,
  is_monotonic_improvement,
  sudden_jump_in_score,
  improvement_trajectory_variance,
  player_avg_submission_time,
  player_avg_iterations,
  
  // Player Baseline (6)
  player_avg_keystroke_speed,
  deviation_from_player_baseline,
  player_success_rate_on_domain,
  player_recent_rating_change,
  player_flag_rate,
  player_integrity_history_score,
  
  // Paste Detection (8)
  paste_size_avg,
  paste_frequency,
  pasted_code_ratio,
  external_source_similarity,
  github_similarity,
  leetcode_similarity,
  formatting_matches_template,
  unusual_whitespace,
  
  // Complexity Features (6)
  complexity_vs_optimal,
  is_optimal_solution,
  optimization_level_score,
  execution_time_ms,
  memory_used_mb,
  efficiency_vs_player_avg,
  
  // Additional Features (10)
  language_encoded,
  domain_encoded,
  difficulty_encoded,
  player_rating_normalized,
  match_time_remaining,
  opponent_rating_diff,
  player_recent_wins,
  player_recent_losses,
  time_since_last_match,
  match_number_today
]
```

### Model Architecture

**Recommended: Gradient Boosting Classifier (XGBoost/LightGBM)**

```
Input Layer (87 features)
    ↓
Feature Normalization & Scaling
    ↓
XGBoost Classifier
├─ Tree 1: Temporal features focus
├─ Tree 2: Code characteristics focus
├─ Tree 3: Behavioral patterns focus
├─ Tree 4: Paste detection focus
└─ Tree 5-100: Ensemble refinement
    ↓
Output Layer (3 classes)
├─ Legitimate (0-0.33)
├─ AI-Assisted (0.33-0.67)
└─ Pasted (0.67-1.0)
```

**Alternative: Transformer-based Model**

```
Input Features (87)
    ↓
Embedding Layer
    ↓
Multi-Head Attention (8 heads)
├─ Temporal attention
├─ Code structure attention
├─ Behavioral attention
└─ Paste detection attention
    ↓
Feed-Forward Network
    ↓
Classification Head (3 outputs)
```

## Output Format

```json
{
  "submission_id": "sub_001",
  "classification": {
    "legitimate_probability": 0.85,
    "ai_assisted_probability": 0.12,
    "pasted_probability": 0.03,
    "predicted_class": "legitimate",
    "confidence_score": 0.85
  },
  "feature_importance": {
    "keystroke_speed_variance": 0.18,
    "deviation_from_player_baseline": 0.15,
    "time_to_first_submission": 0.12,
    "deletion_ratio": 0.11,
    "external_source_similarity": 0.10,
    "other_features": 0.34
  },
  "risk_factors": [
    "Keystroke speed variance is unusually low (0.5 vs player avg 12.5)",
    "Time to first submission is very fast (3 seconds vs player avg 35)"
  ],
  "recommendations": [
    "Flag for manual review",
    "Increase monitoring for this player",
    "Request code explanation from player"
  ],
  "classified_at": "2026-02-25T19:30:00Z"
}
```

## Training Data Requirements

### Example 1: Legitimate Submission

```json
{
  "submission_id": "sub_001",
  "label": "legitimate",
  "features": {
    "time_to_first_submission": 28,
    "keystroke_speed_avg": 42.5,
    "keystroke_speed_variance": 11.2,
    "copy_paste_events": 0,
    "deletion_ratio": 0.18,
    "code_length": 245,
    "comment_ratio": 0.12,
    "indentation_consistency": 0.96,
    "submission_count": 3,
    "iterations_to_solution": 3,
    "improvement_trajectory": [33, 66, 100],
    "is_monotonic_improvement": true,
    "deviation_from_player_baseline": 0.08,
    "external_source_similarity": 0.15,
    "github_similarity": 0.12,
    "execution_time_ms": 45,
    "efficiency_vs_player_avg": 0.98
  },
  "confidence": 0.92
}
```

### Example 2: AI-Assisted Submission

```json
{
  "submission_id": "sub_002",
  "label": "ai_assisted",
  "features": {
    "time_to_first_submission": 3,
    "keystroke_speed_avg": 65.2,
    "keystroke_speed_variance": 2.1,
    "copy_paste_events": 1,
    "deletion_ratio": 0.02,
    "code_length": 312,
    "comment_ratio": 0.05,
    "indentation_consistency": 1.0,
    "submission_count": 1,
    "iterations_to_solution": 1,
    "improvement_trajectory": [100],
    "is_monotonic_improvement": false,
    "deviation_from_player_baseline": 0.72,
    "external_source_similarity": 0.45,
    "github_similarity": 0.38,
    "execution_time_ms": 28,
    "efficiency_vs_player_avg": 2.1,
    "complexity_vs_optimal": 1.0,
    "is_optimal_solution": true
  },
  "confidence": 0.88
}
```

### Example 3: Pasted Submission

```json
{
  "submission_id": "sub_003",
  "label": "pasted",
  "features": {
    "time_to_first_submission": 2,
    "keystroke_speed_avg": 120.5,
    "keystroke_speed_variance": 45.2,
    "copy_paste_events": 3,
    "deletion_ratio": 0.01,
    "code_length": 428,
    "comment_ratio": 0.08,
    "indentation_consistency": 0.88,
    "submission_count": 1,
    "iterations_to_solution": 1,
    "improvement_trajectory": [100],
    "is_monotonic_improvement": false,
    "deviation_from_player_baseline": 0.95,
    "external_source_similarity": 0.92,
    "github_similarity": 0.89,
    "leetcode_similarity": 0.91,
    "formatting_matches_template": true,
    "unusual_whitespace": true,
    "execution_time_ms": 32,
    "efficiency_vs_player_avg": 1.8
  },
  "confidence": 0.91
}
```

## Model Performance Metrics

### Target Metrics
- **Precision**: > 95% (minimize false positives)
- **Recall**: > 90% (catch most cheaters)
- **F1-Score**: > 92%
- **ROC-AUC**: > 0.95

### Class-Specific Metrics
- **Legitimate**: Precision > 98%, Recall > 95%
- **AI-Assisted**: Precision > 92%, Recall > 88%
- **Pasted**: Precision > 94%, Recall > 92%

## Implementation Notes

1. **Feature Engineering**: Normalize all features to 0-1 range
2. **Class Imbalance**: Use weighted loss or SMOTE for imbalanced classes
3. **Real-time Prediction**: Model should run in < 100ms
4. **Continuous Learning**: Retrain monthly with new labeled data
5. **Explainability**: Use SHAP values for feature importance
6. **Monitoring**: Track false positive/negative rates continuously

## Next Steps

1. Collect labeled training data (1000+ examples per class)
2. Implement feature extraction pipeline
3. Train and validate model
4. Deploy to production with monitoring
5. Collect feedback and retrain monthly
6. Implement appeal mechanism for false positives
