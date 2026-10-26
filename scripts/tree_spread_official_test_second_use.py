"""Prepare by default; access Test only with --i-have-permission. Never fit models."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
LOCK = "docs/signal_lock_tree_spread.md"
LOCK_SHA256 = "d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca"
LOCK_COMMIT = "4e381150edf08d49a134505e669058f1e0d27b48"
NOTICE = (
    "Official Test lần dùng thứ hai, cho tín hiệu đã khóa, dùng lại RF đã lưu từ tuần 9; "
    "không phải xác nhận độc lập sạch; không có tín hiệu nào khác được thử"
)
MODEL_HASHES = {
    "vocabulary": "899e9283e2eb01b4df6913eadd6cf8a4a823df0298ddfe820d14ba5912ffe7be",
    "grammar": "bc285a202de126247240982696ca94c16dbee82bf15906d8e75ebdf4405a8f91",
}
FEATURES = (
    "word_count", "sentence_count", "mean_sentence_length", "mtld", "mattr",
    "mean_word_frequency", "mean_word_length", "lexical_density", "noun_diversity",
    "detected_grammar_errors_per_100_words", "detected_error_free_sentence_ratio",
    "complex_sentence_ratio", "estimated_clauses_per_sentence", "subordinate_clause_ratio",
)
FEATURE_PATH = "data/05_model_features/official_test_features.csv"
MANIFEST_PATH = "data/02_split_manifest/essay_split_manifest.csv"
PREDICTION_PATH = "outputs/predictions/official_test_predictions.csv"
# Saved numeric human targets only; the raw essay/label CSV is never opened.
LABEL_PATH = "docs/data/phase9_tables/large_error_labels.csv"
INPUT_HASHES = {
    FEATURE_PATH: "dc7f7d03a9210a87f834b99ce5abd202296455d7c65871c52ab8fa2dea4a1967",
    MANIFEST_PATH: "a998e6ed7edd1361de31739f4e3474a248a3eda7f705ee8e2a8eba36d396cc96",
    PREDICTION_PATH: "48eb85d8bda27dd6261179d839fd5377d694741c5740f94ac88029b0593393e8",
    LABEL_PATH: "e234f6bd38ab9e708cf88db1176fe695c81fd192d91ace80fb09534e50827a44",
}
LOG_PATH = "reports/week9/tree_spread_official_test_second_use_log.json"
# CSV float round-trip allowance, fixed before Test access; no relative tolerance.
PREDICTION_ATOL = 1e-12


class GateError(RuntimeError):
    """Only aggregate, non-text diagnostics may enter this exception."""


def require(condition, message):
    if not condition:
        raise GateError(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hash(relative, expected):
    actual = sha256(ROOT / relative)
    require(actual == expected, f"SHA256 mismatch: {relative}; expected={expected}; actual={actual}")
    return actual


def check_predictions(actual, saved, target):
    import numpy as np

    require(actual.shape == saved.shape, f"RF prediction shape mismatch: {target}")
    require(np.isfinite(actual).all() and np.isfinite(saved).all(),
            f"Nonfinite RF predictions: {target}")
    delta = np.abs(actual - saved)
    require(bool((delta <= PREDICTION_ATOL).all()),
            f"RF prediction mismatch: {target}; mismatched_rows={int((delta > PREDICTION_ATOL).sum())}; "
            f"max_absolute_difference={float(delta.max())}; atol={PREDICTION_ATOL}; rtol=0")


def check_population_and_errors(n, large, saved_large):
    import numpy as np

    require(n == 2518, f"Eligible population mismatch: expected=2518; actual={n}")
    require(bool(np.array_equal(large, saved_large)),
            f"Large-error membership mismatch: rows={int(np.count_nonzero(large != saved_large))}")
    require(int(large.sum()) == 208,
            f"Large-error count mismatch: expected=208; actual={int(large.sum())}")


def load_checked_inputs(record, checkpoint):
    import pandas as pd

    # Hash and identify the fixed cohort before reading numeric labels.
    record["input_sha256"] = {p: verify_hash(p, h) for p, h in INPUT_HASHES.items()}
    record["cohort"] = "Existing Phase 9 Official Test; privacy_review_status=not_flagged"
    record["fold_membership"] = "single existing holdout; no resplitting"
    checkpoint()

    def read(path, columns):
        frame = pd.read_csv(ROOT / path, usecols=columns, dtype={"essay_id": str},
                            float_precision="round_trip")
        require(frame.essay_id.notna().all() and frame.essay_id.is_unique,
                f"Missing or duplicate essay IDs: {path}")
        return frame

    manifest = read(MANIFEST_PATH, ["essay_id", "split", "privacy_review_status"])
    official = manifest.loc[manifest.split.eq("official_test")]
    eligible = official.loc[official.privacy_review_status.eq("not_flagged"), ["essay_id"]]
    require(len(eligible) == 2518, f"Eligible population mismatch: expected=2518; actual={len(eligible)}")
    features = read(FEATURE_PATH, ["essay_id", *FEATURES])
    require(len(official) == len(features) == 2571 and set(official.essay_id) == set(features.essay_id),
            "Feature IDs do not match the frozen 2571-row Official Test population")
    predictions = read(PREDICTION_PATH, ["essay_id", "random_forest_vocabulary", "random_forest_grammar"])
    labels = read(LABEL_PATH, ["essay_id", "Vocabulary", "Grammar"])
    expected_ids = set(eligible.essay_id)
    require(expected_ids == set(predictions.essay_id) == set(labels.essay_id),
            "Eligible IDs, saved predictions and saved numeric labels differ")
    frame = eligible.merge(features, on="essay_id", validate="one_to_one").merge(
        predictions, on="essay_id", validate="one_to_one").merge(
        labels, on="essay_id", validate="one_to_one")
    return frame.sort_values("essay_id").reset_index(drop=True)


def evaluate(record, checkpoint):
    import joblib
    import numpy as np
    from scipy.stats import hypergeom

    record["lock_sha256"] = verify_hash(LOCK, LOCK_SHA256)
    models = {}
    record["model_sha256"] = {}
    for target, expected_hash in MODEL_HASHES.items():
        path = f"outputs/phase6/random_forest_{target}.joblib"
        record["model_sha256"][path] = verify_hash(path, expected_hash)
    for target in MODEL_HASHES:
        pipeline = joblib.load(ROOT / f"outputs/phase6/random_forest_{target}.joblib")
        forest = pipeline.named_steps["model"]
        expected = dict(n_estimators=300, max_features="sqrt", max_depth=10,
                        min_samples_leaf=2 if target == "vocabulary" else 5,
                        random_state=42, n_jobs=1)
        require(all(forest.get_params()[key] == value for key, value in expected.items())
                and len(forest.estimators_) == 300
                and pipeline.named_steps["imputer"].strategy == "median",
                f"Frozen pipeline configuration mismatch: {target}")
        models[target] = pipeline
    frame = load_checked_inputs(record, checkpoint)
    require(len(frame) == 2518,
            f"Eligible population mismatch: expected=2518; actual={len(frame)}")
    x = frame.loc[:, list(FEATURES)]
    y = frame[["Vocabulary", "Grammar"]].to_numpy(dtype=float)
    require(np.isfinite(x.to_numpy(dtype=float)).all() and np.isfinite(y).all(),
            "Nonfinite input features or targets")
    actual = []
    for target in MODEL_HASHES:
        values = models[target].predict(x)
        check_predictions(values, frame[f"random_forest_{target}"].to_numpy(), target)
        actual.append(values)
    actual = np.column_stack(actual)
    saved = frame[["random_forest_vocabulary", "random_forest_grammar"]].to_numpy()
    large = np.max(np.abs(actual - y), axis=1) >= 1.0
    saved_large = np.max(np.abs(saved - y), axis=1) >= 1.0
    check_population_and_errors(len(frame), large, saved_large)
    record["pre_signal_checks"] = "PASS: model hashes, predictions, identical error IDs, N=2518, K=208"
    checkpoint()

    # First and only signal computation; all mandatory stop gates precede this point.
    stds = []
    for target in MODEL_HASHES:
        pipeline = models[target]
        transformed = pipeline[:-1].transform(x)
        tree_predictions = np.stack([tree.predict(transformed) for tree in pipeline[-1].estimators_])
        stds.append(tree_predictions.std(axis=0, ddof=0))
    signal = np.maximum(stds[0], stds[1])
    require(np.isfinite(signal).all(), "Nonfinite locked tree-spread signal")
    n, K = len(frame), int(large.sum())
    k = math.ceil(0.20 * n)
    queue = sorted(range(n), key=lambda i: (-float(signal[i]), str(frame.essay_id.iloc[i])))[:k]
    caught = int(large[queue].sum())
    # Detect concurrent file changes before releasing any signal result.
    for path, expected_hash in {LOCK: LOCK_SHA256, **INPUT_HASHES,
                               **{f"outputs/phase6/random_forest_{t}.joblib": h
                                  for t, h in MODEL_HASHES.items()}}.items():
        verify_hash(path, expected_hash)
    record["result"] = dict(eligible_count=n, budget_ceil_20pct=k, large_error_count=K,
                            caught=caught, expected_random=k*K/n,
                            exact_one_sided_p=float(hypergeom.sf(caught-1, n, K, k)))
    record["status"] = "COMPLETED"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--i-have-permission", action="store_true",
                        help="Explicitly authorize opening Test and evaluating the single locked signal")
    args = parser.parse_args(argv)
    if not args.i_have_permission:
        print("NOT RUN: explicit --i-have-permission required; no Test files opened.")
        return 0
    log_path = ROOT / LOG_PATH
    # Exclusive creation: never overwrite a completed, failed or interrupted Test-use log.
    try:
        stream = log_path.open("x", encoding="utf-8")
    except FileExistsError:
        print("STOP: second-use log already exists; no Test files opened.")
        return 2
    with stream:
        record = dict(status="STARTED", notice=NOTICE, teacher_permission_date="",
                      started_utc=datetime.now(timezone.utc).isoformat(), lock_commit=LOCK_COMMIT,
                      prediction_atol=PREDICTION_ATOL, prediction_rtol=0)

        def checkpoint():
            stream.seek(0)
            json.dump(record, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.truncate()
            stream.flush()

        checkpoint()
        try:
            record["run_commit"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
            record["script_sha256"] = sha256(Path(__file__))
            evaluate(record, checkpoint)
        except Exception as exc:
            record.pop("result", None)
            record["status"] = "STOPPED"
            # Never echo third-party exceptions, which can include data values.
            record["failure"] = str(exc) if isinstance(exc, GateError) else type(exc).__name__
            checkpoint()
            print("STOP: " + record["failure"] + "; no signal result released.")
            return 2
        checkpoint()
    print(NOTICE)
    print(json.dumps(record["result"], ensure_ascii=False))
    print("Log: " + LOG_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
