"""Leakage-aware model-train/validation splitting for the official training file."""

from __future__ import annotations

import hashlib
import re

import pandas as pd
from sklearn.model_selection import train_test_split


def normalized_text_hash(text: str) -> str:
    """Hash text after case-folding, trimming, and collapsing whitespace."""
    normalized = re.sub(r"\s+", " ", text.strip().casefold())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def make_splits(
    frame: pd.DataFrame,
    *,
    validation_size: float = 0.20,
    random_seed: int = 42,
    stratify_column: str = "prompt_id",
) -> pd.DataFrame:
    """Split official-train rows into model-train and validation partitions.

    Exact normalized-text duplicates are grouped. The official test file is deliberately not
    accepted by this function and must remain the source-provided final partition.
    """
    if validation_size <= 0 or validation_size >= 1:
        raise ValueError("validation_size must be between 0 and 1.")
    required = {"essay_id", "essay_text", stratify_column}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing split columns: {sorted(missing)}")
    if frame["essay_id"].duplicated().any():
        raise ValueError("essay_id must be unique before splitting.")
    if frame[stratify_column].isna().any():
        raise ValueError(f"{stratify_column} must be complete for stratified splitting.")

    working = frame[["essay_id", "essay_text", stratify_column]].copy()
    working["text_group"] = working["essay_text"].map(normalized_text_hash)
    group_rows = []
    for group_hash, group in working.groupby("text_group", sort=True):
        group_rows.append(
            {
                "text_group": group_hash,
                "stratum": str(group[stratify_column].value_counts().index[0]),
            }
        )
    groups = pd.DataFrame(group_rows)
    if groups["stratum"].value_counts().min() < 2:
        raise ValueError("Every stratification value needs at least two distinct text groups.")

    model_groups, validation_groups = train_test_split(
        groups["text_group"],
        test_size=validation_size,
        random_state=random_seed,
        stratify=groups["stratum"],
    )
    labels = {group: "model_train" for group in model_groups}
    labels.update({group: "validation" for group in validation_groups})
    return pd.DataFrame(
        {
            "essay_id": working["essay_id"],
            "split": working["text_group"].map(labels),
            "normalized_text_hash": working["text_group"],
        }
    )
