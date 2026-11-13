from binary_tools import to_binary
import pytest


def test_known_answers():
    assert to_binary(0) == "0"
    assert to_binary(1) == "1"
    assert to_binary(2) == "10"
    assert to_binary(5) == "101"
    assert to_binary(6) == "110"
    assert to_binary(13) == "1101"
    assert to_binary(255) == "11111111"


def test_matches_python_on_a_thousand_numbers():
    for n in range(0, 1001):
        assert to_binary(n) == bin(n)[2:]


@pytest.mark.parametrize("bad", [-1, 2.5, "5", True])
def test_bad_input_is_refused(bad):
    with pytest.raises(ValueError):
        to_binary(bad)