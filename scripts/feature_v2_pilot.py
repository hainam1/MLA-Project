"""Technical pilot of the frozen v2 schema on the existing 30-essay audit.

The pilot checks finite outputs and category patterns; it does not use validation
labels to select features or assert that tool detections are true rubric errors.
Student text and matched substrings are never exported.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from mla_project.features.build_features import load_default_extractor
from mla_project.features.feature_v2 import V2_FEATURE_NAMES, extract_v2_features
from mla_project.features.preprocessing import clean_text

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data" / "04_intermediate_work" / "improvement_audit" / "controlled_error_audit_private.csv"
PRIVATE_REVIEW = (
    ROOT / "data" / "04_intermediate_work" / "improvement_audit" / "feature_v2_rubric_review_private.csv"
)
OUTPUT_DIR = ROOT / "docs" / "data" / "improvement_tables"


def main() -> None:
    sample = pd.read_csv(PRIVATE, dtype={"essay_id": "string"})
    if len(sample) != 30 or sample["essay_id"].duplicated().any():
        raise ValueError("Expected the frozen 30-essay controlled audit sample.")
    extractor = load_default_extractor(language_tool_version="6.6")
    rows = []
    try:
        for row in sample.to_dict("records"):
            cleaned = clean_text(str(row["full_text"]))
            doc = extractor.nlp(cleaned)
            matches = extractor.grammar_checker.check(cleaned)
            features = extract_v2_features(doc, matches)
            rows.append(
                {
                    "essay_id": row["essay_id"],
                    "audit_category": row["audit_category"],
                    "trait": row["trait"],
                    **features,
                }
            )
    finally:
        extractor.grammar_checker.close()
    pilot = pd.DataFrame(rows)
    if not np.isfinite(pilot[list(V2_FEATURE_NAMES)].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite v2 pilot feature.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pilot.to_csv(OUTPUT_DIR / "feature_v2_pilot_30.csv", index=False, float_format="%.12g")
    group = pilot.groupby(["trait", "audit_category"], dropna=False)[list(V2_FEATURE_NAMES)]
    group.mean().reset_index().to_csv(
        OUTPUT_DIR / "feature_v2_pilot_group_means.csv", index=False, float_format="%.12g"
    )
    review = sample[
        [
            "essay_id",
            "audit_category",
            "trait",
            "human_score",
            "machine_score",
            "full_text",
        ]
    ].merge(pilot.drop(columns=["audit_category", "trait"]), on="essay_id", validate="one_to_one")
    for column in (
        "word_choice_or_precision_evidence",
        "word_form_evidence",
        "grammar_accuracy_evidence",
        "language_tool_false_positive_examples",
        "language_tool_missed_error_examples",
        "reviewer_notes",
    ):
        review[column] = ""
    review["review_status"] = "pending_rubric_review"
    PRIVATE_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    if not PRIVATE_REVIEW.exists():
        review.to_csv(PRIVATE_REVIEW, index=False, float_format="%.12g")
    summary = {
        "rows": len(pilot),
        "non_finite_values": 0,
        "student_text_exported_to_public_tables": False,
        "private_review_worksheet": str(PRIVATE_REVIEW.relative_to(ROOT)),
        "rubric_error_validation_complete": False,
        "use_for_feature_selection": False,
        "feature_names": list(V2_FEATURE_NAMES),
    }
    (OUTPUT_DIR / "feature_v2_pilot_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
