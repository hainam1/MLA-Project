"""Restore missing Phase 5 length-only model artifacts after reproduction checks.

This script reads development data only. It never reads official-test features or labels.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from mla_project.evaluation.regression_metrics import regression_metrics
from mla_project.models.length_baselines import (
    FROZEN_FOREST_PARAMETERS,
    FROZEN_RIDGE_ALPHA,
    LENGTH_FEATURES,
    TARGETS,
    predict_length_models,
    reconstruct_length_models,
)
from mla_project.pipelines.training_pipeline import prepare_training_data

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
MANIFEST_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
HISTORICAL_PREDICTIONS_PATH = ROOT / "outputs" / "predictions" / "phase5_validation_baselines.csv"
HISTORICAL_METRICS_PATH = (
    ROOT / "docs" / "data" / "phase5_tables" / "baseline_regression_metrics.csv"
)
OUTPUT_DIR = ROOT / "outputs" / "phase5" / "reconstructed"
PREDICTION_ATOL = 1e-10
METRIC_ATOL = 1e-8


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    if (OUTPUT_DIR / "artifact_manifest.json").exists():
        raise FileExistsError("Reconstructed baseline artifacts already exist; refusing to refit.")
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    manifest = pd.read_csv(MANIFEST_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, manifest, eligible_status="not_flagged")
    models = reconstruct_length_models(prepared.train)
    reproduced = predict_length_models(models, prepared.validation)
    historical = pd.read_csv(HISTORICAL_PREDICTIONS_PATH, dtype={"essay_id": "string"})
    prediction_columns = [
        f"length_{family}_{target.lower()}"
        for target in TARGETS
        for family in ("ridge", "random_forest")
    ]
    joined = reproduced.merge(
        historical[["essay_id", *prediction_columns]],
        on="essay_id",
        how="inner",
        validate="one_to_one",
        suffixes=("_reproduced", "_historical"),
    )
    if len(joined) != 762:
        raise ValueError("Historical validation predictions do not match the frozen 762-row set.")
    prediction_differences = {
        column: float(
            np.max(
                np.abs(
                    joined[f"{column}_reproduced"].to_numpy(dtype=float)
                    - joined[f"{column}_historical"].to_numpy(dtype=float)
                )
            )
        )
        for column in prediction_columns
    }
    if max(prediction_differences.values()) > PREDICTION_ATOL:
        raise RuntimeError(
            f"Reconstructed validation predictions differ from history: {prediction_differences}"
        )

    historical_metrics = pd.read_csv(HISTORICAL_METRICS_PATH).set_index(["baseline", "target"])
    metric_differences: dict[str, dict[str, float]] = {}
    for target in TARGETS:
        actual = prepared.validation[target].to_numpy(dtype=float)
        for family in ("ridge", "random_forest"):
            baseline = f"length_{family}"
            column = f"{baseline}_{target.lower()}"
            observed = regression_metrics(actual, reproduced[column].to_numpy(dtype=float))
            key = f"{baseline}/{target}"
            metric_differences[key] = {
                metric: abs(
                    float(observed[metric])
                    - float(historical_metrics.loc[(baseline, target), metric])
                )
                for metric in ("mae", "rmse", "r2")
            }
    if max(value for row in metric_differences.values() for value in row.values()) > METRIC_ATOL:
        raise RuntimeError(
            f"Reconstructed validation metrics differ from history: {metric_differences}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=False)
    model_files: dict[str, str] = {}
    for name, model in models.items():
        filename = f"{name}.joblib"
        joblib.dump(model, OUTPUT_DIR / filename)
        model_files[name] = filename
    reproduction = {
        "official_test_loaded": False,
        "train_rows": len(prepared.train),
        "validation_rows": len(prepared.validation),
        "features": list(LENGTH_FEATURES),
        "ridge_alpha": FROZEN_RIDGE_ALPHA,
        "random_forest_parameters": FROZEN_FOREST_PARAMETERS,
        "prediction_atol": PREDICTION_ATOL,
        "metric_atol": METRIC_ATOL,
        "maximum_prediction_differences": prediction_differences,
        "metric_absolute_differences": metric_differences,
    }
    reproduction_path = OUTPUT_DIR / "reproduction_check.json"
    reproduction_path.write_text(json.dumps(reproduction, indent=2), encoding="utf-8")
    files = [*model_files.values(), reproduction_path.name]
    artifact_manifest = {
        "model_files": model_files,
        "sha256": {filename: sha256(OUTPUT_DIR / filename) for filename in files},
        "source_sha256": {
            "development_features": sha256(DEVELOPMENT_PATH),
            "split_manifest": sha256(MANIFEST_PATH),
            "historical_predictions": sha256(HISTORICAL_PREDICTIONS_PATH),
            "historical_metrics": sha256(HISTORICAL_METRICS_PATH),
        },
    }
    manifest_path = OUTPUT_DIR / "artifact_manifest.json"
    manifest_path.write_text(json.dumps(artifact_manifest, indent=2), encoding="utf-8")
    print(json.dumps({**reproduction, "artifact_manifest": artifact_manifest}, indent=2))


if __name__ == "__main__":
    main()
