"""
Test script for problem statement generator
Run this to verify the generator works correctly
"""

import os
import json
from problem_statement_generator import ProblemStatementGenerator


def test_beginner_problem():
    """Test beginner level problem generation"""
    
    print("\n=== Test 1: Beginner Level - Arrays ===")
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY not set in environment")
            return False
        
        generator = ProblemStatementGenerator(api_key=api_key)
        
        # Generate beginner problem
        problem = generator.generate_problem_statement(
            problem_id="test_beginner_001",
            elo_rating=1100,
            domain="arrays",
            include_hints=True
        )
        
        print(f"✓ Generated problem: {problem.title}")
        print(f"✓ Difficulty score: {problem.difficulty_score}")
        print(f"✓ Domain: {problem.domain}")
        print(f"✓ Estimated success rate: {problem.estimated_success_rate}")
        
        # Validate
        is_valid = generator.validate_problem_statement(problem)
        print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Show details
        print(f"\nProblem Details:")
        print(f"  Title: {problem.title}")
        print(f"  Description: {problem.description[:100]}...")
        print(f"  Constraints: {len(problem.constraints)} constraints")
        print(f"  Example Input: {problem.example_input[:50]}...")
        print(f"  Example Output: {problem.example_output}")
        if problem.hints:
            print(f"  Hints: {len(problem.hints)} hints provided")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intermediate_problem():
    """Test intermediate level problem generation"""
    
    print("\n=== Test 2: Intermediate Level - Strings ===")
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        generator = ProblemStatementGenerator(api_key=api_key)
        
        # Generate intermediate problem
        problem = generator.generate_problem_statement(
            problem_id="test_intermediate_001",
            elo_rating=1350,
            domain="strings",
            include_hints=False
        )
        
        print(f"✓ Generated problem: {problem.title}")
        print(f"✓ Difficulty score: {problem.difficulty_score}")
        print(f"✓ Domain: {problem.domain}")
        
        # Validate
        is_valid = generator.validate_problem_statement(problem)
        print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Show details
        print(f"\nProblem Details:")
        print(f"  Title: {problem.title}")
        print(f"  Description length: {len(problem.description)} chars")
        print(f"  Input spec: {problem.input_specification[:60]}...")
        print(f"  Output spec: {problem.output_specification[:60]}...")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_advanced_problem():
    """Test advanced level problem generation"""
    
    print("\n=== Test 3: Advanced Level - Dynamic Programming ===")
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        generator = ProblemStatementGenerator(api_key=api_key)
        
        # Generate advanced problem
        problem = generator.generate_problem_statement(
            problem_id="test_advanced_001",
            elo_rating=1650,
            domain="dynamic_programming",
            difficulty_level="advanced"
        )
        
        print(f"✓ Generated problem: {problem.title}")
        print(f"✓ Difficulty score: {problem.difficulty_score}")
        print(f"✓ Estimated success rate: {problem.estimated_success_rate}")
        
        # Validate
        is_valid = generator.validate_problem_statement(problem)
        print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_problem_variations():
    """Test problem variation generation"""
    
    print("\n=== Test 4: Problem Variations ===")
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        generator = ProblemStatementGenerator(api_key=api_key)
        
        # Generate base problem
        print("Generating base problem...")
        base_problem = generator.generate_problem_statement(
            problem_id="test_base_001",
            elo_rating=1200,
            domain="arrays"
        )
        print(f"✓ Base problem: {base_problem.title}")
        
        # Generate variations
        print("\nGenerating variations...")
        variations = generator.generate_variations(base_problem, num_variations=2)
        
        print(f"✓ Generated {len(variations)} variations")
        for i, var in enumerate(variations, 1):
            print(f"  Variation {i}: {var.title}")
        
        return len(variations) > 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_json_export():
    """Test JSON export functionality"""
    
    print("\n=== Test 5: JSON Export ===")
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        generator = ProblemStatementGenerator(api_key=api_key)
        
        # Generate problem
        problem = generator.generate_problem_statement(
            problem_id="test_export_001",
            elo_rating=1300,
            domain="linked_lists"
        )
        
        # Convert to dict
        problem_dict = generator.to_dict(problem)
        
        # Export to JSON
        json_str = json.dumps(problem_dict, indent=2)
        print(f"✓ Exported to JSON ({len(json_str)} bytes)")
        print(f"✓ Problem ID: {problem_dict['problem_id']}")
        print(f"✓ Title: {problem_dict['title']}")
        
        # Verify all fields present
        required_fields = [
            'problem_id', 'title', 'description', 'input_specification',
            'output_specification', 'example_input', 'example_output',
            'constraints', 'difficulty_score', 'domain'
        ]
        
        all_present = all(field in problem_dict for field in required_fields)
        print(f"✓ All required fields: {'PRESENT' if all_present else 'MISSING'}")
        
        return all_present
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_all_domains():
    """Test problem generation across all domains"""
    
    print("\n=== Test 6: All Domains ===")
    
    domains = [
        "arrays", "strings", "linked_lists", "trees", 
        "graphs", "dynamic_programming", "sorting", "searching"
    ]
    
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        generator = ProblemStatementGenerator(api_key=api_key)
        
        success_count = 0
        
        for domain in domains:
            try:
                problem = generator.generate_problem_statement(
                    problem_id=f"test_{domain}_001",
                    elo_rating=1300,
                    domain=domain
                )
                print(f"✓ {domain}: {problem.title}")
                success_count += 1
            except Exception as e:
                print(f"✗ {domain}: Failed - {e}")
        
        print(f"\n✓ Successfully generated {success_count}/{len(domains)} domains")
        return success_count >= len(domains) * 0.8  # 80% success rate
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Problem Statement Generator")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Beginner Problem", test_beginner_problem()))
    
    print("\n")
    input("Press Enter to continue to next test...")
    results.append(("Intermediate Problem", test_intermediate_problem()))
    
    print("\n")
    input("Press Enter to continue to next test...")
    results.append(("Advanced Problem", test_advanced_problem()))
    
    print("\n")
    input("Press Enter to continue to next test...")
    results.append(("Problem Variations", test_problem_variations()))
    
    print("\n")
    input("Press Enter to continue to next test...")
    results.append(("JSON Export", test_json_export()))
    
    print("\n")
    input("Press Enter to test all domains (will make 8 API calls)...")
    results.append(("All Domains", test_all_domains()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results:")
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed"))
