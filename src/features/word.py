"""Features for the context-free CEFR word classifier."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyphen
import wordfreq

BASE_WORD_FEATURE_COLUMNS = [
    "char_length",
    "syllable_count",
    "vowel_count",
    "vowel_ratio",
    "wordfreq_zipf",
    "wordfreq_freq",
]

MORPHOLOGY_FEATURE_COLUMNS = [
    "suffix_tion",
    "suffix_ity",
    "suffix_ment",
    "suffix_able",
    "suffix_ible",
    "suffix_ology",
    "suffix_istic",
    "suffix_ize",
    "suffix_ness",
    "suffix_ive",
    "prefix_un",
    "prefix_in",
    "prefix_dis",
    "prefix_counter",
    "prefix_hyper",
    "prefix_anti",
]

WORD_FEATURE_COLUMNS = BASE_WORD_FEATURE_COLUMNS + MORPHOLOGY_FEATURE_COLUMNS

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


def extract_morphology_features(word: str) -> dict[str, int]:
    w = normalize_word(word)
    return {
        "suffix_tion": int((w.endswith("tion") or w.endswith("sion")) and len(w) > 6),
        "suffix_ity": int(w.endswith("ity") and len(w) > 5),
        "suffix_ment": int(w.endswith("ment") and len(w) > 6),
        "suffix_able": int(w.endswith("able") and len(w) > 6),
        "suffix_ible": int(w.endswith("ible") and len(w) > 6),
        "suffix_ology": int(w.endswith("ology") and len(w) > 7),
        "suffix_istic": int((w.endswith("istic") or w.endswith("ist")) and len(w) > 5),
        "suffix_ize": int((w.endswith("ize") or w.endswith("ise")) and len(w) > 5),
        "suffix_ness": int(w.endswith("ness") and len(w) > 6),
        "suffix_ive": int(w.endswith("ive") and len(w) > 5),
        "prefix_un": int(w.startswith("un") and len(w) > 4),
        "prefix_in": int(
            (
                w.startswith("in")
                or w.startswith("im")
                or w.startswith("il")
                or w.startswith("ir")
            )
            and len(w) > 4
        ),
        "prefix_dis": int(w.startswith("dis") and len(w) > 5),
        "prefix_counter": int(w.startswith("counter") and len(w) > 9),
        "prefix_hyper": int(w.startswith("hyper") and len(w) > 7),
        "prefix_anti": int(w.startswith("anti") and len(w) > 6),
    }


def extract_word_features(word: str, include_morphology: bool = True) -> pd.DataFrame:
    """Return the exact feature schema consumed by Model 2a."""
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
    if include_morphology:
        values.update(extract_morphology_features(normalized))
        cols = WORD_FEATURE_COLUMNS
    else:
        cols = BASE_WORD_FEATURE_COLUMNS

    frame = pd.DataFrame([values], columns=cols)
    return frame.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def extract_word_feature_table(
    words: pd.Series, include_morphology: bool = True
) -> pd.DataFrame:
    """Vector-friendly helper used by dataset builders and parity tests."""
    rows = [
        extract_word_features(word, include_morphology=include_morphology).iloc[0].to_dict()
        for word in words
    ]
    cols = WORD_FEATURE_COLUMNS if include_morphology else BASE_WORD_FEATURE_COLUMNS
    return pd.DataFrame(rows, columns=cols)
