"""Post-midterm supplementary, Validation-only analyses from saved predictions.

No training, tuning, Official Test evaluation, or frozen-output writes. Prompt
length descriptions and one feature example use eligible development data only.
"""

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from mla_project.evaluation.review_metrics import review_queue_metrics
from mla_project.features.build_features import FEATURE_NAMES
from mla_project.evaluation.rater_reliability import (
    load_allowlisted_rater_scores,
    rater_reliability_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/data/post_midterm"


def validation_signals(frame):
    """Require an eligible Validation population and add fixed-reference signals."""
    if frame.empty or set(frame["split"]) != {"validation"}:
        raise ValueError("Supplementary triage/error analysis requires Validation only.")
    if not frame["privacy_review_status"].eq("not_flagged").all():
        raise ValueError("Only privacy-eligible rows are allowed.")
    if frame["essay_id"].isna().any() or frame["essay_id"].duplicated().any():
        raise ValueError("Unique non-null essay IDs are required.")
    numeric = [
        "Vocabulary",
        "Grammar",
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    ]
    if not np.isfinite(frame[numeric].to_numpy(dtype=float)).all():
        raise ValueError("Labels and predictions must be finite.")
    result = frame.copy()
    result["max_rf_error"] = np.maximum(
        abs(result.Vocabulary - result.random_forest_vocabulary),
        abs(result.Grammar - result.random_forest_grammar),
    )
    result["large_error"] = result.max_rf_error.ge(1.0)
    result["dV"] = abs(result.ridge_vocabulary - result.random_forest_vocabulary)
    result["dG"] = abs(result.ridge_grammar - result.random_forest_grammar)
    result["D_max"] = result[["dV", "dG"]].max(axis=1)
    result["D_mean"] = result[["dV", "dG"]].mean(axis=1)
    return result


def top_ids(frame, column, *, budget=0.20, ascending=False):
    """Exact ceiling budget and ascending string-ID ties, without label use."""
    if not 0 < budget <= 1:
        raise ValueError("budget must be in (0, 1].")
    ranked = frame.assign(essay_id=frame.essay_id.astype(str)).sort_values(
        [column, "essay_id"], ascending=[ascending, True], kind="stable"
    )
    return set(ranked.head(math.ceil(len(frame) * budget)).essay_id)


def feature_error_comparison(frame):
    """Descriptive mean/median and pooled-SD differences, without significance tests."""
    rows = []
    large, other = frame[frame.large_error], frame[~frame.large_error]
    for name in FEATURE_NAMES:
        a, b = large[name], other[name]
        pooled = math.sqrt(
            ((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2)
        )
        rows.append(
            dict(
                feature=name,
                large_n=len(a),
                non_large_n=len(b),
                large_mean=a.mean(),
                non_large_mean=b.mean(),
                large_median=a.median(),
                non_large_median=b.median(),
                mean_difference=a.mean() - b.mean(),
                standardized_mean_difference=(
                    (a.mean() - b.mean()) / pooled if pooled > 0 else np.nan
                ),
            )
        )
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "manifest": "data/02_split_manifest/essay_split_manifest.csv",
        "features": "data/05_model_features/development_features_with_targets.csv",
        "predictions": "outputs/phase6/validation_predictions.csv",
        "clean": "data/03_clean_ready_to_use/full_clean_corpus_6482.csv",
        "rater": "data/01_original_source/rater_scores/ellipsis_raw_rater_scores_anon_all_essay.csv",
        "rater_summary": "docs/data/improvement_tables/human_machine_reliability.csv",
        "ridge_metrics": "docs/data/phase7_tables/regression_metrics.csv",
        "parameters": "outputs/phase6/selected_parameters.json",
    }
    read = lambda key: pd.read_csv(ROOT / paths[key])
    manifest = read("manifest")
    eligible = manifest[
        manifest.split.isin(["model_train", "validation"])
        & manifest.privacy_review_status.eq("not_flagged")
    ]
    features = read("features")
    development = features.merge(
        eligible[["essay_id", "prompt_id", "privacy_review_status"]],
        on="essay_id",
        validate="one_to_one",
    )
    assert len(development) == 3812 and not development.split.eq("official_test").any()
    validation = development[development.split.eq("validation")].merge(
        read("predictions"), on="essay_id", validate="one_to_one"
    )
    frame = validation_signals(validation)
    assert len(frame) == 762 and int(frame.large_error.sum()) == 69
    max_ids, mean_ids = top_ids(frame, "D_max"), top_ids(frame, "D_mean")
    strategies = []
    for name, ids in [("D_max", max_ids), ("D_mean", mean_ids)]:
        metrics = review_queue_metrics(
            frame.large_error.to_numpy(), frame.essay_id.isin(ids).to_numpy()
        )
        strategies.append(
            {
                "strategy": name,
                "analysis": "Post-midterm validation sensitivity analysis requested by instructor",
                **metrics,
            }
        )
    pd.DataFrame(strategies).to_csv(OUT / "max_vs_mean_validation.csv", index=False)
    overlap = {
        "selected_each": len(max_ids),
        "intersection": len(max_ids & mean_ids),
        "overlap_fraction": len(max_ids & mean_ids) / len(max_ids),
        "jaccard": len(max_ids & mean_ids) / len(max_ids | mean_ids),
    }
    errors = feature_error_comparison(frame)
    errors.to_csv(OUT / "feature_error_comparison_validation.csv", index=False)
    threshold = 0.133989655155  # frozen Validation-median analysis threshold
    samples, already = [], set()
    for group, mask, count, columns in [
        ("highest_rf_error", frame.large_error, 12, ["max_rf_error", "essay_id"]),
        ("shared_blind_spot", frame.large_error & frame.D_max.lt(threshold), 10, ["essay_id"]),
        ("low_rf_error_comparison", frame.max_rf_error.lt(0.5), 10, ["max_rf_error", "essay_id"]),
    ]:
        ascending = [False, True] if group == "highest_rf_error" else True
        sample = (
            frame[mask & ~frame.essay_id.isin(already)]
            .sort_values(columns, ascending=ascending)
            .head(count)
            .copy()
        )
        assert len(sample) == count
        sample["sample_group"] = group
        already.update(sample.essay_id)
        samples.append(sample)
    manual = pd.concat(samples)
    for col in [
        "reviewer",
        "off_topic_task_response",
        "unusual_vocabulary",
        "grammar_checker_mismatch",
        "coherence_content",
        "length_observation",
        "unusual_syntax",
        "rater_ambiguity",
        "manual_notes",
    ]:
        manual[col] = ""
    manual_cols = [
        "sample_group",
        "essay_id",
        "prompt_id",
        "Vocabulary",
        "Grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
        "max_rf_error",
        "D_max",
        "word_count",
        "detected_grammar_errors_per_100_words",
        "reviewer",
        "off_topic_task_response",
        "unusual_vocabulary",
        "grammar_checker_mismatch",
        "coherence_content",
        "length_observation",
        "unusual_syntax",
        "rater_ambiguity",
        "manual_notes",
    ]
    manual_dir = ROOT / "docs/data/error_analysis"
    manual_dir.mkdir(parents=True, exist_ok=True)
    manual[manual_cols].to_csv(manual_dir / "manual_error_review.csv", index=False)
    lengths = development.groupby("prompt_id").word_count.agg(
        n="size",
        mean="mean",
        median="median",
        sd="std",
        q1=lambda x: x.quantile(0.25),
        q3=lambda x: x.quantile(0.75),
    )
    lengths["iqr"] = lengths.q3 - lengths.q1
    lengths.to_csv(OUT / "length_by_operational_prompt_development.csv")
    grand = development.word_count.mean()
    between = float((lengths.n * (lengths["mean"] - grand) ** 2).sum())
    total = float(((development.word_count - grand) ** 2).sum())
    train = development[development.split.eq("model_train")]
    example = (
        train.assign(distance=(train.word_count - train.word_count.median()).abs())
        .sort_values(["distance", "essay_id"])
        .iloc[0]
    )
    pd.DataFrame(
        {"feature": FEATURE_NAMES, "actual_value": [example[name] for name in FEATURE_NAMES]}
    ).to_csv(OUT / "real_feature_example.csv", index=False)
    clean = pd.read_csv(
        ROOT / paths["clean"], usecols=["essay_id", "gender", "grade", "race_ethnicity", "ses"]
    )
    demographics = clean[clean.essay_id.isin(frame.essay_id)][
        ["essay_id", "gender", "grade", "race_ethnicity", "ses"]
    ]
    audit = frame.merge(demographics, on="essay_id", validate="one_to_one")
    shortest_ids = top_ids(frame, "word_count", ascending=True)
    subgroup = []
    for attribute in ["gender", "grade", "race_ethnicity", "ses"]:
        for group, sub in audit.groupby(attribute, dropna=False):
            n = len(sub)
            large_count = int(sub.large_error.sum())
            selected = sub.essay_id.isin(max_ids)
            subgroup.append(
                dict(
                    attribute=attribute,
                    group=str(group),
                    n=n,
                    vocabulary_mae=abs(sub.Vocabulary - sub.random_forest_vocabulary).mean(),
                    grammar_mae=abs(sub.Grammar - sub.random_forest_grammar).mean(),
                    large_error_count=large_count,
                    large_error_rate=large_count / n,
                    selected_count=int(selected.sum()),
                    selection_rate=selected.mean(),
                    capture_rate=(
                        int((selected & sub.large_error).sum()) / large_count
                        if large_count
                        else np.nan
                    ),
                    shortest_selection_rate=sub.essay_id.isin(shortest_ids).mean(),
                    random_expected_selection_rate=len(max_ids) / len(frame),
                    small_n=n < 20,
                )
            )
    pd.DataFrame(subgroup).to_csv(OUT / "subgroup_audit_validation.csv", index=False)
    raters = load_allowlisted_rater_scores(
        ROOT / paths["rater"],
        frame.essay_id,
        forbidden_ids=manifest.loc[manifest.split.eq("official_test"), "essay_id"],
    )
    rater_rows = []
    for target in ["Vocabulary", "Grammar"]:
        values = rater_reliability_metrics(
            raters, rater_1_column=target + "_1", rater_2_column=target + "_2"
        )
        diff = abs(raters[target + "_1"] - raters[target + "_2"])
        rater_rows.append(
            {
                "target": target,
                **values,
                "exactly_one_count": int(diff.eq(1).sum()),
                "at_least_one_count": int(diff.ge(1).sum()),
                "greater_than_one_count": int(diff.gt(1).sum()),
            }
        )
    pd.DataFrame(rater_rows).to_csv(OUT / "rater_threshold_context_validation.csv", index=False)
    summary = {
        "analysis": "post-midterm supplementary research",
        "validation_n": len(frame),
        "large_errors": int(frame.large_error.sum()),
        "max_mean": strategies,
        "overlap": overlap,
        "prompt_identity": "canonical mapping unresolved; operational categories only",
        "unseen_prompt_experiment": "blocked_pending_authoritative_canonical_mapping",
        "length_prompt_eta_squared_descriptive": between / total,
        "prompt_mean_length_min": lengths["mean"].min(),
        "prompt_mean_length_max": lengths["mean"].max(),
        "feature_example": {
            "essay_id": example.essay_id,
            "split": example.split,
            "privacy_review_status": example.privacy_review_status,
            "Vocabulary": example.Vocabulary,
            "Grammar": example.Grammar,
        },
        "manual_review_status": "32 unique Validation essays, all human fields blank; coding pending",
        "input_sha256": {
            key: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for key, path in paths.items()
        },
    }
    (OUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    before = json.loads((OUT / "frozen_integrity_before.json").read_text())
    mismatches = [
        p for p, h in before.items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h
    ]
    assert not mismatches, mismatches
    print(
        json.dumps(
            {
                "max_mean": strategies,
                "overlap": overlap,
                "example": summary["feature_example"],
                "length_eta_squared": between / total,
                "frozen_checked": len(before),
                "frozen_mismatches": mismatches,
            },
            indent=2,
        )
    )
    print(
        errors[
            ["feature", "large_mean", "non_large_mean", "standardized_mean_difference"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
