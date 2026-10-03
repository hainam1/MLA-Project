"""Run the frozen Phase 8 review-prioritization study on validation only.

The script reads the official-train development feature table, frozen split manifest, and Phase 6
artifacts. It rejects non-validation evaluation rows and never reads official-test features,
predictions, or labels.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from mla_project.evaluation.phase8 import (
    add_review_signals,
    disagreement_ranking,
    metrics_for_selected_ids,
    random_reference_draws,
    review_count,
)
from mla_project.evaluation.regression_metrics import regression_metrics
from mla_project.pipelines.training_pipeline import load_model_artifacts, prepare_training_data
from mla_project.review.baselines import ridge_extremity, shortest_first

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
MANIFEST_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
PHASE6_DIR = ROOT / "outputs" / "phase6"
PHASE6_PREDICTIONS_PATH = PHASE6_DIR / "validation_predictions.csv"
TABLE_DIR = ROOT / "docs" / "data" / "phase8_tables"
REPORT_PATH = ROOT / "docs" / "phase8_review_prioritization.md"

PRIMARY_ERROR_THRESHOLD = 1.0
ERROR_THRESHOLDS = (0.5, 1.0, 1.5)
PRIMARY_REVIEW_BUDGET = 0.20
REVIEW_BUDGETS = (0.10, 0.20, 0.30)
RANDOM_SEED = 42
RANDOM_REPETITIONS = 1_000
EXPECTED_TRAIN_ROWS = 3_050
EXPECTED_VALIDATION_ROWS = 762


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    def render(value: object) -> str:
        if pd.isna(value):
            return "NA"
        if isinstance(value, (float, np.floating)):
            return f"{float(value):.6f}"
        return str(value)

    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for _, row in frame.loc[:, columns].iterrows():
        lines.append("| " + " | ".join(render(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def _load_validation_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    manifest = pd.read_csv(MANIFEST_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, manifest, eligible_status="not_flagged")
    if (
        len(prepared.train) != EXPECTED_TRAIN_ROWS
        or len(prepared.validation) != EXPECTED_VALIDATION_ROWS
    ):
        raise ValueError(
            "Phase 8 population does not match the frozen 3,050/762 development split."
        )

    predictions = pd.read_csv(PHASE6_PREDICTIONS_PATH, dtype={"essay_id": "string"})
    prediction_columns = [
        "essay_id",
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    ]
    missing = sorted(set(prediction_columns).difference(predictions.columns))
    if missing:
        raise ValueError(f"Phase 6 validation predictions are missing columns: {missing}")
    predictions = predictions.loc[:, prediction_columns]
    if predictions["essay_id"].duplicated().any():
        raise ValueError("Phase 6 validation predictions contain duplicate essay IDs.")
    expected_ids = set(prepared.validation["essay_id"].astype(str))
    if set(predictions["essay_id"].astype(str)) != expected_ids:
        raise ValueError("Phase 6 predictions do not exactly match eligible validation IDs.")

    validation = prepared.validation[
        ["essay_id", "split", "word_count", "Vocabulary", "Grammar"]
    ].merge(predictions, on="essay_id", how="inner", validate="one_to_one")
    models, feature_columns, metadata = load_model_artifacts(PHASE6_DIR)
    if metadata.get("official_test_loaded") is not False:
        raise ValueError("Phase 6 artifacts do not affirm that official test was excluded.")
    x_train = prepared.train.loc[:, list(feature_columns)]
    train_ridge = pd.DataFrame(
        {
            "ridge_vocabulary": models["ridge_vocabulary"].predict(x_train),
            "ridge_grammar": models["ridge_grammar"].predict(x_train),
        }
    )
    centers = {
        "median_ridge_vocabulary": float(train_ridge["ridge_vocabulary"].median()),
        "median_ridge_grammar": float(train_ridge["ridge_grammar"].median()),
    }
    return validation, prepared.train, centers


def _rankings(validation: pd.DataFrame, centers: dict[str, float], selected_count: int):
    shortest = shortest_first(validation[["essay_id", "word_count"]], selected_count=selected_count)
    extremity = ridge_extremity(
        validation[["essay_id", "ridge_vocabulary", "ridge_grammar"]],
        median_ridge_vocabulary=centers["median_ridge_vocabulary"],
        median_ridge_grammar=centers["median_ridge_grammar"],
        selected_count=selected_count,
    )
    disagreement = disagreement_ranking(validation, selected_count=selected_count)
    return {
        "Shortest-first": shortest,
        "Ridge extremity": extremity,
        "Ridge-RF disagreement": disagreement,
    }


def _summarize_random(draws: pd.DataFrame) -> dict[str, float | int | str]:
    row: dict[str, float | int | str] = {
        "strategy": "Random",
        "selected_count": int(draws["selected_count"].iloc[0]),
        "large_error_count": int(draws["large_error_count"].iloc[0]),
        "large_error_prevalence": float(draws["large_error_prevalence"].iloc[0]),
        "captured_count": float(draws["captured_count"].mean()),
    }
    for metric in ("capture_rate", "precision", "lift"):
        values = draws[metric].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        row[metric] = float(finite.mean()) if finite.size else float("nan")
        row[f"{metric}_reference_low"] = (
            float(np.percentile(finite, 2.5)) if finite.size else float("nan")
        )
        row[f"{metric}_reference_high"] = (
            float(np.percentile(finite, 97.5)) if finite.size else float("nan")
        )
    return row


def main() -> None:
    validation, _, centers = _load_validation_inputs()
    primary_signals = add_review_signals(validation, error_threshold=PRIMARY_ERROR_THRESHOLD)
    if len(primary_signals) != EXPECTED_VALIDATION_ROWS:
        raise ValueError("Phase 8 must evaluate exactly 762 validation essays.")

    comparison_rows: list[dict[str, object]] = []
    random_frames: list[pd.DataFrame] = []
    for threshold in ERROR_THRESHOLDS:
        signals = add_review_signals(validation, error_threshold=threshold)
        for budget in REVIEW_BUDGETS:
            selected_count = review_count(len(signals), budget)
            rankings = _rankings(signals, centers, selected_count)
            draws = random_reference_draws(
                signals["large_error"].to_numpy(dtype=bool),
                selected_count=selected_count,
                repetitions=RANDOM_REPETITIONS,
                random_seed=RANDOM_SEED,
            )
            draws.insert(0, "error_threshold", threshold)
            draws.insert(1, "review_budget", budget)
            random_frames.append(draws)
            rows = [_summarize_random(draws)]
            for strategy, ranking in rankings.items():
                selected_ids = set(ranking.loc[ranking["selected"], "essay_id"].astype(str))
                rows.append(metrics_for_selected_ids(signals, selected_ids, strategy=strategy))
            for row in rows:
                comparison_rows.append(
                    {
                        "is_primary": threshold == PRIMARY_ERROR_THRESHOLD
                        and budget == PRIMARY_REVIEW_BUDGET,
                        "error_threshold": threshold,
                        "review_budget": budget,
                        "validation_rows": len(signals),
                        "random_seed": RANDOM_SEED if row["strategy"] == "Random" else np.nan,
                        "random_repetitions": (
                            RANDOM_REPETITIONS if row["strategy"] == "Random" else np.nan
                        ),
                        **row,
                    }
                )

    comparison = pd.DataFrame(comparison_rows)
    random_distribution = pd.concat(random_frames, ignore_index=True)
    primary_count = review_count(len(primary_signals), PRIMARY_REVIEW_BUDGET)
    primary_rankings = _rankings(primary_signals, centers, primary_count)
    shortest = primary_rankings["Shortest-first"].set_index("essay_id")
    extremity = primary_rankings["Ridge extremity"].set_index("essay_id")
    disagreement = primary_rankings["Ridge-RF disagreement"].set_index("essay_id")

    score_table = primary_signals[
        [
            "essay_id",
            "word_count",
            "ridge_vocabulary",
            "ridge_grammar",
            "random_forest_vocabulary",
            "random_forest_grammar",
            "disagreement_vocabulary",
            "disagreement_grammar",
            "disagreement",
        ]
    ].copy()
    score_table["median_ridge_vocabulary"] = centers["median_ridge_vocabulary"]
    score_table["median_ridge_grammar"] = centers["median_ridge_grammar"]
    score_table["ridge_extremity"] = score_table["essay_id"].map(extremity["ridge_extremity"])
    score_table["shortest_rank"] = score_table["essay_id"].map(shortest["rank"])
    score_table["ridge_extremity_rank"] = score_table["essay_id"].map(extremity["rank"])
    score_table["disagreement_rank"] = score_table["essay_id"].map(disagreement["rank"])

    large_error_table = primary_signals[
        [
            "essay_id",
            "Vocabulary",
            "Grammar",
            "random_forest_vocabulary",
            "random_forest_grammar",
            "error_vocabulary",
            "error_grammar",
            "max_rf_absolute_error",
            "large_error",
        ]
    ].copy()

    correlations = pd.DataFrame(
        [
            {
                "comparison": "disagreement_vs_actual_max_rf_error",
                "spearman_rho": float(
                    spearmanr(
                        primary_signals["disagreement"], primary_signals["max_rf_absolute_error"]
                    ).statistic
                ),
            },
            {
                "comparison": "disagreement_vs_ridge_extremity",
                "spearman_rho": float(
                    spearmanr(score_table["disagreement"], score_table["ridge_extremity"]).statistic
                ),
            },
            {
                "comparison": "disagreement_vs_word_count",
                "spearman_rho": float(
                    spearmanr(score_table["disagreement"], score_table["word_count"]).statistic
                ),
            },
        ]
    )
    rf_metrics = pd.DataFrame(
        [
            {
                "target": target,
                **regression_metrics(
                    primary_signals[target].to_numpy(dtype=float),
                    primary_signals[f"random_forest_{target.lower()}"].to_numpy(dtype=float),
                ),
            }
            for target in ("Vocabulary", "Grammar")
        ]
    )

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(
        TABLE_DIR / "review_strategy_comparison.csv", index=False, float_format="%.12g"
    )
    random_distribution.to_csv(
        TABLE_DIR / "random_reference_distribution.csv", index=False, float_format="%.12g"
    )
    score_table.to_csv(TABLE_DIR / "disagreement_scores.csv", index=False, float_format="%.12g")
    large_error_table.to_csv(
        TABLE_DIR / "large_error_labels.csv", index=False, float_format="%.12g"
    )

    primary = comparison.loc[comparison["is_primary"]].copy()
    primary_random = primary.loc[primary["strategy"].eq("Random")]
    random_intervals = pd.DataFrame(
        [
            {
                "metric": metric,
                "mean": float(primary_random[metric].iloc[0]),
                "reference_2.5_percentile": float(
                    primary_random[f"{metric}_reference_low"].iloc[0]
                ),
                "reference_97.5_percentile": float(
                    primary_random[f"{metric}_reference_high"].iloc[0]
                ),
            }
            for metric in ("capture_rate", "precision", "lift")
        ]
    )
    report = [
        "# Phase 8: Validation Review Prioritization",
        "",
        "> Validation only: 762 privacy-eligible essays. No official-test predictions or labels were loaded or evaluated.",
        "",
        "## Frozen primary result",
        "",
        _markdown_table(
            primary,
            [
                "strategy",
                "selected_count",
                "large_error_count",
                "captured_count",
                "capture_rate",
                "precision",
                "lift",
            ],
        ),
        "",
        "Random values are means over 1,000 uniform selections without replacement. Its 2.5th-97.5th percentiles are empirical random-selection reference intervals, not bootstrap confidence intervals.",
        "",
        _markdown_table(
            random_intervals,
            [
                "metric",
                "mean",
                "reference_2.5_percentile",
                "reference_97.5_percentile",
            ],
        ),
        "",
        "## Correlations",
        "",
        _markdown_table(correlations, ["comparison", "spearman_rho"]),
        "",
        "## RF reference-predictor metrics",
        "",
        _markdown_table(rf_metrics, ["target", "mae", "rmse", "r2", "qwk"]),
        "",
        "## Protocol",
        "",
        f"- Primary large error: maximum RF absolute error >= {PRIMARY_ERROR_THRESHOLD:.1f}.",
        f"- Primary review budget: {PRIMARY_REVIEW_BUDGET:.0%}, selecting {primary_count} essays by ceiling.",
        f"- Ridge centers are medians of predictions on {EXPECTED_TRAIN_ROWS:,} eligible model-train essays: Vocabulary {centers['median_ridge_vocabulary']:.12g}, Grammar {centers['median_ridge_grammar']:.12g}.",
        "- Shortest-first ranks word count ascending; extremity and disagreement rank descending; deterministic ties use ascending string essay ID.",
        "- Disagreement is a triage signal, not a probability of error or calibrated confidence.",
        "- Thresholds 0.5 and 1.5 and budgets 10% and 30% are sensitivity analyses in the output table; they do not replace the primary result.",
        "",
        "## Interpretation",
        "",
    ]
    disagreement_row = primary.loc[primary["strategy"].eq("Ridge-RF disagreement")].iloc[0]
    deterministic = primary.loc[~primary["strategy"].eq("Random")]
    best_capture = float(deterministic["capture_rate"].max())
    if float(disagreement_row["capture_rate"]) == best_capture:
        tied = deterministic.loc[
            deterministic["capture_rate"].eq(best_capture), "strategy"
        ].tolist()
        if len(tied) > 1:
            interpretation = (
                "Ridge-RF disagreement ties with "
                + ", ".join(strategy for strategy in tied if strategy != "Ridge-RF disagreement")
                + " for the highest deterministic validation capture rate under the frozen primary protocol."
            )
        else:
            interpretation = "Ridge-RF disagreement has the highest deterministic validation capture rate under the frozen primary protocol."
    else:
        interpretation = "Ridge-RF disagreement does not attain the highest deterministic validation capture rate under the frozen primary protocol. This is a negative comparative result, not a project failure."
    report.extend([interpretation, ""])
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "official_test_loaded": False,
                "validation_rows": len(primary_signals),
                "selected_count": primary_count,
                "ridge_centers": centers,
                "primary_results": primary[
                    [
                        "strategy",
                        "selected_count",
                        "large_error_count",
                        "captured_count",
                        "capture_rate",
                        "precision",
                        "lift",
                    ]
                ].to_dict(orient="records"),
                "correlations": correlations.to_dict(orient="records"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
