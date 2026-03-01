"""
Test Case Generator - AI-powered test case generation for coding challenges
Uses LLM to generate comprehensive test cases covering edge cases and boundaries
"""

import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


@dataclass
class TestCase:
    """Individual test case with input and expected output"""
    test_case_id: str
    input: str
    expected_output: str
    category: str  # basic, edge_case, boundary, mixed
    description: str


@dataclass
class TestSuite:
    """Complete test suite for a challenge"""
    test_suite_id: str
    problem_id: str
    test_cases: List[TestCase]
    coverage_metrics: Dict[str, Any]
    generated_at: str


class TestCaseGenerator:
    """Generate test cases using AI for coding challenges"""
    
    def __init__(self, api_key: str = None, provider: str = None):
        """
        Initialize with API key from env or parameter
        
        Args:
            api_key: API key (if None, will use env variable)
            provider: "anthropic" or "gemini" (if None, checks AI_PROVIDER env var, defaults to gemini)
        """
        self.provider = (provider or os.getenv("AI_PROVIDER", "gemini")).lower()
        
        if self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai not installed. Install with: pip install google-generativeai")
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel("gemini-1.5-pro")
        else:  # anthropic
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_test_cases(
        self,
        problem_id: str,
        title: str,
        description: str,
        constraints: Dict[str, str],
        input_format: str,
        output_format: str,
        example_input: str = None,
        example_output: str = None,
        num_test_cases: int = 8
    ) -> TestSuite:
        """
        Generate comprehensive test cases for a coding challenge
        
        Args:
            problem_id: Unique problem identifier
            title: Problem title
            description: Problem description
            constraints: Dict of constraint descriptions
            input_format: Description of input format
            output_format: Description of output format
            example_input: Optional example input
            example_output: Optional example output
            num_test_cases: Number of test cases to generate (default 8)
        
        Returns:
            TestSuite with generated test cases
        """
        
        prompt = self._build_prompt(
            title, description, constraints, input_format, output_format,
            example_input, example_output, num_test_cases
        )
        
        if self.provider == "gemini":
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=4000,
                    temperature=0.7
                )
            )
            response_text = response.text
        else:  # anthropic
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            response_text = response.content[0].text
        
        # Parse response
        test_cases_data = self._parse_response(response_text)
        
        # Build test suite
        test_cases = []
        for i, tc_data in enumerate(test_cases_data):
            test_cases.append(TestCase(
                test_case_id=f"tc_{i+1:03d}",
                input=tc_data["input"],
                expected_output=tc_data["expected_output"],
                category=tc_data.get("category", "basic"),
                description=tc_data.get("description", "")
            ))
        
        # Calculate coverage metrics
        coverage = self._calculate_coverage(test_cases)
        
        from datetime import datetime
        test_suite = TestSuite(
            test_suite_id=f"ts_{problem_id}",
            problem_id=problem_id,
            test_cases=test_cases,
            coverage_metrics=coverage,
            generated_at=datetime.utcnow().isoformat() + "Z"
        )
        
        return test_suite
    
    def _build_prompt(
        self,
        title: str,
        description: str,
        constraints: Dict[str, str],
        input_format: str,
        output_format: str,
        example_input: str,
        example_output: str,
        num_test_cases: int
    ) -> str:
        """Build prompt for LLM to generate test cases"""
        
        constraints_str = "\n".join([f"- {k}: {v}" for k, v in constraints.items()])
        
        example_section = ""
        if example_input and example_output:
            example_section = f"""
Example:
Input: {example_input}
Output: {example_output}
"""
        
        prompt = f"""Generate {num_test_cases} comprehensive test cases for the following coding challenge.

Problem: {title}

Description: {description}

Constraints:
{constraints_str}

Input Format: {input_format}
Output Format: {output_format}
{example_section}

Generate test cases that cover:
1. Basic cases (2-3): Standard inputs demonstrating core functionality
2. Edge cases (2-3): Boundary conditions, empty inputs, single elements
3. Boundary cases (2-3): Minimum and maximum constraint values
4. Mixed cases (1-2): Combinations of different input types

For each test case, provide:
- input: The test input (use exact format specified)
- expected_output: The correct output
- category: One of [basic, edge_case, boundary, mixed]
- description: Brief explanation of what this test case validates

Return ONLY a valid JSON array of test cases in this exact format:
[
  {{
    "input": "test input here",
    "expected_output": "expected output here",
    "category": "basic",
    "description": "what this tests"
  }},
  ...
]

Do not include any markdown formatting, code blocks, or explanatory text. Return only the raw JSON array."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse LLM response into test case data"""
        
        # Clean response - remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```"):
            # Remove markdown code block markers
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
            text = text.replace("```json", "").replace("```", "").strip()
        
        try:
            test_cases = json.loads(text)
            return test_cases
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {text}")
    
    def _calculate_coverage(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Calculate coverage metrics for test suite"""
        
        categories = {}
        for tc in test_cases:
            categories[tc.category] = categories.get(tc.category, 0) + 1
        
        # Simple coverage score based on category distribution
        has_basic = categories.get("basic", 0) > 0
        has_edge = categories.get("edge_case", 0) > 0
        has_boundary = categories.get("boundary", 0) > 0
        has_mixed = categories.get("mixed", 0) > 0
        
        coverage_score = (
            (0.25 if has_basic else 0) +
            (0.35 if has_edge else 0) +
            (0.30 if has_boundary else 0) +
            (0.10 if has_mixed else 0)
        )
        
        return {
            "total_test_cases": len(test_cases),
            "categories": categories,
            "coverage_score": round(coverage_score, 2),
            "edge_cases_covered": categories.get("edge_case", 0),
            "boundary_cases_covered": categories.get("boundary", 0),
            "basic_cases_covered": categories.get("basic", 0)
        }
    
    def validate_test_suite(self, test_suite: TestSuite) -> bool:
        """
        Validate that test suite meets minimum quality requirements
        
        Returns:
            True if valid, False otherwise
        """
        
        # Must have at least 5 test cases
        if len(test_suite.test_cases) < 5:
            return False
        
        # Must have at least one edge case
        if test_suite.coverage_metrics["edge_cases_covered"] < 1:
            return False
        
        # Must have at least one boundary case
        if test_suite.coverage_metrics["boundary_cases_covered"] < 1:
            return False
        
        # Coverage score must be at least 0.6
        if test_suite.coverage_metrics["coverage_score"] < 0.6:
            return False
        
        return True
    
    def to_dict(self, test_suite: TestSuite) -> Dict[str, Any]:
        """Convert test suite to dictionary for JSON serialization"""
        return {
            "test_suite_id": test_suite.test_suite_id,
            "problem_id": test_suite.problem_id,
            "test_cases": [asdict(tc) for tc in test_suite.test_cases],
            "coverage_metrics": test_suite.coverage_metrics,
            "generated_at": test_suite.generated_at
        }
