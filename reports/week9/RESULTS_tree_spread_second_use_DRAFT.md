# Nháp RESULTS — Official Test lần dùng thứ hai

**CHƯA CHẠY.** Ngày thầy cho phép: **26/10/2026**. Nguồn: **nhận xét tuần 10 của thầy Khánh**, theo xác nhận của người phụ trách trong cuộc trao đổi này.

Official Test lần dùng thứ hai, cho tín hiệu đã khóa, dùng lại RF đã lưu từ tuần 9; không phải xác nhận độc lập sạch; không có tín hiệu nào khác được thử

## T0: nhận diện mô hình trước truy cập Test

| Đích | File mô hình | SHA256 đã đối chiếu với file hiện tại |
|---|---|---|
| Vocabulary | `outputs/phase6/random_forest_vocabulary.joblib` | `899e9283e2eb01b4df6913eadd6cf8a4a823df0298ddfe820d14ba5912ffe7be` |
| Grammar | `outputs/phase6/random_forest_grammar.joblib` | `bc285a202de126247240982696ca94c16dbee82bf15906d8e75ebdf4405a8f91` |

Nguồn nhận diện: `docs/evaluation_protocol_freeze.md`, mục Frozen artifacts and features; `reports/week9/RESULTS_week9.md`, các dòng `READ_AUDIT outputs/phase6/random_forest_*.joblib` (1392–1393); `docs/data/phase9_tables/artifact_manifest.json`, mục `phase6_model_sha256`.

Tập huấn luyện: **3.050 bài model_train có `privacy_review_status=not_flagged`**, trong 3.128 bài model-train gốc; không gồm Validation hoặc Official Test. Nguồn: `reports/week9/RESULTS_week9.md`, `FROZEN_FIT_RECORD` (379–380), xác nhận cả hai RF fit lại trên toàn bộ 3.050 bài đủ điều kiện; `reports/week9/t3_eligibility_counts.csv`, dòng model_train; `reports/week9/t3_eligibility_code.csv`, quy tắc lọc trong training_pipeline. Nguồn đặc trưng development được ghi ở `reports/week9/t3_eligibility_sources.csv`: `data/05_model_features/development_features_with_targets.csv`.

Liên hệ với kết quả cũ: `docs/phase9_official_test_evaluation.md`, mục Population and integrity, xác nhận dùng mô hình Phase 6 khớp hash và không huấn luyện lại; mục Frozen primary review comparison ghi D bắt **47/208** trên **2.518** bài. `reports/week9/t0_provenance.md`, mục Reproduction and evidence, ghi lại cùng kết quả và đường dẫn bảng dự đoán `outputs/predictions/official_test_predictions.csv`. Đây là kết quả D đã có, không phải kết quả mới của độ phân tán cây; script mới không tính D.

File khóa `docs/signal_lock_tree_spread.md` khớp SHA256 `d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca`, tại commit khóa `4e381150edf08d49a134505e669058f1e0d27b48`. Chỉ dùng lại pipeline đã lưu, không fit hoặc thay đổi mô hình. Metadata hai pipeline đã kiểm tra: 300 cây, max_depth=10, max_features=sqrt, min_samples_leaf=2/5, random_state=42, n_jobs=1, imputer trung vị.

## Kế hoạch chạy đã bảo vệ — chưa thực hiện

Script: `scripts/tree_spread_official_test_second_use.py`. Gọi không có tham số sẽ thoát trước mọi truy cập Test, kể cả đọc hash. Chỉ `--i-have-permission` mới cho phép chạy. Không thực thi lệnh có cờ này trong T0.

Trước tính tín hiệu, script kiểm tra hash file khóa, cả hai mô hình và các nguồn đầu vào so với manifest đã lưu; xác nhận đúng 2.518 ID đủ điều kiện; dự đoán RF khớp bảng dự đoán cũ theo ID (rtol=0, atol=1e-12 chỉ cho sai số vòng đọc CSV); tập ID sai lớn khớp và số sai lớn đúng 208. Lệch bất cứ kiểm tra nào: dừng, ghi lý do, không tính hoặc xuất kết quả tín hiệu. Các lỗi sau bước này cũng không được xuất kết quả tín hiệu.

Chỉ đọc 14 đặc trưng số, ID/trạng thái đủ điều kiện, hai dự đoán RF và hai nhãn số tổng hợp đã lưu trong `docs/data/phase9_tables/large_error_labels.csv`. Không mở CSV bài luận gốc, corpus hoặc tính tín hiệu khác.

Tín hiệu duy nhất: max(std của 300 cây Vocabulary, std của 300 cây Grammar), ddof=0. Xếp giảm dần, hòa thì essay_id dạng chuỗi tăng dần. Một tập holdout cố định; k=ceil(0,20×N), dự kiến **504** nếu N=2.518. Nhãn sai lớn: max sai số tuyệt đối hai đích RF ≥ 1. Kỳ vọng ngẫu nhiên kK/N; p chính xác một phía = hypergeom.sf(C−1,N,K,k). Không bốc mẫu ngẫu nhiên, không đổi ngưỡng hoặc ngân sách.

Log dự kiến: `reports/week9/tree_spread_official_test_second_use_log.json`; ghi commit chạy, hash script/file khóa/mô hình/nguồn số, cohort, một holdout cố định, các kiểm tra và kết quả. File log được tạo độc quyền, không ghi đè hoặc tự chạy lại nếu log đã tồn tại. Ô ngày thầy cho phép trong log giữ trống cho người phụ trách điền. Log chưa được tạo trong T0.

## Lịch sử dùng Test và ô kết quả chờ điền

Lần dùng đầu: kết quả Phase 9 đã lưu; tuần 9 tái tính từ dự đoán cũ, không huấn luyện lại. Ngày truy cập Test đầu tiên **không xác định được từ lịch sử sẵn có** theo `reports/week9/t0_provenance.md`; không dùng ngày commit thay ngày chạy. Lần thứ hai đang được chuẩn bị ở đây chỉ đánh giá tín hiệu cây đã khóa; dùng lại Test đã được xem nên không phải xác nhận độc lập sạch. Phạm vi này theo chỉ dẫn người phụ trách, thay yêu cầu cohort mới và so sánh thêm D trong giao thức gốc; không sửa file khóa.

| Trường sau khi được phép chạy | Kết quả thực chạy |
|---|---|
| Ngày thầy cho phép | 26/10/2026; nguồn: nhận xét tuần 10 của thầy Khánh, theo xác nhận của người phụ trách |
| Ngày giờ thực chạy / commit / hash file khóa | |
| Số bài đủ điều kiện N / ngân sách k | |
| Số bài sai lớn K / số bắt được C | |
| Kỳ vọng ngẫu nhiên kK/N | |
| p chính xác một phía | |

T0 chỉ đọc tài liệu, mã nguồn và metadata/mã băm mô hình; chưa mở dữ liệu, nhãn, đặc trưng hoặc bảng dự đoán Test; chưa chạy tín hiệu trên Test.
