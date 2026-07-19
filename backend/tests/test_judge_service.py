import ast
import json
from pathlib import Path

import httpx
import pytest

from app.services.judge_service import (
    CodeExecutionUnavailable,
    Judge0Client,
    JudgeService,
    build_python_source,
)


def test_unconfigured_runner_fails_closed() -> None:
    client = Judge0Client(base_url="")

    with pytest.raises(CodeExecutionUnavailable, match="Isolated execution is not configured"):
        client.execute_python("print('never runs')", "")


def test_judge0_request_enforces_resource_limits_and_no_network() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            201,
            json={
                "stdout": "6\n",
                "stderr": None,
                "compile_output": None,
                "time": "0.012",
                "memory": 2048,
                "status": {"id": 3, "description": "Accepted"},
            },
        )

    client = Judge0Client(
        base_url="https://judge.example",
        auth_token="test-token",
        transport=httpx.MockTransport(handler),
    )
    result = client.execute_python("print(6)", "1 2 3")

    assert result.accepted is True
    assert result.stdout == "6\n"
    assert result.execution_time_ms == 12.0
    assert result.memory_used_mb == 2.0
    assert captured["url"].startswith("https://judge.example/submissions?")
    assert captured["headers"]["x-auth-token"] == "test-token"
    assert captured["payload"]["enable_network"] is False
    assert captured["payload"]["cpu_time_limit"] > 0
    assert captured["payload"]["memory_limit"] > 0


def test_judge_service_appends_stable_driver() -> None:
    source = build_python_source("def solve(arr):\n    return sum(arr)")

    assert "def solve(arr)" in source
    assert "_coderoad_main()" in source
    assert "eval(" not in source


def test_judge_module_does_not_import_subprocess() -> None:
    module_path = Path(__file__).parents[1] / "app" / "services" / "judge_service.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert "subprocess" not in imports
    assert JudgeService is not None
