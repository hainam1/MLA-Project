"""Calibrate Model 2a/2b probabilities and derive selective-review thresholds."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.metrics import accuracy_score, f1_score, log_loss

from src.features import SENTENCE_FEATURE_COLUMNS, WORD_FEATURE_COLUMNS
from src.models.calibration import TemperatureScaledClassifier

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_SPECS = {
    "model2a": {
        "model": PROJECT_ROOT / "src/models/cefr_word_classifier/model.pkl",
        "metadata": PROJECT_ROOT / "src/models/cefr_word_classifier/metadata.json",
        "val": PROJECT_ROOT / "data/processed/model2a_word_cefr_val.csv",
        "test": PROJECT_ROOT / "data/processed/model2a_word_cefr_test.csv",
        "features": WORD_FEATURE_COLUMNS,
    },
    "model2b": {
        "model": PROJECT_ROOT / "src/models/cefr_sentence_classifier/model.pkl",
        "metadata": PROJECT_ROOT / "src/models/cefr_sentence_classifier/metadata.json",
        "val": PROJECT_ROOT / "data/processed/model2b_sentence_cefr_val.csv",
        "test": PROJECT_ROOT / "data/processed/model2b_sentence_cefr_test.csv",
        "features": SENTENCE_FEATURE_COLUMNS,
    },
}


def fit_temperature(estimator, features, labels) -> float:
    classes = estimator.classes_
    probabilities = np.clip(estimator.predict_proba(features), 1e-12, 1.0)

    def objective(temperature):
        logits = np.log(probabilities) / temperature
        logits -= logits.max(axis=1, keepdims=True)
        scaled = np.exp(logits)
        scaled /= scaled.sum(axis=1, keepdims=True)
        return log_loss(labels, scaled, labels=classes)

    result = minimize_scalar(objective, bounds=(0.25, 5.0), method="bounded")
    if not result.success:
        raise RuntimeError(f"Temperature optimization failed: {result.message}")
    return float(result.x)


def expected_calibration_error(y_true, probabilities, bins: int = 10) -> float:
    confidences = probabilities.max(axis=1)
    predictions = probabilities.argmax(axis=1)
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for lower, upper in zip(edges[:-1], edges[1:]):
        include = (confidences > lower) & (confidences <= upper)
        if include.any():
            accuracy = np.mean(predictions[include] == np.asarray(y_true)[include])
            ece += include.mean() * abs(accuracy - confidences[include].mean())
    return float(ece)


def multiclass_brier_score(y_true, probabilities, classes) -> float:
    class_to_index = {label: index for index, label in enumerate(classes)}
    one_hot = np.zeros_like(probabilities)
    for row, label in enumerate(y_true):
        one_hot[row, class_to_index[label]] = 1.0
    return float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1)))


def probability_metrics(model, features, labels) -> dict:
    probabilities = model.predict_proba(features)
    predictions = model.predict(features)
    return {
        "accuracy": round(float(accuracy_score(labels, predictions)), 4),
        "macro_f1": round(float(f1_score(labels, predictions, average="macro")), 4),
        "log_loss": round(float(log_loss(labels, probabilities, labels=model.classes_)), 4),
        "brier_multiclass": round(multiclass_brier_score(labels, probabilities, model.classes_), 4),
        "ece_10_bins": round(expected_calibration_error(labels, probabilities), 4),
    }


def choose_review_threshold(model, features, labels) -> tuple[float, dict]:
    probabilities = model.predict_proba(features)
    confidence = probabilities.max(axis=1)
    predictions = model.predict(features)
    baseline_accuracy = accuracy_score(labels, predictions)
    target_accuracy = min(0.85, baseline_accuracy + 0.10)
    candidates = []
    for threshold in np.arange(0.30, 0.91, 0.01):
        accepted = confidence >= threshold
        coverage = accepted.mean()
        if coverage < 0.20:
            continue
        selective_accuracy = accuracy_score(np.asarray(labels)[accepted], predictions[accepted])
        candidates.append((threshold, coverage, selective_accuracy))

    meeting_target = [row for row in candidates if row[2] >= target_accuracy]
    if meeting_target:
        selected = min(meeting_target, key=lambda row: row[0])
        rule = "lowest_threshold_reaching_baseline_plus_10pp"
    else:
        selected = max(candidates, key=lambda row: (row[2], row[1]))
        rule = "best_selective_accuracy_with_minimum_20pct_coverage"

    threshold, coverage, selective_accuracy = selected
    return round(float(threshold), 2), {
        "selection_rule": rule,
        "minimum_coverage": 0.20,
        "target_selective_accuracy": round(float(target_accuracy), 4),
        "validation_coverage": round(float(coverage), 4),
        "validation_selective_accuracy": round(float(selective_accuracy), 4),
        "validation_review_rate": round(float(1.0 - coverage), 4),
    }


def selective_test_metrics(model, features, labels, threshold: float) -> dict:
    probabilities = model.predict_proba(features)
    confidence = probabilities.max(axis=1)
    predictions = model.predict(features)
    accepted = confidence >= threshold
    return {
        "coverage": round(float(accepted.mean()), 4),
        "review_rate": round(float(1.0 - accepted.mean()), 4),
        "selective_accuracy": round(
            float(accuracy_score(np.asarray(labels)[accepted], predictions[accepted])), 4
        ),
        "accepted_samples": int(accepted.sum()),
        "review_samples": int((~accepted).sum()),
    }


def calibrate_model(name: str, spec: dict) -> dict:
    backup = spec["model"].with_name("model_uncalibrated.pkl")
    base_model = joblib.load(spec["model"])
    if isinstance(base_model, TemperatureScaledClassifier):
        if backup.exists():
            base_model = joblib.load(backup)
        else:
            raise RuntimeError(f"{name} is already calibrated; retrain it before calibrating again")
    validation = pd.read_csv(spec["val"])
    test = pd.read_csv(spec["test"])
    feature_names = spec["features"]
    x_val, y_val = validation[feature_names], validation["cefr_label"]
    x_test, y_test = test[feature_names], test["cefr_label"]

    before = probability_metrics(base_model, x_test, y_test)
    temperature = fit_temperature(base_model, x_val, y_val)
    calibrated = TemperatureScaledClassifier(base_model, temperature)
    after = probability_metrics(calibrated, x_test, y_test)
    threshold, policy = choose_review_threshold(calibrated, x_val, y_val)
    test_policy = selective_test_metrics(calibrated, x_test, y_test, threshold)

    shutil.copy2(spec["model"], backup)
    joblib.dump(calibrated, spec["model"])

    metadata = json.loads(spec["metadata"].read_text(encoding="utf-8"))
    metadata["calibration"] = {
        "method": "temperature_scaling",
        "temperature": round(temperature, 6),
        "fit_split": "validation",
        "test_metrics_before": before,
        "test_metrics_after": after,
        "needs_review_threshold": threshold,
        "threshold_policy": policy,
        "test_selective_metrics": test_policy,
        "uncalibrated_backup": backup.relative_to(PROJECT_ROOT).as_posix(),
    }
    spec["metadata"].write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return metadata["calibration"]


def main() -> None:
    for name, spec in MODEL_SPECS.items():
        result = calibrate_model(name, spec)
        print(f"{name}: {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
