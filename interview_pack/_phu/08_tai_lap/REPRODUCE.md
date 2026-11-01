# Tái lập và phạm vi thực thi
Gói hiển thị hoàn toàn offline; xem HTML/PDF/PNG không cần môi trường Python.
Hai kiểm tra tính toán chỉ cần Python standard library:
```
python interview_pack/07_kiem_tra_offline/check_d_88_of_386.py
python interview_pack/07_kiem_tra_offline/check_synthetic_ranking.py
```
Có thể đối chiếu nguồn gốc bằng cách truyền đúng reports/week9/t3_heldout_predictions.csv cho script đầu; chỉ lọc prompt_disjoint.
Bản kèm development_predictions.csv chỉ chứa ID, fold, nhãn và dự đoán development; không có văn bản, prompt hoặc thông tin cá nhân.
K là số nhãn sai lớn; k là ngân sách, tính ceil(0,20N) từng fold. Kỳ vọng cộng k_f*K_f/N_f. Không gộp thành một phép lấy 20% toàn cục.

## Nguồn sinh bảng đã lưu (ghi để truy xuất, KHÔNG chạy lại trong nhiệm vụ này)
- Bảng D: `.venv/Scripts/python.exe scripts/week9/t3_evaluate.py --capture`; nguồn RESULTS_week9.md / Task 3, Producer. Dự đoán lưu do quy trình huấn luyện trước tạo; không gọi lại quy trình có fit trong nhiệm vụ này.
- Cây 96/386: `.venv/Scripts/python.exe -u scripts/week9b/tree_spread_oof.py --append` (nguồn RESULTS_week9.md). Có fit lại fold, ngoài phạm vi được phép hiện tại.
- Khoảng ghép cặp: `.venv/Scripts/python.exe -u scripts/week9b/paired_tree_spread.py --append` (nguồn cùng RESULTS). Bootstrap 44 normalised_prompt, 2000 lượt, seed 42; giữ hàng đợi, không rerank. CI có điều kiện trên mô hình OOF đã fit.
- Test: chỉ trích log/RESULTS đã lưu; không chạy lệnh đánh giá Test, không cần có đầu vào Test để dùng gói.

## Môi trường suy luận development đã kiểm tra
Python 3.14.5; scikit-learn 1.9.1; NumPy 2.4.6; joblib 1.6.0; seed cấu hình 42. Phiên bản khớp hồ sơ RESULTS_tree_spread_second_use.md và môi trường .venv tại lúc dựng gói.
`extract_saved_models.py` dùng joblib/NumPy; cần reports/week9/t3_eligible_development.csv, outputs/phase6/feature_schema.json và bốn model Ridge/RF ở outputs/phase6. Chỉ chọn hai ID source_partition=official_train; kiểm hash trước/sau; không gọi fit. Kết quả là phép tính Phase 6 riêng, không thay dự đoán OOF.
`build_pack.py` dùng reportlab, Pillow, PyMuPDF; đọc allowlist cố định trong script. Fonts Arial tại C:/Windows/Fonts. Mọi script mới nằm trong gói.

## File tối thiểu để kiểm tra và truy xuất
- 07_kiem_tra_offline/development_predictions.csv và hai script cùng thư mục.
- Nguồn dự đoán gốc reports/week9/t3_heldout_predictions.csv; ID/fold theo reports/week9/t3_fold_composition.csv, bản trích trong nguon/.
- reports/week9/t3_pooled.csv, t3_regression.csv, RESULTS_week9.md.
- reports/week9/RESULTS_tree_spread_second_use.md và hai log JSON (không phải dữ liệu Test).
- reports/week10/gec_part_a_68.csv, b2_oof.csv, RESULTS_week10.md; chỉ cần khi dựng lại gói.
- docs/data_card.md, signal_lock_tree_spread.md, split_and_leakage_protocol.md, phieu_luyen_*.md, du_lieu_interview.md, llm_disclosure.md.
Chi tiết hash nguồn đọc thực tế ở SOURCES.sha256. Không sao chép corpus, workbook có bài luận hoặc model vào gói.

## Bổ sung 11–15
`python interview_pack/08_tai_lap/supplement_pack.py` dựng lại cả gói nền và phần bổ sung, không mô hình/không fit/không Test. Sau kiểm tra hình, chạy finalize_pack.py để chốt manifest. Cần Python với reportlab, Pillow, PyMuPDF và font Arial. Nguồn được kiểm tra bằng SUPPLEMENT_SOURCES.sha256.
