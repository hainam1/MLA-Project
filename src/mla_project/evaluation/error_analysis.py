"""Reference-score-dependent residual analysis."""

from __future__ import annotations

import pandas as pd


def build_error_analysis(
    essay_ids: pd.Series,
    reference_scores: pd.Series | None,
    predictions: pd.Series,
) -> pd.DataFrame:
    """Build residual rows only when human reference scores are supplied."""
    if reference_scores is None:
        raise ValueError("Error analysis requires human reference scores.")
    result = pd.DataFrame(
        {
            "essay_id": essay_ids.to_numpy(),
            "reference_score": reference_scores.to_numpy(dtype=float),
            "predicted_score": predictions.to_numpy(dtype=float),
        }
    )
    result["residual"] = result["reference_score"] - result["predicted_score"]
    result["absolute_error"] = result["residual"].abs()
    return result.sort_values("absolute_error", ascending=False).reset_index(drop=True)
