# Classification Model - Complete Summary

## Purpose

The classification model detects three types of code submissions:
1. **Legitimate** - Code written by the player
2. **AI-Assisted** - Code generated or heavily modified by LLM
3. **Pasted** - Code copied from external sources

## Key Features (87 Total)

### Temporal Features (15)
- Time to first submission
- Time between submissions
- Total submission time
- Time to solve
- Keystroke speed metrics
- Pause frequency and duration
- Clipboard access count

### Code Characteristics (20)
- Code length and lines
- Unique tokens
- Comment ratio
- Indentation consistency
- Variable naming style
- Cyclomatic complexity
- Nesting depth
- Language-specific features

### Behavioral Patterns (18)
- Submission count
- Success rate
- Improvement trajectory
- Monotonic improvement indicator
- Sudden score jumps
- Player baseline deviations
- Historical patterns

### Paste Detection (12)
- Copy-paste events
- Deletion ratio
- External source similarity
- GitHub similarity
- LeetCode similarity
- Formatting anomalies
- Unusual whitespace

### Complexity & Efficiency (10)
- Time complexity
- Space complexity
- Optimization level
- Execution time
- Memory usage
- Efficiency vs player average

### Additional Features (12)
- Language encoding
- Domain encoding
- Difficulty encoding
- Player rating
- Match time remaining
- Opponent rating difference
- Recent wins/losses
- Time since last match

## Model Architecture

**Primary: XGBoost Classifier**
- 100 trees with feature importance tracking
- Handles non-linear relationships
- Fast inference (< 100ms)
- Explainable via SHAP values

**Alternative: Transformer-based**
- Multi-head attention for feature interactions
- Better for complex patterns
- Slower inference but higher accuracy

## Output

```json
{
  "legitimate_probability": 0.85,
  "ai_assisted_probability": 0.12,
  "pasted_probability": 0.03,
  "predicted_class": "legitimate",
  "confidence_score": 0.85,
  "feature_importance": {...},
  "risk_factors": [...],
  "recommendations": [...]
}
```

## Training Data

### Legitimate Submissions
- Natural keystroke variance (10-15)
- Gradual improvement across iterations
- Low external source similarity (< 0.2)
- Variable submission times
- High deletion ratio (0.15-0.25)

### AI-Assisted Submissions
- Uniform keystroke speed (variance < 3)
- Sudden jumps to 100% test case pass
- Optimal or near-optimal solutions
- Very fast first submission (< 5 seconds)
- Low deletion ratio (< 0.05)
- High deviation from player baseline

### Pasted Submissions
- Extreme keystroke variance (> 40)
- Very high external source similarity (> 0.85)
- Formatting inconsistencies
- Copy-paste events detected
- Unusual whitespace patterns
- Matches known templates

## Performance Targets

- **Precision**: > 95% (minimize false positives)
- **Recall**: > 90% (catch most cheaters)
- **F1-Score**: > 92%
- **ROC-AUC**: > 0.95

## Implementation Status

✅ **Completed**:
- Feature specification (87 features)
- Model architecture design
- Training data format
- Example logs (3 per category)
- Output format specification
- Performance metrics

⏳ **Next Steps**:
1. Collect labeled training data (1000+ examples)
2. Implement feature extraction pipeline
3. Train and validate model
4. Deploy to production
5. Monitor and retrain monthly

## Integration with Backend

### Submission Model Updates
- Added 20+ new fields for classification features
- Tracks keystroke dynamics
- Records copy-paste events
- Stores classification results

### API Response Updates
- SubmissionResponse includes classification fields
- Returns probabilities for all three classes
- Includes confidence score
- Provides risk factors and recommendations

## Database Schema

```sql
ALTER TABLE submissions ADD COLUMN (
  time_to_first_submission INT,
  keystroke_speed_avg FLOAT,
  keystroke_speed_variance FLOAT,
  copy_paste_events INT,
  deletion_ratio FLOAT,
  code_length INT,
  code_lines INT,
  unique_tokens INT,
  comment_ratio FLOAT,
  indentation_consistency FLOAT,
  variable_naming_style VARCHAR(50),
  submission_count_in_match INT,
  time_to_solve INT,
  iterations_to_solution INT,
  code_paste_probability FLOAT,
  ai_assisted_probability FLOAT,
  classification_confidence FLOAT
);
```

## Monitoring & Feedback Loop

### Metrics to Track
- False positive rate (flagged legitimate code)
- False negative rate (missed cheating)
- Model accuracy by player skill level
- Model accuracy by programming language
- Model accuracy by problem domain

### Continuous Improvement
- Monthly retraining with new labeled data
- A/B testing of model versions
- Player appeals and feedback
- Manual review of edge cases
- Feature importance analysis

## Security Considerations

1. **Privacy**: Don't store raw keystroke data long-term
2. **Fairness**: Regular bias audits across skill levels
3. **Transparency**: Players can view their classification results
4. **Appeals**: Mechanism for players to appeal decisions
5. **Audit Trail**: Log all classification decisions

## References

- Training data: `ml/training_data/classification_model/README.md`
- Submission model: `backend/app/models/submission.py`
- Submission schema: `backend/app/schemas/submission_schema.py`
- Integrity service: `backend/app/services/integrity_service.py`
