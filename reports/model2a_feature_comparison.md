# Model 2a: Bảng So Sánh Các Cấu Hình Huấn Luyện (Model 2a Feature Comparison)

**Tập kiểm thử:** `data/processed/model2a_word_cefr_test.csv` (Đúng **765 mẫu**, `random_state=42`)  
*(Ghi chú: Toàn bộ tập dữ liệu gốc gồm 3.584 Train + 767 Val + 765 Test = 5.116 mẫu).*  
**Semantic Embedding PCA:** 32 thành phần từ GloVe 100D dense vectors, Explained Variance Ratio = **62.51%** (Vượt ngưỡng yêu cầu giữ lại > 50% phương sai).

---

### 1. Bảng So Sánh Hiệu Năng Trên Toàn Bộ Test Set (765 mẫu)

| Cấu hình mô hình | Số đặc trưng | Accuracy | Macro F1 | Weighted F1 | Selective Accuracy (Calibrated, Cov $\approx 25\%$) | Selective Accuracy (Thresh=0.42) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **(a) Baseline Logistic Regression (6 feats)** | 6 | **36.08%** *(276/765)* | **36.65%** | **35.38%** | **44.44%** *(Cov=20.0%, T=1.1594)* | **43.09%** *(Cov=23.7%)* |
| **(b) Logistic Regression + Morphology (22 feats)** | 22 | **34.51%** *(264/765)* | **35.18%** | **33.19%** | **43.33%** *(Cov=27.5%)* | **43.33%** *(Cov=27.5%)* |
| **(c1) Full Features: Logistic Regression** | 54 | **41.18%** *(315/765)* | **41.28%** | **40.79%** | **45.57%** *(Cov=60.5%)* | **45.57%** *(Cov=60.5%)* |
| **(c2) Full Features: LightGBM (BEST)** | 54 | **42.61%** *(326/765)* | **43.73%** | **42.49%** | **51.53%** *(Cov=25.6%, T=1.4796)* | **47.07%** *(Cov=53.6%)* |
| **(c3) Full Features: Ordinal Logistic Regression** | 54 | **30.72%** *(235/765)* | **28.45%** | **25.88%** | **32.51%** *(Cov=68.8%)* | **32.51%** *(Cov=68.8%)* |

---

### 2. Hiệu Chuẩn Xác Suất Độc Lập Cho LightGBM (Temperature Scaling trên Val Set)
- Tham số nhiệt độ tối ưu cho LightGBM được khớp trên tập Validation (767 mẫu): **$T = 1.4796$**.
- Bảng độ chính xác chọn lọc (Selective Accuracy) theo ngưỡng tin cậy sau hiệu chuẩn:
  - Ngưỡng **0.35**: Selective Accuracy = **44.27%** | Coverage = **84.4%** (646/765 mẫu)
  - Ngưỡng **0.40**: Selective Accuracy = **47.96%** | Coverage = **64.1%** (490/765 mẫu)
  - Ngưỡng **0.42**: Selective Accuracy = **47.07%** | Coverage = **53.6%** (410/765 mẫu)
  - Ngưỡng **0.50**: Selective Accuracy = **51.53%** | Coverage = **25.6%** (196/765 mẫu — ở mức coverage tương đương baseline 20-25%, selective accuracy tăng từ 44.44% lên 51.53%).

---

### 3. Phân Tích So Sánh Khoa Học
1. **LightGBM (c2) vượt trội (+6.53% Accuracy, +7.08% Macro F1):**
   - Sự kết hợp giữa cây quyết định tăng cường gradient phi tuyến tính với 54 đặc trưng (Tần suất + Hình thái + Vector nhúng) cho phép nắm bắt các tương tác phức tạp (ví dụ: từ ngắn nhưng có tiền tố/hậu tố hiếm hoặc vị trí vector ngữ nghĩa đặc thù).
2. **Tại sao Ordinal Regression (c3) đạt kết quả thấp nhất (30.72%)?**
   - Ordinal Logistic Regression giả định tính đơn điệu song song (proportional odds assumption). Trong thực tế phân loại cấp độ từ vựng tiếng Anh, ranh giới giữa A2, B1, B2 không hoàn toàn tuyến tính trên không gian vector, dẫn đến việc phân chia ngưỡng bị lệch nghiêm trọng ở các lớp giữa.
3. **Tại sao thêm riêng Morphology vào Logistic Regression (b) không tăng Accuracy?**
   - Các đặc trưng tiền tố/hậu tố có tính thưa (sparse binary features). Trong mô hình tuyến tính đơn giản không có tương tác phi tuyến, các đặc trưng thưa này bị nhiễu và lấn át bởi tần suất Zipf nếu không có mô hình cây hoặc vector nhúng đi kèm.
