# Problem Statement Generator - Training Data

## Overview
Training data for the AI model that generates coding challenge problem statements based on difficulty level (ELO rating) and domain.

## Data Format

Each training example contains:
- **input**: ELO rating and domain
- **output**: Generated problem statement
- **metadata**: Difficulty level, domain, success metrics

## Example Logs

### Example 1: Beginner Level - Arrays Domain

**Input:**
```json
{
  "elo_rating": 1100,
  "domain": "arrays",
  "difficulty_level": "beginner",
  "template_id": "array_basic_001"
}
```

**Output:**
```json
{
  "problem_id": "prob_001",
  "title": "Find the Sum of Array Elements",
  "description": "Given an array of integers, write a function that returns the sum of all elements in the array. The array can contain both positive and negative numbers.",
  "input_specification": "First line: integer n (1 ≤ n ≤ 100) - size of array\nSecond line: n space-separated integers (-1000 ≤ each element ≤ 1000)",
  "output_specification": "Single integer representing the sum of all array elements",
  "example_input": "5\n1 2 3 4 5",
  "example_output": "15",
  "constraints": [
    "1 ≤ n ≤ 100",
    "-1000 ≤ each element ≤ 1000",
    "Time limit: 1 second",
    "Memory limit: 256MB"
  ],
  "difficulty_score": 1.2,
  "estimated_success_rate": 0.75,
  "domain": "arrays",
  "generated_at": "2026-02-25T18:15:00Z"
}
```

**Metadata:**
```json
{
  "elo_range": [1000, 1200],
  "success_rate_target": 0.70,
  "actual_success_rate": 0.73,
  "quality_score": 0.92,
  "feedback": "Clear problem statement, appropriate difficulty for beginner level"
}
```

---

### Example 2: Intermediate Level - Strings Domain

**Input:**
```json
{
  "elo_rating": 1350,
  "domain": "strings",
  "difficulty_level": "intermediate",
  "template_id": "string_manipulation_002"
}
```

**Output:**
```json
{
  "problem_id": "prob_002",
  "title": "Longest Palindromic Substring",
  "description": "Given a string s, find the longest contiguous substring that is a palindrome. A palindrome is a word, phrase, number, or other sequence of characters that reads the same forward and backward (ignoring spaces, punctuation, and capitalization for this problem, consider only alphanumeric characters and case-sensitive).",
  "input_specification": "Single line: string s (1 ≤ length ≤ 1000) containing only lowercase English letters",
  "output_specification": "The longest palindromic substring. If multiple palindromes have the same length, return the first one found",
  "example_input": "babad",
  "example_output": "bab",
  "constraints": [
    "1 ≤ length(s) ≤ 1000",
    "s contains only lowercase English letters",
    "Time limit: 2 seconds",
    "Memory limit: 256MB"
  ],
  "difficulty_score": 2.1,
  "estimated_success_rate": 0.55,
  "domain": "strings",
  "generated_at": "2026-02-25T18:20:00Z"
}
```

**Metadata:**
```json
{
  "elo_range": [1300, 1500],
  "success_rate_target": 0.55,
  "actual_success_rate": 0.58,
  "quality_score": 0.88,
  "feedback": "Good intermediate problem, requires understanding of string algorithms"
}
```

---

### Example 3: Advanced Level - Dynamic Programming Domain

**Input:**
```json
{
  "elo_rating": 1650,
  "domain": "dynamic_programming",
  "difficulty_level": "advanced",
  "template_id": "dp_advanced_003"
}
```

**Output:**
```json
{
  "problem_id": "prob_003",
  "title": "Edit Distance (Levenshtein Distance)",
  "description": "Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2. You have the following three operations permitted on a word: (1) Insert a character, (2) Delete a character, (3) Replace a character. This is also known as the Levenshtein distance or edit distance.",
  "input_specification": "Line 1: string word1 (0 ≤ length ≤ 500)\nLine 2: string word2 (0 ≤ length ≤ 500)\nBoth strings contain only lowercase English letters",
  "output_specification": "Single integer representing the minimum edit distance",
  "example_input": "horse\nros",
  "example_output": "3",
  "constraints": [
    "0 ≤ length(word1) ≤ 500",
    "0 ≤ length(word2) ≤ 500",
    "Both strings contain only lowercase English letters",
    "Time limit: 3 seconds",
    "Memory limit: 512MB"
  ],
  "difficulty_score": 3.5,
  "estimated_success_rate": 0.35,
  "domain": "dynamic_programming",
  "generated_at": "2026-02-25T18:25:00Z"
}
```

**Metadata:**
```json
{
  "elo_range": [1600, 1800],
  "success_rate_target": 0.35,
  "actual_success_rate": 0.38,
  "quality_score": 0.91,
  "feedback": "Excellent advanced problem, requires DP knowledge and optimization skills"
}
```

---

## Training Process

1. **Data Collection**: Gather problem statements across difficulty levels
2. **Feature Extraction**: Extract ELO rating, domain, difficulty level
3. **Model Training**: Train LLM to generate problems based on input features
4. **Validation**: Test generated problems for clarity and correctness
5. **Calibration**: Adjust difficulty based on actual success rates
6. **Feedback Loop**: Use player success rates to improve generation

## Success Metrics

- **Clarity Score**: 0-100 (how clear is the problem statement)
- **Correctness Score**: 0-100 (are test cases valid)
- **Difficulty Accuracy**: How close actual success rate is to target
- **Diversity Score**: How unique are generated problems

## Next Steps

- Collect more training examples across all domains
- Fine-tune LLM on domain-specific problem statements
- Implement difficulty calibration feedback loop
- Monitor success rates and adjust generation parameters
