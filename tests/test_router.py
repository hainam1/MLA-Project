import pytest

from src.pipeline.input_type_detector import detect_input_type, validate_vocabulary_input


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("persevere", "word_mode"),
        ("look after", "word_mode"),
        ("look forward to", "word_mode"),
        ("I am.", "sentence_mode"),
        ("Why not?", "sentence_mode"),
        ("Stop it!", "sentence_mode"),
        ("cats like drinking milk", "sentence_mode"),
        ("", "invalid_input"),
        ("   ", "invalid_input"),
        (None, "invalid_input"),
    ],
)
def test_detect_input_type(text, expected):
    assert detect_input_type(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("học", True),
        ("quả táo", True),
        ("máy học", True),
        ("Tôi học tiếng Anh", False),
        ("học.", False),
        ("", False),
        (None, False),
    ],
)
def test_validate_vocabulary_only_contract(text, expected):
    valid, _ = validate_vocabulary_input(text)
    assert valid is expected
