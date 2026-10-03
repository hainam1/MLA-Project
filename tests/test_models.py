from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from mla_project.models.model_selection import build_model_set


def test_four_target_model_pairs_and_preprocessing():
    models = build_model_set({"alpha": 2.0}, {"n_estimators": 5, "random_seed": 7, "n_jobs": 1})
    assert set(models) == {
        "ridge_vocabulary",
        "ridge_grammar",
        "random_forest_vocabulary",
        "random_forest_grammar",
    }
    assert isinstance(models["ridge_vocabulary"].named_steps["model"], Ridge)
    assert isinstance(models["ridge_vocabulary"].named_steps["scaler"], StandardScaler)
    assert isinstance(models["random_forest_grammar"].named_steps["model"], RandomForestRegressor)
    assert models["random_forest_grammar"].named_steps["model"].n_jobs == 1
    assert "scaler" not in models["random_forest_grammar"].named_steps
