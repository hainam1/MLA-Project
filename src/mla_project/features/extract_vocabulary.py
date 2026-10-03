"""The six predeclared vocabulary features."""

from __future__ import annotations

from typing import Any

from wordfreq import zipf_frequency

from mla_project.features.preprocessing import word_tokens


def extract_vocabulary_features(
    doc: Any,
    *,
    mtld_threshold: float = 0.72,
    mtld_min_tokens: int = 10,
    mattr_window: int = 50,
) -> dict[str, float]:
    """Extract richness, frequency, length, density, and noun-diversity measures."""
    word_objects = word_tokens(doc)
    tokens = [token.text.casefold() for token in word_objects]
    if not tokens:
        return {
            "mtld": 0.0,
            "mattr": 0.0,
            "mean_word_frequency": 0.0,
            "mean_word_length": 0.0,
            "lexical_density": 0.0,
            "noun_diversity": 0.0,
        }

    try:
        from lexicalrichness import LexicalRichness

        richness = LexicalRichness(" ".join(tokens))
        mtld = (
            float(richness.mtld(threshold=mtld_threshold))
            if len(tokens) >= mtld_min_tokens
            else 0.0
        )
        mattr = (
            float(richness.mattr(window_size=min(mattr_window, len(tokens))))
            if len(tokens) >= 2
            else 0.0
        )
    except (ImportError, ZeroDivisionError, ValueError, TypeError):
        mtld = 0.0
        mattr = len(set(tokens)) / len(tokens) if len(tokens) >= 2 else 0.0

    content_pos = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}
    content_count = sum(token.pos_ in content_pos for token in word_objects)
    nouns = [
        (token.lemma_ or token.text).casefold()
        for token in word_objects
        if token.pos_ in {"NOUN", "PROPN"}
    ]
    frequencies = [zipf_frequency(token, "en") for token in tokens]
    return {
        "mtld": mtld,
        "mattr": mattr,
        "mean_word_frequency": float(sum(frequencies) / len(frequencies)),
        "mean_word_length": float(sum(map(len, tokens)) / len(tokens)),
        "lexical_density": float(content_count / len(tokens)),
        "noun_diversity": float(len(set(nouns)) / len(nouns)) if nouns else 0.0,
    }
