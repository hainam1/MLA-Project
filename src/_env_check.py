"""Verify dependencies for the core project and optional contextual extension."""

from __future__ import annotations

import argparse
import importlib
import platform
import sys

CORE_PACKAGES = [
    "pandas",
    "numpy",
    "scipy",
    "sklearn",
    "spacy",
    "wordfreq",
    "textstat",
    "pyphen",
    "datasets",
]
CONTEXTUAL_PACKAGES = ["torch", "transformers"]


def check_packages(packages: list[str]) -> bool:
    passed = True
    for name in packages:
        try:
            module = importlib.import_module(name)
            print(f"[OK] {name}: {getattr(module, '__version__', 'installed')}")
        except Exception as exc:
            passed = False
            print(f"[FAIL] {name}: {exc}")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contextual", action="store_true")
    args = parser.parse_args()
    print(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {sys.version.split()[0]}")
    passed = check_packages(CORE_PACKAGES)
    if args.contextual:
        passed = check_packages(CONTEXTUAL_PACKAGES) and passed
    try:
        import spacy

        spacy.load("en_core_web_sm")
        print("[OK] spaCy model: en_core_web_sm")
    except Exception as exc:
        passed = False
        print(f"[FAIL] spaCy model: {exc}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
