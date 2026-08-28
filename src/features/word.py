"""Features for the context-free CEFR word classifier."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyphen
import wordfreq

WORD_FEATURE_COLUMNS = [
    "char_length",
    "syllable_count",
    "vowel_count",
    "vowel_ratio",
    "wordfreq_zipf",
    "wordfreq_freq",
]

_VOWELS = frozenset("aeiouy")
_HYPHENATOR = pyphen.Pyphen(lang="en_US")


def normalize_word(word: str) -> str:
    """Normalize a lexical item without changing its spelling."""
    return " ".join(str(word).strip().lower().split())


def count_syllables(word: str) -> int:
    normalized = normalize_word(word)
    if not normalized:
        return 1
    hyphenated = _HYPHENATOR.inserted(normalized)
    return max(1, len(hyphenated.split("-"))) if hyphenated else 1


def extract_word_features(word: str) -> pd.DataFrame:
    """Return the exact feature schema consumed by Model 2a.

    Only features available for arbitrary user input are included. Dataset-only
    Google N-gram values and context-dependent POS labels are deliberately
    excluded to prevent train-serving skew.
    """
    normalized = normalize_word(word)
    char_length = len(normalized)
    vowel_count = sum(char in _VOWELS for char in normalized)
    values = {
        "char_length": char_length,
        "syllable_count": count_syllables(normalized),
        "vowel_count": vowel_count,
        "vowel_ratio": round(vowel_count / max(1, char_length), 4),
        "wordfreq_zipf": round(wordfreq.zipf_frequency(normalized, "en"), 4),
        "wordfreq_freq": float(wordfreq.word_frequency(normalized, "en")),
    }
    frame = pd.DataFrame([values], columns=WORD_FEATURE_COLUMNS)
    return frame.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def extract_word_feature_table(words: pd.Series) -> pd.DataFrame:
    """Vector-friendly helper used by dataset builders and parity tests."""
    rows = [extract_word_features(word).iloc[0].to_dict() for word in words]
    return pd.DataFrame(rows, columns=WORD_FEATURE_COLUMNS)
