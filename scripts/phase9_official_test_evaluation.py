"""Execute the one-time official-test evaluation under the frozen protocol.

This script contains no fitting or hyperparameter-search operation. It refuses to run when any
Phase 9 output already exists.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from mla_project.evaluation.phase8 import (
    disagreement_ranking,
    metrics_for_selected_ids,
    random_reference_draws,
    review_count,
)
from mla_project.evaluation.phase8b import fairness_table, summarize_error_groups
from mla_project.evaluation.phase9 import (
    ERROR_THRESHOLDS,
    EXPECTED_TOTAL_ROWS,
    PRIMARY_ERROR_THRESHOLD,
    PRIMARY_REVIEW_BUDGET,
    RANDOM_REPETITIONS,
    RANDOM_SEED,
    REFERENCE_PREDICTORS,
    REVIEW_BUDGETS,
    RIDGE_CENTERS,
    VALIDATION_DISAGREEMENT_THRESHOLD,
    add_frozen_test_signals,
    classify_confirmatory_evidence,
    prepare_official_population,
)
from mla_project.evaluation.regression_metrics import regression_metrics
from mla_project.features.build_features import FEATURE_NAMES
from mla_project.models.length_baselines import LENGTH_FEATURES, TARGETS
from mla_project.pipelines.training_pipeline import prepare_training_data
from mla_project.review.baselines import ridge_extremity, shortest_first

ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = ROOT / "data" / "05_model_features" / "official_test_features.csv"
LABELS_PATH = ROOT / "data" / "03_clean_ready_to_use" / "official_test_2571.csv"
MANIFEST_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
PHASE6_DIR = ROOT / "outputs" / "phase6"
LENGTH_MODEL_DIR = ROOT / "outputs" / "phase5" / "reconstructed"
PREDICTIONS_PATH = ROOT / "outputs" / "predictions" / "official_test_predictions.csv"
TABLE_DIR = ROOT / "docs" / "data" / "phase9_tables"
REPORT_PATH = ROOT / "docs" / "phase9_official_test_evaluation.md"
PROTOCOL_PATH = ROOT / "docs" / "evaluation_protocol_freeze.md"
ADDENDUM_PATH = ROOT / "docs" / "length_baseline_reconstruction_addendum.md"

PHASE6_HASHES = {
    "ridge_vocabulary.joblib": "14591A1822FFA4FC7C9006A5ABD270928401721739BEA3F9FE5A76852780EF64",
    "ridge_grammar.joblib": "812885CAAB21DAC6508835C83DC91DE75B23D622577BA15A8E37E207E59B085F",
    "random_forest_vocabulary.joblib": "899E9283E2EB01B4DF6913EADD6CF8A4A823DF0298DDFE820D14BA5912FFE7BE",
    "random_forest_grammar.joblib": "BC285A202DE126247240982696CA94C16DBEE82BF15906D8E75EBDF4405A8F91",
}
LENGTH_MODEL_HASHES = {
    "length_ridge_vocabulary.joblib": "AA069D615F77BE8CCE8561E6044A4D73F22805537DBFDBD79D8DC38876187FBA",
    "length_random_forest_vocabulary.joblib": "EBA39122B5F2A7209954D9D7B44C59BBB71D6F5C4EA707F14CEBA7A14C7E3324",
    "length_ridge_grammar.joblib": "1F7A2DB84DC086860B6EFC4A75BB8ECFB418EDDF89C6D7643B9C7ADD296B60B5",
    "length_random_forest_grammar.joblib": "73B16013F4AE9B043E1A8FCE688AD39AFC3ACA85D070A89FFE29E0BD30B55CF6",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_verified_models(directory: Path, expected: dict[str, str]) -> dict[str, Any]:
    models: dict[str, Any] = {}
    for filename, frozen_hash in expected.items():
        path = directory / filename
        if not path.is_file() or sha256(path) != frozen_hash:
            raise ValueError(f"Frozen model hash mismatch: {path}")
        models[filename.removesuffix(".joblib")] = joblib.load(path)
    return models


def assert_one_time_gate() -> None:
    targets = [
        PREDICTIONS_PATH,
        REPORT_PATH,
        TABLE_DIR / "artifact_manifest.json",
        TABLE_DIR / "regression_metrics.csv",
    ]
    existing = [str(path) for path in targets if path.exists()]
    if existing:
        raise FileExistsError(f"Phase 9 is one-time only; outputs already exist: {existing}")


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
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


def random_summary(draws: pd.DataFrame) -> dict[str, object]:
    row: dict[str, object] = {
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


def rankings(signals: pd.DataFrame, selected_count: int) -> dict[str, pd.DataFrame]:
    return {
        "Shortest-first": shortest_first(
            signals[["essay_id", "word_count"]], selected_count=selected_count
        ),
        "Ridge extremity": ridge_extremity(
            signals[["essay_id", "ridge_vocabulary", "ridge_grammar"]],
            **RIDGE_CENTERS,
            selected_count=selected_count,
        ),
        "Ridge-RF disagreement": disagreement_ranking(signals, selected_count=selected_count),
    }


def main() -> None:
    assert_one_time_gate()
    phase6_models = load_verified_models(PHASE6_DIR, PHASE6_HASHES)
    length_models = load_verified_models(LENGTH_MODEL_DIR, LENGTH_MODEL_HASHES)
    if tuple(FEATURE_NAMES) != (
        "word_count",
        "sentence_count",
        "mean_sentence_length",
        "mtld",
        "mattr",
        "mean_word_frequency",
        "mean_word_length",
        "lexical_density",
        "noun_diversity",
        "detected_grammar_errors_per_100_words",
        "detected_error_free_sentence_ratio",
        "complex_sentence_ratio",
        "estimated_clauses_per_sentence",
        "subordinate_clause_ratio",
    ):
        raise ValueError("Frozen 14-feature schema changed before Phase 9.")

    features = pd.read_csv(FEATURES_PATH, dtype={"essay_id": "string"})
    labels = pd.read_csv(
        LABELS_PATH,
        usecols=["essay_id", "vocabulary", "grammar", "gender", "race_ethnicity", "ses"],
        dtype={"essay_id": "string"},
    ).rename(columns={"vocabulary": "Vocabulary", "grammar": "Grammar", "ses": "SES"})
    manifest = pd.read_csv(MANIFEST_PATH, dtype={"essay_id": "string"})
    population = prepare_official_population(features, labels, manifest)

    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, manifest, eligible_status="not_flagged")
    train_means = {target: float(prepared.train[target].mean()) for target in TARGETS}

    x_full = population.loc[:, list(FEATURE_NAMES)]
    x_length = population.loc[:, list(LENGTH_FEATURES)]
    predictions = pd.DataFrame({"essay_id": population["essay_id"].to_numpy()})
    for name, model in phase6_models.items():
        predictions[name] = model.predict(x_full)
    for name, model in length_models.items():
        predictions[name] = model.predict(x_length)
    for target in TARGETS:
        lower = target.lower()
        predictions[f"mean_{lower}"] = train_means[target]
        predictions[f"length_consensus_{lower}"] = (
            predictions[f"length_ridge_{lower}"] + predictions[f"length_random_forest_{lower}"]
        ) / 2.0

    analysis = population[
        ["essay_id", "word_count", "Vocabulary", "Grammar", "gender", "race_ethnicity", "SES"]
    ].merge(predictions, on="essay_id", validate="one_to_one")
    signals = add_frozen_test_signals(analysis)

    metric_rows: list[dict[str, object]] = []
    model_columns = {
        "Ridge": "ridge",
        "Random Forest": "random_forest",
        "Mean-score baseline": "mean",
        "Length-only Ridge": "length_ridge",
        "Length-only Random Forest": "length_random_forest",
        "Length-only consensus": "length_consensus",
    }
    for target in TARGETS:
        for model_name, prefix in model_columns.items():
            values = regression_metrics(
                signals[target].to_numpy(dtype=float),
                signals[f"{prefix}_{target.lower()}"].to_numpy(dtype=float),
            )
            metric_rows.append(
                {
                    "model": model_name,
                    "target": target,
                    "n": len(signals),
                    **values,
                }
            )
    regression = pd.DataFrame(metric_rows)

    comparison_rows: list[dict[str, object]] = []
    random_frames: list[pd.DataFrame] = []
    for threshold in ERROR_THRESHOLDS:
        threshold_signals = add_frozen_test_signals(analysis, error_threshold=threshold)
        for budget in REVIEW_BUDGETS:
            selected_count = review_count(len(threshold_signals), budget)
            fixed_rankings = rankings(threshold_signals, selected_count)
            draws = random_reference_draws(
                threshold_signals["large_error"].to_numpy(dtype=bool),
                selected_count=selected_count,
                repetitions=RANDOM_REPETITIONS,
                random_seed=RANDOM_SEED,
            )
            draws.insert(0, "error_threshold", threshold)
            draws.insert(1, "review_budget", budget)
            random_frames.append(draws)
            rows = [random_summary(draws)]
            for strategy, ranking in fixed_rankings.items():
                selected_ids = set(ranking.loc[ranking["selected"], "essay_id"].astype(str))
                rows.append(
                    metrics_for_selected_ids(threshold_signals, selected_ids, strategy=strategy)
                )
            for row in rows:
                comparison_rows.append(
                    {
                        "analysis_role": (
                            "primary"
                            if threshold == PRIMARY_ERROR_THRESHOLD
                            and budget == PRIMARY_REVIEW_BUDGET
                            else "sensitivity"
                        ),
                        "error_threshold": threshold,
                        "review_budget": budget,
                        "test_rows": len(threshold_signals),
                        "random_seed": RANDOM_SEED if row["strategy"] == "Random" else np.nan,
                        "random_repetitions": (
                            RANDOM_REPETITIONS if row["strategy"] == "Random" else np.nan
                        ),
                        **row,
                    }
                )
    comparison = pd.DataFrame(comparison_rows)
    random_distribution = pd.concat(random_frames, ignore_index=True)
    primary = comparison.loc[comparison["analysis_role"].eq("primary")].copy()
    primary_count = review_count(len(signals), PRIMARY_REVIEW_BUDGET)
    primary_rankings = rankings(signals, primary_count)
    signals["disagreement_selected"] = signals["essay_id"].isin(
        set(
            primary_rankings["Ridge-RF disagreement"]
            .loc[lambda frame: frame["selected"], "essay_id"]
            .astype(str)
        )
    )
    signals["shortest_selected"] = signals["essay_id"].isin(
        set(
            primary_rankings["Shortest-first"]
            .loc[lambda frame: frame["selected"], "essay_id"]
            .astype(str)
        )
    )

    high_disagreement = signals["disagreement"].ge(VALIDATION_DISAGREEMENT_THRESHOLD)
    conditions = [
        high_disagreement & signals["large_error"],
        high_disagreement & ~signals["large_error"],
        ~high_disagreement & signals["large_error"],
    ]
    labels_quadrant = [
        "High disagreement + Large error",
        "High disagreement + No large error",
        "Low disagreement + Large error",
    ]
    signals["error_quadrant"] = np.select(
        conditions, labels_quadrant, default="Low disagreement + No large error"
    )
    quadrants = summarize_error_groups(signals, ["error_quadrant"])
    quadrants.insert(1, "frozen_disagreement_threshold", VALIDATION_DISAGREEMENT_THRESHOLD)
    fairness = fairness_table(signals, selected_count=primary_count)

    correlations = {
        "disagreement_vs_actual_max_rf_error": float(
            spearmanr(signals["disagreement"], signals["max_rf_absolute_error"]).statistic
        ),
        "disagreement_vs_ridge_extremity": float(
            spearmanr(
                signals["disagreement"],
                signals["essay_id"].map(
                    primary_rankings["Ridge extremity"].set_index("essay_id")["ridge_extremity"]
                ),
            ).statistic
        ),
        "disagreement_vs_word_count": float(
            spearmanr(signals["disagreement"], signals["word_count"]).statistic
        ),
    }

    validation_regression = pd.read_csv(
        ROOT / "docs" / "data" / "phase7_tables" / "regression_metrics.csv"
    )
    validation_review = pd.read_csv(
        ROOT / "docs" / "data" / "phase8_tables" / "review_strategy_comparison.csv"
    )
    validation_primary = validation_review.loc[validation_review["is_primary"]]
    validation_quadrants = pd.read_csv(
        ROOT / "docs" / "data" / "phase8_tables" / "error_quadrants.csv"
    )

    def metric_mae(model: str, target: str, source: pd.DataFrame) -> float:
        return float(
            source.loc[source["model"].eq(model) & source["target"].eq(target), "mae"].iloc[0]
        )

    def capture(strategy: str, source: pd.DataFrame) -> float:
        return float(source.loc[source["strategy"].eq(strategy), "capture_rate"].iloc[0])

    disagreement_primary = primary.loc[primary["strategy"].eq("Ridge-RF disagreement")].iloc[0]
    validation_disagreement = validation_primary.loc[
        validation_primary["strategy"].eq("Ridge-RF disagreement")
    ].iloc[0]
    test_blind_spot = float(
        quadrants.loc[
            quadrants["error_quadrant"].eq("Low disagreement + Large error"), "percentage"
        ].iloc[0]
        / 100.0
    )
    validation_blind_spot = float(
        validation_quadrants.loc[
            validation_quadrants["error_quadrant"].eq("Low disagreement + Large error"),
            "percentage",
        ].iloc[0]
        / 100.0
    )
    test_metric_lookup = regression.set_index(["model", "target"])
    comparison_metrics = [
        (
            "Ridge Vocabulary MAE",
            metric_mae("Ridge", "Vocabulary", validation_regression),
            float(test_metric_lookup.loc[("Ridge", "Vocabulary"), "mae"]),
        ),
        (
            "RF Vocabulary MAE",
            metric_mae("Random Forest", "Vocabulary", validation_regression),
            float(test_metric_lookup.loc[("Random Forest", "Vocabulary"), "mae"]),
        ),
        (
            "Ridge Grammar MAE",
            metric_mae("Ridge", "Grammar", validation_regression),
            float(test_metric_lookup.loc[("Ridge", "Grammar"), "mae"]),
        ),
        (
            "RF Grammar MAE",
            metric_mae("Random Forest", "Grammar", validation_regression),
            float(test_metric_lookup.loc[("Random Forest", "Grammar"), "mae"]),
        ),
        ("Large-error prevalence", 69 / 762, float(signals["large_error"].mean())),
        (
            "Random Capture Rate @20%",
            capture("Random", validation_primary),
            capture("Random", primary),
        ),
        (
            "Shortest Capture Rate @20%",
            capture("Shortest-first", validation_primary),
            capture("Shortest-first", primary),
        ),
        (
            "Ridge Extremity Capture Rate @20%",
            capture("Ridge extremity", validation_primary),
            capture("Ridge extremity", primary),
        ),
        (
            "Disagreement Capture Rate @20%",
            float(validation_disagreement["capture_rate"]),
            float(disagreement_primary["capture_rate"]),
        ),
        (
            "Disagreement Precision @20%",
            float(validation_disagreement["precision"]),
            float(disagreement_primary["precision"]),
        ),
        (
            "Disagreement Lift @20%",
            float(validation_disagreement["lift"]),
            float(disagreement_primary["lift"]),
        ),
        ("Shared-blind-spot proportion", validation_blind_spot, test_blind_spot),
    ]
    validation_vs_test = pd.DataFrame(
        comparison_metrics, columns=["metric", "validation", "official_test"]
    )

    large_error_output = signals[
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
    large_error_output["vocabulary_large_error"] = large_error_output["error_vocabulary"].ge(1.0)
    large_error_output["grammar_large_error"] = large_error_output["error_grammar"].ge(1.0)
    vocabulary_only = int(
        (
            large_error_output["vocabulary_large_error"]
            & ~large_error_output["grammar_large_error"]
        ).sum()
    )
    grammar_only = int(
        (
            ~large_error_output["vocabulary_large_error"]
            & large_error_output["grammar_large_error"]
        ).sum()
    )
    both_traits = int(
        (
            large_error_output["vocabulary_large_error"] & large_error_output["grammar_large_error"]
        ).sum()
    )

    random_primary = primary.loc[primary["strategy"].eq("Random")].iloc[0]
    classification = classify_confirmatory_evidence(
        disagreement=float(disagreement_primary["capture_rate"]),
        random_mean=float(random_primary["capture_rate"]),
        shortest=capture("Shortest-first", primary),
        ridge_extremity=capture("Ridge extremity", primary),
    )

    TABLE_DIR.mkdir(parents=True, exist_ok=False)
    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(PREDICTIONS_PATH, index=False, float_format="%.12g")
    regression.to_csv(TABLE_DIR / "regression_metrics.csv", index=False, float_format="%.12g")
    primary.to_csv(TABLE_DIR / "review_strategy_comparison.csv", index=False, float_format="%.12g")
    random_distribution.to_csv(
        TABLE_DIR / "random_reference_distribution.csv", index=False, float_format="%.12g"
    )
    large_error_output.to_csv(
        TABLE_DIR / "large_error_labels.csv", index=False, float_format="%.12g"
    )
    quadrants.to_csv(TABLE_DIR / "error_quadrants.csv", index=False, float_format="%.12g")
    fairness.to_csv(TABLE_DIR / "fairness_audit.csv", index=False, float_format="%.12g")
    comparison.to_csv(TABLE_DIR / "sensitivity_analysis.csv", index=False, float_format="%.12g")
    validation_vs_test.to_csv(
        TABLE_DIR / "validation_vs_test.csv", index=False, float_format="%.12g"
    )

    report = [
        "# Phase 9: One-Time Official-Test Evaluation",
        "",
        "> Confirmatory evaluation under the frozen protocol. Models, features, reference predictors, thresholds, budgets, rankings, and metrics were not changed after test access.",
        "",
        "## Population and integrity",
        "",
        f"- Official-test rows: {EXPECTED_TOTAL_ROWS:,}; privacy-eligible rows evaluated: {len(signals):,}.",
        f"- Primary review budget: 20%, K = {primary_count}.",
        "- All four Phase 6 and four reconstructed Phase 5 length-only model hashes matched before prediction.",
        "- No model was retrained during Phase 9.",
        "",
        "## Regression metrics",
        "",
        markdown_table(regression, ["model", "target", "n", "mae", "rmse", "qwk"]),
        "",
        "## Large errors",
        "",
        f"There were {int(signals['large_error'].sum())} large errors ({signals['large_error'].mean():.6%}): {vocabulary_only} Vocabulary-only, {grammar_only} Grammar-only, and {both_traits} on both traits.",
        "",
        "## Frozen primary review comparison",
        "",
        markdown_table(
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
        f"Random empirical intervals: Capture Rate {float(random_primary['capture_rate_reference_low']):.6f}-{float(random_primary['capture_rate_reference_high']):.6f}; Precision {float(random_primary['precision_reference_low']):.6f}-{float(random_primary['precision_reference_high']):.6f}; Lift {float(random_primary['lift_reference_low']):.6f}-{float(random_primary['lift_reference_high']):.6f}.",
        "",
        "## Error quadrants",
        "",
        f"The high-disagreement threshold remained the frozen validation median, D = {VALIDATION_DISAGREEMENT_THRESHOLD}.",
        "",
        markdown_table(
            quadrants,
            [
                "error_quadrant",
                "n",
                "percentage",
                "mean_disagreement",
                "mean_max_rf_error",
                "mean_word_count",
            ],
        ),
        "",
        "## Fairness audit",
        "",
        markdown_table(
            fairness,
            [
                "attribute",
                "group",
                "n",
                "vocabulary_mae",
                "grammar_mae",
                "large_error_prevalence",
                "disagreement_selection_rate",
                "within_group_capture_rate",
                "shortest_first_selection_rate",
                "random_expected_selection_rate",
                "small_n_flag",
            ],
        ),
        "",
        "These are observed subgroup differences, not automatic evidence of bias or unfairness. Demographics were not model predictors.",
        "",
        "## Diagnostics",
        "",
        *[f"- {name}: Spearman rho = {value:.6f}" for name, value in correlations.items()],
        "",
        "## Validation versus official test",
        "",
        markdown_table(validation_vs_test, ["metric", "validation", "official_test"]),
        "",
        "## Confirmatory interpretation",
        "",
        f"**{classification}**",
        "",
        "This classification follows the frozen comparison against random selection, shortest-first, and Ridge extremity. Test results were not used to alter the protocol. All predeclared sensitivity combinations are reported in `sensitivity_analysis.csv`.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")

    output_paths = [
        PREDICTIONS_PATH,
        TABLE_DIR / "regression_metrics.csv",
        TABLE_DIR / "review_strategy_comparison.csv",
        TABLE_DIR / "random_reference_distribution.csv",
        TABLE_DIR / "large_error_labels.csv",
        TABLE_DIR / "error_quadrants.csv",
        TABLE_DIR / "fairness_audit.csv",
        TABLE_DIR / "sensitivity_analysis.csv",
        TABLE_DIR / "validation_vs_test.csv",
        REPORT_PATH,
    ]
    artifact_manifest = {
        "one_time_official_test_evaluation": True,
        "official_test_loaded": True,
        "models_retrained": False,
        "total_rows": EXPECTED_TOTAL_ROWS,
        "eligible_rows": len(signals),
        "primary_selected_count": primary_count,
        "reference_predictors": REFERENCE_PREDICTORS,
        "frozen_ridge_centers": RIDGE_CENTERS,
        "frozen_disagreement_threshold": VALIDATION_DISAGREEMENT_THRESHOLD,
        "phase6_model_sha256": PHASE6_HASHES,
        "length_model_sha256": LENGTH_MODEL_HASHES,
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "addendum_sha256": sha256(ADDENDUM_PATH),
        "input_sha256": {
            "official_test_features": sha256(FEATURES_PATH),
            "official_test_labels": sha256(LABELS_PATH),
            "split_manifest": sha256(MANIFEST_PATH),
        },
        "output_sha256": {path.relative_to(ROOT).as_posix(): sha256(path) for path in output_paths},
        "large_error_summary": {
            "count": int(signals["large_error"].sum()),
            "prevalence": float(signals["large_error"].mean()),
            "vocabulary_only": vocabulary_only,
            "grammar_only": grammar_only,
            "both_traits": both_traits,
        },
        "correlations": correlations,
        "confirmatory_classification": classification,
    }
    manifest_path = TABLE_DIR / "artifact_manifest.json"
    manifest_path.write_text(json.dumps(artifact_manifest, indent=2), encoding="utf-8")
    print(json.dumps(artifact_manifest, indent=2))


if __name__ == "__main__":
    main()
