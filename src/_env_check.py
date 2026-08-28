"""Verify imports, spaCy assets, and actual CPU/GPU execution."""

from __future__ import annotations

import importlib
import platform
import sys

from src.runtime.hardware import inspect_torch_device

PACKAGES = [
    "torch",
    "transformers",
    "datasets",
    "sklearn",
    "xgboost",
    "wordfreq",
    "textstat",
    "sacrebleu",
    "pyphen",
    "spacy",
]


def test_imports() -> bool:
    passed = True
    for name in PACKAGES:
        try:
            module = importlib.import_module(name)
            print(f"[OK] {name}: {getattr(module, '__version__', 'installed')}")
        except Exception as exc:  # diagnostic command: report every import failure
            passed = False
            print(f"[FAIL] {name}: {exc}")
    try:
        import spacy

        spacy.load("en_core_web_sm")
        print("[OK] spaCy model: en_core_web_sm")
    except Exception as exc:
        passed = False
        print(f"[FAIL] spaCy model: {exc}")
    return passed


def test_hardware() -> bool:
    status = inspect_torch_device()
    print(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Accelerator: {status.to_dict()}")
    if status.cuda_reported and not status.cuda_usable:
        print("[WARN] CUDA is visible but cannot execute a tensor; CPU fallback is required.")
    return True


def main() -> int:
    return 0 if test_imports() and test_hardware() else 1


if __name__ == "__main__":
    raise SystemExit(main())
