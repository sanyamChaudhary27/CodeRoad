"""
Example: Integrating Challenge Service with Match Service

This shows how to use the AI-powered challenge generator
in your match creation workflow.
"""

from app.services.challenge_service import get_challenge_service
from app.services.match_service import MatchService
from app.core.database import get_db

# Example 1: Generate challenge when creating a match
def create_match_with_challenge(player1_id: str, player2_id: str, db):
    """
    Create a match with an AI-generated challenge
    """
    
    # Get services
    challenge_service = get_challenge_service()
    match_service = MatchService(db)
    
    # Get player ratings for adaptive difficulty
    from app.models.player import Player
    player1 = db.query(Player).filter(Player.id == player1_id).first()
    player2 = db.query(Player).filter(Player.id == player2_id).first()
    
    # Calculate average rating
    avg_rating = (player1.current_rating + player2.current_rating) // 2
    
    # Generate challenge based on average rating
    challenge = challenge_service.generate_challenge(
        difficulty="intermediate",  # Will be adjusted based on rating
        player_rating=avg_rating,
        domain=None  # Random domain
    )
    
    print(f"Generated challenge: {challenge['title']}")
    print(f"Test cases: {len(challenge['test_cases'])}")
    print(f"Coverage score: {challenge['coverage_metrics']['coverage_score']}")
    
    # Create match with challenge
    match = match_service.create_match(
        player1_id=player1_id,
        player2_id=player2_id,
        challenge_id=challenge["id"],
        match_format="1v1",
        time_limit_seconds=challenge["time_limit_seconds"]
    )
    
    return {
        "match": match,
        "challenge": challenge
    }


# Example 2: Send challenge to players via WebSocket
async def send_challenge_to_players(match_id: str, challenge: dict, websocket_manager):
    """
    Broadcast challenge to both players in a match
    """
    
    # Filter test cases - hide some for fairness
    visible_test_cases = [
        tc for tc in challenge["test_cases"]
        if not tc.get("is_hidden", False)
    ]
    
    # Prepare challenge for players (without hidden test cases)
    player_challenge = {
        "id": challenge["id"],
        "title": challenge["title"],
        "description": challenge["description"],
        "difficulty": challenge["difficulty"],
        "constraints": challenge["constraints"],
        "input_format": challenge["input_format"],
        "output_format": challenge["output_format"],
        "example_input": challenge.get("example_input"),
        "example_output": challenge.get("example_output"),
        "time_limit_seconds": challenge["time_limit_seconds"],
        "visible_test_cases": visible_test_cases,
        "total_test_cases": len(challenge["test_cases"])
    }
    
    # Broadcast to match room
    await websocket_manager.broadcast_to_match(
        match_id=match_id,
        message={
            "type": "challenge_assigned",
            "challenge": player_challenge
        }
    )
    
    print(f"Sent challenge to players in match {match_id}")
    print(f"Visible test cases: {len(visible_test_cases)}/{len(challenge['test_cases'])}")


# Example 3: Use test cases for judging
def judge_submission(submission_code: str, challenge: dict):
    """
    Evaluate a submission against challenge test cases
    """
    
    results = []
    passed_tests = 0
    
    for test_case in challenge["test_cases"]:
        # Execute code with test input
        # (This is simplified - actual execution would use sandbox)
        try:
            # Simulate code execution
            result = execute_code_in_sandbox(
                code=submission_code,
                input_data=test_case["input"],
                timeout=5
            )
            
            # Compare output
            if result["output"].strip() == test_case["expected_output"].strip():
                passed_tests += 1
                results.append({
                    "test_case_id": test_case["id"],
                    "category": test_case["category"],
                    "passed": True
                })
            else:
                results.append({
                    "test_case_id": test_case["id"],
                    "category": test_case["category"],
                    "passed": False,
                    "expected": test_case["expected_output"],
                    "actual": result["output"]
                })
        
        except Exception as e:
            results.append({
                "test_case_id": test_case["id"],
                "category": test_case["category"],
                "passed": False,
                "error": str(e)
            })
    
    # Calculate score
    total_tests = len(challenge["test_cases"])
    test_case_score = (passed_tests / total_tests) * 100
    
    return {
        "test_case_score": test_case_score,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "results": results
    }


# Example 4: Adaptive difficulty based on performance
def adapt_challenge_difficulty(player_id: str, db):
    """
    Adjust challenge difficulty based on player's recent performance
    """
    
    challenge_service = get_challenge_service()
    match_service = MatchService(db)
    
    # Get player's recent matches
    recent_matches = match_service.get_player_matches(player_id, limit=5)
    
    # Calculate recent performance
    recent_wins = []
    for match in recent_matches:
        if match["winner_id"] == player_id:
            recent_wins.append(True)
        else:
            recent_wins.append(False)
    
    # Get current difficulty (from player profile or default)
    from app.models.player import Player
    player = db.query(Player).filter(Player.id == player_id).first()
    
    # Determine difficulty based on rating
    if player.current_rating < 1100:
        current_difficulty = "beginner"
    elif player.current_rating < 1400:
        current_difficulty = "intermediate"
    else:
        current_difficulty = "advanced"
    
    # Adapt difficulty
    new_difficulty = challenge_service.adapt_difficulty(
        player_id=player_id,
        recent_performance=recent_wins,
        current_difficulty=current_difficulty
    )
    
    print(f"Player {player_id} difficulty: {current_difficulty} → {new_difficulty}")
    
    return new_difficulty


# Example 5: Complete match flow with challenge
async def complete_match_flow(player1_id: str, player2_id: str, db, websocket_manager):
    """
    Complete flow: matchmaking → challenge generation → match → judging
    """
    
    print("=== Starting Match Flow ===")
    
    # Step 1: Create match with challenge
    print("\n1. Creating match with AI-generated challenge...")
    match_data = create_match_with_challenge(player1_id, player2_id, db)
    match = match_data["match"]
    challenge = match_data["challenge"]
    
    # Step 2: Send challenge to players
    print("\n2. Sending challenge to players...")
    await send_challenge_to_players(match["match_id"], challenge, websocket_manager)
    
    # Step 3: Start match
    print("\n3. Starting match timer...")
    match_service = MatchService(db)
    match_service.start_match(match["match_id"])
    
    # Step 4: Players submit code (simulated)
    print("\n4. Players submitting code...")
    # (In real flow, this comes from WebSocket)
    
    # Step 5: Judge submissions
    print("\n5. Judging submissions...")
    player1_submission = "def solve(): return 42"  # Simulated
    player2_submission = "def solve(): return 43"  # Simulated
    
    player1_result = judge_submission(player1_submission, challenge)
    player2_result = judge_submission(player2_submission, challenge)
    
    print(f"Player 1 score: {player1_result['test_case_score']}")
    print(f"Player 2 score: {player2_result['test_case_score']}")
    
    # Step 6: Conclude match
    print("\n6. Concluding match...")
    conclusion = match_service.conclude_match(
        match_id=match["match_id"],
        player1_score=player1_result["test_case_score"],
        player2_score=player2_result["test_case_score"]
    )
    
    print(f"Winner: {conclusion['winner_id']}")
    print(f"Result: {conclusion['result']}")
    
    # Step 7: Adapt difficulty for next match
    print("\n7. Adapting difficulty for next match...")
    new_difficulty = adapt_challenge_difficulty(conclusion["winner_id"], db)
    
    print("\n=== Match Flow Complete ===")
    
    return conclusion


# Utility function (placeholder)
def execute_code_in_sandbox(code: str, input_data: str, timeout: int):
    """
    Execute code in isolated sandbox
    (This is a placeholder - actual implementation would use Docker)
    """
    # TODO: Implement actual sandbox execution
    return {
        "output": "42",
        "execution_time": 0.1,
        "memory_used": 1024
    }


# Example usage
if __name__ == "__main__":
    """
    To use this in your application:
    
    1. Import the functions you need:
       from CHALLENGE_INTEGRATION_EXAMPLE import create_match_with_challenge
    
    2. Call them in your match service:
       match_data = create_match_with_challenge(player1_id, player2_id, db)
    
    3. Send challenge to players:
       await send_challenge_to_players(match_id, challenge, websocket_manager)
    
    4. Judge submissions:
       result = judge_submission(submission.code, challenge)
    """
    
    print("Challenge Integration Examples")
    print("=" * 50)
    print("\nSee function docstrings for usage examples")
    print("\nKey integration points:")
    print("  1. create_match_with_challenge() - Generate challenge for match")
    print("  2. send_challenge_to_players() - Send via WebSocket")
    print("  3. judge_submission() - Evaluate against test cases")
    print("  4. adapt_challenge_difficulty() - Adjust for next match")
    print("  5. complete_match_flow() - Full end-to-end flow")
