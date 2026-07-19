"""API and model-output schemas for the Adversarial Test Arena."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


AttackCategory = Literal[
    "boundary",
    "sign",
    "ordering",
    "duplicate",
    "magnitude",
    "structure",
]


class CandidateInput(BaseModel):
    """One inspectable counterexample hypothesis proposed by the model."""

    values: list[int] = Field(min_length=1, max_length=30)
    category: AttackCategory
    rationale: str = Field(min_length=1, max_length=240)
    targets_assumption: str = Field(min_length=1, max_length=240)


class CandidateBatch(BaseModel):
    """Structured output returned by the configured OpenAI model in one bounded call."""

    candidates: list[CandidateInput] = Field(min_length=1, max_length=12)


class AttackSolution(BaseModel):
    label: str = Field(min_length=1, max_length=40)
    code: str = Field(min_length=1, max_length=50_000)
    language: Literal["python"] = "python"

    @field_validator("label")
    @classmethod
    def normalize_label(cls, value: str) -> str:
        return value.strip()


class AttackRoundRequest(BaseModel):
    problem_id: Literal["max-subarray"] = "max-subarray"
    solution_a: AttackSolution
    solution_b: AttackSolution


class AttackProblem(BaseModel):
    id: str
    title: str
    statement: str
    input_format: str
    constraints: list[str]
    ordinary_tests: list[list[int]]
    boilerplate_code: str


class ExecutionView(BaseModel):
    status: str
    output: str
    execution_time_ms: Optional[float] = None
    passed: bool
    diagnostic: Optional[str] = None


class BaselineTrial(BaseModel):
    values: list[int]
    expected_output: str
    solution_a: ExecutionView
    solution_b: ExecutionView


class AttackTrial(BaseModel):
    values: list[int]
    expected_output: str
    category: AttackCategory
    rationale: str
    targets_assumption: str
    solution_a: ExecutionView
    solution_b: ExecutionView
    distinguished: bool


class AttackRoundResponse(BaseModel):
    problem: AttackProblem
    generation_source: Literal["openai", "deterministic-fallback"]
    model: Optional[str] = None
    generation_note: str
    baseline_passed: bool
    ordinary_trials: list[BaselineTrial]
    attack_trials: list[AttackTrial]
    candidates_proposed: int
    candidates_verified: int
    witness: Optional[AttackTrial] = None
    winner: Literal["solution_a", "solution_b", "draw", "baseline_failed"]
    verdict: str
