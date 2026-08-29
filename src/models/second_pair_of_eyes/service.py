"""Inference service for Model 4 (Second Pair of Eyes Meta-Classifier) - Leakage-Free Clean Pilot."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent
BUNDLE_PATH = MODEL_DIR / "model4_auditor.joblib"
LEVEL_MAP = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}


class QualityAuditorService:
    """Audit pipeline outputs and predict failure probability using strictly intrinsic text & CEFR signals."""

    def __init__(self, bundle_path: Path = BUNDLE_PATH):
        self.bundle_path = Path(bundle_path)
        if not self.bundle_path.exists():
            raise FileNotFoundError(
                f"Model 4 bundle not found at {self.bundle_path}. Run training script first."
            )
        data = joblib.load(self.bundle_path)
        self.scaler = data["scaler"]
        self.tfidf = data["tfidf"]
        self.svd = data["svd"]
        self.classifier = data["classifier"]
        self.feature_names = data["feature_names"]
        self.is_leakage_free = data.get("is_leakage_free", True)

    def audit(
        self,
        model_name: str,
        source_text: str,
        model_output: str,
        expected_level: str = "",
        predicted_level: str = "",
        automatic_reasons: list[str] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Predict whether the generated output contains a failure using intrinsic signals only."""
        f = {}
        # 1. Model source
        f["is_model3a"] = 1.0 if model_name == "model3a" else 0.0
        f["is_model1"] = 1.0 if model_name == "model1" else 0.0
        f["is_model3b"] = 1.0 if model_name == "model3b" else 0.0
        
        # 2. Surface text statistics
        out_text = str(model_output).strip()
        src_text = str(source_text).strip()
        out_words = out_text.split()
        src_words = src_text.split()
        
        f["out_char_len"] = float(len(out_text))
        f["out_word_count"] = float(len(out_words))
        f["src_word_count"] = float(len(src_words))
        f["word_count_diff"] = float(abs(len(out_words) - len(src_words)))
        f["length_ratio"] = float(len(out_words) / max(1, len(src_words)))
        f["is_short_sentence"] = 1.0 if len(out_words) <= 5 else 0.0
        f["is_long_sentence"] = 1.0 if len(out_words) >= 25 else 0.0
        f["is_capitalized"] = 1.0 if (out_text and out_text[0].isupper()) else 0.0
        
        has_rep = 0.0
        if len(out_words) >= 4:
            for i in range(len(out_words) - 1):
                if out_words[i].lower() == out_words[i+1].lower() and len(out_words[i]) > 2:
                    has_rep = 1.0
                    break
        f["has_repeated_word"] = has_rep
        
        # 3. CEFR alignment
        exp_lvl = LEVEL_MAP.get(str(expected_level).strip().upper(), 0)
        pred_lvl = LEVEL_MAP.get(str(predicted_level).strip().upper(), 0)
        f["exp_level_num"] = float(exp_lvl)
        f["pred_level_num"] = float(pred_lvl)
        f["has_cefr_levels"] = 1.0 if (exp_lvl > 0 and pred_lvl > 0) else 0.0
        f["cefr_diff"] = float(abs(exp_lvl - pred_lvl)) if (exp_lvl > 0 and pred_lvl > 0) else 0.0
        f["cefr_undershoot"] = float(max(0, exp_lvl - pred_lvl)) if (exp_lvl > 0 and pred_lvl > 0) else 0.0
        f["cefr_overshoot"] = float(max(0, pred_lvl - exp_lvl)) if (exp_lvl > 0 and pred_lvl > 0) else 0.0
        f["is_high_target"] = 1.0 if exp_lvl >= 4 else 0.0
        
        # 4. Text embedding SVD
        vec = self.tfidf.transform([out_text])
        emb = self.svd.transform(vec)[0]
        for i in range(6):
            f[f"text_svd_{i}"] = float(emb[i])
            
        feat_vector = np.array([[f[col] for col in self.feature_names]])
        feat_scaled = self.scaler.transform(feat_vector)
        
        prob_failure = float(self.classifier.predict_proba(feat_scaled)[0, 1])
        is_failure = bool(prob_failure >= 0.5)
        
        return {
            "is_failure_suspected": is_failure,
            "failure_probability": round(prob_failure, 4),
            "audit_verdict": "FLAGGED_FOR_HUMAN_REVIEW" if is_failure else "PASS_AUTOMATED_AUDIT",
            "model_audited": model_name,
            "auditor_status": "PILOT_PRELIMINARY_FILTER",
        }
