"""Deterministic challenge contracts used by the Adversarial Test Arena.

Every model-proposed input is validated by one of these contracts. Adding a new
problem requires an explicit parser/validator/oracle rather than trusting a
language model's expected output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..schemas.attack_round_schema import AttackProblem


def maximum_subarray(values: list[int]) -> int:
    """Return the non-empty contiguous subarray's maximum sum (Kadane)."""

    if not values:
        raise ValueError("values must contain at least one integer")
    best = current = values[0]
    for value in values[1:]:
        current = max(value, current + value)
        best = max(best, current)
    return best


@dataclass(frozen=True)
class ProblemContract:
    public: AttackProblem
    ordinary_tests: tuple[tuple[int, ...], ...]
    oracle: Callable[[list[int]], int]
    minimum_value: int
    maximum_value: int
    minimum_length: int
    maximum_length: int

    def validate(self, values: list[int]) -> tuple[int, ...]:
        if not self.minimum_length <= len(values) <= self.maximum_length:
            raise ValueError(
                f"input length must be between {self.minimum_length} and {self.maximum_length}"
            )
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise ValueError("every input value must be an integer")
        if any(value < self.minimum_value or value > self.maximum_value for value in values):
            raise ValueError(
                f"values must be between {self.minimum_value} and {self.maximum_value}"
            )
        return tuple(values)

    def expected_output(self, values: list[int]) -> str:
        validated = list(self.validate(values))
        return str(self.oracle(validated))

    def stdin(self, values: list[int]) -> str:
        validated = self.validate(values)
        return " ".join(str(value) for value in validated)


MAX_SUBARRAY = ProblemContract(
    public=AttackProblem(
        id="max-subarray",
        title="Maximum Subarray",
        statement=(
            "Given a non-empty array of integers, return the largest possible sum "
            "of a contiguous subarray."
        ),
        input_format="One line of space-separated integers; solve(arr) returns one integer.",
        constraints=["1 ≤ n ≤ 30", "-100 ≤ arr[i] ≤ 100", "The subarray must be non-empty"],
        ordinary_tests=[[4, -1, 2, 1], [1, 2, 3], [-2, 3, -1], [5]],
        boilerplate_code=(
            "def solve(arr):\n"
            "    # Return the maximum sum of a non-empty contiguous subarray.\n"
            "    raise NotImplementedError\n"
        ),
    ),
    ordinary_tests=((4, -1, 2, 1), (1, 2, 3), (-2, 3, -1), (5,)),
    oracle=maximum_subarray,
    minimum_value=-100,
    maximum_value=100,
    minimum_length=1,
    maximum_length=30,
)


PROBLEMS: dict[str, ProblemContract] = {MAX_SUBARRAY.public.id: MAX_SUBARRAY}


def get_problem(problem_id: str) -> ProblemContract:
    try:
        return PROBLEMS[problem_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported adversarial problem: {problem_id}") from exc
