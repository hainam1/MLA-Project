from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
import pytest

from mla_project.features.build_features import FEATURE_NAMES
from mla_project.pipelines.training_pipeline import (
    load_model_artifacts,
    prepare_training_data,
    save_training_result,
    train_models,
)


def prepared_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = 31
    essay_ids = [f"essay-{index:02d}" for index in range(rows)]
    split = ["model_train"] * 25 + ["validation"] * 6
    cv_fold = [float(index % 5) for index in range(25)] + [np.nan] * 6
    base = np.linspace(0.1, 3.1, rows)
    development = pd.DataFrame(
        {
            "essay_id": essay_ids,
            "source_partition": "official_train",
            "split": split,
            "cv_fold": cv_fold,
            **{
                feature: base * (feature_index + 1)
                for feature_index, feature in enumerate(FEATURE_NAMES)
            },
            "Vocabulary": 1.0 + (base % 4.0),
            "Grammar": 1.0 + ((base * 1.2) % 4.0),
        }
    )
    manifest = development[["essay_id", "source_partition", "split", "cv_fold"]].copy()
    manifest["prompt_id"] = [f"prompt-{index % 3}" for index in range(rows)]
    manifest["normalized_text_hash"] = [f"hash-{index}" for index in range(rows)]
    manifest["privacy_review_status"] = "not_flagged"
    manifest.loc[0, "privacy_review_status"] = "flagged_by_rater"
    return development, manifest


def tiny_training_config() -> dict[str, object]:
    return {
        "cv": {"folds": 5, "scoring": "neg_mean_absolute_error", "n_jobs": 1},
        "search": {
            "ridge": {"alpha": [1.0]},
            "random_forest": {
                "n_estimators": [5],
                "max_depth": [None],
                "min_samples_leaf": [1],
                "max_features": ["sqrt"],
            },
        },
        "prediction": {"clip_predictions": False, "round_predictions": False},
    }


def test_prepare_training_data_applies_privacy_split_and_schema_guards():
    development, manifest = prepared_frames()

    prepared = prepare_training_data(development, manifest)

    assert len(prepared.train) == 24
    assert len(prepared.validation) == 6
    assert "essay-00" not in set(prepared.train["essay_id"])
    assert prepared.feature_columns == FEATURE_NAMES
    assert set(prepared.train["cv_fold"].astype(int)) == set(range(5))
    assert set(prepared.privacy_counts) == {
        "model_train_flagged_by_rater",
        "model_train_not_flagged",
        "validation_not_flagged",
    }


def test_prepare_training_data_rejects_metadata_mismatch_and_test_rows():
    development, manifest = prepared_frames()
    manifest.loc[1, "split"] = "validation"
    with pytest.raises(ValueError, match="metadata does not match"):
        prepare_training_data(development, manifest)

    development, manifest = prepared_frames()
    development.loc[0, "split"] = "official_test"
    manifest.loc[0, "split"] = "official_test"
    development.loc[0, "source_partition"] = "official_test"
    manifest.loc[0, "source_partition"] = "official_test"
    with pytest.raises(ValueError, match="official-test"):
        prepare_training_data(development, manifest)

    development, manifest = prepared_frames()
    with pytest.raises(ValueError, match="privacy gate"):
        prepare_training_data(development, manifest, eligible_status="flagged_by_rater")


def test_train_save_and_reload_four_models(tmp_path):
    development, manifest = prepared_frames()
    result = train_models(
        development,
        manifest,
        ridge_config={"alpha": 1.0},
        random_forest_config={
            "n_estimators": 5,
            "max_depth": None,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "random_seed": 42,
            "n_jobs": 1,
        },
        training_config=tiny_training_config(),
    )

    assert set(result.models) == {
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    }
    assert len(result.cv_results) == 4
    assert len(result.validation_predictions) == 6
    assert list(result.validation_predictions.columns) == [
        "essay_id",
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    ]
    assert not {"Vocabulary", "Grammar"}.intersection(result.validation_predictions.columns)
    assert "essay-00" not in set(result.validation_predictions["essay_id"])
    assert result.summary["official_test_loaded"] is False
    assert result.summary["model_train_rows"] == 24
    assert result.summary["validation_rows"] == 6

    manifest_path = save_training_result(
        result,
        tmp_path,
        run_metadata={
            "development_sha256": "abc",
            "split_sha256": "def",
            "python_version": "3.14.test",
            "package_versions": {"scikit-learn": "test"},
            "code_version": {"source_tree_sha256": "code"},
            "config_version": {"config_set_sha256": "config"},
        },
    )
    artifact_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert set(artifact_manifest["model_files"]) == set(result.models)
    assert (tmp_path / "cv_results.csv").is_file()
    assert (tmp_path / "validation_predictions.csv").is_file()
    assert not (tmp_path / "validation_metrics.csv").exists()
    assert joblib.load(tmp_path / artifact_manifest["model_files"]["ridge_vocabulary"])

    models, feature_columns, metadata = load_model_artifacts(tmp_path)
    assert set(models) == set(result.models)
    assert feature_columns == FEATURE_NAMES
    assert metadata["official_test_loaded"] is False
    assert set(metadata["model_metadata"]) == set(result.models)
    for model_name, model_info in metadata["model_metadata"].items():
        assert model_info["feature_columns"] == list(FEATURE_NAMES)
        assert model_info["feature_count"] == 14
        assert model_info["eligible_fit_rows"] == 24
        assert model_info["cv"]["splitter"] == "PredefinedSplit"
        assert model_info["cv"]["folds"] == 5
        assert model_info["python_version"] == "3.14.test"
        assert model_info["code_version"]["source_tree_sha256"] == "code"
        assert model_info["config_version"]["config_set_sha256"] == "config"
        assert model_info["target"] in {"Vocabulary", "Grammar"}
        assert model_info["family"] in {"ridge", "random_forest"}

    prepared = prepare_training_data(development, manifest)
    validation_x = prepared.validation.loc[:, list(FEATURE_NAMES)]
    saved_predictions = pd.read_csv(tmp_path / "validation_predictions.csv")
    for model_name, model in models.items():
        np.testing.assert_allclose(
            model.predict(validation_x),
            saved_predictions[model_name].to_numpy(),
            rtol=0,
            atol=1e-10,
        )


def test_train_models_keeps_vocabulary_and_grammar_targets_separate():
    development, manifest = prepared_frames()
    base = train_models(
        development,
        manifest,
        ridge_config={"alpha": 1.0},
        random_forest_config={
            "n_estimators": 5,
            "max_depth": None,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "random_seed": 42,
            "n_jobs": 1,
        },
        training_config=tiny_training_config(),
    )

    vocabulary_changed = development.copy()
    vocabulary_changed["Vocabulary"] += 0.25
    vocabulary_result = train_models(
        vocabulary_changed,
        manifest,
        ridge_config={"alpha": 1.0},
        random_forest_config={
            "n_estimators": 5,
            "max_depth": None,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "random_seed": 42,
            "n_jobs": 1,
        },
        training_config=tiny_training_config(),
    )
    np.testing.assert_allclose(
        base.validation_predictions["ridge_grammar"],
        vocabulary_result.validation_predictions["ridge_grammar"],
    )
    assert not np.allclose(
        base.validation_predictions["ridge_vocabulary"],
        vocabulary_result.validation_predictions["ridge_vocabulary"],
    )

    grammar_changed = development.copy()
    grammar_changed["Grammar"] += 0.25
    grammar_result = train_models(
        grammar_changed,
        manifest,
        ridge_config={"alpha": 1.0},
        random_forest_config={
            "n_estimators": 5,
            "max_depth": None,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "random_seed": 42,
            "n_jobs": 1,
        },
        training_config=tiny_training_config(),
    )
    np.testing.assert_allclose(
        base.validation_predictions["ridge_vocabulary"],
        grammar_result.validation_predictions["ridge_vocabulary"],
    )
    assert not np.allclose(
        base.validation_predictions["ridge_grammar"],
        grammar_result.validation_predictions["ridge_grammar"],
    )
