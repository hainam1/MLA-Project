"""Evaluate meaning retrieval separately from CEFR selection."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.models.translator import TranslatorService
from src.pipeline.run_pipeline import CapyVocabPipeline

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def evaluate(gold_path: Path, top_k: int = 5, device: str = "auto") -> dict:
    pipeline = CapyVocabPipeline(
        translator=TranslatorService(device=device),
        cefr_engine=object(),
        example_generator=object(),
        device=device,
    )
    cases = []
    with gold_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        acceptable = {item.casefold() for item in row["acceptable_lemmas"].split("|")}
        candidates, _ = pipeline._translation_candidates(row["vietnamese"])
        predicted = []
        for item in candidates:
            lemma = item.lemma.casefold()
            if lemma not in predicted:
                predicted.append(lemma)
            if len(predicted) >= top_k:
                break
        hit = any(item in acceptable for item in predicted)
        cases.append(
            {
                "vietnamese": row["vietnamese"],
                "acceptable": sorted(acceptable),
                "predicted": predicted,
                "top_1_hit": bool(predicted and predicted[0] in acceptable),
                "top_k_hit": hit,
            }
        )
    hits = sum(item["top_k_hit"] for item in cases)
    top_1_hits = sum(item["top_1_hit"] for item in cases)
    return {
        "metric": f"meaning_retrieval_recall_at_{top_k}",
        "score": round(hits / len(cases), 4) if cases else 0.0,
        "top_1_accuracy": round(top_1_hits / len(cases), 4) if cases else 0.0,
        "top_1_hits": top_1_hits,
        "hits": hits,
        "total": len(cases),
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gold",
        type=Path,
        default=PROJECT_ROOT / "data/evaluation/vocabulary_translation_gold.csv",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(args.gold, args.top_k, args.device)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
