# CEFR Sentence Corpus Sources & Licensing (Model 2b: Sentence Classifier)

Tài liệu ghi lại danh sách các bộ dữ liệu độ khó câu theo khung CEFR từ tổ chức **UniversalCEFR** trên Hugging Face Hub.

---

## 1. Danh Sách Các Sub-Dataset Tiếng Anh ở Cấp Độ Câu (Sentence-Level)

Qua rà soát toàn bộ 25 datasets của tổ chức **UniversalCEFR**, các tập dữ liệu thỏa mãn: (a) Tiếng Anh (`en`), (b) Granularity cấp độ câu (`sentence-level`), và (c) License hợp lệ cho nghiên cứu/học thuật:

| Dataset ID | Quy mô | Granularity | Cấp độ nhãn | License | Trạng thái thu thập |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`UniversalCEFR/cefr_sp_en`](https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en) | **10.004 câu** | Sentence-level | A1, A2, B1, B2, C1, C2 | **CC-BY-NC-SA-4.0** | **Đã tải về** (`cefr_sp_en_train.csv`) |
| [`UniversalCEFR/readme_en`](https://huggingface.co/datasets/UniversalCEFR/readme_en) | **2.822 câu** | Sentence-level | A1, A2, B1, B2, C1, C2 | **CC-BY-NC-SA-4.0** | **Đã tải về** (`readme_en_train.csv`) |
| [`UniversalCEFR/cambridge_exams_en`](https://huggingface.co/datasets/UniversalCEFR/cambridge_exams_en) | ~800 câu | Sentence-level | A2, B1, B2, C1 | CC-BY-NC-SA-4.0 | Dự phòng |
| [`UniversalCEFR/elg_cefr_en`](https://huggingface.co/datasets/UniversalCEFR/elg_cefr_en) | ~500 câu | Sentence-level | A1, A2, B1, B2, C1 | CC-BY-NC-4.0 | Dự phòng |
| [`UniversalCEFR/cefr_asag_en`](https://huggingface.co/datasets/UniversalCEFR/cefr_asag_en) | ~600 câu | Short-answer | B1, B2, C1 | CC-BY-NC-SA-4.0 | Dự phòng |

---

## 2. Chi Tiết Các Tệp Đã Thu Thập:

### A. `UniversalCEFR/cefr_sp_en` (Primary Sentence Dataset)
- **Cấu trúc**: `['title', 'lang', 'source_name', 'format', 'category', 'cefr_level', 'license', 'text']`
- **Số lượng**: **10.004 câu** tiếng Anh chuẩn ngữ pháp.
- **Phân bố**: Đầy đủ các cấp độ từ cơ bản đến nâng cao (A1, A2, B1, B2, C1).
- **Mẫu dữ liệu**:
  - A1: *"Is that your bike ?"*
  - A1: *"She had a beautiful necklace around her neck ."*
  - B2: *"Despite the adverse weather conditions, the expedition continued toward the summit."*

### B. `UniversalCEFR/readme_en` (Supplementary Academic Sentence Dataset)
- **Cấu trúc**: `['title', 'lang', 'source_name', 'format', 'category', 'cefr_level', 'license', 'text']`
- **Số lượng**: **2.822 câu** văn phong học thuật, khoa học.
- **Mẫu dữ liệu**:
  - C1: *"The price elasticity of demand depends on the availability of substitutes."*

---

## 📌 Đề xuất sử dụng trong Pipeline:
- Ghép nối 2 tập trên thành bộ dữ liệu chuẩn **~12.800 câu** gán nhãn CEFR để trích xuất đặc trưng cú pháp spaCy, chỉ số đọc hiểu `textstat` và huấn luyện Model 2b (CEFR Sentence Classifier).
