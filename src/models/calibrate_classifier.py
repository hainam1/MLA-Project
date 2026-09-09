"""Fit temperature scaling for the selected sentence classifier on validation data only."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.metrics import log_loss

from src.models.calibration import TemperatureScaledClassifier


def fit_temperature(model, features: pd.DataFrame, labels: pd.Series) -> float:
    probabilities = np.clip(model.predict_proba(features), 1e-12, 1.0)

    def objective(temperature: float) -> float:
        logits = np.log(probabilities) / temperature
        logits -= logits.max(axis=1, keepdims=True)
        scaled = np.exp(logits)
        scaled /= scaled.sum(axis=1, keepdims=True)
        return float(log_loss(labels, scaled, labels=model.classes_))

    result = minimize_scalar(objective, bounds=(0.25, 5.0), method="bounded")
    if not result.success:
        raise RuntimeError(result.message)
    return float(result.x)


def main() -> None:
    model_dir = Path("src/models/sentence_cefr")
    metadata_path = model_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    features = metadata["feature_columns"]
    validation = pd.read_csv("data/processed/sentence_cefr_validation.csv")
    base_model = joblib.load(model_dir / "best_model.joblib")
    temperature = fit_temperature(base_model, validation[features], validation["cefr_label"])
    calibrated = TemperatureScaledClassifier(base_model, temperature)
    joblib.dump(calibrated, model_dir / "best_model_calibrated.joblib")
    metadata["calibration"] = {
        "method": "temperature_scaling",
        "fit_split": "validation",
        "temperature": round(temperature, 6),
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata["calibration"], indent=2))


if __name__ == "__main__":
    main()
