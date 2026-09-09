import pytest

from src.inference import validate_sentence


def test_validate_sentence_normalizes_whitespace():
    assert validate_sentence("  This   is a sentence. ") == "This is a sentence."


@pytest.mark.parametrize("value", ["", "   ", "1234", "word"])
def test_validate_sentence_rejects_invalid_demo_input(value):
    with pytest.raises(ValueError):
        validate_sentence(value)
