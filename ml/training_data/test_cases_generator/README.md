# Test Cases Generator - Training Data

## Overview
Training data for the AI model that generates comprehensive test cases for coding challenges. Test cases must be valid, diverse, and cover edge cases.

## Data Format

Each training example contains:
- **input**: Problem statement and constraints
- **output**: Generated test cases with expected outputs
- **metadata**: Coverage metrics, edge case analysis

## Example Logs

### Example 1: Array Sum - Test Cases

**Input:**
```json
{
  "problem_id": "prob_001",
  "title": "Find the Sum of Array Elements",
  "constraints": {
    "array_size": "1 ≤ n ≤ 100",
    "element_range": "-1000 ≤ each element ≤ 1000"
  }
}
```

**Output:**
```json
{
  "test_suite_id": "ts_001",
  "problem_id": "prob_001",
  "test_cases": [
    {
      "test_case_id": "tc_001",
      "input": "5\n1 2 3 4 5",
      "expected_output": "15",
      "category": "basic",
      "description": "Simple positive numbers"
    },
    {
      "test_case_id": "tc_002",
      "input": "1\n42",
      "expected_output": "42",
      "category": "edge_case",
      "description": "Single element array"
    },
    {
      "test_case_id": "tc_003",
      "input": "5\n-1 -2 -3 -4 -5",
      "expected_output": "-15",
      "category": "edge_case",
      "description": "All negative numbers"
    },
    {
      "test_case_id": "tc_004",
      "input": "6\n-5 -3 0 2 4 6",
      "expected_output": "4",
      "category": "mixed",
      "description": "Mix of positive, negative, and zero"
    },
    {
      "test_case_id": "tc_005",
      "input": "3\n1000 1000 1000",
      "expected_output": "3000",
      "category": "boundary",
      "description": "Maximum element values"
    },
    {
      "test_case_id": "tc_006",
      "input": "3\n-1000 -1000 -1000",
      "expected_output": "-3000",
      "category": "boundary",
      "description": "Minimum element values"
    },
    {
      "test_case_id": "tc_007",
      "input": "100\n1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
      "expected_output": "100",
      "category": "boundary",
      "description": "Maximum array size"
    }
  ],
  "coverage_metrics": {
    "edge_cases_covered": 7,
    "boundary_cases_covered": 3,
    "basic_cases_covered": 1,
    "coverage_score": 0.98
  },
  "generated_at": "2026-02-25T18:45:00Z"
}
```

**Metadata:**
```json
{
  "total_test_cases": 7,
  "categories": {
    "basic": 1,
    "edge_case": 2,
    "mixed": 1,
    "boundary": 3
  },
  "quality_score": 0.96,
  "feedback": "Comprehensive test suite covering all edge cases and boundaries"
}
```

---

### Example 2: Longest Palindromic Substring - Test Cases

**Input:**
```json
{
  "problem_id": "prob_002",
  "title": "Longest Palindromic Substring",
  "constraints": {
    "string_length": "1 ≤ length ≤ 1000",
    "characters": "lowercase English letters only"
  }
}
```

**Output:**
```json
{
  "test_suite_id": "ts_002",
  "problem_id": "prob_002",
  "test_cases": [
    {
      "test_case_id": "tc_001",
      "input": "babad",
      "expected_output": "bab",
      "category": "basic",
      "description": "Odd-length palindrome"
    },
    {
      "test_case_id": "tc_002",
      "input": "cbbd",
      "expected_output": "bb",
      "category": "basic",
      "description": "Even-length palindrome"
    },
    {
      "test_case_id": "tc_003",
      "input": "a",
      "expected_output": "a",
      "category": "edge_case",
      "description": "Single character"
    },
    {
      "test_case_id": "tc_004",
      "input": "ac",
      "expected_output": "a",
      "category": "edge_case",
      "description": "No palindrome longer than 1"
    },
    {
      "test_case_id": "tc_005",
      "input": "racecar",
      "expected_output": "racecar",
      "category": "edge_case",
      "description": "Entire string is palindrome"
    },
    {
      "test_case_id": "tc_006",
      "input": "abcdefedcba",
      "expected_output": "abcdefedcba",
      "category": "boundary",
      "description": "Long palindrome"
    },
    {
      "test_case_id": "tc_007",
      "input": "abcdefghijklmnopqrstuvwxyz",
      "expected_output": "a",
      "category": "boundary",
      "description": "No palindrome (all unique characters)"
    },
    {
      "test_case_id": "tc_008",
      "input": "aaaaaaaaaa",
      "expected_output": "aaaaaaaaaa",
      "category": "boundary",
      "description": "All same characters"
    }
  ],
  "coverage_metrics": {
    "odd_length_palindromes": 1,
    "even_length_palindromes": 1,
    "single_character": 1,
    "no_palindrome": 1,
    "full_string_palindrome": 2,
    "coverage_score": 0.95
  },
  "generated_at": "2026-02-25T18:50:00Z"
}
```

**Metadata:**
```json
{
  "total_test_cases": 8,
  "categories": {
    "basic": 2,
    "edge_case": 3,
    "boundary": 3
  },
  "quality_score": 0.94,
  "feedback": "Good coverage of odd/even palindromes and edge cases"
}
```

---

### Example 3: Edit Distance - Test Cases

**Input:**
```json
{
  "problem_id": "prob_003",
  "title": "Edit Distance",
  "constraints": {
    "string_length": "0 ≤ length ≤ 500",
    "characters": "lowercase English letters only"
  }
}
```

**Output:**
```json
{
  "test_suite_id": "ts_003",
  "problem_id": "prob_003",
  "test_cases": [
    {
      "test_case_id": "tc_001",
      "input": "horse\nros",
      "expected_output": "3",
      "category": "basic",
      "description": "Standard case with substitutions and deletions"
    },
    {
      "test_case_id": "tc_002",
      "input": "intention\nexecution",
      "expected_output": "5",
      "category": "basic",
      "description": "Multiple operations needed"
    },
    {
      "test_case_id": "tc_003",
      "input": "a\nb",
      "expected_output": "1",
      "category": "edge_case",
      "description": "Single character replacement"
    },
    {
      "test_case_id": "tc_004",
      "input": "\nabc",
      "expected_output": "3",
      "category": "edge_case",
      "description": "Empty source string (all insertions)"
    },
    {
      "test_case_id": "tc_005",
      "input": "abc\n",
      "expected_output": "3",
      "category": "edge_case",
      "description": "Empty target string (all deletions)"
    },
    {
      "test_case_id": "tc_006",
      "input": "abc\nabc",
      "expected_output": "0",
      "category": "edge_case",
      "description": "Identical strings"
    },
    {
      "test_case_id": "tc_007",
      "input": "abc\nxyz",
      "expected_output": "3",
      "category": "boundary",
      "description": "Completely different strings (all replacements)"
    },
    {
      "test_case_id": "tc_008",
      "input": "abcdefghij\nfedcbahgij",
      "expected_output": "6",
      "category": "boundary",
      "description": "Longer strings with mixed operations"
    }
  ],
  "coverage_metrics": {
    "insertions": 1,
    "deletions": 1,
    "replacements": 1,
    "mixed_operations": 2,
    "identical_strings": 1,
    "empty_strings": 2,
    "coverage_score": 0.97
  },
  "generated_at": "2026-02-25T18:55:00Z"
}
```

**Metadata:**
```json
{
  "total_test_cases": 8,
  "categories": {
    "basic": 2,
    "edge_case": 4,
    "boundary": 2
  },
  "quality_score": 0.96,
  "feedback": "Excellent coverage of all three operations and edge cases"
}
```

---

## Test Case Categories

1. **Basic Cases**: Standard inputs that demonstrate core functionality
2. **Edge Cases**: Boundary conditions and special cases
3. **Boundary Cases**: Minimum and maximum constraint values
4. **Mixed Cases**: Combinations of different input types

## Coverage Metrics

- **Edge Case Coverage**: Percentage of edge cases covered
- **Boundary Coverage**: Percentage of boundary conditions tested
- **Operation Coverage**: For algorithms, coverage of different operation types
- **Overall Coverage Score**: Weighted average of all metrics

## Next Steps

- Collect more test cases across all problem domains
- Implement automated test case generation using constraint solving
- Create test case mutation engine for robustness testing
- Build feedback loop to improve test case quality based on player solutions
