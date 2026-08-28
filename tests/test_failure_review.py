import json

import pandas as pd
import pytest

from src.quality.failure_review import (
    COLUMNS,
    build_review_queue,
    review_candidate,
    stable_candidate_id,
)


def test_candidate_id_is_stable():
    first = stable_candidate_id("model3a", "source", "A2", "output")
    second = stable_candidate_id("model3a", "source", "A2", "output")
    assert first == second
    assert len(first) == 16


def test_build_queue_keeps_human_fields_pending(tmp_path):
    model3a = {
        "sample_predictions": [
            {
                "target_word": "scientific",
                "target_level": "B2",
                "reference": "Scientific work matters.",
                "prediction": "Science matters.",
                "predicted_cefr": "A2",
                "lexical_constraint_satisfied": False,
            }
        ]
    }
    model3b = {"sample_predictions": []}
    path3a, path3b = tmp_path / "3a.json", tmp_path / "3b.json"
    path3a.write_text(json.dumps(model3a), encoding="utf-8")
    path3b.write_text(json.dumps(model3b), encoding="utf-8")
    queue = tmp_path / "queue.csv"
    frame, summary = build_review_queue(path3a, path3b, queue)
    assert list(frame.columns) == COLUMNS
    assert frame.iloc[0].review_status == "pending"
    assert frame.iloc[0].human_verdict == ""
    assert summary["model4_training_ready"] is False


def test_review_candidate_requires_a_real_reviewer(tmp_path):
    queue = tmp_path / "queue.csv"
    pd.DataFrame(
        [
            {
                **{column: "" for column in COLUMNS},
                "candidate_id": "abc",
                "model": "model3a",
                "review_status": "pending",
            }
        ]
    ).to_csv(queue, index=False)
    with pytest.raises(ValueError, match="reviewer"):
        review_candidate(queue, "abc", "failure", "fluency", "")
    summary = review_candidate(queue, "abc", "failure", "fluency", "reviewer-1")
    reviewed = pd.read_csv(queue, keep_default_na=False).iloc[0]
    assert reviewed.review_status == "reviewed"
    assert reviewed.human_verdict == "failure"
    assert summary["reviewed"] == 1
