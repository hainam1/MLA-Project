"""Build and maintain a human-review queue from real held-out model outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUEUE = PROJECT_ROOT / "data/review/model4_failure_candidates.csv"
DEFAULT_SUMMARY = PROJECT_ROOT / "data/review/model4_review_summary.json"
REVIEW_CATEGORIES = {
    "lexical_constraint",
    "cefr_mismatch",
    "meaning_loss",
    "no_simplification",
    "fluency",
    "repetition",
    "other",
}
COLUMNS = [
    "candidate_id",
    "model",
    "task",
    "split",
    "source_text",
    "control",
    "model_output",
    "expected_level",
    "predicted_level",
    "automatic_reasons",
    "automatic_metrics",
    "candidate_source",
    "review_status",
    "human_verdict",
    "failure_category",
    "reviewer",
    "reviewer_notes",
    "reviewed_at",
]


def stable_candidate_id(model: str, source: str, control: str, output: str) -> str:
    payload = "\x1f".join([model, source, control, output]).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _pending_record(
    *,
    model: str,
    task: str,
    source: str,
    control: str,
    output: str,
    expected_level: str,
    predicted_level: str | None,
    reasons: list[str],
    metrics: dict,
) -> dict:
    return {
        "candidate_id": stable_candidate_id(model, source, control, output),
        "model": model,
        "task": task,
        "split": "test",
        "source_text": source,
        "control": control,
        "model_output": output,
        "expected_level": expected_level,
        "predicted_level": predicted_level or "",
        "automatic_reasons": "|".join(sorted(set(reasons))),
        "automatic_metrics": json.dumps(metrics, ensure_ascii=False, sort_keys=True),
        "candidate_source": "held_out_test_metadata_sample",
        "review_status": "pending",
        "human_verdict": "",
        "failure_category": "",
        "reviewer": "",
        "reviewer_notes": "",
        "reviewed_at": "",
    }


def candidates_from_model3a(metadata: dict) -> list[dict]:
    records = []
    for sample in metadata.get("sample_predictions", []):
        reasons = []
        lexical_ok = bool(sample.get("lexical_constraint_satisfied"))
        if not lexical_ok:
            reasons.append("lexical_constraint")
        if sample.get("predicted_cefr") != sample.get("target_level"):
            reasons.append("cefr_mismatch")
        if not reasons:
            continue
        records.append(
            _pending_record(
                model="model3a",
                task="example_generation",
                source=sample.get("reference", ""),
                control=f"word={sample.get('target_word', '')};level={sample.get('target_level', '')}",
                output=sample.get("prediction", ""),
                expected_level=sample.get("target_level", ""),
                predicted_level=sample.get("predicted_cefr"),
                reasons=reasons,
                metrics={"lexical_constraint_satisfied": lexical_ok},
            )
        )
    return records


def candidates_from_model3b(metadata: dict) -> list[dict]:
    records = []
    for sample in metadata.get("sample_predictions", []):
        reasons = []
        changed = bool(sample.get("rewrite_changed"))
        sari = float(sample.get("sari", 0.0))
        semantic = float(sample.get("semantic_tfidf_cosine", 0.0))
        if sample.get("direction") == "simplify" and not changed:
            reasons.append("no_simplification")
        if sample.get("predicted_level") != sample.get("target_level"):
            reasons.append("cefr_mismatch")
        if sari < 30.0:
            reasons.append("low_sari")
        if semantic < 0.75:
            reasons.append("low_semantic_similarity")
        if not reasons:
            continue
        records.append(
            _pending_record(
                model="model3b",
                task=sample.get("direction", "sentence_rewriting"),
                source=sample.get("source", ""),
                control=f"target_level={sample.get('target_level', '')}",
                output=sample.get("prediction", ""),
                expected_level=sample.get("target_level", ""),
                predicted_level=sample.get("predicted_level"),
                reasons=reasons,
                metrics={
                    "rewrite_changed": changed,
                    "sari": sari,
                    "semantic_tfidf_cosine": semantic,
                },
            )
        )
    return records


def summarize_queue(frame: pd.DataFrame) -> dict:
    reviewed = frame.review_status.eq("reviewed") if len(frame) else pd.Series(dtype=bool)
    failures = frame.human_verdict.eq("failure") if len(frame) else pd.Series(dtype=bool)
    return {
        "total_candidates": int(len(frame)),
        "pending_review": int((~reviewed).sum()),
        "reviewed": int(reviewed.sum()),
        "human_confirmed_failures": int((reviewed & failures).sum()),
        "by_model": {key: int(value) for key, value in frame.model.value_counts().items()},
        "model4_training_ready": bool(reviewed.sum() >= 100 and (reviewed & failures).sum() >= 50),
        "readiness_policy": {"minimum_reviewed": 100, "minimum_confirmed_failures": 50},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_queue(frame: pd.DataFrame, destination: Path = DEFAULT_QUEUE) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False, encoding="utf-8")
    summary = summarize_queue(frame)
    summary_path = destination.with_name("model4_review_summary.json")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def build_review_queue(
    model3a_metadata: Path | None = None,
    model3b_metadata: Path | None = None,
    destination: Path = DEFAULT_QUEUE,
) -> tuple[pd.DataFrame, dict]:
    model3a_path = model3a_metadata or PROJECT_ROOT / "src/models/example_generator/metadata.json"
    model3b_path = model3b_metadata or PROJECT_ROOT / "src/models/sentence_rewriter/metadata.json"
    records = candidates_from_model3a(json.loads(model3a_path.read_text(encoding="utf-8")))
    records.extend(candidates_from_model3b(json.loads(model3b_path.read_text(encoding="utf-8"))))
    frame = pd.DataFrame(records, columns=COLUMNS).drop_duplicates("candidate_id")
    if destination.exists():
        existing = pd.read_csv(destination, keep_default_na=False)
        reviewed = existing[existing.review_status.eq("reviewed")]
        frame = pd.concat([reviewed, frame], ignore_index=True).drop_duplicates(
            "candidate_id", keep="first"
        )
    return frame, write_queue(frame, destination)


def review_candidate(
    queue_path: Path,
    candidate_id: str,
    verdict: str,
    category: str,
    reviewer: str,
    notes: str = "",
) -> dict:
    if verdict not in {"acceptable", "failure"}:
        raise ValueError("verdict must be acceptable or failure")
    if category not in REVIEW_CATEGORIES:
        raise ValueError(f"category must be one of {sorted(REVIEW_CATEGORIES)}")
    if not reviewer.strip():
        raise ValueError("reviewer must not be empty")
    frame = pd.read_csv(queue_path, keep_default_na=False)
    matches = frame.candidate_id.eq(candidate_id)
    if matches.sum() != 1:
        raise ValueError(f"candidate_id must match exactly one row: {candidate_id}")
    frame.loc[matches, "review_status"] = "reviewed"
    frame.loc[matches, "human_verdict"] = verdict
    frame.loc[matches, "failure_category"] = category
    frame.loc[matches, "reviewer"] = reviewer.strip()
    frame.loc[matches, "reviewer_notes"] = notes.strip()
    frame.loc[matches, "reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return write_queue(frame, queue_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--output", type=Path, default=DEFAULT_QUEUE)
    listing = subparsers.add_parser("list")
    listing.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    listing.add_argument("--limit", type=int, default=20)
    review = subparsers.add_parser("review")
    review.add_argument("candidate_id")
    review.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    review.add_argument("--verdict", choices=["acceptable", "failure"], required=True)
    review.add_argument("--category", choices=sorted(REVIEW_CATEGORIES), required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.command == "build":
        _, summary = build_review_queue(destination=args.output)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.command == "list":
        frame = pd.read_csv(args.queue, keep_default_na=False)
        pending = frame[frame.review_status.eq("pending")].head(args.limit)
        print(
            pending[["candidate_id", "model", "automatic_reasons", "model_output"]].to_string(
                index=False
            )
        )
    else:
        summary = review_candidate(
            args.queue,
            args.candidate_id,
            args.verdict,
            args.category,
            args.reviewer,
            args.notes,
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
