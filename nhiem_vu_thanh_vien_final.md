# HƯỚNG DẪN ĐỌC VÀ ĐÁNH GIÁ 10 CA LỖI (NHÓM 03 - ELLIPSE)

Tài liệu này hướng dẫn hai thành viên trong nhóm thực hiện quy trình đọc độc lập, khách quan 10 ca lỗi (development) nhằm thu thập bằng chứng định tính cho báo cáo cuối kỳ.

---

## 1. Phân công nhiệm vụ

| Thành viên | Phạm vi mã ca được phân công | Tệp văn bản đọc trước | Tệp phiếu đọc | Tệp đối chiếu (chỉ mở ở Bước 2) |
| :--- | :---: | :---: | :---: | :---: |
| **Giang** | **CA01 đến CA05** (5 ca) | `local_only/doc_10_ca/1_doc_truoc/CA01.txt` ... `CA05.txt` | `local_only/doc_10_ca/phieu_doc_10_ca.xlsx` | `local_only/doc_10_ca/2_doi_chieu/CA01_doi_chieu.txt` ... `CA05_doi_chieu.txt` |
| **Linh** | **CA06 đến CA10** (5 ca) | `local_only/doc_10_ca/1_doc_truoc/CA06.txt` ... `CA10.txt` | `local_only/doc_10_ca/phieu_doc_10_ca.xlsx` | `local_only/doc_10_ca/2_doi_chieu/CA06_doi_chieu.txt` ... `CA10_doi_chieu.txt` |

---

## 2. Quy trình thực hiện (Bắt buộc theo thứ tự)

### BƯỚC 1: ĐỌC MÙ (TRƯỚC KHI BIẾT ĐIỂM)
> [!IMPORTANT]
> **Tuyệt đối KHÔNG mở thư mục `2_doi_chieu` trong Bước 1.** Mọi quan sát về từ vựng, ngữ pháp phải được ghi nhận độc lập dựa trên năng lực ngôn ngữ của người đọc mà không bị định kiến bởi điểm thật hay dự đoán của mô hình.

1. Mở các file bài viết được phân công trong thư mục:
   `local_only/doc_10_ca/1_doc_truoc/`
2. Mở file Excel: `local_only/doc_10_ca/phieu_doc_10_ca.xlsx`, chọn sheet **`doc_truoc`**.
3. Điền các cột cho từng ca (từ dòng 2 đến dòng 6 hoặc dòng 7 đến 11):
   - `nguoi_doc`: Tên người đọc (Giang hoặc Linh).
   - `ngay_gio_bat_dau`: Thời điểm bắt đầu đọc bài.
   - `ngay_gio_luu`: Thời điểm hoàn thành đánh giá bài.
   - `pham_vi_doc`: Ghi rõ phạm vi (ví dụ: `150 từ đầu` hoặc `toàn bài`).
   - `so_loi_ngu_phap_150_tu`: Số lỗi ngữ pháp đếm thủ công trên 150 từ đầu tiên.
   - `quan_sat_tu_vung`: Nhận xét về vốn từ, độ phong phú, lỗi dùng từ.
   - `cau_trich_tu_vung (≤15 từ)`: Trích một câu/cụm ngắn (tối đa 15 từ) minh họa cho nhận xét từ vựng.
   - `quan_sat_ngu_phap`: Nhận xét về cấu trúc câu, lỗi chia thì, hòa hợp chủ vị, câu đơn/ghép.
   - `cau_trich_ngu_phap (≤15 từ)`: Trích một câu/cụm ngắn (tối đa 15 từ) minh họa cho nhận xét ngữ pháp.
   - `muc_V_thap_trung_cao`: Ước lượng mức Từ vựng (`Thấp`, `Trung`, hoặc `Cao`).
   - `muc_G_thap_trung_cao`: Ước lượng mức Ngữ pháp (`Thấp`, `Trung`, hoặc `Cao`).
4. **Lưu file Excel** trước khi chuyển sang Bước 2.

---

### BƯỚC 2: ĐỐI CHIẾU VÀ ĐÁNH GIÁ NGUYÊN NHÂN LỖI
Sau khi đã hoàn tất và lưu sheet `doc_truoc`, người đọc chuyển sang đối chiếu:

1. Mở file đối chiếu tương ứng trong thư mục:
   `local_only/doc_10_ca/2_doi_chieu/CAxx_doi_chieu.txt`
   *(File chứa: điểm thật, dự đoán RF/Ridge, sai số, giá trị D và thứ hạng, 14 đặc trưng z-score, cảnh báo LanguageTool 6.6 và sửa đổi GECToR + ERRANT trên 150 từ đầu).*
2. Trong file Excel `local_only/doc_10_ca/phieu_doc_10_ca.xlsx`, chọn sheet **`sau_doi_chieu`**.
3. Điền các cột:
   - `nguoi_doc`: Tên người đọc.
   - `ngay_gio`: Thời điểm điền đối chiếu.
   - `diem_that_co_hop_ly`: `Có` / `Không` / `Nghi ngờ nhãn rater`.
   - `nguyen_nhan_nghi_ngo`: Nhận định vì sao mô hình đoán sai lớn (ví dụ: bài quá ngắn/dài, từ vựng phong phú nhưng ngữ pháp yếu, lỗi thuộc nhóm đặc trưng bị trần/sàn, v.v.).
   - `la_quan_sat_hay_chi_nghi_ngo`: Ghi rõ nhận định dựa trên bằng chứng đọc được (`Quan sát`) hay phỏng đoán (`Nghi ngờ`).
   - `buoc_kiem_tra_tiep`: Đề xuất bước kiểm chứng tiếp theo (nếu có).
   - `quyet_dinh`: Kết luận ca này (ví dụ: `Giữ nhãn - mô hình sai`, `Nghi rò rỉ rater`, `Thiếu đặc trưng bắt lỗi`).
4. Lưu file Excel hoàn thiện.

---

## 3. Lưu ý bảo mật dữ liệu
- Thư mục `local_only/` đã được git-ignore và tuyệt đối **không được đẩy lên GitHub** hay bất kỳ kho công khai nào để tuân thủ giấy phép CC BY-NC-SA 4.0 và quy định của học phần.
- Các trích dẫn văn bản trong phiếu đọc tuyệt đối không vượt quá 15 từ.
