from types import SimpleNamespace

from app.schemas.attack_round_schema import CandidateBatch, CandidateInput
from app.services.attack_problem_registry import MAX_SUBARRAY
from app.services.counterexample_generator import OpenAICandidateGenerator


class FakeResponses:
    def __init__(self) -> None:
        self.arguments = None

    def parse(self, **kwargs):
        self.arguments = kwargs
        return SimpleNamespace(
            output_parsed=CandidateBatch(
                candidates=[
                    CandidateInput(
                        values=[-5, -2, -8],
                        category="sign",
                        rationale="All values are negative.",
                        targets_assumption="The optimum is non-negative.",
                    )
                ]
            )
        )


def test_openai_generator_uses_one_typed_responses_call() -> None:
    OpenAICandidateGenerator._cache.clear()
    responses = FakeResponses()
    client = SimpleNamespace(responses=responses)
    generator = OpenAICandidateGenerator(client=client)

    result = generator.generate(MAX_SUBARRAY, "solution a", "solution b")

    assert result.source == "openai"
    assert result.batch.candidates[0].values == [-5, -2, -8]
    assert responses.arguments["text_format"] is CandidateBatch
    assert responses.arguments["store"] is False
    assert responses.arguments["max_output_tokens"] <= 1600
    assert len(responses.arguments["input"]) == 2


def test_openai_generator_caches_identical_solution_pair() -> None:
    OpenAICandidateGenerator._cache.clear()
    responses = FakeResponses()
    generator = OpenAICandidateGenerator(client=SimpleNamespace(responses=responses))

    first = generator.generate(MAX_SUBARRAY, "same a", "same b")
    responses.arguments = None
    second = generator.generate(MAX_SUBARRAY, "same a", "same b")

    assert first.batch == second.batch
    assert responses.arguments is None
    assert "no new API credits" in second.note
