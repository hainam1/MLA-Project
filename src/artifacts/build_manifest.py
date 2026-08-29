"""Create a portable SHA-256 manifest for generated model artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATHS = [
    "data/external/vi_en_dictionary/vi_en_dict.db",
    "data/external/nltk_data/corpora/wordnet.zip",
    "src/models/semantic_reranker/checkpoint/config.json",
    "src/models/semantic_reranker/checkpoint/model.safetensors",
    "src/models/semantic_reranker/checkpoint/sentencepiece.bpe.model",
    "src/models/semantic_reranker/checkpoint/special_tokens_map.json",
    "src/models/semantic_reranker/checkpoint/tokenizer.json",
    "src/models/semantic_reranker/checkpoint/tokenizer_config.json",
    "src/models/cefr_word_classifier/model.pkl",
    "src/models/cefr_word_classifier/model_uncalibrated.pkl",
    "src/models/cefr_word_classifier/metadata.json",
    "src/models/cefr_sentence_classifier/model.pkl",
    "src/models/cefr_sentence_classifier/model_uncalibrated.pkl",
    "src/models/cefr_sentence_classifier/metadata.json",
    "src/models/translator/checkpoint-best/config.json",
    "src/models/translator/checkpoint-best/model.safetensors",
    "src/models/translator/checkpoint-best/source.spm",
    "src/models/translator/checkpoint-best/target.spm",
    "src/models/translator/checkpoint-best/vocab.json",
    "src/models/translator/checkpoint-lora-best/adapter_config.json",
    "src/models/translator/checkpoint-lora-best/adapter_model.safetensors",
    "src/models/translator/checkpoint-lora-best/source.spm",
    "src/models/translator/checkpoint-lora-best/target.spm",
    "src/models/translator/checkpoint-lora-best/tokenizer_config.json",
    "src/models/translator/checkpoint-lora-best/vocab.json",
    "src/models/translator/metadata.json",
    "src/models/second_pair_of_eyes/model4_auditor.joblib",
    "src/models/example_generator/checkpoint-best/config.json",
    "src/models/example_generator/checkpoint-best/generation_config.json",
    "src/models/example_generator/checkpoint-best/model.safetensors",
    "src/models/example_generator/checkpoint-best/spiece.model",
    "src/models/example_generator/checkpoint-best/tokenizer.json",
    "src/models/example_generator/checkpoint-best/tokenizer_config.json",
    "src/models/example_generator/metadata.json",
    "src/models/sentence_rewriter/checkpoint-best/config.json",
    "src/models/sentence_rewriter/checkpoint-best/generation_config.json",
    "src/models/sentence_rewriter/checkpoint-best/model.safetensors",
    "src/models/sentence_rewriter/checkpoint-best/spiece.model",
    "src/models/sentence_rewriter/checkpoint-best/tokenizer.json",
    "src/models/sentence_rewriter/checkpoint-best/tokenizer_config.json",
    "src/models/sentence_rewriter/metadata.json",
]

SERVING_ARTIFACT_PATHS = [path for path in ARTIFACT_PATHS if "sentence_rewriter" not in path]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_manifest() -> dict:
    artifacts = []
    for relative in ARTIFACT_PATHS:
        path = PROJECT_ROOT / relative
        if path.exists():
            artifacts.append(
                {
                    "path": relative,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifacts,
    }


def verify_manifest(path: Path) -> list[str]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    failures = []
    for artifact in manifest["artifacts"]:
        candidate = PROJECT_ROOT / artifact["path"]
        if not candidate.exists():
            failures.append(f"missing: {artifact['path']}")
        elif candidate.stat().st_size != artifact["bytes"]:
            failures.append(f"size mismatch: {artifact['path']}")
        elif sha256(candidate) != artifact["sha256"]:
            failures.append(f"hash mismatch: {artifact['path']}")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    destination = PROJECT_ROOT / "artifacts/manifest.json"
    if args.verify:
        failures = verify_manifest(destination)
        if failures:
            raise SystemExit("\n".join(failures))
        print("Artifact manifest verification passed")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(build_manifest(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Wrote artifacts/manifest.json")


if __name__ == "__main__":
    main()
