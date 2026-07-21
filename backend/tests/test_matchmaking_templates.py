from pathlib import Path
import json

import pytest

from app.services.challenge_service import ChallengeService


ROOT = Path(__file__).parents[2]


def test_debug_template_fallback_is_available_without_optional_module() -> None:
    challenge = ChallengeService()._generate_template_debug_challenge("intermediate", set())

    assert challenge["challenge_type"] == "debug"
    assert challenge["test_cases"]
    assert challenge["broken_code"]


def test_live_matchmaking_consumes_prewarmed_ai_challenges_without_network_waits() -> None:
    source = (ROOT / "backend/app/services/match_service.py").read_text(encoding="utf-8")
    status_method = source.split("def get_queue_status_with_matchmaking", 1)[1].split(
        "def leave_match_queue", 1
    )[0]

    assert status_method.count("use_ai=False") == 2
    assert source.count("use_ai=False") == 4
    assert source.count("prewarm_challenge") == 2


def test_nim_challenge_payload_is_normalized_for_live_matchmaking() -> None:
    payload = {
        "title": "Count Positive Values",
        "description": "Return the number of positive integers in the provided array.",
        "domain": "arrays",
        "input_format": "Space-separated integers",
        "output_format": "One integer",
        "constraints": {"input_size": "1 <= n <= 100"},
        "boilerplate_code": "def solve(arr):\n    return len(arr)",
        "test_cases": [
            {"input": "1 -2 3", "expected_output": "2", "category": "basic", "description": "Mixed signs"},
            {"input": "-1 -2", "expected_output": "0", "category": "edge", "description": "No positives"},
            {"input": "5", "expected_output": "1", "category": "edge", "description": "One positive"},
        ],
    }

    challenge = ChallengeService()._parse_nim_challenge(json.dumps(payload), "dsa", "beginner")

    assert challenge["challenge_type"] == "dsa"
    assert challenge["test_cases"][2]["is_hidden"] is True
    assert challenge["boilerplate_code"] == "def solve(arr):\n    # Write your solution here\n    return 0"


def test_nim_challenge_payload_rejects_invalid_test_cases() -> None:
    payload = {
        "title": "Broken Payload",
        "description": "This should be rejected because it has too few test cases.",
        "domain": "arrays",
        "input_format": "Space-separated integers",
        "output_format": "One integer",
        "constraints": {},
        "test_cases": [],
    }

    with pytest.raises(ValueError, match="three to eight"):
        ChallengeService()._parse_nim_challenge(json.dumps(payload), "dsa", "beginner")


def test_render_requirements_include_startup_http_dependency() -> None:
    requirements = (ROOT / "backend/requirements-render.txt").read_text(encoding="utf-8")

    assert "requests==2.32.3" in requirements
    assert "groq==" not in requirements
