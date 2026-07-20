from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).parents[2]


def test_render_blueprint_contains_no_inline_secrets() -> None:
    blueprint = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "sk-" not in blueprint
    assert "postgresql://" not in blueprint
    for key in ("DATABASE_URL", "NVIDIA_NIM_KEY", "JUDGE0_AUTH_TOKEN"):
        assert re.search(rf"- key: {key}\n\s+sync: false", blueprint)
    assert re.search(r"- key: JUDGE0_API_URL\n\s+value: https://ce\.judge0\.com", blueprint)
    assert re.search(r"- key: SECRET_KEY\n\s+generateValue: true", blueprint)


def test_docker_backend_has_one_environment_mapping() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    backend_block = compose.split("  backend:", 1)[1].split("\n  ml-service:", 1)[0]

    assert backend_block.count("\n    environment:") == 1


def test_unsafe_automatic_migration_surface_is_removed() -> None:
    app_source = (ROOT / "backend/app/app.py").read_text(encoding="utf-8")

    assert "data_migration" not in app_source
    assert "auto_migrate" not in app_source
    assert not (ROOT / "backend/app/api/data_migration.py").exists()
    assert not (ROOT / "backend/app/core/auto_migrate.py").exists()
    assert not (ROOT / "coderoad_production_export.json").exists()


def test_no_tracked_python_bytecode() -> None:
    tracked = subprocess.check_output(
        ["git", "ls-files", "backend/**/__pycache__/*.pyc"],
        cwd=ROOT,
        text=True,
    )
    assert tracked.strip() == ""
