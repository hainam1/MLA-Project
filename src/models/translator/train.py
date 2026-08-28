# -*- coding: utf-8 -*-
"""
CAPYVOCAB ML - MODEL 1: TRANSLATOR (VI -> EN) - PHASE 4 CONTROLLED RETRAINING.
Base model: Helsinki-NLP/opus-mt-vi-en (MarianMT, ~74M parameters).
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import re
import time
import json
import argparse
import random
import math
from datetime import datetime

# Import torch and transformers FIRST before numpy/pandas to avoid Windows OpenMP DLL collision
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import MarianTokenizer, MarianMTModel, get_linear_schedule_with_warmup
import sacrebleu

import pandas as pd

from src.runtime.hardware import select_device

MODEL_NAME = "Helsinki-NLP/opus-mt-vi-en"


def clean_and_detokenize(text: str) -> str:
    """Chuẩn hóa dữ liệu text: loại bỏ khoảng trắng thừa trước dấu câu (đặc trưng dữ liệu IWSLT)."""
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r"\s+([,.:;?!%\'\"])", r"\1", text)
    text = re.sub(r"([\'\"])\s+", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class TranslationDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=128):
        self.sources = [clean_and_detokenize(x) for x in df["vi"].tolist()]
        self.targets = [clean_and_detokenize(x) for x in df["en"].tolist()]
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.sources)

    def __getitem__(self, idx):
        src_text = self.sources[idx]
        tgt_text = self.targets[idx]

        src_enc = self.tokenizer(
            src_text,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        tgt_enc = self.tokenizer(
            tgt_text,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        labels = tgt_enc["input_ids"].squeeze(0)
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids": src_enc["input_ids"].squeeze(0),
            "attention_mask": src_enc["attention_mask"].squeeze(0),
            "labels": labels,
        }


def evaluate_metrics(model, tokenizer, df, max_samples=1000, batch_size=16, random_state=42):
    """Đánh giá SacreBLEU và ChrF++ chuẩn hóa."""
    model.eval()
    device = next(model.parameters()).device

    if max_samples and max_samples < len(df):
        eval_df = df.sample(n=max_samples, random_state=random_state).copy()
    else:
        eval_df = df.copy()
    sources = [clean_and_detokenize(x) for x in eval_df["vi"].tolist()]
    references = [clean_and_detokenize(x) for x in eval_df["en"].tolist()]

    predictions = []
    t0 = time.time()

    for i in range(0, len(sources), batch_size):
        batch_src = sources[i : i + batch_size]
        encoded = tokenizer(
            batch_src, return_tensors="pt", padding=True, truncation=True, max_length=128
        )
        inputs = {k: v.to(device) for k, v in encoded.items()}
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=128, num_beams=4)
        preds = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        predictions.extend([clean_and_detokenize(p) for p in preds])

    eval_time = round(time.time() - t0, 2)
    bleu = round(float(sacrebleu.corpus_bleu(predictions, [references]).score), 2)
    chrf = round(float(sacrebleu.corpus_chrf(predictions, [references]).score), 2)

    return {
        "bleu": bleu,
        "chrf": chrf,
        "eval_time_sec": eval_time,
        "sources": sources,
        "references": references,
        "predictions": predictions,
    }


def main():
    parser = argparse.ArgumentParser(description="Model 1 Controlled Retraining VI->EN")
    parser.add_argument("--epochs", type=int, default=3, help="So epoch huan luyen")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--grad_accum", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--lr", type=float, default=1.5e-5, help="Learning rate can than")
    parser.add_argument("--train_samples", type=int, default=3500, help="So luong mau train sach")
    parser.add_argument(
        "--eval_samples",
        type=int,
        default=1000,
        help="Random evaluation sample size; use 0 for the full split",
    )
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()

    out_dir = "src/models/translator"
    checkpoint_best_dir = os.path.join(out_dir, "checkpoint-best")
    meta_path = os.path.join(out_dir, "metadata.json")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 80)
    print("CAPYVOCAB ML - HUAN LUYEN LAI CO KIEM SOAT MODEL 1 (TRANSLATOR VI -> EN)")
    print("=" * 80)
    device = select_device(args.device)
    print(f"1. Thiet bi thuc thi: {device.type.upper()}")

    print("\n2. Dang doc va chuan hoa du lieu song ngu...")
    train_df = pd.read_csv("data/processed/model1_translator_train.csv")
    val_df = pd.read_csv("data/processed/model1_translator_val.csv")
    test_df = pd.read_csv("data/processed/model1_translator_test.csv")

    print(f"   - Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")

    print(f"\n3. Tai Base Model: {MODEL_NAME}...")
    tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
    base_model = MarianMTModel.from_pretrained(MODEL_NAME).to(device)
    print("   [OK] Model va Tokenizer da san sang!")

    # The untouched baseline is a real candidate and must be reproducible.
    base_model.save_pretrained(checkpoint_best_dir)
    tokenizer.save_pretrained(checkpoint_best_dir)

    # 4. Đánh giá Baseline Model trên cả Val và Test
    eval_n = len(test_df) if args.eval_samples == 0 else min(args.eval_samples, len(test_df))
    print(f"\n4. Danh gia BASELINE MODEL goc tren {eval_n:,} mau Test...")
    base_eval_test = evaluate_metrics(
        base_model, tokenizer, test_df, max_samples=eval_n, batch_size=args.batch_size
    )
    base_eval_val = evaluate_metrics(
        base_model, tokenizer, val_df, max_samples=eval_n, batch_size=args.batch_size
    )
    print(
        f"   * Baseline Test: SacreBLEU = {base_eval_test['bleu']} | ChrF++ = {base_eval_test['chrf']}"
    )
    print(
        f"   * Baseline Val : SacreBLEU = {base_eval_val['bleu']} | ChrF++ = {base_eval_val['chrf']}"
    )

    # 5. Chuẩn bị tập Train
    train_n = min(args.train_samples, len(train_df))
    train_subset = train_df.iloc[:train_n].copy()
    print(f"\n5. Chuan bi tap huan luyen ({train_n:,} samples sach, da detokenize)...")

    train_ds = TranslationDataset(train_subset, tokenizer, max_len=128)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)

    optimizer = AdamW(base_model.parameters(), lr=args.lr, weight_decay=0.05)
    total_steps = math.ceil(len(train_loader) / args.grad_accum) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=max(1, total_steps)
    )

    effective_bs = args.batch_size * args.grad_accum
    print(f"\n6. Bat dau huan luyen co kiem soat:")
    print(
        f"   - Epochs: {args.epochs} | Batch size: {args.batch_size} | Accumulation: {args.grad_accum} | Effective Batch: {effective_bs}"
    )
    print(
        f"   - Learning rate: {args.lr} (Giam 3.3x so voi lan truoc de chong catastrophic forgetting)"
    )
    print(f"   - Weight decay: 0.05 | Warmup ratio: 10%")

    best_val_bleu = base_eval_val["bleu"]
    best_epoch = 0
    epoch_history = []

    train_t0 = time.time()

    for epoch in range(1, args.epochs + 1):
        base_model.train()
        epoch_loss = 0.0
        optimizer.zero_grad()

        ep_t0 = time.time()
        for step, batch in enumerate(train_loader, 1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = base_model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss / args.grad_accum
            loss.backward()
            epoch_loss += loss.item() * args.grad_accum

            if step % args.grad_accum == 0 or step == len(train_loader):
                torch.nn.utils.clip_grad_norm_(base_model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

            if step % 50 == 0 or step == len(train_loader):
                step_vram = (
                    f" | VRAM: {torch.cuda.max_memory_allocated() / (1024 * 1024):.1f} MiB"
                    if device.type == "cuda"
                    else ""
                )
                print(
                    f"      Step {step:3d}/{len(train_loader)} - Batch Loss: {loss.item() * args.grad_accum:.4f}{step_vram}"
                )

        avg_loss = epoch_loss / len(train_loader)
        ep_duration = round(time.time() - ep_t0, 2)
        vram_info = (
            f" | Peak VRAM: {torch.cuda.max_memory_allocated() / (1024 * 1024):.2f} MiB / 8151 MiB"
            if device.type == "cuda"
            else ""
        )

        # Đánh giá trên Validation Set sau mỗi epoch
        print(
            f"\n   [Epoch {epoch}/{args.epochs}] Train Loss: {avg_loss:.4f} ({ep_duration}s){vram_info}"
        )
        print(f"   -> Dang danh gia tren {eval_n} mau Validation...")
        val_eval = evaluate_metrics(
            base_model, tokenizer, val_df, max_samples=eval_n, batch_size=args.batch_size
        )
        print(f"   -> Val SacreBLEU: {val_eval['bleu']} | Val ChrF++: {val_eval['chrf']}")

        is_best = False
        if val_eval["bleu"] > best_val_bleu:
            best_val_bleu = val_eval["bleu"]
            best_epoch = epoch
            is_best = True
            print(
                f"   [BEST CHECKPOINT] Dat dinh moi o Epoch {epoch} (Val BLEU: {best_val_bleu}) -> Dang luu checkpoint-best..."
            )
            base_model.save_pretrained(checkpoint_best_dir)
            tokenizer.save_pretrained(checkpoint_best_dir)

        epoch_history.append(
            {
                "epoch": epoch,
                "train_loss": round(avg_loss, 4),
                "val_bleu": val_eval["bleu"],
                "val_chrf": val_eval["chrf"],
                "is_best": is_best,
            }
        )

    total_train_time = round(time.time() - train_t0, 2)
    print(f"\n[OK] Hoan tat huan luyen trong: {total_train_time}s ({total_train_time/60:.2f} phut)")
    print(
        f"   * Checkpoint tot nhat duoc chon tu: Epoch {best_epoch if best_epoch > 0 else 'Base Pretrained'}"
    )

    # 7. Always reload the selected checkpoint. When no epoch improves, this is
    # the untouched baseline saved before optimizer updates.
    eval_model = MarianMTModel.from_pretrained(checkpoint_best_dir).to(device)
    eval_tokenizer = MarianTokenizer.from_pretrained(checkpoint_best_dir)

    print(f"\n7. Danh gia FINE-TUNED MODEL tren {eval_n:,} mau Test...")
    fine_eval_test = evaluate_metrics(
        eval_model,
        eval_tokenizer,
        test_df,
        max_samples=eval_n,
        batch_size=args.batch_size,
    )

    delta_bleu = round(fine_eval_test["bleu"] - base_eval_test["bleu"], 2)
    delta_chrf = round(fine_eval_test["chrf"] - base_eval_test["chrf"], 2)

    print("\n" + "=" * 80)
    print("BANG TIEN TRINH THEO TUNG EPOCH (VALIDATION SET)")
    print("=" * 80)
    print(
        f"{'Epoch':<8} | {'Train Loss':<12} | {'Val BLEU':<12} | {'Val ChrF++':<12} | {'Ghi chu':<20}"
    )
    print("-" * 80)
    print(
        f"{'Base':<8} | {'-':<12} | {base_eval_val['bleu']:<12} | {base_eval_val['chrf']:<12} | Pre-trained Baseline"
    )
    for row in epoch_history:
        note = "⭐ BEST CHECKPOINT" if row["is_best"] else "No improvement"
        print(
            f"{row['epoch']:<8} | {row['train_loss']:<12} | {row['val_bleu']:<12} | {row['val_chrf']:<12} | {note}"
        )

    print("\n" + "=" * 80)
    print("KET QUA CUOI CUNG TREN TEST SET")
    print("=" * 80)
    print(
        f"* Baseline Pre-trained Model : SacreBLEU = {base_eval_test['bleu']:<6} | ChrF++ = {base_eval_test['chrf']}"
    )
    print(
        f"* Fine-tuned Model (Best)    : SacreBLEU = {fine_eval_test['bleu']:<6} | ChrF++ = {fine_eval_test['chrf']}"
    )
    print(
        f"* Cai thien thuc te (Delta)  : Delta BLEU = {'+' if delta_bleu >= 0 else ''}{delta_bleu} | Delta ChrF++ = {'+' if delta_chrf >= 0 else ''}{delta_chrf}"
    )

    # 8. 10 câu mẫu định tính
    print("\n" + "=" * 80)
    print("--- 10 CAP CAU MAU DINH TINH (QUALITATIVE EXAMPLES) ---")
    print("=" * 80)
    random.seed(42)
    sample_indices = random.sample(
        range(len(base_eval_test["sources"])), min(10, len(base_eval_test["sources"]))
    )

    sample_records = []
    for idx, s_idx in enumerate(sample_indices, 1):
        src_text = base_eval_test["sources"][s_idx]
        ref_text = base_eval_test["references"][s_idx]
        pred_text = fine_eval_test["predictions"][s_idx]
        base_text = base_eval_test["predictions"][s_idx]

        print(f"\n[Vi du #{idx}]")
        print(f"  VI goc       : {src_text}")
        print(f"  Tham chieu   : {ref_text}")
        print(f"  Model dich   : {pred_text}")
        print(f"  (Base dich)  : {base_text}")

        sample_records.append(
            {
                "vi_source": src_text,
                "en_reference": ref_text,
                "model_translation": pred_text,
                "base_translation": base_text,
            }
        )

    # 9. Lưu Metadata
    metadata = {
        "model_name": MODEL_NAME,
        "task": "Translation VI -> EN (Controlled Retraining)",
        "training_config": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "gradient_accumulation_steps": args.grad_accum,
            "effective_batch_size": effective_bs,
            "learning_rate": args.lr,
            "weight_decay": 0.05,
            "warmup_ratio": 0.1,
            "max_length": 128,
            "device": device.type,
            "train_samples": train_n,
            "eval_samples": eval_n,
            "evaluation_sampling": "full" if args.eval_samples == 0 else "random_seed_42",
            "best_epoch": best_epoch,
        },
        "epoch_progression": epoch_history,
        "metrics": {
            "baseline_test": {"sacrebleu": base_eval_test["bleu"], "chrf": base_eval_test["chrf"]},
            "finetuned_test": {
                "sacrebleu": fine_eval_test["bleu"],
                "chrf": fine_eval_test["chrf"],
                "delta_bleu": delta_bleu,
                "delta_chrf": delta_chrf,
            },
        },
        "training_time_seconds": total_train_time,
        "sample_translations": sample_records,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"\n[DONE] Da luu metadata tai: {meta_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
