import pytest

from mla_project.data.load_data import load_ellipse
from mla_project.data.validate_data import validate_ellipse_schema


def test_validate_schema_returns_numeric_scores_and_trimmed_text(essay_frame):
    essay_frame.loc[0, "essay_text"] = "  A short essay.  "
    validated = validate_ellipse_schema(essay_frame)
    assert validated.loc[0, "essay_text"] == "A short essay."
    assert validated["Vocabulary"].dtype.kind == "f"
    assert validated["Grammar"].dtype.kind == "f"


def test_validate_schema_rejects_duplicate_ids(essay_frame):
    essay_frame.loc[1, "essay_id"] = essay_frame.loc[0, "essay_id"]
    with pytest.raises(ValueError, match="unique"):
        validate_ellipse_schema(essay_frame)


def test_validate_schema_rejects_missing_required_column(essay_frame):
    with pytest.raises(ValueError, match="missing required"):
        validate_ellipse_schema(essay_frame.drop(columns="Grammar"))


def test_load_dataset_auto_maps_ellipse_columns(tmp_path):
    ellipse_csv = tmp_path / "ellipse_sample.csv"
    ellipse_csv.write_text(
        "text_id_kaggle,full_text,Vocabulary,Grammar,prompt\n"
        "id1,Essay text one.,3.5,3.0,Prompt A\n"
        "id2,Essay text two.,4.0,4.5,Prompt B\n",
        encoding="utf-8",
    )
    loaded = load_ellipse(ellipse_csv)
    assert set(loaded.columns).issuperset(
        {"essay_id", "essay_text", "Vocabulary", "Grammar", "prompt_id"}
    )
    assert len(loaded) == 2
    assert loaded.loc[0, "essay_id"] == "id1"
    assert loaded.loc[0, "Vocabulary"] == 3.5
