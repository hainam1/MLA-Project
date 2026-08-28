from pathlib import Path

import pytest
import yaml

from src.artifacts.build_manifest import verify_manifest


def test_config_matches_primary_contracts():
    config = yaml.safe_load(Path("configs/config.yaml").read_text(encoding="utf-8"))
    assert config["project"]["cefr_levels"] == ["A1", "A2", "B1", "B2", "C1"]
    assert config["model2a"]["split"]["group"] == "word"
    assert config["model3a"]["status"] == "trained_and_integrated"
    assert config["model3b"]["status"] == "trained_and_integrated"
    assert config["model3b"]["supported_directions"] == ["simplify", "preserve"]
    assert config["model3b"]["unsupported_direction"] == "upgrade"
    assert config["model4"]["status"] == "awaiting_human_review"
    assert config["model4"]["training_ready"] is False
    assert config["pipeline"]["input_contract"] == "vietnamese_vocabulary_only"
    assert config["pipeline"]["target_level_required"] is True
    assert config["pipeline"]["sentence_rewriting_enabled"] is False


@pytest.mark.integration
def test_artifact_manifest_is_current():
    assert verify_manifest(Path("artifacts/manifest.json")) == []
