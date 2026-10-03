"""Inference for a new essay with explicit teacher-review prioritization."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from mla_project.features.build_features import FeatureExtractor
from mla_project.models.predict import predict_model_set
from mla_project.review.disagreement import model_disagreement, review_priority


def predict_essay(
    text: str,
    *,
    extractor: FeatureExtractor,
    models: Mapping[str, Any],
    feature_columns: Sequence[str],
    review_threshold: float = 0.75,
) -> dict[str, Any]:
    """Score one essay and report disagreement as a review signal, not confidence."""
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
        "notice": "Model disagreement is a triage signal, not an error probability or confidence score.",
    }
