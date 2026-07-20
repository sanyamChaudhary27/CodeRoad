from types import SimpleNamespace

from app.schemas.attack_round_schema import CandidateBatch, CandidateInput
from app.services.attack_problem_registry import MAX_SUBARRAY
from app.services.counterexample_generator import NvidiaNimCandidateGenerator


class FakeCompletions:
    def __init__(self) -> None:
        self.arguments = None

    def create(self, **kwargs):
        self.arguments = kwargs
        payload = CandidateBatch(
            candidates=[
                CandidateInput(
                    values=[-5, -2, -8],
                    category="sign",
                    rationale="All values are negative.",
                    targets_assumption="The optimum is non-negative.",
                )
            ]
        ).model_dump_json()
        return [SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=payload))])]


def test_nvidia_generator_uses_one_streaming_chat_completion() -> None:
    NvidiaNimCandidateGenerator._cache.clear()
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    generator = NvidiaNimCandidateGenerator(client=client)

    result = generator.generate(MAX_SUBARRAY, "solution a", "solution b")

    assert result.source == "nvidia-nim"
    assert result.batch.candidates[0].values == [-5, -2, -8]
    assert completions.arguments["stream"] is True
    assert completions.arguments["extra_body"]["chat_template_kwargs"]["thinking"] is False
    assert completions.arguments["max_tokens"] <= 1600
    assert len(completions.arguments["messages"]) == 1


def test_nvidia_generator_caches_identical_solution_pair() -> None:
    NvidiaNimCandidateGenerator._cache.clear()
    completions = FakeCompletions()
    generator = NvidiaNimCandidateGenerator(
        client=SimpleNamespace(chat=SimpleNamespace(completions=completions))
    )

    first = generator.generate(MAX_SUBARRAY, "same a", "same b")
    completions.arguments = None
    second = generator.generate(MAX_SUBARRAY, "same a", "same b")

    assert first.batch == second.batch
    assert completions.arguments is None
    assert "no new API credits" in second.note
