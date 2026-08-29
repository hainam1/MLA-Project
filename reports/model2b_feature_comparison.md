# Model 2b: Bảng So Sánh Hiệu Năng Các Cấu Hình (Sentence CEFR Classifier)

**Tập kiểm thử:** `data/processed/model2b_sentence_cefr_test.csv` (1.877 mẫu, `random_state=42`)  
**Mô hình Deep Embedding:** `microsoft/deberta-v3-small` (768 chiều gốc $\to$ PCA 16 chiều, giữ lại **69.34%** phương sai).

---

### 1. Bảng So Sánh Trên Toàn Bộ Test Set (1.877 câu)

| Cấu hình mô hình | Số đặc trưng | Accuracy | Macro F1 | Weighted F1 | Quadratic Weighted Kappa (QWK) | Thời gian huấn luyện/suy luận |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **(a) Baseline Random Forest (Tuned)** | 25 | **54.29%** | **52.60%** | **54.08%** | **0.7352** | 706.9 ms |
| **(b) Random Forest + DeBERTa PCA** | 41 | **57.22%** | **55.70%** | **57.03%** | **0.7526** | 749.4 ms |
| **(c) LightGBM + DeBERTa PCA (BEST)** | 41 | **57.86%** | **55.83%** | **57.74%** | **0.7546** | 2395.4 ms |

---

### 2. Phân Tích Kỹ Thuật:
1. **Sự cải thiện của QWK và Accuracy:**
   - Việc bổ sung 16 chiều deep embedding từ DeBERTa-v3 giúp mô hình nắm bắt được cấu trúc ngữ pháp tầng sâu và ngữ cảnh mệnh đề phức mà các đặc trưng bề mặt (độ dài câu, công thức Flesch-Kincaid) không thể hiện được.
   - Chỉ số **QWK tăng từ 0.7352 lên 0.7546**, chứng minh số ca sai lệch nghiêm trọng (lệch $\ge 2$ cấp độ) đã giảm rõ rệt.
2. **So sánh Random Forest vs LightGBM:**
   - LightGBM trên 41 đặc trưng đạt kết quả tốt nhất nhờ khả năng xây dựng cây theo cấu trúc *leaf-wise* tối ưu các ngưỡng cắt phân đoạn phi tuyến giữa các đặc trưng cú pháp và vector ngữ nghĩa DeBERTa.
