"""Validate the optimized pack; write FILE_LIST and manifest only after content."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,quote
from datetime import datetime,timezone,timedelta
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import csv,io,json,re,hashlib,time,os,sys
import fitz
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[2];A=P/'_phu';Q=A/'_kiem_tra/toi_uu'
for planned in ['BAO_CAO_KIEM_TRA.md','TREE.txt','FILE_LIST.md','MANIFEST.sha256']:
 if not (A/planned).exists():(A/planned).write_text('',encoding='utf-8')
expected=json.loads((A/'_cong_cu/expected_root.json').read_text(encoding='utf-8'))
assert set(p.name for p in P.iterdir())==set(expected)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
def stamp(p):return datetime.fromtimestamp(p.stat().st_mtime,timezone(timedelta(hours=7))).strftime('%Y-%m-%d %H:%M:%S.%f +07:00')
move=json.loads((A/'_kiem_tra/di_chuyen_toi_uu.json').read_text(encoding='utf-8'))
assert move['complete'] and not move.get('pending_locked')
assert not move['deleted_files']
for r in move['files']:
 assert (P/r['current']).exists(),r
 assert sha(P/r['current'])==r.get('sha256_after_move',r['sha256_before']),r
for r in move['files']:
 if r['original'] in ['01_trinh_chieu.pdf','03_so_do_chia.pdf','10_so_tay_so_lieu.pdf']:assert sha(P/r['original'])==r['sha256_before']
assert sha(A/'12_mang_theo/signal_lock_tree_spread.md')=='d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca'
page_counts={};bad_bounds=[];pdf_links=[];raster_pages=[]
for f in P.rglob('*.pdf'):
 with fitz.open(f) as doc:
  if f.parent==P:page_counts[f.name]=len(doc)
  for i,page in enumerate(doc):
   if f.parent==P:
    assert (Q/f'{f.stem}_page{i+1:02}.png').exists()
    if not page.get_text().strip():raster_pages.append(f.name+':'+str(i+1))
    for b in page.get_text('dict')['blocks']:
     for line in b.get('lines',[]):
      for s in line['spans']:
       x0,y0,x1,y1=s['bbox']
       if min(x0,y0)<0 or x1>page.rect.width or y1>page.rect.height:bad_bounds.append((f.name,i+1))
   for link in page.get_links():
    url=link.get('uri') or link.get('file')
    if url:pdf_links.append((f.relative_to(P).as_posix(),url))
assert not bad_bounds
assert page_counts=={'01_trinh_chieu.pdf':8,'02_mau_truy_vet.pdf':2,'03_so_do_chia.pdf':1,'04_bang_ket_qua.pdf':1,'06_lich_su_dung_test.pdf':1,'08_tai_lap.pdf':2,'10_so_tay_so_lieu.pdf':1,'11_ba_cau_giai_thich.pdf':3,'12_mang_theo.pdf':2,'13_cau_truc_bao_cao_cuoi.pdf':1,'14_luot_di_qua.pdf':2}
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def workbook_cells(p):
 with ZipFile(p) as z:
  wb=ET.fromstring(z.read('xl/workbook.xml'));sheets=[x.attrib['name'] for x in wb.find('s:sheets',NS)]
  ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
  allcells=[]
  for j,name in enumerate(sheets,1):
   d={}
   for cell in ET.fromstring(z.read(f'xl/worksheets/sheet{j}.xml')).findall('.//s:c',NS):
    v=cell.find('s:v',NS);value=v.text if v is not None else ''
    if cell.attrib.get('t')=='s' and value:value=ss[int(value)]
    elif cell.attrib.get('t')=='inlineStr':value=''.join(cell.find('s:is',NS).itertext())
    d[cell.attrib['r']]=value or ''
   allcells.append(d)
  return sheets,allcells
names,cells=workbook_cells(P/'05_ca_loi.xlsx');assert names==['Ca lỗi']
# First five explanations/conclusions are authorized summaries of submitted forms.
assert all(cells[0].get(f'{col}{row}','')=='' for row in range(11,16) for col in 'ABCDEFGHIJKL')
submitted=json.loads((A/'_cong_cu/workbook_input.json').read_text(encoding='utf-8'))['cases']
for rownum,r in enumerate(submitted,6):
 assert cells[0][f'J{rownum}']==r['submitted_explanation']
 assert cells[0][f'K{rownum}']==r['submitted_conclusion']
 assert float(cells[0][f'F{rownum}'])==r['reader_A_submitted_count']
 assert float(cells[0][f'G{rownum}'])==r['reader_B_submitted_count']
names,cells=workbook_cells(P/'09_dong_gop_va_ai.xlsx');assert names==['Nhật ký đóng góp','Khai báo AI']
assert all(cells[0].get(f'{c}{r}','')=='' for r in range(4,10) for c in 'ABCDE')
assert all(cells[0].get(f'{c}{r}','')=='' for r in range(14,17) for c in 'BCD')
assert all(cells[1].get(f'{c}{r}','')=='' for r in range(4,12) for c in 'BC')
with ZipFile(P/'15_review_tuan10_mau.docx') as z:
 doc=ET.fromstring(z.read('word/document.xml'));n={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 tables=doc.findall('.//w:tbl',n);assert len(tables)==2
 for t in tables:
  for row in t.findall('w:tr',n)[1:]:assert not ''.join(row.itertext())
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src','action']:self.urls.append(v)
broken=[];network=[];html_count=0;markdown_count=0
def check(base,url):
 s=urlsplit(url.strip('<>'))
 if s.scheme or s.netloc:network.append((base.relative_to(P).as_posix(),url));return
 if s.path:
  t=(base.parent/unquote(s.path)).resolve()
  if not t.is_relative_to(P) or not t.exists():broken.append((base.relative_to(P).as_posix(),url))
for f in P.rglob('*.html'):
 p=HTML();p.feed(f.read_text(encoding='utf-8-sig'))
 for url in p.urls:check(f,url);html_count+=1
for f,url in pdf_links:check(P/f,url)
# Exclude not-yet-authored canonical list; all preserved source Markdown links are checked.
for f in P.rglob('*.md'):
 if f==A/'FILE_LIST.md':continue
 for url in re.findall(r'\[[^\]]*\]\(([^)]+)\)',f.read_text(encoding='utf-8-sig')):check(f,url);markdown_count+=1
assert not broken and not network,(broken,network)
bat=json.loads((Q/'BAT_run.json').read_text());assert bat['returncode']==0 and bat['wall_seconds']<10
# Format-aware text extraction; no learner text is printed or compared with a corpus.
texts={};image_count=0
for f in P.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(P).as_posix()
 if f.suffix=='.png':
  with Image.open(f) as im:im.verify()
  image_count+=1
 elif f.suffix=='.pdf':
  with fitz.open(f) as d:texts[rel]='\n'.join(p.get_text() for p in d)
 elif f.suffix in ['.xlsx','.docx']:
  with ZipFile(f) as z:texts[rel]='\n'.join(z.read(n).decode('utf-8') for n in z.namelist() if n.endswith('.xml'))
 elif f.suffix in ['.md','.txt','.py','.mjs','.ps1','.bat','.json','.ndjson','.csv','.sha256','.html']:
  texts[rel]=f.read_text(encoding='utf-8-sig')
payload=[];names_found=[]
full_name=re.compile(r'\b(?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý)\s+[A-ZĐÀ-Ỹ][\wÀ-ỹ]+(?:\s+[A-ZĐÀ-Ỹ][\wÀ-ỹ]+){0,3}\s+(?:Nam|Giang|Linh)\b')
for rel,text in texts.items():
 if full_name.search(text):names_found.append(rel)
 if rel.endswith('.csv'):
  headers=next(csv.reader(io.StringIO(text)))
  if set(headers)&{'essay_text','full_text','first150_words','student_id','student_name','full_name'}:payload.append(rel)
assert not payload and not names_found
prior_scan=json.loads((A/'_kiem_tra/privacy_scan.json').read_text(encoding='utf-8'))
assert not prior_scan['payload_field_hits'] and not prior_scan['full_name_pattern_hits']
write(A/'_kiem_tra/toi_uu/privacy.json',json.dumps({'text_or_office_files_scanned':len(texts),'png_decoded':image_count,'forbidden_columns':payload,'member_full_name_pattern_hits':names_found,'note':'10-digit numeric essay_id was already directly confirmed in eligible development; remaining long numeric fragments include decimal predictions and hashes. No corpus opened. No OCR; raster pages/PNGs visually checked against saved source assets; heuristics do not prove arbitrary-name absence.'},ensure_ascii=False,indent=2))
write(A/'_kiem_tra/toi_uu/links.json',json.dumps({'HTML_links':html_count,'PDF_links':len(pdf_links),'source_Markdown_links':markdown_count,'broken':broken,'network':network},ensure_ascii=False,indent=2))
# Create placeholders before recording directory mtimes; only FILE_LIST and manifest are written last.
for name in ['BAO_CAO_KIEM_TRA.md','TREE.txt','FILE_LIST.md','MANIFEST.sha256']:
 if not (A/name).exists():write(A/name,'')
root_rows=[]
for name in expected:
 f=P/name;root_rows.append([name,str(f.stat().st_size) if f.is_file() else 'thư mục',stamp(f)])
report='''# Kiểm tra cuối gói một file mỗi mục
Gói chỉ đọc hồ sơ đã có; không mở Official Test/corpus, không in nội dung bài luận, không huấn luyện lại. Không xóa file có nội dung. Nhật ký di chuyển và hash trước/sau ở _kiem_tra/di_chuyen_toi_uu.json; chỉ rmdir sau khi kiểm tra thật sự rỗng.

## 1 Cấp cao nhất
Đúng 16 file từ 00 đến 15 và một thư mục _phu. Bộ 01 (8 trang), 03 và 10 giữ nguyên SHA-256 so với trước tối ưu.

| Tên | Kích thước byte | Giờ sửa Việt Nam |
|---|---:|---|
'''+''.join('| '+' | '.join(r)+' |\n' for r in root_rows)+'''
## 2 PDF và Office
'''+''.join(f'- {name}: {count} trang; đã render toàn bộ và kiểm tra trực quan tiếng Việt, bảng, biên trang.\n' for name,count in sorted(page_counts.items()))+'''
Tổng 24 trang PDF chính; file Word render kiểm tra bằng Word cài sẵn: 1 trang. Bộ render_docx.py đã thử nhưng máy không có LibreOffice; fallback Word native chỉ mở file DOCX mới ở chế độ read-only để xuất PDF. Cả 3 sheet Excel đã render bằng artifact-tool và xem lại. 05 có một sheet; 09 có đúng hai sheet. 05 đã nhận hai bản điền đầy đủ cho cùng 5 bài, mỗi người đủ 40 ô Phần A/B và 6 ô xác nhận; ghép ID bằng 6 số điểm thật/RF/Ridge do thứ tự bài khác nhau. Số đếm A/B được chép đúng nguồn mới; chỉ lưu alias/hash, không sao chép workbook chứa bài hay danh tính. Có nội dung tự xác nhận, chưa kiểm chứng quy trình. Ô giải thích/kết luận của 5 ca đã điền bằng tóm lược hai bản nộp theo yêu cầu mới, có tách ý A/B và tọa độ ô/hash nguồn ở 05_ca_loi/tom_luoc_nhan_xet_da_nop.json; không sao chép ví dụ trích bài. Năm dòng bổ sung và mọi ô trả lời đóng góp/AI vẫn trống. File Word chỉnh sửa được, các ô trả lời trống. Bản ghi nguồn mới ở 05_ca_loi/kiem_tra_hai_ban_da_nop.json; kết luận thiếu bản nộp trong hồ sơ cũ là trạng thái lịch sử, không phải trạng thái hiện tại.
Mục 02 đã sửa theo yêu cầu làm rõ: nghĩa tiếng Việt trong ngoặc và miền min–max theo định nghĩa của 14 đặc trưng thô, không dùng cực trị quan sát trong dữ liệu. Tỷ lệ có miền 0–1; số đếm và độ dài không có trần cố định; sentence_count tối thiểu 1 ở đầu vào hợp lệ. Zipf có sàn 0 và trần lý thuyết 9 theo log10(p)+9 với p<=1; thường gặp 0–8, không coi 8 là trần cứng. Nguồn và hash nguồn: 02_mau_truy_vet/nguon_mien_gia_tri.json; giai_nghia_va_mien_gia_tri.csv; docs/feature_specification.md và mã extractor/wordfreq. Hai trang 02 đã render và xem lại; không đổi số liệu bài, dự đoán, D hoặc thứ hạng. Các tệp max_development trước và PDF trước sửa được giữ làm lịch sử trong _phu, không phải miền giá trị hiện tại.

## 3 Liên kết
0 liên kết hỏng, 0 liên kết mạng trong mọi HTML và mọi annotation liên kết PDF. Các liên kết Markdown nguồn cũng được kiểm tra. Nguồn citation dạng tên file/commit là văn bản, không cần mạng. 00 có đường dẫn trực tiếp tới 01–15. Kết quả tĩnh ở _kiem_tra/toi_uu/links.json; không cần máy chủ.

## 4 Chạy BAT khi chặn mạng
'''+f"07_kiem_tra_offline.bat chạy thực tế bằng cmd.exe, return code 0, toàn tiến trình {bat['wall_seconds']:.3f} giây. Python audit hook từ chối socket/urllib/http và mọi đọc repository ngoài gói. Hai script cũ được giữ nguyên. D in 88/386; E=77.362908 (77.36), dòng nhắc 77,36; synthetic N=10, K=3, k=2, caught=1, E=0,6. BAT có pause; test cấp newline chỉ để đi qua pause. Stdout thực tế và PNG kết xuất stdout ở _kiem_tra/toi_uu/BAT_stdout.txt và BAT_stdout.png.\n"+'''
## 5 Riêng tư
Quét text/PDF/OOXML XLSX/DOCX, kiểm cột CSV và mẫu họ tên thành viên; không phát hiện payload bài luận, cột mã sinh viên hoặc họ tên đầy đủ. Essay_id số 10 chữ số đã được đối chiếu trực tiếp với development ở lượt trước; giữ nguyên. Không OCR PNG và không đối chiếu corpus; ảnh đã kiểm tra trực quan/nguồn tạo, không tuyên bố phương pháp regex chứng minh tuyệt đối mọi loại tên bất kỳ. Các nhãn Nam/Giang/Linh chỉ dùng nơi mẫu yêu cầu.

## 6 FILE_LIST và manifest
FILE_LIST được viết sau nội dung, MANIFEST được viết cuối cùng sau FILE_LIST. Mọi file trong cả gói được băm, trừ _phu/MANIFEST.sha256 không thể tự băm. FILE_LIST liệt kê đúng các mục manifest; TREE đầy đủ có kích thước. Hash manifest và số khớp/không khớp được in sau bước cuối, không ghi hash manifest vào file bên trong gây vòng tham chiếu.

## 7 Chưa có nguồn hoặc cần xác nhận
- MAE mean baseline cùng GroupKFold: chưa có nguồn.
- Mô hình từng fold OOF để phân rã chính xác từng dự đoán: chưa có nguồn được xác nhận; phân rã Phase 6 cũ được giữ riêng.
- Ngày truy cập Test đầu tiên: chưa xác định; tuần 9 là mốc báo cáo.
- Rubric gốc 26/10 và bản trả lời gốc của thầy, cách tính trang phụ lục: chưa có nguồn xác nhận.
- Đã nhận hai bản điền đủ và có lời tự xác nhận; còn chưa kiểm chứng trình tự đọc, lịch sử xem thông tin hay trao đổi. Không tiếp tục gọi hai bản mới là trống/chưa làm; bản B cũ là hồ sơ lịch sử riêng.
- Quyền hiển thị văn bản từng bài và nhật ký đóng góp/AI chi tiết: chưa rõ/chờ thành viên; gói không kèm văn bản bài.
- 15,0% và 16,6% đã có nguồn 35/233 và 36/217 trong báo cáo tuần 10, không còn là số thiếu nguồn.

Các script dựng cũ trong 08_tai_lap là hồ sơ lịch sử trước đổi bố cục. Cách chạy trực tiếp hiện tại là BAT; công cụ dựng/chốt bố cục mới ở _cong_cu. Không chạy các script lịch sử có fit hoặc đánh giá Test.
'''
write(A/'BAO_CAO_KIEM_TRA.md',report)
manifest=A/'MANIFEST.sha256';filelist=A/'FILE_LIST.md';tree=A/'TREE.txt'
files=sorted(f for f in P.rglob('*') if f.is_file() and f!=manifest)
listing='# Danh sách file khớp MANIFEST.sha256\n\nMỗi mục dưới có một hash trong manifest. Manifest không tự băm. Liên kết tính từ _phu.\n\n'+''.join(f'- [{f.relative_to(P).as_posix()}]({quote(os.path.relpath(f,A).replace(chr(92),chr(47)),safe="/._-")})\n' for f in files)
manifest_size=sum(len(('0'*64+'  '+f.relative_to(P).as_posix()+'\n').encode('utf-8')) for f in files)
# Fixed-width self-size fields make TREE stable without writing after manifest.
filelist_size=len(listing.encode('utf-8'))
for _ in range(10):
 entries=['interview_pack/ | byte; [MẪU TRỐNG] = ô trả lời chưa điền']
 for f in sorted(P.rglob('*')):
  if not f.is_file():continue
  size=manifest_size if f==manifest else filelist_size if f==filelist else f.stat().st_size
  flag=' [MẪU TRỐNG]' if f.name in ['09_dong_gop_va_ai.xlsx','15_review_tuan10_mau.docx','mau_10_ca.csv','mau_nhat_ky_dong_gop.csv','ba_hanh_dong.csv','moi_thanh_vien_mot_buoc.csv'] else ''
  entries.append(f'{f.relative_to(P).as_posix()} | {size:12d} bytes'+flag)
 value='\n'.join(entries)+'\n';old=tree.read_text(encoding='utf-8');write(tree,value)
 if value==old:break
else:raise RuntimeError('TREE did not stabilize')
write(filelist,listing)
latest_content=max(f.stat().st_mtime_ns for f in files if f!=filelist)
os.utime(filelist,ns=(time.time_ns(),max(time.time_ns(),latest_content+1_000_000)))
write(manifest,''.join(f'{sha(f)}  {f.relative_to(P).as_posix()}\n' for f in files))
assert manifest.stat().st_size==manifest_size
os.utime(manifest,ns=(time.time_ns(),max(time.time_ns(),filelist.stat().st_mtime_ns+1_000_000)))
checked={line.split('  ',1)[1]:line.split('  ',1)[0] for line in manifest.read_text(encoding='utf-8').splitlines()}
assert set(checked)=={f.relative_to(P).as_posix() for f in files}
assert all(sha(P/rel)==h for rel,h in checked.items())
assert filelist.stat().st_mtime_ns>latest_content and manifest.stat().st_mtime_ns>filelist.stat().st_mtime_ns
print(json.dumps({'root':root_rows,'pdf_pages':page_counts,'file_count_matched':len(checked),'file_count_mismatched':0,'manifest_sha256':sha(manifest),'FILE_LIST_second_last':True,'MANIFEST_last':True,'HTML_links':html_count,'PDF_links':len(pdf_links),'broken_links':broken,'network_links':network,'bat_seconds':bat['wall_seconds'],'retained_content_files':len(move['files']),'deleted_content_files':0,'deleted_empty_directories':move['deleted_directories_verified_empty']},ensure_ascii=False,indent=2))
