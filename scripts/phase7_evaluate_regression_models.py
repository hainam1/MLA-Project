"""Evaluate the frozen Phase 6 predictions on eligible validation rows only.

This script does not fit or tune a model. It reads the text-free Phase 6 predictions, joins them
to the frozen validation labels by essay ID, verifies the Phase 5 baseline artifacts, computes
regression metrics and error summaries, and writes a reproducible report. Official-test files are
never read.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mla_project.evaluation.phase7 import (
    MODEL_COLUMNS,
    PREDICTION_COLUMNS,
    TARGETS,
    baseline_comparison_table,
    choose_point_predictors,
    error_table,
    machine_by_human_score_table,
    regression_metrics_table,
    scorer_distribution_table,
    validate_and_join_predictions,
)
from mla_project.evaluation.regression_metrics import regression_metrics
from mla_project.features.build_features import FEATURE_NAMES
from mla_project.pipelines.training_pipeline import load_model_artifacts, prepare_training_data

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
SPLIT_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
PHASE6_DIR = ROOT / "outputs" / "phase6"
PHASE6_PREDICTIONS_PATH = PHASE6_DIR / "validation_predictions.csv"
PHASE6_SUMMARY_PATH = PHASE6_DIR / "training_summary.json"
PHASE6_MANIFEST_PATH = PHASE6_DIR / "artifact_manifest.json"
PHASE5_BASELINE_METRICS_PATH = (
    ROOT / "docs" / "data" / "phase5_tables" / "baseline_regression_metrics.csv"
)
PHASE5_REVIEW_METRICS_PATH = ROOT / "docs" / "data" / "phase5_tables" / "review_baselines.csv"
PHASE5_SUMMARY_PATH = ROOT / "docs" / "data" / "phase5_tables" / "phase5_audit_summary.json"
PHASE5_PREDICTIONS_PATH = ROOT / "outputs" / "predictions" / "phase5_validation_baselines.csv"
TABLE_DIR = ROOT / "docs" / "data" / "phase7_tables"
FIGURE_DIR = ROOT / "outputs" / "figures" / "phase7"
PREDICTIONS_OUTPUT_PATH = (
    ROOT / "outputs" / "predictions" / "phase7_validation_regression_predictions.csv"
)
REPORT_PATH = ROOT / "docs" / "phase7_regression_evaluation.md"

BASELINE_COLUMNS = {
    "Vocabulary": {
        "mean": "mean_vocabulary",
        "length_ridge": "length_ridge_vocabulary",
        "length_random_forest": "length_random_forest_vocabulary",
        "length_consensus": "length_consensus_vocabulary",
    },
    "Grammar": {
        "mean": "mean_grammar",
        "length_ridge": "length_ridge_grammar",
        "length_random_forest": "length_random_forest_grammar",
        "length_consensus": "length_consensus_grammar",
    },
}
MIN_GROUP_SIZE = 20


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_close(left: float, right: float, *, label: str, atol: float = 1e-6) -> None:
    if not np.isclose(left, right, rtol=0.0, atol=atol):
        raise ValueError(f"{label} differs from the frozen artifact: {left} != {right}")


def load_and_validate_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    split_manifest = pd.read_csv(SPLIT_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, split_manifest)
    phase6_models, phase6_features, phase6_metadata = load_model_artifacts(PHASE6_DIR)
    if phase6_features != FEATURE_NAMES:
        raise ValueError("Phase 6 artifact schema does not match the frozen 14 features.")
    if set(phase6_models) != {
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    }:
        raise ValueError("Phase 6 artifact set does not contain exactly four expected models.")
    if phase6_metadata.get("official_test_loaded") is not False:
        raise ValueError("Phase 6 metadata does not confirm official-test isolation.")
    if phase6_metadata.get("validation_metrics_computed") is not False:
        raise ValueError("Phase 6 validation metrics were already computed unexpectedly.")

    predictions = pd.read_csv(PHASE6_PREDICTIONS_PATH, dtype={"essay_id": "string"})
    expected_phase6_columns = [
        "essay_id",
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    ]
    if list(predictions.columns) != expected_phase6_columns:
        raise ValueError("Phase 6 predictions do not have the frozen text-free schema.")
    expected_ids = prepared.validation["essay_id"].astype(str)
    joined = validate_and_join_predictions(
        prepared.validation,
        predictions,
        expected_ids=expected_ids,
    )
    return joined, prepared.validation, phase6_metadata


def validate_phase5_baselines(
    labels: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Recompute and verify Phase 5 baseline metrics before comparison."""
    baseline_metrics = pd.read_csv(PHASE5_BASELINE_METRICS_PATH)
    review_metrics = pd.read_csv(PHASE5_REVIEW_METRICS_PATH)
    phase5_summary = read_json(PHASE5_SUMMARY_PATH)
    expected_hashes = {
        "baseline_metrics_sha256": PHASE5_BASELINE_METRICS_PATH,
        "review_baselines_sha256": PHASE5_REVIEW_METRICS_PATH,
        "validation_predictions_sha256": PHASE5_PREDICTIONS_PATH,
    }
    for summary_key, path in expected_hashes.items():
        expected_hash = phase5_summary.get(summary_key)
        if expected_hash != file_sha256(path):
            raise ValueError(f"Phase 5 artifact hash mismatch: {path}")

    phase5_predictions = pd.read_csv(PHASE5_PREDICTIONS_PATH, dtype={"essay_id": "string"})
    expected_ids = set(labels["essay_id"].astype(str))
    observed_ids = set(phase5_predictions["essay_id"].astype(str))
    if observed_ids != expected_ids or phase5_predictions["essay_id"].duplicated().any():
        raise ValueError("Phase 5 baseline predictions do not match eligible validation IDs.")
    phase5_joined = labels[["essay_id", *TARGETS]].merge(
        phase5_predictions, on="essay_id", how="inner", validate="one_to_one"
    )
    for target in TARGETS:
        actual_column = f"actual_{target.lower()}"
        if actual_column not in phase5_joined:
            raise ValueError(f"Phase 5 baseline artifact lacks {actual_column}.")
        if not np.allclose(
            phase5_joined[target].to_numpy(dtype=float),
            phase5_joined[actual_column].to_numpy(dtype=float),
            rtol=0.0,
            atol=1e-10,
        ):
            raise ValueError(f"Phase 5 baseline actual labels do not match {target} labels.")

    for target, columns in BASELINE_COLUMNS.items():
        y_true = phase5_joined[target].to_numpy(dtype=float)
        for baseline_name, column in columns.items():
            recomputed = regression_metrics(y_true, phase5_joined[column].to_numpy(dtype=float))
            recorded = baseline_metrics.loc[
                baseline_metrics["baseline"].eq(baseline_name)
                & baseline_metrics["target"].eq(target)
            ]
            if len(recorded) != 1:
                raise ValueError(f"Expected one Phase 5 baseline row: {baseline_name}/{target}")
            for metric_name in ("mae", "rmse", "r2"):
                assert_close(
                    recomputed[metric_name],
                    float(recorded.iloc[0][metric_name]),
                    label=f"Phase 5 {baseline_name}/{target} {metric_name}",
                )
            if int(recorded.iloc[0]["validation_rows"]) != len(labels):
                raise ValueError("Phase 5 baseline population differs from Phase 7 population.")
    return baseline_metrics, review_metrics, phase5_summary


def assign_analysis_groups(
    train_labels: pd.DataFrame, validation_labels: pd.DataFrame
) -> pd.DataFrame:
    """Add train-derived length bands and fixed exploratory score bands."""
    result = validation_labels[["essay_id", "Vocabulary", "Grammar", "word_count"]].copy()
    quantiles = np.unique(train_labels["word_count"].quantile([0.0, 0.25, 0.5, 0.75, 1.0]))
    if len(quantiles) >= 3:
        edges = np.concatenate(([-np.inf], quantiles[1:-1], [np.inf]))
        labels = [f"Q{index}" for index in range(1, len(edges))]
        result["length_band"] = pd.cut(
            result["word_count"], bins=edges, labels=labels, include_lowest=True, right=False
        ).astype("string")
    else:
        result["length_band"] = "all"
    score_edges = [-np.inf, 2.0, 3.0, 4.0, np.inf]
    score_labels = ["<2", "2-<3", "3-<4", "4+"]
    for target in TARGETS:
        result[f"{target.lower()}_score_band"] = pd.cut(
            result[target],
            bins=score_edges,
            labels=score_labels,
            include_lowest=True,
            right=False,
        ).astype("string")
    return result


def grouped_mae_table(
    joined: pd.DataFrame,
    group_frame: pd.DataFrame,
    point_predictors: pd.DataFrame,
) -> pd.DataFrame:
    """Compute exploratory MAE by train-derived length and fixed score bands."""
    selected = dict(
        zip(point_predictors["target"], point_predictors["selected_model"], strict=True)
    )
    rows: list[dict[str, object]] = []
    for target in TARGETS:
        model = selected[target]
        prediction_column = MODEL_COLUMNS[target][model]
        for group_type, group_column in (
            ("length_band", "length_band"),
            ("score_band", f"{target.lower()}_score_band"),
        ):
            values = group_frame[group_column]
            for group_name in values.dropna().unique():
                mask = values.eq(group_name).to_numpy()
                count = int(mask.sum())
                if count < MIN_GROUP_SIZE:
                    continue
                metrics = regression_metrics(
                    joined.loc[mask, target].to_numpy(dtype=float),
                    joined.loc[mask, prediction_column].to_numpy(dtype=float),
                )
                rows.append(
                    {
                        "group_type": group_type,
                        "group": str(group_name),
                        "target": target,
                        "selected_model": model,
                        "n_samples": count,
                        "mae": metrics["mae"],
                        "rmse": metrics["rmse"],
                        "r2": metrics["r2"],
                        "group_definition": (
                            "Training word-count quartiles"
                            if group_type == "length_band"
                            else "Fixed score intervals [<2, 2-<3, 3-<4, 4+]"
                        ),
                    }
                )
    table = pd.DataFrame(rows)
    if table.empty:
        return table
    group_order = {
        "Q1": 1,
        "Q2": 2,
        "Q3": 3,
        "Q4": 4,
        "<2": 1,
        "2-<3": 2,
        "3-<4": 3,
        "4+": 4,
    }
    table["_group_type_order"] = table["group_type"].map({"length_band": 1, "score_band": 2})
    table["_target_order"] = table["target"].map({"Vocabulary": 1, "Grammar": 2})
    table["_group_order"] = table["group"].map(group_order)
    return table.sort_values(
        ["_group_type_order", "_target_order", "_group_order"], kind="stable"
    ).drop(columns=["_group_type_order", "_target_order", "_group_order"])


def error_summary_table(errors: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, target), group in errors.groupby(["model", "target"], sort=False):
        rows.append(
            {
                "model": model,
                "target": target,
                "n_samples": len(group),
                "mean_residual": float(group["residual"].mean()),
                "mean_absolute_error": float(group["absolute_error"].mean()),
                "median_absolute_error": float(group["absolute_error"].median()),
                "p90_absolute_error": float(group["absolute_error"].quantile(0.90)),
                "max_absolute_error": float(group["absolute_error"].max()),
                "predictions_below_1": int((group["prediction"] < 1.0).sum()),
                "predictions_above_5": int((group["prediction"] > 5.0).sum()),
            }
        )
    return pd.DataFrame(rows)


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    def format_value(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, (float, np.floating)):
            return f"{float(value):.6f}"
        return str(value)

    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for _, row in frame.loc[:, columns].iterrows():
        lines.append("| " + " | ".join(format_value(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def plot_predicted_vs_human(joined: pd.DataFrame) -> Path:
    figure, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    colors = {"Ridge": "#1f77b4", "Random Forest": "#d62728"}
    for axis, target in zip(axes, TARGETS, strict=True):
        plotted_values = np.concatenate(
            [
                joined[target].to_numpy(dtype=float),
                *(
                    joined[column].to_numpy(dtype=float)
                    for column in MODEL_COLUMNS[target].values()
                ),
            ]
        )
        lower = min(1.0, float(plotted_values.min()))
        upper = max(5.0, float(plotted_values.max()))
        margin = max(0.05, (upper - lower) * 0.03)
        for model, column in MODEL_COLUMNS[target].items():
            axis.scatter(
                joined[target],
                joined[column],
                s=16,
                alpha=0.42,
                label=model,
                color=colors[model],
            )
        axis.plot([1, 5], [1, 5], color="black", linestyle="--", linewidth=1, label="y=x")
        axis.set_title(f"{target}: predicted vs human")
        axis.set_xlabel("Human score")
        axis.set_ylabel("Predicted score")
        axis.set_xlim(1 - margin, 5 + margin)
        axis.set_ylim(lower - margin, upper + margin)
        axis.axhline(1, color="grey", linestyle=":", linewidth=0.8, label="rubric bounds")
        axis.axhline(5, color="grey", linestyle=":", linewidth=0.8)
        axis.legend()
        axis.grid(alpha=0.2)
    path = FIGURE_DIR / "phase7_predicted_vs_human.png"
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return path


def plot_residuals(errors: pd.DataFrame) -> Path:
    figure, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    colors = {"Ridge": "#1f77b4", "Random Forest": "#d62728"}
    for axis, target in zip(axes, TARGETS, strict=True):
        subset = errors.loc[errors["target"].eq(target)]
        for model in ("Ridge", "Random Forest"):
            values = subset.loc[subset["model"].eq(model), "residual"]
            axis.hist(values, bins=24, alpha=0.5, label=model, color=colors[model])
        axis.axvline(0, color="black", linestyle="--", linewidth=1)
        axis.set_title(f"{target}: residual distribution")
        axis.set_xlabel("Prediction - human score")
        axis.set_ylabel("Essays")
        axis.legend()
        axis.grid(alpha=0.2)
    path = FIGURE_DIR / "phase7_residual_distributions.png"
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return path


def plot_group_mae(group_metrics: pd.DataFrame) -> Path | None:
    length = group_metrics.loc[group_metrics["group_type"].eq("length_band")]
    if length.empty:
        return None
    figure, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    for axis, target in zip(axes, TARGETS, strict=True):
        subset = length.loc[length["target"].eq(target)]
        axis.bar(subset["group"], subset["mae"], color="#6a3d9a")
        axis.set_title(f"{target}: selected point-predictor MAE by length")
        axis.set_xlabel("Train-derived word-count quartile")
        axis.set_ylabel("MAE (score points)")
        axis.grid(axis="y", alpha=0.2)
    path = FIGURE_DIR / "phase7_mae_by_length_band.png"
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return path


def write_report(
    metrics: pd.DataFrame,
    comparisons: pd.DataFrame,
    point_predictors: pd.DataFrame,
    errors: pd.DataFrame,
    error_summary: pd.DataFrame,
    scorer_distribution: pd.DataFrame,
    machine_by_human_score: pd.DataFrame,
    group_metrics: pd.DataFrame,
    phase5_summary: dict[str, object],
    phase6_metadata: dict[str, object],
    figure_paths: list[Path],
) -> None:
    selected_errors = errors.sort_values("absolute_error", ascending=False).head(10)
    baseline_result = (
        "Every full-feature model has lower MAE than all four available Phase 5 baselines."
        if comparisons["mae_improvement_pct"].gt(0).all()
        else "At least one full-feature model does not beat every available Phase 5 baseline."
    )
    error_findings: list[str] = []
    for selection in point_predictors.to_dict(orient="records"):
        target = str(selection["target"])
        model = str(selection["selected_model"])
        summary_row = error_summary.loc[
            error_summary["target"].eq(target) & error_summary["model"].eq(model)
        ].iloc[0]
        largest = (
            errors.loc[errors["target"].eq(target) & errors["model"].eq(model)]
            .nlargest(1, "absolute_error")
            .iloc[0]
        )
        error_findings.append(
            f"- **{target} ({model}):** mean residual {summary_row['mean_residual']:.4f}, "
            f"90th-percentile absolute error {summary_row['p90_absolute_error']:.4f}, and maximum "
            f"absolute error {summary_row['max_absolute_error']:.4f} on essay `{largest['essay_id']}` "
            f"(human {largest['actual']:.2f}, prediction {largest['prediction']:.4f})."
        )
    score_band_findings: list[str] = []
    for target in TARGETS:
        bands = group_metrics.loc[
            group_metrics["group_type"].eq("score_band") & group_metrics["target"].eq(target)
        ].set_index("group")
        if {"2-<3", "3-<4", "4+"}.issubset(bands.index):
            score_band_findings.append(
                f"- **{target}:** MAE is {bands.loc['2-<3', 'mae']:.4f} for scores 2–<3 and "
                f"{bands.loc['4+', 'mae']:.4f} for scores 4+, versus "
                f"{bands.loc['3-<4', 'mae']:.4f} in the central 3–<4 band."
            )
    out_of_range = (
        error_summary[["predictions_below_1", "predictions_above_5"]].to_numpy(dtype=int).sum()
    )
    if out_of_range:
        outside = errors.loc[(errors["prediction"] < 1.0) | (errors["prediction"] > 5.0)].iloc[0]
        rubric_note = (
            f"One raw prediction falls outside the 1–5 rubric: {outside['model']} "
            f"{outside['target']} predicts {outside['prediction']:.4f} for essay "
            f"`{outside['essay_id']}`. It remains unclipped in every metric."
        )
    else:
        rubric_note = "No raw prediction falls outside the 1–5 rubric."
    report = [
        "# Phase 7 — Validation Regression Evaluation",
        "",
        "> **Scope:** eligible validation rows only; no model fitting, tuning, disagreement queue, or official-test access.",
        "",
        "## Evaluation population",
        "",
        "Phase 7 joins the text-free Phase 6 predictions to human Vocabulary and Grammar scores by `essay_id`.",
        f"The evaluation population contains **{len(errors) // 4} eligible validation essays** "
        "(each essay contributes four model/target error rows). The 21 excluded validation rows "
        "remain outside prediction and metrics.",
        "",
        f"Phase 5 baseline artifacts were re-hashed and their metrics recomputed before comparison. "
        f"The Phase 5 summary records {phase5_summary['validation_rows_after_privacy_filter']} eligible validation rows; "
        f"Phase 6 records {phase6_metadata['validation_prediction_rows']} predictions.",
        "",
        "## Regression metrics",
        "",
        markdown_table(
            metrics,
            ["model", "target", "n_samples", "mae", "rmse", "r2"],
        ),
        "",
        "Predictions are continuous values exactly as saved by Phase 6; no rounding or clipping was applied before metric computation.",
        "",
        "## Human and machine score statistics",
        "",
        "The human rows describe the reference-score distribution. Ridge and Random Forest rows describe continuous, unrounded machine predictions on the same 762 essays.",
        "",
        markdown_table(
            scorer_distribution,
            [
                "target",
                "scorer",
                "n_samples",
                "mean",
                "standard_deviation",
                "minimum",
                "q25",
                "median",
                "q75",
                "maximum",
            ],
        ),
        "",
        "Machine behavior at each observed human-score level is reported below. `mean_difference_machine_minus_human` is positive for overprediction and negative for underprediction. Tolerance rates use raw continuous predictions.",
        "",
        markdown_table(
            machine_by_human_score,
            [
                "target",
                "model",
                "human_score",
                "n_samples",
                "mean_machine_score",
                "mean_difference_machine_minus_human",
                "mae",
                "within_0_5_points_rate",
                "within_1_0_point_rate",
            ],
        ),
        "",
        "## Comparison with Phase 5 baselines",
        "",
        markdown_table(
            comparisons,
            [
                "model",
                "target",
                "baseline",
                "baseline_mae",
                "full_feature_mae",
                "mae_improvement_pct",
            ],
        ),
        "",
        "Positive improvement means the full-feature model has lower MAE. Negative values are retained as evidence that the model did not beat that baseline.",
        baseline_result,
        "",
        "## Point predictor selected per target",
        "",
        markdown_table(
            point_predictors,
            ["target", "ridge_mae", "random_forest_mae", "selected_model", "tie_within_atol"],
        ),
        "",
        "The rule is applied separately to Vocabulary and Grammar: lower validation MAE wins; Ridge is selected when the MAEs tie within 1e-12. The two predictions are not averaged.",
        "",
        "## Error analysis",
        "",
        markdown_table(
            error_summary,
            [
                "model",
                "target",
                "mean_residual",
                "median_absolute_error",
                "p90_absolute_error",
                "max_absolute_error",
                "predictions_below_1",
                "predictions_above_5",
            ],
        ),
        "",
        *error_findings,
        "",
        "The score-band pattern is consistent with regression toward the middle of the rubric: errors are larger at lower and higher reference-score bands than in the central band. Near-zero overall mean residuals therefore do not imply uniformly unbiased predictions across score levels.",
        "",
        *score_band_findings,
        "",
        rubric_note,
        "",
        "The largest absolute-error table contains IDs and scores only; essay text is not copied into any Phase 7 output.",
        "",
        "Top absolute-error rows (for diagnostic follow-up):",
        "",
        markdown_table(
            selected_errors,
            ["essay_id", "model", "target", "actual", "prediction", "residual", "absolute_error"],
        ),
        "",
        "## Subgroup checks",
        "",
        "Length groups use quartile cut points derived from model-train `word_count`; score bands are fixed exploratory intervals. Groups with fewer than 20 validation essays are omitted.",
        "",
        (
            markdown_table(
                group_metrics,
                [
                    "group_type",
                    "group",
                    "target",
                    "selected_model",
                    "n_samples",
                    "mae",
                    "rmse",
                    "r2",
                ],
            )
            if not group_metrics.empty
            else "No subgroup met the minimum sample-size threshold."
        ),
        "",
        "## Outputs and limitations",
        "",
        "- Metrics are validation-based and support model selection; they are not an independent final test estimate.",
        "- This phase does not compute model disagreement, review priority, error capture, ablations, or official-test performance.",
        "- Residuals and subgroup results describe observed validation behavior and do not establish causal explanations.",
        "- Official-test features and labels were not read, loaded, previewed, or used.",
        "",
        "Generated figures:",
        "",
    ]
    report.extend(f"- `{path.relative_to(ROOT).as_posix()}`" for path in figure_paths)
    report.extend(
        [
            "",
            "Reproduce with:",
            "",
            "```powershell",
            "uv run --extra analysis python scripts/phase7_evaluate_regression_models.py",
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    joined, validation_labels, phase6_metadata = load_and_validate_inputs()
    baseline_metrics, review_metrics, phase5_summary = validate_phase5_baselines(validation_labels)
    metrics = regression_metrics_table(joined)
    point_predictors = choose_point_predictors(metrics)
    metrics["selected_point_predictor"] = metrics.apply(
        lambda row: bool(
            point_predictors.loc[
                point_predictors["target"].eq(row["target"]), "selected_model"
            ].iloc[0]
            == row["model"]
        ),
        axis=1,
    )
    comparisons = baseline_comparison_table(metrics, baseline_metrics)
    errors = error_table(joined)
    error_summary = error_summary_table(errors)
    scorer_distribution = scorer_distribution_table(joined)
    machine_by_human_score = machine_by_human_score_table(joined)
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    split_manifest = pd.read_csv(SPLIT_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, split_manifest)
    group_frame = assign_analysis_groups(prepared.train, validation_labels)
    group_metrics = grouped_mae_table(joined, group_frame, point_predictors)

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    PREDICTIONS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    predictions_output = joined.loc[:, list(PREDICTION_COLUMNS)]
    predictions_output.to_csv(PREDICTIONS_OUTPUT_PATH, index=False, float_format="%.12g")
    metrics.to_csv(TABLE_DIR / "regression_metrics.csv", index=False, float_format="%.12g")
    comparisons.to_csv(TABLE_DIR / "baseline_comparisons.csv", index=False, float_format="%.12g")
    point_predictors.to_csv(TABLE_DIR / "point_predictors.csv", index=False, float_format="%.12g")
    errors.to_csv(TABLE_DIR / "error_rows.csv", index=False, float_format="%.12g")
    error_summary.to_csv(TABLE_DIR / "error_summary.csv", index=False, float_format="%.12g")
    scorer_distribution.to_csv(
        TABLE_DIR / "scorer_distribution_summary.csv", index=False, float_format="%.12g"
    )
    machine_by_human_score.to_csv(
        TABLE_DIR / "machine_by_human_score.csv", index=False, float_format="%.12g"
    )
    group_metrics.to_csv(TABLE_DIR / "error_by_group.csv", index=False, float_format="%.12g")
    errors.sort_values("absolute_error", ascending=False).head(40).to_csv(
        TABLE_DIR / "largest_errors.csv", index=False, float_format="%.12g"
    )

    figure_paths = [plot_predicted_vs_human(joined), plot_residuals(errors)]
    group_figure = plot_group_mae(group_metrics)
    if group_figure is not None:
        figure_paths.append(group_figure)
    write_report(
        metrics,
        comparisons,
        point_predictors,
        errors,
        error_summary,
        scorer_distribution,
        machine_by_human_score,
        group_metrics,
        phase5_summary,
        phase6_metadata,
        figure_paths,
    )

    summary = {
        "official_test_loaded": False,
        "evaluation_population": "eligible_validation_not_flagged",
        "validation_rows": len(joined),
        "model_train_rows": len(prepared.train),
        "excluded_validation_rows": int(
            len(split_manifest.loc[split_manifest["split"].eq("validation")]) - len(joined)
        ),
        "feature_count": len(FEATURE_NAMES),
        "metrics": ["mae", "rmse", "r2"],
        "predictions_continuous_unrounded": True,
        "validation_metrics_used_for_point_selection": True,
        "disagreement_queue_computed": False,
        "official_test_evaluated": False,
        "baseline_artifacts_verified": True,
        "phase5_baseline_review_metrics_loaded": True,
        "point_predictors": point_predictors.to_dict(orient="records"),
        "input_sha256": {
            "development_features": file_sha256(DEVELOPMENT_PATH),
            "split_manifest": file_sha256(SPLIT_PATH),
            "phase6_predictions": file_sha256(PHASE6_PREDICTIONS_PATH),
            "phase6_artifact_manifest": file_sha256(PHASE6_MANIFEST_PATH),
            "phase5_baseline_metrics": file_sha256(PHASE5_BASELINE_METRICS_PATH),
            "phase5_review_metrics": file_sha256(PHASE5_REVIEW_METRICS_PATH),
            "phase5_predictions": file_sha256(PHASE5_PREDICTIONS_PATH),
        },
        "output_sha256": {
            "predictions": file_sha256(PREDICTIONS_OUTPUT_PATH),
            "regression_metrics": file_sha256(TABLE_DIR / "regression_metrics.csv"),
            "baseline_comparisons": file_sha256(TABLE_DIR / "baseline_comparisons.csv"),
            "point_predictors": file_sha256(TABLE_DIR / "point_predictors.csv"),
            "error_summary": file_sha256(TABLE_DIR / "error_summary.csv"),
            "scorer_distribution_summary": file_sha256(
                TABLE_DIR / "scorer_distribution_summary.csv"
            ),
            "machine_by_human_score": file_sha256(TABLE_DIR / "machine_by_human_score.csv"),
            "error_by_group": file_sha256(TABLE_DIR / "error_by_group.csv"),
            "report": file_sha256(REPORT_PATH),
        },
        "phase5_review_baseline_rows": len(review_metrics),
        "phase5_review_metrics_sha256": file_sha256(PHASE5_REVIEW_METRICS_PATH),
    }
    (TABLE_DIR / "phase7_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
