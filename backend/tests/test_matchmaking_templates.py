from pathlib import Path

from app.services.challenge_service import ChallengeService


ROOT = Path(__file__).parents[2]


def test_debug_template_fallback_is_available_without_optional_module() -> None:
    challenge = ChallengeService()._generate_template_debug_challenge("intermediate", set())

    assert challenge["challenge_type"] == "debug"
    assert challenge["test_cases"]
    assert challenge["broken_code"]


def test_live_matchmaking_disables_network_challenge_generation() -> None:
    source = (ROOT / "backend/app/services/match_service.py").read_text(encoding="utf-8")
    status_method = source.split("def get_queue_status_with_matchmaking", 1)[1].split(
        "def leave_match_queue", 1
    )[0]

    assert status_method.count("use_ai=False") == 2
    assert source.count("use_ai=False") == 4


def test_render_requirements_include_startup_http_dependency() -> None:
    requirements = (ROOT / "backend/requirements-render.txt").read_text(encoding="utf-8")

    assert "requests==2.32.3" in requirements
    assert "groq==" not in requirements
