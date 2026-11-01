# Đề cương báo cáo cuối - khung 6–8 trang

Chỉ là đề cương. Nguồn định hướng: chỉ dẫn người dùng trong yêu cầu bổ sung, thuật lại trả lời câu 2 của thầy; chưa có bản trả lời gốc để xác minh. Phân bổ trang dưới đây là đề xuất biên tập, không phải quy định mới của thầy. Không fine-tune encoder; giữ MiniLM như nguồn đối chiếu đã lưu.

| Phần nội dung | Trọng tâm cần trình bày | Ánh xạ cấu trúc 6–8 trang | Bằng chứng dự kiến |
|---|---|---|---|
| (1) So cách ưu tiên đọc | Đối chiếu D với ngẫu nhiên, Ridge extremity (xa trung vị dự đoán, không dùng điểm thật để chọn), bài ngắn nhất; giữ cùng nhãn, ngân sách và phá hòa | Tóm tắt/Giới thiệu; Dữ liệu/Phương pháp; Thiết lập thí nghiệm; Kết quả | 04_bang_ket_qua; week9/t3_pooled.csv; biểu đồ nén về giữa |
| (2) Gộp nguồn thông tin | Một bảng so Ridge, TF-IDF, MiniLM: cùng sai, bắt lỗi, kỳ vọng, nhóm 276; không mở rộng thành phần fine-tune | Dữ liệu/Phương pháp; Thiết lập; một bảng trong Kết quả | 12_mang_theo/bang_3_4.pdf; reports/week10/RESULTS_week10.md |
| (3) Phân tích mọi mô hình cùng sai | Ưu tiên ca có RF/Ridge/TF-IDF/MiniLM đều sai; công khai quy tắc chọn, đích, thiếu dữ liệu và trạng thái đọc; chỉ tổng hợp nhận xét thành viên đã xác nhận | Kết quả/Phân tích lỗi là phần trọng tâm; giới hạn ở Thảo luận/Kết luận | 05_ca_loi; 14_luot_di_qua; bảng dự đoán development đã lưu; không tự coi 191 ca RF/Ridge/MiniLM là giao của cả bốn |
| (4) Nghiên cứu cùng dữ liệu | Một đoạn ngắn: bài liên quan, cùng ELLIPSE nhưng khác split/nhãn/nhiệm vụ thì giới hạn khả năng so | Giới thiệu hoặc Thảo luận; Tham khảo | Chỉ dùng tài liệu đã đọc và có trích dẫn; chưa điền số từ nghiên cứu khác |

Gợi ý bố cục tổng thể: Tóm tắt/Giới thiệu → Dữ liệu/Phương pháp → Thiết lập thí nghiệm → Kết quả/Phân tích lỗi → Thảo luận/Kết luận → Tham khảo/Phụ lục. Điều chỉnh để nằm trong 6–8 trang theo chỉ dẫn được cung cấp; chưa mặc định phụ lục có tính vào giới hạn.

Phụ lục: GECToR, bảng phụ theo fold/vùng điểm, CI và đơn vị bootstrap, lịch sử Test, hash và lệnh tái lập. Trong thân bài chỉ dẫn tới phụ lục khi cần. Thành viên tự viết nội dung, kết luận, quyết định và khai báo AI.
