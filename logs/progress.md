# Nhật Ký Tiến Độ Dự Án (Project Progress Log)

Tài liệu ghi lại toàn bộ quá trình phát triển, các quyết định kỹ thuật, thử nghiệm và kết quả theo từng buổi làm việc nhằm phục vụ báo cáo và bảo vệ đề tài CapyVocab ML.

---

## [2026-08-27]
- **Việc đã làm:**
  - Khởi tạo toàn bộ cấu trúc thư mục dự án Machine Learning theo chuẩn: `data/` (`raw`, `interim`, `processed`), `notebooks/`, `src/` (`data`, `models/translator`, `models/cefr_classifier`, `models/example_generator`, `models/second_pair_of_eyes`, `eval`, `pipeline`), `reports/figures/`, `configs/`, `logs/`, `tests/`.
  - Thiết lập Git repository (`git init`) và cấu hình `.gitignore` loại bỏ các file nặng (`data/raw/*`, `*.ckpt`, `*.pt`, `*.bin`, `*.safetensors`, `.venv/`, `logs/*.log`, `__pycache__/`).
  - Viết tài liệu `README.md` mô tả tổng quan kiến trúc 4 modules và hướng dẫn cài đặt.
  - Khởi tạo file `configs/config.yaml` khung sườn chứa cấu hình tập trung cho toàn bộ pipeline.
  - Tạo môi trường ảo `.venv` (Python 3.12) và cài đặt đầy đủ các thư viện trong `requirements.txt` (Deep Learning, NLP, Linguistic Features, Evaluation, Quality Assurance).
  - Viết và thực thi script kiểm tra môi trường `src/_env_check.py` để kiểm tra import 9 thư viện cốt lõi (`torch`, `transformers`, `datasets`, `sklearn`, `xgboost`, `wordfreq`, `textstat`, `sacrebleu`, `pyphen`) cùng trạng thái tăng tốc phần cứng (CUDA/GPU). Toàn bộ 9/9 thư viện nạp thành công [OK].
  - Kiểm tra phần cứng: Nhận diện GPU NVIDIA GeForce RTX 5060 Laptop GPU với CUDA khả dụng (`torch.cuda.is_available() = True`).

- **Vấn đề gặp phải:**
  - Python mặc định không nằm trong PATH hệ thống; đã sử dụng `uv` với CPython 3.12 để tạo `.venv` và cài đặt các thư viện Deep Learning.
  - Xảy ra xung đột phiên bản giữa `datasets`, `pyarrow` và `huggingface-hub` khi nâng cấp; đã giải quyết triệt để bằng cách cố định `datasets>=3.0.0,<3.5.0`, `pyarrow<19.0.0` và `huggingface-hub<1.0,>=0.34.0`.
  - GPU NVIDIA GeForce RTX 5060 thuộc kiến trúc mới (Compute Capability sm_120); PyTorch 2.6 CUDA 12.4 nhận diện được CUDA nhưng cảnh báo kiến trúc native sm_120. Máy local có thể chạy tốt inference và training các model nhẹ/vừa, nhưng khuyến nghị kết hợp Google Colab / Kaggle GPU (T4/A100) khi huấn luyện các mô hình Seq2Seq / DeBERTa kích thước lớn để đạt hiệu năng tối đa.

- **Việc tiếp theo:**
  - Chuyển sang Phase 1: Thu thập và tiền xử lý dữ liệu (Data Pipeline).
  - Tải và xử lý các tập dữ liệu từ vựng song ngữ, CEFR wordlist, và ngữ cảnh mẫu.
