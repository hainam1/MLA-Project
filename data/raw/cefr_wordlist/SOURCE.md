# CEFR Wordlist Corpus Sources & Licensing (Model 2a: Word Classifier)

Tài liệu ghi lại nguồn gốc, quy mô, cấu trúc và giấy phép (license) của tập dữ liệu phân loại độ khó từ vựng theo CEFR.

---

## 1. Nguồn Dữ Liệu: Zenodo Record 12501 (Istanbul Sehir University)
- **Tên nghiên cứu**: *"Classification of word levels with usage frequency, expert opinions and machine learning"*
- **Tác giả**: Onur Guzey, Gihad Sohsah, Muhammed Unal (Istanbul Sehir University, 2014).
- **Zenodo DOI**: [`10.5281/zenodo.12501`](https://doi.org/10.5281/zenodo.12501)
- **License**: **Creative Commons Attribution 4.0 International (CC-BY-4.0)** — Hoàn toàn tự do sử dụng cho mục đích học thuật, giảng dạy và nghiên cứu kèm trích dẫn tác giả.

---

## 2. Cấu Trúc Các Tệp Dữ Liệu Thu Thập:

| Tên tệp | Số lượng mẫu | Các trường dữ liệu chính (Columns) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `WordsTeachersLevelsGoogleFrequenciesPredictions.csv` | **7.000 từ** | `Word`, `PoS`, `Teachers Avg`, `Level.Teachers.Average`, `X2000`...`X2008`, `AvrgOfYears`, `Level.Predicted.RF/NN/SVM` | Tập dữ liệu 7.000 từ vựng cốt lõi tiếng Anh có nhãn CEFR do hội đồng 30 giáo viên thẩm định kết hợp tần suất Google N-gram. |
| `SurveyResults.csv` | **21.000 đánh giá** | `Word`, `PoS`, `Teacher.ID`, `Level` | 21.000 lượt chấm điểm độ khó độc lập từ 30 giáo viên tiếng Anh bản ngữ/chuyên gia. |
| `AllDataClassified.csv` | **51.352 từ** | `Word`, `PoS`, `X2000`...`X2008`, `AvrgOfYears`, `Level.Predicted.RF/NN/SVM` | Tập mở rộng hơn 51.000 từ vựng được phân loại tự động bởi các mô hình ML (Random Forest, NN, SVM). |

---

## 📌 Đề xuất sử dụng trong Pipeline:
- Sử dụng tập **7.000 từ chuẩn thẩm định bởi chuyên gia (`WordsTeachersLevelsGoogleFrequenciesPredictions.csv`)** làm Ground Truth chất lượng cao để trích xuất đặc trưng (`src/data/features.py`) và huấn luyện Model 2a (CEFR Word Classifier).
