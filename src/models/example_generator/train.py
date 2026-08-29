"""Train and evaluate Model 3a, a word-conditioned CEFR example generator."""

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

import pandas as pd
import sacrebleu
import torch
from rouge_score import rouge_scorer
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, get_linear_schedule_with_warmup

from src.models.example_generator.service import build_prompt, contains_target
from src.pipeline.predict_cefr import CEFRInferenceEngine
from src.runtime.hardware import select_device

BASE_MODEL = "google/flan-t5-small"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = Path(__file__).resolve().parent
CHECKPOINT_DIR = MODEL_DIR / "checkpoint-best"
LEVEL_TO_INDEX = {level: index for index, level in enumerate(["A1", "A2", "B1", "B2", "C1"])}


def checkpoint_selection_score(metrics: dict) -> float:
    """Require CEFR alignment instead of rewarding prompt echo alone."""
    return (
        0.25 * metrics["rouge_l_f1"]
        + 0.25 * metrics["lexical_constraint_satisfaction"]
        + 0.50 * metrics["cefr_exact_alignment"]
    )


def clean_sentence(text: str) -> str:
    text = re.sub(r"\s+([,.:;?!%])", r"\1", str(text))
    return re.sub(r"\s+", " ", text).strip()


class ExampleDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, tokenizer, max_source=48, max_target=64):
        self.frame = frame.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_source = max_source
        self.max_target = max_target

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, index):
        row = self.frame.iloc[index]
        source = self.tokenizer(
            build_prompt(row.target_word, row.target_level),
            max_length=self.max_source,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        target = self.tokenizer(
            clean_sentence(row.target_sentence),
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


def select_frame(frame: pd.DataFrame, samples: int, seed: int) -> pd.DataFrame:
    if samples <= 0 or samples >= len(frame):
        return frame.reset_index(drop=True)
    return frame.sample(samples, random_state=seed).reset_index(drop=True)


def generate_predictions(model, tokenizer, frame, device, batch_size=16, mode="raw"):
    prompts = [build_prompt(row.target_word, row.target_level) for row in frame.itertuples()]
    words = [row.target_word for row in frame.itertuples()]
    levels = [row.target_level for row in frame.itertuples()]
    predictions = []
    model.eval()
    for start in range(0, len(prompts), batch_size):
        batch_prompts = prompts[start : start + batch_size]
        batch_words = words[start : start + batch_size]
        batch_levels = levels[start : start + batch_size]
        encoded = tokenizer(
            batch_prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=48,
        )
        inputs = {name: tensor.to(device) for name, tensor in encoded.items()}
        with torch.inference_mode():
            outputs = model.generate(
                **inputs, max_new_tokens=64, num_beams=4, no_repeat_ngram_size=3
            )
        batch_preds = [
            clean_sentence(text)
            for text in tokenizer.batch_decode(outputs, skip_special_tokens=True)
        ]
        
        if mode == "constrained":
            refined_preds = []
            for pred, word, level in zip(batch_preds, batch_words, batch_levels):
                if contains_target(pred, word):
                    refined_preds.append(pred)
                else:
                    # Strategy 1: Prompt reinforcement retry
                    retry_prompt = (
                        f'Write one {level} English sentence containing the exact word "{word}".'
                    )
                    retry_enc = tokenizer(retry_prompt, return_tensors="pt").to(device)
                    with torch.inference_mode():
                        retry_out = model.generate(
                            **retry_enc, max_new_tokens=64, num_beams=4, no_repeat_ngram_size=3
                        )
                    retry_pred = clean_sentence(
                        tokenizer.decode(retry_out[0], skip_special_tokens=True)
                    )
                    if contains_target(retry_pred, word):
                        refined_preds.append(retry_pred)
                    else:
                        # Strategy 2: Decoder Prefix forcing (pure local decoding, no template)
                        prefix_tokens = tokenizer(f"{word}", add_special_tokens=False).input_ids
                        dec_ids = torch.tensor(
                            [[model.config.decoder_start_token_id, *prefix_tokens]], device=device
                        )
                        orig_enc = tokenizer(build_prompt(word, level), return_tensors="pt").to(
                            device
                        )
                        with torch.inference_mode():
                            dec_out = model.generate(
                                **orig_enc,
                                decoder_input_ids=dec_ids,
                                max_new_tokens=64,
                                num_beams=4,
                                no_repeat_ngram_size=3,
                            )
                        dec_pred = clean_sentence(
                            tokenizer.decode(dec_out[0], skip_special_tokens=True)
                        )
                        refined_preds.append(dec_pred)
            batch_preds = refined_preds

        predictions.extend(batch_preds)
    return [clean_sentence(text) for text in predictions]


def evaluate(model, tokenizer, frame, device, cefr_engine=None, batch_size=16, mode="raw"):
    started = time.time()
    predictions = generate_predictions(
        model, tokenizer, frame, device, batch_size=batch_size, mode=mode
    )
    references = [clean_sentence(text) for text in frame.target_sentence]
    lexical = [
        contains_target(prediction, target)
        for prediction, target in zip(predictions, frame.target_word)
    ]
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    rouge_l = [
        scorer.score(reference, prediction)["rougeL"].fmeasure
        for prediction, reference in zip(predictions, references)
    ]
    metrics = {
        "samples": len(frame),
        "evaluation_mode": mode,
        "lexical_constraint_satisfaction": round(sum(lexical) / max(1, len(lexical)), 4),
        "sacrebleu": round(float(sacrebleu.corpus_bleu(predictions, [references]).score), 2),
        "rouge_l_f1": round(sum(rouge_l) / max(1, len(rouge_l)), 4),
        "evaluation_seconds": round(time.time() - started, 2),
    }
    if cefr_engine is not None:
        exact = 0
        within_one = 0
        valid = 0
        predicted_levels = []
        for prediction, expected in zip(predictions, frame.target_level):
            result = cefr_engine.predict(prediction, route_override="sentence_mode")
            predicted = result.get("predicted_level")
            predicted_levels.append(predicted)
            if predicted in LEVEL_TO_INDEX:
                valid += 1
                distance = abs(LEVEL_TO_INDEX[predicted] - LEVEL_TO_INDEX[str(expected)])
                exact += int(distance == 0)
                within_one += int(distance <= 1)
        metrics["cefr_exact_alignment"] = round(exact / max(1, valid), 4)
        metrics["cefr_within_one_level"] = round(within_one / max(1, valid), 4)
    else:
        predicted_levels = [None] * len(predictions)
    records = []
    for row, prediction, predicted_level, constraint_ok in zip(
        frame.itertuples(), predictions, predicted_levels, lexical
    ):
        records.append(
            {
                "target_word": row.target_word,
                "target_level": row.target_level,
                "reference": clean_sentence(row.target_sentence),
                "prediction": prediction,
                "predicted_cefr": predicted_level,
                "lexical_constraint_satisfied": constraint_ok,
            }
        )
    return metrics, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--grad_accum", type=int, default=2)
    parser.add_argument("--learning_rate", type=float, default=3e-4)
    parser.add_argument("--train_samples", type=int, default=10000)
    parser.add_argument("--eval_samples", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--output_dir", type=str, default=str(MODEL_DIR / "checkpoint-candidate"))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = select_device(args.device)
    paths = {
        split: PROJECT_ROOT / f"data/processed/model3a_example_gen_{split}.csv"
        for split in ("train", "val", "test")
    }
    frames = {split: pd.read_csv(path) for split, path in paths.items()}
    train_frame = select_frame(frames["train"], args.train_samples, args.seed)
    val_frame = select_frame(frames["val"], args.eval_samples, args.seed)
    test_frame = select_frame(frames["test"], args.eval_samples, args.seed)

    print(f"Device: {device.type}")
    print(f"Output Checkpoint Directory: {output_dir}")
    print(
        f"Dataset train/val/test: {len(frames['train']):,}/{len(frames['val']):,}/"
        f"{len(frames['test']):,}; selected: {len(train_frame):,}/{len(val_frame):,}/"
        f"{len(test_frame):,}"
    )
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL).to(device)
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    cefr_engine = CEFRInferenceEngine()
    baseline_val, _ = evaluate(
        model,
        tokenizer,
        val_frame,
        device,
        cefr_engine=cefr_engine,
        batch_size=args.batch_size,
    )
    print(f"Baseline validation: {baseline_val}")
    baseline_score = checkpoint_selection_score(baseline_val)
    print(
        f"Raw Base Pretrained Selection Score: {baseline_score:.4f} (Note: Lexical satisfaction inflated by prompt echo)"
    )
    best_score = -1.0
    best_epoch = 0
    history = []
    dataset = ExampleDataset(train_frame, tokenizer)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.01)
    total_steps = math.ceil(len(loader) / args.grad_accum) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, int(total_steps * 0.05), max(1, total_steps)
    )
    train_started = time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        optimizer.zero_grad()
        epoch_loss = 0.0
        for step, batch in enumerate(loader, 1):
            batch = {name: tensor.to(device) for name, tensor in batch.items()}
            loss = model(**batch).loss
            (loss / args.grad_accum).backward()
            epoch_loss += loss.item()
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
        val_metrics, _ = evaluate(
            model,
            tokenizer,
            val_frame,
            device,
            cefr_engine=cefr_engine,
            batch_size=args.batch_size,
        )
        score = checkpoint_selection_score(val_metrics)
        selected = score > best_score
        if selected:
            best_score = score
            best_epoch = epoch
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(epoch_loss / max(1, len(loader)), 4),
                "validation": val_metrics,
                "selection_score": round(score, 4),
                "selected": selected,
            }
        )
        print(f"Epoch {epoch}: {history[-1]}")

    print(f"\n[SELECTION SUMMARY] Best Epoch: {best_epoch} with Validation Score: {best_score:.4f}")
    selected_model = AutoModelForSeq2SeqLM.from_pretrained(output_dir).to(device)
    
    print("\n--- Running Evaluation on Test Set (1. Raw Model / Unconstrained) ---")
    test_metrics_raw, test_records_raw = evaluate(
        selected_model,
        tokenizer,
        test_frame,
        device,
        cefr_engine=cefr_engine,
        batch_size=args.batch_size,
        mode="raw",
    )
    print(f"Raw Test Metrics: {test_metrics_raw}")
    
    print("\n--- Running Evaluation on Test Set (2. Constrained Decoding / Local Prefix & Retry) ---")
    test_metrics_constrained, test_records_constrained = evaluate(
        selected_model,
        tokenizer,
        test_frame,
        device,
        cefr_engine=cefr_engine,
        batch_size=args.batch_size,
        mode="constrained",
    )
    print(f"Constrained Test Metrics: {test_metrics_constrained}")

    metadata = {
        "model_name": BASE_MODEL,
        "task": "word-conditioned CEFR example generation",
        "checkpoint_selection": (
            "0.25 * validation ROUGE-L + 0.25 * lexical satisfaction + "
            "0.50 * CEFR exact alignment"
        ),
        "best_epoch": best_epoch,
        "dataset_rows": {split: len(frame) for split, frame in frames.items()},
        "training_config": {
            **vars(args),
            "device_used": device.type,
            "selected_train_rows": len(train_frame),
            "selected_validation_rows": len(val_frame),
            "selected_test_rows": len(test_frame),
            "sampling": "random_seed_42" if args.train_samples > 0 else "full",
        },
        "baseline_validation": baseline_val,
        "epoch_history": history,
        "test_metrics_raw": test_metrics_raw,
        "test_metrics_constrained": test_metrics_constrained,
        "test_metrics": test_metrics_raw,
        "training_seconds": round(time.time() - train_started, 2),
        "sample_predictions_raw": test_records_raw[:20],
        "sample_predictions_constrained": test_records_constrained[:20],
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

    # Generate 20-sample comparison markdown artifact
    comparison_md_path = PROJECT_ROOT / "reports/model3a_20_sample_comparison.md"
    comparison_md_path.parent.mkdir(parents=True, exist_ok=True)
    comp_lines = [
        "# Model 3a: Bảng Đối Chiếu 20 Mẫu Ngẫu Nhiên (Raw Model vs Constrained Decoding)\n",
        f"**Thời gian đánh giá:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        f"**Tập kiểm thử:** {len(test_frame)} mẫu ngẫu nhiên từ `model3a_example_gen_test.csv` (Seed {args.seed})\n",
        "| # | Target Word | Level | Raw Prediction | Raw Satisfied? | Constrained Prediction | Constrained Satisfied? | Reference Sentence |",
        "|---|---|---|---|:---:|---|:---:|---|",
    ]
    for idx, (raw_rec, const_rec) in enumerate(zip(test_records_raw[:20], test_records_constrained[:20]), 1):
        raw_sat = "✅ True" if raw_rec["lexical_constraint_satisfied"] else "❌ False"
        const_sat = "✅ True" if const_rec["lexical_constraint_satisfied"] else "❌ False"
        comp_lines.append(
            f"| {idx} | `{raw_rec['target_word']}` | **{raw_rec['target_level']}** | {raw_rec['prediction']} | {raw_sat} | {const_rec['prediction']} | {const_sat} | {raw_rec['reference']} |"
        )
    comparison_md_path.write_text("\n".join(comp_lines) + "\n", encoding="utf-8")
    print(f"[ARTIFACT] Wrote 20-sample comparison to: {comparison_md_path}")

    # Generate Failure Cases Analysis artifact
    failures_md_path = PROJECT_ROOT / "reports/model3a_failure_cases.md"
    failure_records = [
        (idx, raw_rec, const_rec)
        for idx, (raw_rec, const_rec) in enumerate(zip(test_records_raw, test_records_constrained), 1)
        if not raw_rec["lexical_constraint_satisfied"] or not const_rec["lexical_constraint_satisfied"]
        or raw_rec["predicted_cefr"] != raw_rec["target_level"]
    ]
    fail_lines = [
        "# Model 3a: Phân Tích Các Trường Hợp Thất Bại (Failure Cases Analysis)\n",
        f"**Tổng số ca lỗi phát hiện trên test set ({len(test_frame)} mẫu):** {len(failure_records)}\n",
        "### Danh sách 10 ca lỗi điển hình và phân tích nguyên nhân:\n",
    ]
    for rank, (orig_idx, raw_rec, const_rec) in enumerate(failure_records[:10], 1):
        error_types = []
        if not raw_rec["lexical_constraint_satisfied"]:
            error_types.append("Raw Lexical Omission (quên từ đích)")
        if not const_rec["lexical_constraint_satisfied"]:
            error_types.append("Constrained Decoding Failure")
        if raw_rec["predicted_cefr"] != raw_rec["target_level"]:
            error_types.append(f"CEFR Mismatch (Mục tiêu: {raw_rec['target_level']} -> Thực tế: {raw_rec['predicted_cefr']})")
        
        fail_lines.append(f"#### Case {rank} (Mẫu #{orig_idx}): Từ khóa `{raw_rec['target_word']}` (Level yêu cầu: **{raw_rec['target_level']}**)")
        fail_lines.append(f"- **Phân loại lỗi:** {', '.join(error_types)}")
        fail_lines.append(f"- **Raw Prediction:** \"{raw_rec['prediction']}\" (CEFR: `{raw_rec['predicted_cefr']}`)")
        fail_lines.append(f"- **Constrained Prediction:** \"{const_rec['prediction']}\"")
        fail_lines.append(f"- **Reference:** \"{raw_rec['reference']}\"")
        fail_lines.append(f"- **Phân tích kỹ thuật:** ")
        if not raw_rec["lexical_constraint_satisfied"]:
            fail_lines.append(f"  + Mô hình sinh tự do đã biến đổi hình thái từ hoặc thay thế bằng từ đồng nghĩa khác trong ngữ cảnh.")
        else:
            fail_lines.append(f"  + Mô hình chứa đúng từ nhưng độ phức tạp ngữ pháp câu chưa đạt đúng mức CEFR mục tiêu (Model 2b phân loại lệch).")
        fail_lines.append("")
    failures_md_path.write_text("\n".join(fail_lines) + "\n", encoding="utf-8")
    print(f"[ARTIFACT] Wrote failure cases analysis to: {failures_md_path}")


if __name__ == "__main__":
    main()
