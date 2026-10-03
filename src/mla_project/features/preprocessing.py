"""Shared, deterministic text preparation for all feature groups."""

from __future__ import annotations

import re
import unicodedata
from typing import Any


def clean_text(text: str) -> str:
    """Normalize Unicode and whitespace without correcting the learner's writing."""
    if not isinstance(text, str):
        raise TypeError("Essay text must be a string.")
    cleaned = unicodedata.normalize("NFKC", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        raise ValueError("Essay text must be non-empty after cleaning.")
    return cleaned


def word_tokens(doc: Any) -> list[Any]:
    """Return alphabetic spaCy tokens used as the common word denominator."""
    return [token for token in doc if token.is_alpha]


def sentence_spans(doc: Any) -> list[Any]:
    """Return parser-provided sentence spans and fail loudly if unavailable."""
    try:
        sentences = list(doc.sents)
    except (ValueError, AttributeError) as exc:
        raise RuntimeError(
            "The spaCy pipeline must provide sentence boundaries (parser or sentencizer)."
        ) from exc
    if not sentences:
        raise RuntimeError("No sentence boundary was produced for a non-empty essay.")
    return sentences
