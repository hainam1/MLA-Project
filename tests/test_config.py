from mla_project.utils.config import load_project_config, load_yaml
from mla_project.utils.paths import PROJECT_ROOT


def test_canonical_configs_cover_features_paths_and_models():
    config = load_project_config()
    assert set(config) == {"paths", "features", "ridge", "random_forest"}
    assert config["paths"]["data"]["splits"] == "data/02_split_manifest"
    assert set(config["features"]["groups"]) == {"length", "vocabulary", "grammar", "syntax"}
    assert config["ridge"]["alpha"] > 0
    assert config["random_forest"]["random_seed"] == 42


def test_phase5_baseline_protocol_is_frozen():
    config = load_yaml(PROJECT_ROOT / "configs" / "phase5_baselines.yaml")
    assert config["privacy"]["eligible_status"] == "not_flagged"
    assert config["baselines"]["length_only"]["features"] == [
        "word_count",
        "sentence_count",
        "mean_sentence_length",
    ]
    assert config["baselines"]["length_only"]["random_forest"]["n_jobs"] == 1
    assert config["baselines"]["review"] == {
        "priority_score": "max_target_ridge_rf_disagreement",
        "consensus_prediction": "mean_ridge_random_forest",
        "large_error_threshold": 1.0,
        "review_budget": 0.20,
        "random_repetitions": 1000,
        "random_seed": 42,
    }


def test_phase6_training_protocol_is_frozen():
    config = load_yaml(PROJECT_ROOT / "configs" / "phase6_training.yaml")
    assert config["privacy"]["eligible_status"] == "not_flagged"
    assert config["cv"] == {
        "folds": 5,
        "scoring": "neg_mean_absolute_error",
        "n_jobs": 1,
    }
    assert config["prediction"] == {
        "clip_predictions": False,
        "round_predictions": False,
    }
    assert config["search"]["ridge"]["alpha"] == [0.1, 1.0, 10.0, 100.0, 1000.0]


def test_phase8_reference_predictors_are_random_forests_selected_by_validation_mae():
    config = load_yaml(PROJECT_ROOT / "configs" / "experiment.yaml")
    evaluation = config["evaluation"]
    assert evaluation["reference_prediction"] == "random_forest_per_target"
    assert evaluation["reference_predictor_selection_rule"] == ("lower_validation_mae_per_target")
    assert evaluation["selected_reference_predictors"] == {
        "Vocabulary": "random_forest_vocabulary",
        "Grammar": "random_forest_grammar",
    }
    assert evaluation["random_interval"] == ("empirical_2.5_to_97.5_percentile_reference_interval")
