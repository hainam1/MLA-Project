"""Train and compare linguistic-feature models for sentence CEFR classification."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.features import SENTENCE_FEATURE_COLUMNS

RANDOM_STATE = 42
AUXILIARY_LEXICON_FEATURES = ["avg_word_cefr", "max_word_cefr", "word_oov_ratio"]


def evaluate_predictions(labels: pd.Series, predictions: np.ndarray) -> dict[str, float]:
    label_array = np.asarray(labels)
    prediction_array = np.asarray(predictions)
    return {
        "accuracy": round(float(accuracy_score(label_array, prediction_array)), 4),
        "macro_f1": round(float(f1_score(label_array, prediction_array, average="macro")), 4),
        "weighted_f1": round(float(f1_score(label_array, prediction_array, average="weighted")), 4),
        "quadratic_weighted_kappa": round(
            float(cohen_kappa_score(label_array, prediction_array, weights="quadratic")), 4
        ),
        "adjacent_accuracy": round(float(np.mean(np.abs(label_array - prediction_array) <= 1)), 4),
        "mean_absolute_level_error": round(
            float(mean_absolute_error(label_array, prediction_array)), 4
        ),
    }


def candidate_models() -> dict[str, object]:
    return {
        "majority": DummyClassifier(strategy="most_frequent"),
        "knn": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    KNeighborsClassifier(
                        n_neighbors=11,
                        weights="distance",
                        metric="minkowski",
                        p=2,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "decision_tree": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "classifier",
                    DecisionTreeClassifier(
                        max_depth=12,
                        min_samples_split=4,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def fit_and_evaluate(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    feature_columns: list[str],
) -> tuple[dict[str, object], list[dict]]:
    trained: dict[str, object] = {}
    results: list[dict] = []
    for name, model in candidate_models().items():
        started = time.perf_counter()
        model.fit(train[feature_columns], train["cefr_label"])
        elapsed = time.perf_counter() - started
        predictions = model.predict(validation[feature_columns])
        trained[name] = model
        results.append(
            {
                "model": name,
                "feature_set": "linguistic",
                "feature_count": len(feature_columns),
                "validation": evaluate_predictions(validation["cefr_label"], predictions),
                "training_seconds": round(elapsed, 3),
            }
        )
    return trained, results


def safe_name(value: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "_", value.casefold()).strip("_")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evaluate-test",
        action="store_true",
        help="Open the held-out test split; use only after configurations are frozen",
    )
    parser.add_argument(
        "--without-auxiliary-lexicon",
        action="store_true",
        help="Run the required ablation without aggregate word-CEFR features",
    )
    args = parser.parse_args()

    data_dir = Path("data/processed")
    train = pd.read_csv(data_dir / "sentence_cefr_train.csv")
    validation = pd.read_csv(data_dir / "sentence_cefr_validation.csv")
    feature_columns = list(SENTENCE_FEATURE_COLUMNS)
    if args.without_auxiliary_lexicon:
        feature_columns = [
            column for column in feature_columns if column not in AUXILIARY_LEXICON_FEATURES
        ]

    forbidden = {"text", "source", "cluster_id", "sentence_id", "cefr_level", "cefr_label"}
    if forbidden.intersection(feature_columns):
        raise AssertionError("A metadata or target column entered the feature matrix")
    missing = set(feature_columns).difference(train.columns)
    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")

    trained, results = fit_and_evaluate(train, validation, feature_columns)
    selected = max(
        (result for result in results if result["model"] != "majority"),
        key=lambda result: result["validation"]["macro_f1"],
    )["model"]

    model_dir = Path("src/models/sentence_cefr")
    model_dir.mkdir(parents=True, exist_ok=True)
    for name, model in trained.items():
        if name != "majority":
            joblib.dump(model, model_dir / f"{safe_name(name)}.joblib")
    joblib.dump(trained[selected], model_dir / "best_model.joblib")

    output = {
        "status": "validation_complete",
        "random_state": RANDOM_STATE,
        "selection_metric": "validation_macro_f1",
        "selected_model": selected,
        "feature_columns": feature_columns,
        "uses_auxiliary_lexicon": not args.without_auxiliary_lexicon,
        "results": results,
    }

    if args.evaluate_test:
        test = pd.read_csv(data_dir / "sentence_cefr_test.csv")
        test_outputs = []
        prediction_frame = test[
            ["sentence_id", "text", "source", "cefr_level", "cefr_label"]
        ].copy()
        for name, model in trained.items():
            predictions = model.predict(test[feature_columns])
            prediction_frame[f"prediction_{safe_name(name)}"] = predictions
            test_outputs.append(
                {
                    "model": name,
                    "metrics": evaluate_predictions(test["cefr_label"], predictions),
                    "classification_report": classification_report(
                        test["cefr_label"], predictions, output_dict=True, zero_division=0
                    ),
                    "confusion_matrix": confusion_matrix(test["cefr_label"], predictions).tolist(),
                }
            )
        output["status"] = "test_complete"
        output["test_results"] = test_outputs
        reports = Path("reports")
        prediction_frame.to_csv(reports / "final_predictions.csv", index=False, encoding="utf-8")
        (reports / "final_metrics.json").write_text(
            json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    (model_dir / "metadata.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
