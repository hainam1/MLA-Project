"""Validation-only error and subgroup summaries for the frozen Phase 8 protocol."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd


def assign_error_quadrants(frame: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Split validation essays at the population median disagreement."""
    required = {"essay_id", "disagreement", "large_error"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Quadrant data are missing columns: {missing}")
    result = frame.copy()
    threshold = float(result["disagreement"].median())
    result["high_disagreement"] = result["disagreement"].ge(threshold)
    conditions = [
        result["high_disagreement"] & result["large_error"],
        result["high_disagreement"] & ~result["large_error"],
        ~result["high_disagreement"] & result["large_error"],
    ]
    labels = [
        "High disagreement + Large error",
        "High disagreement + No large error",
        "Low disagreement + Large error",
    ]
    result["error_quadrant"] = np.select(
        conditions, labels, default="Low disagreement + No large error"
    )
    return result, threshold


def _distribution_json(values: pd.Series) -> str:
    counts = values.value_counts().sort_index()
    payload = {f"{float(score):g}": int(count) for score, count in counts.items()}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _direction_metrics(group: pd.DataFrame, target: str) -> dict[str, float]:
    signed = group[f"random_forest_{target.lower()}"] - group[target]
    return {
        f"{target.lower()}_mean_signed_error": float(signed.mean()),
        f"{target.lower()}_overprediction_rate": float(signed.gt(0).mean()),
        f"{target.lower()}_underprediction_rate": float(signed.lt(0).mean()),
    }


def summarize_error_groups(
    frame: pd.DataFrame, group_columns: list[str], *, include_score_distributions: bool = False
) -> pd.DataFrame:
    """Summarize frozen RF errors for arbitrary validation-only groups."""
    rows: list[dict[str, object]] = []
    grouper: str | list[str] = group_columns[0] if len(group_columns) == 1 else group_columns
    for keys, group in frame.groupby(grouper, observed=True, dropna=False, sort=True):
        key_values = (keys,) if len(group_columns) == 1 else keys
        row: dict[str, object] = dict(zip(group_columns, key_values, strict=True))
        row.update(
            {
                "n": len(group),
                "percentage": float(100.0 * len(group) / len(frame)),
                "mean_disagreement": float(group["disagreement"].mean()),
                "mean_max_rf_error": float(group["max_rf_absolute_error"].mean()),
                "mean_word_count": float(group["word_count"].mean()),
                "large_error_count": int(group["large_error"].sum()),
                "large_error_prevalence": float(group["large_error"].mean()),
                **_direction_metrics(group, "Vocabulary"),
                **_direction_metrics(group, "Grammar"),
            }
        )
        if include_score_distributions:
            row["vocabulary_human_score_distribution"] = _distribution_json(group["Vocabulary"])
            row["grammar_human_score_distribution"] = _distribution_json(group["Grammar"])
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_by_human_score(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize errors at each observed human score separately per target."""
    rows: list[dict[str, object]] = []
    for target in ("Vocabulary", "Grammar"):
        prediction = f"random_forest_{target.lower()}"
        for score, group in frame.groupby(target, sort=True):
            signed = group[prediction] - group[target]
            rows.append(
                {
                    "target": target,
                    "human_score": float(score),
                    "n": len(group),
                    "mean_target_absolute_error": float(signed.abs().mean()),
                    "mean_target_signed_error": float(signed.mean()),
                    "overprediction_rate": float(signed.gt(0).mean()),
                    "underprediction_rate": float(signed.lt(0).mean()),
                    "mean_max_rf_error": float(group["max_rf_absolute_error"].mean()),
                    "large_error_count": int(group["large_error"].sum()),
                    "large_error_prevalence": float(group["large_error"].mean()),
                    "mean_disagreement": float(group["disagreement"].mean()),
                }
            )
    return pd.DataFrame(rows)


def fairness_table(
    frame: pd.DataFrame,
    *,
    attributes: tuple[str, ...] = ("gender", "race_ethnicity", "SES"),
    selected_count: int,
) -> pd.DataFrame:
    """Report descriptive subgroup errors and fixed-queue selection behavior."""
    expected_random_rate = selected_count / len(frame)
    rows: list[dict[str, object]] = []
    for attribute in attributes:
        for value, group in frame.groupby(attribute, dropna=False, sort=True):
            large_count = int(group["large_error"].sum())
            captured = int((group["large_error"] & group["disagreement_selected"]).sum())
            rows.append(
                {
                    "attribute": attribute,
                    "group": "Missing" if pd.isna(value) else str(value),
                    "n": len(group),
                    "vocabulary_mae": float(group["error_vocabulary"].mean()),
                    "grammar_mae": float(group["error_grammar"].mean()),
                    "large_error_count": large_count,
                    "large_error_prevalence": float(group["large_error"].mean()),
                    "disagreement_selected_count": int(group["disagreement_selected"].sum()),
                    "disagreement_selection_rate": float(group["disagreement_selected"].mean()),
                    "within_group_capture_rate": (
                        float(captured / large_count) if large_count else float("nan")
                    ),
                    "shortest_selected_count": int(group["shortest_selected"].sum()),
                    "shortest_first_selection_rate": float(group["shortest_selected"].mean()),
                    "random_expected_selection_rate": float(expected_random_rate),
                    "small_n_flag": len(group) < 20,
                }
            )
    return pd.DataFrame(rows)
