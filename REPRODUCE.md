# Hướng dẫn tái lập kết quả thực nghiệm (Reproduction Guide)
**ELLIPSE Project — Nhóm 03**

Tài liệu này cung cấp hướng dẫn chi tiết, minh bạch và khả thi để tái lập toàn bộ các kết quả, bảng số liệu và phát hiện thực nghiệm trong Báo cáo cuối kỳ của Nhóm 03.

---

## 1. Nguyên tắc cốt lõi & Cảnh báo an toàn dữ liệu

1. **Tuyệt đối không mở dữ liệu nhãn Official Test:** Mọi lệnh tái lập chỉ chạy trên tập Development (3.812 bài hợp lệ) và tập Validation (762 bài hợp lệ). Không có bất kỳ lệnh nào truy cập nhãn hay dự đoán Official Test.
2. **Phân loại cấp độ thực thi minh bạch:**
   - **[Loại 1] Tái lập nhanh từ dự đoán / số liệu đã lưu (Deterministic Verification):** Thời gian chạy `< 10 giây`, chỉ đọc ma trận dự đoán hoặc bảng số liệu đã chốt để tính toán số học, kiểm tra tính nhất quán, bootstrap và vẽ bảng.
   - **[Loại 2] Huấn luyện lại mô hình từ ma trận đặc trưng (Retraining / Refitting):** Thời gian chạy `1 – 5 phút`, fit lại Ridge Regression hoặc Random Forest trên 5-fold GroupKFold hoặc 3.050 bài `model_train`.
   - **[Loại 3] Chạy lại trích xuất đặc trưng / Mô hình nơ-ron sâu (Neural Inference / GEC Pipeline):** Thời gian chạy `nhiều phút đến hàng giờ`, yêu cầu môi trường chuyên dụng (`.venv_gec`), PyTorch và checkpoint mô hình nặng.
3. **Bảo mật văn bản bài viết:** Các file chứa văn bản bài viết thô phục vụ kiểm toán đọc bài nằm hoàn toàn trong thư mục `local_only/` (đã cấu hình trong `.gitignore`) và không bao giờ được đưa lên kho chứa công khai.
4. **Ghi chú về kiểm tra byte-level khi chạy lại:**
   - Khi chạy lại các script đánh giá như `scripts/phase7_evaluate_regression_models.py` hoặc `scripts/phase5_feature_audit_and_baselines.py`, các chỉ số MAE, RMSE, $R^2$ hoàn toàn **trùng khớp 100% đến từng chữ số thập phân**.
   - Tuy nhiên, file CSV xuất ra có thể khác biệt byte so với bản commit gốc do hàm đánh giá nội bộ `regression_metrics` tự động bổ sung thêm cột chỉ số phụ `qwk` (Quadratic Weighted Kappa) vào bảng kết quả, hoặc do chuẩn hóa ký tự xuống dòng (CRLF trên Windows vs LF trên Linux). Vì vậy, dự án giữ nguyên các file kết quả đã khóa trong commit lịch sử để bảo toàn mã băm SHA-256 đã công bố.

---

## 2. Thiết lập môi trường thực thi (Environment Setup)

Dự án sử dụng hai môi trường ảo Python tách biệt để đảm bảo tính cô lập phụ thuộc:

### Môi trường 1: `.venv` (Pipeline chính, Hồi quy, Ngữ pháp LanguageTool)
- **Phiên bản Python:** Python 3.14.5 (hoặc Python 3.10+)
- **Thư viện chính:** `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, `language_tool_python`
- **Mục đích:** Chạy toàn bộ pipeline từ Phase 2 đến Phase 8, cross-validation 5 fold tuần 9, và kiểm toán LanguageTool 6.6.

### Môi trường 2: `.venv_gec` (Neural Transformers, GECToR, Sentence Embeddings)
- **Phiên bản Python:** Python 3.12.13
- **Thư viện chính:** `torch==2.6.0`, `transformers==4.51.3`, `sentence-transformers==4.1.0`, `gector==1.2.0`, `errant==3.0.2`
- **Mục đích:** Trích xuất sentence embedding MiniLM L6 v2, đo lường độ dài cắt token, và suy luận sửa lỗi ngữ pháp GECToR RoBERTa.

---

## 3. Quy trình tuần tự từ đầu (End-to-End Pipeline: Phase 2 đến Phase 6)

Để xây dựng lại toàn bộ pipeline mô hình từ dữ liệu thô:

### Phase 2: Kiểm toán tập dữ liệu toàn thể & Quyền riêng tư
- **Script:** `scripts/phase2_dataset_audit.py`
- **Lệnh:** `.venv\Scripts\python.exe scripts/phase2_dataset_audit.py`
- **Môi trường:** `.venv`
- **Đầu vào:** `data/01_original_source/official_corpus/`, `data/01_original_source/rater_scores/`
- **Đầu ra:** `docs/data/phase2_tables/phase2_audit_summary.json`
- **Thời gian chạy:** ~18 giây.
- **Kết quả kiểm toán:**
  - Tổng số 6.482 bài (3.911 train official + 2.571 test official).
  - Không có bài trống (blank=0), không khuyết điểm (missing=0).
  - 44 prompt phân bố đồng đều.
  - 138 bài bị gắn cờ quyền riêng tư rater được đánh dấu để lọc.

### Phase 3: Phân hoạch chia tập Train/Val/Test cố định
- **Script:** `scripts/phase3_build_split.py`
- **Lệnh:** `.venv\Scripts\python.exe scripts/phase3_build_split.py`
- **Môi trường:** `.venv`
- **Đầu vào:** `data/01_original_source/official_corpus/train.csv`, manifest rater
- **Đầu ra:** `data/02_split_manifest/essay_split_manifest.csv`, `docs/data/phase3_tables/split_audit_summary.json`
- **Thời gian chạy:** ~5 giây.
- **Kết quả:**
  - 3.911 official train chia thành: 3.128 `model_train` và 783 `validation` (stratified theo prompt và hash text, seed 42).
  - Sau cổng quyền riêng tư (`privacy_review_status == not_flagged`): còn đúng **3.050 bài `model_train`** và **762 bài `validation`**. Tổng Development hợp lệ: **3.812 bài**.

### Phase 4: Trích xuất 14 đặc trưng ngôn ngữ giải thích được
- **Script:** `scripts/phase4_extract_features.py`
- **Lệnh:** `.venv\Scripts\python.exe scripts/phase4_extract_features.py`
- **Môi trường:** `.venv` (spaCy `en_core_web_sm`, `language_tool_python`, `lexicalrichness`, `wordfreq`)
- **Đầu vào:** `data/01_original_source/official_corpus/train.csv`, `data/02_split_manifest/essay_split_manifest.csv`
- **Đầu ra:** `data/05_model_features/development_features_with_targets.csv` (SHA256: `cafb1bca2742...`)
- **Thời gian chạy:** `[Loại 3]` ~30–45 phút trên CPU.
- **Trạng thái:** Bảng đặc trưng đã trích xuất hoàn tất và được khóa hash.

### Phase 5: Kiểm toán đặc trưng & Đánh giá baseline độ dài
- **Script:** `scripts/phase5_feature_audit_and_baselines.py`
- **Lệnh:** `.venv\Scripts\python.exe scripts/phase5_feature_audit_and_baselines.py`
- **Môi trường:** `.venv`
- **Đầu vào:** `data/05_model_features/development_features_with_targets.csv`, `data/02_split_manifest/essay_split_manifest.csv`
- **Đầu ra:** `docs/data/phase5_tables/phase5_audit_summary.json`, `baseline_regression_metrics.csv`
- **Thời gian chạy:** ~7 giây.
- **Kết quả kiểm toán:**
  - 14 đặc trưng: 0 missing, 0 infinite, 0 near-constant.
  - Baselines: Mean baseline (Vocab MAE = 0.465594, Grammar MAE = 0.549460); Length-only Ridge (Vocab MAE = 0.436107, Grammar MAE = 0.542828).

### Phase 6: Huấn luyện mô hình chính (Model Training & Grid Search Tuning)
- **Script:** `scripts/phase6_train_models.py`
- **Lệnh kiểm tra tiền điều kiện (Preflight Check — không ghi đè mô hình):**
  ```powershell
  .venv\Scripts\python.exe scripts/phase6_train_models.py --preflight-only
  ```
  *Kết quả preflight trong ~2s:* Xác nhận đầy đủ 3.050 bài `model_train`, 762 bài `validation`, 5 fold PredefinedSplit `{0: 609, 1: 610, 2: 610, 3: 611, 4: 610}`, `ready: true`.
- **Lệnh huấn luyện lại đầy đủ:**
  ```powershell
  .venv\Scripts\python.exe scripts/phase6_train_models.py
  ```
- **Môi trường:** `.venv`
- **Đầu vào:** `data/05_model_features/development_features_with_targets.csv`, `configs/phase6_training.yaml`
- **Đầu ra:** 4 artifact mô hình đã fit trong `outputs/phase6/` (`ridge_vocabulary.joblib`, `ridge_grammar.joblib`, `random_forest_vocabulary.joblib`, `random_forest_grammar.joblib`) và ma trận dự đoán `outputs/phase6/validation_predictions.csv`.
- **Thời gian chạy:** ~2–3 phút.

---

## 4. Hướng dẫn tái lập từng Bảng chính trong Báo cáo

### Bảng 7: Baseline MAE & Hiệu năng hồi quy đơn đích (Regression Performance)
- **Mục tiêu:** Tái lập sai số tuyệt đối trung bình (MAE) của hai mô hình chính (Ridge, Random Forest) và các baseline (Mean, Text-length) trên tập Validation ($N=762$) và Development OOF ($N=3.812$).
- **Phân loại:** **[Loại 1] Tái lập nhanh từ dự đoán đã lưu**
- **Môi trường:** `.venv`
- **Lệnh thực thi:**
  ```powershell
  # 1. Đánh giá trên tập Validation (762 bài):
  .venv\Scripts\python.exe scripts/phase7_evaluate_regression_models.py

  # 2. Đánh giá Mean Baseline trên Development OOF (3.812 bài):
  .venv\Scripts\python.exe scripts/build_interview_sources.py

  # 3. Đánh giá Ridge và Random Forest trên Development OOF (3.812 bài):
  .venv\Scripts\python.exe -c "
  import pandas as pd, numpy as np
  df = pd.read_csv('reports/week10/b2_oof.csv')
  print('Ridge OOF MAE:', np.mean(np.abs(df['Vocabulary'] - df['Ridge_V'])), np.mean(np.abs(df['Grammar'] - df['Ridge_G'])))
  print('RF OOF MAE:   ', np.mean(np.abs(df['Vocabulary'] - df['RF_V'])), np.mean(np.abs(df['Grammar'] - df['RF_G'])))
  "
  ```
- **File đầu vào:**
  - `outputs/phase6/validation_predictions.csv` (SHA256: `6e86fe84b322...`)
  - `data/05_model_features/development_features_with_targets.csv` (SHA256: `cafb1bca2742...`)
  - `reports/week9/t3_heldout_predictions.csv` (SHA256: `15cedfabd362...`)
  - `reports/week10/b2_oof.csv` (SHA256: `ed51bdded954...`)
- **File đầu ra:**
  - `docs/data/phase7_tables/regression_metrics.csv`
  - `docs/data/phase7_tables/baseline_comparisons.csv`
  - `docs/nguon_bao_cao_interview/d1_mean_dev.csv`
- **Thời gian chạy thực tế:** ~12 giây (Phase 7), ~0.85 giây (Dev sources), ~0.4 giây (OOF check).
- **Số liệu đối chiếu:**
  | Tập đánh giá | Mô hình | MAE Vocabulary | MAE Grammar | Nguồn / Lệnh |
  |---|---|---:|---:|---|
  | **Validation (762)** | Mean Baseline (Train Mean) | 0.465594 | 0.549460 | `phase7_evaluate_regression_models.py` |
  | **Validation (762)** | Length-only Ridge | 0.436107 | 0.542828 | `phase7_evaluate_regression_models.py` |
  | **Validation (762)** | Ridge (14 đặc trưng) | 0.374814 | 0.456298 | `phase7_evaluate_regression_models.py` |
  | **Validation (762)** | Random Forest (14 đặc trưng) | 0.372977 | 0.447710 | `phase7_evaluate_regression_models.py` (Point predictor) |
  | **Dev OOF (3.812)** | Mean Baseline (CV Fold Mean) | 0.474015 | 0.564001 | `build_interview_sources.py` (`d1_mean_dev.csv`) |
  | **Dev OOF (3.812)** | Ridge (14 đặc trưng) | 0.373424 | 0.463037 | `reports/week10/b2_oof.csv` (hoặc `t3_heldout_predictions.csv`) |
  | **Dev OOF (3.812)** | Random Forest (14 đặc trưng) | 0.372165 | 0.455404 | `reports/week10/b2_oof.csv` (hoặc `t3_heldout_predictions.csv`) |

---

### Bảng 8: Chiến lược chọn hàng đợi rà soát giáo viên (Review Prioritization)
- **Mục tiêu:** Tái lập tỷ lệ thu giữ lỗi lớn ($L_i = 1[\max(|RF_V-y_V|, |RF_G-y_G|) \ge 1.0]$), độ chính xác và độ lợi (Lift) ở các ngân sách $k = \lceil 0.20 N \rceil$ giữa 4 chiến lược: Random, Shortest-first, Ridge extremity, và Ridge-RF Disagreement ($D$).
- **Phân loại:** **[Loại 1] Tái lập nhanh từ dự đoán đã lưu**
- **Môi trường:** `.venv`
- **Lệnh thực thi:**
  ```powershell
  .venv\Scripts\python.exe scripts/phase8_evaluate_review_prioritization.py
  ```
- **File đầu vào:** `outputs/phase6/validation_predictions.csv`, `data/05_model_features/development_features_with_targets.csv`
- **File đầu ra:** `docs/data/phase8_tables/review_strategy_comparison.csv`
- **Thời gian chạy thực tế:** ~3.2 giây.
- **Ghi chú quan trọng về hàng Random:**
  - Dòng `Random` của script sử dụng **mô phỏng Monte Carlo (1.000 lần rút ngẫu nhiên với seed=42)**, cho kết quả trung bình thực nghiệm là **13,946 bài**.
  - Báo cáo chính thức của nhóm sử dụng **kỳ vọng lý thuyết chính xác (Hypergeometric Expectation):**
    $$\mathbb{E}[C] = \frac{k \times K}{N} = \frac{153 \times 69}{762} = 13,85433... \approx 13,855 \text{ bài}$$
- **Số liệu đối chiếu (Validation $N=762$, Số lỗi lớn $K=69$, Ngân sách $k=153$ - 20%):**
  | Chiến lược rà soát | Số bài chọn ($k$) | Bắt được ($C$) | Tỷ lệ bắt (Capture) | Độ chính xác (Precision) | Lift so với ngẫu nhiên |
  |---|---:|---:|---:|---:|---:|
  | **Kỳ vọng lý thuyết chính xác** | 153 | **13.855** | **20.08%** | **9.06%** | **1.0000** (Tham chiếu chuẩn) |
  | **Random (Monte Carlo 1.000 lượt, seed 42)** | 153 | 13.946 | 20.21% | 9.12% | 1.0066 |
  | **Shortest-first** | 153 | 15.000 | 21.74% | 9.80% | 1.0827 |
  | **Ridge extremity** | 153 | 10.000 | 14.49% | 6.54% | 0.7218 |
  | **Ridge-RF Disagreement ($D$)** | 153 | 15.000 | 21.74% | 9.80% | 1.0827 |

---

### Bảng 9: Tính cực đoan và nén phương sai của Ridge (Extremity & Variance Shrinkage)
- **Mục tiêu:** Phân tích định lượng hiện tượng nén phương sai (shrinkage) của mô hình hồi quy Ridge và Random Forest trên cả hai tập: Validation ($N=762$) và Development OOF ($N=3.812$).
- **Phân loại:** **[Loại 1] Đọc kết quả đã lưu, chưa chạy lại script**
- **Môi trường:** `.venv`
- **Lệnh tra cứu & kiểm chứng số học nhanh:**
  ```powershell
  # 1. Tra cứu bảng kết quả đã chốt tại commit e88d82c:
  # reports/week10/RESULTS_week10.md (Part B: Validation dòng 31-90, Development OOF dòng 97-120)

  # 2. Hoặc kiểm chứng số học trực tiếp từ ma trận dự đoán b2_oof.csv:
  .venv\Scripts\python.exe -c "
  import pandas as pd, numpy as np
  from scipy.stats import pearsonr
  df = pd.read_csv('reports/week10/b2_oof.csv')
  for t, rf_col, r_col in [('Vocabulary', 'RF_V', 'Ridge_V'), ('Grammar', 'RF_G', 'Ridge_G')]:
      y = df[t].to_numpy(); rf_p = df[rf_col].to_numpy(); r_p = df[r_col].to_numpy()
      sd_y = np.std(y, ddof=0)
      print(f'{t} Dev RF:    SD_true={sd_y:.6f}, SD_pred={np.std(rf_p, ddof=0):.6f}, ratio={np.std(rf_p, ddof=0)/sd_y:.6f}, r={pearsonr(y, rf_p)[0]:.6f}')
      print(f'{t} Dev Ridge: SD_true={sd_y:.6f}, SD_pred={np.std(r_p, ddof=0):.6f}, ratio={np.std(r_p, ddof=0)/sd_y:.6f}, r={pearsonr(y, r_p)[0]:.6f}')
  "
  ```
  *(Lưu ý: Script `scripts/week10/spread_analysis.py` có cơ chế kiểm toán chặt chẽ qua `sys.addaudithook` và khóa chống ghi đè duplicate append vào `RESULTS_week10.md`. Số liệu dưới đây được đọc trực tiếp từ kết quả đã lưu và khớp hoàn toàn với phép tính OOF ở lệnh trên).*
- **Số liệu đối chiếu:**
  - **Tập Validation ($N=762$):**
    - Ridge Vocabulary: $SD_{true}=0.5737$, $SD_{pred}=0.3362$ $\rightarrow$ Ratio = **0.5860**, Pearson $r=0.5527$.
    - Ridge Grammar: $SD_{true}=0.6815$, $SD_{pred}=0.4022$ $\rightarrow$ Ratio = **0.5901**, Pearson $r=0.5697$.
    - RF Vocabulary: $SD_{true}=0.5737$, $SD_{pred}=0.3098$ $\rightarrow$ Ratio = **0.5399**, Pearson $r=0.5478$.
    - RF Grammar: $SD_{true}=0.6815$, $SD_{pred}=0.3882$ $\rightarrow$ Ratio = **0.5695**, Pearson $r=0.5818$.
  - **Tập Development OOF ($N=3.812$):**
    - Ridge Vocabulary: $SD_{true}=0.5842$, $SD_{pred}=0.3397$ $\rightarrow$ Ratio = **0.5815**, Pearson $r=0.5850$.
    - Ridge Grammar: $SD_{true}=0.7011$, $SD_{pred}=0.4068$ $\rightarrow$ Ratio = **0.5802**, Pearson $r=0.5716$.
    - RF Vocabulary: $SD_{true}=0.5842$, $SD_{pred}=0.3114$ $\rightarrow$ Ratio = **0.5331** (~0.533), Pearson $r=0.5874$ (~0.587).
    - RF Grammar: $SD_{true}=0.7011$, $SD_{pred}=0.3929$ $\rightarrow$ Ratio = **0.5604** (~0.560), Pearson $r=0.5862$ (~0.586).
  - **Tỷ lệ bài thật cực đoan bị dự đoán dồn vào dải giữa [2.5, 4.0] (Validation):**
    - Vocab thật $\ge 4.5$ ($n=25$): Ridge dồn **24/25 bài (96.00%)**; RF dồn **22/25 bài (88.00%)**.
    - Vocab thật $\le 2.0$ ($n=29$): Ridge dồn **23/29 bài (79.31%)**; RF dồn **28/29 bài (96.55%)**.
    - Grammar thật $\ge 4.5$ ($n=27$): Ridge dồn **27/27 bài (100.00%)**; RF dồn **26/27 bài (96.30%)**.
    - Grammar thật $\le 2.0$ ($n=113$): Ridge dồn **82/113 bài (72.57%)**; RF dồn **81/113 bài (71.68%)**.

---

### Bảng 10: Thay thế nguồn thông tin (B1 TF-IDF, B2 MiniLM L6 v2)
- **Mục tiêu:** Kiểm định xem tín hiệu bất đồng $D$ có phải là hệ quả riêng của 14 đặc trưng đóng băng hay không, bằng cách thay thế bằng:
  - **B1:** Văn bản n-gram thuần túy (TF-IDF unigram + bigram, $\min\_df=5$, Ridge $\alpha=10$).
  - **B2:** Mô hình biểu diễn câu nơ-ron trước huấn luyện (`all-MiniLM-L6-v2` 384-dim, encoder đóng băng, Ridge $\alpha=10$).
- **Phân loại:**
  - One-liner đọc ma trận OOF: **[Loại 1] Đã chạy thử (thực thi trong 0.6s)**
  - Huấn luyện lại B1 TF-IDF: **[Loại 2] Chưa chạy thử (đã có kết quả lưu, dự kiến ~45s)**
  - Huấn luyện lại B2 MiniLM: **[Loại 3] Chưa chạy thử (đã có kết quả lưu, dự kiến ~3-5m, yêu cầu `.venv_gec`)**
- **Lệnh thực thi:**
  ```powershell
  # [Loại 1 - ĐÃ CHẠY THẬT] Đọc ma trận OOF 3.812 bài từ file lưu:
  .venv\Scripts\python.exe -c "
  import pandas as pd, numpy as np
  df = pd.read_csv('reports/week10/b2_oof.csv')
  for m, v, g in [('RF_14feat', 'RF_V', 'RF_G'), ('Ridge_14feat', 'Ridge_V', 'Ridge_G'), ('B1_TFIDF', 'B1_V', 'B1_G'), ('B2_MiniLM', 'B2_V', 'B2_G')]:
      print(f'{m}: MAE_V={np.mean(np.abs(df[\"Vocabulary\"]-df[v])):.6f}, MAE_G={np.mean(np.abs(df[\"Grammar\"]-df[g])):.6f}, LargeErr={(np.maximum(np.abs(df[\"Vocabulary\"]-df[v]), np.abs(df[\"Grammar\"]-df[g]))>=1.0).sum()}')
  "
  ```
- **Số liệu đối chiếu (Development OOF 3.812 bài):**
  | Nguồn thông tin | MAE Vocabulary | MAE Grammar | Số ca sai lớn ($L_i \ge 1.0$) | Số ca cùng sai lớn với RF | Tỷ lệ bắt $D$ ($k=764$) |
  |---|---:|---:|---:|---:|---:|
  | **RF (14 đặc trưng)** | 0.372165 | 0.455404 | 386 | — | — |
  | **Ridge (14 đặc trưng)** | 0.373424 | 0.463037 | 384 | 276 / 386 | 88 / 386 (Kỳ vọng 77.36) |
  | **B1 (TF-IDF n-grams)** | 0.406626 | 0.506841 | 483 | 233 / 386 | 81 / 386 (Kỳ vọng 77.36) |
  | **B2 (MiniLM sentence emb)**| 0.404448 | 0.507500 | 519 | 217 / 386 | 93 / 386 (Kỳ vọng 77.36) |

---

### Bảng 18: Tỷ lệ bắt lỗi lớn $D$ theo từng fold (Fold-level D capture)
- **Mục tiêu:** Tái lập bảng chi tiết số bài bắt được theo từng fold của GroupKFold 5 fold theo cụm đề trên 3.812 bài Development, và tính khoảng tin cậy Bootstrap cụm đề (Prompt-cluster bootstrap 2.000 lượt).
- **Phân loại:** **[Loại 1] Tái lập nhanh từ dự đoán đã lưu & Bootstrap**
- **Môi trường:** `.venv`
- **Lệnh thực thi:**
  ```powershell
  .venv\Scripts\python.exe scripts/calculate_c_cluster_bootstrap.py
  ```
- **File đầu vào:** `reports/week9/t3_heldout_predictions.csv`, `reports/week10/b2_oof.csv`
- **File đầu ra:** `docs/final_evidence/c_cluster_bootstrap.csv`, `docs/nguon_bao_cao_interview/e5_bat_theo_fold.csv`
- **Thời gian chạy thực tế:** ~1.5 giây.
- **Số liệu đối chiếu từng fold:**
  | Fold | Số bài ($N_f$) | Số lỗi lớn RF ($K_f$) | Ngân sách ($k_f$) | $D$ bắt ($C_f$) | Kỳ vọng ngẫu nhiên ($k_f K_f / N_f$) | $p$-value Hypergeometric |
  |---|---:|---:|---:|---:|---:|---:|
  | **Fold 1** | 769 | 73 | 154 | 15 | 14.6190 | 0.5045 |
  | **Fold 2** | 768 | 88 | 154 | 22 | 17.6458 | 0.1384 |
  | **Fold 3** | 761 | 75 | 153 | 20 | 15.0788 | 0.0925 |
  | **Fold 4** | 745 | 76 | 149 | 17 | 15.2000 | 0.3396 |
  | **Fold 5** | 769 | 74 | 154 | 14 | 14.8192 | 0.6486 |
  | **Tổng (Pooled)** | **3.812** | **386** | **764** | **88** | **77.3629** | **0.0884** (tích chập PMF) |

- **Khoảng tin cậy Bootstrap cụm đề (Prompt-cluster, 44 cụm, 2.000 lượt, seed=42):**
  - $D_{MiniLM} - D_{cũ} = +5$ $\rightarrow$ **95% CI: [-17.0, +26.0]** (66.10% lượt dương, khoảng chứa 0 $\rightarrow$ Chưa chứng minh hơn $D$ cũ).
  - $D_{TF-IDF} - D_{cũ} = -7$ $\rightarrow$ **95% CI: [-27.0, +12.0]** (24.30% lượt dương, khoảng chứa 0).
  - $D_{MiniLM} - \text{Kỳ vọng ngẫu nhiên} = +15.637$ $\rightarrow$ **95% CI: [+0.638, +31.032]** (97.95% lượt dương, cận dưới > 0 ổn định qua seed 42, 43, 44, 45).
  - $D_{TF-IDF} - \text{Kỳ vọng ngẫu nhiên} = +3.637$ $\rightarrow$ **95% CI: [-9.995, +18.841]** (69.85% lượt dương, chứa 0).

---

### Bảng 20: Đối chiếu công cụ đếm lỗi ngữ pháp (LanguageTool 6.6 vs GECToR + ERRANT)
- **Mục tiêu:** So sánh số đếm lỗi trên cùng cửa sổ 150 từ đầu tiên giữa người đọc độc lập, LanguageTool 6.6 (`ruleIssueType=grammar`) và GECToR v1.2.0 + ERRANT v3.0.2 trên 68 bài Validation (36 bài ngẫu nhiên phân tầng + 32 bài ca lỗi tuần 9).
- **Phân loại & Trạng thái chạy thực tế:**
  - **LanguageTool 6.6:** Được chạy lại thật 100% trên cả 10 bài sanity check và 68 bài Validation (mất ~65 giây).
  - **GECToR v1.2.0 + ERRANT v3.0.2:** Đọc từ số đếm đã lưu trong `reports/week10/gec_part_a_68.csv` (chưa chạy lại mô hình nơ-ron từ đầu để tiết kiệm thời gian, mô hình này yêu cầu `.venv_gec` và tốn khoảng 5–10 phút).
- **Lệnh thực thi:**
  ```powershell
  .venv\Scripts\python.exe scripts/calculate_d_tool_agreement.py
  ```
- **File đầu vào:** `data/03_clean_ready_to_use/validation_783.csv`, `reports/week10/gec_part_a_68.csv`, `docs/final_evidence/a_doi_chieu_so_lieu.csv`
- **File đầu ra:** `docs/final_evidence/d_tool_window_counts.csv`, `docs/final_evidence/d_tool_agreement.csv`
- **Thời gian chạy thực tế:** ~65 giây.
- **Số liệu đối chiếu trên cùng cửa sổ 150 từ đầu:**
  | Nhóm bài | Công cụ | Số đếm TB | Độ lệch so với người (Bias) | Spearman $r$ với người | 95% Bootstrap CI của $r$ |
  |---|---|---:|---:|---:|---:|
  | **Mẫu ngẫu nhiên (36 bài)** | Người đọc độc lập | 7.3333 | — | — | — |
  | | LanguageTool 6.6 (chạy lại) | 1.2222 | -6.1111 (thiếu nặng) | 0.7081 | [0.4797, 0.8481] |
  | | GECToR + ERRANT (đã lưu) | 14.3333 | +7.0000 (thừa) | 0.7604 | [0.5069, 0.9032] |
  | | *Hiệu số (GECToR - LT)* | — | — | **+0.0522** | **[-0.0851, +0.1915]** (chứa 0) |
  | **Mẫu ca lỗi tuần 9 (32 bài)** | Người đọc độc lập | 9.4375 | — | — | — |
  | | LanguageTool 6.6 (chạy lại) | 1.4062 | -8.0312 (thiếu nặng) | 0.5234 | [0.2005, 0.7640] |
  | | GECToR + ERRANT (đã lưu) | 14.3125 | +4.8750 (thừa) | 0.8772 | [0.7149, 0.9459] |
  | | *Hiệu số (GECToR - LT)* | — | — | **+0.3538** | **[+0.0873, +0.6621]** |
  | **Gộp (68 bài)** | Người đọc độc lập | 8.3235 | — | — | — |
  | | LanguageTool 6.6 (chạy lại) | 1.3088 | -7.0147 | 0.6229 | [0.4383, 0.7702] |
  | | GECToR + ERRANT (đã lưu) | 14.3235 | +6.0000 | 0.7985 | [0.6468, 0.8913] |
  | | *Hiệu số (GECToR - LT)* | — | — | **+0.1756** | **[+0.0183, +0.3527]** |

---

## 5. Tái lập các Bằng chứng Bổ sung (Mục B và A)

### Mục B: Tỷ lệ bài viết bị cắt bởi tokenizer MiniLM L6 v2
- **Lệnh thực thi:**
  ```powershell
  .venv_gec\Scripts\python.exe scripts/calculate_b_minilm_truncation.py
  ```
- **Thời gian chạy thực tế:** ~10 giây trong `.venv_gec`.
- **Giải thích nhãn phân nhóm:**
  - Nhóm `rf_large_errors_386`: 386 bài Development có sai số RF lớn ($L_i \ge 1.0$).
  - Nhóm `rf_and_minilm_joint_large_errors_217`: 217 bài Development mà cả Random Forest và MiniLM (B2) đều có sai số lớn $\ge 1.0$.
- **Kết quả đối chiếu:**
  - Toàn bộ 3.812 bài Development: **3.378 / 3.812 bài bị cắt (88.6149%)**.
  - Phân bố token: Min = 16, Median = **459.0**, P90 = **761.0**, Max = 1.435.
  - Nhóm RF sai lớn (386 bài): 334 / 386 bài bị cắt (**86.5285%**).
  - Nhóm RF và MiniLM cùng sai lớn (217 bài): 186 / 217 bài bị cắt (**85.7143%**).
  - Tỷ lệ nội dung bị cắt trung bình ở các bài bị cắt: **44.9462%**.
- **File đầu ra:** `docs/final_evidence/b_minilm_truncation.csv`.

### Mục A: Gói đọc mù 10 ca lỗi và Khóa mã băm SHA-256
- **Lệnh thực thi:**
  ```powershell
  .venv\Scripts\python.exe scripts/build_a_reading_pack.py
  .venv\Scripts\python.exe scripts/export_a_evidence.py
  ```
- **Mã băm SHA-256 chốt trước khi gửi người đọc:**
  - Phiếu trống (`phieu_doc_10_ca.xlsx`): `98547da55c8610193036f1e6172c0deabc878badfea9fc2aab5185af32086461`
  - Thư mục đọc trước (`1_doc_truoc/`): `62cf4f28254259169a2ffeb02c125c29c7a62121a1f884c0cf68eaa2c3cf23bc`
- **File bằng chứng đã commit:** `docs/final_evidence/a_reading_pack_hashes.txt`, `docs/final_evidence/a_doi_chieu_so_lieu.csv`.

---

## 6. Bảng tổng hợp mức độ khả thi thực thi (Execution Matrix)

| Bảng / Mục | Phân loại | Môi trường | Lệnh thực thi chính | Đầu vào chính | Đầu ra chính | Thời gian | Trạng thái xác nhận |
|---|---|---|---|---|---|---:|---|
| **Phase 2 (Audit)** | Loại 1 | `.venv` | `phase2_dataset_audit.py` | `official_corpus/` | `phase2_audit_summary.json` | ~18s | **ĐÃ CHẠY THỬ (PASS)** |
| **Phase 3 (Split)** | Loại 1 | `.venv` | `phase3_build_split.py` | `train.csv` | `essay_split_manifest.csv` | ~5s | **ĐÃ CHẠY THỬ (PASS)** |
| **Phase 4 (Features)**| Loại 3 | `.venv` | `phase4_extract_features.py` | `train.csv` | `development_features_with_targets.csv`| ~35m | Chưa chạy lại (đã khóa hash) |
| **Phase 5 (Baseline)**| Loại 1 | `.venv` | `phase5_feature_audit_and_baselines.py`| `development_features_with_targets.csv`| `baseline_regression_metrics.csv` | ~7s | **ĐÃ CHẠY THỬ (PASS)** |
| **Phase 6 (Preflight)**| Loại 1 | `.venv`| `phase6_train_models.py --preflight-only`| `configs/phase6_training.yaml`| Stdout JSON (ready: true) | ~2s | **ĐÃ CHẠY THỬ (PASS)** |
| **Phase 6 (Train)** | Loại 2 | `.venv` | `phase6_train_models.py` | `configs/phase6_training.yaml` | 4 mô hình `.joblib` | ~2.5m | Chưa chạy lại (đã có model lưu) |
| **Bảng 7 (Val)** | Loại 1 | `.venv` | `phase7_evaluate_regression_models.py` | `validation_predictions.csv` | `regression_metrics.csv` | ~12s | **ĐÃ CHẠY THỬ (PASS)** |
| **Bảng 7 (Dev)** | Loại 1 | `.venv` | `build_interview_sources.py` & one-liner | `b2_oof.csv`, `t3_heldout_predictions.csv` | `d1_mean_dev.csv` | ~1.2s | **ĐÃ CHẠY THỬ (PASS)** |
| **Bảng 8** | Loại 1 | `.venv` | `phase8_evaluate_review_prioritization.py` | `validation_predictions.csv` | `review_strategy_comparison.csv` | ~3.5s | **ĐÃ CHẠY THỬ (PASS)** |
| **Bảng 9** | Loại 1 | `.venv` | Tra cứu `RESULTS_week10.md` Part B | `b2_oof.csv` / `RESULTS_week10.md` | `RESULTS_week10.md` | < 1s | **Đọc kết quả đã lưu, chưa chạy lại script** |
| **Bảng 10 (OOF)** | Loại 1 | `.venv` | One-liner Python đọc `b2_oof.csv` | `b2_oof.csv` | In stdout bảng số liệu | < 1s | **ĐÃ CHẠY THỬ (PASS)** |
| **Bảng 10 (B1 Train)**| Loại 2 | `.venv` | `information_sources_oof.py` | `t3_eligible_development.csv` | `b1_oof.csv` | ~45s | Chưa chạy thử (đã có kết quả lưu) |
| **Bảng 10 (B2 Train)**| Loại 3 | `.venv_gec` | `gec_b2.py` | `b2_assets/model` | `b2_oof.csv`, `b2_results.json` | ~3m | Chưa chạy thử (đã có kết quả lưu) |
| **Bảng 18 (Fold)**| Loại 1 | `.venv` | `calculate_c_cluster_bootstrap.py` | `t3_heldout_predictions.csv` | `c_cluster_bootstrap.csv` | ~1.5s | **ĐÃ CHẠY THỬ (PASS)** |
| **Bảng 20 (Agree)**| Loại 1/3 | `.venv` | `calculate_d_tool_agreement.py` | `gec_part_a_68.csv`, raw text | `d_tool_agreement.csv` | ~65s | **ĐÃ CHẠY THỬ (LT chạy thật, GECToR từ lưu)** |
| **Mục B (Cut)** | Loại 3 | `.venv_gec` | `calculate_b_minilm_truncation.py` | `b2_assets/model`, raw text | `b_minilm_truncation.csv` | ~10s | **ĐÃ CHẠY THỬ (PASS)** |
| **Mục A (Pack)** | Loại 1 | `.venv` | `build_a_reading_pack.py` | `t3_heldout_predictions.csv` | `phieu_doc_10_ca.xlsx` | ~2s | **ĐÃ CHẠY THỬ (PASS)** |
