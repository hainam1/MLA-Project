import torch  # noqa: F401 - Initialize torch OpenMP/C++ runtime before third-party C-extensions

import argparse
import json
import logging
import re
import unicodedata
from pathlib import Path

import joblib
import pandas as pd
import wordfreq

from src.features import SentenceFeatureExtractor, extract_word_features
from src.pipeline.input_type_detector import detect_input_type

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1"]
LOGGER = logging.getLogger(__name__)
VN_DIACRITICS_PATTERN = re.compile(
    r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡ" r"ùúụủũưừứựửữỳýỵỷỹđ]",
    re.IGNORECASE,
)
VN_UNACCENTED_MARKERS = {
    "toi",
    "tao",
    "minh",
    "ban",
    "chung",
    "la",
    "rat",
    "dep",
    "trai",
    "gai",
    "nguoi",
    "viet",
    "nam",
    "khong",
    "ko",
    "duoc",
    "cua",
    "mot",
    "nhung",
    "nay",
    "sao",
    "khi",
    "den",
    "vao",
    "nhu",
    "dang",
    "roi",
    "chua",
    "phai",
    "biet",
    "muon",
    "thay",
    "lam",
    "hoc",
    "hieu",
    "anh",
    "em",
    "ong",
    "ba",
    "con",
    "cai",
    "nhe",
    "nha",
    "troi",
}


def detect_language(text: str) -> tuple[bool, str, str]:
    """Conservative English gate; ambiguous English function words are allowed."""
    normalized = unicodedata.normalize("NFC", str(text).strip())
    if not normalized:
        return False, "Chuỗi rỗng", "unknown"
    if VN_DIACRITICS_PATTERN.search(normalized):
        return False, "Phát hiện ký tự / dấu thanh tiếng Việt", "vietnamese"

    words = re.findall(r"\b[a-zA-Z]+\b", normalized.lower())
    if not words:
        return False, "Không chứa ký tự chữ cái hợp lệ", "unknown"
    marker_count = sum(word in VN_UNACCENTED_MARKERS for word in words)
    if marker_count >= 2 and marker_count / len(words) >= 0.4:
        return (
            False,
            f"Phát hiện cấu trúc tiếng Việt không dấu ({marker_count}/{len(words)} từ)",
            "vietnamese",
        )
    if len(words) == 1 and words[0] in VN_UNACCENTED_MARKERS:
        return False, "Phát hiện từ tiếng Việt không dấu", "vietnamese"

    english_oov = sum(wordfreq.zipf_frequency(word, "en") == 0 for word in words)
    if len(words) >= 3 and english_oov / len(words) >= 0.6:
        return False, "Đa số từ không có trong từ điển tiếng Anh", "non_english"
    return True, "Hợp lệ", "english"


class CEFRInferenceEngine:
    """Load both CEFR models once and provide deterministic predictions."""

    def __init__(
        self,
        model2a_path: Path | str | None = None,
        model2b_path: Path | str | None = None,
        wordlist_path: Path | str | None = None,
    ):
        model2a_path = Path(
            model2a_path or PROJECT_ROOT / "src/models/cefr_word_classifier/model.pkl"
        )
        model2b_path = Path(
            model2b_path or PROJECT_ROOT / "src/models/cefr_sentence_classifier/model.pkl"
        )
        wordlist_path = Path(
            wordlist_path or PROJECT_ROOT / "data/processed/cefr_wordlist_clean.csv"
        )
        missing = [
            path for path in (model2a_path, model2b_path, wordlist_path) if not path.exists()
        ]
        if missing:
            raise FileNotFoundError(f"Missing inference artifacts: {missing}")

        # joblib/pickle is trusted only because these files are locally produced.
        self.model2a = joblib.load(model2a_path)
        self.model2b = joblib.load(model2b_path)
        self.model2a_metadata = json.loads(
            model2a_path.with_name("metadata.json").read_text(encoding="utf-8")
        )
        self.model2b_metadata = json.loads(
            model2b_path.with_name("metadata.json").read_text(encoding="utf-8")
        )
        wordlist = pd.read_csv(wordlist_path, usecols=["word", "pos", "cefr_level"])
        self.word_entries_lookup: dict[str, list[dict[str, str]]] = {}
        for row in wordlist.itertuples(index=False):
            key = str(row.word).casefold()
            entry = {
                "part_of_speech": str(row.pos).upper(),
                "cefr_level": str(row.cefr_level).upper(),
            }
            if entry not in self.word_entries_lookup.setdefault(key, []):
                self.word_entries_lookup[key].append(entry)
        self.review_thresholds = {
            "word_mode": float(
                self.model2a_metadata.get("calibration", {}).get("needs_review_threshold", 0.0)
            ),
            "sentence_mode": float(
                self.model2b_metadata.get("calibration", {}).get("needs_review_threshold", 0.0)
            ),
        }
        self.sentence_extractor = SentenceFeatureExtractor.from_wordlist(wordlist_path)
        LOGGER.info("CEFR models and shared feature extractor are ready")

    def extract_word_features(self, word: str) -> pd.DataFrame:
        return extract_word_features(word)

    def extract_sentence_features(self, sentence: str) -> pd.DataFrame:
        return self.sentence_extractor.extract(sentence)

    def predict_vocabulary(self, word: str, part_of_speech: str | None = None) -> dict:
        """Use an exact lemma+POS CEFR label; never combine unrelated rows."""
        text = str(word).strip()
        entries = (
            self.word_entries_lookup.get(text.casefold(), []) if len(text.split()) == 1 else []
        )
        requested_pos = str(part_of_speech or "").upper() or None
        matching = [item for item in entries if item["part_of_speech"] == requested_pos]
        if requested_pos is None:
            matching = entries
        levels = sorted({item["cefr_level"] for item in matching}, key=CEFR_LEVELS.index)
        level = levels[0] if len(levels) == 1 else None
        if level in CEFR_LEVELS:
            probabilities = {candidate: 0.0 for candidate in CEFR_LEVELS}
            probabilities[level] = 100.0
            return {
                "input": text,
                "status": "success",
                "is_english": True,
                "route": "word_mode",
                "model": "CEFR Wordlist Exact Lookup",
                "predicted_level": level,
                "part_of_speech": requested_pos or matching[0]["part_of_speech"],
                "lexicon_matches": matching,
                "confidence": 100.0,
                "probabilities": probabilities,
                "needs_review": False,
                "confidence_status": "accepted",
                "review_threshold": 100.0,
                "probability_calibration": "not_applicable_exact_lookup",
            }
        result = self.predict(text, route_override="word_mode")
        if result.get("status") == "success":
            result["part_of_speech"] = requested_pos
            result["lexicon_matches"] = matching
            if len(levels) > 1:
                result["needs_review"] = True
                result["confidence_status"] = "ambiguous_lemma_without_pos"
                result["warning"] = "CEFR lookup is ambiguous without a matching part of speech."
        return result

    @staticmethod
    def _probability_payload(model, probabilities) -> dict[str, float]:
        return {
            CEFR_LEVELS[int(label)]: round(float(probability) * 100, 2)
            for label, probability in zip(model.classes_, probabilities)
        }

    def predict(self, user_input: str, route_override: str | None = None) -> dict:
        text = str(user_input).strip()
        if not text:
            return {"input": text, "status": "error", "message": "Văn bản đầu vào rỗng!"}
        is_english, reason, language = detect_language(text)
        if not is_english:
            return {
                "input": text,
                "status": "blocked_non_english",
                "is_english": False,
                "language": language,
                "reason": reason,
            }

        route = route_override or detect_input_type(text)
        if route not in {"word_mode", "sentence_mode"}:
            return {
                "input": text,
                "status": "error",
                "message": f"Unsupported route: {route}",
            }
        if route == "word_mode":
            features = self.extract_word_features(text)
            model = self.model2a
            model_name = "Model 2a (CEFR Word Classifier)"
        else:
            features = self.extract_sentence_features(text)
            model = self.model2b
            model_name = "Model 2b (CEFR Sentence Classifier)"

        prediction = int(model.predict(features)[0])
        probabilities = model.predict_proba(features)[0]
        probability_map = self._probability_payload(model, probabilities)
        predicted_position = list(model.classes_).index(prediction)
        confidence_raw = float(probabilities[predicted_position])
        result = {
            "input": text,
            "status": "success",
            "is_english": True,
            "route": route,
            "model": model_name,
            "predicted_level": CEFR_LEVELS[prediction],
            "confidence": probability_map[CEFR_LEVELS[prediction]],
            "probabilities": probability_map,
        }
        threshold = self.review_thresholds[route]
        result["needs_review"] = confidence_raw < threshold
        result["confidence_status"] = "low_confidence" if result["needs_review"] else "accepted"
        result["review_threshold"] = round(threshold * 100, 2)
        result["probability_calibration"] = "temperature_scaling"
        if route == "word_mode" and len(text.split()) > 1:
            result["warning"] = (
                "Model 2a được huấn luyện trên từ đơn; kết quả cho cụm từ là ngoài "
                "phân phối huấn luyện."
            )
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", default="apple")
    args = parser.parse_args()
    engine = CEFRInferenceEngine()
    print(json.dumps(engine.predict(args.text), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
