"""Inference service for simplification/preservation Model 3b."""

from __future__ import annotations

import os
import re
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
_torch_lib = Path(__file__).resolve().parents[3] / ".venv/Lib/site-packages/torch/lib"
if _torch_lib.exists() and hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(str(_torch_lib))
    except Exception:
        pass

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from src.runtime.hardware import select_device

CHECKPOINT_DIR = Path(__file__).resolve().parent / "checkpoint-best"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]


def build_prompt(sentence: str, target_level: str) -> str:
    return (
        f"Rewrite this English sentence at {target_level} CEFR. "
        f"Simplify it or preserve its meaning: {sentence.strip()}"
    )


def normalize_generated_text(text: str) -> str:
    text = re.sub(r"\s+([,.:;?!%'])", r"\1", str(text))
    return re.sub(r"\s+", " ", text).strip()


class SentenceRewriterService:
    """Generate only simplification or same-level rewrites."""

    def __init__(self, checkpoint=CHECKPOINT_DIR, device: str = "auto"):
        self.checkpoint = Path(checkpoint)
        if not self.checkpoint.exists():
            raise FileNotFoundError(
                f"Model 3b checkpoint not found at {self.checkpoint}. Run training first."
            )
        self.device = select_device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.checkpoint).to(self.device)
        self.model.eval()

    def rewrite(self, sentence: str, source_level: str, target_level: str) -> dict:
        source = str(sentence).strip()
        source_cefr = str(source_level).upper().strip()
        target_cefr = str(target_level).upper().strip()
        if not source:
            raise ValueError("sentence must not be empty")
        if source_cefr not in LEVELS or target_cefr not in LEVELS:
            raise ValueError(f"CEFR levels must be one of {LEVELS}")
        if LEVELS.index(target_cefr) > LEVELS.index(source_cefr):
            raise ValueError("Model 3b does not support upgrade; target must not exceed source")

        encoded = self.tokenizer(
            build_prompt(source, target_cefr),
            return_tensors="pt",
            truncation=True,
            max_length=96,
        )
        inputs = {name: tensor.to(self.device) for name, tensor in encoded.items()}
        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=80,
                num_beams=4,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        rewrite = normalize_generated_text(
            self.tokenizer.decode(output[0], skip_special_tokens=True)
        )
        changed = rewrite.casefold() != normalize_generated_text(source).casefold()
        result = {
            "status": "success",
            "source_sentence": source,
            "source_level": source_cefr,
            "target_level": target_cefr,
            "direction": "preserve" if source_cefr == target_cefr else "simplify",
            "rewritten_sentence": rewrite,
            "rewrite_changed": changed,
            "model": "Model 3b FLAN-T5-small",
        }
        if source_cefr != target_cefr and not changed:
            result["warning"] = (
                "Model returned the source unchanged; simplification was not achieved."
            )
        return result
