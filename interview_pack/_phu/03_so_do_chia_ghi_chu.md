# Sơ đồ và phạm vi

Chia gốc: Official train 3.911 → model-train 3.128 + Validation 783. Sau cổng riêng tư: development 3.812; Validation đủ điều kiện 762.

Model-train: fit trung vị điền thiếu; Ridge fit thêm StandardScaler; CV để chọn tham số. Validation chọn/cố định cấu hình trước đánh giá chính.

Thăm dò mới trên development: GroupKFold(5) theo normalised_prompt; mỗi lượt fit chỉ bốn fold còn lại. Fold giữ lại không có đề trùng phần fit.

Official Test gốc 2.571; đủ điều kiện 2.518. Chỉ dùng sau chốt lựa chọn; đã dùng lại nên kết quả là thăm dò. Gói này chỉ trích kết quả tổng hợp đã lưu.

Nguồn: docs/split_and_leakage_protocol.md; reports/week9/t3_fold_composition.csv; reports/week9/RESULTS_week9.md.
