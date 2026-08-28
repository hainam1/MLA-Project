"""Lazy local inference service for the Vietnamese-to-English translator."""

from __future__ import annotations

import logging
import re
import shutil
import tempfile
from pathlib import Path

import torch

from src.runtime.hardware import select_device

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOGGER = logging.getLogger(__name__)


def normalize_translation_text(text: str) -> str:
    value = str(text)
    value = re.sub(r"\s+([,.:;?!%\'\"])", r"\1", value)
    value = re.sub(r"([\'\"])\s+", r"\1", value)
    return re.sub(r"\s+", " ", value).strip()


class TranslatorService:
    def __init__(self, checkpoint: Path | str | None = None, device: str = "auto"):
        self.checkpoint = Path(checkpoint or PROJECT_ROOT / "src/models/translator/checkpoint-best")
        required = [self.checkpoint / "config.json", self.checkpoint / "model.safetensors"]
        missing = [path for path in required if not path.exists()]
        if missing:
            raise FileNotFoundError(f"Translator checkpoint is incomplete: {missing}")
        # Lazy imports avoid native DLL collisions in processes that only use
        # the lightweight classifier pipeline.
        from transformers import MarianMTModel, MarianTokenizer

        self.device = select_device(device)
        LOGGER.info("Loading translator from %s on %s", self.checkpoint, self.device)
        tokenizer_path = self._ascii_tokenizer_path()
        self.tokenizer = MarianTokenizer.from_pretrained(tokenizer_path)
        self.model = MarianMTModel.from_pretrained(self.checkpoint).to(self.device)
        self.model.eval()
        LOGGER.info("Translator is ready")

    def _ascii_tokenizer_path(self) -> Path:
        """Stage SentencePiece assets because its Windows DLL rejects Unicode paths."""
        if str(self.checkpoint).isascii():
            return self.checkpoint
        destination = Path(tempfile.gettempdir()) / "capyvocab" / "translator-tokenizer"
        destination.mkdir(parents=True, exist_ok=True)
        filenames = [
            "source.spm",
            "target.spm",
            "vocab.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "config.json",
        ]
        for filename in filenames:
            source = self.checkpoint / filename
            if not source.exists():
                raise FileNotFoundError(f"Missing tokenizer asset: {source}")
            target = destination / filename
            if not target.exists() or target.stat().st_size != source.stat().st_size:
                shutil.copy2(source, target)
        return destination

    def translate(self, vietnamese_text: str, num_beams: int = 4) -> str:
        return self.translate_candidates(vietnamese_text, num_candidates=1, num_beams=num_beams)[0]

    def translate_candidates(
        self, vietnamese_text: str, num_candidates: int = 12, num_beams: int = 12
    ) -> list[str]:
        """Return ranked, unique translation candidates for CEFR-aware selection."""
        source = normalize_translation_text(vietnamese_text)
        if not source:
            raise ValueError("Translation input cannot be empty")
        candidate_count = max(1, min(int(num_candidates), int(num_beams)))
        encoded = self.tokenizer(
            [source], return_tensors="pt", padding=True, truncation=True, max_length=128
        )
        encoded = {name: tensor.to(self.device) for name, tensor in encoded.items()}
        with torch.inference_mode():
            generated = self.model.generate(
                **encoded,
                max_length=128,
                num_beams=max(int(num_beams), candidate_count),
                num_return_sequences=candidate_count,
                early_stopping=True,
            )
        unique = []
        seen = set()
        for translated in self.tokenizer.batch_decode(generated, skip_special_tokens=True):
            candidate = normalize_translation_text(translated).strip(" .,:;!?")
            key = candidate.casefold()
            if candidate and key not in seen:
                seen.add(key)
                unique.append(candidate)
        if not unique:
            raise RuntimeError("Translator did not produce a vocabulary candidate")
        return unique
