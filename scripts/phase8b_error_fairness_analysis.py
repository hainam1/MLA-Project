"""Produce the frozen validation-only Phase 8B error and fairness audit."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from mla_project.evaluation.phase8 import review_count
from mla_project.evaluation.phase8b import (
    assign_error_quadrants,
    fairness_table,
    summarize_by_human_score,
    summarize_error_groups,
)
from mla_project.pipelines.training_pipeline import prepare_training_data

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
MANIFEST_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
VALIDATION_METADATA_PATH = ROOT / "data" / "03_clean_ready_to_use" / "validation_783.csv"
PHASE8_DIR = ROOT / "docs" / "data" / "phase8_tables"
PHASE8_SCORES_PATH = PHASE8_DIR / "disagreement_scores.csv"
PHASE8_LABELS_PATH = PHASE8_DIR / "large_error_labels.csv"
PHASE8_COMPARISON_PATH = PHASE8_DIR / "review_strategy_comparison.csv"
HUMAN_RATER_PATH = ROOT / "docs" / "data" / "improvement_tables" / "human_machine_reliability.csv"
REPORT_PATH = ROOT / "docs" / "phase8_error_fairness_analysis.md"

EXPECTED_VALIDATION_ROWS = 762
PRIMARY_BUDGET = 0.20
PRIMARY_ERROR_THRESHOLD = 1.0
EXPECTED_SENSITIVITY_BUDGETS = {0.10, 0.20, 0.30}
EXPECTED_SENSITIVITY_THRESHOLDS = {0.5, 1.0, 1.5}


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


def load_validation_analysis_frame() -> tuple[pd.DataFrame, pd.DataFrame]:
    scores = pd.read_csv(PHASE8_SCORES_PATH, dtype={"essay_id": "string"})
    labels = pd.read_csv(PHASE8_LABELS_PATH, dtype={"essay_id": "string"})
    metadata = pd.read_csv(
        VALIDATION_METADATA_PATH,
        usecols=["essay_id", "prompt", "gender", "race_ethnicity", "ses"],
        dtype={"essay_id": "string"},
    ).rename(columns={"prompt": "prompt_id", "ses": "SES"})
    if any(table["essay_id"].duplicated().any() for table in (scores, labels, metadata)):
        raise ValueError("Phase 8B inputs must contain unique essay IDs.")
    frame = labels.merge(
        scores[["essay_id", "word_count", "disagreement", "shortest_rank", "disagreement_rank"]],
        on="essay_id",
        how="inner",
        validate="one_to_one",
    ).merge(metadata, on="essay_id", how="left", validate="one_to_one")
    if (
        len(frame) != EXPECTED_VALIDATION_ROWS
        or frame[["prompt_id", "gender", "race_ethnicity", "SES"]].isna().any().any()
    ):
        raise ValueError("Phase 8B metadata join does not match 762 complete validation rows.")
    if not frame["large_error"].equals(frame["max_rf_absolute_error"].ge(1.0)):
        raise ValueError("Phase 8B large-error labels do not match the frozen >= 1.0 rule.")
    selected_count = review_count(len(frame), PRIMARY_BUDGET)
    frame["disagreement_selected"] = frame["disagreement_rank"].le(selected_count)
    frame["shortest_selected"] = frame["shortest_rank"].le(selected_count)

    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    manifest = pd.read_csv(MANIFEST_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, manifest, eligible_status="not_flagged")
    if len(prepared.validation) != EXPECTED_VALIDATION_ROWS:
        raise ValueError("Phase 8B is validation only and requires exactly 762 eligible rows.")
    return frame, prepared.train


def add_length_bands(frame: pd.DataFrame, train: pd.DataFrame) -> tuple[pd.DataFrame, list[float]]:
    quartiles = train["word_count"].quantile([0.25, 0.50, 0.75]).to_numpy(dtype=float)
    edges = [-np.inf, *np.unique(quartiles).tolist(), np.inf]
    labels = [f"Q{index}" for index in range(1, len(edges))]
    result = frame.copy()
    result["length_band"] = pd.cut(
        result["word_count"], edges, labels=labels, include_lowest=True, right=False
    )
    return result, edges


def validated_sensitivity_table() -> pd.DataFrame:
    table = pd.read_csv(PHASE8_COMPARISON_PATH)
    if set(table["error_threshold"]) != EXPECTED_SENSITIVITY_THRESHOLDS:
        raise ValueError("Phase 8 sensitivity thresholds do not match the frozen set.")
    if set(table["review_budget"]) != EXPECTED_SENSITIVITY_BUDGETS:
        raise ValueError("Phase 8 sensitivity budgets do not match the frozen set.")
    if set(table["validation_rows"]) != {EXPECTED_VALIDATION_ROWS}:
        raise ValueError("Sensitivity analysis must use exactly 762 validation rows.")
    table.insert(
        0,
        "analysis_role",
        np.where(table["is_primary"], "primary", "sensitivity"),
    )
    return table


def main() -> None:
    frame, train = load_validation_analysis_frame()
    frame, length_edges = add_length_bands(frame, train)
    frame, disagreement_threshold = assign_error_quadrants(frame)

    quadrants = summarize_error_groups(frame, ["error_quadrant"], include_score_distributions=True)
    quadrant_order = {
        "High disagreement + Large error": 1,
        "High disagreement + No large error": 2,
        "Low disagreement + Large error": 3,
        "Low disagreement + No large error": 4,
    }
    quadrants["order"] = quadrants["error_quadrant"].map(quadrant_order)
    quadrants.insert(1, "high_disagreement_threshold", disagreement_threshold)
    quadrants = quadrants.sort_values("order").drop(columns="order")
    by_length = summarize_error_groups(frame, ["length_band"])
    by_score = summarize_by_human_score(frame)
    by_prompt = summarize_error_groups(frame, ["prompt_id"])
    fairness = fairness_table(
        frame,
        selected_count=review_count(len(frame), PRIMARY_BUDGET),
    )
    sensitivity = validated_sensitivity_table()
    human_rater = pd.read_csv(HUMAN_RATER_PATH)

    quadrants.to_csv(PHASE8_DIR / "error_quadrants.csv", index=False, float_format="%.12g")
    by_length.to_csv(PHASE8_DIR / "error_by_length.csv", index=False, float_format="%.12g")
    by_score.to_csv(PHASE8_DIR / "error_by_score.csv", index=False, float_format="%.12g")
    by_prompt.to_csv(PHASE8_DIR / "error_by_prompt.csv", index=False, float_format="%.12g")
    fairness.to_csv(PHASE8_DIR / "fairness_audit.csv", index=False, float_format="%.12g")
    sensitivity.to_csv(PHASE8_DIR / "sensitivity_analysis.csv", index=False, float_format="%.12g")

    blind_spot = quadrants.loc[quadrants["error_quadrant"].eq("Low disagreement + Large error")]
    small_groups = fairness.loc[fairness["small_n_flag"]]
    primary = sensitivity.loc[sensitivity["analysis_role"].eq("primary")]
    prompt_report = by_prompt.loc[by_prompt["n"].ge(20)].sort_values(
        ["large_error_prevalence", "prompt_id"], ascending=[False, True]
    )
    report = [
        "# Phase 8B: Validation Error Analysis and Fairness Audit",
        "",
        "> Descriptive validation-only analysis under the frozen Phase 8 protocol. No model was retrained, no feature or threshold was changed, and no official-test prediction or label was accessed.",
        "",
        "## Error quadrants",
        "",
        f"High disagreement is frozen for this analysis as D >= the validation-population median, {disagreement_threshold:.12g}.",
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
        "The low-disagreement plus large-error quadrant is the shared-blind-spot group: both model families are relatively close while the selected RF reference prediction is still wrong by at least one point on one or both traits. This is an observed error pattern, not evidence of a causal mechanism.",
        "",
        "### Shared-blind-spot detail",
        "",
        markdown_table(
            blind_spot,
            [
                "n",
                "percentage",
                "mean_disagreement",
                "mean_max_rf_error",
                "vocabulary_overprediction_rate",
                "grammar_overprediction_rate",
                "vocabulary_human_score_distribution",
                "grammar_human_score_distribution",
            ],
        ),
        "",
        "## Errors by essay length",
        "",
        markdown_table(
            by_length,
            [
                "length_band",
                "n",
                "large_error_prevalence",
                "mean_max_rf_error",
                "vocabulary_mean_signed_error",
                "grammar_mean_signed_error",
            ],
        ),
        "",
        "## Errors by human score level and direction",
        "",
        markdown_table(
            by_score,
            [
                "target",
                "human_score",
                "n",
                "mean_target_absolute_error",
                "mean_target_signed_error",
                "overprediction_rate",
                "underprediction_rate",
                "large_error_prevalence",
            ],
        ),
        "",
        "Positive signed error is overprediction and negative signed error is underprediction. The observed pattern is regression toward the middle of the score scale; extreme score levels have very small samples and must be interpreted cautiously.",
        "",
        "## Errors by prompt",
        "",
        "The table below is limited to prompts with at least 20 eligible validation essays for readability. The complete 44-prompt descriptive table, including small groups, is in `error_by_prompt.csv`.",
        "",
        markdown_table(
            prompt_report,
            [
                "prompt_id",
                "n",
                "large_error_prevalence",
                "mean_max_rf_error",
                "vocabulary_mean_signed_error",
                "grammar_mean_signed_error",
            ],
        ),
        "",
        "## Fairness audit",
        "",
        "Demographic attributes are used only for this validation audit. They are not among the 14 model predictors.",
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
        "These are subgroup disparities or observed differences; this audit does not establish causation or justify labeling them as bias.",
        "",
        "## Sensitivity analysis",
        "",
        "The primary threshold remains 1.0 and the primary budget remains 20%. Thresholds 0.5 and 1.5 and budgets 10% and 30% are predeclared sensitivity analyses, not settings searched for favorable disagreement performance.",
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
        "All predeclared combinations are in `docs/data/phase8_tables/sensitivity_analysis.csv`.",
        "",
        "## Human-rater context",
        "",
        markdown_table(
            human_rater,
            [
                "trait",
                "n_samples",
                "human_human_mae",
                "within_0_5_points_rate",
                "quadratic_weighted_kappa",
                "model_aggregate_human_mae",
                "model_individual_human_mae",
            ],
        ),
        "",
        "Human-human MAE compares two individual ratings. Model-aggregate MAE compares a model with the released aggregate label, while model-individual MAE averages comparisons with each individual rater. These quantities have different reference structures. A smaller model-aggregate MAE than human-human MAE is therefore not proof that the model is better than human raters; the results provide context for label uncertainty only.",
        "",
        "## Analysis definitions and cautions",
        "",
        f"- Length bands use eligible model-train word-count quartiles with left-closed intervals and edges `{json.dumps(length_edges)}`.",
        "- Human-score and prompt results are descriptive. Overprediction and underprediction use RF prediction minus human aggregate score and make no causal claim.",
        f"- {len(small_groups)} fairness rows have N < 20 and are explicitly flagged; estimates for these groups are unstable.",
        "- Prompt-level results include many small groups and should not be ranked as if their estimates had equal precision.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "official_test_loaded": False,
                "validation_rows": len(frame),
                "high_disagreement_threshold": disagreement_threshold,
                "shared_blind_spot": blind_spot.to_dict(orient="records"),
                "fairness_rows": len(fairness),
                "fairness_small_n_rows": len(small_groups),
                "sensitivity_rows": len(sensitivity),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
