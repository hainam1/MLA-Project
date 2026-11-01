# Truy vết hai bài development
CSV một dòng và PNG dùng dự đoán held-out GroupKFold theo đề từ hồ sơ đã lưu.
Ridge: y_hat = intercept + sum_j(coefficient_j * standardized_value_j).
Chuẩn hóa dùng trung bình/độ lệch chuẩn của tập đã fit, sau điền thiếu bằng trung vị tập fit.
RF: y_hat = sum(tree_prediction_t)/300, sau tiền xử lý của pipeline đã lưu.
Các file *_ridge_terms.csv, *_300_trees.csv và saved_model_arithmetic.json là phép tính từ mô hình Phase 6 đã lưu, đã kiểm SHA256; không phải mô hình OOF của bảng truy vết. Không ghép chúng để giải thích chính xác dự đoán OOF.
0514D25768A0 thuộc validation ban đầu; 684166ED2438 thuộc model_train ban đầu, nên phép tính từ mô hình Phase 6 của bài thứ hai là in-sample. Chỉ bảng OOF dùng để đánh giá held-out.
Không còn mô hình riêng của từng fold đã lưu được xác nhận trong nhiệm vụ này; vì vậy phân rã đúng các dự đoán OOF: để trống, lý do thiếu mô hình fold. Không fit lại để lấp khoảng trống.
Nguồn: docs/phieu_luyen_*.md; reports/week9/t3_eligible_development.csv; reports/week9/t3_heldout_predictions.csv; outputs/phase6/*.joblib; hash chi tiết trong JSON.
