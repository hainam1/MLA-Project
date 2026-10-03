"""Audit the 14-feature development table and evaluate frozen validation baselines.

The script never reads official-test features or targets. It excludes every development row whose
frozen privacy status is not ``not_flagged`` before diagnostics, fitting, or evaluation.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy.stats import ks_2samp

from mla_project.evaluation.regression_metrics import regression_metrics
from mla_project.evaluation.review_metrics import (
    random_review_distribution,
    review_queue_metrics,
)
from mla_project.features import FEATURE_NAMES
from mla_project.models.train_random_forest import build_random_forest
from mla_project.models.train_ridge import build_ridge

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
MANIFEST_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
CONFIG_PATH = ROOT / "configs" / "phase5_baselines.yaml"
TABLES = ROOT / "docs" / "data" / "phase5_tables"
FIGURES = ROOT / "docs" / "assets"
PREDICTIONS = ROOT / "outputs" / "predictions" / "phase5_validation_baselines.csv"

TARGETS = ("Vocabulary", "Grammar")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_config() -> dict[str, object]:
    with CONFIG_PATH.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def load_eligible_development() -> tuple[pd.DataFrame, dict[str, int]]:
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    manifest = pd.read_csv(
        MANIFEST_PATH,
        usecols=["essay_id", "source_partition", "split", "privacy_review_status"],
        dtype={"essay_id": "string"},
    )
    manifest = manifest.loc[manifest["source_partition"].eq("official_train")]
    if "official_test" in set(development["split"]):
        raise RuntimeError("Development table unexpectedly contains official-test rows.")
    merged = development.merge(
        manifest[["essay_id", "privacy_review_status"]],
        on="essay_id",
        how="left",
        validate="one_to_one",
    )
    if merged["privacy_review_status"].isna().any():
        raise RuntimeError("Privacy-status join failed.")
    counts = {
        f"{split}_{status}": int(count)
        for (split, status), count in merged.groupby(["split", "privacy_review_status"])
        .size()
        .items()
    }
    eligible = merged.loc[merged["privacy_review_status"].eq("not_flagged")].copy()
    eligible = eligible.drop(columns="privacy_review_status")
    if set(eligible["split"]) != {"model_train", "validation"}:
        raise RuntimeError("Expected eligible model-train and validation rows.")
    return eligible, counts


def population_stability_index(
    train_values: pd.Series, validation_values: pd.Series, *, bins: int
) -> float:
    """Compute PSI using train-derived quantile bins and small zero-count smoothing."""
    quantiles = np.linspace(0, 1, bins + 1)[1:-1]
    interior = np.unique(train_values.quantile(quantiles).to_numpy(dtype=float))
    edges = np.concatenate(([-np.inf], interior, [np.inf]))
    train_counts = np.histogram(train_values, bins=edges)[0].astype(float)
    validation_counts = np.histogram(validation_values, bins=edges)[0].astype(float)
    epsilon = 1e-6
    train_share = np.clip(train_counts / train_counts.sum(), epsilon, None)
    validation_share = np.clip(validation_counts / validation_counts.sum(), epsilon, None)
    return float(np.sum((validation_share - train_share) * np.log(validation_share / train_share)))


def audit_features(
    train: pd.DataFrame, validation: pd.DataFrame, config: dict[str, object]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    audit = config["feature_audit"]
    quality_rows: list[dict[str, object]] = []
    stability_rows: list[dict[str, object]] = []
    for feature in FEATURE_NAMES:
        train_values = train[feature]
        validation_values = validation[feature]
        q1, q3 = train_values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        train_outlier = ~train_values.between(lower, upper)
        validation_outlier = ~validation_values.between(lower, upper)
        dominant_share = float(train_values.value_counts(normalize=True).max())
        train_std = float(train_values.std(ddof=1))
        validation_std = float(validation_values.std(ddof=1))
        pooled_std = math.sqrt((train_std**2 + validation_std**2) / 2)
        smd = (
            float((validation_values.mean() - train_values.mean()) / pooled_std)
            if pooled_std
            else 0.0
        )
        psi = population_stability_index(
            train_values, validation_values, bins=int(audit["psi_bins"])
        )
        ks = float(ks_2samp(train_values, validation_values).statistic)
        near_constant = bool(
            train_std <= float(audit["near_constant_std_threshold"])
            or dominant_share >= float(audit["near_constant_dominant_share_threshold"])
        )
        quality_rows.append(
            {
                "feature": feature,
                "train_missing": int(train_values.isna().sum()),
                "validation_missing": int(validation_values.isna().sum()),
                "train_infinite": int(np.isinf(train_values).sum()),
                "validation_infinite": int(np.isinf(validation_values).sum()),
                "train_unique": int(train_values.nunique()),
                "train_dominant_value_share": dominant_share,
                "train_min": float(train_values.min()),
                "train_p01": float(train_values.quantile(0.01)),
                "train_q1": float(q1),
                "train_median": float(train_values.median()),
                "train_mean": float(train_values.mean()),
                "train_q3": float(q3),
                "train_p99": float(train_values.quantile(0.99)),
                "train_max": float(train_values.max()),
                "train_std": train_std,
                "iqr_outlier_lower_fence": float(lower),
                "iqr_outlier_upper_fence": float(upper),
                "train_outlier_count": int(train_outlier.sum()),
                "train_outlier_share": float(train_outlier.mean()),
                "validation_outlier_count": int(validation_outlier.sum()),
                "validation_outlier_share": float(validation_outlier.mean()),
                "near_constant": near_constant,
            }
        )
        stable = bool(
            abs(smd) <= float(audit["stability_smd_threshold"])
            and psi <= float(audit["stability_psi_threshold"])
            and ks <= float(audit["stability_ks_threshold"])
        )
        stability_rows.append(
            {
                "feature": feature,
                "train_mean": float(train_values.mean()),
                "validation_mean": float(validation_values.mean()),
                "train_std": train_std,
                "validation_std": validation_std,
                "standardized_mean_difference": smd,
                "ks_statistic": ks,
                "population_stability_index": psi,
                "stable_under_predeclared_thresholds": stable,
            }
        )

    pearson = train[list(FEATURE_NAMES)].corr(method="pearson")
    spearman = train[list(FEATURE_NAMES)].corr(method="spearman")
    threshold = float(audit["high_correlation_threshold"])
    correlation_rows = []
    for left_index, left in enumerate(FEATURE_NAMES):
        for right in FEATURE_NAMES[left_index + 1 :]:
            pearson_value = float(pearson.loc[left, right])
            spearman_value = float(spearman.loc[left, right])
            correlation_rows.append(
                {
                    "feature_left": left,
                    "feature_right": right,
                    "pearson_correlation": pearson_value,
                    "spearman_correlation": spearman_value,
                    "high_similarity": bool(
                        abs(pearson_value) >= threshold or abs(spearman_value) >= threshold
                    ),
                }
            )
    correlations = pd.DataFrame(correlation_rows).sort_values(
        ["high_similarity", "pearson_correlation"],
        ascending=[False, False],
        key=lambda column: column.abs() if column.name == "pearson_correlation" else column,
    )
    return (
        pd.DataFrame(quality_rows),
        pd.DataFrame(stability_rows),
        correlations,
    )


def fit_baselines(
    train: pd.DataFrame, validation: pd.DataFrame, config: dict[str, object]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline = config["baselines"]
    length_features = list(baseline["length_only"]["features"])
    if tuple(length_features) != FEATURE_NAMES[:3]:
        raise RuntimeError("Length-only baseline must use exactly the first three features.")
    x_train = train[length_features]
    x_validation = validation[length_features]
    metric_rows: list[dict[str, object]] = []
    predictions = pd.DataFrame({"essay_id": validation["essay_id"].to_numpy()})

    forest_config = baseline["length_only"]["random_forest"]
    for target in TARGETS:
        y_train = train[target].to_numpy(dtype=float)
        y_validation = validation[target].to_numpy(dtype=float)
        mean_prediction = np.full(len(validation), y_train.mean(), dtype=float)
        ridge = build_ridge(alpha=float(baseline["length_only"]["ridge_alpha"]))
        forest = build_random_forest(
            n_estimators=int(forest_config["n_estimators"]),
            max_depth=forest_config["max_depth"],
            min_samples_leaf=int(forest_config["min_samples_leaf"]),
            max_features=forest_config["max_features"],
            random_state=int(baseline["review"]["random_seed"]),
            n_jobs=int(forest_config["n_jobs"]),
        )
        ridge.fit(x_train, y_train)
        forest.fit(x_train, y_train)
        ridge_prediction = ridge.predict(x_validation)
        forest_prediction = forest.predict(x_validation)
        consensus_prediction = (ridge_prediction + forest_prediction) / 2
        model_predictions = {
            "mean": mean_prediction,
            "length_ridge": ridge_prediction,
            "length_random_forest": forest_prediction,
            "length_consensus": consensus_prediction,
        }
        for model_name, prediction in model_predictions.items():
            metrics = regression_metrics(y_validation, prediction)
            metric_rows.append(
                {
                    "baseline": model_name,
                    "target": target,
                    "train_rows": len(train),
                    "validation_rows": len(validation),
                    "feature_count": 0 if model_name == "mean" else 3,
                    **metrics,
                }
            )
            predictions[f"{model_name}_{target.lower()}"] = prediction
        predictions[f"actual_{target.lower()}"] = y_validation
        predictions[f"disagreement_{target.lower()}"] = np.abs(ridge_prediction - forest_prediction)

    review_config = baseline["review"]
    predictions["review_priority_score"] = predictions[
        ["disagreement_vocabulary", "disagreement_grammar"]
    ].max(axis=1)
    predictions["max_consensus_absolute_error"] = np.maximum(
        np.abs(predictions["actual_vocabulary"] - predictions["length_consensus_vocabulary"]),
        np.abs(predictions["actual_grammar"] - predictions["length_consensus_grammar"]),
    )
    predictions["large_error"] = predictions["max_consensus_absolute_error"].ge(
        float(review_config["large_error_threshold"])
    )
    selected_count = math.ceil(float(review_config["review_budget"]) * len(predictions))
    ranked = predictions.sort_values(
        ["review_priority_score", "essay_id"], ascending=[False, True], kind="stable"
    )
    selected_ids = set(ranked.head(selected_count)["essay_id"])
    predictions["selected_by_length_disagreement"] = predictions["essay_id"].isin(selected_ids)
    disagreement_metrics = review_queue_metrics(
        predictions["large_error"].to_numpy(),
        predictions["selected_by_length_disagreement"].to_numpy(),
    )
    random_metrics = random_review_distribution(
        predictions["large_error"].to_numpy(),
        selected_count=selected_count,
        repetitions=int(review_config["random_repetitions"]),
        random_seed=int(review_config["random_seed"]),
    )
    review_rows = [
        {
            "strategy": "length_disagreement",
            "review_budget": float(review_config["review_budget"]),
            "validation_rows": len(validation),
            **disagreement_metrics,
            "repetitions": 1,
            "capture_rate_ci_low": np.nan,
            "capture_rate_ci_high": np.nan,
            "precision_ci_low": np.nan,
            "precision_ci_high": np.nan,
            "lift_ci_low": np.nan,
            "lift_ci_high": np.nan,
        },
        {
            "strategy": "uniform_random",
            "review_budget": float(review_config["review_budget"]),
            "validation_rows": len(validation),
            "selected_count": random_metrics["selected_count"],
            "large_error_count": random_metrics["large_error_count"],
            "captured_count": np.nan,
            "large_error_prevalence": random_metrics["large_error_prevalence"],
            "capture_rate": random_metrics["capture_rate_mean"],
            "precision": random_metrics["precision_mean"],
            "lift": random_metrics["lift_mean"],
            "repetitions": random_metrics["repetitions"],
            "capture_rate_ci_low": random_metrics["capture_rate_ci_low"],
            "capture_rate_ci_high": random_metrics["capture_rate_ci_high"],
            "precision_ci_low": random_metrics["precision_ci_low"],
            "precision_ci_high": random_metrics["precision_ci_high"],
            "lift_ci_low": random_metrics["lift_ci_low"],
            "lift_ci_high": random_metrics["lift_ci_high"],
        },
    ]
    return pd.DataFrame(metric_rows), pd.DataFrame(review_rows), predictions


def plot_feature_distributions(train: pd.DataFrame, validation: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(4, 4, figsize=(16, 13))
    axes_flat = axes.ravel()
    for axis, feature in zip(axes_flat, FEATURE_NAMES, strict=False):
        combined = pd.concat([train[feature], validation[feature]], ignore_index=True)
        low, high = combined.quantile([0.01, 0.99])
        train_clipped = train[feature].clip(low, high)
        validation_clipped = validation[feature].clip(low, high)
        bins = np.histogram_bin_edges(combined.clip(low, high), bins=24)
        axis.hist(train_clipped, bins=bins, density=True, alpha=0.45, label="model_train")
        axis.hist(validation_clipped, bins=bins, density=True, alpha=0.45, label="validation")
        axis.set_title(feature, fontsize=9)
        axis.tick_params(labelsize=8)
    for axis in axes_flat[len(FEATURE_NAMES) :]:
        axis.axis("off")
    axes_flat[0].legend(fontsize=8)
    figure.suptitle("Phase 5 feature distributions (display clipped to pooled 1st–99th percentile)")
    figure.tight_layout()
    figure.savefig(FIGURES / "phase5_feature_distributions.png", dpi=180)
    plt.close(figure)


def main() -> None:
    config = load_config()
    eligible, privacy_counts = load_eligible_development()
    train = eligible.loc[eligible["split"].eq("model_train")].copy()
    validation = eligible.loc[eligible["split"].eq("validation")].copy()
    quality, stability, correlations = audit_features(train, validation, config)
    metrics, review, predictions = fit_baselines(train, validation, config)

    TABLES.mkdir(parents=True, exist_ok=True)
    PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    quality.to_csv(TABLES / "feature_quality_summary.csv", index=False, float_format="%.8g")
    stability.to_csv(TABLES / "feature_stability.csv", index=False, float_format="%.8g")
    correlations.to_csv(TABLES / "feature_correlations.csv", index=False, float_format="%.8g")
    metrics.to_csv(TABLES / "baseline_regression_metrics.csv", index=False, float_format="%.8g")
    review.to_csv(TABLES / "review_baselines.csv", index=False, float_format="%.8g")
    predictions.to_csv(PREDICTIONS, index=False, float_format="%.12g")
    plot_feature_distributions(train, validation)

    summary = {
        "official_test_loaded": False,
        "feature_count": len(FEATURE_NAMES),
        "eligible_privacy_status": "not_flagged",
        "model_train_rows_before_privacy_filter": 3128,
        "model_train_rows_after_privacy_filter": len(train),
        "validation_rows_before_privacy_filter": 783,
        "validation_rows_after_privacy_filter": len(validation),
        "privacy_status_counts": privacy_counts,
        "missing_feature_values": int(eligible[list(FEATURE_NAMES)].isna().sum().sum()),
        "infinite_feature_values": int(np.isinf(eligible[list(FEATURE_NAMES)].to_numpy()).sum()),
        "near_constant_features": quality.loc[quality["near_constant"], "feature"].tolist(),
        "unstable_features": stability.loc[
            ~stability["stable_under_predeclared_thresholds"], "feature"
        ].tolist(),
        "high_similarity_pairs": int(correlations["high_similarity"].sum()),
        "primary_review_budget": float(config["baselines"]["review"]["review_budget"]),
        "selected_validation_essays": int(review.iloc[0]["selected_count"]),
        "large_error_threshold": float(config["baselines"]["review"]["large_error_threshold"]),
        "random_review_repetitions": int(config["baselines"]["review"]["random_repetitions"]),
        "random_seed": int(config["baselines"]["review"]["random_seed"]),
        "random_forest_n_jobs": int(config["baselines"]["length_only"]["random_forest"]["n_jobs"]),
        "baseline_metrics_sha256": file_sha256(TABLES / "baseline_regression_metrics.csv"),
        "review_baselines_sha256": file_sha256(TABLES / "review_baselines.csv"),
        "validation_predictions_sha256": file_sha256(PREDICTIONS),
    }
    (TABLES / "phase5_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
