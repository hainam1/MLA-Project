# Model 2a: Bảng Xếp Hạng Đóng Góp Đặc Trưng (Feature Importance)

Mô hình phân tích: **LightGBM (Full Features)**

### 1. Tổng quan theo nhóm đặc trưng (Grouped Importance):
| Nhóm đặc trưng | Số lượng | Tỷ lệ đóng góp (%) | Ý nghĩa kỹ thuật |
| :--- | :---: | :---: | :--- |
| **Semantic Embedding (32D PCA Components)** | 32 | **86.10%** | Nắm bắt phân bố ngữ nghĩa và ngữ cảnh xuất hiện của từ trong kho ngữ liệu |
| **Tần suất & Hình thái gốc (Base 6 features)** | 6 | **13.55%** | Tần suất Zipf, tần suất thực tế, độ dài ký tự và số âm tiết |
| **Tiền tố & Hậu tố Morphology (16 features)** | 16 | **0.35%** | Nhận diện hình thái cấu tạo từ học thuật (-tion, -ity, -able, un-, dis-...) |

### 2. Top 15 Đặc trưng đơn lẻ quan trọng nhất:
| Hạng | Tên đặc trưng | Tỷ lệ đóng góp (%) | Nhóm đặc trưng |
| :---: | :--- | :---: | :--- |
| 1 | `wordfreq_zipf` | **9.88%** | Tần suất / Độ dài gốc |
| 2 | `pca_emb_1` | **6.47%** | Semantic Embedding PCA |
| 3 | `pca_emb_5` | **3.89%** | Semantic Embedding PCA |
| 4 | `pca_emb_3` | **3.59%** | Semantic Embedding PCA |
| 5 | `pca_emb_28` | **3.01%** | Semantic Embedding PCA |
| 6 | `pca_emb_21` | **3.00%** | Semantic Embedding PCA |
| 7 | `pca_emb_27` | **2.94%** | Semantic Embedding PCA |
| 8 | `pca_emb_2` | **2.90%** | Semantic Embedding PCA |
| 9 | `pca_emb_6` | **2.89%** | Semantic Embedding PCA |
| 10 | `pca_emb_17` | **2.80%** | Semantic Embedding PCA |
| 11 | `pca_emb_8` | **2.79%** | Semantic Embedding PCA |
| 12 | `pca_emb_23` | **2.78%** | Semantic Embedding PCA |
| 13 | `pca_emb_25` | **2.76%** | Semantic Embedding PCA |
| 14 | `pca_emb_16` | **2.59%** | Semantic Embedding PCA |
| 15 | `pca_emb_9` | **2.53%** | Semantic Embedding PCA |
