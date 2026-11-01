## Slide 1: Giáo viên đọc lại bài nào trước?

- Sau khi bài viết hoàn tất, dự đoán hai điểm: Từ vựng và Ngữ pháp; ưu tiên giáo viên đọc lại 20% bài.
- Một dòng là một bài, nhận diện bằng essay_id. Đây là dự đoán điểm bài viết, không đo toàn bộ năng lực người học.
- “Sai lớn”: max(|RF_V − y_V|, |RF_G − y_G|) ≥ 1 điểm. D = max(|RF_V − Ridge_V|, |RF_G − Ridge_G|).
- Câu hỏi: bất đồng giữa hai máy có tìm được bài RF sai lớn tốt hơn đọc ngẫu nhiên cùng ngân sách?

Nguồn: docs/data_card.md; docs/signal_lock_tree_spread.md / Signal definition; reports/week9/RESULTS_week9.md / Task 3.

## Slide 2: Một bài đi từ đặc trưng đến nhãn

- ELLIPSE v1.0: bài viết học sinh lớp 8–12; điểm tổng hợp từ người chấm, thang 1–5, bước 0,5. Dùng hai đích V/G.
- Theo data card: CC BY-NC-SA 4.0; cho phép phân phối kèm điều kiện. Quyền hiển thị văn bản từng bài và xử lý riêng tư: chưa rõ.
- Nguồn gốc: 3.911 train + 2.571 Test; development đủ điều kiện = 3.812. Các tổng lấy từ hồ sơ, không mở corpus/Test.
- 0514D25768A0: 328 từ, 22 câu → RF V=3,201; Ridge V=3,407 → nhãn V=2; RF sai lớn. Xem PNG truy vết.

Nguồn: docs/data_card.md; reports/week9/t3_eligible_development.csv; docs/phieu_luyen_mot_bai_development.md; CSV và hash trong gói.

## Slide 3: Hai cách chia, hai vai trò đánh giá

- Chia gốc: Official train 3.911 → model-train 3.128 + Validation 783. Sau cổng riêng tư: development 3.812; Validation đủ điều kiện 762.
- Model-train: fit trung vị điền thiếu; Ridge fit thêm StandardScaler; CV để chọn tham số. Validation chọn/cố định cấu hình trước đánh giá chính.
- Thăm dò mới trên development: GroupKFold(5) theo normalised_prompt; mỗi lượt fit chỉ bốn fold còn lại. Fold giữ lại không có đề trùng phần fit.
- Official Test gốc 2.571; đủ điều kiện 2.518. Chỉ dùng sau chốt lựa chọn; đã dùng lại nên kết quả là thăm dò. Gói này chỉ trích kết quả tổng hợp đã lưu.

Nguồn: docs/split_and_leakage_protocol.md; reports/week9/t3_fold_composition.csv; RESULTS_week9.md / Week 9b. Xem sơ đồ riêng và ghi chú phạm vi.

## Slide 4: Baseline và hai họ mô hình



[
  {
    "model": "Mean",
    "MAE_V": "",
    "MAE_G": "",
    "assumption": "Điểm trung bình tập fit",
    "training_loss": "Bình phương sai số",
    "why": "Mốc hằng số để kiểm tra giá trị của ML",
    "source": "Chưa có nguồn cho MAE mean baseline cùng GroupKFold; không điền"
  },
  {
    "model": "Ridge",
    "MAE_V": 0.3734244371454302,
    "MAE_G": 0.46303653771248415,
    "assumption": "Quan hệ tuyến tính gần đúng trên đặc trưng chuẩn hóa",
    "training_loss": "SSE + alpha * ||beta||²",
    "why": "Giảm hệ số lớn, dễ phân rã",
    "source": "reports/week9/t3_regression.csv; prompt_disjoint, pooled"
  },
  {
    "model": "RF",
    "MAE_V": 0.37216506904049607,
    "MAE_G": 0.45540371959591663,
    "assumption": "Quan hệ phi tuyến; mẫu tương lai gần phân phối huấn luyện",
    "training_loss": "Cây giảm bình phương sai số; lấy trung bình",
    "why": "Mô hình tương tác và ngưỡng đặc trưng",
    "source": "reports/week9/t3_regression.csv; prompt_disjoint, pooled"
  }
]

Nguồn: reports/week9/t3_regression.csv, prompt_disjoint / pooled; cấu hình: docs/signal_lock_tree_spread.md và RESULTS_week9.md / Week 9b. MAE là sai số tuyệt đối trung bình; khác loss huấn luyện. Mean baseline cùng phép chia: chưa có nguồn cho MAE.

## Slide 5: Cùng ngân sách đọc 20%, cùng cách phá hòa



[
  {
    "scope": "Dev - D",
    "N": 3812,
    "K": 386,
    "budget": 764,
    "caught": 88,
    "random": 77.362908429581,
    "base_rate": 0.1012591815320042,
    "source": "S1: reports/week9/t3_pooled.csv; prompt_disjoint, A1_RF, Disagreement"
  },
  {
    "scope": "Dev - D, cùng sai",
    "N": 3812,
    "K": 276,
    "budget": 764,
    "caught": 44,
    "random": 55.32185687702314,
    "base_rate": 0.07240293809024134,
    "source": "S1: reports/week9/t3_pooled.csv; prompt_disjoint, A3_Both_wrong, Disagreement"
  },
  {
    "scope": "Dev - độ lệch cây",
    "N": 3812,
    "K": 386,
    "budget": 764,
    "caught": 96,
    "random": 77.362908429581,
    "base_rate": 0.1012591815320042,
    "source": "S2: reports/week9/RESULTS_week9.md; Week 9b CAPTURE_METRICS"
  },
  {
    "scope": "Test - D đã lưu",
    "N": 2518,
    "K": 208,
    "budget": 504,
    "caught": 47,
    "random": 41.6330420969023,
    "base_rate": 0.08260524225575853,
    "source": "S3: reports/week9/RESULTS_week9.md; Task 0"
  },
  {
    "scope": "Test - cây, dùng lại",
    "N": 2518,
    "K": 208,
    "budget": 504,
    "caught": 55,
    "random": 41.6330420969023,
    "base_rate": 0.08260524225575853,
    "source": "S4: reports/week9/tree_spread_official_test_second_use_log_attempt2.json; result"
  }
]

S1: reports/week9/t3_pooled.csv (prompt_disjoint). S2: RESULTS_week9.md / Week 9b. S3: cùng RESULTS / Task 0. S4: tree_spread_official_test_second_use_log_attempt2.json / result. Các nguồn nằm dưới reports/week9; trích số offline tại 08_tai_lap/nguon.

## Slide 6: Kiểm tra đã lưu cho thấy điều gì?

- Nguồn thứ hai: TF-IDF bắt 81, MiniLM bắt 93 so D cũ 88 trên 386 lỗi. MiniLM chưa chứng minh hơn D: chênh +5, CI [−16,025; 27].
- Đếm lỗi trên 36 bài random: người đọc 7,33; công cụ cũ 1,24 (ước lượng). GECToR đếm 14,33, không gần người hơn ở mẫu này.
- Hệ quả diễn giải: chưa coi đồng thuận là đúng; chưa coi công cụ đếm là nhãn chuẩn. “Quyết định nhóm đổi”: để trống cho thành viên xác nhận.
- Cây so D: +8 [−11; 27] ở development. Bootstrap 44 cụm đề, 2.000 lượt, seed 42; giữ hàng đợi; chưa chứng minh hơn D.

Nguồn: reports/week10/RESULTS_week10.md / B2 concise tables, Exploratory Part A; reports/week9/RESULTS_week9.md / paired tree spread. Quyết định cá nhân: mẫu trống.

## Slide 7: Ca lỗi: hai máy gần nhau vẫn cùng sai

- 0514D25768A0: 328 từ; mtld=87,872; mattr=0,807; tỷ lệ câu phức=0,591. Chỉ mô tả đặc trưng, không gán nguyên nhân.
- V / G: nhãn 2 / 2; RF 3,201 / 2,785; Ridge 3,407 / 2,993; MiniLM 3,255 / 2,819.
- D=0,208493; hạng 174/769, ngoài 154 bài được đọc. RF và Ridge cùng sai lớn ở Từ vựng.
- 150 từ đầu: người đọc 9 lỗi; công cụ cũ ước lượng 3,20; GECToR 12 chỉnh sửa ngữ pháp. Không coi chỉnh sửa là lỗi chuẩn.

Nguồn: docs/phieu_luyen_mot_bai_development.md; reports/week9/t3_heldout_predictions.csv; reports/week10/b2_oof.csv và gec_part_a_68.csv, đúng essay_id.

## Slide 8: Giới hạn và phần thành viên cần tự xác nhận

- Test lần đầu được báo cáo ở tuần 9; ngày truy cập đầu chưa xác định. 26/10: dừng 07:14 UTC; chốt chặn từ chối; hoàn thành 07:27 UTC.
- Kết quả sau nhiều lần chọn là thăm dò. Test cây 55/208 có p=0,0116 so ngẫu nhiên; không phải p chứng minh hơn D.
- Thiếu: hai phiếu độc lập hợp lệ, phân rã đúng mô hình từng fold, MAE mean cùng phép chia, rubric gốc. Số 15/16,6 đã có nguồn ở bảng 3.4 bổ sung.
- Đóng góp, quyết định, giờ và khai báo AI: thành viên tự điền mẫu. Hồ sơ AI trước đây chưa đủ nhật ký chi tiết.

Nguồn: reports/week9/RESULTS_tree_spread_second_use.md; docs/du_lieu_interview.md; docs/llm_disclosure.md. Thiếu nguồn được liệt kê ở 08_tai_lap/THIEU_VA_DOI_CHIEU.md.