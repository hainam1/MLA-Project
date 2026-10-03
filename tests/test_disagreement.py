from mla_project.review.disagreement import model_disagreement, review_priority


def test_disagreement_is_absolute_score_difference():
    assert model_disagreement(2.25, 3.0) == 0.75
    prioritized, reasons = review_priority(0.75, 0.1, threshold=0.75)
    assert prioritized is True
    assert reasons == ["vocabulary model disagreement meets the review threshold"]
