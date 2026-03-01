import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

# Try to import ML generators (optional)
try:
    from ml.challenge_generation.problem_statement_generator import ProblemStatementGenerator
    from ml.challenge_generation.test_case_generator import TestCaseGenerator
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML generators not available - will use templates")


class ChallengeService:
    """Robust challenge generation service with three-tier fallback strategy"""
    
    def __init__(self):
        """Initialize service with optional ML support"""
        self.ml_available = ML_AVAILABLE
        self.test_case_generator = None
        self.problem_generator = None
        
        if self.ml_available:
            try:
                self.test_case_generator = TestCaseGenerator()
                self.problem_generator = ProblemStatementGenerator()
                logger.info("ML generators initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize ML generators: {e}")
                self.ml_available = False
        
        self.templates = self._load_templates()
        self.template_index = {'beginner': 0, 'intermediate': 3, 'advanced': 6}
    
    def _load_templates(self) -> List[Dict]:
        """Load pre-built challenge templates"""
        return [
            {'title': 'Sum of Two Numbers', 'description': 'Write a function that takes two numbers and returns their sum.', 'difficulty': 'beginner', 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '-1000 ≤ x ≤ 1000'}, 'input_format': 'Two integers separated by space', 'output_format': 'Single integer (sum)', 'example_input': '5 3', 'example_output': '8', 'time_limit_seconds': 1, 'test_cases': [{'id': 'tc1', 'input': '5 3', 'expected_output': '8', 'category': 'basic', 'description': 'Basic addition', 'is_hidden': False}, {'id': 'tc2', 'input': '0 0', 'expected_output': '0', 'category': 'edge', 'description': 'Zero values', 'is_hidden': False}, {'id': 'tc3', 'input': '-5 3', 'expected_output': '-2', 'category': 'edge', 'description': 'Negative number', 'is_hidden': True}, {'id': 'tc4', 'input': '1000 1000', 'expected_output': '2000', 'category': 'boundary', 'description': 'Large values', 'is_hidden': True}]},
            {'title': 'Find Maximum in Array', 'description': 'Find the maximum element in an array of integers.', 'difficulty': 'beginner', 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '-1000 ≤ x ≤ 1000'}, 'input_format': 'Array of integers', 'output_format': 'Maximum value', 'example_input': '3 7 2 9 1', 'example_output': '9', 'time_limit_seconds': 1, 'test_cases': [{'id': 'tc1', 'input': '3 7 2 9 1', 'expected_output': '9', 'category': 'basic', 'description': 'Basic max', 'is_hidden': False}, {'id': 'tc2', 'input': '5', 'expected_output': '5', 'category': 'edge', 'description': 'Single element', 'is_hidden': False}, {'id': 'tc3', 'input': '-5 -2 -10', 'expected_output': '-2', 'category': 'edge', 'description': 'All negative', 'is_hidden': True}, {'id': 'tc4', 'input': '1000 999 998', 'expected_output': '1000', 'category': 'boundary', 'description': 'Large values', 'is_hidden': True}]},
            {'title': 'Reverse a String', 'description': 'Reverse the given string.', 'difficulty': 'beginner', 'domain': 'strings', 'constraints': {'input_size': '1 ≤ n ≤ 100', 'character_set': 'ASCII'}, 'input_format': 'Single string', 'output_format': 'Reversed string', 'example_input': 'hello', 'example_output': 'olleh', 'time_limit_seconds': 1, 'test_cases': [{'id': 'tc1', 'input': 'hello', 'expected_output': 'olleh', 'category': 'basic', 'description': 'Basic reverse', 'is_hidden': False}, {'id': 'tc2', 'input': 'a', 'expected_output': 'a', 'category': 'edge', 'description': 'Single char', 'is_hidden': False}, {'id': 'tc3', 'input': '', 'expected_output': '', 'category': 'edge', 'description': 'Empty string', 'is_hidden': True}, {'id': 'tc4', 'input': 'racecar', 'expected_output': 'racecar', 'category': 'boundary', 'description': 'Palindrome', 'is_hidden': True}]},
            {'title': 'Two Sum Problem', 'description': 'Find two numbers in array that add up to target.', 'difficulty': 'intermediate', 'domain': 'arrays', 'constraints': {'input_size': '2 ≤ n ≤ 1000', 'value_range': '-10000 ≤ x ≤ 10000'}, 'input_format': 'Array and target sum', 'output_format': 'Indices of two numbers', 'example_input': '2 7 11 15 9', 'example_output': '0 1', 'time_limit_seconds': 2, 'test_cases': [{'id': 'tc1', 'input': '2 7 11 15 9', 'expected_output': '0 1', 'category': 'basic', 'description': 'Basic two sum', 'is_hidden': False}, {'id': 'tc2', 'input': '3 3 4', 'expected_output': '0 1', 'category': 'edge', 'description': 'Duplicate values', 'is_hidden': False}, {'id': 'tc3', 'input': '-1 -2 -3 5 10', 'expected_output': '2 4', 'category': 'edge', 'description': 'Negative numbers', 'is_hidden': True}, {'id': 'tc4', 'input': '1 2 3 4 5 6 7 8 9 10 15', 'expected_output': '4 10', 'category': 'boundary', 'description': 'Large array', 'is_hidden': True}]},
            {'title': 'Palindrome Check', 'description': 'Check if a string is a palindrome.', 'difficulty': 'intermediate', 'domain': 'strings', 'constraints': {'input_size': '1 ≤ n ≤ 1000', 'character_set': 'ASCII'}, 'input_format': 'Single string', 'output_format': 'true or false', 'example_input': 'racecar', 'example_output': 'true', 'time_limit_seconds': 2, 'test_cases': [{'id': 'tc1', 'input': 'racecar', 'expected_output': 'true', 'category': 'basic', 'description': 'Basic palindrome', 'is_hidden': False}, {'id': 'tc2', 'input': 'hello', 'expected_output': 'false', 'category': 'basic', 'description': 'Not palindrome', 'is_hidden': False}, {'id': 'tc3', 'input': 'a', 'expected_output': 'true', 'category': 'edge', 'description': 'Single char', 'is_hidden': True}, {'id': 'tc4', 'input': 'A man a plan a canal Panama', 'expected_output': 'true', 'category': 'boundary', 'description': 'With spaces', 'is_hidden': True}]},
            {'title': 'Merge Sorted Arrays', 'description': 'Merge two sorted arrays into one sorted array.', 'difficulty': 'intermediate', 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 1000', 'value_range': '-10000 ≤ x ≤ 10000'}, 'input_format': 'Two sorted arrays', 'output_format': 'Merged sorted array', 'example_input': '1 3 5 2 4 6', 'example_output': '1 2 3 4 5 6', 'time_limit_seconds': 2, 'test_cases': [{'id': 'tc1', 'input': '1 3 5 2 4 6', 'expected_output': '1 2 3 4 5 6', 'category': 'basic', 'description': 'Basic merge', 'is_hidden': False}, {'id': 'tc2', 'input': '1 2 3', 'expected_output': '1 2 3', 'category': 'edge', 'description': 'One empty', 'is_hidden': False}, {'id': 'tc3', 'input': '-5 -2 1 -3 0 2', 'expected_output': '-5 -3 -2 0 1 2', 'category': 'edge', 'description': 'Negative numbers', 'is_hidden': True}, {'id': 'tc4', 'input': '1 1 1 1 1 1', 'expected_output': '1 1 1 1 1 1', 'category': 'boundary', 'description': 'Duplicates', 'is_hidden': True}]},
            {'title': 'Longest Substring Without Repeating', 'description': 'Find length of longest substring without repeating characters.', 'difficulty': 'advanced', 'domain': 'strings', 'constraints': {'input_size': '1 ≤ n ≤ 10000', 'character_set': 'ASCII'}, 'input_format': 'Single string', 'output_format': 'Integer (length)', 'example_input': 'abcabcbb', 'example_output': '3', 'time_limit_seconds': 3, 'test_cases': [{'id': 'tc1', 'input': 'abcabcbb', 'expected_output': '3', 'category': 'basic', 'description': 'Basic case', 'is_hidden': False}, {'id': 'tc2', 'input': 'bbbbb', 'expected_output': '1', 'category': 'edge', 'description': 'All same', 'is_hidden': False}, {'id': 'tc3', 'input': 'au', 'expected_output': '2', 'category': 'edge', 'description': 'No repeats', 'is_hidden': True}, {'id': 'tc4', 'input': 'dvdf', 'expected_output': '3', 'category': 'boundary', 'description': 'Complex pattern', 'is_hidden': True}]},
            {'title': 'Binary Tree Level Order Traversal', 'description': 'Return level order traversal of binary tree.', 'difficulty': 'advanced', 'domain': 'trees', 'constraints': {'input_size': '1 ≤ n ≤ 1000', 'tree_height': '1 ≤ h ≤ 100'}, 'input_format': 'Tree structure', 'output_format': 'Level order list', 'example_input': '[3,9,20,null,null,15,7]', 'example_output': '[[3],[9,20],[15,7]]', 'time_limit_seconds': 3, 'test_cases': [{'id': 'tc1', 'input': '[3,9,20,null,null,15,7]', 'expected_output': '[[3],[9,20],[15,7]]', 'category': 'basic', 'description': 'Basic tree', 'is_hidden': False}, {'id': 'tc2', 'input': '[1]', 'expected_output': '[[1]]', 'category': 'edge', 'description': 'Single node', 'is_hidden': False}, {'id': 'tc3', 'input': '[1,2,3,4,5,6,7]', 'expected_output': '[[1],[2,3],[4,5,6,7]]', 'category': 'boundary', 'description': 'Complete tree', 'is_hidden': True}, {'id': 'tc4', 'input': '[1,2,null,3]', 'expected_output': '[[1],[2],[3]]', 'category': 'boundary', 'description': 'Skewed tree', 'is_hidden': True}]},
            {'title': 'Longest Increasing Subsequence', 'description': 'Find length of longest increasing subsequence.', 'difficulty': 'advanced', 'domain': 'dynamic_programming', 'constraints': {'input_size': '1 ≤ n ≤ 10000', 'value_range': '-10000 ≤ x ≤ 10000'}, 'input_format': 'Array of integers', 'output_format': 'Integer (length)', 'example_input': '10 9 2 5 3 7 101 18', 'example_output': '4', 'time_limit_seconds': 3, 'test_cases': [{'id': 'tc1', 'input': '10 9 2 5 3 7 101 18', 'expected_output': '4', 'category': 'basic', 'description': 'Basic LIS', 'is_hidden': False}, {'id': 'tc2', 'input': '0 1 0 4 4 4 3 5 1', 'expected_output': '4', 'category': 'basic', 'description': 'Multiple options', 'is_hidden': False}, {'id': 'tc3', 'input': '5 4 3 2 1', 'expected_output': '1', 'category': 'edge', 'description': 'Decreasing', 'is_hidden': True}, {'id': 'tc4', 'input': '1 2 3 4 5', 'expected_output': '5', 'category': 'boundary', 'description': 'Increasing', 'is_hidden': True}]},
        ]
    
    def generate_challenge(self, difficulty: str = "intermediate", player_rating: int = 1200, domain: Optional[str] = None, use_ai: bool = True) -> Dict[str, Any]:
        """Generate a challenge with three-tier fallback strategy"""
        try:
            if use_ai and self.ml_available and self.problem_generator and self.test_case_generator:
                try:
                    logger.info(f"Attempting AI generation for {difficulty} challenge")
                    challenge = self._generate_ai_challenge(difficulty, player_rating, domain)
                    challenge['generation_method'] = 'ai'
                    return challenge
                except Exception as e:
                    logger.warning(f"AI generation failed, falling back to templates: {e}")
            
            try:
                logger.info(f"Using template generation for {difficulty} challenge")
                challenge = self._generate_template_challenge(difficulty, domain)
                challenge['generation_method'] = 'template'
                return challenge
            except Exception as e:
                logger.warning(f"Template generation failed, using minimal fallback: {e}")
            
            logger.warning("Using minimal fallback challenge")
            challenge = self._generate_minimal_challenge(difficulty)
            challenge['generation_method'] = 'minimal'
            return challenge
        except Exception as e:
            logger.error(f"All generation methods failed: {e}")
            raise
    
    def _generate_ai_challenge(self, difficulty: str, player_rating: int, domain: Optional[str]) -> Dict[str, Any]:
        """Generate challenge using AI models"""
        problem = self.problem_generator.generate_problem(difficulty=difficulty, elo_rating=player_rating, domain=domain)
        test_cases_data = self.test_case_generator.generate_test_cases(problem_statement=problem['statement'], difficulty=difficulty, domain=problem.get('domain', 'arrays'))
        test_cases = [{'id': f"tc{i+1}", 'input': tc.get('input', ''), 'expected_output': tc.get('expected_output', ''), 'category': tc.get('category', 'basic'), 'description': tc.get('description', ''), 'is_hidden': i >= 2} for i, tc in enumerate(test_cases_data.get('test_cases', [])[:8])]
        return {'id': str(uuid.uuid4()), 'title': problem.get('title', 'AI Generated Challenge'), 'description': problem.get('statement', ''), 'difficulty': difficulty, 'domain': problem.get('domain', 'arrays'), 'constraints': problem.get('constraints', {}), 'input_format': problem.get('input_format', 'See description'), 'output_format': problem.get('output_format', 'See description'), 'example_input': test_cases[0]['input'] if test_cases else '', 'example_output': test_cases[0]['expected_output'] if test_cases else '', 'time_limit_seconds': 3 if difficulty == 'advanced' else 2 if difficulty == 'intermediate' else 1, 'generated_at': datetime.utcnow().isoformat(), 'test_cases': test_cases, 'coverage_metrics': test_cases_data.get('coverage_metrics', {})}
    
    def _generate_template_challenge(self, difficulty: str, domain: Optional[str]) -> Dict[str, Any]:
        """Generate challenge from pre-built templates"""
        start_idx = self.template_index.get(difficulty, 0)
        candidates = []
        for i in range(start_idx, start_idx + 3):
            if i < len(self.templates):
                template = self.templates[i]
                if domain is None or template['domain'] == domain:
                    candidates.append(template)
        if candidates:
            template = candidates[0]
        else:
            template = self.templates[start_idx] if start_idx < len(self.templates) else self.templates[0]
        challenge = template.copy()
        challenge['id'] = str(uuid.uuid4())
        challenge['generated_at'] = datetime.utcnow().isoformat()
        if 'coverage_metrics' not in challenge:
            challenge['coverage_metrics'] = {}
        return challenge
    
    def _generate_minimal_challenge(self, difficulty: str) -> Dict[str, Any]:
        """Generate minimal fallback challenge"""
        return {'id': str(uuid.uuid4()), 'title': f'Challenge - {difficulty.capitalize()}', 'description': 'Write a function to solve this problem.', 'difficulty': difficulty, 'domain': 'arrays', 'constraints': {'input_size': '1 ≤ n ≤ 100'}, 'input_format': 'See example', 'output_format': 'See example', 'example_input': '1 2 3', 'example_output': '6', 'time_limit_seconds': 3 if difficulty == 'advanced' else 2 if difficulty == 'intermediate' else 1, 'generated_at': datetime.utcnow().isoformat(), 'test_cases': [{'id': 'tc1', 'input': '1 2 3', 'expected_output': '6', 'category': 'basic', 'description': 'Basic test', 'is_hidden': False}], 'coverage_metrics': {}}
    
    def get_challenge_by_id(self, challenge_id: str, db=None) -> Optional[Dict]:
        """Retrieve challenge by ID from database"""
        logger.warning(f"Challenge retrieval not yet implemented for {challenge_id}")
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
        return {'ml_available': self.ml_available, 'test_case_generator': self.test_case_generator is not None, 'problem_generator': self.problem_generator is not None, 'templates_available': len(self.templates) > 0, 'status': 'ready'}


_challenge_service_instance = None

def get_challenge_service() -> ChallengeService:
    """Get or create singleton instance of ChallengeService"""
    global _challenge_service_instance
    if _challenge_service_instance is None:
        _challenge_service_instance = ChallengeService()
    return _challenge_service_instance
