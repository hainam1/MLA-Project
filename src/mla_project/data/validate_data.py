"""ELLIPSE schema validation."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

ID_COLUMN = "essay_id"
TEXT_COLUMN = "essay_text"
TARGET_COLUMNS = ("Vocabulary", "Grammar")


def validate_ellipse_schema(
    frame: pd.DataFrame,
    *,
    require_targets: bool = True,
    targets: Iterable[str] = TARGET_COLUMNS,
) -> pd.DataFrame:
    """Validate and normalize the columns used by this project."""
    required = {ID_COLUMN, TEXT_COLUMN}
    target_columns = tuple(targets)
    if require_targets:
        required.update(target_columns)
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    if frame.empty:
        raise ValueError("Dataset contains no rows.")
    if frame[ID_COLUMN].isna().any() or not frame[ID_COLUMN].is_unique:
        raise ValueError("essay_id must be non-null and unique.")
    text = frame[TEXT_COLUMN]
    if text.isna().any() or (~text.map(lambda value: isinstance(value, str))).any():
        raise ValueError("essay_text must contain non-null strings.")
    if text.str.strip().eq("").any():
        raise ValueError("essay_text must not contain empty writing samples.")

    validated = frame.copy()
    validated[TEXT_COLUMN] = text.str.strip()
    if require_targets:
        for target in target_columns:
            values = pd.to_numeric(validated[target], errors="coerce")
            if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
                raise ValueError(f"{target} must contain finite numeric values.")
            validated[target] = values.astype(float)
    return validated
