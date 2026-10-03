import numpy as np

from mla_project.models.train_ordinal import CumulativeLogitRegressor


def test_cumulative_logit_regressor_returns_continuous_bounded_scores():
    x = np.arange(30, dtype=float).reshape(10, 3)
    y = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0])
    model = CumulativeLogitRegressor(max_iter=500).fit(x, y)
    prediction = model.predict(x)
    assert prediction.shape == (10,)
    assert np.isfinite(prediction).all()
    assert (prediction >= 1.0).all()
    assert (prediction <= 5.0).all()
