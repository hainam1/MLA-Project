# Nguồn báo cáo interview — A đến K

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| Phạm vi | Chỉ hồ sơ nguồn; không viết báo cáo. Không mở dữ liệu/nhãn/dự đoán Official Test, corpus hoặc bài luận; số Test chỉ trích log/kết quả tổng hợp. Không huấn luyện lại. | ĐÃ CÓ | `scripts/build_interview_sources.py`, commit NEW |
| Quy ước | V = Từ vựng; G = Ngữ pháp. NEW = commit chứa hồ sơ này, hash được gửi cùng bàn giao. Mọi kết quả TÍNH MỚI (dev) đều **chỉ development, thăm dò**. CSV nằm trong `docs/nguon_bao_cao_interview/`. | ĐÃ CÓ | HEAD trước nhiệm vụ `755929233dab6aee1983dfa028f2be1ed3e7f87c`; lệnh mới: `.venv/Scripts/python.exe scripts/build_interview_sources.py` (CMD) |
| S01 | `docs/evaluation_protocol_freeze.md` | ĐÃ CÓ | commit `2c7982e` |
| S02 | `docs/phase1_problem_definition.md`, nguyên văn câu hỏi ở mục 1.1 | ĐÃ CÓ | commit `2c7982e`; các dòng trích thuộc bản đã commit |
| S03 | `docs/data_card.md`; `docs/data_inventory.md` | ĐÃ CÓ | commit `2c7982e` |
| S04 | `docs/split_and_leakage_protocol.md`; `docs/data/phase3_tables/split_audit_summary.json` | ĐÃ CÓ | commit `2c7982e` |
| S05 | `docs/feature_specification.md` | ĐÃ CÓ | commit `2c7982e` |
| S06 | `docs/phase6_training_readiness.md`; `src/mla_project/models/train_ridge.py`; `src/mla_project/models/train_random_forest.py`; `src/mla_project/pipelines/training_pipeline.py` | ĐÃ CÓ | commit `2c7982e`; dùng phần cấu hình/code đã commit |
| S07 | `reports/week9/t3_eligible_development.csv`; `reports/week9/t3_heldout_predictions.csv`; `reports/week9/t3_pooled.csv` | ĐÃ CÓ | commit `81aec90` |
| S08 | `reports/week9/RESULTS_week9.md` | ĐÃ CÓ | commit `3e6f0d8`; Task 0, Week 9b và paired tree-spread |
| S09 | `reports/week10/RESULTS_week10.md` | ĐÃ CÓ | commit `e88d82c`; Part B, reading audit, OOF sources, GECToR và B2 |
| S10 | `scripts/week10/information_sources_oof.py` | ĐÃ CÓ | commit `b6398ea` |
| S11 | `docs/signal_lock_tree_spread.md` | ĐÃ CÓ | commit `4e381150edf08d49a134505e669058f1e0d27b48` |
| S12 | `reports/week9/RESULTS_tree_spread_second_use.md`; `reports/week9/tree_spread_official_test_second_use_log_attempt2.json` | ĐÃ CÓ | commit `97159a6b9a10e46b881b8e1a66cd278171dff4f6` |
| S13 | `docs/data/phase7_tables/regression_metrics.csv` | ĐÃ CÓ | commit `2c7982e` |
| S14 | `docs/llm_disclosure.md` | ĐÃ CÓ | commit `81aec90` |
| S15 | `logs/progress.md` | ĐÃ CÓ | commit `2c7982e` |

## A

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| A1 | Với cùng một ngân sách xem lại cố định, việc xếp hạng bài viết theo mức bất đồng giữa Ridge Regression và Random Forest có thu giữ được nhiều bài có sai số dự đoán lớn hơn chọn ngẫu nhiên cùng số lượng hay không? | ĐÃ CÓ | S02, mục 1.1; giữ nguyên câu chữ |
| A2 | `L_i = 1[max(abs(RF_V−y_V), abs(RF_G−y_G)) ≥ 1,0]`. Lấy max giữa hai đích; RF là mô hình tham chiếu hiện hành. Bản consensus ở Phase 1 là lịch sử, không dùng thay định nghĩa khóa. | ĐÃ CÓ | S01, Frozen evaluation definitions |
| A2 — lý do 1,0 | Có ghi ngưỡng chốt trước Test; không tìm thấy căn cứ định lượng/sư phạm giải thích vì sao chọn đúng 1,0. | KHÔNG CÓ NGUỒN | S02 mục 1.6 chỉ ghi chốt trước Test; S01 khóa ngưỡng |
| A3 | `k = ceil(0,20N)`; ngân sách chính 20%, 10%/30% là độ nhạy, không chọn ngân sách tốt nhất sau xem kết quả. | ĐÃ CÓ | S01; S02 mục 1.1 |
| A3 — lý do 20% | Có bối cảnh thời gian giáo viên hạn chế; chưa có khảo sát hay căn cứ chọn riêng mức 20%. | KHÔNG CÓ NGUỒN | S02 mục 1.2 và 1.1 |
| A4 | `D = max(abs(RF_V−Ridge_V), abs(RF_G−Ridge_G))`; giảm dần, hòa thì essay_id dạng chuỗi tăng dần. N là số bài, K số sai lớn, k ngân sách, C số bắt được. Một holdout: kỳ vọng `kK/N`, p một phía `hypergeom.sf(C−1,N,K,k)`. OOF: kỳ vọng `sum(k_f K_f/N_f)`, p là đuôi tích chập các Hypergeom theo fold, không dùng công thức gộp toàn cục thay thế. | ĐÃ CÓ | S01; S11, Future confirmation protocol; giả định ngẫu nhiên độc lập giữa fold là reference-null, các tập train OOF vẫn chồng nhau |

## B

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| B1 | ELLIPSE v1.0 (2023), Crossley và cộng sự; URL `https://github.com/scrosseye/ELLIPSE-Corpus`; CC BY-NC-SA 4.0. Raw 8.890 bài; final reliable 6.482 = 3.911 official train + 2.571 official test. | ĐÃ CÓ | S03, Identity/Data quality; chỉ trích link trong repo, không mở web |
| B2 | Repo ghi raw và final reliable là hai bản phát hành; không có bảng đầy đủ từng bước loại bài từ 8.890 xuống 6.482 kèm số loại theo từng lý do. Không gọi privacy gate của dự án là bước tạo reliable upstream. | KHÔNG CÓ NGUỒN | S03, Data quality; có số đầu/cuối, thiếu chuỗi lọc upstream |
| B3 | Eligible = `privacy_review_status=not_flagged`. Development: 3.911−99=3.812 (85 flagged, 14 unresolved). Test: 2.571−53 flagged=2.518. Train/Test là phân hoạch official upstream, dự án giữ nguyên, không tự chia thành 3.812/2.518. | ĐÃ CÓ | S04, Privacy status; S07; `reports/week9/t3_eligibility_counts.csv`, `t3_eligibility_reasons.csv`, commit `81aec90` |
| B3 — ngày khóa dự án | Dự án khóa split ngày 23/09/2026, script `scripts/phase3_build_split.py`. | ĐÃ CÓ | S04, Frozen on/Reproducible split procedure |
| B3 — ai/lúc nào upstream | Chưa có nguồn về người và ngày upstream thực hiện phân hoạch official; không suy từ tác giả git thành người trực tiếp chia dữ liệu. | KHÔNG CÓ NGUỒN | S04 không xác định danh tính/thời điểm chia upstream |
| B4 | Ban đầu official train chia 3.128/783 theo nhóm hash văn bản trùng chính xác và stratify prompt, seed 42; qua privacy gate còn 3.050/762. CV tuning: PredefinedSplit 5 fold trong 3.050; phân tích tuần 9: GroupKFold 5 fold theo normalised_prompt trên 3.812, hai protocol khác nhau. Số prompt vận hành: development 44, Validation 44, Test 44 (Test chỉ từ audit đã lưu). | ĐÃ CÓ | S04; S06; S08, Task 3/Week 9b |
| B5 | V/G: 1,0–5,0, bước 0,5 trong final; điểm tổng hợp/trung bình của hai người chấm được đào tạo, không khẳng định adjudication. | ĐÃ CÓ | S03, Human-rating process/Valid score range |
| B6 | `b6_phan_bo_nhan_dev.csv`: phân bố đầy đủ từng mức V/G, chỉ 3.812 development. | TÍNH MỚI (dev) | CMD → CSV cùng tên; S07; commit NEW |
| B7 | OOF development: RF sai lớn 386/3.812; RF và Ridge cùng sai lớn 276/386. Validation: RF sai lớn 69/762, cả hai cùng sai 51/69. Test: 208/2.518. Đây là các tỉ lệ nền đúng với từng protocol; không cộng Validation thêm vào development. | ĐÃ CÓ | S07 `t3_pooled.csv`; S08 Task 0 và Week 9b STEP1A; Test chỉ bảng Task 0 |
| B8 | Đếm lỗi tự động bỏ sót/khác quy tắc người đọc; điểm người chấm có biến thiên; prompt lặp qua train/Validation ban đầu; không có ID người viết ổn định để bảo đảm tách theo người. Chưa xác nhận một nhãn cụ thể sai chỉ từ bất đồng với người đọc. | ĐÃ CÓ | S03/S04, limitations; S09, reading audit/provenance |

## C

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| C1 — quy ước | W: token chữ cái spaCy; S: câu; N: danh từ; C: đầu mệnh đề; U: đầu mệnh đề phụ; G: cảnh báo LanguageTool loại grammar. Các nhóm dưới là mục đích mô tả đặc trưng, cả 14 cùng vào cả hai mô hình V/G. | ĐÃ CÓ | S05, Shared preprocessing/Feature table |
| C1.1 `word_count` (số từ) | `len(W)`; spaCy `en_core_web_sm`; nhóm độ dài, dùng chung V/G. | ĐÃ CÓ | S05, hàng 1 |
| C1.2 `sentence_count` (số câu) | `len(S)`; spaCy; nhóm độ dài, dùng chung V/G. | ĐÃ CÓ | S05, hàng 2 |
| C1.3 `mean_sentence_length` (độ dài câu trung bình) | `len(W)/len(S)`; spaCy; độ dài/cấu trúc, dùng chung V/G. | ĐÃ CÓ | S05, hàng 3 |
| C1.4 `mtld` (đa dạng từ vựng MTLD) | Hai chiều, ngưỡng TTR 0,72; lexicalrichness; dưới 10 từ hoặc không xác định trả 0; nhóm V. | ĐÃ CÓ | S05, hàng 4 |
| C1.5 `mattr` (đa dạng từ theo cửa sổ) | TTR trung bình cửa sổ `min(50,len(W))`; lexicalrichness; dưới 2 từ trả 0; nhóm V. | ĐÃ CÓ | S05, hàng 5 |
| C1.6 `mean_word_frequency` (tần suất từ trung bình) | Trung bình Zipf tiếng Anh của từ bề mặt viết thường; wordfreq; từ không biết góp 0; nhóm V. | ĐÃ CÓ | S05, hàng 6 |
| C1.7 `mean_word_length` (độ dài từ trung bình) | Trung bình số ký tự Unicode của từ viết thường; spaCy/Python; nhóm V. | ĐÃ CÓ | S05, hàng 7 |
| C1.8 `lexical_density` (mật độ từ nội dung) | Số NOUN/PROPN/VERB/ADJ/ADV chia len(W); spaCy; nhóm V. | ĐÃ CÓ | S05, hàng 8 |
| C1.9 `noun_diversity` (đa dạng danh từ) | Số lemma danh từ/proper noun duy nhất sau casefold chia len(N); spaCy; không danh từ trả 0; nhóm V. | ĐÃ CÓ | S05, hàng 9 |
| C1.10 `detected_grammar_errors_per_100_words` (cảnh báo ngữ pháp/100 từ) | `100*len(G)/max(len(W),1)`; LanguageTool 6.6, en-US, chỉ ruleIssueType=grammar; nhóm G. | ĐÃ CÓ | S05, hàng 10 |
| C1.11 `detected_error_free_sentence_ratio` (tỷ lệ câu không có cảnh báo) | Số câu không giao cảnh báo G theo offset ký tự chia len(S); spaCy + LanguageTool; nhóm G. | ĐÃ CÓ | S05, hàng 11 |
| C1.12 `complex_sentence_ratio` (tỷ lệ câu phức) | Số câu có ít nhất một đầu mệnh đề phụ ước lượng chia len(S); spaCy dependency; nhóm cú pháp/G. | ĐÃ CÓ | S05, hàng 12 |
| C1.13 `estimated_clauses_per_sentence` (mệnh đề ước lượng/câu) | `len(C)/len(S)`; đầu VERB/AUX với ROOT/conj hoặc dependency phụ đã khóa; spaCy; nhóm cú pháp/G. | ĐÃ CÓ | S05, hàng 13 và Operational syntax rules |
| C1.14 `subordinate_clause_ratio` (tỷ lệ mệnh đề phụ) | `len(U)/len(C)`; U thuộc advcl/ccomp/xcomp/acl/relcl/csubj/csubjpass; không C trả 0; spaCy; nhóm cú pháp/G. | ĐÃ CÓ | S05, hàng 14 |
| C2 | Cả 14 cột đều 0 giá trị thiếu, tỷ lệ 0 trên 3.812 bài; `c2_thieu_dac_trung.csv`. Các giá trị 0 theo chính sách văn bản ngắn/không phát hiện không phải NA. | TÍNH MỚI (dev) | CMD → CSV; S07; chính sách 0: S05; commit NEW |
| C3 | Ridge: `('imputer',SimpleImputer(strategy='median'))`, `('scaler',StandardScaler())`, `('model',Ridge(alpha=alpha))`; RF: median imputer rồi RF, không StandardScaler. Fit bên trong pipeline trên train của từng fold, rồi refit model-train; không fit preprocessing trên Validation. OOF theo đề cũng fit riêng train fold. | ĐÃ CÓ | S06: `train_ridge.py:13–15`, `train_random_forest.py:25–26`, `training_pipeline.py:202–212` (GridSearchCV, PredefinedSplit, search.fit); OOF: S10 `information_sources_oof.py:207–218` |
| C4 | Công cụ cũ: LanguageTool 6.6, chỉ grammar; số đoạn đầu dùng `rate*min(150,word_count)/100`, là ước lượng từ tỷ lệ toàn bài. GECToR + ERRANT dùng để kiểm tra đặc trưng lỗi trên 68 bài đã có người đếm (32 chọn có chủ đích + 36 ngẫu nhiên phân tầng), không thay feature trong RF/Ridge. Trung bình: người 8,323529; cũ 1,323504; GECToR grammar edits 14,323529. | ĐÃ CÓ | S05; S09, Exploratory Part A (2026-10-24); `reports/week10/gec_part_a_68.csv`, `gec_part_a_statistics.json` (artifact gitignored; số đã in trong S09, commit `2cab63e`, được giữ tại `e88d82c`) |
| C5 | `c5_tam_quan_trong_dac_trung.csv`: hệ số Ridge trên X đã chuẩn hóa (y vẫn đơn vị điểm); RF impurity/MDI importance. Trích 4 pipeline Phase 6 đã fit 3.050 model-train, không huấn luyện hay tính permutation. Không gọi MDI là tác động nhân quả hoặc importance Validation. | TÍNH MỚI (dev) | CMD → CSV; `outputs/phase6/{ridge,random_forest}_{vocabulary,grammar}.joblib`; hash trong `i3_ma_bam_nguon_dev.csv`; commit NEW |

## D

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| D1 | Mean OOF: V=0,474015445938; G=0,564000740273. Trong mỗi GroupKFold theo đề, đoán trung bình nhãn các fold train; gộp MAE trên toàn development, không lấy trung bình MAE fold. | TÍNH MỚI (dev) | CMD → `d1_mean_dev.csv`; S07; commit NEW |
| D2 | Alpha thử: 0,1; 1; 10; 100; 1000. PredefinedSplit 5 fold cố định trong model-train, GridSearchCV chọn theo neg_mean_absolute_error; chọn V=100, G=0,1. Loss Ridge: tổng bình phương residual + alpha nhân bình phương chuẩn L2 hệ số, không phải MAE; MAE là metric chọn. | ĐÃ CÓ | S06, Model selection và build_ridge; thư viện sklearn Ridge được dùng trong code |
| D3 | RF grid: n_estimators=300; max_depth=10/None; min_samples_leaf=2/5; max_features=sqrt/1,0. CV/metric như D2. Chốt depth=10, max_features=sqrt, leaf V=2/G=5, seed 42, n_jobs=1. criterion mặc định squared_error (giảm phương sai/MSE khi chia), dự đoán trung bình cây. | ĐÃ CÓ | S06, Model selection; factory RF gọi RandomForestRegressor, không override criterion |
| D4 | TF-IDF word unigram/bigram, min_df=5, max_df=1, sublinear_tf=True, lowercase=True, norm=l2, smooth_idf=True, không stopwords/max_features. Ridge phía trên alpha=10, solver=lsqr, tol=1e-6, max_iter=10000. MAE OOF V=0,406626218232; G=0,506841213957. | ĐÃ CÓ | S10:39–44; S09, B1/OOF comparison |
| D5 | `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; encoder đóng băng, không fine-tune; embedding 384 chiều, max_seq_length=256, mean pooling + Normalize gốc; Ridge alpha=10/lsqr như D4. MAE V=0,404448035882; G=0,507499800211. | ĐÃ CÓ | S09, Exploratory B2; `scripts/week10/gec_b2.py`, commit `e88d82c` |
| D6 — Mean | MAE V/G = 0,474015445938 / 0,564000740273; 3.812 OOF theo đề. | TÍNH MỚI (dev) | D1; CSV; CMD; commit NEW |
| D6 — Ridge | MAE V/G = 0,373424437145 / 0,463036537712; 3.812 OOF theo đề. Validation riêng: 0,374813522850 / 0,456297593656. | ĐÃ CÓ | S09, B2 OOF_MAE; S13 cho Validation |
| D6 — RF | MAE V/G = 0,372165069040 / 0,455403719596; 3.812 OOF theo đề. Validation riêng: 0,372977108380 / 0,447710320540. | ĐÃ CÓ | S09, B2 OOF_MAE; S13 cho Validation |
| D6 — TF-IDF/MiniLM | MAE theo D4/D5 là OOF development; không trộn với Validation Phase 7. | ĐÃ CÓ | S09 |
| D6 — Validation baseline text | Không có MAE Validation tương ứng của TF-IDF/MiniLM trong hồ sơ đã tìm. | KHÔNG CÓ NGUỒN | S09 chỉ báo cáo OOF theo đề |
| D7 | Ridge là họ tuyến tính có regularization, RF là họ phi tuyến để so sánh; cùng bộ đặc trưng dễ giải thích. Không có nguồn chứng minh đây là hai mô hình tối ưu trong mọi lựa chọn. | ĐÃ CÓ | `docs/methodology.md`, đoạn “Ridge Regression supplies a regularized linear model … Random Forest … nonlinear comparison”, commit `2c7982e` |

## E

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| E1 | D bắt 88/386, kỳ vọng 77,362908429581; p chính xác theo tích chập fold=0,0883568421584. Empirical 1.000 lượt tuần 9=0,105, là phép tính khác, không thay cho exact p. | ĐÃ CÓ | S08:1437; S07 `t3_pooled.csv` |
| E2 | Cả hai cùng sai 276/386; D bắt 44/276; kỳ vọng 55,3218568770231; p exact theo fold=0,970123345661. | ĐÃ CÓ | S08, A3_CAPTURE pooled D |
| E3 | Validation D bắt 15/69, k=153/762; kỳ vọng 13,8543307086614; p exact=0,409805547271. | ĐÃ CÓ | S08, Task 0 |
| E4 | Test lần 1: 47/208, N=2.518, k=504, kỳ vọng 41,6330420969023, p exact=0,188324671369. Ngày thực thi đầu tiên chưa xác định được; không dùng mtime làm ngày chạy. | ĐÃ CÓ | S08 Task 0; `reports/week9/t0_provenance.md`, commit `24399b7`; ngày đầu: KHÔNG CÓ NGUỒN |
| E5 | `e5_bat_theo_fold.csv`: N, K, k, D bắt, kỳ vọng cho từng fold; tổng bắt=88, tổng K=386. | TÍNH MỚI (dev) | CMD → CSV, tính kiểm tra từ S07; commit NEW |
| E6 — Ridge | Trong 386 RF sai lớn, Ridge cũng sai 276; D RF–Ridge bắt 88/386. Trên nhóm 276 cùng sai, D bắt 44, kỳ vọng 55,321857. | ĐÃ CÓ | S07; S08, A3_CAPTURE |
| E6 — TF-IDF | RF/TF-IDF cùng sai 233/386; D RF–TF-IDF bắt 81/386, kỳ vọng 77,362908; trên nhóm 233 cùng sai bắt 35/233=15,021459 trên 100, kỳ vọng 46,698038/233 (khoảng 20 trên 100). Trong 276 ca RF/Ridge cùng sai, TF-IDF còn sai 203, được cứu 73; tỷ lệ cứu 73/276=0,264493. | ĐÃ CÓ | S09, OOF comparison, A3_new_RF_and_B và shared; commit `b6398ea` giữ trong `e88d82c` |
| E6 — MiniLM | RF/MiniLM cùng sai 217/386; D RF–MiniLM bắt 93/386, kỳ vọng 77,362908; trên nhóm 217 cùng sai bắt 36/217=16,589862 trên 100, kỳ vọng 43,495178/217 (khoảng 20 trên 100). Trong 276 ca cũ, MiniLM còn sai 191, được cứu 85; tỷ lệ cứu 85/276=0,307971. | ĐÃ CÓ | S09, B2 captures/shared; commit `e88d82c` |
| E7 — dev V/G | RF: (SD_pred/SD_true; Pearson r; OLS **truth theo prediction**, có intercept): V=(0,533074; 0,587418; 1,101945); G=(0,560419; 0,586226; 1,046048). | ĐÃ CÓ | S09 Part B, Development_OOF SMALL_SUMMARY_TABLE |
| E7 — Validation V/G | RF: V=(0,539935; 0,547795; 1,014558); G=(0,569546; 0,581778; 1,021478). Độ dốc truth~pred bằng r/(SD_pred/SD_true), nên gần 1 vẫn tương thích dự đoán bị nén. | ĐÃ CÓ | S09 Part B, Validation SMALL_SUMMARY_TABLE/ARITHMETIC |
| E7 — dải điểm dev | V thật <2,5: n=137, thật TB 1,937956, RF 2,858085; >4,0: n=155, thật 4,632258, RF 3,681137. G thật <2,5: n=555, thật 1,969369, RF 2,691154; >4,0: n=163, thật 4,588957, RF 3,568046. | ĐÃ CÓ | S09 Part B, Development_OOF TRUTH_BAND_MEANS |

## F

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| F1 | `tree_spread=max(std(tree_predictions_V,ddof=0),std(tree_predictions_G,ddof=0))`, mỗi đích 300 cây; giảm dần, hòa ID chuỗi tăng dần, ngân sách ceil(0,20N) mỗi fold. | ĐÃ CÓ | S11, Signal definition |
| F2 | Validation 25/69, kỳ vọng 13,8543307086614, p=0,000776590325432. Dev OOF 96/386, kỳ vọng 77,362908429581, p theo fold=0,00853607092650. p global=0,00851908434572 dùng null khác, không lẫn với p theo fold. | ĐÃ CÓ | S08:1370,1436 |
| F3 | Chênh tree−D=+8 bài; CI percentile 95% [−11;27]; bootstrap ghép cặp 44 cụm đề, 2.000 lượt, default_rng(42); giữ hàng đợi cố định, không xếp hạng/fit/tính lại ngân sách. CI chứa 0. | ĐÃ CÓ | S08, paired prompt-cluster bootstrap; `scripts/week9b/paired_tree_spread.py`, commit `3e6f0d8` |
| F4 | Khóa tại S11, SHA256 `d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca`; thời điểm ghi trong khóa: 19/10/2026 05:41:03 UTC. Nội dung khóa còn câu Test not used là trạng thái lịch sử tại thời điểm khóa. | ĐÃ CÓ | S11; commit khóa `4e381150edf08d49a134505e669058f1e0d27b48` |
| F5 | Test lần hai hoàn thành 26/10/2026 07:27:32 UTC: 55/208, kỳ vọng 41,6330420969023, p=0,011585706847145556; status=COMPLETED, pre_signal_checks=PASS. Chạy tại `cdc0a6a`, lưu kết quả `97159a6`; chỉ tín hiệu khóa, dùng RF đã lưu, kết quả thăm dò do Test dùng lại. | ĐÃ CÓ | S12; ngày cho phép 26/10/2026 từ nhận xét tuần 10 theo xác nhận người phụ trách trong RESULTS |
| F5 — sự cố | Lần gọi đầu bị dừng trước tín hiệu: 2.015 dòng V vượt atol=1e-12, lệch max 4,995115432393504e-12; log STOPPED giữ nguyên (`9405677`). Sửa dung sai dựa kiểm tra development thành atol=1e-11, rtol=0 (`529e5b9`); sửa chốt chặn log (`cdc0a6a`); attempt2 mới hoàn thành. Không mô tả là chỉ có một lần gọi kỹ thuật. | ĐÃ CÓ | S12, Sự cố; `reports/week9/tree_spread_official_test_second_use_log.json`, commit `9405677` |
| F6 | Tree bắt 65/276 ca RF/Ridge cùng sai; kỳ vọng 55,3218568770231, p theo fold=0,0777028979575. | ĐÃ CÓ | S08, A3_CAPTURE pooled tree_std |

## G

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| G1 | `g1_ca_loi.csv`: 10 ca development RF sai lớn, gồm 0514D25768A0 và 684166ED2438, thêm 8 ca theo RF max-error giảm dần/ID tăng dần. Có nhãn/dự đoán V/G, fold, D, hạng, k, được chọn hay không, cả hai sai và nhóm số học. Nhóm số học không phải nhận xét người đọc. | TÍNH MỚI (dev) | CMD → CSV; S07; commit NEW |
| G1 — tree từng bài | Chưa có OOF tree_spread lưu theo bài; producer giữ DataFrame trong bộ nhớ, chỉ xuất bảng tổng hợp. Không thay bằng spread mô hình Phase 6 có thể đã học bài đó. Không fit lại để lấp thiếu. | KHÔNG CÓ NGUỒN | `scripts/week9b/tree_spread_oof.py`, commit `879d24f`/`ecf0cdf`; S08 có số tổng hợp |
| G2 | 684166ED2438: D=0,06233669853577917, hạng 671/769, k=154, không chọn. MiniLM V=3,054166078567505; G=3,095129728317261. | ĐÃ CÓ | `docs/du_lieu_interview.md`, commit `7559292`; nguồn gốc S07 và `reports/week10/b2_oof.csv` (hash CSV trong I3; số trích đã commit) |
| G3 | Mẫu ngẫu nhiên phân tầng 36 Validation: mỗi dải điểm 12 bài, seed chọn 2026, loại mẫu 32 bài cũ; trung bình người đọc 7,333333 và công cụ 1,236789 lỗi. Người đọc đếm 150 từ đầu; công cụ là ước lượng tỷ lệ toàn bài đổi về tối đa 150 từ. | ĐÃ CÓ | S09, Part C/filled random reading audit; `scripts/week10/random_reading.py`, commit `5be9156`; `reading_compare.py`, commit `0e89a8a` |
| G3 — ai/quy tắc chi tiết | Chưa xác minh danh tính người trực tiếp đếm và trình tự đọc mù; không có đủ bằng chứng cell-level. Có phạm vi 150 từ đầu và trường số lỗi; chưa có danh mục đủ chi tiết về tách/gộp từng loại lỗi để coi là gold-standard thống nhất. | KHÔNG CÓ NGUỒN | S09, Provenance of blind reading (commit `dceecfe` giữ tại `e88d82c`) |

## H

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| H1 | `h1_doi_ngan_sach.csv`: 10% D bắt 50, kỳ vọng 38,781738; 20% D bắt 88, kỳ vọng 77,362908; 30% D bắt 122, kỳ vọng 116,046092. Giữ fold/score cố định. | TÍNH MỚI (dev) | CMD → CSV; S07; commit NEW |
| H1 — tree | Chỉ có mốc 20% bắt 96 đã lưu; thiếu 10% và 30% do chưa có spread OOF theo bài. Dừng trường này, không huấn luyện lại. | KHÔNG CÓ NGUỒN | S08:1436 cho mốc đã có; lý do thiếu như G1 |
| H2 | `h2_doi_nguong.csv`: ngưỡng 0,75: K=965, D bắt 200, kỳ vọng 193,405068; 1,0: K=386, bắt 88, kỳ vọng 77,362908; 1,25: K=127, bắt 35, kỳ vọng 25,458886. Ngân sách giữ 20% từng fold. | TÍNH MỚI (dev) | CMD → CSV; S07; commit NEW |

## I

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| I1 — tái lập hồ sơ | Chạy CMD; chỉ đọc bảng development số, kiểm tra fold, tính số học và trích hệ số/MDI mô hình đã lưu. Không fit/predict. Mọi CSV tính mới do cùng script tạo; lần kiểm tra lại hoàn thành phần xử lý trong 0,944640 giây (không tính import thư viện); không dùng thời gian này để ước lượng huấn luyện. | TÍNH MỚI (dev) | `scripts/build_interview_sources.py`, stdout lần kiểm tra; commit NEW |
| I1 — pipeline lịch sử | Thứ tự dev: `scripts/week9/t3_eligibility.py` → `t3_preflight.py` → `t3_evaluate.py`; tree: `scripts/week9b/tree_spread_oof.py` → `paired_tree_spread.py`; nguồn text: `scripts/week10/information_sources_oof.py`, B2: `gec_b2.py`. Đây là tên entrypoint lịch sử, **không chạy trong nhiệm vụ này**; các bước text cần dữ liệu bị hạn chế nên không đưa lệnh thực thi chúng. Thời gian chạy đầy đủ từng entrypoint: chưa có nguồn đo thống nhất. | ĐÃ CÓ | S08/S09; script theo commit S07/S10/`879d24f`/`3e6f0d8`/`e88d82c`; thời gian đầy đủ: KHÔNG CÓ NGUỒN |
| I2 | Môi trường feature/OOF tuần 9: Python 3.14.5, numpy 2.4.6, pandas 2.3.3, scipy 1.18.1, sklearn 1.9.1. B2 trong môi trường riêng: torch 2.6.0, transformers 4.51.3, sentence-transformers 4.1.0, numpy 2.5.4, scipy 1.18.1, sklearn 1.9.1; pandas không cài trong môi trường B2 đó. Không trộn thành một environment duy nhất. | ĐÃ CÓ | S08 VERSIONS; S09 B2 PACKAGE lines 1476–1482 |
| I3 | `i3_ma_bam_nguon_dev.csv`: đường dẫn và SHA256 hiện tại của bảng dự đoán development, mô hình và log/kết quả đã dùng. `t3_heldout_predictions.csv` kèm fold; `b2_oof.csv` kèm fold. Artifact gitignored không có commit riêng, được chốt hash trong commit NEW. Không mở/hash lại file dự đoán Test. | TÍNH MỚI (dev) | CMD → CSV; commit NEW; các log chỉ băm byte, không xuất nội dung bài |

## J

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| J1 — tuần 1 | Chưa tìm thấy hồ sơ ánh xạ tuần học 1 với công việc/quyết định ELLIPSE. | KHÔNG CÓ NGUỒN | S15 có mốc ngày/Phase, không có ánh xạ tuần 1 |
| J1 — tuần 2 | Chưa tìm thấy ánh xạ tuần học 2. | KHÔNG CÓ NGUỒN | S15; git log tại `7559292` |
| J1 — tuần 3 | Chưa tìm thấy ánh xạ tuần học 3. | KHÔNG CÓ NGUỒN | S15; git log tại `7559292` |
| J1 — tuần 4 | Chưa tìm thấy ánh xạ tuần học 4. | KHÔNG CÓ NGUỒN | S15; git log tại `7559292` |
| J1 — tuần 5 | Chưa tìm thấy ánh xạ tuần học 5. | KHÔNG CÓ NGUỒN | S15; git log tại `7559292` |
| J1 — tuần 6 | Chưa tìm thấy ánh xạ tuần học 6. | KHÔNG CÓ NGUỒN | S15; git log tại `7559292` |
| J1 — tuần 7 | Chưa tìm thấy ánh xạ tuần học 7. | KHÔNG CÓ NGUỒN | S15; git log tại `7559292` |
| J1 — tuần 8 | Chưa tìm thấy ánh xạ tuần học 8. Không tự đồng nhất Phase 8 với tuần 8. | KHÔNG CÓ NGUỒN | S15; git log tại `7559292` |
| J1 — mốc trước tuần 9 | 20/09/2026 reset/scoping; 21/09 chấp nhận ELLIPSE; 23/09 khóa bài toán/split/14 feature/privacy gate; 24/09 train 4 pipeline và đánh giá Validation. Chuyển từ lịch sử CapyVocab sang ELLIPSE được ghi trong git, không gán tuần học. | ĐÃ CÓ | S15; git commit `2c7982e` “rebuild project around ELLIPSE scoring pipeline”; tài liệu ghi ngày thực hiện, commit ghi ngày lưu lịch sử |
| J1 — tuần 9 | Tái lập kết quả khóa; đổi anchor RF/Ridge/cả hai để kiểm tra; GroupKFold theo đề; đọc 32 ca; phát hiện điểm mù cùng đặc trưng; thăm dò độ lệch cây, bootstrap ghép cặp. | ĐÃ CÓ | S08; commits `81aec90`, `364fd21`, `879d24f`, `3e6f0d8` |
| J1 — tuần 10 | Khóa tín hiệu; mẫu đọc ngẫu nhiên phân tầng; kiểm tra provenance đọc mù; TF-IDF/MiniLM không fine-tune; GECToR/ERRANT đối chiếu đếm lỗi; dùng lại Test có phép và ghi thăm dò; chuẩn bị interview. | ĐÃ CÓ | S09; S11/S12; commits `4e38115`, `e88d82c`, `97159a6`, `7559292` |
| J2 — lần 1 | Phase 9 dùng Test cho D/baseline chính; 47/208, p=0,188324671369. Ngày truy cập đầu tiên và người cho phép lần đó: chưa có nguồn độc lập. Tuần 9 là tái lập số đã lưu, không chứng minh là lần truy cập đầu. | ĐÃ CÓ | S08 Task 0; `reports/week9/t0_provenance.md` commit `24399b7`; phần ngày/cho phép: KHÔNG CÓ NGUỒN |
| J2 — lần 2 | Thầy cho phép 26/10/2026 theo xác nhận người phụ trách, chỉ tín hiệu đã khóa; đã có lần gọi STOPPED trước attempt2 COMPLETED; 55/208, p=0,0115857068471. Kết quả Test dùng lại là thăm dò, không phải xác nhận độc lập sạch. | ĐÃ CÓ | S12; lịch sử kỹ thuật F5, không bỏ qua lần dừng |

## K

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| K1 | Tại HEAD trước nhiệm vụ: Đào Hải Nam 30 commit, CapyVocab Developer 11, hainam1 2; vùng file theo tác giả trong `k1_tac_gia_git.csv`. Đếm commit reachable từ HEAD, gồm merge và lịch sử dự án cũ; tên là author git nguyên trạng, không xác nhận danh tính/người thực hiện. Không có bằng chứng gán số commit cho Giang/Linh. | ĐÃ CÓ | `git log 755929233dab6aee1983dfa028f2be1ed3e7f87c --format=%an --name-only`; CSV tái lập bằng CMD, commit NEW |
| K1 — đóng góp ngoài git | Không suy việc đọc, trình bày, phụ trách mô hình hoặc mức đóng góp từng thành viên từ tên author/file mẫu. Chưa có nhật ký đóng góp đã hoàn thành được xác minh trong hồ sơ này. | KHÔNG CÓ NGUỒN | S14 có ghi nhóm đọc lại, không phân công từng người; template không là bằng chứng hoàn thành |
| K2 | AI được ghi cho scoping, tổ chức repo, gợi ý debug/test, sửa tài liệu; nhật ký 20/09/2026 ghi Codex và còn yêu cầu người phụ trách review. Tuần 9 ghi AI coding agent hỗ trợ tổ chức nhận xét 32 bài theo quy trình hai lượt và 7 tiêu chí; nhóm đọc lại/adopt notes; AI hỗ trợ script/bảng. Đây là lời khai đã ghi, chưa chứng minh đọc mù độc lập. | ĐÃ CÓ | S14, Usage log/Week 9; provenance giới hạn: S09 |
| K2 — thiếu | Chưa có nhật ký chi tiết mọi lần dùng, model/version và bằng chứng ai đã kiểm tra từng artifact. Không coi câu “to review” là đã kiểm tra xong. | KHÔNG CÓ NGUỒN | S14, dòng Human verification và yêu cầu bổ sung material use |

## Các phần thiếu nguồn

| Mục | Giá trị | Trạng thái | Nguồn (file + commit/lệnh) |
|---|---|---|---|
| Danh sách | A2 lý do chọn 1,0; A3 lý do chọn 20%; B2 chuỗi lọc upstream; B3 người/ngày chia official upstream; D6 Validation TF-IDF/MiniLM; E4/J2 ngày truy cập Test đầu và phép lần đầu; G1 spread OOF từng bài; G3 danh tính/trình tự đọc mù/quy tắc lỗi đầy đủ; H1 tree 10%/30%; I1 thời gian đầy đủ từng pipeline; J1 ánh xạ tuần 1–8; K1 đóng góp từng thành viên ngoài git; K2 nhật ký AI/kiểm chứng chi tiết. | KHÔNG CÓ NGUỒN | Chi tiết và phạm vi đã ghi ở từng hàng A–K; không mở Test/corpus để bổ sung |
