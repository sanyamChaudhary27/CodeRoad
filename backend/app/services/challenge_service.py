import logging
import uuid
import json
import random
import os
from datetime import datetime
from typing import Optional, Dict, List, Any, Set
from sqlalchemy.orm import Session
from ..models import Challenge

logger = logging.getLogger(__name__)

# Try to import Gemini for AI challenge generation
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed - AI challenge generation disabled")


class ChallengeService:
    """Robust challenge generation service with three-tier fallback strategy"""
    
    def __init__(self):
        """Initialize service with optional Gemini AI support"""
        self.ai_available = False
        self.gemini_model = None
        self._recently_used_titles: Set[str] = set()
        
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    # Try models in order of preference
                    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                    for model_name in model_names:
                        try:
                            self.gemini_model = genai.GenerativeModel(model_name)
                            # Test the model with a simple request
                            test_response = self.gemini_model.generate_content(
                                "Say 'OK'",
                                generation_config=genai.types.GenerationConfig(
                                    temperature=0.7,
                                    max_output_tokens=10,
                                ),
                                request_options={'timeout': 5}
                            )
                            if test_response and test_response.text:
                                self.ai_available = True
                                logger.info(f"Gemini AI initialized with model: {model_name}")
                                break
                        except Exception as e:
                            logger.debug(f"Model {model_name} not available: {e}")
                            continue
                    
                    if not self.ai_available:
                        logger.warning("No Gemini models available, using templates")
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini: {e}")
        
        self.templates = self._load_templates()
        # Difficulty -> list of valid template indices
        self._difficulty_indices = {
            'beginner': [i for i, t in enumerate(self.templates) if t['difficulty'] == 'beginner'],
            'intermediate': [i for i, t in enumerate(self.templates) if t['difficulty'] == 'intermediate'],
            'advanced': [i for i, t in enumerate(self.templates) if t['difficulty'] == 'advanced'],
        }
    
    def _load_templates(self) -> List[Dict]:
        """Load pre-built challenge templates"""
        return [
            {'title': 'Sum of Two Numbers', 'description': 'Write a function that takes two numbers and returns their sum.', 'difficulty': 'beginner', 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '-1000 ≤ x ≤ 1000'}, 'input_format': 'Two integers separated by space', 'output_format': 'Single integer (sum)', 'example_input': '5 3', 'example_output': '8', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(a, b):\n    # Write your code here\n    return 0', 'test_cases': [{'id': 'tc1', 'input': '5 3', 'expected_output': '8', 'category': 'basic', 'description': 'Basic addition', 'is_hidden': False}, {'id': 'tc2', 'input': '0 0', 'expected_output': '0', 'category': 'edge', 'description': 'Zero values', 'is_hidden': False}, {'id': 'tc3', 'input': '-5 3', 'expected_output': '-2', 'category': 'edge', 'description': 'Negative number', 'is_hidden': True}, {'id': 'tc4', 'input': '1000 1000', 'expected_output': '2000', 'category': 'boundary', 'description': 'Large values', 'is_hidden': True}]},
            {'title': 'Find Maximum in Array', 'description': 'Find the maximum element in an array of integers.', 'difficulty': 'beginner', 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '-1000 ≤ x ≤ 1000'}, 'input_format': 'Array of integers', 'output_format': 'Maximum value', 'example_input': '3 7 2 9 1', 'example_output': '9', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(arr):\n    # Write your code here\n    return 0', 'test_cases': [{'id': 'tc1', 'input': '3 7 2 9 1', 'expected_output': '9', 'category': 'basic', 'description': 'Basic max', 'is_hidden': False}, {'id': 'tc2', 'input': '5', 'expected_output': '5', 'category': 'edge', 'description': 'Single element', 'is_hidden': False}, {'id': 'tc3', 'input': '-5 -2 -10', 'expected_output': '-2', 'category': 'edge', 'description': 'All negative', 'is_hidden': True}, {'id': 'tc4', 'input': '1000 999 998', 'expected_output': '1000', 'category': 'boundary', 'description': 'Large values', 'is_hidden': True}]},
            {'title': 'Reverse a String', 'description': 'Reverse the given string.', 'difficulty': 'beginner', 'domain': 'strings', 'constraints': {'input_size': '1 ≤ n ≤ 100', 'character_set': 'ASCII'}, 'input_format': 'Single string', 'output_format': 'Reversed string', 'example_input': 'hello', 'example_output': 'olleh', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(s):\n    # Write your code here\n    return ""', 'test_cases': [{'id': 'tc1', 'input': 'hello', 'expected_output': 'olleh', 'category': 'basic', 'description': 'Basic reverse', 'is_hidden': False}, {'id': 'tc2', 'input': 'a', 'expected_output': 'a', 'category': 'edge', 'description': 'Single char', 'is_hidden': False}, {'id': 'tc3', 'input': '', 'expected_output': '', 'category': 'edge', 'description': 'Empty string', 'is_hidden': True}, {'id': 'tc4', 'input': 'racecar', 'expected_output': 'racecar', 'category': 'boundary', 'description': 'Palindrome', 'is_hidden': True}]},
            {'title': 'Two Sum Problem', 'description': 'Find two numbers in array that add up to target.', 'difficulty': 'intermediate', 'domain': 'arrays', 'constraints': {'input_size': '2 ≤ n ≤ 1000', 'value_range': '-10000 ≤ x ≤ 10000'}, 'input_format': 'Array and target sum', 'output_format': 'Indices of two numbers', 'example_input': '2 7 11 15 9', 'example_output': '0 1', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(arr, x):\n    # Write your code here\n    return [0, 1]', 'test_cases': [{'id': 'tc1', 'input': '2 7 11 15 9', 'expected_output': '0 1', 'category': 'basic', 'description': 'Basic two sum', 'is_hidden': False}, {'id': 'tc2', 'input': '3 3 6', 'expected_output': '0 1', 'category': 'edge', 'description': 'Duplicate values', 'is_hidden': False}, {'id': 'tc3', 'input': '-1 -2 -3 5 2', 'expected_output': '2 3', 'category': 'edge', 'description': 'Negative numbers', 'is_hidden': True}, {'id': 'tc4', 'input': '1 2 3 4 5 6 7 8 9 10 15', 'expected_output': '6 7', 'category': 'boundary', 'description': 'Large array', 'is_hidden': True}]},
            {'title': 'Palindrome Check', 'description': 'Check if a string is a palindrome. Ignore case, spaces, and punctuation (e.g., "A man a plan a canal Panama" is a palindrome).', 'difficulty': 'intermediate', 'domain': 'strings', 'constraints': {'input_size': '1 ≤ n ≤ 1000', 'character_set': 'ASCII'}, 'input_format': 'Single string', 'output_format': 'true or false', 'example_input': 'racecar', 'example_output': 'true', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(s):\n    # Write your code here\n    return True', 'test_cases': [{'id': 'tc1', 'input': 'racecar', 'expected_output': 'true', 'category': 'basic', 'description': 'Basic palindrome', 'is_hidden': False}, {'id': 'tc2', 'input': 'hello', 'expected_output': 'false', 'category': 'basic', 'description': 'Not palindrome', 'is_hidden': False}, {'id': 'tc3', 'input': 'a', 'expected_output': 'true', 'category': 'edge', 'description': 'Single char', 'is_hidden': True}, {'id': 'tc4', 'input': 'A man a plan a canal Panama', 'expected_output': 'true', 'category': 'boundary', 'description': 'With spaces', 'is_hidden': True}]},
            {'title': 'Merge Sorted Arrays', 'description': 'Merge two sorted arrays into one sorted array.', 'difficulty': 'intermediate', 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 1000', 'value_range': '-10000 ≤ x ≤ 10000'}, 'input_format': 'Two sorted arrays', 'output_format': 'Merged sorted array', 'example_input': '1 3 5 2 4 6', 'example_output': '1 2 3 4 5 6', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(arr1, arr2):\n    # Write your code here\n    return []', 'test_cases': [{'id': 'tc1', 'input': '1 3 5 2 4 6', 'expected_output': '1 2 3 4 5 6', 'category': 'basic', 'description': 'Basic merge', 'is_hidden': False}, {'id': 'tc2', 'input': '1 2 3', 'expected_output': '1 2 3', 'category': 'edge', 'description': 'One empty', 'is_hidden': False}, {'id': 'tc3', 'input': '-5 -2 1 -3 0 2', 'expected_output': '-5 -3 -2 0 1 2', 'category': 'edge', 'description': 'Negative numbers', 'is_hidden': True}, {'id': 'tc4', 'input': '1 1 1 1 1 1', 'expected_output': '1 1 1 1 1 1', 'category': 'boundary', 'description': 'Duplicates', 'is_hidden': True}]},
            {'title': 'Longest Substring Without Repeating', 'description': 'Find length of longest substring without repeating characters.', 'difficulty': 'advanced', 'domain': 'strings', 'constraints': {'input_size': '1 ≤ n ≤ 10000', 'character_set': 'ASCII'}, 'input_format': 'Single string', 'output_format': 'Integer (length)', 'example_input': 'abcabcbb', 'example_output': '3', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(s):\n    # Write your code here\n    return 0', 'test_cases': [{'id': 'tc1', 'input': 'abcabcbb', 'expected_output': '3', 'category': 'basic', 'description': 'Basic case', 'is_hidden': False}, {'id': 'tc2', 'input': 'bbbbb', 'expected_output': '1', 'category': 'edge', 'description': 'All same', 'is_hidden': False}, {'id': 'tc3', 'input': 'au', 'expected_output': '2', 'category': 'edge', 'description': 'No repeats', 'is_hidden': True}, {'id': 'tc4', 'input': 'dvdf', 'expected_output': '3', 'category': 'boundary', 'description': 'Complex pattern', 'is_hidden': True}]},
            {'title': 'Binary Tree Level Order Traversal', 'description': 'Return level order traversal of binary tree.', 'difficulty': 'advanced', 'domain': 'trees', 'constraints': {'input_size': '1 ≤ n ≤ 1000', 'tree_height': '1 ≤ h ≤ 100'}, 'input_format': 'Tree structure', 'output_format': 'Level order list', 'example_input': '[3,9,20,null,null,15,7]', 'example_output': '[[3],[9,20],[15,7]]', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(root):\n    # Write your code here\n    return []', 'test_cases': [{'id': 'tc1', 'input': '[3,9,20,null,null,15,7]', 'expected_output': '[[3],[9,20],[15,7]]', 'category': 'basic', 'description': 'Basic tree', 'is_hidden': False}, {'id': 'tc2', 'input': '[1]', 'expected_output': '[[1]]', 'category': 'edge', 'description': 'Single node', 'is_hidden': False}, {'id': 'tc3', 'input': '[1,2,3,4,5,6,7]', 'expected_output': '[[1],[2,3],[4,5,6,7]]', 'category': 'boundary', 'description': 'Complete tree', 'is_hidden': True}, {'id': 'tc4', 'input': '[1,2,null,3]', 'expected_output': '[[1],[2],[3]]', 'category': 'boundary', 'description': 'Skewed tree', 'is_hidden': True}]},
            {'title': 'Longest Increasing Subsequence', 'description': 'Find length of longest increasing subsequence.', 'difficulty': 'advanced', 'domain': 'dynamic_programming', 'constraints': {'input_size': '1 ≤ n ≤ 10000', 'value_range': '-10000 ≤ x ≤ 10000'}, 'input_format': 'Array of integers', 'output_format': 'Integer (length)', 'example_input': '10 9 2 5 3 7 101 18', 'example_output': '4', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(nums):\n    # Write your code here\n    return 0', 'test_cases': [{'id': 'tc1', 'input': '10 9 2 5 3 7 101 18', 'expected_output': '4', 'category': 'basic', 'description': 'Basic LIS', 'is_hidden': False}, {'id': 'tc2', 'input': '0 1 0 4 4 4 3 5 1', 'expected_output': '4', 'category': 'basic', 'description': 'Multiple options', 'is_hidden': False}, {'id': 'tc3', 'input': '5 4 3 2 1', 'expected_output': '1', 'category': 'edge', 'description': 'Decreasing', 'is_hidden': True}, {'id': 'tc4', 'input': '1 2 3 4 5', 'expected_output': '5', 'category': 'boundary', 'description': 'Increasing', 'is_hidden': True}]},
            {'title': 'FizzBuzz', 'description': 'Print numbers 1 to n. For multiples of 3 return Fizz. For multiples of 5 return Buzz. For both return FizzBuzz.', 'difficulty': 'beginner', 'domain': 'math', 'constraints': {'input_size': '1 ≤ n ≤ 10000'}, 'input_format': 'Single integer n', 'output_format': 'Array or space-separated list of strings', 'example_input': '5', 'example_output': '1 2 Fizz 4 Buzz', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(n):\n    # Write your code here\n    return []', 'test_cases': [{'id': 'tc1', 'input': '5', 'expected_output': '1 2 Fizz 4 Buzz', 'category': 'basic', 'description': 'Basic 5', 'is_hidden': False}, {'id': 'tc2', 'input': '15', 'expected_output': '1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz', 'category': 'basic', 'description': 'Up to 15', 'is_hidden': False}, {'id': 'tc3', 'input': '1', 'expected_output': '1', 'category': 'edge', 'description': 'Single number', 'is_hidden': True}]},
            {'title': 'Reverse Linked List', 'description': 'Reverse a singly linked list.', 'difficulty': 'intermediate', 'domain': 'linked_lists', 'constraints': {'input_size': '0 ≤ n ≤ 5000', 'value_range': '-5000 ≤ Node.val ≤ 5000'}, 'input_format': 'List of integers representing nodes', 'output_format': 'Reversed list of integers', 'example_input': '1 2 3 4 5', 'example_output': '5 4 3 2 1', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(head):\n    # Write your code here\n    return None', 'test_cases': [{'id': 'tc1', 'input': '1 2 3 4 5', 'expected_output': '5 4 3 2 1', 'category': 'basic', 'description': 'Standard list', 'is_hidden': False}, {'id': 'tc2', 'input': '1 2', 'expected_output': '2 1', 'category': 'edge', 'description': 'Two nodes', 'is_hidden': False}, {'id': 'tc3', 'input': '', 'expected_output': '', 'category': 'edge', 'description': 'Empty list', 'is_hidden': True}]},
            {'title': 'Sort Array by Parity', 'description': 'Move all even integers to the beginning of the array followed by all odd integers.', 'difficulty': 'intermediate', 'domain': 'sorting', 'constraints': {'input_size': '1 ≤ n ≤ 5000', 'value_range': '0 ≤ A[i] ≤ 5000'}, 'input_format': 'Array of integers', 'output_format': 'Sorted array by parity', 'example_input': '3 1 2 4', 'example_output': '2 4 3 1', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(arr):\n    # Write your code here\n    return []', 'test_cases': [{'id': 'tc1', 'input': '3 1 2 4', 'expected_output': '2 4 3 1', 'category': 'basic', 'description': 'Mixed numbers', 'is_hidden': False}, {'id': 'tc2', 'input': '0', 'expected_output': '0', 'category': 'edge', 'description': 'Single zero', 'is_hidden': False}, {'id': 'tc3', 'input': '2 4 6', 'expected_output': '2 4 6', 'category': 'edge', 'description': 'All even', 'is_hidden': True}]},
        ]
    
    def generate_challenge(self, db: Session, difficulty: str = "intermediate", player_rating: int = 1200, domain: Optional[str] = None, use_ai: bool = True) -> Dict[str, Any]:
        """Generate a challenge with three-tier fallback strategy and PERSIST to DB"""
        challenge_data = None
        try:
            if use_ai and self.ai_available and self.gemini_model:
                try:
                    logger.info(f"Attempting Gemini AI generation for {difficulty} challenge")
                    challenge_data = self._generate_ai_challenge(difficulty, player_rating, domain)
                    challenge_data['generation_method'] = 'ai'
                except Exception as e:
                    logger.warning(f"AI generation failed, falling back to templates: {e}")
            
            if not challenge_data:
                try:
                    logger.info(f"Using template generation for {difficulty} challenge")
                    challenge_data = self._generate_template_challenge(difficulty, domain)
                    challenge_data['generation_method'] = 'template'
                except Exception as e:
                    logger.warning(f"Template generation failed, using minimal fallback: {e}")
            
            if not challenge_data:
                logger.warning("Using minimal fallback challenge")
                challenge_data = self._generate_minimal_challenge(difficulty)
                challenge_data['generation_method'] = 'minimal'

            # PERSIST TO DATABASE
            new_challenge = Challenge(
                id=challenge_data['id'],
                title=challenge_data['title'],
                description=challenge_data['description'],
                difficulty=challenge_data['difficulty'],
                domain=challenge_data['domain'],
                input_format=challenge_data['input_format'],
                output_format=challenge_data['output_format'],
                example_input=challenge_data.get('example_input', ''),
                example_output=challenge_data.get('example_output', ''),
                constraints=json.dumps(challenge_data.get('constraints', {})),
                time_limit_seconds=challenge_data.get('time_limit_seconds', 5),
                boilerplate_code=challenge_data.get('boilerplate_code', ''),
                test_cases=json.dumps(challenge_data.get('test_cases', [])),
                coverage_metrics=json.dumps(challenge_data.get('coverage_metrics', {}))
            )
            db.add(new_challenge)
            db.commit()
            logger.info(f"Persisted challenge {challenge_data['id']} to database")
            
            return challenge_data
        except Exception as e:
            logger.error(f"All generation methods failed: {e}")
            raise
    
    def _generate_ai_challenge(self, difficulty: str, player_rating: int, domain: Optional[str]) -> Dict[str, Any]:
        """Generate challenge using Gemini AI"""
        domain_hint = f" in the '{domain}' domain" if domain else ""
        
        # Build exclusion list from recently used titles
        exclusion = ""
        if self._recently_used_titles:
            titles_list = ', '.join(f'"{t}"' for t in list(self._recently_used_titles)[-10:])
            exclusion = f"\nDO NOT generate any of these problems (already used): {titles_list}"

        prompt = f"""Generate a unique coding challenge for a competitive programming arena.

Difficulty: {difficulty} (player ELO: {player_rating})
Domain: {domain or 'any'}{exclusion}

Requirements:
- The function must be named `solve` 
- Input is provided as space-separated values on a single line
- Output should be a single value or space-separated values
- Include exactly 4 test cases (2 visible, 2 hidden)
- Test cases must have deterministic, verifiable answers
- Keep it simple enough to solve in under 5 minutes

Respond ONLY with valid JSON (no markdown, no backticks) in this exact format:
{{
  "title": "Problem Title",
  "description": "Full problem description with clear instructions",
  "domain": "arrays|strings|math|sorting|dynamic_programming",
  "input_format": "Description of input format",
  "output_format": "Description of output format",
  "constraints": {{"input_size": "1 ≤ n ≤ 1000"}},
  "boilerplate_code": "def solve(arr):\\n    # Write your code here\\n    return 0",
  "test_cases": [
    {{"input": "1 2 3", "expected_output": "6", "category": "basic", "description": "Basic test"}},
    {{"input": "0", "expected_output": "0", "category": "edge", "description": "Edge case"}},
    {{"input": "-1 -2 -3", "expected_output": "-6", "category": "edge", "description": "Negative numbers"}},
    {{"input": "100 200 300", "expected_output": "600", "category": "boundary", "description": "Large values"}}
  ]
}}"""

        response = self.gemini_model.generate_content(
            prompt,
            request_options={"timeout": 15.0}
        )
        text = response.text.strip()
        
        # Clean up any markdown wrapping
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        
        # Build test cases with proper IDs and hidden flags
        test_cases = []
        for i, tc in enumerate(data.get('test_cases', [])[:8]):
            test_cases.append({
                'id': f'tc{i+1}',
                'input': str(tc.get('input', '')),
                'expected_output': str(tc.get('expected_output', '')),
                'category': tc.get('category', 'basic'),
                'description': tc.get('description', ''),
                'is_hidden': i >= 2
            })
        
        title = data.get('title', 'AI Generated Challenge')
        self._recently_used_titles.add(title)

        return {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': data.get('description', ''),
            'difficulty': difficulty,
            'domain': data.get('domain', domain or 'arrays'),
            'constraints': data.get('constraints', {}),
            'input_format': data.get('input_format', 'See description'),
            'output_format': data.get('output_format', 'See description'),
            'example_input': test_cases[0]['input'] if test_cases else '',
            'example_output': test_cases[0]['expected_output'] if test_cases else '',
            'time_limit_seconds': 300,
            'boilerplate_code': data.get('boilerplate_code', 'def solve(arr):\n    # Write your code here\n    return 0'),
            'generated_at': datetime.utcnow().isoformat(),
            'test_cases': test_cases,
            'coverage_metrics': {}
        }
    
    def _generate_template_challenge(self, difficulty: str, domain: Optional[str]) -> Dict[str, Any]:
        """Generate challenge from pre-built templates with randomization and repeat avoidance"""
        # Get all templates for this difficulty
        indices = self._difficulty_indices.get(difficulty, self._difficulty_indices.get('intermediate', []))
        if not indices:
            indices = list(range(len(self.templates)))
        
        candidates = [self.templates[i] for i in indices]
        
        # Filter by domain if specified
        if domain:
            domain_filtered = [t for t in candidates if t['domain'] == domain]
            if domain_filtered:
                candidates = domain_filtered
        
        # Filter out recently used titles
        fresh = [t for t in candidates if t['title'] not in self._recently_used_titles]
        if fresh:
            candidates = fresh
        else:
            # All templates exhausted, reset tracking
            self._recently_used_titles.clear()
            logger.info("All templates used, resetting repeat tracker")
        
        # Randomly select from candidates
        template = random.choice(candidates)
        self._recently_used_titles.add(template['title'])
        
        challenge = template.copy()
        challenge['id'] = str(uuid.uuid4())
        challenge['generated_at'] = datetime.utcnow().isoformat()
        if 'coverage_metrics' not in challenge:
            challenge['coverage_metrics'] = {}
        return challenge
    
    def _generate_minimal_challenge(self, difficulty: str) -> Dict[str, Any]:
        """Generate minimal fallback challenge"""
        return {'id': str(uuid.uuid4()), 'title': f'Challenge - {difficulty.capitalize()}', 'description': 'Write a function to solve this problem.', 'difficulty': difficulty, 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 100'}, 'input_format': 'See example', 'output_format': 'See example', 'example_input': '1 2 3', 'example_output': '6', 'time_limit_seconds': 300, 'boilerplate_code': 'def solve(arr):\n    return sum(arr)', 'generated_at': datetime.utcnow().isoformat(), 'test_cases': [{'id': 'tc1', 'input': '1 2 3', 'expected_output': '6', 'category': 'basic', 'description': 'Basic test', 'is_hidden': False}], 'coverage_metrics': {}}
    
    def get_challenge_by_id(self, challenge_id: str, db: Session) -> Optional[Dict]:
        """Retrieve challenge by ID from database"""
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if challenge:
            return challenge.to_dict()
        return None
    
    def adapt_difficulty(self, player_id: str, recent_performance: List[bool], current_difficulty: str) -> str:
        """Adapt difficulty based on player performance"""
        if not recent_performance:
            return current_difficulty
        win_rate = sum(recent_performance) / len(recent_performance)
        if win_rate >= 0.8 and current_difficulty != 'advanced':
            progression = {'beginner': 'intermediate', 'intermediate': 'advanced', 'advanced': 'advanced'}
            return progression.get(current_difficulty, current_difficulty)
        if win_rate <= 0.2 and current_difficulty != 'beginner':
            regression = {'beginner': 'beginner', 'intermediate': 'beginner', 'advanced': 'intermediate'}
            return regression.get(current_difficulty, current_difficulty)
        return current_difficulty
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {'ai_available': self.ai_available, 'gemini_model': self.gemini_model is not None, 'templates_available': len(self.templates), 'recently_used': len(self._recently_used_titles), 'status': 'ready'}


_challenge_service_instance = None

def get_challenge_service() -> ChallengeService:
    """Get or create singleton instance of ChallengeService"""
    global _challenge_service_instance
    if _challenge_service_instance is None:
        _challenge_service_instance = ChallengeService()
    return _challenge_service_instance
