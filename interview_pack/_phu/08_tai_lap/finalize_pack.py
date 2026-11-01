"""Validate pack contents and write a non-self-referential SHA256 manifest."""
from pathlib import Path
import csv, hashlib, json, re, sys
import fitz
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[1];R=P.parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def data(rel):
 with (P/rel).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
source_count=0
for line in (P/'08_tai_lap/SOURCES.sha256').read_text(encoding='utf-8').splitlines():
 h,rel=line.split('  ',1);assert digest(R/rel)==h,rel;source_count+=1
for line in (P/'08_tai_lap/SUPPLEMENT_SOURCES.sha256').read_text(encoding='utf-8').splitlines():
 h,rel=line.split('  ',1);assert digest(R/rel)==h,rel
lock=P/'12_mang_theo/signal_lock_tree_spread.md'
assert lock.read_bytes()==(R/'docs/signal_lock_tree_spread.md').read_bytes()
assert digest(lock)=='d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca'
table34=data('12_mang_theo/bang_3_4.csv')
assert [(int(x['shared_of_386']),int(x['caught_of_386'])) for x in table34]==[(276,88),(233,81),(217,93)]
assert [(x['old276_remain'],x['old276_fixed']) for x in table34[1:]]==[('203','73'),('191','85')]
for rel in ['15_review_tuan10_mau/ba_hanh_dong.csv','15_review_tuan10_mau/moi_thanh_vien_mot_buoc.csv']:
 assert len(data(rel))==3 and all(all(v=='' for v in row.values()) for row in data(rel))
assert '**__________**' in (P/'11_ba_cau_giai_thich/cau_lich_su_dung_test.md').read_text(encoding='utf-8')
ar=json.loads((P/'02_mau_truy_vet/saved_model_arithmetic.json').read_text(encoding='utf-8'))
for name,m in ar['models'].items():assert digest(R/m['source'])==m['sha256']
main=data('04_bang_ket_qua/bang_chinh.csv')
assert [(int(r['caught']),int(r['K'])) for r in main]==[(88,386),(44,276),(96,386),(47,208),(55,208)]
q=data('07_kiem_tra_offline/development_predictions.csv')
assert len(q)==3812 and all(r['split_type']=='prompt_disjoint' for r in q)
assert set(q[0])=={'essay_id','split_type','fold','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G'}
cases=data('05_ca_loi/5_ca_cho_hai_ban.csv')
assert len(cases)==5 and all(r['reader_B_count']==r['reader_explanation']=='' for r in cases)
assert all(all(v=='' for v in row.values()) for row in data('05_ca_loi/mau_10_ca.csv'))
assert data('09_dong_gop_va_ai/mau_nhat_ky_dong_gop.csv')==[]
pages=0
for f in P.rglob('*.pdf'):
 with fitz.open(f) as d:
  pages+=len(d)
  for page in d:
   assert page.get_text().strip()
   for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
     for span in line['spans']:
      x0,y0,x1,y1=span['bbox'];assert x0>=-1 and y0>=-1 and x1<=page.rect.width+1 and y1<=page.rect.height+1,(f,span)
pngs=list(P.rglob('*.png'))
for f in pngs:
 with Image.open(f) as image:image.verify()
# No learner prose/name columns are present in any exported CSV.
for f in P.rglob('*.csv'):
 with f.open(encoding='utf-8-sig',newline='') as handle:
  headers=next(csv.reader(handle))
  assert not set(headers)&{'essay_text','full_text','first150_words','student_id','student_name','full_name','Identifying_Info'},f
index=(P/'00_START_HERE.html').read_text(encoding='utf-8')
for url in re.findall(r'href="([^"]+)"',index):
 rel=url.split('#')[0]
 if rel!='FILE_LIST.md':assert (P/rel).exists(),url
assert not re.search(r'(?:src|href)=["\']https?://',index)
report=f'''# Kiểm định gói cuối
Đã kết xuất và kiểm tra trực quan cả {len(list(P.rglob('*.pdf')))} PDF, tổng {pages} trang, cùng các PNG trình chiếu/đầu ra; chữ tiếng Việt, nguồn, bảng và tên file hiển thị đúng. Ảnh ghép có tên file: contact_01.png, contact_02.png, contact_03.png, contact_04_bo_sung.png. Từng trang PDF có bản PNG riêng và pdf_pages.csv để truy vết.
Kiểm tra tự động: toàn bộ PDF có văn bản trong biên trang; {len(pngs)} PNG giải mã được; mọi link HTML nội bộ hợp lệ; không có CDN hay phụ thuộc mạng.
Hai script đã chạy thành công; stdout thực tế và ảnh kết xuất stdout ở 07_kiem_tra_offline/. D=88/386, budget=764, kỳ vọng=77,362908; thời gian tính khoảng 0,04 giây, dưới 10 giây. Ví dụ giả N=10, K=3, budget=2, caught=1, kỳ vọng=0,6. Nguồn: các file *_output.txt, script và CSV đầu vào cùng thư mục.
{source_count} hash nguồn văn bản/bảng và bốn hash model đã kiểm lại, không thay đổi so với lúc dựng. Hai RF khớp 899e9283…e7be và bc285a20…8f91; mỗi phép cộng Ridge và trung bình 300 cây khớp trong sai số dưới 1e-11 (nguồn saved_model_arithmetic.json).
Nguồn dữ liệu được xuất theo danh sách cột: ID bài, nhãn, đặc trưng, dự đoán và metadata phương pháp. Không xuất văn bản bài luận, mã sinh viên hoặc họ tên đầy đủ; chỉ dùng ba nhãn thư mục thành viên được yêu cầu. Không giải mã workbook chứa bài luận.
Không mở Official Test, full_clean_corpus_6482.csv hoặc corpus gộp trong nhiệm vụ; không chạy Test, không fit lại mô hình; chỉ suy luận trên hai dòng development bằng model đã lưu. Không sửa code kết quả đã commit. Gói được bỏ qua bằng .git/info/exclude; không stage/commit dữ liệu.
Thiếu bằng chứng được ghi ở 08_tai_lap/THIEU_VA_DOI_CHIEU.md. Có 32 ghi nhận đọc cũ, trong đó 22 RF sai lớn; 0/5 cặp phiếu mới đủ điều kiện so sánh độc lập (nguồn docs/du_lieu_interview.md, không kiểm workbook mới trong nhiệm vụ).
Bổ sung 11–15: hình nén ghi đúng chiều OLS thật~RF (beta=r/q), biểu đồ RF~thật (slope=r*q). Các bộ hệ số khớp RESULTS_week10.md / Part B; bảng 3.4 đối chiếu 276/233/217, 88/81/93, 203/73 và 191/85. Số 15,0 và 16,6 đã có nguồn: 100*35/233 và 100*36/217, không còn ghi thiếu nguồn. Hai hình và bảng PNG mở offline được. Bản khóa sao nguyên byte, hash khớp d2eabcb7…8eca. Ngày cho phép dùng Test, ba hành động và bước pipeline của thành viên đều để trống.
MANIFEST.sha256 liệt kê mọi file trong gói, trừ chính manifest vì không thể chứa ổn định hash của chính nó. Hash manifest được báo riêng trong kết quả giao gói. Thay đổi bất kỳ file nào sau khi chốt cần chạy lại finalizer.
'''
(P/'_kiem_tra/hien_thi/VERIFICATION.md').write_text(report,encoding='utf-8')
expected=[p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and p.name not in ['MANIFEST.sha256','FILE_LIST.md']]+['FILE_LIST.md','MANIFEST.sha256']
(P/'FILE_LIST.md').write_text('# Danh sách file\n\n'+''.join(f'- [{rel}]({rel})\n' for rel in sorted(expected)),encoding='utf-8')
files=sorted([p for p in P.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256'])
(P/'MANIFEST.sha256').write_text(''.join(f'{digest(p)}  {p.relative_to(P).as_posix()}\n' for p in files),encoding='utf-8')
for line in (P/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
 h,rel=line.split('  ',1);assert digest(P/rel)==h
print(f'PASS: {len(files)} manifest entries; {pages} PDF pages; {len(pngs)} PNGs; source integrity; privacy columns; blank templates; internal links.')
print('MANIFEST_SHA256='+digest(P/'MANIFEST.sha256'))
