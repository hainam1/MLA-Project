"""Descriptive checks cited in the post-midterm progress report.

Reads saved Validation labels/predictions only; does not train or touch Official Test.
Writes docs/data/post_midterm/progress_report_checks.csv.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/data/post_midterm/progress_report_checks.csv"
SHORT_PROMPTS = [
    "Community service",
    "Cell phones at school",
    "Grades for extracurricular activities",
]
BUDGET_K = 153


def main() -> None:
    labels = pd.read_csv(ROOT / "docs/data/phase8_tables/large_error_labels.csv")
    features = pd.read_csv(ROOT / "data/05_model_features/development_features_with_targets.csv")
    manifest = pd.read_csv(ROOT / "data/02_split_manifest/essay_split_manifest.csv")
    rows = []

    # Per-target large error (|y - RF| >= 1) by reference-score band.
    for target in ["Vocabulary", "Grammar"]:
        error = labels[f"error_{target.lower()}"].ge(1.0)
        bands = pd.cut(labels[target], [0, 2.0, 4.0, 5.0], labels=["<=2.0", "2.5-4.0", ">=4.5"])
        for band in bands.cat.categories:
            mask = bands.eq(band)
            rows.append({"check": "per_target_large_error_by_band", "target": target, "group": band,
                         "count": int((mask & error).sum()), "n": int(mask.sum())})
        prediction = labels[f"random_forest_{target.lower()}"]
        rows.append({"check": "rf_prediction_min", "target": target, "group": "", "count": "", "n": round(prediction.min(), 4)})
        rows.append({"check": "rf_prediction_max", "target": target, "group": "", "count": "", "n": round(prediction.max(), 4)})

    # Prompt composition of the Shortest-first queue (K = 153, ties by essay_id).
    validation = (
        features[features.essay_id.isin(labels.essay_id)]
        .merge(manifest[["essay_id", "prompt_id"]], on="essay_id")
    )
    queue = validation.sort_values(["word_count", "essay_id"]).head(BUDGET_K)
    rows.append({"check": "three_shortest_prompts_in_validation", "target": "", "group": "",
                 "count": int(validation.prompt_id.isin(SHORT_PROMPTS).sum()), "n": len(validation)})
    rows.append({"check": "three_shortest_prompts_in_shortest_first_queue", "target": "", "group": "",
                 "count": int(queue.prompt_id.isin(SHORT_PROMPTS).sum()), "n": len(queue)})

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
