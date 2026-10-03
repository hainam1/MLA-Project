"""Freeze baseline v1, audit human reliability, and sample controlled Phase 7 errors.

The script retains raw individual ratings only for privacy-eligible official-train development IDs.
Official-test IDs are forbidden and are never retained, joined, or evaluated.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from mla_project.evaluation.rater_reliability import (
    load_allowlisted_rater_scores,
    model_and_rater_comparison,
    rater_reliability_metrics,
)
from mla_project.features.build_features import FEATURE_NAMES
from mla_project.pipelines.training_pipeline import prepare_training_data

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
SPLIT_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
RAW_RATER_PATH = (
    ROOT
    / "data"
    / "01_original_source"
    / "rater_scores"
    / "ellipsis_raw_rater_scores_anon_all_essay.csv"
)
PHASE6_DIR = ROOT / "outputs" / "phase6"
PHASE7_PREDICTIONS_PATH = (
    ROOT / "outputs" / "predictions" / "phase7_validation_regression_predictions.csv"
)
PHASE7_SUMMARY_PATH = ROOT / "docs" / "data" / "phase7_tables" / "phase7_audit_summary.json"
CONFIG_PATH = ROOT / "configs" / "improvement_study.yaml"
TABLE_DIR = ROOT / "docs" / "data" / "improvement_tables"
PRIVATE_AUDIT_DIR = ROOT / "data" / "04_intermediate_work" / "improvement_audit"
REPORT_PATH = ROOT / "docs" / "model_improvement_audit.md"

TARGETS = ("Vocabulary", "Grammar")
PREDICTION_COLUMNS = {
    "Vocabulary": "random_forest_vocabulary",
    "Grammar": "random_forest_grammar",
}
MIN_GROUP_SIZE = 20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    def render(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, (float, np.floating)):
            return f"{float(value):.6f}"
        return str(value)

    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for _, row in frame.loc[:, columns].iterrows():
        lines.append("| " + " | ".join(render(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def assign_groups(frame: pd.DataFrame, train: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    edges = np.concatenate(
        (
            [-np.inf],
            np.unique(train["word_count"].quantile([0.25, 0.5, 0.75]).to_numpy(dtype=float)),
            [np.inf],
        )
    )
    labels = [f"Q{index}" for index in range(1, len(edges))]
    result["length_band"] = pd.cut(
        result["word_count"], edges, labels=labels, include_lowest=True, right=False
    ).astype("string")
    for target in TARGETS:
        result[f"{target.lower()}_score_band"] = pd.cut(
            result[target],
            [-np.inf, 2.5, 3.5, np.inf],
            labels=["low_1_to_2.5", "middle_3_to_3.5", "high_4_to_5"],
            include_lowest=True,
            right=True,
        ).astype("string")
    return result


def subgroup_reliability_table(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for target in TARGETS:
        for group_type, group_column in (
            ("split", "split"),
            ("score_band", f"{target.lower()}_score_band"),
            ("length_band", "length_band"),
            ("prompt", "prompt_id"),
        ):
            for group_name, group in frame.groupby(group_column, observed=True, sort=True):
                if len(group) < MIN_GROUP_SIZE:
                    continue
                rows.append(
                    {
                        "trait": target,
                        "group_type": group_type,
                        "group": str(group_name),
                        **rater_reliability_metrics(
                            group,
                            rater_1_column=f"{target}_1",
                            rater_2_column=f"{target}_2",
                        ),
                    }
                )
    return pd.DataFrame(rows)


def error_reliability_relationship(validation: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summaries: list[dict[str, object]] = []
    rows: list[pd.DataFrame] = []
    for target in TARGETS:
        prediction_column = PREDICTION_COLUMNS[target]
        subset = validation[
            [
                "essay_id",
                target,
                f"{target}_1",
                f"{target}_2",
                prediction_column,
            ]
        ].copy()
        subset["trait"] = target
        subset["human_disagreement"] = np.abs(subset[f"{target}_1"] - subset[f"{target}_2"])
        subset["model_absolute_error"] = np.abs(subset[prediction_column] - subset[target])
        correlation = spearmanr(
            subset["human_disagreement"], subset["model_absolute_error"]
        ).statistic
        high_model_error = subset["model_absolute_error"].ge(
            subset["model_absolute_error"].quantile(0.90)
        )
        summaries.append(
            {
                "trait": target,
                "n_samples": len(subset),
                "spearman_human_disagreement_vs_model_absolute_error": float(correlation),
                "mean_model_error_when_raters_agree": float(
                    subset.loc[subset["human_disagreement"].eq(0), "model_absolute_error"].mean()
                ),
                "mean_model_error_when_raters_disagree": float(
                    subset.loc[subset["human_disagreement"].gt(0), "model_absolute_error"].mean()
                ),
                "top_10pct_model_error_with_rater_disagreement_rate": float(
                    subset.loc[high_model_error, "human_disagreement"].gt(0).mean()
                ),
            }
        )
        rows.append(subset)
    return pd.DataFrame(summaries), pd.concat(rows, ignore_index=True)


def controlled_error_sample(validation: pd.DataFrame) -> pd.DataFrame:
    chosen_ids: set[str] = set()
    samples: list[pd.DataFrame] = []
    specifications = (
        ("low_score_overprediction", lambda frame, target: frame[target].le(2.5), False),
        ("high_score_underprediction", lambda frame, target: frame[target].ge(4.0), False),
        ("good_prediction", lambda frame, target: pd.Series(True, index=frame.index), True),
    )
    for category, eligible_mask, ascending in specifications:
        for target in TARGETS:
            prediction_column = PREDICTION_COLUMNS[target]
            candidates = validation.loc[eligible_mask(validation, target)].copy()
            candidates["residual"] = candidates[prediction_column] - candidates[target]
            candidates["absolute_error"] = candidates["residual"].abs()
            if category == "low_score_overprediction":
                candidates = candidates.loc[candidates["residual"].gt(0)]
                sort_column = "residual"
            elif category == "high_score_underprediction":
                candidates = candidates.loc[candidates["residual"].lt(0)]
                sort_column = "residual"
                ascending = True
            else:
                sort_column = "absolute_error"
            candidates = candidates.loc[~candidates["essay_id"].isin(chosen_ids)].sort_values(
                [sort_column, "essay_id"], ascending=[ascending, True], kind="stable"
            )
            selected = candidates.head(5).copy()
            if len(selected) != 5:
                raise ValueError(f"Could not sample five unique rows for {category}/{target}.")
            chosen_ids.update(selected["essay_id"].astype(str))
            selected.insert(1, "audit_category", category)
            selected.insert(2, "trait", target)
            selected["human_score"] = selected[target]
            selected["machine_score"] = selected[prediction_column]
            samples.append(selected)
    result = pd.concat(samples, ignore_index=True)
    result["feature_extraction_status"] = "pending_manual_review"
    result["language_tool_false_positive"] = "pending_manual_review"
    result["language_tool_false_negative"] = "pending_manual_review"
    result["missing_rubric_signal"] = "pending_manual_review"
    result["formatting_or_prompt_issue"] = "pending_manual_review"
    result["reviewer_notes"] = ""
    columns = [
        "essay_id",
        "audit_category",
        "trait",
        "human_score",
        "machine_score",
        "residual",
        "absolute_error",
        "Vocabulary_1",
        "Vocabulary_2",
        "Grammar_1",
        "Grammar_2",
        "prompt_id",
        "length_band",
        *FEATURE_NAMES,
        "feature_extraction_status",
        "language_tool_false_positive",
        "language_tool_false_negative",
        "missing_rubric_signal",
        "formatting_or_prompt_issue",
        "reviewer_notes",
    ]
    return result.loc[:, columns]


def main() -> None:
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    manifest = pd.read_csv(SPLIT_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, manifest)
    eligible = pd.concat((prepared.train, prepared.validation), ignore_index=True)
    allowed_ids = set(eligible["essay_id"].astype(str))
    official_test_ids = set(
        manifest.loc[manifest["split"].eq("official_test"), "essay_id"].astype(str)
    )
    if allowed_ids.intersection(official_test_ids):
        raise ValueError("Eligible development IDs overlap official-test IDs.")

    rater_scores = load_allowlisted_rater_scores(
        RAW_RATER_PATH,
        allowed_ids,
        forbidden_ids=official_test_ids,
    )
    if set(rater_scores["essay_id"]) != allowed_ids:
        missing = sorted(allowed_ids.difference(rater_scores["essay_id"]))
        raise ValueError(f"Eligible development IDs missing raw-rater linkage: {missing[:5]}")

    metadata = manifest.loc[manifest["essay_id"].isin(allowed_ids), ["essay_id", "prompt_id"]]
    eligible_raters = eligible.merge(rater_scores, on="essay_id", validate="one_to_one").merge(
        metadata, on="essay_id", validate="one_to_one"
    )
    eligible_raters = assign_groups(eligible_raters, prepared.train)

    predictions = pd.read_csv(PHASE7_PREDICTIONS_PATH, dtype={"essay_id": "string"})
    expected_prediction_columns = {
        "essay_id",
        "Vocabulary",
        "Grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    }
    if not expected_prediction_columns.issubset(predictions.columns):
        raise ValueError("Phase 7 predictions are missing selected-model columns.")
    validation = eligible_raters.loc[eligible_raters["split"].eq("validation")].merge(
        predictions.loc[:, sorted(expected_prediction_columns)],
        on="essay_id",
        how="inner",
        validate="one_to_one",
        suffixes=("", "_phase7"),
    )
    if len(validation) != 762 or set(validation["essay_id"]) != set(
        prepared.validation["essay_id"]
    ):
        raise ValueError("Rater audit does not match the frozen 762-row validation population.")
    for target in TARGETS:
        if not np.allclose(
            validation[target], validation[f"{target}_phase7"], rtol=0.0, atol=1e-12
        ):
            raise ValueError(f"Phase 7 {target} labels do not match development labels.")

    comparison = pd.DataFrame(
        [
            model_and_rater_comparison(
                validation,
                target=target,
                prediction_column=PREDICTION_COLUMNS[target],
            )
            for target in TARGETS
        ]
    )
    subgroups = subgroup_reliability_table(eligible_raters)
    relationship, error_rows = error_reliability_relationship(validation)
    audit_sample = controlled_error_sample(validation)
    rare_cases = validation.loc[
        validation["Vocabulary"].le(1.5)
        | validation["Vocabulary"].ge(4.5)
        | validation["Grammar"].le(1.5)
        | validation["Grammar"].ge(4.5)
    ].copy()

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(
        TABLE_DIR / "human_machine_reliability.csv", index=False, float_format="%.12g"
    )
    subgroups.to_csv(
        TABLE_DIR / "rater_reliability_by_group.csv", index=False, float_format="%.12g"
    )
    relationship.to_csv(
        TABLE_DIR / "model_error_vs_rater_disagreement.csv", index=False, float_format="%.12g"
    )
    error_rows.to_csv(
        TABLE_DIR / "validation_model_and_rater_errors.csv", index=False, float_format="%.12g"
    )
    audit_sample.to_csv(
        TABLE_DIR / "controlled_error_audit_sample.csv", index=False, float_format="%.12g"
    )
    rare_cases.loc[
        :,
        [
            "essay_id",
            "Vocabulary",
            "Grammar",
            "Vocabulary_1",
            "Vocabulary_2",
            "Grammar_1",
            "Grammar_2",
            "random_forest_vocabulary",
            "random_forest_grammar",
            "prompt_id",
            "word_count",
        ],
    ].to_csv(TABLE_DIR / "rare_extreme_case_studies.csv", index=False, float_format="%.12g")

    raw_train = pd.read_csv(
        ROOT
        / "data"
        / "01_original_source"
        / "official_corpus"
        / "ELLIPSE_Final_github_train.csv",
        usecols=["text_id_kaggle", "full_text"],
        dtype={"text_id_kaggle": "string"},
    ).rename(columns={"text_id_kaggle": "essay_id"})
    private_sample = audit_sample.merge(raw_train, on="essay_id", how="left", validate="one_to_one")
    if private_sample["full_text"].isna().any():
        raise ValueError("Controlled audit sample is missing essay text.")
    private_sample.to_csv(PRIVATE_AUDIT_DIR / "controlled_error_audit_private.csv", index=False)

    baseline_freeze = {
        "baseline_version": "v1",
        "official_test_loaded": False,
        "validation_reuse_for_model_development_forbidden": True,
        "validation_rows": len(validation),
        "eligible_model_train_rows": len(prepared.train),
        "selected_models": {
            "Vocabulary": {"model": "Random Forest", "mae": 0.3729771083796588},
            "Grammar": {"model": "Random Forest", "mae": 0.44771032053951443},
        },
        "input_sha256": {
            "improvement_config": sha256(CONFIG_PATH),
            "phase6_manifest": sha256(PHASE6_DIR / "artifact_manifest.json"),
            "phase7_summary": sha256(PHASE7_SUMMARY_PATH),
            "phase7_predictions": sha256(PHASE7_PREDICTIONS_PATH),
            "split_manifest": sha256(SPLIT_PATH),
        },
        "raw_rater_guard": {
            "allowlisted_eligible_development_ids": len(allowed_ids),
            "retained_rater_rows": len(rater_scores),
            "forbidden_official_test_ids": len(official_test_ids),
            "retained_official_test_ids": 0,
            "official_test_scores_evaluated": False,
        },
    }
    (TABLE_DIR / "baseline_v1_freeze.json").write_text(
        json.dumps(baseline_freeze, indent=2), encoding="utf-8"
    )

    report = [
        "# Model Improvement Audit — Human Reliability and Controlled Errors",
        "",
        "> Baseline v1 is frozen. This audit does not fit a model, tune on validation, or evaluate official test.",
        "",
        "## Human–human and model–human comparison",
        "",
        markdown_table(
            comparison,
            [
                "trait",
                "n_samples",
                "human_human_mae",
                "exact_agreement_rate",
                "within_0_5_points_rate",
                "quadratic_weighted_kappa",
                "icc_a_1",
                "model_aggregate_human_mae",
                "model_individual_human_mae",
            ],
        ),
        "",
        "`model_aggregate_human_mae` is the frozen RF error against the released aggregate target. "
        "`model_individual_human_mae` averages RF error against each raw rater separately and is the "
        "more direct comparison with human–human disagreement.",
        "",
        "## Model error versus rater disagreement",
        "",
        markdown_table(
            relationship,
            [
                "trait",
                "n_samples",
                "spearman_human_disagreement_vs_model_absolute_error",
                "mean_model_error_when_raters_agree",
                "mean_model_error_when_raters_disagree",
                "top_10pct_model_error_with_rater_disagreement_rate",
            ],
        ),
        "",
        "## Controlled manual-audit sample",
        "",
        "The text-free audit table contains 30 rows: five Vocabulary and five Grammar rows in each "
        "of low-score overprediction, high-score underprediction, and good-prediction categories. "
        "The private, git-ignored copy adds essay text for manual inspection. Rare extreme scores are "
        "stored separately as case studies and are not treated as stable subgroups.",
        "",
        "- `docs/data/improvement_tables/controlled_error_audit_sample.csv`",
        "- `data/04_intermediate_work/improvement_audit/controlled_error_audit_private.csv`",
        "- `docs/data/improvement_tables/rare_extreme_case_studies.csv`",
        "",
        "## Isolation guarantees",
        "",
        f"The raw-rater loader retained exactly {len(rater_scores)} allowlisted, privacy-eligible "
        f"development rows. It retained 0 of {len(official_test_ids)} forbidden official-test IDs. "
        "Raw scores are audit-only and are not model inputs.",
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(baseline_freeze, indent=2))


if __name__ == "__main__":
    main()
