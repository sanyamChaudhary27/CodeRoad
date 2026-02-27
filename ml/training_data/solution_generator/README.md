# Solution Generator - Training Data

## Overview
Training data for the AI model that generates reference solutions for coding challenges. Used for validation and as examples for players.

## Data Format

Each training example contains:
- **input**: Problem statement and constraints
- **output**: Reference solution code
- **metadata**: Language, complexity analysis, quality metrics

## Example Logs

### Example 1: Array Sum - Python Solution

**Input:**
```json
{
  "problem_id": "prob_001",
  "title": "Find the Sum of Array Elements",
  "description": "Given an array of integers, write a function that returns the sum of all elements in the array.",
  "language": "python",
  "difficulty_level": "beginner"
}
```

**Output:**
```json
{
  "solution_id": "sol_001",
  "problem_id": "prob_001",
  "language": "python",
  "code": "def array_sum(n, arr):\n    \"\"\"\n    Calculate the sum of all elements in an array.\n    \n    Args:\n        n: Number of elements\n        arr: List of integers\n    \n    Returns:\n        Sum of all elements\n    \"\"\"\n    total = 0\n    for num in arr:\n        total += num\n    return total\n\n# Alternative: Using built-in sum()\n# return sum(arr)\n\n# Read input\nn = int(input())\narr = list(map(int, input().split()))\n\n# Calculate and print result\nprint(array_sum(n, arr))",
  "time_complexity": "O(n)",
  "space_complexity": "O(1)",
  "explanation": "Iterate through the array once, accumulating the sum. Time complexity is linear as we visit each element exactly once.",
  "quality_score": 0.95,
  "generated_at": "2026-02-25T18:30:00Z"
}
```

**Metadata:**
```json
{
  "test_cases_passed": 100,
  "execution_time_ms": 12,
  "memory_used_mb": 8,
  "code_quality": {
    "readability": 0.98,
    "efficiency": 0.95,
    "best_practices": 0.92
  },
  "feedback": "Clean, efficient solution with good documentation"
}
```

---

### Example 2: Longest Palindromic Substring - Python Solution

**Input:**
```json
{
  "problem_id": "prob_002",
  "title": "Longest Palindromic Substring",
  "description": "Given a string s, find the longest contiguous substring that is a palindrome.",
  "language": "python",
  "difficulty_level": "intermediate"
}
```

**Output:**
```json
{
  "solution_id": "sol_002",
  "problem_id": "prob_002",
  "language": "python",
  "code": "def longest_palindrome(s):\n    \"\"\"\n    Find the longest palindromic substring using expand-around-center approach.\n    \n    Args:\n        s: Input string\n    \n    Returns:\n        Longest palindromic substring\n    \"\"\"\n    if not s:\n        return \"\"\n    \n    def expand_around_center(left, right):\n        while left >= 0 and right < len(s) and s[left] == s[right]:\n            left -= 1\n            right += 1\n        return s[left + 1:right]\n    \n    longest = \"\"\n    for i in range(len(s)):\n        # Check for odd-length palindromes (single character center)\n        p1 = expand_around_center(i, i)\n        if len(p1) > len(longest):\n            longest = p1\n        \n        # Check for even-length palindromes (two character center)\n        p2 = expand_around_center(i, i + 1)\n        if len(p2) > len(longest):\n            longest = p2\n    \n    return longest\n\n# Read input\ns = input().strip()\nprint(longest_palindrome(s))",
  "time_complexity": "O(n²)",
  "space_complexity": "O(1)",
  "explanation": "Expand around each possible center (both single characters and pairs). For each center, expand outward while characters match. Time complexity is O(n²) as we have n centers and each expansion takes O(n) time.",
  "quality_score": 0.89,
  "generated_at": "2026-02-25T18:35:00Z"
}
```

**Metadata:**
```json
{
  "test_cases_passed": 98,
  "execution_time_ms": 145,
  "memory_used_mb": 12,
  "code_quality": {
    "readability": 0.88,
    "efficiency": 0.85,
    "best_practices": 0.90
  },
  "feedback": "Good solution with clear explanation. Could optimize with Manacher's algorithm for O(n) time."
}
```

---

### Example 3: Edit Distance - Python Solution

**Input:**
```json
{
  "problem_id": "prob_003",
  "title": "Edit Distance (Levenshtein Distance)",
  "description": "Given two strings, return the minimum number of operations required to convert word1 to word2.",
  "language": "python",
  "difficulty_level": "advanced"
}
```

**Output:**
```json
{
  "solution_id": "sol_003",
  "problem_id": "prob_003",
  "language": "python",
  "code": "def edit_distance(word1, word2):\n    \"\"\"\n    Calculate minimum edit distance using dynamic programming.\n    \n    Args:\n        word1: Source string\n        word2: Target string\n    \n    Returns:\n        Minimum number of operations (insert, delete, replace)\n    \"\"\"\n    m, n = len(word1), len(word2)\n    \n    # Create DP table\n    dp = [[0] * (n + 1) for _ in range(m + 1)]\n    \n    # Initialize base cases\n    for i in range(m + 1):\n        dp[i][0] = i  # Delete all characters from word1\n    for j in range(n + 1):\n        dp[0][j] = j  # Insert all characters to get word2\n    \n    # Fill DP table\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if word1[i - 1] == word2[j - 1]:\n                # Characters match, no operation needed\n                dp[i][j] = dp[i - 1][j - 1]\n            else:\n                # Take minimum of three operations\n                dp[i][j] = 1 + min(\n                    dp[i - 1][j],      # Delete from word1\n                    dp[i][j - 1],      # Insert into word1\n                    dp[i - 1][j - 1]   # Replace\n                )\n    \n    return dp[m][n]\n\n# Read input\nword1 = input().strip()\nword2 = input().strip()\nprint(edit_distance(word1, word2))",
  "time_complexity": "O(m*n)",
  "space_complexity": "O(m*n)",
  "explanation": "Use dynamic programming with a 2D table where dp[i][j] represents the edit distance between the first i characters of word1 and first j characters of word2. Fill the table bottom-up using the recurrence relation.",
  "quality_score": 0.93,
  "generated_at": "2026-02-25T18:40:00Z"
}
```

**Metadata:**
```json
{
  "test_cases_passed": 100,
  "execution_time_ms": 234,
  "memory_used_mb": 45,
  "code_quality": {
    "readability": 0.92,
    "efficiency": 0.88,
    "best_practices": 0.95
  },
  "feedback": "Excellent DP solution with clear explanation. Space can be optimized to O(n) using rolling array."
}
```

---

## Training Process

1. **Solution Collection**: Gather reference solutions for all problems
2. **Code Analysis**: Extract complexity metrics and quality scores
3. **Model Training**: Train code generation model on solutions
4. **Validation**: Verify solutions pass all test cases
5. **Optimization**: Identify and document optimization opportunities
6. **Feedback**: Use player solutions to improve generation

## Quality Metrics

- **Correctness**: Does solution pass all test cases?
- **Efficiency**: Time and space complexity analysis
- **Readability**: Code clarity and documentation
- **Best Practices**: Follows language conventions and patterns

## Next Steps

- Collect solutions in multiple languages (Python, Java, C++, JavaScript)
- Fine-tune code generation model on domain-specific solutions
- Implement code quality scoring system
- Create optimization suggestion engine
