import spacy

from mla_project.features.build_features import FeatureExtractor
from mla_project.pipelines.inference_pipeline import predict_essay


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
