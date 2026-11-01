"""Read-only frozen-model inference smoke check on synthetic learner text."""

import hashlib
import json
from pathlib import Path

import joblib

from mla_project.features.build_features import load_default_extractor
from mla_project.pipelines.inference_pipeline import predict_essay, prioritize_essay_batch

ROOT = Path(__file__).resolve().parents[1]


def main():
    frozen = json.loads((ROOT / "docs/data/phase9_tables/artifact_manifest.json").read_text())
    models = {}
    for filename, digest in frozen["phase6_model_sha256"].items():
        path = ROOT / "outputs/phase6" / filename
        assert hashlib.sha256(path.read_bytes()).hexdigest().upper() == digest
        models[path.stem] = joblib.load(path)
    columns = json.loads((ROOT / "outputs/phase6/feature_schema.json").read_text())
    extractor = load_default_extractor()
    kwargs = dict(extractor=extractor, models=models, feature_columns=columns)
    try:
        text = "Learning English takes practice. I write every day because it helps me explain my ideas."
        single = predict_essay(text, **kwargs)
        assert single["priority_for_teacher_review"] is None
        assert single["review_priority_score"] == max(single["disagreement"].values())
        assert set(single["scores"]) == {"vocabulary", "grammar"}
        assert all(
            set(scores) == {"ridge", "random_forest", "consensus"}
            for scores in single["scores"].values()
        )
        essays = {f"synthetic-{i:02}": text + " I enjoy reading." * i for i in range(10)}
        ranked = prioritize_essay_batch(essays, review_budget=0.20, **kwargs)
        assert len(ranked) == 10 and sum(row["review_first"] for row in ranked) == 2
        assert ranked == sorted(
            ranked, key=lambda row: (-row["review_priority_score"], row["essay_id"])
        )
        print(
            "PASS: 4 frozen models loaded; real spaCy/LanguageTool extraction; single schema; batch N=10 K=2"
        )
        print(
            json.dumps(
                {
                    "scores": single["scores"],
                    "review_priority_score": single["review_priority_score"],
                },
                indent=2,
            )
        )
    finally:
        extractor.grammar_checker.close()


if __name__ == "__main__":
    main()
