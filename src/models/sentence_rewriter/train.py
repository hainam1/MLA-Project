"""Train and evaluate Model 3b for simplification and level preservation."""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8")
import argparse
import json
import math
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, get_linear_schedule_with_warmup

# Import Torch/Transformers before NumPy-backed NLP libraries on Windows to avoid
# loading incompatible OpenMP runtimes in the opposite order.
import numpy as np
import pandas as pd
import textstat
from rouge_score import rouge_scorer
from sklearn.feature_extraction.text import TfidfVectorizer

from src.models.sentence_rewriter.service import build_prompt, normalize_generated_text
from src.pipeline.predict_cefr import CEFRInferenceEngine
from src.runtime.hardware import select_device

BASE_MODEL = "google/flan-t5-small"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = Path(__file__).resolve().parent
CHECKPOINT_DIR = MODEL_DIR / "checkpoint-best"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]


class RewriteDataset(Dataset):
    def __init__(self, frame, tokenizer, max_source=96, max_target=80):
        self.frame = frame.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_source = max_source
        self.max_target = max_target

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, index):
        row = self.frame.iloc[index]
        source = self.tokenizer(
            build_prompt(row.original, row.target_level),
            max_length=self.max_source,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        target = self.tokenizer(
            normalize_generated_text(row.rewrite),
            max_length=self.max_target,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        ).input_ids.squeeze(0)
        target[target == self.tokenizer.pad_token_id] = -100
        return {
            "input_ids": source.input_ids.squeeze(0),
            "attention_mask": source.attention_mask.squeeze(0),
            "labels": target,
        }


def sample_rows(frame, samples, seed):
    if samples <= 0 or samples >= len(frame):
        return frame.reset_index(drop=True)
    return frame.sample(samples, random_state=seed).reset_index(drop=True)


def build_evaluation_tasks(frame, samples, seed):
    grouped = []
    columns = ["original", "source_level", "target_level", "task_direction"]
    for keys, group in frame.groupby(columns, sort=False):
        grouped.append(
            {
                **dict(zip(columns, keys)),
                "references": [normalize_generated_text(value) for value in group.rewrite],
                "target_fkgl": float(group.target_fkgl.mean()),
            }
        )
    tasks = pd.DataFrame(grouped)
    return sample_rows(tasks, samples, seed)


def ngrams(text, size):
    tokens = re.findall(r"\b\w+(?:'\w+)?\b", text.lower())
    return {tuple(tokens[index : index + size]) for index in range(len(tokens) - size + 1)}


def f1(precision, recall):
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def sari_score(source, prediction, references):
    scores = []
    for size in range(1, 5):
        source_set = ngrams(source, size)
        prediction_set = ngrams(prediction, size)
        reference_set = set().union(*(ngrams(reference, size) for reference in references))

        added = prediction_set - source_set
        wanted_add = reference_set - source_set
        add_precision = len(added & wanted_add) / max(1, len(added))
        add_recall = len(added & wanted_add) / max(1, len(wanted_add))

        kept = prediction_set & source_set
        wanted_keep = reference_set & source_set
        keep_precision = len(kept & wanted_keep) / max(1, len(kept))
        keep_recall = len(kept & wanted_keep) / max(1, len(wanted_keep))

        deleted = source_set - prediction_set
        wanted_delete = source_set - reference_set
        delete_precision = len(deleted & wanted_delete) / max(1, len(deleted))
        scores.append(
            (f1(add_precision, add_recall) + f1(keep_precision, keep_recall) + delete_precision) / 3
        )
    return 100 * sum(scores) / 4


def generate_predictions(model, tokenizer, tasks, device, batch_size):
    prompts = [build_prompt(row.original, row.target_level) for row in tasks.itertuples()]
    predictions = []
    model.eval()
    for start in range(0, len(prompts), batch_size):
        encoded = tokenizer(
            prompts[start : start + batch_size],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=96,
        )
        inputs = {name: tensor.to(device) for name, tensor in encoded.items()}
        with torch.inference_mode():
            output = model.generate(
                **inputs, max_new_tokens=80, num_beams=2, no_repeat_ngram_size=3
            )
        predictions.extend(tokenizer.batch_decode(output, skip_special_tokens=True))
    return [normalize_generated_text(value) for value in predictions]


def semantic_tfidf_cosine(sources, predictions):
    corpus = list(sources) + list(predictions)
    matrix = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(corpus)
    count = len(sources)
    similarities = matrix[:count].multiply(matrix[count:]).sum(axis=1)
    return np.asarray(similarities).ravel().tolist()


def evaluate(model, tokenizer, tasks, device, batch_size=16, cefr_engine=None):
    started = time.time()
    predictions = generate_predictions(model, tokenizer, tasks, device, batch_size)
    sources = tasks.original.tolist()
    semantic = semantic_tfidf_cosine(sources, predictions)
    rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    sari_values = []
    rouge_values = []
    fkgl_errors = []
    direction_success = []
    changed_values = []
    simplify_success = []
    preserve_success = []
    records = []
    exact = within_one = valid = 0
    for row, prediction, similarity in zip(tasks.itertuples(), predictions, semantic):
        sari = sari_score(row.original, prediction, row.references)
        rouge_l = max(
            rouge.score(reference, prediction)["rougeL"].fmeasure for reference in row.references
        )
        prediction_fkgl = float(textstat.flesch_kincaid_grade(prediction))
        source_fkgl = float(textstat.flesch_kincaid_grade(row.original))
        changed = prediction.casefold() != normalize_generated_text(row.original).casefold()
        if row.task_direction == "simplify":
            direction_ok = changed and prediction_fkgl < source_fkgl - 0.25
            simplify_success.append(direction_ok)
        else:
            direction_ok = abs(prediction_fkgl - source_fkgl) <= 2.0
            preserve_success.append(direction_ok)
        predicted_level = None
        if cefr_engine is not None:
            result = cefr_engine.predict(prediction, route_override="sentence_mode")
            predicted_level = result.get("predicted_level")
            if predicted_level in LEVELS:
                valid += 1
                distance = abs(LEVELS.index(predicted_level) - LEVELS.index(row.target_level))
                exact += int(distance == 0)
                within_one += int(distance <= 1)
        sari_values.append(sari)
        rouge_values.append(rouge_l)
        fkgl_errors.append(abs(prediction_fkgl - row.target_fkgl))
        direction_success.append(direction_ok)
        changed_values.append(changed)
        records.append(
            {
                "source": row.original,
                "target_level": row.target_level,
                "direction": row.task_direction,
                "prediction": prediction,
                "predicted_level": predicted_level,
                "sari": round(sari, 2),
                "semantic_tfidf_cosine": round(similarity, 4),
                "rewrite_changed": changed,
            }
        )
    metrics = {
        "tasks": len(tasks),
        "sari": round(float(np.mean(sari_values)), 2),
        "rouge_l_f1_best_reference": round(float(np.mean(rouge_values)), 4),
        "semantic_tfidf_cosine": round(float(np.mean(semantic)), 4),
        "target_fkgl_mae": round(float(np.mean(fkgl_errors)), 2),
        "direction_success": round(float(np.mean(direction_success)), 4),
        "rewrite_changed_rate": round(float(np.mean(changed_values)), 4),
        "simplification_success": round(float(np.mean(simplify_success)), 4),
        "preservation_success": round(float(np.mean(preserve_success)), 4),
        "evaluation_seconds": round(time.time() - started, 2),
    }
    if cefr_engine is not None:
        metrics["cefr_exact_alignment"] = round(exact / max(1, valid), 4)
        metrics["cefr_within_one_level"] = round(within_one / max(1, valid), 4)
    return metrics, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--grad_accum", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=3e-4)
    parser.add_argument("--train_samples", type=int, default=10000)
    parser.add_argument("--eval_tasks", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--output_dir", type=str, default=str(MODEL_DIR / "checkpoint-candidate"))
    parser.add_argument("--evaluate_only", action="store_true")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = select_device(args.device)

    frames = {
        split: pd.read_csv(PROJECT_ROOT / f"data/processed/model3b_rewrite_{split}.csv")
        for split in ("train", "val", "test")
    }
    if any((frame.task_direction == "upgrade_proxy_only").any() for frame in frames.values()):
        raise ValueError("Unsupported upgrade rows found in Model 3b splits")
    train_frame = sample_rows(frames["train"], args.train_samples, args.seed)
    val_tasks = build_evaluation_tasks(frames["val"], args.eval_tasks, args.seed)
    test_tasks = build_evaluation_tasks(frames["test"], args.eval_tasks, args.seed)
    print(
        f"Device={device.type}; Output Checkpoint Directory={output_dir}; selected train/val tasks/test tasks="
        f"{len(train_frame):,}/{len(val_tasks):,}/{len(test_tasks):,}"
    )

    if args.evaluate_only:
        tokenizer = AutoTokenizer.from_pretrained(output_dir)
        model = AutoModelForSeq2SeqLM.from_pretrained(output_dir).to(device)
        test_metrics, samples = evaluate(
            model,
            tokenizer,
            test_tasks,
            device,
            args.batch_size,
            CEFRInferenceEngine(),
        )
        meta_filename = (
            "metadata.json"
            if output_dir.resolve() == CHECKPOINT_DIR.resolve()
            else "metadata-candidate.json"
        )
        metadata_path = MODEL_DIR / meta_filename
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["test_metrics"] = test_metrics
        metadata["sample_predictions"] = samples[:20]
        metadata["reevaluated_at"] = datetime.now(timezone.utc).isoformat()
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(test_metrics, indent=2))
        return

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL).to(device)
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    baseline_val, _ = evaluate(model, tokenizer, val_tasks, device, args.batch_size)
    print(f"Baseline validation: {baseline_val}")
    best_score = baseline_val["sari"] + 20 * baseline_val["semantic_tfidf_cosine"]
    best_epoch = 0
    history = []

    loader = DataLoader(
        RewriteDataset(train_frame, tokenizer), batch_size=args.batch_size, shuffle=True
    )
    optimizer = AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.01)
    total_steps = math.ceil(len(loader) / args.grad_accum) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, int(total_steps * 0.05), max(1, total_steps)
    )
    training_started = time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()
        total_loss = 0.0
        for step, batch in enumerate(loader, 1):
            batch = {name: tensor.to(device) for name, tensor in batch.items()}
            loss = model(**batch).loss
            (loss / args.grad_accum).backward()
            total_loss += loss.item()
            if step % args.grad_accum == 0 or step == len(loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
            if step % 100 == 0:
                vram_info = (
                    f" | VRAM: {torch.cuda.max_memory_allocated() / (1024 * 1024):.1f} MiB"
                    if device.type == "cuda"
                    else ""
                )
                print(f"Epoch {epoch} step {step}/{len(loader)} loss={loss.item():.4f}{vram_info}")
        validation, _ = evaluate(model, tokenizer, val_tasks, device, args.batch_size)
        score = validation["sari"] + 20 * validation["semantic_tfidf_cosine"]
        selected = score > best_score
        if selected:
            best_score = score
            best_epoch = epoch
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(total_loss / len(loader), 4),
                "validation": validation,
                "selection_score": round(score, 4),
                "selected": selected,
            }
        )
        print(f"Epoch {epoch}: {history[-1]}")

    selected_model = AutoModelForSeq2SeqLM.from_pretrained(output_dir).to(device)
    test_metrics, samples = evaluate(
        selected_model,
        tokenizer,
        test_tasks,
        device,
        args.batch_size,
        CEFRInferenceEngine(),
    )
    metadata = {
        "model_name": BASE_MODEL,
        "task": "English sentence simplification and level preservation",
        "supported_directions": ["simplify", "preserve"],
        "unsupported_direction": "upgrade",
        "checkpoint_selection": "validation SARI + 20 * semantic TF-IDF cosine",
        "best_epoch": best_epoch,
        "dataset_rows": {split: len(frame) for split, frame in frames.items()},
        "dataset_unique_originals": {
            split: int(frame.original.nunique()) for split, frame in frames.items()
        },
        "training_config": {
            **vars(args),
            "device_used": device.type,
            "selected_train_rows": len(train_frame),
            "selected_validation_tasks": len(val_tasks),
            "selected_test_tasks": len(test_tasks),
            "sampling": "random_seed_42",
        },
        "baseline_validation": baseline_val,
        "epoch_history": history,
        "test_metrics": test_metrics,
        "training_seconds": round(time.time() - training_started, 2),
        "sample_predictions": samples[:20],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    meta_filename = (
        "metadata.json"
        if output_dir.resolve() == CHECKPOINT_DIR.resolve()
        else "metadata-candidate.json"
    )
    (MODEL_DIR / meta_filename).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\n[DONE] Saved metadata to: {MODEL_DIR / meta_filename}")
    print(json.dumps(test_metrics, indent=2))


if __name__ == "__main__":
    main()
