"""Minimal sentence-only command-line inference for the final project demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib

from src.features import SentenceFeatureExtractor

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1"]


def validate_sentence(text: object) -> str:
    normalized = " ".join(str(text).strip().split())
    if not normalized:
        raise ValueError("Input sentence is empty")
    if not any(character.isalpha() for character in normalized):
        raise ValueError("Input must contain alphabetic text")
    if len(normalized.split()) < 2:
        raise ValueError("Input must be a sentence rather than a single token")
    return normalized


class SentenceCEFRPredictor:
    def __init__(
        self,
        model_path: Path | str = "src/models/sentence_cefr/best_model.joblib",
        metadata_path: Path | str = "src/models/sentence_cefr/metadata.json",
        lexicon_path: Path | str = "data/processed/cefr_wordlist_clean.csv",
    ):
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        if not self.model_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError("Train the sentence CEFR model before running inference")
        self.model = joblib.load(self.model_path)
        self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        lexicon = Path(lexicon_path)
        if self.metadata.get("uses_auxiliary_lexicon", False):
            if not lexicon.exists():
                raise FileNotFoundError(f"Missing required auxiliary lexicon: {lexicon}")
            self.extractor = SentenceFeatureExtractor.from_wordlist(lexicon)
        else:
            self.extractor = SentenceFeatureExtractor({})

    def predict(self, sentence: str) -> dict:
        text = validate_sentence(sentence)
        features = self.extractor.extract(text)[self.metadata["feature_columns"]]
        prediction = int(self.model.predict(features)[0])
        probabilities = self.model.predict_proba(features)[0]
        probability_map = {
            CEFR_LEVELS[int(label)]: round(float(probability), 4)
            for label, probability in zip(self.model.classes_, probabilities)
        }
        return {
            "sentence": text,
            "predicted_level": CEFR_LEVELS[prediction],
            "confidence": probability_map[CEFR_LEVELS[prediction]],
            "probabilities": probability_map,
            "model": self.metadata.get("selected_model", "unknown"),
            "disclaimer": "Estimated sentence difficulty; not an assessment of a learner.",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sentence")
    args = parser.parse_args()
    predictor = SentenceCEFRPredictor()
    print(json.dumps(predictor.predict(args.sentence), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
