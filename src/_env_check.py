"""
Environment Verification Script for CapyVocab ML.
Checks all core library imports, hardware availability (CPU/GPU/CUDA), and system info.
"""

import sys
import platform

# Ensure UTF-8 output encoding for Windows terminal
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def p(msg=""):
    print(msg, flush=True)

def test_imports():
    packages = [
        ("torch", "PyTorch"),
        ("transformers", "Hugging Face Transformers"),
        ("datasets", "Hugging Face Datasets"),
        ("sklearn", "Scikit-Learn"),
        ("xgboost", "XGBoost"),
        ("wordfreq", "Wordfreq (Zipf frequency)"),
        ("textstat", "Textstat (Readability scores)"),
        ("sacrebleu", "SacreBLEU (Translation metrics)"),
        ("pyphen", "Pyphen (Syllable counting)"),
        ("spacy", "spaCy (Syntactic & POS NLP)"),
    ]

    p("=" * 65)
    p("KIEM TRA IMPORT CAC THU VIEN COT LOI (CAPYVOCAB ML)")
    p("=" * 65)

    success_count = 0
    for module_name, label in packages:
        try:
            mod = __import__(module_name)
            ver = getattr(mod, "__version__", "installed")
            p(f"  [OK]  {label:35} : v{ver}")
            success_count += 1
        except ImportError as e:
            p(f"  [FAIL] {label:35} : Chua cai dat ({e})")
        except Exception as e:
            p(f"  [ERR]  {label:35} : Loi khi nap ({e})")

    # Kiem tra model spacy en_core_web_sm
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("CapyVocab makes learning English vocabulary easy.")
        p(f"  [OK]  {'spaCy Model (en_core_web_sm)':35} : Loaded successfully ({len(doc)} tokens)")
        success_count += 1
    except Exception as e:
        p(f"  [FAIL] {'spaCy Model (en_core_web_sm)':35} : ❌ Failed to load ({e})")

    total_checks = len(packages) + 1
    p("-" * 65)
    p(f"Ti le kiem tra thanh cong: {success_count}/{total_checks}")
    p("=" * 65)
    return success_count == total_checks

def test_hardware():
    p("\n" + "=" * 65)
    p("KIEM TRA THONG TIN PHAN CUNG & ACCELERATOR")
    p("=" * 65)
    p(f"  He dieu hanh    : {platform.system()} {platform.release()} ({platform.machine()})")
    p(f"  Python Version  : {sys.version.split()[0]}")

    try:
        import torch
        cuda_available = torch.cuda.is_available()
        p(f"  torch.cuda.is_available() : {cuda_available}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            p(f"  So luong GPU              : {device_count}")
            for i in range(device_count):
                p(f"    - GPU {i}                : {torch.cuda.get_device_name(i)}")
            p(f"  CUDA Version              : {torch.version.cuda}")
            p(f"  cuDNN Version             : {torch.backends.cudnn.version()}")
            p("\n  👉 KET LUAN: Local CO GPU ho tro CUDA (NVIDIA). Co the train truc tiep cac model tren may local!")
        else:
            p("\n  👉 KET LUAN: Local KHONG co GPU CUDA (CPU Only). Cac model nang (Seq2Seq / DeBERTa fine-tuning) nen train tren Google Colab / Kaggle GPU.")
    except ImportError:
        p("  PyTorch chua duoc cai dat, khong the kiem tra CUDA.")

    p("=" * 65)

if __name__ == "__main__":
    test_imports()
    test_hardware()
