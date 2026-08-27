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
    ]

    p("=" * 60)
    p("KIEM TRA IMPORT CAC THU VIEN COT LOI (CAPYVOCAB ML)")
    p("=" * 60)

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

    p("-" * 60)
    p(f"Ti le thu vien san sang: {success_count}/{len(packages)}")
    p("=" * 60)
    return success_count == len(packages)

def test_hardware():
    p("\n" + "=" * 60)
    p("KIEM TRA THONG TIN PHAN CUNG & ACCELERATOR")
    p("=" * 60)
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

    p("=" * 60)

if __name__ == "__main__":
    test_imports()
    test_hardware()
