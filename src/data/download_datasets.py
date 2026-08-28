"""
Data Ingestion & Download Script for CapyVocab ML (Phase 1).

Downloads and stages raw datasets for:
1. Model 1 (Translator VI-EN): MTET & IWSLT 2015 -> data/raw/translator_corpus/
2. Model 2a (CEFR Word Classifier): Zenodo Record 12501 -> data/raw/cefr_wordlist/
3. Model 2b (CEFR Sentence Classifier): UniversalCEFR (cefr_sp_en, readme_en) -> data/raw/cefr_sentence/
4. Model 3b (Sentence Rewriter): facebook/asset -> data/raw/sentence_simplification/
"""

import sys
import os
import urllib.request
import tarfile
import pandas as pd
from datasets import load_dataset

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def download_translator_corpus():
    print("\n[1/4] Processing Translator Datasets (VI -> EN)...")
    out_dir = "data/raw/translator_corpus"
    os.makedirs(out_dir, exist_ok=True)

    # 1. MTET Stream Sample
    mtet_path = os.path.join(out_dir, "mtet_sample5k.csv")
    if not os.path.exists(mtet_path):
        print("  - Streaming 5,000 samples from phongmt184172/mtet...")
        ds_mtet = load_dataset("phongmt184172/mtet", split="train", streaming=True)
        samples = []
        for i, item in enumerate(ds_mtet):
            if i >= 5000:
                break
            tr = item.get("translation", {})
            samples.append({"en": tr.get("target", ""), "vi": tr.get("source", "")})
        pd.DataFrame(samples).to_csv(mtet_path, index=False, encoding="utf-8")
        print(f"    Saved: {mtet_path}")
    else:
        print(f"    Already exists: {mtet_path}")

    # 2. IWSLT 2015 en-vi
    iwslt_train_path = os.path.join(out_dir, "iwslt2015_en_vi_train.csv")
    if not os.path.exists(iwslt_train_path):
        print("  - Downloading IWSLT 2015 en-vi splits...")
        ds_iwslt = load_dataset("thainq107/iwslt2015-en-vi")
        for split in ["train", "validation", "test"]:
            df = pd.DataFrame(ds_iwslt[split])
            df.to_csv(
                os.path.join(out_dir, f"iwslt2015_en_vi_{split}.csv"), index=False, encoding="utf-8"
            )
        print(f"    Saved IWSLT splits ({len(ds_iwslt['train'])} train rows)")
    else:
        print(f"    Already exists: {iwslt_train_path}")


def download_cefr_wordlist():
    print("\n[2/4] Processing CEFR Wordlist Dataset (Zenodo 12501)...")
    out_dir = "data/raw/cefr_wordlist"
    os.makedirs(out_dir, exist_ok=True)
    target_csv = os.path.join(out_dir, "WordsTeachersLevelsGoogleFrequenciesPredictions.csv")

    if not os.path.exists(target_csv):
        print("  - Fetching archive from Zenodo Record 12501...")
        archive_path = os.path.join(out_dir, "word-level-survey.tar.gz")
        dl_url = "https://zenodo.org/records/12501/files/word-level-survey.tar.gz?download=1"
        req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(archive_path, "wb") as f:
            f.write(resp.read())
        print(f"    Downloaded: {archive_path}")

        print("  - Extracting archive...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=out_dir)
        print(f"    Extracted files to: {out_dir}")
    else:
        print(f"    Already exists: {target_csv}")


def download_cefr_sentence():
    print("\n[3/4] Processing UniversalCEFR Sentence Datasets...")
    out_dir = "data/raw/cefr_sentence"
    os.makedirs(out_dir, exist_ok=True)

    # 1. CEFR-SP (10,004 sentences)
    sp_path = os.path.join(out_dir, "cefr_sp_en_train.csv")
    if not os.path.exists(sp_path):
        print("  - Downloading UniversalCEFR/cefr_sp_en...")
        ds_sp = load_dataset("UniversalCEFR/cefr_sp_en")
        pd.DataFrame(ds_sp["train"]).to_csv(sp_path, index=False, encoding="utf-8")
        print(f"    Saved: {sp_path} ({len(ds_sp['train'])} rows)")
    else:
        print(f"    Already exists: {sp_path}")

    # 2. README-EN (2,822 sentences)
    readme_path = os.path.join(out_dir, "readme_en_train.csv")
    if not os.path.exists(readme_path):
        print("  - Downloading UniversalCEFR/readme_en...")
        ds_readme = load_dataset("UniversalCEFR/readme_en")
        pd.DataFrame(ds_readme["train"]).to_csv(readme_path, index=False, encoding="utf-8")
        print(f"    Saved: {readme_path} ({len(ds_readme['train'])} rows)")
    else:
        print(f"    Already exists: {readme_path}")


def download_sentence_simplification():
    print("\n[4/4] Processing facebook/asset Simplification Dataset...")
    out_dir = "data/raw/sentence_simplification"
    os.makedirs(out_dir, exist_ok=True)
    val_path = os.path.join(out_dir, "asset_validation.csv")

    if not os.path.exists(val_path):
        print("  - Downloading facebook/asset...")
        ds_asset = load_dataset("facebook/asset")
        pd.DataFrame(ds_asset["validation"]).to_csv(val_path, index=False, encoding="utf-8")
        pd.DataFrame(ds_asset["test"]).to_csv(
            os.path.join(out_dir, "asset_test.csv"), index=False, encoding="utf-8"
        )
        print(
            f"    Saved ASSET splits (validation={len(ds_asset['validation'])}, test={len(ds_asset['test'])})"
        )
    else:
        print(f"    Already exists: {val_path}")


def main():
    print("=" * 70)
    print("CAPYVOCAB ML - DATA COLLECTION PIPELINE (PHASE 1 PART B.1)")
    print("=" * 70)
    download_translator_corpus()
    download_cefr_wordlist()
    download_cefr_sentence()
    download_sentence_simplification()
    print("\n" + "=" * 70)
    print(">>> DATA COLLECTION COMPLETED SUCCESSFULLY! <<<")
    print("=" * 70)


if __name__ == "__main__":
    main()
