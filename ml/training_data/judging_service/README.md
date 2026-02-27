# Judging Service - Training Data

## Overview
Training data for the AI model that evaluates code submissions. The judging service scores submissions based on:
1. Test case correctness (primary)
2. AI quality assessment (secondary)
3. Complexity analysis (tertiary)

## Data Format

Each training example contains:
- **input**: Submitted code and test cases
- **output**: Evaluation scores and metrics
- **metadata**: Quality assessment and feedback

## Example Logs

### Example 1: Array Sum - Evaluation

**Input:**
```json
{
  "submission_id": "sub_001",
  "problem_id": "prob_001",
  "code": "def array_sum(n, arr):\n    total = 0\n    for num in arr:\n        total += num\n    return total\n\nn = int(input())\narr = list(map(int, input().split()))\nprint(array_sum(n, arr))",
  "language": "python",
  "test_cases": [
    {"input": "5\n1 2 3 4 5", "expected_output": "15"},
    {"input": "1\n42", "expected_output": "42"},
    {"input": "5\n-1 -2 -3 -4 -5", "expected_output": "-15"}
  ]
}
```

**Output:**
```json
{
  "evaluation_id": "eval_001",
  "submission_id": "sub_001",
  "test_case_results": [
    {
      "test_case_id": 1,
      "passed": true,
      "expected": "15",
      "actual": "15",
      "execution_time_ms": 5
    },
    {
      "test_case_id": 2,
      "passed": true,
      "expected": "42",
      "actual": "42",
      "execution_time_ms": 4
    },
    {
      "test_case_id": 3,
      "passed": true,
      "expected": "-15",
      "actual": "-15",
      "execution_time_ms": 5
    }
  ],
  "test_case_score": 100,
  "ai_quality_assessment": {
    "readability": 95,
    "efficiency": 95,
    "best_practices": 92,
    "overall_quality_score": 94
  },
  "complexity_analysis": {
    "time_complexity": "O(n)",
    "space_complexity": "O(1)",
    "complexity_score": 98
  },
  "final_score": 97,
  "winner_indicator": "excellent",
  "feedback": "Perfect solution with optimal complexity and clean code",
  "evaluated_at": "2026-02-25T19:00:00Z"
}
```

**Metadata:**
```json
{
  "execution_time_total_ms": 14,
  "memory_used_mb": 8,
  "code_quality": {
    "has_comments": true,
    "follows_conventions": true,
    "uses_built_ins": false,
    "is_readable": true
  },
  "feedback": "Excellent beginner solution"
}
```

---

### Example 2: Longest Palindromic Substring - Evaluation

**Input:**
```json
{
  "submission_id": "sub_002",
  "problem_id": "prob_002",
  "code": "def longest_palindrome(s):\n    if not s:\n        return \"\"\n    def expand_around_center(left, right):\n        while left >= 0 and right < len(s) and s[left] == s[right]:\n            left -= 1\n            right += 1\n        return s[left + 1:right]\n    longest = \"\"\n    for i in range(len(s)):\n        p1 = expand_around_center(i, i)\n        if len(p1) > len(longest):\n            longest = p1\n        p2 = expand_around_center(i, i + 1)\n        if len(p2) > len(longest):\n            longest = p2\n    return longest\n\ns = input().strip()\nprint(longest_palindrome(s))",
  "language": "python",
  "test_cases": [
    {"input": "babad", "expected_output": "bab"},
    {"input": "cbbd", "expected_output": "bb"},
    {"input": "a", "expected_output": "a"},
    {"input": "racecar", "expected_output": "racecar"}
  ]
}
```

**Output:**
```json
{
  "evaluation_id": "eval_002",
  "submission_id": "sub_002",
  "test_case_results": [
    {
      "test_case_id": 1,
      "passed": true,
      "expected": "bab",
      "actual": "bab",
      "execution_time_ms": 8
    },
    {
      "test_case_id": 2,
      "passed": true,
      "expected": "bb",
      "actual": "bb",
      "execution_time_ms": 7
    },
    {
      "test_case_id": 3,
      "passed": true,
      "expected": "a",
      "actual": "a",
      "execution_time_ms": 6
    },
    {
      "test_case_id": 4,
      "passed": true,
      "expected": "racecar",
      "actual": "racecar",
      "execution_time_ms": 9
    }
  ],
  "test_case_score": 100,
  "ai_quality_assessment": {
    "readability": 88,
    "efficiency": 85,
    "best_practices": 90,
    "overall_quality_score": 88
  },
  "complexity_analysis": {
    "time_complexity": "O(n²)",
    "space_complexity": "O(1)",
    "complexity_score": 82
  },
  "final_score": 90,
  "winner_indicator": "very_good",
  "feedback": "Good solution using expand-around-center approach. Could optimize with Manacher's algorithm for O(n) time.",
  "evaluated_at": "2026-02-25T19:05:00Z"
}
```

**Metadata:**
```json
{
  "execution_time_total_ms": 30,
  "memory_used_mb": 12,
  "code_quality": {
    "has_comments": false,
    "follows_conventions": true,
    "uses_built_ins": false,
    "is_readable": true
  },
  "optimization_suggestions": [
    "Consider Manacher's algorithm for O(n) time complexity",
    "Add comments explaining the expand-around-center approach"
  ],
  "feedback": "Solid intermediate solution with room for optimization"
}
```

---

### Example 3: Edit Distance - Evaluation

**Input:**
```json
{
  "submission_id": "sub_003",
  "problem_id": "prob_003",
  "code": "def edit_distance(word1, word2):\n    m, n = len(word1), len(word2)\n    dp = [[0] * (n + 1) for _ in range(m + 1)]\n    for i in range(m + 1):\n        dp[i][0] = i\n    for j in range(n + 1):\n        dp[0][j] = j\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if word1[i - 1] == word2[j - 1]:\n                dp[i][j] = dp[i - 1][j - 1]\n            else:\n                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])\n    return dp[m][n]\n\nword1 = input().strip()\nword2 = input().strip()\nprint(edit_distance(word1, word2))",
  "language": "python",
  "test_cases": [
    {"input": "horse\nros", "expected_output": "3"},
    {"input": "intention\nexecution", "expected_output": "5"},
    {"input": "a\nb", "expected_output": "1"},
    {"input": "\nabc", "expected_output": "3"}
  ]
}
```

**Output:**
```json
{
  "evaluation_id": "eval_003",
  "submission_id": "sub_003",
  "test_case_results": [
    {
      "test_case_id": 1,
      "passed": true,
      "expected": "3",
      "actual": "3",
      "execution_time_ms": 12
    },
    {
      "test_case_id": 2,
      "passed": true,
      "expected": "5",
      "actual": "5",
      "execution_time_ms": 15
    },
    {
      "test_case_id": 3,
      "passed": true,
      "expected": "1",
      "actual": "1",
      "execution_time_ms": 10
    },
    {
      "test_case_id": 4,
      "passed": true,
      "expected": "3",
      "actual": "3",
      "execution_time_ms": 11
    }
  ],
  "test_case_score": 100,
  "ai_quality_assessment": {
    "readability": 92,
    "efficiency": 88,
    "best_practices": 94,
    "overall_quality_score": 91
  },
  "complexity_analysis": {
    "time_complexity": "O(m*n)",
    "space_complexity": "O(m*n)",
    "complexity_score": 85
  },
  "final_score": 92,
  "winner_indicator": "excellent",
  "feedback": "Excellent DP solution with clear logic. Space can be optimized to O(n) using rolling array.",
  "evaluated_at": "2026-02-25T19:10:00Z"
}
```

**Metadata:**
```json
{
  "execution_time_total_ms": 48,
  "memory_used_mb": 45,
  "code_quality": {
    "has_comments": false,
    "follows_conventions": true,
    "uses_built_ins": false,
    "is_readable": true
  },
  "optimization_suggestions": [
    "Space optimization: Use rolling array to reduce space to O(n)",
    "Consider memoization approach for smaller inputs"
  ],
  "feedback": "Advanced solution demonstrating strong DP understanding"
}
```

---

## Scoring Criteria

### 1. Test Case Score (Primary - 50%)
- Percentage of test cases passed
- 100 = all tests pass, 0 = no tests pass

### 2. AI Quality Score (Secondary - 30%)
- **Readability** (0-100): Code clarity and structure
- **Efficiency** (0-100): Algorithmic efficiency
- **Best Practices** (0-100): Language conventions and patterns
- Overall = weighted average

### 3. Complexity Score (Tertiary - 20%)
- **Time Complexity**: Optimal vs actual
- **Space Complexity**: Optimal vs actual
- Score based on how close to optimal

## Final Score Calculation

```
final_score = (test_case_score * 0.5) + (quality_score * 0.3) + (complexity_score * 0.2)
```

## Winner Determination

1. Compare test_case_score (highest wins)
2. If tied: Compare quality_score
3. If tied: Compare complexity_score
4. If all tied: Earlier submission wins

## Next Steps

- Collect more evaluation examples across all problem types
- Train transformer model for code quality assessment
- Implement complexity analysis engine
- Build feedback generation system
- Create optimization suggestion engine
