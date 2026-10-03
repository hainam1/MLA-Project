"""Train-only metrics and acceptance rules for the tail-bias improvement study."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import t
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

SCORE_BANDS = ("low", "middle", "high")


def score_bands(values: np.ndarray | pd.Series) -> np.ndarray:
    """Map rubric scores to predeclared low, middle, and high bands."""
    scores = np.asarray(values, dtype=float)
    return np.select(
        [scores <= 2.5, scores <= 3.5, scores >= 4.0],
        SCORE_BANDS,
        default="invalid",
    )


def inverse_sqrt_band_weights(values: np.ndarray | pd.Series) -> np.ndarray:
    """Compute mean-one inverse-square-root frequency weights within a fit partition."""
    bands = score_bands(values)
    if np.any(bands == "invalid"):
        raise ValueError("Sample weighting received scores outside the frozen rubric bands.")
    counts = pd.Series(bands).value_counts()
    weights = np.array([1.0 / np.sqrt(counts[band]) for band in bands], dtype=float)
    return weights / weights.mean()


def calibration_slope(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Return the least-squares slope for human score as a function of prediction."""
    prediction_variance = float(np.var(y_pred))
    if prediction_variance == 0.0:
        return float("nan")
    return float(np.cov(y_pred, y_true, ddof=0)[0, 1] / prediction_variance)


def overall_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute the predeclared overall train-only evaluation metrics."""
    residual = y_pred - y_true
    absolute_error = np.abs(residual)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
        "mean_bias": float(residual.mean()),
        "within_0_5_points_rate": float(np.mean(absolute_error <= 0.5)),
        "within_1_0_point_rate": float(np.mean(absolute_error <= 1.0)),
        "calibration_slope": calibration_slope(y_true, y_pred),
        "prediction_standard_deviation": float(np.std(y_pred, ddof=1)),
        "human_standard_deviation": float(np.std(y_true, ddof=1)),
    }


def band_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> pd.DataFrame:
    """Compute sample count, MAE, and signed bias in each predeclared score band."""
    bands = score_bands(y_true)
    rows = []
    for band in SCORE_BANDS:
        mask = bands == band
        residual = y_pred[mask] - y_true[mask]
        rows.append(
            {
                "score_band": band,
                "n_samples": int(mask.sum()),
                "mae": float(np.abs(residual).mean()),
                "signed_bias": float(residual.mean()),
                "within_0_5_points_rate": float(np.mean(np.abs(residual) <= 0.5)),
                "within_1_0_point_rate": float(np.mean(np.abs(residual) <= 1.0)),
            }
        )
    return pd.DataFrame(rows)


def fold_mae_interval(fold_maes: np.ndarray) -> tuple[float, float, float]:
    """Return fold mean and a two-sided t interval from the five frozen folds."""
    values = np.asarray(fold_maes, dtype=float)
    mean = float(values.mean())
    if len(values) < 2:
        return mean, float("nan"), float("nan")
    half_width = float(t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values)))
    return mean, mean - half_width, mean + half_width


def acceptance_table(
    overall: pd.DataFrame,
    bands: pd.DataFrame,
    folds: pd.DataFrame,
    *,
    baseline_variant: str = "rf_baseline",
    maximum_overall_mae_increase: float = 0.005,
    minimum_macro_improvement: float = 0.10,
    minimum_tail_bias_reduction: float = 0.20,
    maximum_group_mae_increase: float = 0.05,
    minimum_improved_folds: int = 4,
) -> pd.DataFrame:
    """Apply every predeclared acceptance condition against RF baseline OOF predictions."""
    rows: list[dict[str, object]] = []
    for target in overall["target"].unique():
        target_overall = overall.loc[overall["target"].eq(target)].set_index("variant")
        target_bands = bands.loc[bands["target"].eq(target)]
        baseline_overall = target_overall.loc[baseline_variant]
        baseline_bands = target_bands.loc[target_bands["variant"].eq(baseline_variant)].set_index(
            "score_band"
        )
        baseline_macro = float(baseline_bands["mae"].mean())
        baseline_tail_bias = float(baseline_bands.loc[["low", "high"], "signed_bias"].abs().max())
        baseline_fold = folds.loc[
            folds["target"].eq(target) & folds["variant"].eq(baseline_variant)
        ].set_index("fold")
        for variant, candidate in target_overall.iterrows():
            if variant == baseline_variant:
                continue
            candidate_bands = target_bands.loc[target_bands["variant"].eq(variant)].set_index(
                "score_band"
            )
            candidate_macro = float(candidate_bands["mae"].mean())
            candidate_tail_bias = float(
                candidate_bands.loc[["low", "high"], "signed_bias"].abs().max()
            )
            candidate_fold = folds.loc[
                folds["target"].eq(target) & folds["variant"].eq(variant)
            ].set_index("fold")
            aligned = baseline_fold[["mae"]].join(
                candidate_fold[["mae"]], lsuffix="_baseline", rsuffix="_candidate"
            )
            improved_folds = int((aligned["mae_candidate"] < aligned["mae_baseline"]).sum())
            overall_pass = bool(
                candidate["mae"] <= baseline_overall["mae"] + maximum_overall_mae_increase
            )
            macro_improvement = (baseline_macro - candidate_macro) / baseline_macro
            macro_pass = bool(macro_improvement >= minimum_macro_improvement)
            tail_reduction = (
                (baseline_tail_bias - candidate_tail_bias) / baseline_tail_bias
                if baseline_tail_bias
                else 0.0
            )
            tail_pass = bool(tail_reduction >= minimum_tail_bias_reduction)
            maximum_band_increase = float((candidate_bands["mae"] - baseline_bands["mae"]).max())
            group_pass = bool(maximum_band_increase <= maximum_group_mae_increase)
            folds_pass = bool(improved_folds >= minimum_improved_folds)
            rows.append(
                {
                    "target": target,
                    "variant": variant,
                    "overall_mae": float(candidate["mae"]),
                    "overall_mae_change": float(candidate["mae"] - baseline_overall["mae"]),
                    "macro_band_mae": candidate_macro,
                    "macro_band_mae_improvement_fraction": macro_improvement,
                    "max_tail_absolute_bias": candidate_tail_bias,
                    "max_tail_bias_reduction_fraction": tail_reduction,
                    "maximum_band_mae_increase": maximum_band_increase,
                    "improved_folds": improved_folds,
                    "overall_mae_pass": overall_pass,
                    "macro_band_mae_pass": macro_pass,
                    "tail_bias_pass": tail_pass,
                    "group_degradation_pass": group_pass,
                    "fold_consistency_pass": folds_pass,
                    "all_acceptance_rules_pass": bool(
                        overall_pass and macro_pass and tail_pass and group_pass and folds_pass
                    ),
                }
            )
    return pd.DataFrame(rows)
