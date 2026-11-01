"""Small post-feedback analyses from saved artifacts; never fit or predict models.

Validation-only heuristics defined before execution: grammar-error-rate descending
and word-count ascending. Both use ceil(.20*N), string-ID ties, and frozen RF
large-error labels. Official-test reads are confined to descriptive overlap and
manual-sampling diagnostics, never heuristic selection or tuning.
"""

from pathlib import Path
import hashlib
import json

import pandas as pd

from mla_project.evaluation.phase8 import review_count
from mla_project.evaluation.review_metrics import review_queue_metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/data/finalization_tables"


def read(path):
    return pd.read_csv(ROOT / path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = read("data/02_split_manifest/essay_split_manifest.csv")
    clean = read("data/03_clean_ready_to_use/full_clean_corpus_6482.csv")
    assert (
        clean.set_index("essay_id")["prompt"]
        .sort_index()
        .equals(manifest.set_index("essay_id")["prompt_id"].sort_index())
    )
    for eligible, name in [(False, "prompt_crosstab_all"), (True, "prompt_crosstab_eligible")]:
        population = (
            manifest[manifest.privacy_review_status.eq("not_flagged")] if eligible else manifest
        )
        table = pd.crosstab(population.prompt_id, population.split)
        table = table.reindex(columns=["model_train", "validation", "official_test"])
        table.to_csv(OUT / f"{name}.csv")
        print(name, "categories", len(table), "missing split cells", int(table.eq(0).sum().sum()))
    raw_counts = {}
    for split in ["train", "test"]:
        raw = read(f"data/01_original_source/official_corpus/ELLIPSE_Final_github_{split}.csv")
        raw_counts[split] = {
            "prompt_unique": int(raw.prompt.nunique()),
            "task_unique": int(raw.task.nunique()),
        }
    (OUT / "prompt_evidence.json").write_text(json.dumps(raw_counts, indent=2), encoding="utf-8")
    features = read("data/05_model_features/development_features_with_targets.csv")
    validation_ids = manifest.loc[
        manifest.split.eq("validation") & manifest.privacy_review_status.eq("not_flagged"),
        "essay_id",
    ]
    validation = features[features.essay_id.isin(validation_ids)].merge(
        read("docs/data/phase8_tables/large_error_labels.csv")[["essay_id", "large_error"]],
        on="essay_id",
        validate="one_to_one",
    )
    assert len(validation) == 762 and validation.split.eq("validation").all()
    count = review_count(len(validation), 0.20)
    rows = []
    for strategy, column, ascending in [
        ("grammar_error_rate_first", "detected_grammar_errors_per_100_words", False),
        ("shortest_first", "word_count", True),
    ]:
        ranked = validation.sort_values([column, "essay_id"], ascending=[ascending, True])
        ids = set(ranked.head(count).essay_id)
        metrics = review_queue_metrics(
            validation.large_error.to_numpy(), validation.essay_id.isin(ids).to_numpy()
        )
        rows.append(
            {
                "strategy": strategy,
                "analysis": "exploratory validation-only analysis added after teacher feedback",
                **metrics,
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "teacher_heuristics_validation.csv", index=False)
    predictions = read("outputs/predictions/official_test_predictions.csv")
    errors = read("docs/data/phase9_tables/large_error_labels.csv")
    frame = predictions.merge(
        errors[["essay_id", "max_rf_absolute_error", "large_error"]],
        on="essay_id",
        validate="one_to_one",
    )
    frozen = json.loads((ROOT / "docs/data/phase9_tables/artifact_manifest.json").read_text())
    frame["disagreement"] = pd.concat(
        [
            (frame.ridge_vocabulary - frame.random_forest_vocabulary).abs(),
            (frame.ridge_grammar - frame.random_forest_grammar).abs(),
        ],
        axis=1,
    ).max(axis=1)
    centers = frozen["frozen_ridge_centers"]
    frame["extremity"] = pd.concat(
        [
            (frame.ridge_vocabulary - centers["median_ridge_vocabulary"]).abs(),
            (frame.ridge_grammar - centers["median_ridge_grammar"]).abs(),
        ],
        axis=1,
    ).max(axis=1)
    count = frozen["primary_selected_count"]
    d = set(
        frame.sort_values(["disagreement", "essay_id"], ascending=[False, True])
        .head(count)
        .essay_id
    )
    e = set(
        frame.sort_values(["extremity", "essay_id"], ascending=[False, True]).head(count).essay_id
    )
    large = set(frame.loc[frame.large_error, "essay_id"])
    overlap = {
        "top20_overlap_count": len(d & e),
        "top20_overlap_fraction": len(d & e) / count,
        "jaccard": len(d & e) / len(d | e),
        "large_errors_both": len(large & d & e),
        "large_errors_only_disagreement": len((large & d) - e),
        "large_errors_only_extremity": len((large & e) - d),
        "large_errors_neither": len(large - (d | e)),
        "spearman_disagreement_extremity": frame.disagreement.corr(
            frame.extremity, method="spearman"
        ),
    }
    pd.DataFrame(list(overlap.items()), columns=["comparison", "value"]).to_csv(
        OUT / "disagreement_extremity.csv", index=False
    )
    threshold = frozen["frozen_disagreement_threshold"]
    frame = frame.merge(
        read("data/05_model_features/official_test_features.csv")[
            ["essay_id", "word_count", "detected_grammar_errors_per_100_words"]
        ],
        on="essay_id",
        validate="one_to_one",
    )
    samples = []
    for group, mask, n in [
        ("shared_blind_spot", frame.large_error & frame.disagreement.lt(threshold), 12),
        ("high_disagreement_large_error", frame.large_error & frame.disagreement.ge(threshold), 10),
        (
            "low_disagreement_no_large_error",
            ~frame.large_error & frame.disagreement.lt(threshold),
            5,
        ),
    ]:
        sample = frame[mask].sort_values("essay_id").head(n).copy()
        sample["sample_group"] = group
        sample["manual_notes"] = ""
        samples.append(sample)
    pd.concat(samples)[
        [
            "sample_group",
            "essay_id",
            "max_rf_absolute_error",
            "disagreement",
            "word_count",
            "detected_grammar_errors_per_100_words",
            "manual_notes",
        ]
    ].to_csv(OUT / "manual_analysis_sample.csv", index=False)
    draws = read("docs/data/phase9_tables/random_reference_distribution.csv")
    primary = draws[draws.error_threshold.eq(1) & draws.review_budget.eq(0.2)]
    p = float(primary.captured_count.ge(len(large & d)).mean())
    summary = {
        "empirical_one_sided_p": p,
        "draws": len(primary),
        "tail_draws": int(primary.captured_count.ge(47).sum()),
        "shared_blind_spots": int((frame.large_error & frame.disagreement.lt(threshold)).sum()),
        **overlap,
    }
    (OUT / "supplement_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))
    print(json.dumps(summary, indent=2))
    # Assert existing official manifest outputs still match their original hashes.
    for path, expected in frozen["output_sha256"].items():
        assert (
            hashlib.sha256((ROOT / path).read_bytes()).hexdigest().upper() == expected.upper()
        ), path
    print("Frozen Phase 9 manifest outputs: unchanged")


if __name__ == "__main__":
    main()
