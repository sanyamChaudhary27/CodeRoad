import os
from dotenv import load_dotenv
from ml.challenge_generation.problem_statement_generator import ProblemStatementGenerator

def test_problem_gen():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("No GEMINI_API_KEY found. Skipping test.")
        return

    try:
        generator = ProblemStatementGenerator()
        problem = generator.generate_problem(difficulty="intermediate", elo_rating=1500, domain="graphs")
        print("SUCCESS! Generated Problem:")
        print(f"Title: {problem.get('title')}")
        print(f"Domain: {problem.get('domain')}")
        print(f"Constraints: {problem.get('constraints')}")
        print(f"Input: {problem.get('input_format')}")
        print(f"Output: {problem.get('output_format')}")
        print(f"Statement: {problem.get('statement')[:100]}...")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_problem_gen()
