"""Leakage-safe Task 6 training for the four approved regressors."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, PredefinedSplit

from mla_project.features.build_features import FEATURE_NAMES
from mla_project.models.train_random_forest import build_random_forest
from mla_project.models.train_ridge import build_ridge

TARGETS = ("Vocabulary", "Grammar")
MODEL_NAMES = (
    "ridge_vocabulary",
    "ridge_grammar",
    "random_forest_vocabulary",
    "random_forest_grammar",
)


@dataclass(frozen=True)
class PreparedTrainingData:
    """Privacy-eligible development partitions with a frozen feature schema."""

    train: pd.DataFrame
    validation: pd.DataFrame
    feature_columns: tuple[str, ...]
    privacy_counts: dict[str, int]


@dataclass
class TrainingResult:
    """Fitted models and text-free CV/validation-prediction evidence."""

    models: dict[str, Any]
    feature_columns: tuple[str, ...]
    selected_parameters: dict[str, dict[str, Any]]
    model_metadata: dict[str, dict[str, Any]]
    cv_results: pd.DataFrame
    validation_predictions: pd.DataFrame
    summary: dict[str, Any]


def _require_columns(frame: pd.DataFrame, required: set[str], *, table: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{table} is missing required columns: {missing}")


def _metadata_equal(left: pd.Series, right: pd.Series, *, numeric: bool = False) -> bool:
    if numeric:
        return left.astype("Int64").equals(right.astype("Int64"))
    return left.astype("string").equals(right.astype("string"))


def prepare_training_data(
    development_features: pd.DataFrame,
    split_ids: pd.DataFrame,
    *,
    eligible_status: str = "not_flagged",
    feature_columns: tuple[str, ...] = FEATURE_NAMES,
) -> PreparedTrainingData:
    """Validate, join, and privacy-filter the official-train development data."""
    if eligible_status != "not_flagged":
        raise ValueError("The frozen privacy gate permits only not_flagged rows.")
    if tuple(feature_columns) != FEATURE_NAMES:
        raise ValueError("Training must use the exact frozen 14-feature schema and order.")

    development = development_features.copy()
    manifest = split_ids.copy()
    _require_columns(
        development,
        {"essay_id", "source_partition", "split", "cv_fold", *feature_columns, *TARGETS},
        table="development feature table",
    )
    _require_columns(
        manifest,
        {"essay_id", "source_partition", "split", "cv_fold", "privacy_review_status"},
        table="split manifest",
    )
    if development["essay_id"].duplicated().any():
        raise ValueError("Development essay IDs must be unique.")
    if manifest["essay_id"].duplicated().any():
        raise ValueError("Split-manifest essay IDs must be unique.")
    if (
        development["split"].eq("official_test").any()
        or development["source_partition"].eq("official_test").any()
    ):
        raise ValueError("The training pipeline rejects official-test rows.")
    if set(development["split"].dropna()) != {"model_train", "validation"}:
        raise ValueError("Development data must contain model_train and validation rows only.")

    manifest_metadata = manifest[
        ["essay_id", "source_partition", "split", "cv_fold", "privacy_review_status"]
    ].rename(
        columns={
            "source_partition": "manifest_source_partition",
            "split": "manifest_split",
            "cv_fold": "manifest_cv_fold",
        }
    )
    merged = development.merge(manifest_metadata, on="essay_id", how="left", validate="one_to_one")
    if merged["privacy_review_status"].isna().any():
        raise ValueError("Every development essay must have a privacy status in the manifest.")
    metadata_matches = (
        _metadata_equal(merged["source_partition"], merged["manifest_source_partition"])
        and _metadata_equal(merged["split"], merged["manifest_split"])
        and _metadata_equal(merged["cv_fold"], merged["manifest_cv_fold"], numeric=True)
    )
    if not metadata_matches:
        raise ValueError("Development metadata does not match the frozen split manifest.")

    privacy_counts = {
        f"{split}_{status}": int(count)
        for (split, status), count in merged.groupby(["split", "privacy_review_status"])
        .size()
        .items()
    }
    eligible = merged.loc[merged["privacy_review_status"].eq(eligible_status)].copy()
    eligible = eligible.drop(
        columns=["manifest_source_partition", "manifest_split", "manifest_cv_fold"]
    )
    if eligible.empty:
        raise ValueError("No development rows pass the frozen privacy gate.")

    numeric = eligible[list(feature_columns) + list(TARGETS)].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any():
        raise ValueError("Features and targets must be complete numeric values.")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("Features and targets must contain only finite values.")
    if not numeric[list(TARGETS)].apply(lambda column: column.between(1.0, 5.0)).all().all():
        raise ValueError("Vocabulary and Grammar targets must remain within [1.0, 5.0].")
    eligible.loc[:, list(feature_columns) + list(TARGETS)] = numeric

    train = eligible.loc[eligible["split"].eq("model_train")].copy()
    validation = eligible.loc[eligible["split"].eq("validation")].copy()
    if train.empty or validation.empty:
        raise ValueError("Eligible model_train and validation partitions must both be non-empty.")
    if train["cv_fold"].isna().any():
        raise ValueError("Every model_train row must have a fixed CV fold.")
    if validation["cv_fold"].notna().any():
        raise ValueError("Validation rows must not have CV-fold assignments.")
    folds = set(train["cv_fold"].astype(int))
    if folds != set(range(5)):
        raise ValueError(f"Expected fixed CV folds 0-4; observed {sorted(folds)}.")
    if set(train["essay_id"]).intersection(validation["essay_id"]):
        raise ValueError("Model-train and validation essay IDs must be disjoint.")

    return PreparedTrainingData(
        train=train.reset_index(drop=True),
        validation=validation.reset_index(drop=True),
        feature_columns=tuple(feature_columns),
        privacy_counts=privacy_counts,
    )


def _parameter_grid(family: str, training_config: dict[str, Any]) -> dict[str, list[Any]]:
    return {
        f"model__{name}": list(values) for name, values in training_config["search"][family].items()
    }


def _fit_search(
    family: str,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    folds: pd.Series,
    *,
    ridge_config: dict[str, Any],
    random_forest_config: dict[str, Any],
    training_config: dict[str, Any],
) -> GridSearchCV:
    if family == "ridge":
        estimator = build_ridge(alpha=float(ridge_config.get("alpha", 1.0)))
    elif family == "random_forest":
        estimator = build_random_forest(
            n_estimators=int(random_forest_config.get("n_estimators", 300)),
            max_depth=random_forest_config.get("max_depth"),
            min_samples_leaf=int(random_forest_config.get("min_samples_leaf", 2)),
            max_features=random_forest_config.get("max_features", "sqrt"),
            random_state=int(random_forest_config.get("random_seed", 42)),
            n_jobs=int(random_forest_config.get("n_jobs", 1)),
        )
    else:
        raise ValueError(f"Unsupported model family: {family}")

    cv_config = training_config["cv"]
    expected_folds = int(cv_config["folds"])
    observed_folds = sorted(folds.astype(int).unique().tolist())
    if observed_folds != list(range(expected_folds)):
        raise ValueError(
            f"Training config expects folds 0-{expected_folds - 1}; observed {observed_folds}."
        )
    search = GridSearchCV(
        estimator=estimator,
        param_grid=_parameter_grid(family, training_config),
        scoring=str(cv_config["scoring"]),
        cv=PredefinedSplit(test_fold=folds.astype(int).to_numpy()),
        n_jobs=int(cv_config["n_jobs"]),
        refit=True,
        return_train_score=False,
        error_score="raise",
    )
    search.fit(x_train, y_train)
    return search


def train_models(
    development_features: pd.DataFrame,
    split_ids: pd.DataFrame,
    *,
    ridge_config: dict[str, Any] | None = None,
    random_forest_config: dict[str, Any] | None = None,
    training_config: dict[str, Any],
) -> TrainingResult:
    """Tune with fixed model-train folds, fit four models, and export predictions only."""
    prediction_config = training_config["prediction"]
    if prediction_config.get("clip_predictions") or prediction_config.get("round_predictions"):
        raise ValueError("Task 6 predictions must remain continuous and unrounded.")
    privacy_status = str(training_config.get("privacy", {}).get("eligible_status", "not_flagged"))
    prepared = prepare_training_data(
        development_features,
        split_ids,
        eligible_status=privacy_status,
    )
    ridge = dict(ridge_config or {})
    forest = dict(random_forest_config or {})
    x_train = prepared.train.loc[:, list(prepared.feature_columns)]
    x_validation = prepared.validation.loc[:, list(prepared.feature_columns)]
    folds = prepared.train["cv_fold"]
    predictions = pd.DataFrame({"essay_id": prepared.validation["essay_id"].to_numpy()})
    models: dict[str, Any] = {}
    selected_parameters: dict[str, dict[str, Any]] = {}
    model_metadata: dict[str, dict[str, Any]] = {}
    cv_rows: list[dict[str, Any]] = []

    for family in ("ridge", "random_forest"):
        for target in TARGETS:
            model_name = f"{family}_{target.lower()}"
            search = _fit_search(
                family,
                x_train,
                prepared.train[target],
                folds,
                ridge_config=ridge,
                random_forest_config=forest,
                training_config=training_config,
            )
            models[model_name] = search.best_estimator_
            selected_parameters[model_name] = {
                key.removeprefix("model__"): value for key, value in search.best_params_.items()
            }
            predictions[model_name] = search.predict(x_validation)
            results = search.cv_results_
            best_index = int(search.best_index_)
            model_metadata[model_name] = {
                "model_name": model_name,
                "family": family,
                "target": target,
                "feature_columns": list(prepared.feature_columns),
                "feature_count": len(prepared.feature_columns),
                "eligible_fit_rows": len(prepared.train),
                "cv": {
                    "splitter": "PredefinedSplit",
                    "folds": int(training_config["cv"]["folds"]),
                    "fold_counts": {
                        str(int(fold)): int(count)
                        for fold, count in folds.value_counts().sort_index().items()
                    },
                    "seed": None,
                    "seed_policy": "not_applicable_fixed_folds",
                    "scoring": str(training_config["cv"]["scoring"]),
                    "n_jobs": int(training_config["cv"]["n_jobs"]),
                },
                "best_parameters": dict(selected_parameters[model_name]),
                "best_cv_mean_mae": float(-results["mean_test_score"][best_index]),
                "best_cv_std_mae": float(results["std_test_score"][best_index]),
                "refit_on_all_eligible_rows": True,
            }
            for candidate_index, parameters in enumerate(results["params"]):
                row: dict[str, Any] = {
                    "model": model_name,
                    "family": family,
                    "target": target,
                    "candidate_index": candidate_index,
                    "parameters": json.dumps(
                        {key.removeprefix("model__"): value for key, value in parameters.items()},
                        sort_keys=True,
                    ),
                    "mean_cv_mae": float(-results["mean_test_score"][candidate_index]),
                    "std_cv_mae": float(results["std_test_score"][candidate_index]),
                    "rank": int(results["rank_test_score"][candidate_index]),
                }
                for fold in range(int(training_config["cv"]["folds"])):
                    row[f"fold_{fold}_mae"] = float(
                        -results[f"split{fold}_test_score"][candidate_index]
                    )
                cv_rows.append(row)

    fold_counts = {
        str(int(fold)): int(count) for fold, count in folds.value_counts().sort_index().items()
    }
    summary = {
        "official_test_loaded": False,
        "eligible_privacy_status": privacy_status,
        "model_train_rows": len(prepared.train),
        "validation_rows": len(prepared.validation),
        "feature_count": len(prepared.feature_columns),
        "feature_columns": list(prepared.feature_columns),
        "model_count": len(models),
        "model_names": list(MODEL_NAMES),
        "cv_fold_counts": fold_counts,
        "privacy_status_counts": prepared.privacy_counts,
        "validation_prediction_rows": len(predictions),
        "predictions_are_continuous": True,
        "validation_metrics_computed": False,
        "review_queue_computed": False,
    }
    return TrainingResult(
        models=models,
        feature_columns=prepared.feature_columns,
        selected_parameters=selected_parameters,
        model_metadata=model_metadata,
        cv_results=pd.DataFrame(cv_rows),
        validation_predictions=predictions,
        summary=summary,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def save_training_result(
    result: TrainingResult,
    output_dir: str | Path,
    *,
    run_metadata: dict[str, Any] | None = None,
) -> Path:
    """Persist models, CV results, predictions, and an integrity manifest."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    model_files: dict[str, str] = {}
    for name in MODEL_NAMES:
        if name not in result.models:
            raise ValueError(f"Training result is missing model {name}.")
        filename = f"{name}.joblib"
        joblib.dump(result.models[name], destination / filename)
        model_files[name] = filename

    data_files = {
        "feature_schema": "feature_schema.json",
        "selected_parameters": "selected_parameters.json",
        "cv_results": "cv_results.csv",
        "validation_predictions": "validation_predictions.csv",
        "training_summary": "training_summary.json",
    }
    (destination / data_files["feature_schema"]).write_text(
        json.dumps(list(result.feature_columns), indent=2), encoding="utf-8"
    )
    (destination / data_files["selected_parameters"]).write_text(
        json.dumps(result.selected_parameters, indent=2, sort_keys=True), encoding="utf-8"
    )
    result.cv_results.to_csv(destination / data_files["cv_results"], index=False)
    result.validation_predictions.to_csv(
        destination / data_files["validation_predictions"], index=False, float_format="%.12g"
    )
    summary = dict(result.summary)
    summary["selected_parameters"] = result.selected_parameters
    common_model_metadata = {
        "python_version": (run_metadata or {}).get("python_version"),
        "package_versions": (run_metadata or {}).get("package_versions", {}),
        "code_version": (run_metadata or {}).get("code_version"),
        "config_version": (run_metadata or {}).get("config_version"),
    }
    summary["model_metadata"] = {
        name: {**metadata, **common_model_metadata}
        for name, metadata in result.model_metadata.items()
    }
    summary["run_metadata"] = dict(run_metadata or {})
    (destination / data_files["training_summary"]).write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    all_files = list(model_files.values()) + list(data_files.values())
    artifact_manifest = {
        "model_files": model_files,
        "data_files": data_files,
        "sha256": {filename: _sha256(destination / filename) for filename in all_files},
    }
    manifest_path = destination / "artifact_manifest.json"
    manifest_path.write_text(
        json.dumps(artifact_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest_path


def load_model_artifacts(
    output_dir: str | Path,
) -> tuple[dict[str, Any], tuple[str, ...], dict[str, Any]]:
    """Load and integrity-check a saved four-model Task 6 artifact set."""
    source = Path(output_dir)
    manifest = json.loads((source / "artifact_manifest.json").read_text(encoding="utf-8"))
    for filename, expected in manifest["sha256"].items():
        path = source / filename
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError(f"Artifact integrity check failed: {filename}")
    models = {
        name: joblib.load(source / filename) for name, filename in manifest["model_files"].items()
    }
    feature_columns = tuple(
        json.loads((source / manifest["data_files"]["feature_schema"]).read_text(encoding="utf-8"))
    )
    if feature_columns != FEATURE_NAMES:
        raise ValueError("Saved artifact feature schema does not match the frozen schema.")
    metadata = json.loads(
        (source / manifest["data_files"]["training_summary"]).read_text(encoding="utf-8")
    )
    return models, feature_columns, metadata
