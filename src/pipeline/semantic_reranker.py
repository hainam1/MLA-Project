"""Cross-lingual semantic scoring used before CEFR selection."""

from __future__ import annotations

from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "src/models/semantic_reranker/checkpoint"


class SemanticReranker:
    """Lazy multilingual E5 encoder with a deterministic no-model fallback."""

    def __init__(self, model_path: Path | str | None = None, device: str = "auto"):
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        self.device_name = device
        self._tokenizer = None
        self._model = None
        self._device = None

    @property
    def available(self) -> bool:
        return (self.model_path / "config.json").exists() and any(
            self.model_path.glob("*.safetensors")
        )

    def _load(self) -> None:
        if self._model is not None:
            return
        if not self.available:
            raise FileNotFoundError(f"Semantic reranker checkpoint is missing: {self.model_path}")
        from transformers import AutoModel, AutoTokenizer

        if self.device_name == "cuda":
            device = torch.device("cuda")
        elif self.device_name == "cpu":
            device = torch.device("cpu")
        else:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)
        self._model = AutoModel.from_pretrained(self.model_path, local_files_only=True)
        self._model.to(device).eval()
        self._device = device

    @staticmethod
    def _average_pool(hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        masked = hidden_state.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return masked.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    def score(self, vietnamese_query: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        if not self.available:
            return [0.0] * len(passages)
        self._load()
        texts = [f"query: {vietnamese_query}", *[f"passage: {item}" for item in passages]]
        encoded = self._tokenizer(
            texts, max_length=128, padding=True, truncation=True, return_tensors="pt"
        ).to(self._device)
        with torch.inference_mode():
            output = self._model(**encoded)
            embeddings = self._average_pool(output.last_hidden_state, encoded["attention_mask"])
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return [float(value) for value in (embeddings[0] @ embeddings[1:].T).cpu().tolist()]
