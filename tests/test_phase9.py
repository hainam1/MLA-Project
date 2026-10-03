from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mla_project.evaluation.phase9 import (
    ERROR_THRESHOLDS,
    EXPECTED_ELIGIBLE_ROWS,
    EXPECTED_TOTAL_ROWS,
    REFERENCE_PREDICTORS,
    REVIEW_BUDGETS,
    RIDGE_CENTERS,
    VALIDATION_DISAGREEMENT_THRESHOLD,
    add_frozen_test_signals,
    prepare_official_population,
    primary_review_count,
)
from mla_project.features.build_features import FEATURE_NAMES

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def synthetic_official_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ids = pd.Series([f"e{index:04d}" for index in range(EXPECTED_TOTAL_ROWS)], dtype="string")
    features = pd.DataFrame({"essay_id": ids})
    for feature in FEATURE_NAMES:
        features[feature] = 1.0
    labels = pd.DataFrame(
        {
            "essay_id": ids,
            "Vocabulary": 3.0,
            "Grammar": 3.0,
            "gender": "group",
            "race_ethnicity": "group",
            "SES": "group",
        }
    )
    manifest = pd.DataFrame(
        {
            "essay_id": ids,
            "split": "official_test",
            "privacy_review_status": ["not_flagged"] * EXPECTED_ELIGIBLE_ROWS
            + ["flagged_by_rater"] * (EXPECTED_TOTAL_ROWS - EXPECTED_ELIGIBLE_ROWS),
        }
    )
    return features, labels, manifest


def test_official_test_eligibility_count_is_frozen():
    features, labels, manifest = synthetic_official_sources()
    population = prepare_official_population(features, labels, manifest)
    assert len(population) == 2_518
    assert population["essay_id"].nunique() == 2_518
    assert np.isfinite(population[list(FEATURE_NAMES)].to_numpy(dtype=float)).all()


def test_phase6_model_artifact_hashes_match_protocol():
    expected = {
        "ridge_vocabulary.joblib": "14591A1822FFA4FC7C9006A5ABD270928401721739BEA3F9FE5A76852780EF64",
        "ridge_grammar.joblib": "812885CAAB21DAC6508835C83DC91DE75B23D622577BA15A8E37E207E59B085F",
        "random_forest_vocabulary.joblib": "899E9283E2EB01B4DF6913EADD6CF8A4A823DF0298DDFE820D14BA5912FFE7BE",
        "random_forest_grammar.joblib": "BC285A202DE126247240982696CA94C16DBEE82BF15906D8E75EBDF4405A8F91",
    }
    for filename, expected_hash in expected.items():
        assert sha256(ROOT / "outputs" / "phase6" / filename) == expected_hash


def test_phase9_has_no_training_operation():
    import scripts.phase9_official_test_evaluation as phase9_script

    source = inspect.getsource(phase9_script)
    assert ".fit(" not in source
    assert "GridSearchCV" not in source
    assert "train_models" not in source


def test_frozen_references_centers_threshold_budget_and_sensitivities():
    assert REFERENCE_PREDICTORS == {
        "Vocabulary": "random_forest_vocabulary",
        "Grammar": "random_forest_grammar",
    }
    assert RIDGE_CENTERS == {
        "median_ridge_vocabulary": 3.26941940240918,
        "median_ridge_grammar": 3.124225726952784,
    }
    assert VALIDATION_DISAGREEMENT_THRESHOLD == 0.133989655155
    assert primary_review_count() == 504
    assert set(ERROR_THRESHOLDS) == {0.5, 1.0, 1.5}
    assert set(REVIEW_BUDGETS) == {0.1, 0.2, 0.3}
    assert (
        len({(threshold, budget) for threshold in ERROR_THRESHOLDS for budget in REVIEW_BUDGETS})
        == 9
    )


def test_large_error_rule_is_inclusive_and_rf_based():
    frame = pd.DataFrame(
        {
            "Vocabulary": [3.0, 3.0],
            "Grammar": [3.0, 3.0],
            "ridge_vocabulary": [5.0, 5.0],
            "ridge_grammar": [5.0, 5.0],
            "random_forest_vocabulary": [4.0, 3.9],
            "random_forest_grammar": [3.0, 3.0],
        }
    )
    result = add_frozen_test_signals(frame)
    assert result["large_error"].tolist() == [True, False]


def test_validation_rows_are_rejected_from_official_population():
    features, labels, manifest = synthetic_official_sources()
    manifest.loc[0, "split"] = "validation"
    with pytest.raises(ValueError, match="2,571-ID population"):
        prepare_official_population(features, labels, manifest)


def test_generated_manifest_records_one_time_separation_when_available():
    path = ROOT / "docs" / "data" / "phase9_tables" / "artifact_manifest.json"
    if not path.exists():
        pytest.skip("Phase 9 has not run yet; artifact-only assertion is post-run.")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["one_time_official_test_evaluation"] is True
    assert manifest["models_retrained"] is False
    assert manifest["eligible_rows"] == 2_518
