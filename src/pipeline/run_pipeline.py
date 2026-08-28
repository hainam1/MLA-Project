"""CapyVocab vocabulary pipeline: Vietnamese lexical item -> target-level English word."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.example_generator import ExampleGeneratorService
from src.models.translator import TranslatorService
from src.pipeline.input_type_detector import validate_vocabulary_input
from src.pipeline.lexical_retriever import LexicalCandidate, VietnameseEnglishLexicon
from src.pipeline.predict_cefr import CEFRInferenceEngine, CEFR_LEVELS
from src.pipeline.vocabulary_candidates import (
    expand_with_wordnet,
    infer_part_of_speech,
    normalize_to_lemma,
    wordnet_related,
)
from src.runtime import configure_logging

CONTROLLED_TEMPLATES = {
    "ADJ": [
        "This is {word}.",
        "I think the result is {word}.",
        "The result seemed {word} after our review.",
        "After reviewing the evidence, the committee concluded that the result was {word}.",
        "Having evaluated the evidence comprehensively, the committee deemed the final result {word}.",
    ],
    "NOUN": [
        "The {word} is here.",
        "We often talk about the {word} at school.",
        "The class discussed the {word} because it was important.",
        "During the meeting, the group discussed {word} from several perspectives.",
        "The committee examined the implications of the {word} comprehensively before reaching a nuanced conclusion.",
    ],
    "VERB": [
        "We {word} every day.",
        "They decided to {word} after school.",
        "The students agreed to {word} after they discussed the problem.",
        "After reviewing the situation carefully, the team decided to {word}.",
        "Having evaluated every available option, the committee resolved to {word} without further delay.",
    ],
    "ADV": [
        "They worked {word}.",
        "She completed the task {word} yesterday.",
        "The team worked {word} because the deadline was close.",
        "Although the task was demanding, the team worked {word} throughout the project.",
        "Despite the considerable pressure, the specialists worked {word} and maintained rigorous standards.",
    ],
}


def build_controlled_examples(word: str, part_of_speech: str | None) -> list[dict]:
    """Create grammatical fallbacks spanning A1-C1 sentence complexity."""
    templates = CONTROLLED_TEMPLATES.get(str(part_of_speech or "").upper())
    if templates is None:
        templates = CONTROLLED_TEMPLATES["NOUN"]
    return [
        {
            "status": "success",
            "target_word": word,
            "target_level": level,
            "sentence": template.format(word=word),
            "lexical_constraint_satisfied": True,
            "constraint_strategy": "controlled_cefr_template",
            "model": "Controlled template + Model 2b verifier",
        }
        for level, template in zip(CEFR_LEVELS, templates)
    ]


def is_complete_example(sentence: str) -> bool:
    text = str(sentence).strip()
    words = [word.casefold() for word in text.rstrip(".!?").split()]
    return bool(
        len(words) >= 3
        and text[0].isupper()
        and text[-1] in ".!?"
        and not any(
            left.strip(",;:") == right.strip(",;:") for left, right in zip(words, words[1:])
        )
    )


class CapyVocabPipeline:
    """Select and verify English vocabulary at a user-requested CEFR level."""

    def __init__(
        self,
        translator=None,
        cefr_engine=None,
        example_generator=None,
        sentence_rewriter=None,
        lexical_retriever=None,
        device: str = "auto",
    ):
        self.translator = translator or TranslatorService(device=device)
        self.cefr_engine = cefr_engine or CEFRInferenceEngine()
        self.example_generator = example_generator
        self.lexical_retriever = lexical_retriever or VietnameseEnglishLexicon(device=device)
        # Kept in the signature for compatibility with older integrations. It is
        # deliberately unused by the vocabulary-only serving contract.
        self.sentence_rewriter = sentence_rewriter
        self.device = device

    def _get_example_generator(self):
        if self.example_generator is None:
            self.example_generator = ExampleGeneratorService(device=self.device)
        return self.example_generator

    @staticmethod
    def _normalize_level(target_level: str | None) -> str | None:
        level = str(target_level or "").strip().upper()
        return level if level in CEFR_LEVELS else None

    def _translation_candidates(self, source: str) -> tuple[list[LexicalCandidate], str]:
        """Resolve meaning and POS before target CEFR is ever consulted."""
        dictionary_candidates = self.lexical_retriever.retrieve(source)
        if hasattr(self.translator, "translate_candidates"):
            raw_translations = self.translator.translate_candidates(source)
        else:
            raw_translations = [self.translator.translate(source)]
        cleaned = [
            str(candidate).strip() for candidate in raw_translations if str(candidate).strip()
        ]
        if not cleaned:
            raise RuntimeError("Translator did not produce a vocabulary candidate")
        semantic_anchor = normalize_to_lemma(cleaned[0])
        # WordNet is candidate generation only. Every generated term must pass
        # bilingual dictionary/E5 validation before it reaches CEFR.
        generated = expand_with_wordnet(
            [semantic_anchor],
            max_candidates=50,
            part_of_speech=infer_part_of_speech(semantic_anchor),
        )
        validated = self.lexical_retriever.validate_english_candidates(
            source, [*cleaned, *generated]
        )
        merged: dict[tuple[str, str | None, str], LexicalCandidate] = {}
        for candidate in [*dictionary_candidates, *validated]:
            key = (candidate.lemma.casefold(), candidate.part_of_speech, candidate.sense_id)
            previous = merged.get(key)
            if previous is None or candidate.relevance_score > previous.relevance_score:
                merged[key] = candidate
        ranked = sorted(merged.values(), key=lambda item: (-item.relevance_score, item.lemma))
        if not ranked:
            raise RuntimeError("No English candidate passed bilingual semantic validation")
        # The semantic floor is established independently of CEFR. Candidates
        # below it cannot be resurrected merely because their CEFR is convenient.
        max_lexical = max(item.lexical_score for item in ranked)
        max_semantic = max(item.semantic_score for item in ranked)
        max_relevance = ranked[0].relevance_score
        english_anchor = ranked[0].lemma
        reranker = getattr(self.lexical_retriever, "semantic_reranker", None)
        english_scores = (
            reranker.score(english_anchor, [item.lemma for item in ranked])
            if reranker is not None
            else [1.0] * len(ranked)
        )
        filtered = [
            item
            for item, english_score in zip(ranked, english_scores)
            if (
                item.translation_rank == 0
                or item.lexical_score
                >= max_lexical
                - (0.15 if item.source.startswith("Marian candidate validated") else 0.06)
            )
            and (max_semantic == 0.0 or item.semantic_score >= max_semantic - 0.07)
            and item.relevance_score >= max_relevance - 0.15
            and (wordnet_related(english_anchor, item.lemma) or english_score >= 0.88)
        ]
        return filtered, semantic_anchor

    def _predict_candidate(self, candidate: LexicalCandidate) -> dict:
        if hasattr(self.cefr_engine, "predict_vocabulary"):
            try:
                return self.cefr_engine.predict_vocabulary(
                    candidate.lemma, part_of_speech=candidate.part_of_speech
                )
            except TypeError:
                return self.cefr_engine.predict_vocabulary(candidate.lemma)
        return self.cefr_engine.predict(candidate.lemma, route_override="word_mode")

    def _select_vocabulary(
        self, candidates: list[LexicalCandidate], target_level: str
    ) -> tuple[dict, dict]:
        analyses = []
        for rank, candidate in enumerate(candidates):
            cefr = self._predict_candidate(candidate)
            if cefr.get("status") != "success":
                continue
            target_probability = float(cefr.get("probabilities", {}).get(target_level, 0.0))
            authoritative = cefr.get("model") == "CEFR Wordlist Exact Lookup"
            predicted_level = cefr.get("predicted_level")
            distance = (
                abs(CEFR_LEVELS.index(predicted_level) - CEFR_LEVELS.index(target_level))
                if predicted_level in CEFR_LEVELS
                else len(CEFR_LEVELS)
            )
            analyses.append((candidate, cefr, rank, target_probability, authoritative, distance))
        if not analyses:
            raise RuntimeError("No valid English vocabulary candidate could be classified")

        authoritative_exact = [
            item for item in analyses if item[4] and item[1].get("predicted_level") == target_level
        ]
        if authoritative_exact:
            selected = max(
                authoritative_exact,
                key=lambda item: (item[0].relevance_score, item[3], -item[2]),
            )
        else:
            # No semantic candidate is known at the requested CEFR. Preserve
            # meaning and prefer a lexicon-backed lemma/POS over an unverified
            # classifier estimate. Requested-level distance is intentionally
            # absent, so CEFR cannot pull the result toward another meaning.
            selected = max(analyses, key=lambda item: (item[4], item[0].relevance_score, -item[2]))
        candidate, cefr, rank, target_probability, authoritative, _ = selected
        estimated_match = cefr.get("predicted_level") == target_level
        target_match = bool(estimated_match and authoritative)
        if target_match:
            selection_status = "verified_wordlist_match"
        else:
            selection_status = "no_exact_level_match"
        verified_levels = sorted(
            {
                item[1].get("predicted_level")
                for item in analyses
                if item[4] and item[1].get("predicted_level") in CEFR_LEVELS
            },
            key=CEFR_LEVELS.index,
        )
        selection = {
            "word": candidate.lemma,
            "lemma": candidate.lemma,
            "part_of_speech": candidate.part_of_speech,
            "sense_id": candidate.sense_id,
            "vietnamese_gloss": candidate.vietnamese_gloss,
            "semantic_source": candidate.source,
            "semantic_relevance": candidate.relevance_score,
            "requested_level": target_level,
            "predicted_level": cefr.get("predicted_level"),
            "target_match": target_match,
            "cefr_estimate_matches_request": estimated_match,
            "exact_level_available": target_level in verified_levels,
            "available_verified_levels": verified_levels,
            "selection_status": selection_status,
            "target_probability": round(target_probability, 2),
            "verification_source": cefr.get("model"),
            "candidates_evaluated": len(analyses),
            "needs_review": bool(cefr.get("needs_review", False) or not target_match),
        }
        return selection, cefr

    def _generate_verified_example(
        self, word: str, target_level: str, part_of_speech: str | None = None
    ) -> dict:
        generator = self._get_example_generator()
        if hasattr(generator, "generate_candidates"):
            candidates = generator.generate_candidates(word, target_level)
        else:
            candidates = [generator.generate(word, target_level)]
        candidates = [*build_controlled_examples(word, part_of_speech), *candidates]

        verified = []
        for rank, example in enumerate(candidates):
            if (
                example.get("status") != "success"
                or not example.get("lexical_constraint_satisfied", False)
                or not is_complete_example(example.get("sentence", ""))
            ):
                continue
            cefr = self.cefr_engine.predict(
                example.get("sentence", ""), route_override="sentence_mode"
            )
            if cefr.get("status") != "success":
                continue
            probability = float(cefr.get("probabilities", {}).get(target_level, 0.0))
            verified.append((example, cefr, rank, probability))
        if not verified:
            raise RuntimeError("No generated example passed lexical and CEFR verification")

        exact = [item for item in verified if item[1].get("predicted_level") == target_level]
        controlled_exact = [
            item
            for item in exact
            if item[0].get("constraint_strategy") == "controlled_cefr_template"
        ]
        pool = controlled_exact or exact or verified
        example, cefr, _, probability = max(pool, key=lambda item: (item[3], -item[2]))
        result = dict(example)
        result["cefr_verification"] = cefr
        result["level_match"] = cefr.get("predicted_level") == target_level
        result["target_probability"] = round(probability, 2)
        result["needs_review"] = bool(cefr.get("needs_review", False) or not result["level_match"])
        return result

    def process(self, vietnamese_vocabulary: str, target_level: str | None = None) -> dict:
        source = str(vietnamese_vocabulary or "").strip()
        valid, message = validate_vocabulary_input(source)
        if not valid:
            return {"status": "error", "input_vi": source, "message": message}
        level = self._normalize_level(target_level)
        if level is None:
            return {
                "status": "error",
                "input_vi": source,
                "message": "target_level is required and must be one of A1, A2, B1, B2, C1.",
            }

        try:
            candidates, baseline_translation = self._translation_candidates(source)
            selection, cefr = self._select_vocabulary(candidates, level)
            example = self._generate_verified_example(
                selection["word"],
                level,
                selection.get("part_of_speech") or cefr.get("part_of_speech"),
            )
        except (OSError, RuntimeError, ValueError) as error:
            return {
                "status": "error",
                "input_vi": source,
                "requested_level": level,
                "message": str(error),
            }

        return {
            "status": "success",
            "input_vi": source,
            "route": "word_mode",
            "requested_level": level,
            "baseline_translation_en": baseline_translation,
            "translation_en": selection["word"],
            "meaning_analysis": {
                "status": (
                    "ambiguous"
                    if len({item.part_of_speech for item in candidates}) > 1
                    else "resolved"
                ),
                "needs_clarification": len({item.part_of_speech for item in candidates}) > 1,
                "semantic_floor_applied": True,
                "candidates": [item.to_dict() for item in candidates[:10]],
            },
            "selected_vocabulary": selection,
            "cefr": cefr,
            "generated_example": example,
            "capabilities": {
                "translation": True,
                "target_level_selection": True,
                "cefr_verification": True,
                "example_generation": True,
                "sentence_rewriting": False,
                "quality_verification": False,
            },
        }


def run_interactive(pipeline: CapyVocabPipeline) -> None:
    print("CapyVocab — Vietnamese vocabulary to target-level English vocabulary")
    while True:
        source = input("Vietnamese vocabulary (or 'q' to quit): ").strip()
        if source.lower() in {"q", "quit", "exit"}:
            break
        level = input("Target CEFR level (A1/A2/B1/B2/C1): ").strip()
        print(json.dumps(pipeline.process(source, level), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vocabulary", nargs="?", help="Vietnamese vocabulary item (up to 3 words)")
    parser.add_argument("--target-level", choices=CEFR_LEVELS, help="Required target CEFR level")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()

    configure_logging()
    pipeline = CapyVocabPipeline(device=args.device)
    if args.interactive or not args.vocabulary:
        run_interactive(pipeline)
    elif not args.target_level:
        parser.error("--target-level is required when vocabulary is provided")
    else:
        print(
            json.dumps(
                pipeline.process(args.vocabulary, args.target_level),
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
