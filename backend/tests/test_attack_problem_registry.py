import pytest

from app.services.attack_problem_registry import MAX_SUBARRAY, maximum_subarray


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([4, -1, 2, 1], 6),
        ([-5, -2, -8], -2),
        ([0, -1], 0),
        ([100], 100),
        ([2, -1, -2, 2], 2),
    ],
)
def test_maximum_subarray_oracle(values: list[int], expected: int) -> None:
    assert maximum_subarray(values) == expected


def test_contract_rejects_empty_and_out_of_range_inputs() -> None:
    with pytest.raises(ValueError, match="input length"):
        MAX_SUBARRAY.validate([])

    with pytest.raises(ValueError, match="between -100 and 100"):
        MAX_SUBARRAY.validate([101])


def test_contract_formats_verified_stdin_and_output() -> None:
    values = [-5, -2, -8]

    assert MAX_SUBARRAY.stdin(values) == "-5 -2 -8"
    assert MAX_SUBARRAY.expected_output(values) == "-2"
