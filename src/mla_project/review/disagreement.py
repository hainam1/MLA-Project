"""Model disagreement measures, distinct from confidence or error probability."""

from __future__ import annotations


def model_disagreement(ridge_prediction: float, forest_prediction: float) -> float:
    """Return absolute prediction difference on the target's score scale."""
    return abs(float(ridge_prediction) - float(forest_prediction))


def review_priority(
    vocabulary_disagreement: float,
    grammar_disagreement: float,
    *,
    threshold: float,
) -> tuple[bool, list[str]]:
    """Flag targets whose model disagreement meets a declared review threshold."""
    reasons = []
    if vocabulary_disagreement >= threshold:
        reasons.append("vocabulary model disagreement meets the review threshold")
    if grammar_disagreement >= threshold:
        reasons.append("grammar model disagreement meets the review threshold")
    return bool(reasons), reasons
