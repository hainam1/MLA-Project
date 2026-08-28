import pytest

from src.pipeline.predict_cefr import detect_language


@pytest.mark.parametrize(
    "text",
    [
        "to do",
        "to be or not to be",
        "do it to me",
        "go to school",
        "The quick brown fox jumps over the lazy dog.",
    ],
)
def test_valid_english_is_not_blocked(text):
    is_english, _, language = detect_language(text)
    assert is_english
    assert language == "english"


@pytest.mark.parametrize(
    "text",
    ["tôi muốn học tiếng Anh", "tao ten la hieu", "toi muon hoc machine learning"],
)
def test_vietnamese_is_blocked(text):
    is_english, _, language = detect_language(text)
    assert not is_english
    assert language == "vietnamese"
