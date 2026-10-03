"""The three predeclared surface-length features."""

from __future__ import annotations

from typing import Any

from mla_project.features.preprocessing import sentence_spans, word_tokens


def extract_length_features(doc: Any) -> dict[str, float]:
    """Count alphabetic tokens and parser-delimited sentences in a spaCy document."""
    word_count = len(word_tokens(doc))
    sentence_count = len(sentence_spans(doc))
    return {
        "word_count": float(word_count),
        "sentence_count": float(sentence_count),
        "mean_sentence_length": float(word_count / sentence_count),
    }
