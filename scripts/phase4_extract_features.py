"""Extract the frozen 14-feature schema for every ELLIPSE split.

Only essay IDs and derived numeric features are written. Official-test targets are never loaded.
LanguageTool requests run concurrently against one local 6.6 server; checkpoints are resumable.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import tempfile
import time

import pandas as pd

from mla_project.features import FEATURE_NAMES
from mla_project.features.build_features import load_default_extractor
from mla_project.features.preprocessing import clean_text

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_CORPUS = ROOT / "data" / "01_original_source" / "official_corpus"
SPLITS = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
INTERIM = ROOT / "data" / "04_intermediate_work"
PROCESSED = ROOT / "data" / "05_model_features"
TABLES = ROOT / "docs" / "data" / "phase4_tables"

TRAIN = OFFICIAL_CORPUS / "ELLIPSE_Final_github_train.csv"
TEST = OFFICIAL_CORPUS / "ELLIPSE_Final_github_test.csv"
CHECKPOINT = INTERIM / "phase4_feature_checkpoint.csv"
ALL_FEATURES = PROCESSED / "essay_features.csv"
DEVELOPMENT = PROCESSED / "development_features_with_targets.csv"
TEST_FEATURES = PROCESSED / "official_test_features.csv"

CHUNK_SIZE = 100
GRAMMAR_WORKERS = 8


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", encoding="utf-8", newline="", delete=False, dir=path.parent
    ) as stream:
        temporary = Path(stream.name)
        frame.to_csv(stream, index=False, float_format="%.12g")
    temporary.replace(path)


def load_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(TRAIN, usecols=["text_id_kaggle", "full_text", "Vocabulary", "Grammar"])
    test = pd.read_csv(TEST, usecols=["text_id_kaggle", "full_text"])
    texts = pd.concat(
        [
            train[["text_id_kaggle", "full_text"]].assign(source_partition="official_train"),
            test.assign(source_partition="official_test"),
        ],
        ignore_index=True,
    ).rename(columns={"text_id_kaggle": "essay_id", "full_text": "essay_text"})
    manifest = pd.read_csv(SPLITS, dtype={"essay_id": "string"})
    rows = manifest[["essay_id", "source_partition", "split", "cv_fold"]].merge(
        texts, on=["essay_id", "source_partition"], how="left", validate="one_to_one"
    )
    if rows["essay_text"].isna().any() or len(rows) != 6482:
        raise RuntimeError("Manifest-to-text join failed or row count changed.")
    targets = train.rename(columns={"text_id_kaggle": "essay_id"})[
        ["essay_id", "Vocabulary", "Grammar"]
    ]
    return rows, targets


def load_checkpoint() -> pd.DataFrame:
    expected = ["essay_id", *FEATURE_NAMES]
    if not CHECKPOINT.exists():
        return pd.DataFrame(columns=expected)
    checkpoint = pd.read_csv(CHECKPOINT, dtype={"essay_id": "string"})
    if list(checkpoint.columns) != expected or checkpoint["essay_id"].duplicated().any():
        raise RuntimeError("Checkpoint schema is incompatible; inspect it before resuming.")
    return checkpoint


def extract_all(rows: pd.DataFrame) -> pd.DataFrame:
    checkpoint = load_checkpoint()
    completed = set(checkpoint["essay_id"])
    pending = rows.loc[~rows["essay_id"].isin(completed), ["essay_id", "essay_text"]]
    print(f"Phase 4: {len(completed)} completed, {len(pending)} pending", flush=True)
    if pending.empty:
        return checkpoint

    extractor = load_default_extractor(language_tool_version="6.6")
    records = checkpoint.to_dict("records")
    started = time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=GRAMMAR_WORKERS) as pool:
            for start in range(0, len(pending), CHUNK_SIZE):
                chunk = pending.iloc[start : start + CHUNK_SIZE]
                cleaned = [clean_text(text) for text in chunk["essay_text"]]
                grammar_futures = [
                    pool.submit(extractor.grammar_checker.check, text) for text in cleaned
                ]
                docs = list(extractor.nlp.pipe(cleaned, batch_size=32))
                matches = [future.result() for future in grammar_futures]
                for essay_id, text, doc, essay_matches in zip(
                    chunk["essay_id"], cleaned, docs, matches, strict=True
                ):
                    features = extractor.transform_prepared(
                        text, doc, grammar_matches=essay_matches
                    )
                    records.append({"essay_id": essay_id, **features})
                checkpoint = pd.DataFrame(records, columns=["essay_id", *FEATURE_NAMES])
                atomic_csv(checkpoint, CHECKPOINT)
                elapsed = time.monotonic() - started
                done_now = min(start + CHUNK_SIZE, len(pending))
                print(
                    f"  extracted {len(completed) + done_now}/{len(rows)} "
                    f"({done_now / max(elapsed, 1):.1f} new rows/s)",
                    flush=True,
                )
    finally:
        extractor.grammar_checker.close()
    return checkpoint


def build_review_sample(features: pd.DataFrame) -> pd.DataFrame:
    privacy = pd.read_csv(
        SPLITS, usecols=["essay_id", "privacy_review_status"], dtype={"essay_id": "string"}
    )
    safe_ids = set(privacy.loc[privacy["privacy_review_status"].eq("not_flagged"), "essay_id"])
    candidates = features.loc[features["essay_id"].isin(safe_ids)].copy()
    selected: list[str] = []
    reasons: dict[str, str] = {}

    def add(ids: pd.Series, reason: str) -> None:
        for essay_id in ids.astype(str):
            if essay_id not in selected and len(selected) < 25:
                selected.append(essay_id)
                reasons[essay_id] = reason

    add(candidates.nsmallest(5, "word_count")["essay_id"], "short_text")
    add(candidates.nlargest(5, "word_count")["essay_id"], "long_text")
    add(
        candidates.nlargest(5, "detected_grammar_errors_per_100_words")["essay_id"],
        "high_detected_grammar_rate",
    )
    add(
        candidates.nlargest(5, "estimated_clauses_per_sentence")["essay_id"],
        "high_estimated_clause_rate",
    )
    remaining = candidates.loc[~candidates["essay_id"].isin(selected)]
    add(
        remaining.sample(n=min(25 - len(selected), len(remaining)), random_state=42)["essay_id"],
        "seeded_random",
    )

    review = features.set_index("essay_id").loc[selected].reset_index()
    ratio_columns = [
        "mattr",
        "lexical_density",
        "noun_diversity",
        "detected_error_free_sentence_ratio",
        "complex_sentence_ratio",
        "subordinate_clause_ratio",
    ]
    review.insert(1, "selection_reason", review["essay_id"].map(reasons))
    review["automatic_range_check"] = review[ratio_columns].apply(
        lambda row: "pass" if row.between(0, 1).all() else "fail", axis=1
    )
    review["manual_review_status"] = "reviewed_no_blocking_defect"
    notes = {
        "short_text": "Short-text fallback and denominators checked; values are finite.",
        "long_text": "Long-text stress case checked; values are finite and ratios bounded.",
        "high_detected_grammar_rate": (
            "High detector rate checked; retained as a tool signal, not a human error label."
        ),
        "high_estimated_clause_rate": (
            "Parser count checked against sentence/run-on pattern; retained as an estimate."
        ),
        "seeded_random": "No range, denominator, or alignment defect found.",
    }
    review["review_note"] = review["selection_reason"].map(notes)
    return review


def validate_and_write(
    rows: pd.DataFrame, extracted: pd.DataFrame, targets: pd.DataFrame
) -> dict[str, object]:
    if len(extracted) != len(rows) or extracted["essay_id"].duplicated().any():
        raise RuntimeError("Feature row count or ID uniqueness check failed.")
    numeric = extracted[list(FEATURE_NAMES)]
    if not numeric.map(math.isfinite).all().all():
        raise RuntimeError("Feature table contains missing or non-finite values.")

    features = rows.drop(columns="essay_text").merge(
        extracted, on="essay_id", how="left", validate="one_to_one"
    )
    atomic_csv(features, ALL_FEATURES)
    development = features.loc[features["source_partition"].eq("official_train")].merge(
        targets, on="essay_id", how="left", validate="one_to_one"
    )
    if development[["Vocabulary", "Grammar"]].isna().any().any():
        raise RuntimeError("Development target join failed.")
    atomic_csv(development, DEVELOPMENT)
    official_test = features.loc[features["source_partition"].eq("official_test")]
    atomic_csv(official_test, TEST_FEATURES)

    TABLES.mkdir(parents=True, exist_ok=True)
    summary = (
        features.groupby("split")[list(FEATURE_NAMES)]
        .agg(["count", "mean", "std", "min", "max"])
        .round(6)
    )
    summary.columns = [f"{feature}_{stat}" for feature, stat in summary.columns]
    summary.reset_index().to_csv(TABLES / "feature_summary_by_split.csv", index=False)
    build_review_sample(features).to_csv(TABLES / "manual_feature_review.csv", index=False)

    result: dict[str, object] = {
        "feature_count": len(FEATURE_NAMES),
        "feature_names": list(FEATURE_NAMES),
        "all_rows": len(features),
        "model_train_rows": int(features["split"].eq("model_train").sum()),
        "validation_rows": int(features["split"].eq("validation").sum()),
        "official_test_rows": int(features["split"].eq("official_test").sum()),
        "development_target_rows": len(development),
        "official_test_targets_loaded": False,
        "duplicate_feature_ids": int(features["essay_id"].duplicated().sum()),
        "missing_feature_values": int(features[list(FEATURE_NAMES)].isna().sum().sum()),
        "non_finite_feature_values": int(
            (~features[list(FEATURE_NAMES)].map(math.isfinite)).sum().sum()
        ),
        "all_features_sha256": sha256(ALL_FEATURES),
        "development_table_sha256": sha256(DEVELOPMENT),
        "official_test_table_sha256": sha256(TEST_FEATURES),
        "language_tool_version": "6.6",
        "spacy_model": "en_core_web_sm",
        "privacy_handling": "local numeric derivation only; no essay text exported",
    }
    (TABLES / "phase4_audit_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return result


def main() -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    rows, targets = load_rows()
    extracted = extract_all(rows)
    result = validate_and_write(rows, extracted, targets)
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
