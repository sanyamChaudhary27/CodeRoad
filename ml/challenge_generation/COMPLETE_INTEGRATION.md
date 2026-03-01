# Complete ML Challenge Generation - Integration Guide

## Overview

You now have TWO AI-powered generators working together:
1. **Problem Statement Generator** - Creates unique problem statements
2. **Test Case Generator** - Creates comprehensive test cases

Together, they create fully AI-generated coding challenges.

## What's Available

### 1. Problem Statement Generator
```python
from ml.challenge_generation import ProblemStatementGenerator

generator = ProblemStatementGenerator()
problem = generator.generate_problem_statement(
    problem_id="prob_001",
    elo_rating=1200,
    domain="arrays",
    include_hints=True
)
```

**Output**:
- Title
- Description
- Input/Output specifications
- Example input/output
- Constraints
- Difficulty score
- Hints (optional)
- Follow-up questions (optional)

### 2. Test Case Generator
```python
from ml.challenge_generation import TestCaseGenerator

generator = TestCaseGenerator()
test_suite = generator.generate_test_cases(
    problem_id="prob_001",
    title="Sum of Array Elements",
    description="Calculate sum...",
    constraints={"array_size": "1 ≤ n ≤ 100"},
    input_format="First line: n...",
    output_format="Single integer",
    example_input="5\n1 2 3 4 5",
    example_output="15"
)
```

**Output**:
- 8+ test cases
- Coverage metrics
- Categories (basic, edge, boundary, mixed)
- Hidden test cases for fairness

## Complete Integration

### Option 1: Use Both Generators (Fully AI-Generated)

```python
from ml.challenge_generation import (
    ProblemStatementGenerator,
    TestCaseGenerator
)

def generate_complete_ai_challenge(player_rating, domain):
    """Generate a completely AI-powered challenge"""
    
    # Step 1: Generate problem statement
    problem_gen = ProblemStatementGenerator()
    problem = problem_gen.generate_problem_statement(
        problem_id=str(uuid.uuid4()),
        elo_rating=player_rating,
        domain=domain,
        include_hints=True
    )
    
    # Step 2: Generate test cases based on problem
    test_gen = TestCaseGenerator()
    
    # Convert constraints list to dict
    constraints_dict = {}
    for constraint in problem.constraints:
        if "≤" in constraint or "<" in constraint or ">" in constraint:
            constraints_dict[constraint.split(":")[0].strip()] = constraint
    
    test_suite = test_gen.generate_test_cases(
        problem_id=problem.problem_id,
        title=problem.title,
        description=problem.description,
        constraints=constraints_dict,
        input_format=problem.input_specification,
        output_format=problem.output_specification,
        example_input=problem.example_input,
        example_output=problem.example_output,
        num_test_cases=8
    )
    
    # Step 3: Combine into complete challenge
    challenge = {
        "id": problem.problem_id,
        "title": problem.title,
        "description": problem.description,
        "difficulty": problem_gen._elo_to_difficulty(player_rating),
        "domain": problem.domain,
        "constraints": problem.constraints,
        "input_format": problem.input_specification,
        "output_format": problem.output_specification,
        "example_input": problem.example_input,
        "example_output": problem.example_output,
        "difficulty_score": problem.difficulty_score,
        "estimated_success_rate": problem.estimated_success_rate,
        "test_cases": [
            {
                "id": tc.test_case_id,
                "input": tc.input,
                "expected_output": tc.expected_output,
                "category": tc.category,
                "description": tc.description,
                "is_hidden": tc.category in ["boundary", "edge_case"]
            }
            for tc in test_suite.test_cases
        ],
        "coverage_metrics": test_suite.coverage_metrics,
        "hints": problem.hints,
        "time_limit_seconds": 90,
        "generated_at": problem.generated_at
    }
    
    return challenge
```

### Option 2: Use Templates + AI Test Cases (Current Approach)

```python
from ml.challenge_generation import TestCaseGenerator

def generate_template_challenge(player_rating, domain):
    """Use template problem + AI test cases"""
    
    # Select template (existing approach)
    template = select_template(player_rating, domain)
    
    # Generate AI test cases
    test_gen = TestCaseGenerator()
    test_suite = test_gen.generate_test_cases(
        problem_id=str(uuid.uuid4()),
        title=template["title"],
        description=template["description"],
        constraints=template["constraints"],
        input_format=template["input_format"],
        output_format=template["output_format"],
        example_input=template["example_input"],
        example_output=template["example_output"]
    )
    
    # Combine
    challenge = {
        **template,
        "test_cases": [tc for tc in test_suite.test_cases],
        "coverage_metrics": test_suite.coverage_metrics
    }
    
    return challenge
```

## Update Challenge Service

Add to `backend/app/services/challenge_service.py`:

```python
from ml.challenge_generation import (
    TestCaseGenerator,
    ProblemStatementGenerator
)

class ChallengeService:
    def __init__(self, api_key=None):
        self.test_case_generator = TestCaseGenerator(api_key)
        self.problem_generator = ProblemStatementGenerator(api_key)
    
    def generate_ai_challenge(
        self,
        player_rating: int,
        domain: str,
        use_ai_problem: bool = False
    ):
        """
        Generate challenge with optional AI problem statement
        
        Args:
            player_rating: Player's ELO rating
            domain: Problem domain
            use_ai_problem: If True, generate AI problem statement
                           If False, use template
        """
        
        if use_ai_problem and self.problem_generator:
            # Fully AI-generated
            return self._generate_full_ai_challenge(player_rating, domain)
        else:
            # Template + AI test cases (current approach)
            return self.generate_challenge(
                difficulty=self._elo_to_difficulty(player_rating),
                player_rating=player_rating,
                domain=domain
            )
    
    def _generate_full_ai_challenge(self, player_rating, domain):
        """Generate completely AI-powered challenge"""
        
        # Generate problem
        problem = self.problem_generator.generate_problem_statement(
            problem_id=str(uuid.uuid4()),
            elo_rating=player_rating,
            domain=domain,
            include_hints=True
        )
        
        # Generate test cases
        constraints_dict = self._parse_constraints(problem.constraints)
        
        test_suite = self.test_case_generator.generate_test_cases(
            problem_id=problem.problem_id,
            title=problem.title,
            description=problem.description,
            constraints=constraints_dict,
            input_format=problem.input_specification,
            output_format=problem.output_specification,
            example_input=problem.example_input,
            example_output=problem.example_output
        )
        
        # Build challenge
        challenge = {
            "id": problem.problem_id,
            "title": problem.title,
            "description": problem.description,
            "difficulty": self._elo_to_difficulty(player_rating),
            "domain": problem.domain,
            "constraints": problem.constraints,
            "input_format": problem.input_specification,
            "output_format": problem.output_specification,
            "example_input": problem.example_input,
            "example_output": problem.example_output,
            "test_cases": [
                {
                    "id": tc.test_case_id,
                    "input": tc.input,
                    "expected_output": tc.expected_output,
                    "category": tc.category,
                    "description": tc.description,
                    "is_hidden": tc.category in ["boundary", "edge_case"]
                }
                for tc in test_suite.test_cases
            ],
            "coverage_metrics": test_suite.coverage_metrics,
            "hints": problem.hints,
            "difficulty_score": problem.difficulty_score,
            "estimated_success_rate": problem.estimated_success_rate,
            "time_limit_seconds": 90,
            "generated_at": problem.generated_at
        }
        
        return challenge
    
    def _parse_constraints(self, constraints_list):
        """Convert constraints list to dict"""
        constraints_dict = {}
        for constraint in constraints_list:
            if ":" in constraint:
                key, value = constraint.split(":", 1)
                constraints_dict[key.strip()] = value.strip()
            else:
                constraints_dict[constraint] = constraint
        return constraints_dict
    
    def _elo_to_difficulty(self, elo_rating):
        """Convert ELO to difficulty level"""
        if elo_rating < 1200:
            return "beginner"
        elif elo_rating < 1500:
            return "intermediate"
        else:
            return "advanced"
```

## API Endpoint

Add to `backend/app/api/challenge.py`:

```python
@router.post("/generate-ai", response_model=ChallengeResponse)
async def generate_ai_challenge(
    request: ChallengeRequest,
    use_ai_problem: bool = False,  # New parameter
    current_user: Player = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered challenge
    
    - use_ai_problem=False: Template + AI test cases (faster, cheaper)
    - use_ai_problem=True: Full AI generation (slower, more expensive, more variety)
    """
    
    challenge_service = get_challenge_service()
    player_rating = current_user.rating if hasattr(current_user, 'rating') else 1200
    
    challenge = challenge_service.generate_ai_challenge(
        player_rating=player_rating,
        domain=request.domain,
        use_ai_problem=use_ai_problem
    )
    
    return challenge
```

## Testing

### Test Problem Generator
```bash
cd ml/challenge_generation
python test_problem_generator.py
```

### Test Test Case Generator
```bash
cd ml/challenge_generation
python test_generator.py
```

### Test Complete Integration
```python
# test_complete_integration.py
from ml.challenge_generation import (
    ProblemStatementGenerator,
    TestCaseGenerator
)

def test_complete_flow():
    # Generate problem
    problem_gen = ProblemStatementGenerator()
    problem = problem_gen.generate_problem_statement(
        problem_id="test_001",
        elo_rating=1300,
        domain="arrays"
    )
    
    print(f"Problem: {problem.title}")
    
    # Generate test cases
    test_gen = TestCaseGenerator()
    test_suite = test_gen.generate_test_cases(
        problem_id=problem.problem_id,
        title=problem.title,
        description=problem.description,
        constraints={c: c for c in problem.constraints},
        input_format=problem.input_specification,
        output_format=problem.output_specification,
        example_input=problem.example_input,
        example_output=problem.example_output
    )
    
    print(f"Test cases: {len(test_suite.test_cases)}")
    print(f"Coverage: {test_suite.coverage_metrics['coverage_score']}")
    
    print("\n✓ Complete integration working!")

if __name__ == "__main__":
    test_complete_flow()
```

## Cost Comparison

### Template + AI Test Cases (Current)
- Problem: $0 (template)
- Test cases: $0.015
- **Total: $0.015 per challenge**

### Full AI Generation
- Problem: $0.015
- Test cases: $0.015
- **Total: $0.030 per challenge**

### Recommendation
- **Development/Testing**: Use full AI generation for variety
- **Production**: Use templates + AI test cases for cost efficiency
- **Special Events**: Use full AI generation for unique challenges

## Performance

| Approach | Time | Cost | Variety | Quality |
|----------|------|------|---------|---------|
| Template + AI Tests | 3-5s | $0.015 | Medium | High |
| Full AI Generation | 6-10s | $0.030 | Very High | Very High |

## Next Steps

1. **Test both generators**:
   ```bash
   cd ml/challenge_generation
   python test_problem_generator.py
   python test_generator.py
   ```

2. **Choose integration approach**:
   - Option 1: Full AI (more variety, higher cost)
   - Option 2: Template + AI tests (current, cost-effective)

3. **Update challenge service** with chosen approach

4. **Add API endpoint** for AI generation

5. **Test end-to-end** with match flow

6. **Monitor costs** and adjust as needed

## Summary

✅ **Problem Statement Generator**: Complete  
✅ **Test Case Generator**: Complete  
✅ **Integration Options**: Documented  
✅ **Cost Analysis**: Provided  
✅ **Testing**: Ready  

**You now have a complete AI-powered challenge generation system!** 🚀
