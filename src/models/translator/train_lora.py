"""Fine-tune MarianMT (VI->EN) with LoRA / PEFT on full training dataset."""

import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from pathlib import Path

venv_torch = (Path(os.getcwd()) / ".venv/Lib/site-packages/torch/lib").resolve()
if venv_torch.exists() and hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(str(venv_torch))
    except Exception:
        pass

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import time
import math
import shutil
import tempfile
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    MarianMTModel,
    MarianTokenizer,
    get_linear_schedule_with_warmup,
)
from peft import LoraConfig, get_peft_model, TaskType
import sacrebleu

from src.models.translator.service import normalize_translation_text
from src.runtime.hardware import select_device

PROJECT_ROOT = Path(os.getcwd())
TRAIN_DATA_PATH = PROJECT_ROOT / "data/processed/model1_translator_train.csv"
VAL_DATA_PATH = PROJECT_ROOT / "data/processed/model1_translator_val.csv"
TEST_DATA_PATH = PROJECT_ROOT / "data/processed/model1_translator_test.csv"
BASE_CHECKPOINT = PROJECT_ROOT / "src/models/translator/checkpoint-best"
OUTPUT_DIR = PROJECT_ROOT / "src/models/translator/checkpoint-lora-best"


def get_ascii_tokenizer_path(checkpoint_dir: Path) -> Path:
    """Stage SentencePiece assets to temp dir to avoid Windows unicode path crash."""
    if str(checkpoint_dir).isascii():
        return checkpoint_dir
    dest = Path(tempfile.gettempdir()) / "capyvocab" / "lora-translator-tokenizer"
    dest.mkdir(parents=True, exist_ok=True)
    filenames = [
        "source.spm",
        "target.spm",
        "vocab.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "config.json",
    ]
    for fn in filenames:
        src = checkpoint_dir / fn
        if src.exists():
            shutil.copy2(src, dest / fn)
    return dest


class TranslationDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer: MarianTokenizer, max_len: int = 128):
        self.vi_texts = df["vi"].astype(str).tolist()
        self.en_texts = df["en"].astype(str).tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.vi_texts)

    def __getitem__(self, idx):
        return self.vi_texts[idx], self.en_texts[idx]


def collate_fn(batch, tokenizer, max_len=128):
    vi_batch, en_batch = zip(*batch)
    vi_norm = [normalize_translation_text(t) for t in vi_batch]
    en_norm = [normalize_translation_text(t) for t in en_batch]

    model_inputs = tokenizer(
        vi_norm,
        max_length=max_len,
        padding=True,
        truncation=True,
        return_tensors="pt",
    )
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            en_norm,
            max_length=max_len,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

    # Replace padding token id with -100 for loss ignoring
    label_ids = labels["input_ids"]
    label_ids[label_ids == tokenizer.pad_token_id] = -100
    model_inputs["labels"] = label_ids
    return model_inputs


def evaluate_bleu(model, tokenizer, val_df, device, max_samples=500, batch_size=32):
    model.eval()
    eval_subset = val_df.iloc[:max_samples].copy().reset_index(drop=True)
    preds = []
    refs = [normalize_translation_text(r) for r in eval_subset["en"].tolist()]

    for i in range(0, len(eval_subset), batch_size):
        batch_vi = eval_subset["vi"].iloc[i : i + batch_size].tolist()
        batch_vi_norm = [normalize_translation_text(t) for t in batch_vi]
        encoded = tokenizer(
            batch_vi_norm,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        ).to(device)
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_length=128,
                num_beams=4,
                early_stopping=True,
            )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        for d in decoded:
            preds.append(normalize_translation_text(d))

    bleu = sacrebleu.corpus_bleu(preds, [refs]).score
    chrf = sacrebleu.corpus_chrf(preds, [refs]).score
    return bleu, chrf, preds


def main():
    print("=" * 85)
    print("KHỞI ĐỘNG HUẤN LUYỆN MARIANMT LORA (VI -> EN)")
    print("=" * 85)

    device = select_device("auto")
    print(f"Device: {device}")

    # Load data
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    val_df = pd.read_csv(VAL_DATA_PATH)
    print(f"Loaded Train: {len(train_df)} samples | Val: {len(val_df)} samples")

    # Load Tokenizer & Base Model
    tok_path = get_ascii_tokenizer_path(BASE_CHECKPOINT)
    tokenizer = MarianTokenizer.from_pretrained(tok_path)
    base_model = MarianMTModel.from_pretrained(BASE_CHECKPOINT)

    # LoRA Config
    peft_config = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        inference_mode=False,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj", "out_proj"],
        bias="none",
    )

    model = get_peft_model(base_model, peft_config)
    model.to(device)
    model.print_trainable_parameters()

    # Hyperparameters
    num_epochs = 3
    batch_size = 32
    gradient_accumulation_steps = 2
    effective_batch = batch_size * gradient_accumulation_steps
    learning_rate = 3e-4
    weight_decay = 0.01

    train_dataset = TranslationDataset(train_df, tokenizer)
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda b: collate_fn(b, tokenizer),
        pin_memory=(device.type == "cuda"),
        num_workers=0,
    )

    total_steps = (len(train_loader) // gradient_accumulation_steps) * num_epochs
    warmup_steps = int(total_steps * 0.05)

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )
    scaler = torch.cuda.amp.GradScaler(enabled=(device.type == "cuda"))

    print(f"\nTraining Plan:")
    print(f"  • Total training pairs: {len(train_df)}")
    print(f"  • Epochs: {num_epochs}")
    print(f"  • Batch size: {batch_size} (Effective: {effective_batch})")
    print(f"  • Total Optimizer Steps: {total_steps} (Warmup: {warmup_steps})")
    print(f"  • Learning rate: {learning_rate}")

    # Baseline before training on validation slice
    print("\nEvaluating initial baseline before training...")
    base_bleu, base_chrf, _ = evaluate_bleu(model, tokenizer, val_df, device, max_samples=500)
    print(f"▶ Initial Val (500 samples): BLEU = {base_bleu:.2f} | chrF++ = {base_chrf:.2f}")

    best_val_bleu = base_bleu
    history = []

    for epoch in range(1, num_epochs + 1):
        model.train()
        epoch_loss = 0.0
        step_loss = 0.0
        t0 = time.time()

        optimizer.zero_grad()
        for step, batch in enumerate(train_loader, 1):
            batch = {k: v.to(device) for k, v in batch.items()}

            with torch.cuda.amp.autocast(enabled=(device.type == "cuda")):
                outputs = model(**batch)
                loss = outputs.loss / gradient_accumulation_steps

            scaler.scale(loss).backward()
            step_loss += loss.item() * gradient_accumulation_steps

            if step % gradient_accumulation_steps == 0 or step == len(train_loader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
                scheduler.step()

            epoch_loss += loss.item() * gradient_accumulation_steps

            if step % 500 == 0 or step == len(train_loader):
                current_lr = scheduler.get_last_lr()[0]
                avg_step_loss = step_loss / 500 if step % 500 == 0 else step_loss / (step % 500)
                print(
                    f"Epoch {epoch}/{num_epochs} | Step {step}/{len(train_loader)} | "
                    f"Train Loss: {avg_step_loss:.4f} | LR: {current_lr:.6f} | "
                    f"Time: {time.time() - t0:.1f}s"
                )
                step_loss = 0.0

        avg_epoch_loss = epoch_loss / len(train_loader)
        epoch_time = time.time() - t0

        # Evaluate on validation slice
        val_bleu, val_chrf, _ = evaluate_bleu(model, tokenizer, val_df, device, max_samples=500)
        is_best = val_bleu > best_val_bleu

        if is_best:
            best_val_bleu = val_bleu
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            # Save PEFT adapter
            model.save_pretrained(OUTPUT_DIR)
            tokenizer.save_pretrained(OUTPUT_DIR)
            print(f"⭐ [Epoch {epoch}] ĐÃ LƯU CHECKPOINT TỐT NHẤT MỚI: Val BLEU = {val_bleu:.2f} (chrF++ = {val_chrf:.2f}) -> {OUTPUT_DIR}")

        record = {
            "epoch": epoch,
            "train_loss": round(avg_epoch_loss, 4),
            "val_bleu": round(val_bleu, 2),
            "val_chrf": round(val_chrf, 2),
            "is_best": is_best,
            "epoch_time_sec": round(epoch_time, 1),
        }
        history.append(record)

        print("\n" + "-" * 70)
        print(f"📊 TỔNG KẾT EPOCH {epoch}/{num_epochs}:")
        print(f"  • Train Loss : {avg_epoch_loss:.4f}")
        print(f"  • Val BLEU   : {val_bleu:.2f} (Best: {best_val_bleu:.2f})")
        print(f"  • Val chrF++ : {val_chrf:.2f}")
        print(f"  • Thời gian  : {epoch_time:.1f}s")
        print("-" * 70 + "\n")

    # Save training log
    log_path = OUTPUT_DIR / "training_history.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    print(f"\nĐã lưu toàn bộ lịch sử huấn luyện vào: {log_path}")


if __name__ == "__main__":
    main()
