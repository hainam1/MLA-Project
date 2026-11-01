import spacy
import pytest
import pandas as pd

from mla_project.features.build_features import FeatureExtractor
from mla_project.pipelines.inference_pipeline import predict_essay, prioritize_essay_batch


class ConstantModel:
    def __init__(self, value):
        self.value = value

    def predict(self, features):
        return [self.value]


class NoMatchesChecker:
    def check(self, text):
        return []


def test_inference_output_has_scores_disagreement_and_review_signal():
    models = {
        "ridge_vocabulary": ConstantModel(3.0),
        "random_forest_vocabulary": ConstantModel(4.0),
        "ridge_grammar": ConstantModel(2.5),
        "random_forest_grammar": ConstantModel(2.75),
    }
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    extractor = FeatureExtractor(nlp=nlp, grammar_checker=NoMatchesChecker())
    columns = tuple(extractor.transform_text("A clear sample essay.").keys())
    result = predict_essay(
        "A clear sample essay.",
        extractor=extractor,
        models=models,
        feature_columns=columns,
        review_threshold=0.75,
    )
    assert set(result) == {
        "scores",
        "disagreement",
        "review_priority_score",
        "priority_for_teacher_review",
        "review_reasons",
        "notice",
    }
    assert result["scores"]["vocabulary"]["consensus"] == 3.5
    assert result["scores"]["grammar"]["consensus"] == 2.625
    assert result["disagreement"] == {"vocabulary": 1.0, "grammar": 0.25}
    assert result["review_priority_score"] == 1.0
    assert result["priority_for_teacher_review"] is True
    assert "not an error probability" in result["notice"]


class NumericExtractor:
    def transform(self, texts):
        return pd.DataFrame({"signal": [float(text) for text in texts]})


class SignalModel:
    def predict(self, features):
        return features["signal"].to_numpy()


@pytest.fixture
def batch_kwargs():
    return dict(
        extractor=NumericExtractor(),
        models={
            "ridge_vocabulary": ConstantModel(0),
            "random_forest_vocabulary": SignalModel(),
            "ridge_grammar": ConstantModel(0),
            "random_forest_grammar": ConstantModel(0),
        },
        feature_columns=("signal",),
    )


def test_budget_ranking_is_deterministic_and_matches_frozen_convention(batch_kwargs):
    essays = {str(i): str(i / 10) for i in range(10)}
    ranked = prioritize_essay_batch(essays, **batch_kwargs)
    assert [row["essay_id"] for row in ranked] == [str(i) for i in range(9, -1, -1)]
    assert sum(row["review_first"] for row in ranked) == 2
    assert [row["rank"] for row in ranked] == list(range(1, 11))
    assert ranked == prioritize_essay_batch(dict(reversed(list(essays.items()))), **batch_kwargs)
    assert all(row["priority_for_teacher_review"] is None for row in ranked)


def test_ties_follow_string_id_not_input_order(batch_kwargs):
    ranked = prioritize_essay_batch({"2": "1", "10": "1", "a": "0"}, **batch_kwargs)
    assert [row["essay_id"] for row in ranked] == ["10", "2", "a"]
    assert sum(row["review_first"] for row in ranked) == 1  # ceil(3 * .2)


@pytest.mark.parametrize("budget", [-0.1, 1.1, "0.2", None, True, float("nan"), float("inf")])
def test_invalid_budgets_are_rejected(budget, batch_kwargs):
    with pytest.raises(ValueError, match="review_budget"):
        prioritize_essay_batch({}, review_budget=budget, **batch_kwargs)


def test_empty_and_single_and_boundary_budgets(batch_kwargs):
    assert prioritize_essay_batch({}, **batch_kwargs) == []
    for budget, expected in [(0, False), (0.2, True), (1, True)]:
        row = prioritize_essay_batch({"one": "0.5"}, review_budget=budget, **batch_kwargs)[0]
        assert row["review_first"] is expected
        assert row["review_priority_score"] == 0.5


def test_single_prediction_defaults_to_score_without_threshold_flag(batch_kwargs):
    result = predict_essay("0.4", **batch_kwargs)
    assert result["priority_for_teacher_review"] is None
    assert result["review_reasons"] == []
    assert result["scores"]["vocabulary"] == {"ridge": 0, "random_forest": 0.4, "consensus": 0.2}
    assert result["disagreement"] == {"vocabulary": 0.4, "grammar": 0}


def test_batch_priority_uses_maximum_across_both_targets(batch_kwargs):
    batch_kwargs["models"]["random_forest_grammar"] = ConstantModel(0.7)
    ranked = prioritize_essay_batch({"a": "0.1", "b": "0.9"}, **batch_kwargs)
    assert [(r["essay_id"], r["review_priority_score"]) for r in ranked] == [("b", 0.9), ("a", 0.7)]


@pytest.mark.parametrize("essays", [{1: "1"}, {"": "1"}, {"a": None}, ["text"]])
def test_batch_rejects_ambiguous_ids_or_invalid_text(essays, batch_kwargs):
    with pytest.raises(ValueError):
        prioritize_essay_batch(essays, **batch_kwargs)
