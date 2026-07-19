"""Isolated submission execution through a separately hosted Judge0 runner.

The API process must never execute player-provided code. The old implementation
wrote source to a temporary file and invoked ``python3`` with ``subprocess`` on
the web server. This module intentionally fails closed when Judge0 is not
configured.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import logging
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Challenge, Match, Submission, SubmissionStatus

logger = logging.getLogger(__name__)


class CodeExecutionUnavailable(RuntimeError):
    """Raised when the isolated runner is unavailable or not configured."""


@dataclass(frozen=True)
class ExecutionResult:
    """Normalized result returned by the isolated execution service."""

    status_id: int
    status: str
    stdout: str
    stderr: str
    compile_output: str
    execution_time_ms: Optional[float]
    memory_used_mb: Optional[float]

    @property
    def accepted(self) -> bool:
        # Judge0 status 3 is Accepted. Output is compared by CodeRoad so this
        # only means the program completed successfully.
        return self.status_id == 3

    @property
    def diagnostic(self) -> str:
        return (self.compile_output or self.stderr or self.status).strip()[:500]


class Judge0Client:
    """Small, synchronous Judge0 adapter used by background submission jobs."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        auth_header: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.base_url = (base_url if base_url is not None else settings.JUDGE0_API_URL).rstrip("/")
        self.auth_token = auth_token if auth_token is not None else settings.JUDGE0_AUTH_TOKEN
        self.auth_header = auth_header or settings.JUDGE0_AUTH_HEADER
        self.timeout_seconds = timeout_seconds or max(
            10.0,
            float(settings.CODE_EXECUTION_TIMEOUT_SECONDS) + 5.0,
        )
        self.transport = transport

    @property
    def configured(self) -> bool:
        return self.base_url.startswith(("https://", "http://"))

    def execute_python(self, source_code: str, stdin: str) -> ExecutionResult:
        if not self.configured:
            raise CodeExecutionUnavailable(
                "Isolated execution is not configured. Set JUDGE0_API_URL to a separately hosted runner."
            )

        headers = {"Accept": "application/json"}
        if self.auth_token:
            headers[self.auth_header] = self.auth_token

        payload = {
            "source_code": source_code,
            "language_id": settings.JUDGE0_PYTHON_LANGUAGE_ID,
            "stdin": stdin,
            "cpu_time_limit": settings.CODE_EXECUTION_TIMEOUT_SECONDS,
            "wall_time_limit": settings.CODE_EXECUTION_TIMEOUT_SECONDS + 1,
            "memory_limit": settings.CODE_MEMORY_LIMIT_MB * 1024,
            "max_file_size": 1024,
            "enable_network": False,
        }

        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                transport=self.transport,
                follow_redirects=False,
            ) as client:
                response = client.post(
                    f"{self.base_url}/submissions",
                    params={"base64_encoded": "false", "wait": "true"},
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise CodeExecutionUnavailable("The isolated execution service could not complete the request.") from exc

        status_data = data.get("status") or {}
        try:
            status_id = int(status_data.get("id", 0))
        except (TypeError, ValueError):
            status_id = 0

        execution_time_ms: Optional[float] = None
        if data.get("time") not in (None, ""):
            try:
                execution_time_ms = float(data["time"]) * 1000
            except (TypeError, ValueError):
                pass

        memory_used_mb: Optional[float] = None
        if data.get("memory") not in (None, ""):
            try:
                # Judge0 reports memory in kilobytes.
                memory_used_mb = float(data["memory"]) / 1024
            except (TypeError, ValueError):
                pass

        return ExecutionResult(
            status_id=status_id,
            status=str(status_data.get("description") or "Unknown runner status"),
            stdout=str(data.get("stdout") or ""),
            stderr=str(data.get("stderr") or ""),
            compile_output=str(data.get("compile_output") or ""),
            execution_time_ms=execution_time_ms,
            memory_used_mb=memory_used_mb,
        )


PYTHON_DRIVER = r'''
import inspect as _inspect
import sys as _sys

def _coderoad_main():
    raw_input = _sys.stdin.read().strip()
    try:
        input_data = list(map(int, raw_input.split())) if raw_input else []
    except ValueError:
        input_data = raw_input.split()

    if "solve" not in globals():
        raise RuntimeError("solve function not found")

    solve_func = globals()["solve"]
    params = list(_inspect.signature(solve_func).parameters.values())

    if len(params) == 1:
        result = solve_func(input_data)
    elif len(params) == 2 and len(input_data) >= 2:
        result = solve_func(input_data[:-1], input_data[-1])
    else:
        result = solve_func(*input_data[:len(params)])

    if result is None:
        print("")
    elif isinstance(result, (list, tuple)):
        print(" ".join(str(value) for value in result))
    elif isinstance(result, bool):
        print(str(result).lower())
    else:
        print(result)

_coderoad_main()
'''


def build_python_source(player_code: str) -> str:
    """Append the stable CodeRoad driver without interpolating user input."""

    return f"{player_code.rstrip()}\n\n{PYTHON_DRIVER}"


class JudgeService:
    """Evaluate submissions through the isolated execution boundary."""

    def __init__(self, runner: Optional[Judge0Client] = None) -> None:
        self.runner = runner or Judge0Client()

    def run_python_solution(self, source_code: str, stdin: str) -> ExecutionResult:
        """Run one solution/input pair through the isolated service."""

        return self.runner.execute_python(build_python_source(source_code), stdin)

    def evaluate_submission(self, db: Session, submission_id: str) -> None:
        logger.info("Evaluating submission %s", submission_id)
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            logger.error("Submission %s not found", submission_id)
            return

        match = db.query(Match).filter(Match.id == submission.match_id).first()
        challenge = (
            db.query(Challenge).filter(Challenge.id == match.challenge_id).first()
            if match
            else None
        )
        if not match or not challenge:
            self._finish_with_error(db, submission, "Match or challenge not found")
            return

        language = submission.language.value if hasattr(submission.language, "value") else str(submission.language)
        if language.lower() != "python":
            submission.status = SubmissionStatus.COMPILE_ERROR
            submission.error_message = f"Unsupported language: {language}"
            submission.completed_at = datetime.utcnow()
            db.commit()
            return

        try:
            test_cases = json.loads(challenge.test_cases or "[]")
        except (TypeError, json.JSONDecodeError):
            test_cases = []
        if not test_cases:
            self._finish_with_error(db, submission, "Challenge has no executable test cases")
            return

        submission.status = SubmissionStatus.EXECUTING
        submission.test_cases_total = len(test_cases)
        db.commit()

        passed = 0
        times: list[float] = []
        peak_memory = 0.0

        try:
            for test_case in test_cases:
                input_data = str(test_case.get("input", ""))
                expected_output = str(test_case.get("expected_output", "")).strip()
                result = self.run_python_solution(submission.code, input_data)

                if result.execution_time_ms is not None:
                    times.append(result.execution_time_ms)
                if result.memory_used_mb is not None:
                    peak_memory = max(peak_memory, result.memory_used_mb)

                if not result.accepted:
                    self._apply_runner_failure(submission, result)
                    break

                actual_output = result.stdout.strip()
                if actual_output == expected_output:
                    passed += 1
                else:
                    submission.error_message = (
                        f"Wrong answer: expected {expected_output!r}, received {actual_output!r}"
                    )[:500]

            submission.test_cases_passed = passed
            if times:
                submission.execution_time_ms = int(sum(times) / len(times))
            if peak_memory:
                submission.memory_used_mb = peak_memory

            if submission.status == SubmissionStatus.EXECUTING:
                submission.status = (
                    SubmissionStatus.SUCCESS
                    if passed == len(test_cases)
                    else SubmissionStatus.RUNTIME_ERROR
                )
        except CodeExecutionUnavailable as exc:
            submission.status = SubmissionStatus.SECURITY_VIOLATION
            submission.error_message = str(exc)[:500]
        except Exception:
            logger.exception("Unexpected isolated judge failure for %s", submission.id)
            submission.status = SubmissionStatus.RUNTIME_ERROR
            submission.error_message = "Internal judge error"
        finally:
            submission.completed_at = datetime.utcnow()
            db.commit()

        logger.info(
            "Submission %s evaluated in isolated runner: %s/%s",
            submission.id,
            passed,
            len(test_cases),
        )

    @staticmethod
    def _apply_runner_failure(submission: Submission, result: ExecutionResult) -> None:
        if result.status_id == 5:
            submission.status = SubmissionStatus.TIMEOUT
        elif result.status_id == 6:
            submission.status = SubmissionStatus.COMPILE_ERROR
        elif result.status_id in {7, 8, 9, 10, 11, 12}:
            submission.status = SubmissionStatus.RUNTIME_ERROR
        else:
            submission.status = SubmissionStatus.RUNTIME_ERROR
        submission.error_message = result.diagnostic

    @staticmethod
    def _finish_with_error(db: Session, submission: Submission, message: str) -> None:
        submission.status = SubmissionStatus.RUNTIME_ERROR
        submission.error_message = message
        submission.completed_at = datetime.utcnow()
        db.commit()
