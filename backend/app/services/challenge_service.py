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

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq not installed - AI challenge generation disabled")


class ChallengeService:
    """Robust challenge generation service with Groq AI and multi-key rotation"""
    
    def __init__(self):
        """Initialize service with multiple Groq API keys for redundancy"""
        self.ai_available = False
        self.groq_clients = []
        self.current_key_index = 0
        self._recently_used_titles: Set[str] = set()
        
        # Load all Groq API keys
        if GROQ_AVAILABLE:
            groq_keys = []
            # Try to load up to 10 keys (GROQ_API_KEY, GROQ_API_KEY_2, etc.)
            for i in range(1, 11):
                key_name = f"GROQ_API_KEY_{i}" if i > 1 else "GROQ_API_KEY"
                api_key = os.getenv(key_name)
                if api_key:
                    groq_keys.append(api_key)
            
            # Initialize clients for each key
            for i, api_key in enumerate(groq_keys):
                try:
                    client = Groq(api_key=api_key)
                    self.groq_clients.append(client)
                    logger.info(f"Groq client {i+1} initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Groq client {i+1}: {e}")
            
            if self.groq_clients:
                self.ai_available = True
                logger.info(f"Groq AI initialized with {len(self.groq_clients)} API keys")
            else:
                logger.warning("No Groq API keys available")
        
        if not self.ai_available:
            logger.warning("No AI providers available, using templates only")
        
        self.templates = self._load_templates()
        
        # Difficulty -> list of valid template indices
        self._difficulty_indices = {
            'beginner': [i for i, t in enumerate(self.templates) if t['difficulty'] == 'beginner'],
            'intermediate': [i for i, t in enumerate(self.templates) if t['difficulty'] == 'intermediate'],
            'advanced': [i for i, t in enumerate(self.templates) if t['difficulty'] == 'advanced'],
        }

    
    def _load_templates(self) -> List[Dict]:
        """Load pre-built challenge templates"""
        # Import from extended_templates to keep this file manageable
        try:
            from .extended_templates import CHALLENGE_TEMPLATES
            return CHALLENGE_TEMPLATES
        except ImportError:
            # Fallback to minimal templates if extended_templates doesn't exist
            return [
                {
                    'title': 'Sum of Two Numbers',
                    'description': 'Write a function that takes two numbers and returns their sum.',
                    'difficulty': 'beginner',
                    'domain': 'arrays',
                    'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '-1000 ≤ x ≤ 1000'},
                    'input_format': 'Two integers separated by space',
                    'output_format': 'Single integer (sum)',
                    'example_input': '5 3',
                    'example_output': '8',
                    'time_limit_seconds': 300,
                    'boilerplate_code': 'def solve(a, b):\n    # Write your code here\n    return 0',
                    'test_cases': [
                        {'id': 'tc1', 'input': '5 3', 'expected_output': '8', 'category': 'basic', 'description': 'Basic addition', 'is_hidden': False},
                        {'id': 'tc2', 'input': '0 0', 'expected_output': '0', 'category': 'edge', 'description': 'Zero values', 'is_hidden': False},
                    ]
                },
                {
                    'title': 'Find Maximum in Array',
                    'description': 'Find the maximum element in an array of integers.',
                    'difficulty': 'beginner',
                    'domain': 'arrays',
                    'constraints': {'input_size': '1 ≤ n ≤ 100', 'value_range': '-1000 ≤ x ≤ 1000'},
                    'input_format': 'Array of integers',
                    'output_format': 'Maximum value',
                    'example_input': '3 7 2 9 1',
                    'example_output': '9',
                    'time_limit_seconds': 300,
                    'boilerplate_code': 'def solve(arr):\n    # Write your code here\n    return 0',
                    'test_cases': [
                        {'id': 'tc1', 'input': '3 7 2 9 1', 'expected_output': '9', 'category': 'basic', 'description': 'Basic max', 'is_hidden': False},
                        {'id': 'tc2', 'input': '5', 'expected_output': '5', 'category': 'edge', 'description': 'Single element', 'is_hidden': False},
                    ]
                }
            ]

    
    def generate_challenge(self, db: Session, difficulty: str = "intermediate", player_rating: int = 300, domain: Optional[str] = None, use_ai: bool = True, player_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a challenge with Groq AI (multi-key rotation) and template fallback
        
        Tries Groq with automatic key rotation, falls back to templates if all keys fail.
        Now includes player history for personalized challenge generation.
        """
        # DIVERSITY FIX: Load recent challenges from database to avoid repetition
        try:
            from datetime import timedelta
            from sqlalchemy import desc
            cutoff = datetime.utcnow() - timedelta(hours=24)
            recent = db.query(Challenge).filter(
                Challenge.created_at >= cutoff,
                Challenge.difficulty == difficulty
            ).order_by(desc(Challenge.created_at)).limit(15).all()
            
            for c in recent:
                self._recently_used_titles.add(c.title)
            
            if recent:
                logger.info(f"Loaded {len(recent)} recent {difficulty} challenges to avoid repetition")
        except Exception as e:
            logger.warning(f"Could not load recent challenges: {e}")
        
        challenge_data = None
        try:
            if use_ai and self.ai_available and self.groq_clients:
                # Try Groq with key rotation
                try:
                    logger.info(f"Attempting Groq AI generation for {difficulty} challenge (rating: {player_rating})")
                    challenge_data = self._generate_groq_challenge(difficulty, player_rating, domain, db, player_id)
                    challenge_data['generation_method'] = 'groq_ai'
                except Exception as e:
                    logger.warning(f"Groq generation failed: {e}")
            
            # Fall back to templates if AI fails or disabled
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

    
    def _clean_boilerplate(self, boilerplate: str) -> str:
        """Clean boilerplate code to remove any solution logic that AI might have included.
        
        Ensures only function signature, comment, and placeholder return remain.
        """
        lines = boilerplate.split('\n')
        
        # Find the function definition line
        func_def_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('def solve'):
                func_def_idx = i
                break
        
        if func_def_idx == -1:
            # No function found, return safe default
            return "def solve(arr):\n    # Write your solution here\n    return 0"
        
        # Keep only: function def + one comment + one return statement
        clean_lines = [lines[func_def_idx]]  # Function definition
        
        # Add a simple comment
        clean_lines.append("    # Write your solution here")
        
        # Add placeholder return
        clean_lines.append("    return 0")
        
        return '\n'.join(clean_lines)

    
    def _generate_groq_challenge(self, difficulty: str, player_rating: int, domain: Optional[str], db: Session = None, player_id: str = None) -> Dict[str, Any]:
        """Generate challenge using Groq AI with automatic key rotation and ELO-smart difficulty"""
        
        # PERSONALIZATION: Get player's recent match history for learning
        player_history = ""
        if db and player_id:
            try:
                from ..models import Match
                from sqlalchemy import desc, or_
                
                recent_matches = db.query(Match).filter(
                    or_(Match.player1_id == player_id, Match.player2_id == player_id),
                    Match.status == 'concluded'
                ).order_by(desc(Match.concluded_at)).limit(5).all()
                
                if recent_matches:
                    history_challenges = []
                    for match in recent_matches:
                        challenge = db.query(Challenge).filter(Challenge.id == match.challenge_id).first()
                        if challenge:
                            # Get player's score for this match
                            player_score = match.player1_score if match.player1_id == player_id else match.player2_score
                            max_score = 4  # Assuming 4 test cases
                            success_rate = (player_score / max_score * 100) if player_score else 0
                            
                            history_challenges.append({
                                'title': challenge.title,
                                'difficulty': challenge.difficulty,
                                'domain': challenge.domain,
                                'success_rate': f"{success_rate:.0f}%"
                            })
                    
                    if history_challenges:
                        player_history = "\n\nPLAYER'S RECENT MATCH HISTORY (Learn from these but generate something NEW):\n"
                        for i, ch in enumerate(history_challenges, 1):
                            player_history += f"{i}. \"{ch['title']}\" ({ch['difficulty']}, {ch['domain']}) - Success: {ch['success_rate']}\n"
                        player_history += "\nGENERATE a problem SIMILAR in style/difficulty to these, but with a DIFFERENT concept/algorithm. DO NOT repeat any of these exact problems!"
                        
                        logger.info(f"Using player history: {len(history_challenges)} recent challenges for personalization")
            except Exception as e:
                logger.warning(f"Could not load player history: {e}")
        
        # Build exclusion list
        exclusion = ""
        if self._recently_used_titles:
            titles_list = ', '.join(f'"{t}"' for t in list(self._recently_used_titles)[-10:])
            exclusion = f"\n\nAVOID THESE PROBLEMS (already used): {titles_list}"

        # ELO-smart difficulty guidance based on player rating
        if player_rating < 500:
            complexity_guide = """
COMPLEXITY LEVEL: BEGINNER (Rating < 500)
Generate SIMPLE, FUNDAMENTAL problems that teach basic programming concepts:
- Array sum, finding max/min, counting elements
- Simple string operations (reverse, count characters)
- Basic math (even/odd, factorial, simple calculations)
- Direct iteration problems with clear patterns

EXAMPLES FOR BEGINNERS:
- Sum of array elements
- Find maximum in array
- Count even numbers
- Reverse a string
- Check if number is prime
"""
        elif player_rating < 800:
            complexity_guide = """
COMPLEXITY LEVEL: INTERMEDIATE (Rating 500-800)
Generate problems requiring basic algorithms and problem-solving:
- Two pointers, sliding window basics
- Simple sorting problems
- Basic string manipulation (palindromes, anagrams)
- Array rotation, partitioning
- Simple greedy approaches

EXAMPLES FOR INTERMEDIATE:
- Find missing number in sequence
- Rotate array by k positions
- Check for palindrome
- Find majority element
- Remove duplicates from sorted array
"""
        else:
            complexity_guide = """
COMPLEXITY LEVEL: ADVANCED (Rating 800+)
Generate challenging problems requiring advanced techniques:
- Dynamic programming (LIS, LCS, knapsack variants)
- Complex two pointers, sliding window
- Advanced graph/tree algorithms
- Bit manipulation tricks
- Mathematical insights

EXAMPLES FOR ADVANCED:
- Longest increasing subsequence
- Maximum subarray sum (Kadane's)
- Count inversions in array
- Product of array except self
- Merge overlapping intervals
"""

        
        # Domain-specific hints
        domain_hints = {
            'arrays': 'Focus on array manipulation, searching, or mathematical properties',
            'strings': 'Focus on string patterns, transformations, or character analysis',
            'trees': 'Focus on tree traversals, properties, or construction',
            'dynamic_programming': 'Focus on optimization problems with overlapping subproblems',
            'graphs': 'Focus on connectivity, paths, or graph properties',
            'math': 'Focus on number properties, calculations, or mathematical patterns',
            'sorting': 'Focus on ordering, comparisons, or arrangement problems',
            'linked_lists': 'Focus on list manipulation, traversal, or reordering'
        }
        
        hint = domain_hints.get(domain or 'arrays', 'Generate an appropriate problem')

        prompt = f"""Generate a coding challenge appropriate for a player with rating {player_rating}.

{complexity_guide}

Difficulty: {difficulty}
Player Rating: {player_rating}
Domain: {domain or 'arrays'}
Hint: {hint}{player_history}{exclusion}

CRITICAL REQUIREMENTS:
1. Match complexity to player rating (see COMPLEXITY LEVEL above)
2. Function MUST be named "solve" and take ONE parameter (an array/list)
3. Input format: ALWAYS space-separated integers on ONE line (even for single element)
4. The function signature MUST be: def solve(arr): where arr is a list
5. Test cases: Input "1 2 3" means arr=[1,2,3], Input "5" means arr=[5] (single-element list)
6. NEVER use multiple parameters - only ONE array parameter
7. Description must clearly state: "Given an array of integers..." or "Given a list..."

IMPORTANT - Function Signature:
- CORRECT: def solve(arr):  # arr is always a list
- WRONG: def solve(a, b):  # Never use multiple parameters
- WRONG: def solve(n):  # Don't use single number parameter

INPUT/OUTPUT CLARITY:
- Input is ALWAYS an array (even if it has one element)
- Example: Input "5" means the array [5], NOT the number 5
- Example: Input "1 2 3" means the array [1, 2, 3]
- Make this CRYSTAL CLEAR in the problem description

BOILERPLATE CODE RULES:
- DO NOT include any solution logic
- DO NOT include loops, conditions, or actual implementation
- ONLY include: function definition, a helpful comment, and "return 0" or similar placeholder
- Example: "def solve(arr):\\n    # Write your solution here\\n    return 0"

Return ONLY valid JSON:
{{
  "title": "Problem Title",
  "description": "MUST start with 'Given an array of integers...' and clearly explain that input is always an array. Include 3-4 example cases showing how the array is processed.",
  "domain": "{domain or 'arrays'}",
  "input_format": "Space-separated integers" or "Single integer",
  "output_format": "Single integer" or "Space-separated integers",
  "constraints": {{"input_size": "1<=n<=1000", "value_range": "-1000<=x<=1000"}},
  "boilerplate_code": "def solve(arr):\\n    # Write your solution here\\n    return 0",
  "test_cases": [
    {{"input": "3 1 4 1 5", "expected_output": "3", "category": "basic", "description": "Array with 5 elements"}},
    {{"input": "7", "expected_output": "0", "category": "edge", "description": "Single-element array [7]"}},
    {{"input": "5 4 3 2 1", "expected_output": "4", "category": "edge", "description": "Descending array"}},
    {{"input": "1 2 3 4 5 6 7 8 9 10", "expected_output": "55", "category": "boundary", "description": "Array with 10 elements"}}
  ]
}}

REMEMBER: Input "7" means the array [7] (single element), NOT the number 7!

Generate a problem appropriate for rating {player_rating}!"""


        # Try each Groq client with key rotation
        last_error = None
        for attempt in range(len(self.groq_clients)):
            try:
                # Use round-robin key selection
                client = self.groq_clients[self.current_key_index]
                logger.debug(f"Using Groq key {self.current_key_index + 1}/{len(self.groq_clients)}")
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a coding challenge generator. Generate problems appropriate for the player's skill level. For beginners (rating < 500), create simple fundamental problems. For intermediate (500-800), create moderate algorithmic problems. For advanced (800+), create challenging problems requiring advanced techniques. NEVER include solution logic in boilerplate code."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1.0,  # Increased from 0.8 for more variety
                    max_tokens=2500,
                )
                
                text = response.choices[0].message.content.strip()
                logger.info(f"Groq response length: {len(text)} chars (key {self.current_key_index + 1})")
                
                # Clean up markdown if present
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                # Extract JSON
                start_idx = text.find('{')
                end_idx = text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    text = text[start_idx:end_idx+1]
                else:
                    raise ValueError("No complete JSON object in Groq response")
                
                # Verify balanced braces
                if text.count('{') != text.count('}'):
                    raise ValueError("Incomplete JSON from Groq (unbalanced braces)")
                
                # Parse JSON
                data = json.loads(text)
                title = data.get('title', 'AI Generated Challenge')
                
                logger.info(f"Successfully parsed Groq challenge: {title} (for rating {player_rating})")
                
                # Clean boilerplate code to ensure no solution is included
                boilerplate = data.get('boilerplate_code', 'def solve(arr):\n    # Write your solution here\n    return 0')
                boilerplate = self._clean_boilerplate(boilerplate)
                
                # Success! Rotate to next key for next time
                self.current_key_index = (self.current_key_index + 1) % len(self.groq_clients)

                
                # Build test cases
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
                    'boilerplate_code': boilerplate,
                    'generated_at': datetime.utcnow().isoformat(),
                    'test_cases': test_cases,
                    'coverage_metrics': {}
                }
                
            except Exception as e:
                last_error = e
                logger.warning(f"Groq key {self.current_key_index + 1} failed: {e}")
                # Rotate to next key and try again
                self.current_key_index = (self.current_key_index + 1) % len(self.groq_clients)
                continue
        
        # All keys failed
        raise Exception(f"All {len(self.groq_clients)} Groq API keys failed. Last error: {last_error}")

    
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
        return {
            'id': str(uuid.uuid4()),
            'title': f'Challenge - {difficulty.capitalize()}',
            'description': 'Write a function to solve this problem.',
            'difficulty': difficulty,
            'domain': 'arrays',
            'constraints': {'input_size': '1 ≤ n ≤ 100'},
            'input_format': 'See example',
            'output_format': 'See example',
            'example_input': '1 2 3',
            'example_output': '6',
            'time_limit_seconds': 300,
            'boilerplate_code': 'def solve(arr):\n    # Write your solution here\n    return 0',
            'generated_at': datetime.utcnow().isoformat(),
            'test_cases': [
                {'id': 'tc1', 'input': '1 2 3', 'expected_output': '6', 'category': 'basic', 'description': 'Basic test', 'is_hidden': False}
            ],
            'coverage_metrics': {}
        }

    
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
        return {
            'ai_available': self.ai_available,
            'groq_clients': len(self.groq_clients),
            'templates_available': len(self.templates),
            'recently_used': len(self._recently_used_titles),
            'status': 'ready'
        }


_challenge_service_instance = None

def get_challenge_service() -> ChallengeService:
    """Get or create singleton instance of ChallengeService"""
    global _challenge_service_instance
    if _challenge_service_instance is None:
        _challenge_service_instance = ChallengeService()
    return _challenge_service_instance


    def generate_debug_challenge(self, db: Session, difficulty: str = "intermediate", player_rating: int = 300, domain: Optional[str] = None, use_ai: bool = True, player_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a debug challenge with broken code
        
        Similar to generate_challenge but creates challenges with intentional bugs.
        """
        # Load recent debug challenges to avoid repetition
        try:
            from datetime import timedelta
            from sqlalchemy import desc
            cutoff = datetime.utcnow() - timedelta(hours=24)
            recent = db.query(Challenge).filter(
                Challenge.created_at >= cutoff,
                Challenge.difficulty == difficulty,
                Challenge.challenge_type == 'debug'
            ).order_by(desc(Challenge.created_at)).limit(15).all()
            
            recent_titles = set()
            for c in recent:
                recent_titles.add(c.title)
            
            if recent:
                logger.info(f"Loaded {len(recent)} recent debug challenges to avoid repetition")
        except Exception as e:
            logger.warning(f"Could not load recent debug challenges: {e}")
            recent_titles = set()
        
        challenge_data = None
        try:
            if use_ai and self.ai_available and self.groq_clients:
                # Try Groq AI for debug challenge
                try:
                    logger.info(f"Attempting Groq AI generation for {difficulty} debug challenge")
                    challenge_data = self._generate_groq_debug_challenge(difficulty, player_rating, domain, db, player_id, recent_titles)
                    challenge_data['generation_method'] = 'groq_ai'
                except Exception as e:
                    logger.warning(f"Groq debug generation failed: {e}")
            
            # Fall back to debug templates
            if not challenge_data:
                try:
                    logger.info(f"Using template generation for {difficulty} debug challenge")
                    challenge_data = self._generate_template_debug_challenge(difficulty, recent_titles)
                    challenge_data['generation_method'] = 'template'
                except Exception as e:
                    logger.warning(f"Debug template generation failed: {e}")
            
            if not challenge_data:
                raise Exception("All debug generation methods failed")

            # PERSIST TO DATABASE
            new_challenge = Challenge(
                id=challenge_data['id'],
                title=challenge_data['title'],
                description=challenge_data['description'],
                difficulty=challenge_data['difficulty'],
                domain=challenge_data['domain'],
                challenge_type='debug',
                broken_code=challenge_data.get('broken_code', ''),
                bug_count=challenge_data.get('bug_count', 1),
                bug_types=json.dumps(challenge_data.get('bug_types', [])),
                input_format=challenge_data['input_format'],
                output_format=challenge_data['output_format'],
                example_input=challenge_data.get('example_input', ''),
                example_output=challenge_data.get('example_output', ''),
                constraints=json.dumps(challenge_data.get('constraints', {})),
                time_limit_seconds=challenge_data.get('time_limit_seconds', 5),
                boilerplate_code=challenge_data.get('broken_code', ''),  # For debug, boilerplate IS the broken code
                test_cases=json.dumps(challenge_data.get('test_cases', [])),
                coverage_metrics=json.dumps(challenge_data.get('coverage_metrics', {}))
            )
            db.add(new_challenge)
            db.commit()
            logger.info(f"Persisted debug challenge {challenge_data['id']} to database")
            
            return challenge_data
        except Exception as e:
            logger.error(f"Debug challenge generation failed: {e}")
            raise

    def _generate_template_debug_challenge(self, difficulty: str, recent_titles: Set[str]) -> Dict[str, Any]:
        """Generate debug challenge from templates"""
        from .extended_templates import DEBUG_TEMPLATES
        
        # Filter templates by difficulty
        matching_templates = [t for t in DEBUG_TEMPLATES if t['difficulty'] == difficulty]
        
        if not matching_templates:
            # Fallback to any difficulty
            matching_templates = DEBUG_TEMPLATES
        
        # Filter out recently used titles
        available_templates = [t for t in matching_templates if t['title'] not in recent_titles]
        
        if not available_templates:
            # If all have been used, use any
            available_templates = matching_templates
        
        # Select random template
        template = random.choice(available_templates)
        
        # Create challenge data
        challenge_data = {
            'id': str(uuid.uuid4()),
            'title': template['title'],
            'description': template['description'],
            'difficulty': template['difficulty'],
            'domain': template['domain'],
            'challenge_type': 'debug',
            'broken_code': template['broken_code'],
            'bug_count': template['bug_count'],
            'bug_types': template['bug_types'],
            'input_format': template['input_format'],
            'output_format': template['output_format'],
            'example_input': template.get('example_input', ''),
            'example_output': template.get('example_output', ''),
            'constraints': template.get('constraints', {}),
            'time_limit_seconds': template.get('time_limit_seconds', 5),
            'test_cases': template['test_cases'],
            'coverage_metrics': {}
        }
        
        return challenge_data

    def _generate_groq_debug_challenge(self, difficulty: str, player_rating: int, domain: Optional[str], db: Session, player_id: str, recent_titles: Set[str]) -> Dict[str, Any]:
        """Generate debug challenge using Groq AI"""
        
        # Get player history for personalization
        player_history = ""
        if db and player_id:
            try:
                from ..models import Match
                from sqlalchemy import desc, or_
                
                recent_matches = db.query(Match).filter(
                    or_(Match.player1_id == player_id, Match.player2_id == player_id),
                    Match.status == 'concluded',
                    Match.challenge_type == 'debug'
                ).order_by(desc(Match.ended_at)).limit(5).all()
                
                if recent_matches:
                    history_challenges = []
                    for match in recent_matches:
                        challenge = db.query(Challenge).filter(Challenge.id == match.challenge_id).first()
                        if challenge:
                            player_score = match.player1_score if match.player1_id == player_id else match.player2_score
                            max_score = 4
                            success_rate = (player_score / max_score * 100) if player_score else 0
                            
                            history_challenges.append({
                                'title': challenge.title,
                                'difficulty': challenge.difficulty,
                                'domain': challenge.domain,
                                'bug_types': json.loads(challenge.bug_types) if challenge.bug_types else [],
                                'success_rate': success_rate
                            })
                    
                    if history_challenges:
                        player_history = "\n\nPLAYER'S RECENT DEBUG MATCH HISTORY (Learn from these but generate something NEW):\n"
                        for i, h in enumerate(history_challenges, 1):
                            player_history += f"{i}. \"{h['title']}\" ({h['difficulty']}, {h['domain']}, bugs: {h['bug_types']}) - Success: {h['success_rate']:.0f}%\n"
                        player_history += "\nGENERATE a problem SIMILAR in style/difficulty to these, but with a DIFFERENT concept/algorithm.\n"
            except Exception as e:
                logger.warning(f"Could not fetch player history: {e}")
        
        # Build exclusion list
        exclusion_text = ""
        if recent_titles:
            exclusion_text = f"\n\nDO NOT generate these recently used challenges:\n" + "\n".join(f"- {title}" for title in list(recent_titles)[:10])
        
        # Create prompt for debug challenge
        domain_text = f" in the domain of {domain}" if domain else ""
        
        prompt = f"""Generate a {difficulty} level debugging challenge{domain_text} for competitive programming.

The challenge should contain BROKEN CODE with intentional bugs that the player must fix.

Requirements:
- Difficulty: {difficulty}
- Bug count: {1 if difficulty == 'beginner' else 2 if difficulty == 'intermediate' else 3}
- Bug types can be: syntax, logic, runtime, algorithm, edge_case
- Include the broken code and what it should do
- Provide test cases to verify the fix

{player_history}
{exclusion_text}

Return ONLY valid JSON with this exact structure:
{{
    "title": "Fix the [Function Name]",
    "description": "Clear description of what the code should do and what's wrong",
    "difficulty": "{difficulty}",
    "domain": "debugging",
    "broken_code": "The buggy code as a string",
    "bug_count": 1-3,
    "bug_types": ["syntax", "logic", etc],
    "input_format": "Description of input",
    "output_format": "Description of output",
    "example_input": "Sample input",
    "example_output": "Expected output",
    "constraints": {{"input_size": "1 ≤ n ≤ 100"}},
    "time_limit_seconds": 5,
    "test_cases": [
        {{"id": "tc1", "input": "...", "expected_output": "...", "category": "basic", "description": "...", "is_hidden": false}},
        {{"id": "tc2", "input": "...", "expected_output": "...", "category": "edge", "description": "...", "is_hidden": true}}
    ]
}}"""
        
        # Try each Groq client with rotation
        for attempt in range(len(self.groq_clients)):
            try:
                client = self.groq_clients[self.current_key_index]
                logger.info(f"Trying Groq key {self.current_key_index + 1}/{len(self.groq_clients)}")
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1.0,
                    max_tokens=2000
                )
                
                content = response.choices[0].message.content.strip()
                
                # Extract JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                challenge_data = json.loads(content)
                challenge_data['id'] = str(uuid.uuid4())
                
                logger.info(f"Successfully generated debug challenge with Groq key {self.current_key_index + 1}")
                return challenge_data
                
            except Exception as e:
                logger.warning(f"Groq key {self.current_key_index + 1} failed: {e}")
                self.current_key_index = (self.current_key_index + 1) % len(self.groq_clients)
        
        raise Exception("All Groq keys failed for debug challenge generation")
