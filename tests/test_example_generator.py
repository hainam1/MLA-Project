import pytest

from src.models.example_generator.service import build_prompt, contains_target


def test_build_prompt_contains_word_and_level():
    prompt = build_prompt("scientific", "B2")
    assert "scientific" in prompt
    assert "B2" in prompt


@pytest.mark.parametrize(
    ("sentence", "word", "expected"),
    [
        ("Scientific research matters.", "scientific", True),
        ("The artist opened a gallery.", "art", False),
        ("Air quality is improving.", "air quality", True),
    ],
)
def test_contains_target_uses_word_boundaries(sentence, word, expected):
    assert contains_target(sentence, word) is expected


def test_build_prompt_uses_requested_level_not_predicted_level():
    assert "C1" in build_prompt("beneficial", "C1")
