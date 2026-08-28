"""Inference service for the word-conditioned Model 3a checkpoint."""

from __future__ import annotations

import re
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from src.runtime.hardware import select_device

CHECKPOINT_DIR = Path(__file__).resolve().parent / "checkpoint-best"
VALID_LEVELS = {"A1", "A2", "B1", "B2", "C1"}


def build_prompt(target_word: str, target_level: str) -> str:
    return f'Write one {target_level} English sentence using the word "{target_word}".'


def contains_target(text: str, target_word: str) -> bool:
    pattern = rf"(?<!\w){re.escape(target_word.strip())}(?!\w)"
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def normalize_generated_text(text: str) -> str:
    text = re.sub(r"\s+([,.:;?!%'])", r"\1", str(text))
    return re.sub(r"\s+", " ", text).strip()


class ExampleGeneratorService:
    """Load Model 3a once and generate lexically constrained examples."""

    def __init__(self, checkpoint=CHECKPOINT_DIR, device: str = "auto"):
        self.checkpoint = Path(checkpoint)
        if not self.checkpoint.exists():
            raise FileNotFoundError(
                f"Model 3a checkpoint not found at {self.checkpoint}. Run the training module first."
            )
        self.device = select_device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.checkpoint).to(self.device)
        self.model.eval()

    def generate(self, target_word: str, target_level: str) -> dict:
        word = str(target_word).strip()
        level = str(target_level).strip().upper()
        if not word:
            raise ValueError("target_word must not be empty")
        if level not in VALID_LEVELS:
            raise ValueError(f"target_level must be one of {sorted(VALID_LEVELS)}")

        generation_args = {
            "max_new_tokens": 64,
            "num_beams": 4,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
        }
        sentence = self._decode(build_prompt(word, level), generation_args)
        strategy = "natural_generation"
        if not contains_target(sentence, word):
            retry_prompt = (
                f"Write one {level} English sentence. You must include the exact word form "
                f'"{word}". Do not replace or change that word.'
            )
            sentence = self._decode(retry_prompt, generation_args)
            strategy = "explicit_constraint_retry"
        if not contains_target(sentence, word):
            # Transformers 4.57 moved force_words_ids behind remote custom code.
            # Prefixing the local decoder with `word,` is a deterministic and
            # auditable fallback that does not require trust_remote_code=True.
            prefix_ids = self.tokenizer(f"{word},", add_special_tokens=False).input_ids
            decoder_ids = torch.tensor(
                [[self.model.config.decoder_start_token_id, *prefix_ids]], device=self.device
            )
            sentence = self._decode(
                build_prompt(word, level), generation_args, decoder_input_ids=decoder_ids
            )
            strategy = "local_decoder_prefix_fallback"
        return {
            "status": "success",
            "target_word": word,
            "target_level": level,
            "sentence": sentence,
            "lexical_constraint_satisfied": contains_target(sentence, word),
            "constraint_strategy": strategy,
            "model": "Model 3a FLAN-T5-small",
        }

    def generate_candidates(
        self, target_word: str, target_level: str, max_candidates: int = 4
    ) -> list[dict]:
        """Generate several ranked examples so the pipeline can verify CEFR fit."""
        word = str(target_word).strip()
        level = str(target_level).strip().upper()
        if not word:
            raise ValueError("target_word must not be empty")
        if level not in VALID_LEVELS:
            raise ValueError(f"target_level must be one of {sorted(VALID_LEVELS)}")

        candidate_count = max(1, min(int(max_candidates), 4))
        generation_args = {
            "max_new_tokens": 64,
            "num_beams": max(4, candidate_count),
            "num_return_sequences": candidate_count,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
        }
        encoded = self.tokenizer(
            build_prompt(word, level), return_tensors="pt", truncation=True, max_length=48
        )
        inputs = {name: tensor.to(self.device) for name, tensor in encoded.items()}
        with torch.inference_mode():
            outputs = self.model.generate(**inputs, **generation_args)

        candidates = []
        seen = set()
        for output in outputs:
            sentence = normalize_generated_text(
                self.tokenizer.decode(output, skip_special_tokens=True)
            )
            key = sentence.casefold()
            if sentence and key not in seen and contains_target(sentence, word):
                seen.add(key)
                candidates.append(
                    {
                        "status": "success",
                        "target_word": word,
                        "target_level": level,
                        "sentence": sentence,
                        "lexical_constraint_satisfied": True,
                        "constraint_strategy": "ranked_beam_generation",
                        "model": "Model 3a FLAN-T5-small",
                    }
                )
        if not candidates:
            candidates.append(self.generate(word, level))
        return candidates

    def _decode(self, prompt: str, generation_args: dict, **extra_generation_args) -> str:
        encoded = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=48)
        inputs = {name: tensor.to(self.device) for name, tensor in encoded.items()}
        with torch.inference_mode():
            output = self.model.generate(**inputs, **generation_args, **extra_generation_args)
        return normalize_generated_text(self.tokenizer.decode(output[0], skip_special_tokens=True))
