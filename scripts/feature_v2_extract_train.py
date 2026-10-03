"""Extract experimental v2 features from privacy-eligible model-train essays only.

The output is numeric and text-free. Validation and official-test essays are never
loaded. A checkpoint makes local LanguageTool extraction resumable.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import tempfile
import time

import numpy as np
import pandas as pd

from mla_project.features.build_features import load_default_extractor
from mla_project.features.feature_v2 import V2_FEATURE_NAMES, extract_v2_features
from mla_project.features.preprocessing import clean_text

ROOT = Path(__file__).resolve().parents[1]
CLEAN_TRAIN = ROOT / "data" / "03_clean_ready_to_use" / "model_train_3128.csv"
MANIFEST = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
CHECKPOINT = ROOT / "data" / "04_intermediate_work" / "feature_v2_train_checkpoint.csv"
OUTPUT = ROOT / "data" / "05_model_features" / "feature_v2_model_train_3050.csv"
SUMMARY = ROOT / "docs" / "data" / "improvement_tables" / "feature_v2_extraction_summary.json"
EXPECTED_ROWS = 3_050
CHUNK_SIZE = 100
WORKERS = 8


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", encoding="utf-8", newline="", delete=False, dir=path.parent
    ) as stream:
        temporary = Path(stream.name)
        frame.to_csv(stream, index=False, float_format="%.12g")
    temporary.replace(path)


def _eligible_rows() -> pd.DataFrame:
    manifest = pd.read_csv(
        MANIFEST,
        usecols=["essay_id", "split", "privacy_review_status"],
        dtype={"essay_id": "string"},
    )
    eligible = manifest.loc[
        manifest["split"].eq("model_train")
        & manifest["privacy_review_status"].eq("not_flagged"),
        ["essay_id"],
    ]
    train = pd.read_csv(CLEAN_TRAIN, usecols=["essay_id", "clean_text"], dtype={"essay_id": "string"})
    rows = eligible.merge(train, on="essay_id", how="left", validate="one_to_one")
    if len(rows) != EXPECTED_ROWS or rows["clean_text"].isna().any():
        raise ValueError("Feature-v2 extraction requires exactly 3,050 eligible model-train texts.")
    return rows


def _load_checkpoint(eligible_ids: set[str]) -> pd.DataFrame:
    columns = ["essay_id", *V2_FEATURE_NAMES]
    if not CHECKPOINT.exists():
        return pd.DataFrame(columns=columns)
    checkpoint = pd.read_csv(CHECKPOINT, dtype={"essay_id": "string"})
    if (
        list(checkpoint.columns) != columns
        or checkpoint["essay_id"].duplicated().any()
        or not set(checkpoint["essay_id"]).issubset(eligible_ids)
    ):
        raise ValueError("Feature-v2 checkpoint schema or IDs changed; inspect before resuming.")
    return checkpoint


def main() -> None:
    rows = _eligible_rows()
    checkpoint = _load_checkpoint(set(rows["essay_id"]))
    pending = rows.loc[~rows["essay_id"].isin(checkpoint["essay_id"])]
    records = checkpoint.to_dict("records")
    print(f"Feature v2: {len(records)} completed, {len(pending)} pending", flush=True)
    if not pending.empty:
        extractor = load_default_extractor(language_tool_version="6.6")
        started = time.monotonic()
        try:
            with ThreadPoolExecutor(max_workers=WORKERS) as pool:
                for start in range(0, len(pending), CHUNK_SIZE):
                    chunk = pending.iloc[start : start + CHUNK_SIZE]
                    texts = [clean_text(value) for value in chunk["clean_text"]]
                    futures = [pool.submit(extractor.grammar_checker.check, text) for text in texts]
                    docs = list(extractor.nlp.pipe(texts, batch_size=32))
                    for essay_id, doc, future in zip(chunk["essay_id"], docs, futures, strict=True):
                        records.append(
                            {"essay_id": essay_id, **extract_v2_features(doc, future.result())}
                        )
                    checkpoint = pd.DataFrame(records, columns=["essay_id", *V2_FEATURE_NAMES])
                    _atomic_csv(checkpoint, CHECKPOINT)
                    completed = min(start + CHUNK_SIZE, len(pending))
                    print(
                        f"  {len(records)}/{EXPECTED_ROWS} rows; "
                        f"{completed / max(time.monotonic() - started, 1):.1f} new rows/s",
                        flush=True,
                    )
        finally:
            extractor.grammar_checker.close()

    features = pd.DataFrame(records, columns=["essay_id", *V2_FEATURE_NAMES])
    if (
        len(features) != EXPECTED_ROWS
        or features["essay_id"].duplicated().any()
        or set(features["essay_id"]) != set(rows["essay_id"])
        or not np.isfinite(features[list(V2_FEATURE_NAMES)].to_numpy(dtype=float)).all()
    ):
        raise ValueError("Feature-v2 result failed completeness or numeric validation.")
    _atomic_csv(features, OUTPUT)
    summary = {
        "status": "experimental_train_only",
        "rows": len(features),
        "features": list(V2_FEATURE_NAMES),
        "validation_loaded": False,
        "official_test_loaded": False,
        "private_text_exported": False,
        "input_sha256": {"clean_train": _sha256(CLEAN_TRAIN), "manifest": _sha256(MANIFEST)},
        "output_sha256": _sha256(OUTPUT),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
