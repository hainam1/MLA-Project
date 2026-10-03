"""Experimental rubric-oriented features; the frozen v1 schema is unchanged.

These are automatic indicators, not verified learner errors. The module only
accepts an already parsed document and LanguageTool matches so one essay needs
one pass through each expensive tool.
"""

from __future__ import annotations

from collections import Counter
import math
from typing import Any, Iterable

from wordfreq import zipf_frequency

from mla_project.features.preprocessing import sentence_spans, word_tokens

V2_FEATURE_NAMES = (
    "content_word_low_frequency_ratio",
    "content_word_frequency_p25",
    "content_lemma_mattr",
    "detected_misspellings_per_100_words",
    "detected_spelling_rule_diversity",
    "detected_grammar_rule_diversity",
    "detected_repeated_grammar_rule_ratio",
    "mean_dependency_distance",
    "mean_sentence_tree_depth",
)

CONTENT_POS = frozenset({"NOUN", "PROPN", "VERB", "ADJ", "ADV"})
RARE_ZIPF_THRESHOLD = 4.0
MAT_TERMS = 50


def _moving_average_diversity(values: list[str], window: int = MAT_TERMS) -> float:
    if not values:
        return 0.0
    width = min(window, len(values))
    return float(
        sum(len(set(values[start : start + width])) / width for start in range(len(values) - width + 1))
        / (len(values) - width + 1)
    )


def _rule_id(match: object) -> str:
    return str(getattr(match, "ruleId", "") or "")


def _issue_type(match: object) -> str:
    return str(getattr(match, "ruleIssueType", "") or "").casefold()


def extract_v2_features(doc: Any, matches: Iterable[object]) -> dict[str, float]:
    """Return nine deterministic numeric candidates in the frozen v2 order."""
    words = word_tokens(doc)
    content = [token for token in words if token.pos_ in CONTENT_POS]
    frequencies = [
        zipf_frequency((token.lemma_ or token.text).casefold(), "en") for token in content
    ]
    lemmas = [(token.lemma_ or token.text).casefold() for token in content]
    all_matches = list(matches)
    spell_matches = [match for match in all_matches if _issue_type(match) == "misspelling"]
    grammar_matches = [match for match in all_matches if _issue_type(match) == "grammar"]
    spell_rules = Counter(_rule_id(match) for match in spell_matches)
    grammar_rules = Counter(_rule_id(match) for match in grammar_matches)

    dependency_distances = [
        abs(token.i - token.head.i)
        for token in doc
        if token.is_alpha and token.head.i != token.i
    ]
    depths: list[int] = []
    for sentence in sentence_spans(doc):
        token_depths = []
        for token in sentence:
            if not token.is_alpha:
                continue
            distance = 0
            current = token
            seen = {token.i}
            while current.head.i != current.i and current.head.i not in seen:
                current = current.head
                seen.add(current.i)
                distance += 1
            token_depths.append(distance)
        depths.append(max(token_depths, default=0))

    result = {
        "content_word_low_frequency_ratio": (
            sum(value < RARE_ZIPF_THRESHOLD for value in frequencies) / len(frequencies)
            if frequencies else 0.0
        ),
        "content_word_frequency_p25": (
            sorted(frequencies)[max(0, math.ceil(0.25 * len(frequencies)) - 1)]
            if frequencies else 0.0
        ),
        "content_lemma_mattr": _moving_average_diversity(lemmas),
        "detected_misspellings_per_100_words": 100 * len(spell_matches) / max(len(words), 1),
        "detected_spelling_rule_diversity": (
            len(spell_rules) / len(spell_matches) if spell_matches else 0.0
        ),
        "detected_grammar_rule_diversity": (
            len(grammar_rules) / len(grammar_matches) if grammar_matches else 0.0
        ),
        "detected_repeated_grammar_rule_ratio": (
            1 - len(grammar_rules) / len(grammar_matches) if grammar_matches else 0.0
        ),
        "mean_dependency_distance": (
            sum(dependency_distances) / len(dependency_distances)
            if dependency_distances else 0.0
        ),
        "mean_sentence_tree_depth": sum(depths) / len(depths),
    }
    if tuple(result) != V2_FEATURE_NAMES or not all(math.isfinite(v) for v in result.values()):
        raise RuntimeError("Invalid v2 feature schema or non-finite output.")
    return {name: float(result[name]) for name in V2_FEATURE_NAMES}
