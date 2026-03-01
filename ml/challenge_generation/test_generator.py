"""
Test script for test case generator
Run this to verify the generator works correctly
"""

import os
import json
from test_case_generator import TestCaseGenerator


def test_basic_generation():
    """Test basic test case generation"""
    
    # Initialize generator
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set in environment")
        return False
    
    generator = TestCaseGenerator(api_key=api_key)
    
    # Test case 1: Array sum
    print("\n=== Test 1: Array Sum Challenge ===")
    try:
        test_suite = generator.generate_test_cases(
            problem_id="test_001",
            title="Sum of Array Elements",
            description="Given an array of integers, calculate the sum of all elements.",
            constraints={
                "array_size": "1 ≤ n ≤ 100",
                "element_range": "-1000 ≤ each element ≤ 1000"
            },
            input_format="First line: integer n (array size)\nSecond line: n space-separated integers",
            output_format="Single integer: sum of all elements",
            example_input="5\n1 2 3 4 5",
            example_output="15",
            num_test_cases=8
        )
        
        print(f"✓ Generated {len(test_suite.test_cases)} test cases")
        print(f"✓ Coverage score: {test_suite.coverage_metrics['coverage_score']}")
        print(f"✓ Categories: {test_suite.coverage_metrics['categories']}")
        
        # Validate
        is_valid = generator.validate_test_suite(test_suite)
        print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Show first test case
        if test_suite.test_cases:
            tc = test_suite.test_cases[0]
            print(f"\nSample test case:")
            print(f"  Category: {tc.category}")
            print(f"  Description: {tc.description}")
            print(f"  Input: {tc.input[:50]}...")
            print(f"  Expected: {tc.expected_output}")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_string_challenge():
    """Test with string manipulation challenge"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    generator = TestCaseGenerator(api_key=api_key)
    
    print("\n=== Test 2: Palindrome Challenge ===")
    try:
        test_suite = generator.generate_test_cases(
            problem_id="test_002",
            title="Longest Palindromic Substring",
            description="Given a string s, return the longest palindromic substring in s.",
            constraints={
                "string_length": "1 ≤ length ≤ 1000",
                "characters": "lowercase English letters only"
            },
            input_format="Single line: string s",
            output_format="Single line: longest palindromic substring",
            example_input="babad",
            example_output="bab",
            num_test_cases=8
        )
        
        print(f"✓ Generated {len(test_suite.test_cases)} test cases")
        print(f"✓ Coverage score: {test_suite.coverage_metrics['coverage_score']}")
        
        is_valid = generator.validate_test_suite(test_suite)
        print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_export_json():
    """Test JSON export functionality"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    generator = TestCaseGenerator(api_key=api_key)
    
    print("\n=== Test 3: JSON Export ===")
    try:
        test_suite = generator.generate_test_cases(
            problem_id="test_003",
            title="Two Sum",
            description="Find two numbers that add up to target",
            constraints={"array_size": "2 ≤ n ≤ 1000"},
            input_format="Array and target",
            output_format="Two indices",
            num_test_cases=6
        )
        
        # Convert to dict
        suite_dict = generator.to_dict(test_suite)
        
        # Export to JSON
        json_str = json.dumps(suite_dict, indent=2)
        print(f"✓ Exported to JSON ({len(json_str)} bytes)")
        print(f"✓ Test suite ID: {suite_dict['test_suite_id']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Test Case Generator")
    print("=" * 50)
    
    results = []
    results.append(("Basic Generation", test_basic_generation()))
    results.append(("String Challenge", test_string_challenge()))
    results.append(("JSON Export", test_export_json()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed"))
