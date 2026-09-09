from __future__ import annotations

from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from src.models.sentence_cefr.train import candidate_models


def test_required_model_families_are_knn_and_decision_tree():
    models = candidate_models()

    assert set(models) == {"majority", "knn", "decision_tree"}
    assert isinstance(models["knn"].named_steps["scaler"], StandardScaler)
    assert isinstance(models["knn"].named_steps["classifier"], KNeighborsClassifier)
    assert isinstance(models["decision_tree"].named_steps["classifier"], DecisionTreeClassifier)


def test_both_required_models_produce_five_class_probabilities():
    features = [[0.0], [0.1], [1.0], [1.1], [2.0], [2.1], [3.0], [3.1], [4.0], [4.1]]
    labels = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

    for name in ("knn", "decision_tree"):
        model = candidate_models()[name]
        if name == "knn":
            model.set_params(classifier__n_neighbors=3)
        model.fit(features, labels)
        assert model.predict([[2.05]]).shape == (1,)
        assert model.predict_proba([[2.05]]).shape == (1, 5)
