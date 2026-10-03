"""Evaluation of a review-priority rule when reference scores exist."""

from __future__ import annotations

import numpy as np


def error_capture_rate(
    absolute_errors: np.ndarray, prioritized: np.ndarray, *, error_threshold: float
) -> float:
    """Return the fraction of large-error cases captured by the review queue."""
    large_errors = np.asarray(absolute_errors) >= error_threshold
    if not large_errors.any():
        return 0.0
    return float(np.asarray(prioritized, dtype=bool)[large_errors].mean())


def review_queue_metrics(large_errors: np.ndarray, selected: np.ndarray) -> dict[str, float | int]:
    """Evaluate a fixed-size review queue against a precomputed large-error mask."""
    error_mask = np.asarray(large_errors, dtype=bool)
    selected_mask = np.asarray(selected, dtype=bool)
    if error_mask.shape != selected_mask.shape:
        raise ValueError("large_errors and selected must have the same shape.")
    selected_count = int(selected_mask.sum())
    if selected_count == 0:
        raise ValueError("The review queue must select at least one essay.")
    large_error_count = int(error_mask.sum())
    captured_count = int((error_mask & selected_mask).sum())
    prevalence = float(error_mask.mean())
    precision = float(captured_count / selected_count)
    capture_rate = float(captured_count / large_error_count) if large_error_count else float("nan")
    lift = float(precision / prevalence) if prevalence else float("nan")
    return {
        "selected_count": selected_count,
        "large_error_count": large_error_count,
        "captured_count": captured_count,
        "large_error_prevalence": prevalence,
        "capture_rate": capture_rate,
        "precision": precision,
        "lift": lift,
    }


def random_review_distribution(
    large_errors: np.ndarray,
    *,
    selected_count: int,
    repetitions: int = 1000,
    random_seed: int = 42,
) -> dict[str, float | int]:
    """Summarize uniform random queues of the same fixed size without replacement."""
    error_mask = np.asarray(large_errors, dtype=bool)
    if not 0 < selected_count <= len(error_mask):
        raise ValueError("selected_count must be between 1 and the number of essays.")
    if repetitions < 1:
        raise ValueError("repetitions must be positive.")
    rng = np.random.default_rng(random_seed)
    metric_names = ("capture_rate", "precision", "lift")
    draws = {name: [] for name in metric_names}
    for _ in range(repetitions):
        selected = np.zeros(len(error_mask), dtype=bool)
        selected[rng.choice(len(error_mask), size=selected_count, replace=False)] = True
        metrics = review_queue_metrics(error_mask, selected)
        for name in metric_names:
            draws[name].append(float(metrics[name]))
    summary: dict[str, float | int] = {
        "selected_count": selected_count,
        "large_error_count": int(error_mask.sum()),
        "large_error_prevalence": float(error_mask.mean()),
        "repetitions": repetitions,
        "random_seed": random_seed,
    }
    for name in metric_names:
        values = np.asarray(draws[name], dtype=float)
        finite = values[np.isfinite(values)]
        if finite.size:
            summary[f"{name}_mean"] = float(finite.mean())
            summary[f"{name}_ci_low"] = float(np.percentile(finite, 2.5))
            summary[f"{name}_ci_high"] = float(np.percentile(finite, 97.5))
        else:
            summary[f"{name}_mean"] = float("nan")
            summary[f"{name}_ci_low"] = float("nan")
            summary[f"{name}_ci_high"] = float("nan")
    return summary
