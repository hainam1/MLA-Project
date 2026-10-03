"""Simple comparison baseline."""

from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def build_mean_baseline() -> Pipeline:
    """Build a train-only mean-score baseline."""
    return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", DummyRegressor())])
