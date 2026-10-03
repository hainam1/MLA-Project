from mla_project.data.make_splits import make_splits


def test_exact_duplicate_texts_stay_in_one_split(essay_frame):
    essay_frame.loc[1, "essay_text"] = essay_frame.loc[0, "essay_text"]
    splits = make_splits(essay_frame, validation_size=0.25)
    labels = splits.set_index("essay_id")["split"]
    assert labels["e0"] == labels["e1"]
    assert set(labels) == {"model_train", "validation"}
    assert "test" not in set(labels)
