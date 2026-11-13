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

## 3. Hướng dẫn tái lập từng Bảng chính trong Báo cáo

### Bảng 7: Baseline MAE & Hiệu năng hồi quy đơn đích (Regression Performance)
- **Mục tiêu:** Tái lập sai số tuyệt đối trung bình (MAE) của hai mô hình chính (Ridge, Random Forest) và các baseline (Mean, Text-length) trên tập Validation ($N=762$) và Development OOF ($N=3.812$).
- **Phân loại:** **[Loại 1] Tái lập nhanh từ dự đoán đã lưu**
- **Môi trường:** `.venv`
- **Lệnh thực thi:**
  ```powershell
  # 1. Đánh giá trên tập Validation (762 bài)
  .venv\Scripts\python.exe scripts/phase7_evaluate_regression_models.py

  # 2. Đánh giá Mean Baseline và OOF trên Development (3.812 bài)
  .venv\Scripts\python.exe scripts/build_interview_sources.py
  ```
- **File đầu vào:**
  - `outputs/phase6/validation_predictions.csv` (SHA256: `6e86fe84b322...`)
  - `data/05_model_features/development_features_with_targets.csv` (SHA256: `cafb1bca2742...`)
  - `reports/week9/t3_heldout_predictions.csv` (SHA256: `15cedfabd362...`)
- **File đầu ra:**
  - `docs/data/phase7_tables/regression_metrics.csv`
  - `docs/data/phase7_tables/baseline_comparisons.csv`
  - `docs/nguon_bao_cao_interview/d1_mean_dev.csv`
- **Thời gian chạy thực tế:** ~12 giây (Phase 7), ~0.85 giây (Dev sources).
- **Số liệu đối chiếu:**
  | Tập đánh giá | Mô hình | MAE Vocabulary | MAE Grammar | Ghi chú |
  |---|---|---:|---:|---|
  | **Validation (762)** | Mean Baseline (Train Mean) | 0.465594 | 0.549460 | Baseline không đặc trưng |
  | **Validation (762)** | Length-only Ridge | 0.436107 | 0.542828 | Chỉ dùng số từ |
  | **Validation (762)** | Ridge (14 đặc trưng) | 0.374814 | 0.456298 | Điểm chốt Phase 6 |
  | **Validation (762)** | Random Forest (14 đặc trưng) | 0.372977 | 0.447710 | Điểm chốt Phase 6 (Point predictor) |
  | **Dev OOF (3.812)** | Mean Baseline (CV Fold Mean) | 0.474015 | 0.564001 | GroupKFold 5-fold OOF |
  | **Dev OOF (3.812)** | Ridge (14 đặc trưng) | 0.373424 | 0.463037 | GroupKFold 5-fold OOF |
  | **Dev OOF (3.812)** | Random Forest (14 đặc trưng) | 0.372165 | 0.455404 | GroupKFold 5-fold OOF |

---

### Bảng 8: Chiến lược chọn hàng đợi rà soát giáo viên (Review Prioritization)
- **Mục tiêu:** Tái lập tỷ lệ thu giữ lỗi lớn ($L_i = 1[\max(|RF_V-y_V|, |RF_G-y_G|) \ge 1.0]$), độ chính xác và độ lợi (Lift) ở các ngân sách $k = \lceil 0.20 N \rceil$ giữa 4 chiến lược: Random, Shortest-first, Ridge extremity, và Ridge-RF Disagreement ($D$).
- **Phân loại:** **[Loại 1] Tái lập nhanh từ dự đoán đã lưu**
- **Môi trường:** `.venv`
- **Lệnh thực thi:**
  ```powershell
  .venv\Scripts\python.exe scripts/phase8_evaluate_review_prioritization.py
  ```
- **File đầu vào:**
  - `outputs/phase6/validation_predictions.csv`
  - `data/05_model_features/development_features_with_targets.csv`
  - `data/02_split_manifest/essay_split_manifest.csv`
- **File đầu ra:**
  - `docs/data/phase8_tables/review_strategy_comparison.csv`
- **Thời gian chạy thực tế:** ~3.2 giây.
- **Số liệu đối chiếu (Validation $N=762$, Số lỗi lớn $K=69$, Ngân sách $k=153$ - 20%):**
  | Chiến lược rà soát | Số bài chọn ($k$) | Bắt được ($C$) | Tỷ lệ bắt (Capture) | Độ chính xác (Precision) | Lift so với ngẫu nhiên |
  |---|---:|---:|---:|---:|---:|
  | **Random (Kỳ vọng 1.000 lượt)** | 153 | 13.946 | 20.21% | 9.12% | 1.0000 (Tham chiếu) |
  | **Shortest-first** | 153 | 15.000 | 21.74% | 9.80% | 1.0827 |
  | **Ridge extremity** | 153 | 10.000 | 14.49% | 6.54% | 0.7218 |
  | **Ridge-RF Disagreement ($D$)** | 153 | 15.000 | 21.74% | 9.80% | 1.0827 |

---

### Bảng 9: Tính cực đoan và nén phương sai của Ridge (Extremity & Variance Shrinkage)
- **Mục tiêu:** Phân tích định lượng hiện tượng nén phương sai (shrinkage) của mô hình hồi quy Ridge và Random Forest. Dự đoán bị co về trung tâm, khiến các bài có điểm thật cực đoan (<2.5 hoặc >4.0) bị dồn vào khoảng giữa [2.5, 4.0].
- **Phân loại:** **[Loại 1] Đọc kết quả kiểm toán đã chốt / [Loại 2] Tái lập bằng refit OOF**
- **Môi trường:** `.venv`
- **Lệnh tra cứu & tái lập:**
  ```powershell
  # Tra cứu bảng số liệu đã chốt tại commit e88d82c:
  # reports/week10/RESULTS_week10.md (Part B, lines 31-90)
  ```
  *(Lưu ý: Script `scripts/week10/spread_analysis.py` có cơ chế kiểm toán chặt chẽ qua `sys.addaudithook` và khóa chống ghi đè duplicate append vào `RESULTS_week10.md`. Khi cần chạy kiểm tra độc lập trên terminal, kết quả in ra stdout trùng khớp hoàn toàn).*
- **File đầu vào:** `reports/week9/t3_eligible_development.csv`, `outputs/phase6/validation_predictions.csv`.
- **Số liệu đối chiếu (Validation $N=762$):**
  - **Tỷ số độ lệch chuẩn ($SD_{pred} / SD_{true}$):**
    - Ridge Vocabulary: $SD_{true}=0.5737$, $SD_{pred}=0.3362$ $\rightarrow$ Ratio = **0.5860** (Nén 41.4%)
    - Ridge Grammar: $SD_{true}=0.6815$, $SD_{pred}=0.4022$ $\rightarrow$ Ratio = **0.5901** (Nén 41.0%)
    - RF Vocabulary: $SD_{true}=0.5737$, $SD_{pred}=0.3098$ $\rightarrow$ Ratio = **0.5399** (Nén 46.0%)
    - RF Grammar: $SD_{true}=0.6815$, $SD_{pred}=0.3882$ $\rightarrow$ Ratio = **0.5695** (Nén 43.0%)
  - **Tỷ lệ bài thật cực đoan bị dự đoán dồn vào dải giữa [2.5, 4.0]:**
    - Điểm thật Vocab $\ge 4.5$ ($n=25$): Ridge dự đoán vào giữa **24/25 bài (96.00%)**; RF **22/25 bài (88.00%)**.
    - Điểm thật Vocab $\le 2.0$ ($n=29$): Ridge dự đoán vào giữa **23/29 bài (79.31%)**; RF **28/29 bài (96.55%)**.
    - Điểm thật Grammar $\ge 4.5$ ($n=27$): Ridge dự đoán vào giữa **27/27 bài (100.00%)**; RF **26/27 bài (96.30%)**.
    - Điểm thật Grammar $\le 2.0$ ($n=113$): Ridge dự đoán vào giữa **82/113 bài (72.57%)**; RF **81/113 bài (71.68%)**.

---

### Bảng 10: Thay thế nguồn thông tin (B1 TF-IDF, B2 MiniLM L6 v2)
- **Mục tiêu:** Kiểm định xem tín hiệu bất đồng $D$ có phải là hệ quả riêng của 14 đặc trưng đóng băng hay không, bằng cách thay thế bằng:
  - **B1:** Văn bản n-gram thuần túy (TF-IDF unigram + bigram, $\min\_df=5$, Ridge $\alpha=10$).
  - **B2:** Mô hình biểu diễn câu nơ-ron trước huấn luyện (`all-MiniLM-L6-v2` 384-dim, encoder đóng băng, Ridge $\alpha=10$).
- **Phân loại:**
  - Đọc và tính lại bảng đối chiếu: **[Loại 1] Tức thì (< 1s)**
  - Huấn luyện lại B1 TF-IDF: **[Loại 2] ~45s**
  - Huấn luyện lại B2 MiniLM: **[Loại 3] ~3-5 phút (yêu cầu `.venv_gec`)**
- **Lệnh thực thi:**
  ```powershell
  # [Loại 1] Đọc ma trận OOF đã lưu (tái lập tức thì):
  .venv\Scripts\python.exe -c "
  import pandas as pd, numpy as np
  df = pd.read_csv('reports/week10/b2_oof.csv')
  for m, v, g in [('RF_14feat', 'RF_V', 'RF_G'), ('Ridge_14feat', 'Ridge_V', 'Ridge_G'), ('B1_TFIDF', 'B1_V', 'B1_G'), ('B2_MiniLM', 'B2_V', 'B2_G')]:
      print(f'{m}: MAE_V={np.mean(np.abs(df[\"Vocabulary\"]-df[v])):.6f}, MAE_G={np.mean(np.abs(df[\"Grammar\"]-df[g])):.6f}, LargeErr={(np.maximum(np.abs(df[\"Vocabulary\"]-df[v]), np.abs(df[\"Grammar\"]-df[g]))>=1.0).sum()}')
  "

  # [Loại 2] Chạy lại toàn bộ pipeline B1 TF-IDF OOF:
  .venv\Scripts\python.exe scripts/week10/information_sources_oof.py

  # [Loại 3] Chạy lại toàn bộ pipeline B2 MiniLM embedding + Ridge OOF:
  .venv_gec\Scripts\python.exe scripts/week10/gec_b2.py
  ```
- **File đầu vào:** `reports/week10/b2_oof.csv`, `reports/week10/b2_results.json`.
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
- **File đầu vào:**
  - `reports/week9/t3_heldout_predictions.csv`
  - `reports/week10/b2_oof.csv`
- **File đầu ra:**
  - `docs/final_evidence/c_cluster_bootstrap.csv`
  - `docs/nguon_bao_cao_interview/e5_bat_theo_fold.csv`
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
- **Phân loại:**
  - Chạy thật LanguageTool và đối chiếu: **[Loại 1 & 3] ~65s (chạy tự động trong `.venv`)**
  - Chạy lại mô hình nơ-ron GECToR từ đầu: **[Loại 3] ~5-10 phút (yêu cầu `.venv_gec` và weights RoBERTa)**
- **Lệnh thực thi:**
  ```powershell
  # Chạy LanguageTool thật và đối chiếu toàn bộ chỉ số thỏa mãn:
  .venv\Scripts\python.exe scripts/calculate_d_tool_agreement.py

  # [Tham khảo] Script chạy GECToR lịch sử trên 68 bài (yêu cầu .venv_gec):
  # .venv_gec\Scripts\python.exe scripts/week10/gec_part_a.py
  ```
- **File đầu vào:**
  - `data/03_clean_ready_to_use/validation_783.csv`
  - `reports/week10/gec_part_a_68.csv`
  - `docs/final_evidence/a_doi_chieu_so_lieu.csv` (10 ca sanity check)
- **File đầu ra:**
  - `docs/final_evidence/d_tool_window_counts.csv`
  - `docs/final_evidence/d_tool_agreement.csv`
- **Thời gian chạy thực tế:** ~65 giây (LanguageTool Java server chạy phân tích 10 + 68 bài).
- **Số liệu đối chiếu trên cùng cửa sổ 150 từ đầu:**
  | Nhóm bài | Công cụ | Số đếm TB | Độ lệch so với người (Bias) | Spearman $r$ với người | 95% Bootstrap CI của $r$ |
  |---|---|---:|---:|---:|---:|
  | **Mẫu ngẫu nhiên (36 bài)** | Người đọc độc lập | 7.3333 | — | — | — |
  | | LanguageTool 6.6 | 1.2222 | -6.1111 (thiếu nặng) | 0.7081 | [0.4797, 0.8481] |
  | | GECToR + ERRANT | 14.3333 | +7.0000 (thừa) | 0.7604 | [0.5069, 0.9032] |
  | | *Hiệu số (GECToR - LT)* | — | — | **+0.0522** | **[-0.0851, +0.1915]** (chứa 0) |
  | **Mẫu ca lỗi tuần 9 (32 bài)** | Người đọc độc lập | 9.4375 | — | — | — |
  | | LanguageTool 6.6 | 1.4062 | -8.0312 (thiếu nặng) | 0.5234 | [0.2005, 0.7640] |
  | | GECToR + ERRANT | 14.3125 | +4.8750 (thừa) | 0.8772 | [0.7149, 0.9459] |
  | | *Hiệu số (GECToR - LT)* | — | — | **+0.3538** | **[+0.0873, +0.6621]** |
  | **Gộp (68 bài)** | Người đọc độc lập | 8.3235 | — | — | — |
  | | LanguageTool 6.6 | 1.3088 | -7.0147 | 0.6229 | [0.4383, 0.7702] |
  | | GECToR + ERRANT | 14.3235 | +6.0000 | 0.7985 | [0.6468, 0.8913] |
  | | *Hiệu số (GECToR - LT)* | — | — | **+0.1756** | **[+0.0183, +0.3527]** |

---

## 4. Tái lập các Bằng chứng Bổ sung (Mục B và A)

### Mục B: Tỷ lệ bài viết bị cắt bởi tokenizer MiniLM L6 v2
- **Lệnh thực thi:**
  ```powershell
  .venv_gec\Scripts\python.exe scripts/calculate_b_minilm_truncation.py
  ```
- **Thời gian chạy thực tế:** ~10 giây trong `.venv_gec`.
- **Kết quả đối chiếu:**
  - Toàn bộ 3.812 bài Development: **3.378 / 3.812 bài bị cắt (88.6149%)**.
  - Phân bố token: Min = 16, Median = **459.0**, P90 = **761.0**, Max = 1.435.
  - Nhóm sai lớn A1 (RF sai lớn 386 bài): 334 / 386 bài bị cắt (**86.5285%**).
  - Nhóm sai lớn chung A3 (RF + B2 cùng sai lớn 217 bài): 186 / 217 bài bị cắt (**85.7143%**).
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

## 5. Bảng tổng hợp mức độ khả thi thực thi (Execution Matrix)

| Bảng / Mục | Phân loại | Môi trường | Lệnh thực thi chính | Đầu vào chính | Đầu ra chính | Thời gian | Trạng thái xác nhận |
|---|---|---|---|---|---|---:|---|
| **Bảng 7 (Val)** | Loại 1 | `.venv` | `phase7_evaluate_regression_models.py` | `validation_predictions.csv` | `regression_metrics.csv` | ~12s | ĐÃ CHẠY THỬ (PASS) |
| **Bảng 7 (Dev)** | Loại 1 | `.venv` | `build_interview_sources.py` | `t3_heldout_predictions.csv` | `d1_mean_dev.csv` | ~0.9s | ĐÃ CHẠY THỬ (PASS) |
| **Bảng 8** | Loại 1 | `.venv` | `phase8_evaluate_review_prioritization.py` | `validation_predictions.csv` | `review_strategy_comparison.csv` | ~3.5s | ĐÃ CHẠY THỬ (PASS) |
| **Bảng 9** | Loại 1 | `.venv` | Tra cứu `RESULTS_week10.md` Part B | `t3_eligible_development.csv` | `RESULTS_week10.md` | < 1s | ĐÃ CHẠY THỬ (PASS) |
| **Bảng 10 (OOF)** | Loại 1 | `.venv` | One-liner Python đọc `b2_oof.csv` | `b2_oof.csv` | In stdout bảng số liệu | < 1s | ĐÃ CHẠY THỬ (PASS) |
| **Bảng 10 (B1 Train)**| Loại 2 | `.venv` | `information_sources_oof.py` | `t3_eligible_development.csv` | `b1_oof.csv` | ~45s | Chưa chạy thử (đã có kết quả lưu) |
| **Bảng 10 (B2 Train)**| Loại 3 | `.venv_gec` | `gec_b2.py` | `b2_assets/model` | `b2_oof.csv`, `b2_results.json` | ~3m | Chưa chạy thử (đã có kết quả lưu) |
| **Bảng 18 (Fold)**| Loại 1 | `.venv` | `calculate_c_cluster_bootstrap.py` | `t3_heldout_predictions.csv` | `c_cluster_bootstrap.csv` | ~1.5s | ĐÃ CHẠY THỬ (PASS) |
| **Bảng 20 (Agree)**| Loại 1/3 | `.venv` | `calculate_d_tool_agreement.py` | `gec_part_a_68.csv`, raw text | `d_tool_agreement.csv` | ~65s | ĐÃ CHẠY THỬ (PASS) |
| **Mục B (Cut)** | Loại 3 | `.venv_gec` | `calculate_b_minilm_truncation.py` | `b2_assets/model`, raw text | `b_minilm_truncation.csv` | ~10s | ĐÃ CHẠY THỬ (PASS) |
| **Mục A (Pack)** | Loại 1 | `.venv` | `build_a_reading_pack.py` | `t3_heldout_predictions.csv` | `phieu_doc_10_ca.xlsx` | ~2s | ĐÃ CHẠY THỬ (PASS) |
