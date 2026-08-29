# Báo Cáo Thực Nghiệm Model 4: Kiểm Định Data Leakage & Đánh Giá Độc Lập

> [!WARNING]
> **TRẠNG THÁI MÔ HÌNH: PILOT / PRELIMINARY RESEARCH ARTIFACT (CHƯA ĐẠT CHUẨN PRODUCTION-READY)**  
> Quy mô dữ liệu hiện tại ($N=100$ mẫu) có phương sai Cross-Validation lớn (CV std xấp xỉ 7-13%). Kết quả dưới đây mang tính chất thăm dò phương pháp luận (Proof-of-Concept), **CẦN MỞ RỘNG TẬP DỮ LIỆU REVIEW (tối thiểu 300-500 MẪU)** trước khi có thể kích hoạt phục vụ tự động trong môi trường sản xuất.

---

## 1. Kiểm Định Data Leakage (Leakage-Prone vs Leakage-Free)

Khi loại bỏ hoàn toàn các đặc trưng nhóm `reason_*` (`reason_count`, `reason_lexical_constraint`, `reason_length_mismatch`, `metric_lexical_ok` - vốn được sinh ra từ chính bộ lọc heuristic chọn mẫu ban đầu), hiệu năng thực tế của các mô hình khi chỉ dựa vào **tín hiệu nội tại của câu (Intrinsic Features: độ dài, CEFR delta, SVD vector, tiền tố/hậu tố)** như sau:

| Mô hình | Cấu hình đặc trưng | Accuracy (OOF) | Precision (Failure) | Recall (Failure) | F1-Score | PR-AUC (Average Prec) | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Extra Trees** | *Có reason_\** | 65.00% | 64.71% | 66.00% | 65.35% | 73.04% | 68.68% |
| **Extra Trees** | **Clean (Không reason_\*)** | **63.00%** | **61.02%** | **72.00%** | **66.06%** | **61.76%** *(CV: 71.11% ± 10.68%)* | **61.96%** |
| **Random Forest** | *Có reason_\** | 68.00% | 68.75% | 66.00% | 67.35% | 65.80% | 65.36% |
| **Random Forest** | **Clean (Không reason_\*)** | **61.00%** | **60.38%** | **64.00%** | **62.14%** | **59.24%** *(CV: 65.00% ± 11.66%)* | **59.76%** |
| **Logistic Reg** | *Có reason_\** | 65.00% | 66.67% | 60.00% | 63.16% | 69.84% | 69.36% |
| **Logistic Reg** | **Clean (Không reason_\*)** | **57.00%** | **57.14%** | **56.00%** | **56.57%** | **55.28%** *(CV: 61.44% ± 8.53%)* | **57.08%** |
| **Gradient Boost** | *Có reason_\** | 54.00% | 53.57% | 60.00% | 56.60% | 59.24% | 54.60% |
| **Gradient Boost** | **Clean (Không reason_\*)** | **56.00%** | **55.17%** | **64.00%** | **59.26%** | **55.76%** *(CV: 61.20% ± 9.70%)* | **56.82%** |

### 🔬 Nhận Xét & Phân Tích Khoa Học:
1. **Mức độ suy giảm khi loại bỏ Heuristic Leakage:**
   - Khi loại bỏ nhóm `reason_*`, Accuracy của Extra Trees giảm từ $65.00\% \to 63.00\%$, PR-AUC giảm từ $73.04\% \to 61.76\%$, Logistic Regression giảm PR-AUC từ $69.84\% \to 55.28\%$.
2. **Khẳng định trung thực:** 
   - Model 4 **vẫn giữ được tín hiệu học máy thực sự trên mức ngẫu nhiên** ($63.00\%$ Accuracy, $72.00\%$ Recall của Extra Trees so với baseline $50.00\%$).
   - Tuy nhiên, phần lớn hiệu năng cao trước đây xuất phát từ việc mô hình "học lại" các cờ heuristic ban đầu.
   - Khi chạy hoàn toàn trên tín hiệu nội tại câu (Intrinsic), mô hình bắt được các mẫu lỗi thông qua độ lệch CEFR, đặc trưng chiều dài và ngữ nghĩa SVD, nhưng độ tin cậy chưa đủ vững chắc để đóng vai trò gate tự động độc lập.

---

## 2. Feature Importances Chuẩn Xác Của Extra Trees (Clean Model)

Dưới đây là bảng đóng góp đặc trưng thực tế trích xuất trực tiếp từ `feature_importances_` (Gini Impurity reduction) của mô hình **Extra Trees (100 cây, max_depth=4)** trên tập dữ liệu sạch:

| Thứ hạng | Tên đặc trưng | Tầm quan trọng (Gini Importance) | Tỷ trọng % | Ý nghĩa bản chất |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `pred_level_num` | **0.0884** | **8.84%** | Cấp độ CEFR dự đoán thực tế từ Model 2b |
| **2** | `exp_level_num` | **0.0865** | **8.65%** | Cấp độ CEFR yêu cầu (Càng cao càng dễ sinh lỗi - Hạn chế h) |
| **3** | `is_high_target` | **0.0824** | **8.24%** | Cờ nhị phân đánh dấu từ mục tiêu thuộc nhóm khó (B2/C1) |
| **4** | `is_long_sentence` | **0.0672** | **6.72%** | Cờ đánh dấu câu có độ dài lớn (>= 25 từ) |
| **5** | `text_svd_1` | **0.0624** | **6.24%** | Vector ngữ nghĩa SVD thành phần 1 |
| **6** | `is_model3a` | **0.0581** | **5.81%** | Cờ mô hình sinh (Model 3a) |
| **7** | `is_model1` | **0.0498** | **4.98%** | Cờ mô hình dịch (Model 1) |
| **8** | `has_cefr_levels` | **0.0469** | **4.69%** | Mẫu có định danh cấp độ CEFR |
| **9** | `text_svd_0` | **0.0460** | **4.60%** | Vector ngữ nghĩa SVD thành phần 0 |
| **10** | `text_svd_5` | **0.0439** | **4.39%** | Vector ngữ nghĩa SVD thành phần 5 |

---

## 3. Đánh Giá Độ Ổn Định (Stability Analysis) & Đề Xuất Quy Trình

1. **Phương sai Folds còn cao:** Độ lệch chuẩn Cross-Validation ở mức $\pm 8.5\% - 13.0\%$, cho thấy với cỡ mẫu $N=100$, sự phân bổ các ca lỗi cú pháp phức tạp giữa các fold vẫn tạo ra biến động đáng kể.
2. **Khuyến nghị sử dụng thực tế:**
   - Model 4 hiện tại nên được định vị là **Bộ Lọc Cảnh Báo Sơ Bộ (Warning / Advisory Heuristic)**, hỗ trợ gợi ý các câu nghi ngờ cho giảng viên/người dùng xem lại, **chưa thể tự động chặn (Hard-block)** độc lập trong serving pipeline.
   - Để đạt chuẩn Production-ready, cần mở rộng thu thập dữ liệu feedback thật từ người dùng trong quá trình sử dụng hệ thống để đạt quy mô tối thiểu **300 - 500 mẫu reviewed**.
