"""Re-extract the controlled 30-essay sample and summarize LanguageTool coverage.

Essay text is read only from the git-ignored private audit file. Public outputs contain IDs,
features, and aggregate rule counts but never student text or matched substrings.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from mla_project.features.build_features import FEATURE_NAMES, load_default_extractor
from mla_project.features.preprocessing import clean_text

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PATH = (
    ROOT
    / "data"
    / "04_intermediate_work"
    / "improvement_audit"
    / "controlled_error_audit_private.csv"
)
PUBLIC_SAMPLE_PATH = (
    ROOT / "docs" / "data" / "improvement_tables" / "controlled_error_audit_sample.csv"
)
TABLE_DIR = ROOT / "docs" / "data" / "improvement_tables"


def main() -> None:
    private = pd.read_csv(PRIVATE_PATH, dtype={"essay_id": "string"})
    public = pd.read_csv(PUBLIC_SAMPLE_PATH, dtype={"essay_id": "string"})
    if len(private) != 30 or set(private["essay_id"]) != set(public["essay_id"]):
        raise ValueError("Feature audit requires the frozen 30-row controlled sample.")

    extractor = load_default_extractor(language_tool_version="6.6")
    audit_rows: list[dict[str, object]] = []
    issue_counts: Counter[str] = Counter()
    rule_counts: Counter[tuple[str, str, str]] = Counter()
    try:
        for row in private.to_dict(orient="records"):
            cleaned = clean_text(str(row["full_text"]))
            doc = extractor.nlp(cleaned)
            matches = extractor.grammar_checker.check(cleaned)
            extracted = extractor.transform_prepared(cleaned, doc, grammar_matches=matches)
            differences = {
                feature: abs(float(extracted[feature]) - float(row[feature]))
                for feature in FEATURE_NAMES
            }
            mismatches = [
                feature for feature, difference in differences.items() if difference > 1e-8
            ]
            essay_issue_counts = Counter(
                str(getattr(match, "ruleIssueType", "unknown") or "unknown").casefold()
                for match in matches
            )
            issue_counts.update(essay_issue_counts)
            for match in matches:
                issue_type = str(getattr(match, "ruleIssueType", "unknown") or "unknown").casefold()
                category = str(getattr(match, "category", "unknown") or "unknown")
                rule_id = str(getattr(match, "ruleId", "unknown") or "unknown")
                rule_counts[(issue_type, category, rule_id)] += 1
            grammar_count = essay_issue_counts.get("grammar", 0)
            ignored_count = len(matches) - grammar_count
            audit_rows.append(
                {
                    "essay_id": row["essay_id"],
                    "audit_category": row["audit_category"],
                    "trait": row["trait"],
                    "human_score": row["human_score"],
                    "machine_score": row["machine_score"],
                    "stored_word_count": row["word_count"],
                    "reextracted_word_count": extracted["word_count"],
                    "feature_mismatch_count": len(mismatches),
                    "maximum_absolute_feature_difference": max(differences.values()),
                    "mismatched_features": ";".join(mismatches),
                    "language_tool_total_matches": len(matches),
                    "language_tool_grammar_matches_used": grammar_count,
                    "language_tool_non_grammar_matches_ignored": ignored_count,
                    "language_tool_issue_counts_json": json.dumps(
                        dict(sorted(essay_issue_counts.items())), sort_keys=True
                    ),
                    "contains_non_ascii": any(ord(character) > 127 for character in cleaned),
                    "cleaned_character_count": len(cleaned),
                    "manual_false_positive_review": "pending_manual_review",
                    "manual_false_negative_review": "pending_manual_review",
                }
            )
    finally:
        extractor.grammar_checker.close()

    audit = pd.DataFrame(audit_rows)
    issue_summary = pd.DataFrame(
        [
            {"issue_type": issue_type, "detected_matches": count}
            for issue_type, count in issue_counts.most_common()
        ]
    )
    rule_summary = pd.DataFrame(
        [
            {
                "issue_type": issue_type,
                "category": category,
                "rule_id": rule_id,
                "detected_matches": count,
            }
            for (issue_type, category, rule_id), count in rule_counts.most_common()
        ]
    )
    audit.to_csv(TABLE_DIR / "feature_reextraction_audit.csv", index=False, float_format="%.12g")
    issue_summary.to_csv(TABLE_DIR / "language_tool_issue_summary.csv", index=False)
    rule_summary.to_csv(TABLE_DIR / "language_tool_rule_summary.csv", index=False)

    if audit["feature_mismatch_count"].eq(0).all():
        public["feature_extraction_status"] = "reextraction_exact_within_1e-8"
    else:
        status = audit.set_index(["essay_id", "trait"])["feature_mismatch_count"]
        public["feature_extraction_status"] = [
            (
                "reextraction_exact_within_1e-8"
                if status.loc[(essay_id, trait)] == 0
                else "reextraction_mismatch_requires_review"
            )
            for essay_id, trait in zip(public["essay_id"], public["trait"], strict=True)
        ]
    ignored = audit.set_index(["essay_id", "trait"])["language_tool_non_grammar_matches_ignored"]
    public["missing_rubric_signal"] = [
        f"LanguageTool non-grammar detections excluded: {int(ignored.loc[(essay_id, trait)])}"
        for essay_id, trait in zip(public["essay_id"], public["trait"], strict=True)
    ]
    public.to_csv(PUBLIC_SAMPLE_PATH, index=False, float_format="%.12g")

    summary = {
        "audited_rows": len(audit),
        "feature_schema": list(FEATURE_NAMES),
        "rows_with_feature_mismatch": int(audit["feature_mismatch_count"].gt(0).sum()),
        "maximum_absolute_feature_difference": float(
            audit["maximum_absolute_feature_difference"].max()
        ),
        "language_tool_total_matches": int(audit["language_tool_total_matches"].sum()),
        "language_tool_grammar_matches_used": int(
            audit["language_tool_grammar_matches_used"].sum()
        ),
        "language_tool_non_grammar_matches_ignored": int(
            audit["language_tool_non_grammar_matches_ignored"].sum()
        ),
        "manual_false_positive_false_negative_review_complete": False,
        "official_test_loaded": False,
    }
    (TABLE_DIR / "feature_audit_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
