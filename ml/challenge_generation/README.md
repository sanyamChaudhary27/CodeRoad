# Test Case Generator - AI-Powered Challenge Generation

## Overview

This module provides AI-powered test case generation for coding challenges using Claude (Anthropic). It generates comprehensive test suites covering edge cases, boundary conditions, and standard cases.

## Features

- **AI-Generated Test Cases**: Uses Claude 3.5 Sonnet to generate diverse test cases
- **Comprehensive Coverage**: Automatically generates basic, edge, boundary, and mixed test cases
- **Validation**: Built-in validation to ensure test suite quality
- **Flexible**: Supports any coding challenge with customizable constraints
- **Fast**: Generates 8+ test cases in ~3-5 seconds

## Installation

```bash
# Install dependencies
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start

```python
from ml.challenge_generation import TestCaseGenerator

# Initialize generator
generator = TestCaseGenerator()

# Generate test cases
test_suite = generator.generate_test_cases(
    problem_id="prob_001",
    title="Sum of Array Elements",
    description="Calculate the sum of all array elements",
    constraints={
        "array_size": "1 ≤ n ≤ 100",
        "element_range": "-1000 ≤ each element ≤ 1000"
    },
    input_format="First line: n\nSecond line: n integers",
    output_format="Single integer: sum",
    example_input="5\n1 2 3 4 5",
    example_output="15",
    num_test_cases=8
)

# Validate test suite
is_valid = generator.validate_test_suite(test_suite)
print(f"Valid: {is_valid}")

# Access test cases
for tc in test_suite.test_cases:
    print(f"{tc.category}: {tc.description}")
    print(f"  Input: {tc.input}")
    print(f"  Expected: {tc.expected_output}")
```

## Integration with Backend

The test case generator is integrated into the Challenge Service:

```python
from backend.app.services.challenge_service import get_challenge_service

# Get service instance
service = get_challenge_service()

# Generate complete challenge with test cases
challenge = service.generate_challenge(
    difficulty="intermediate",
    player_rating=1200,
    domain="arrays"
)

# Challenge includes:
# - Problem statement
# - Constraints
# - AI-generated test cases
# - Coverage metrics
```

## API Endpoint

```bash
# Generate challenge via API
curl -X POST http://localhost:8000/api/challenges/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "intermediate",
    "domain": "arrays"
  }'
```

## Test Case Categories

1. **Basic Cases**: Standard inputs demonstrating core functionality
2. **Edge Cases**: Boundary conditions (empty, single element, etc.)
3. **Boundary Cases**: Min/max constraint values
4. **Mixed Cases**: Combinations of different input types

## Coverage Metrics

The generator calculates coverage metrics:

```python
{
    "total_test_cases": 8,
    "categories": {
        "basic": 2,
        "edge_case": 3,
        "boundary": 2,
        "mixed": 1
    },
    "coverage_score": 0.95,
    "edge_cases_covered": 3,
    "boundary_cases_covered": 2,
    "basic_cases_covered": 2
}
```

## Validation Rules

A valid test suite must have:
- At least 5 test cases
- At least 1 edge case
- At least 1 boundary case
- Coverage score ≥ 0.6

## Testing

Run the test script to verify functionality:

```bash
cd ml/challenge_generation
python test_generator.py
```

Expected output:
```
Testing Test Case Generator
==================================================
=== Test 1: Array Sum Challenge ===
✓ Generated 8 test cases
✓ Coverage score: 0.95
✓ Validation: PASSED

=== Test 2: Palindrome Challenge ===
✓ Generated 8 test cases
✓ Coverage score: 0.90
✓ Validation: PASSED

=== Test 3: JSON Export ===
✓ Exported to JSON (2456 bytes)
✓ Test suite ID: ts_test_003

==================================================
Test Results:
  ✓ PASS: Basic Generation
  ✓ PASS: String Challenge
  ✓ PASS: JSON Export

All tests passed!
```

## Architecture

```
TestCaseGenerator
├── generate_test_cases()    # Main generation method
├── validate_test_suite()    # Quality validation
├── to_dict()                # JSON serialization
└── _build_prompt()          # LLM prompt construction

ChallengeService
├── generate_challenge()     # Complete challenge generation
├── adapt_difficulty()       # Adaptive difficulty
└── CHALLENGE_TEMPLATES      # Problem templates
```

## Performance

- Generation time: ~3-5 seconds per challenge
- API calls: 1 per challenge generation
- Token usage: ~1000-2000 tokens per generation
- Cost: ~$0.01-0.02 per challenge (Claude 3.5 Sonnet)

## Fallback Behavior

If AI generation fails:
1. Service logs warning
2. Falls back to example test case
3. Challenge still usable but with limited test coverage
4. Recommended: Monitor logs and fix API issues

## Future Enhancements

- [ ] Cache generated test suites
- [ ] Support for multiple programming languages
- [ ] Test case mutation for robustness
- [ ] Difficulty calibration based on player performance
- [ ] Automated test case execution validation
- [ ] Support for custom test case templates

## Troubleshooting

**API Key Error**:
```
ValueError: ANTHROPIC_API_KEY not found in environment
```
Solution: Set `ANTHROPIC_API_KEY` environment variable

**JSON Parse Error**:
```
ValueError: Failed to parse LLM response as JSON
```
Solution: Check API response format, may need to adjust prompt

**Validation Failed**:
```
WARNING: Generated test suite failed validation
```
Solution: Increase `num_test_cases` or adjust validation thresholds

## License

Part of Code Road platform - Prototype Development Phase
