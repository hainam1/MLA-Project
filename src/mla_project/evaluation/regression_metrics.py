"""Regression metrics."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import cohen_kappa_score, mean_absolute_error, mean_squared_error, r2_score

SCORE_LEVELS = np.arange(1.0, 5.01, 0.5)


def qwk_scores(y_pred: np.ndarray) -> np.ndarray:
    """Round half-up to the ELLIPSE half-point grid and clip for QWK only."""
    predictions = np.asarray(y_pred, dtype=float)
    if not np.isfinite(predictions).all():
        raise ValueError("QWK predictions must be finite.")
    rounded = np.floor(predictions * 2.0 + 0.5) / 2.0
    return np.clip(rounded, 1.0, 5.0)


def model_qwk(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute quadratic weighted kappa on the fixed nine-level ELLIPSE grid."""
    references = np.asarray(y_true, dtype=float)
    if not np.isfinite(references).all():
        raise ValueError("QWK references must be finite.")
    encoded_reference = np.rint((references - 1.0) * 2.0).astype(int)
    if (
        np.any(references < 1.0)
        or np.any(references > 5.0)
        or not np.allclose(references, encoded_reference / 2.0 + 1.0, rtol=0.0, atol=1e-12)
    ):
        raise ValueError("QWK references must lie on the 1.0-5.0 half-point grid.")
    encoded_prediction = np.rint((qwk_scores(y_pred) - 1.0) * 2.0).astype(int)
    return float(
        cohen_kappa_score(
            encoded_reference,
            encoded_prediction,
            labels=list(range(len(SCORE_LEVELS))),
            weights="quadratic",
        )
    )


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute continuous regression metrics plus half-point-grid model QWK."""
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
        "qwk": model_qwk(y_true, y_pred),
    }
