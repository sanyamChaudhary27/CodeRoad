"""Core orchestration for CodeRoad's Adversarial Test Arena."""

from __future__ import annotations

from typing import Iterable

from ..config import settings
from ..schemas.attack_round_schema import (
    AttackRoundRequest,
    AttackRoundResponse,
    AttackTrial,
    BaselineTrial,
    CandidateInput,
    ExecutionView,
)
from .attack_problem_registry import ProblemContract, get_problem
from .counterexample_generator import CandidateGenerator, ResilientCandidateGenerator
from .judge_service import ExecutionResult, JudgeService


class AttackRoundService:
    def __init__(
        self,
        judge: JudgeService | None = None,
        generator: CandidateGenerator | None = None,
    ) -> None:
        self.judge = judge or JudgeService()
        self.generator = generator or ResilientCandidateGenerator()

    def analyze(self, request: AttackRoundRequest) -> AttackRoundResponse:
        problem = get_problem(request.problem_id)
        ordinary_trials = self._run_baseline(
            problem,
            request.solution_a.code,
            request.solution_b.code,
        )
        baseline_passed = all(
            trial.solution_a.passed and trial.solution_b.passed
            for trial in ordinary_trials
        )
        if not baseline_passed:
            return AttackRoundResponse(
                problem=problem.public,
                generation_source="deterministic-fallback",
                generation_note=(
                    "Attack generation was skipped because both solutions must pass the ordinary "
                    "suite before a robustness tie-break."
                ),
                baseline_passed=False,
                ordinary_trials=ordinary_trials,
                attack_trials=[],
                candidates_proposed=0,
                candidates_verified=0,
                winner="baseline_failed",
                verdict="At least one solution does not pass the ordinary test suite.",
            )

        generated = self.generator.generate(
            problem,
            request.solution_a.code,
            request.solution_b.code,
        )
        proposed = generated.batch.candidates[: settings.ATTACK_ROUND_MAX_CANDIDATES]
        verified = list(self._verified_candidates(problem, proposed))
        attack_trials = self._run_attack_trials(
            problem,
            verified,
            request.solution_a.code,
            request.solution_b.code,
        )
        witness = next((trial for trial in attack_trials if trial.distinguished), None)

        if witness and witness.solution_a.passed:
            winner = "solution_a"
            verdict = (
                f"{request.solution_a.label} survived the verified counterexample that broke "
                f"{request.solution_b.label}."
            )
        elif witness and witness.solution_b.passed:
            winner = "solution_b"
            verdict = (
                f"{request.solution_b.label} survived the verified counterexample that broke "
                f"{request.solution_a.label}."
            )
        else:
            winner = "draw"
            verdict = "No verified candidate distinguished the two solutions in this round."

        return AttackRoundResponse(
            problem=problem.public,
            generation_source=generated.source,
            model=generated.model,
            generation_note=generated.note,
            baseline_passed=True,
            ordinary_trials=ordinary_trials,
            attack_trials=attack_trials,
            candidates_proposed=len(proposed),
            candidates_verified=len(verified),
            witness=witness,
            winner=winner,
            verdict=verdict,
        )

    def _run_baseline(
        self,
        problem: ProblemContract,
        solution_a: str,
        solution_b: str,
    ) -> list[BaselineTrial]:
        trials: list[BaselineTrial] = []
        for values_tuple in problem.ordinary_tests:
            values = list(values_tuple)
            expected = problem.expected_output(values)
            trials.append(
                BaselineTrial(
                    values=values,
                    expected_output=expected,
                    solution_a=self._execute(solution_a, problem.stdin(values), expected),
                    solution_b=self._execute(solution_b, problem.stdin(values), expected),
                )
            )
        return trials

    def _verified_candidates(
        self,
        problem: ProblemContract,
        candidates: Iterable[CandidateInput],
    ) -> Iterable[CandidateInput]:
        ordinary = set(problem.ordinary_tests)
        seen: set[tuple[int, ...]] = set()
        for candidate in candidates:
            try:
                normalized = problem.validate(candidate.values)
            except ValueError:
                continue
            if normalized in ordinary or normalized in seen:
                continue
            seen.add(normalized)
            yield candidate.model_copy(update={"values": list(normalized)})

    def _run_attack_trials(
        self,
        problem: ProblemContract,
        candidates: Iterable[CandidateInput],
        solution_a: str,
        solution_b: str,
    ) -> list[AttackTrial]:
        trials: list[AttackTrial] = []
        for candidate in candidates:
            expected = problem.expected_output(candidate.values)
            result_a = self._execute(solution_a, problem.stdin(candidate.values), expected)
            result_b = self._execute(solution_b, problem.stdin(candidate.values), expected)
            trials.append(
                AttackTrial(
                    values=candidate.values,
                    expected_output=expected,
                    category=candidate.category,
                    rationale=candidate.rationale,
                    targets_assumption=candidate.targets_assumption,
                    solution_a=result_a,
                    solution_b=result_b,
                    distinguished=result_a.passed != result_b.passed,
                )
            )
        return trials

    def _execute(self, source_code: str, stdin: str, expected: str) -> ExecutionView:
        result: ExecutionResult = self.judge.run_python_solution(source_code, stdin)
        actual = result.stdout.strip()
        passed = result.accepted and actual == expected
        diagnostic = None
        if not result.accepted:
            diagnostic = result.diagnostic
        elif not passed:
            diagnostic = f"Expected {expected!r}, received {actual!r}"
        return ExecutionView(
            status=result.status,
            output=actual,
            execution_time_ms=result.execution_time_ms,
            passed=passed,
            diagnostic=diagnostic,
        )
