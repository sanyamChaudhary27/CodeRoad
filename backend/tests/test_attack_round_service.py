from app.schemas.attack_round_schema import (
    AttackRoundRequest,
    AttackSolution,
    CandidateBatch,
    CandidateInput,
)
from app.services.attack_problem_registry import maximum_subarray
from app.services.attack_round_service import AttackRoundService
from app.services.counterexample_generator import GenerationResult
from app.services.judge_service import ExecutionResult


BUGGY = """def solve(arr):
    best = 0
    current = 0
    for value in arr:
        current = max(0, current + value)
        best = max(best, current)
    return best
"""

ROBUST = """def solve(arr):
    best = arr[0]
    current = arr[0]
    for value in arr[1:]:
        current = max(value, current + value)
        best = max(best, current)
    return best
"""


class SemanticFakeJudge:
    """Test double that models the two algorithms without executing source."""

    def run_python_solution(self, source_code: str, stdin: str) -> ExecutionResult:
        values = [int(value) for value in stdin.split()]
        if "return 0" in source_code and "best = 0" not in source_code:
            output = 0
        elif "best = 0" in source_code:
            best = current = 0
            for value in values:
                current = max(0, current + value)
                best = max(best, current)
            output = best
        else:
            output = maximum_subarray(values)
        return ExecutionResult(
            status_id=3,
            status="Accepted",
            stdout=f"{output}\n",
            stderr="",
            compile_output="",
            execution_time_ms=1.5,
            memory_used_mb=1.0,
        )


class FixedGenerator:
    def generate(self, problem, solution_a, solution_b) -> GenerationResult:
        del problem, solution_a, solution_b
        return GenerationResult(
            batch=CandidateBatch(
                candidates=[
                    CandidateInput(
                        values=[-5, -2, -8],
                        category="sign",
                        rationale="All-negative arrays expose empty-subarray initialization.",
                        targets_assumption="The optimum cannot be below zero.",
                    ),
                    CandidateInput(
                        values=[-5, -2, -8],
                        category="duplicate",
                        rationale="Duplicate should be removed.",
                        targets_assumption="Duplicate candidate.",
                    ),
                    CandidateInput(
                        values=[1000],
                        category="magnitude",
                        rationale="Invalid and must never reach execution.",
                        targets_assumption="Constraints are optional.",
                    ),
                ]
            ),
            source="nvidia-nim",
            model="deepseek-ai/deepseek-v4-pro",
            note="typed hypotheses",
        )


def make_request(solution_a: str = BUGGY, solution_b: str = ROBUST) -> AttackRoundRequest:
    return AttackRoundRequest(
        problem_id="max-subarray",
        solution_a=AttackSolution(label="Solution A", code=solution_a),
        solution_b=AttackSolution(label="Solution B", code=solution_b),
    )


def test_verified_counterexample_selects_robust_solution() -> None:
    service = AttackRoundService(judge=SemanticFakeJudge(), generator=FixedGenerator())

    result = service.analyze(make_request())

    assert result.baseline_passed is True
    assert all(trial.solution_a.passed and trial.solution_b.passed for trial in result.ordinary_trials)
    assert result.candidates_proposed == 3
    assert result.candidates_verified == 1
    assert len(result.attack_trials) == 1
    assert result.witness is not None
    assert result.witness.values == [-5, -2, -8]
    assert result.witness.expected_output == "-2"
    assert result.witness.solution_a.output == "0"
    assert result.witness.solution_b.output == "-2"
    assert result.winner == "solution_b"


def test_attack_generation_is_skipped_when_baseline_is_not_a_tie() -> None:
    always_zero = "def solve(arr):\n    return 0"
    service = AttackRoundService(judge=SemanticFakeJudge(), generator=FixedGenerator())

    result = service.analyze(make_request(solution_a=always_zero))

    assert result.baseline_passed is False
    assert result.winner == "baseline_failed"
    assert result.candidates_proposed == 0
    assert result.attack_trials == []
