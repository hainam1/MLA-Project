"""Inference for a new essay with explicit teacher-review prioritization."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from numbers import Real
from typing import Any

import pandas as pd

from mla_project.features.build_features import FeatureExtractor
from mla_project.evaluation.phase8 import review_count
from mla_project.models.predict import predict_model_set
from mla_project.review.disagreement import model_disagreement, review_priority


def predict_essay(
    text: str,
    *,
    extractor: FeatureExtractor,
    models: Mapping[str, Any],
    feature_columns: Sequence[str],
    review_threshold: float | None = None,
) -> dict[str, Any]:
    """Score one essay. Optional legacy threshold flags are not budget-based review.

    Without an explicit threshold the legacy flag is None; use prioritize_essay_batch
    for the review-first policy. Consensus remains an auxiliary arithmetic mean.
    """
    extracted = extractor.transform(pd.Series([text]))
    missing = sorted(set(feature_columns).difference(extracted.columns))
    if missing:
        raise ValueError(f"Extractor did not produce trained features: {missing}")
    features = extracted.loc[:, list(feature_columns)]
    predictions = predict_model_set(models, features)
    vocabulary_disagreement = model_disagreement(
        predictions["ridge_vocabulary"], predictions["random_forest_vocabulary"]
    )
    grammar_disagreement = model_disagreement(
        predictions["ridge_grammar"], predictions["random_forest_grammar"]
    )
    vocabulary_consensus = (
        predictions["ridge_vocabulary"] + predictions["random_forest_vocabulary"]
    ) / 2.0
    grammar_consensus = (predictions["ridge_grammar"] + predictions["random_forest_grammar"]) / 2.0
    review_priority_score = max(vocabulary_disagreement, grammar_disagreement)
    prioritized, reasons = None, []
    if review_threshold is not None:
        if isinstance(review_threshold, bool) or not isinstance(review_threshold, Real):
            raise ValueError("review_threshold must be a finite non-negative number or None.")
        if not math.isfinite(review_threshold) or review_threshold < 0:
            raise ValueError("review_threshold must be a finite non-negative number or None.")
        prioritized, reasons = review_priority(
            vocabulary_disagreement, grammar_disagreement, threshold=review_threshold
        )
    return {
        "scores": {
            "vocabulary": {
                "ridge": predictions["ridge_vocabulary"],
                "random_forest": predictions["random_forest_vocabulary"],
                "consensus": vocabulary_consensus,
            },
            "grammar": {
                "ridge": predictions["ridge_grammar"],
                "random_forest": predictions["random_forest_grammar"],
                "consensus": grammar_consensus,
            },
        },
        "disagreement": {
            "vocabulary": vocabulary_disagreement,
            "grammar": grammar_disagreement,
        },
        "review_priority_score": review_priority_score,
        "priority_for_teacher_review": prioritized,
        "review_reasons": reasons,
        "notice": (
            "Model disagreement is a triage signal, not an error probability or confidence score. "
            "The optional legacy threshold flag is reference behavior, not a Top-20% policy. "
            "Teachers retain authority over every official grade."
        ),
    }


def prioritize_essay_batch(
    essays: Mapping[str, str],
    *,
    extractor: FeatureExtractor,
    models: Mapping[str, Any],
    feature_columns: Sequence[str],
    review_budget: float = 0.20,
) -> list[dict[str, Any]]:
    """Rank ID-to-text essays by descending disagreement, ties by string essay ID.

    Select ceil(N * budget), reusing the frozen evaluation convention for positive
    budgets. Zero budget selects none; an empty batch returns []. All essays still
    require teacher grading. IDs must be unique non-empty strings.
    """
    if isinstance(review_budget, bool) or not isinstance(review_budget, Real):
        raise ValueError("review_budget must be a finite number in [0, 1].")
    if not math.isfinite(review_budget) or not 0 <= review_budget <= 1:
        raise ValueError("review_budget must be a finite number in [0, 1].")
    if not isinstance(essays, Mapping):
        raise ValueError("essays must be a mapping of unique string essay IDs to text.")
    if any(not isinstance(key, str) or not key.strip() for key in essays):
        raise ValueError("essay IDs must be non-empty strings.")
    if any(not isinstance(value, str) for value in essays.values()):
        raise ValueError("essay text must be a string.")
    rows = []
    for essay_id, text in essays.items():
        result = predict_essay(
            text, extractor=extractor, models=models, feature_columns=feature_columns
        )
        if not math.isfinite(result["review_priority_score"]):
            raise ValueError("Review priority scores must be finite.")
        rows.append({"essay_id": essay_id, **result})
    rows.sort(key=lambda row: (-row["review_priority_score"], row["essay_id"]))
    count = review_count(len(rows), review_budget) if rows and review_budget > 0 else 0
    for rank, row in enumerate(rows, start=1):
        row.update(rank=rank, review_first=rank <= count)
    return rows
