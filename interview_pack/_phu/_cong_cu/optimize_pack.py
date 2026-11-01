"""Author projection files from saved pack only; move, never delete populated files."""
from pathlib import Path
import csv,json,hashlib,html,io,os,re,sys,subprocess
from urllib.parse import urlsplit,unquote
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import fitz

sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[2];A=P/'_phu';QA=A/'_kiem_tra/toi_uu';QA.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
state=A/'_kiem_tra/di_chuyen_toi_uu.json'
if not state.exists() or not json.loads(state.read_text(encoding='utf-8')).get('complete',True):
 if state.exists():
  prior=json.loads(state.read_text(encoding='utf-8'));records=prior['files'];mapping={r['original']:r['current'] for r in records};original=[]
 else:original=[P/line.split('  ',1)[1] for line in (P/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines()]+[P/'MANIFEST.sha256']
 if original:mapping={};records=[]
 for f in original:
  rel=f.relative_to(P).as_posix()
  if rel in ['01_trinh_chieu.pdf','03_so_do_chia.pdf','10_so_tay_so_lieu.pdf']:dest=f
  elif rel=='00_START_HERE.html':dest=A/'00_START_HERE_truoc_toi_uu.html'
  elif rel=='MANIFEST.sha256':dest=A/'_kiem_tra/MANIFEST_truoc_toi_uu.sha256'
  elif rel=='FILE_LIST.md':dest=A/'_kiem_tra/FILE_LIST_truoc_toi_uu.md'
  else:dest=A/rel
  mapping[rel]=dest.relative_to(P).as_posix()
  actual=f if f.exists() else dest if dest.exists() else A/rel
  records.append({'original':rel,'current':mapping[rel],'sha256_before':sha(actual)})
 # Verify all moves remain inside pack and none overwrite existing contents.
 removed=[];pending=[]
 write(state,json.dumps({'files':records,'complete':False},ensure_ascii=False,indent=2))
 for r in records:
  old=P/r['original'];dest=P/r['current']
  if old==dest or dest.exists():continue
  assert old.is_file() and dest.is_relative_to(P) and not dest.exists()
  dest.parent.mkdir(parents=True,exist_ok=True)
  try:old.rename(dest)
  except PermissionError:pending.append(r['original'])
 for directory in sorted([d for d in P.rglob('*') if d.is_dir() and not d.is_relative_to(A)],key=lambda d:len(d.parts),reverse=True):
  assert directory.is_relative_to(P) and directory!=P
  if not any(directory.iterdir()):removed.append(directory.relative_to(P).as_posix());directory.rmdir()
 assert all(sha(P/r['current'])==r.get('sha256_after_move',r['sha256_before']) for r in records if r['original'] not in pending)
 # Repair relative navigation in retained source docs, using original locations.
 for r in records:
  f=P/r['current']
  if not f.exists():continue
  if f.suffix not in ['.md','.html']:continue
  text=f.read_text(encoding='utf-8-sig')
  oldparent=Path(r['original']).parent
  def newurl(url):
   parts=urlsplit(url.strip('<>'))
   if parts.scheme or parts.netloc or not parts.path:return url
   original_target=os.path.normpath(str(oldparent/unquote(parts.path))).replace('\\','/')
   target=P/mapping.get(original_target,original_target)
   if not target.exists():return url
   result=os.path.relpath(target,f.parent).replace('\\','/')
   return result+('#'+parts.fragment if parts.fragment else '')
  if f.suffix=='.md':updated=re.sub(r'(\[[^\]]*\]\()([^)]+)(\))',lambda m:m[1]+newurl(m[2])+m[3],text)
  else:updated=re.sub(r'((?:href|src)=")([^"]+)(")',lambda m:m[1]+newurl(m[2])+m[3],text)
  if updated!=text:write(f,updated);r['navigation_updated']=True
  r['sha256_after_move']=sha(f)
 write(state,json.dumps({'files':records,'complete':not pending,'pending_locked':pending,'deleted_files':[],'deleted_directories_verified_empty':removed,'note':'All content files retained; only relative links in source MD/HTML updated.'},ensure_ascii=False,indent=2))
def csvrows(rel):
 path=A/rel if (A/rel).exists() else P/rel
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')
W,H=1200,850;NAVY=colors.HexColor('#17334b');TEAL=colors.HexColor('#087e8b');GRAY=colors.HexColor('#edf0f2')
def para(c,s,x,y,w,size=20):
 st=ParagraphStyle('p',fontName='Arial',fontSize=size,leading=size*1.29,textColor=NAVY)
 p=Paragraph(s,st);_,h=p.wrap(w,2000);assert y-h>=15,(s[:50],y-h);p.drawOn(c,x,y-h);return y-h
def header(c,title,sub='NHÓM 03 · ELLIPSE · HỒ SƠ SỐ LIỆU ĐÃ LƯU'):
 c.setFillColor(colors.white);c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(TEAL);c.rect(0,H-10,W,10,fill=1,stroke=0)
 para(c,sub,40,H-29,W-80,13);para(c,title,40,H-61,W-80,30)
def table(c,data,widths,y,x=40,size=17,pad=7):
 st=ParagraphStyle('cell',fontName='Arial',fontSize=size,leading=size*1.25,textColor=NAVY)
 t=Table([[Paragraph(html.escape(str(v)).replace('\n','<br/>'),st) for v in r] for r in data],colWidths=widths)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GRAY),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d4e1e7')),('INNERGRID',(0,0),(-1,-1),1,colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad)]))
 _,h=t.wrap(sum(widths),2000);assert y-h>35,(h,y);t.drawOn(c,x,y-h);return y-h
def foot(c,s):para(c,s,40,62,W-80,12)
def newpdf(name,pages):
 c=canvas.Canvas(str(P/name),pagesize=(W,H))
 for draw in pages:draw(c);c.showPage()
 c.save()
IDS=['684166ED2438','0514D25768A0'];samples={i:csvrows(f'02_mau_truy_vet/{i}.csv')[0] for i in IDS}
features=list(samples[IDS[0]])[1:15]
counts={r['essay_id']:r for r in csvrows('08_tai_lap/nguon/gec_part_a_68.csv')}
def sample_page(essay,walk=False):
 z=samples[essay]
 def draw(c):
  header(c,('Năm bước đi qua bài ' if walk else 'Đặc trưng → dự đoán → nhãn · ')+essay)
  para(c,('1. Xác nhận nhãn' if walk else 'Nhãn và phạm vi đánh giá')+f": V/G = {z['y_V']} / {z['y_G']}; V &lt; 2,5; thuộc 276/386 ca RF–Ridge cùng sai lớn.",40,735,1120,21)
  para(c,'Nguồn: reports/week9/t3_heldout_predictions.csv, prompt_disjoint; t3_pooled.csv / A3.',40,696,1120,12)
  data=[['Đặc trưng','Giá trị','Đặc trưng','Giá trị']]
  for j in range(7):data.append([features[j],f'{float(z[features[j]]):.6g}',features[j+7],f'{float(z[features[j+7]]):.6g}'])
  para(c,'2. Mười bốn đặc trưng' if walk else 'Một hàng dữ liệu development',40,666,1120,22)
  y=table(c,data,[415,145,415,145],630,size=15,pad=4)
  para(c,'Nguồn 14 giá trị: reports/week9/t3_eligible_development.csv, đúng essay_id; thứ tự theo feature_schema.json.',40,y-12,1120,12)
  if essay in counts:
   h=counts[essay];t=f"Đếm lỗi / 150 từ đầu: người {float(h['reader']):g}; công cụ cũ ước lượng {float(h['LT_estimate']):.2f}; GECToR {h['edits_grammar']} chỉnh sửa."
  else:t='Đếm lỗi: chưa có người đếm; công cụ cũ 0 cảnh báo/100 từ; GECToR chưa có dữ liệu.'
  para(c,t,40,y-42,1120,18)
  para(c,'Nguồn: reports/week10/gec_part_a_68.csv; phiếu docs/phieu_luyen_* tương ứng. Không coi ước lượng là đếm trực tiếp.',40,y-71,1120,12)
  y=y-108
  data=[['Dự đoán giữ lại','Từ vựng','Ngữ pháp','Nguồn'],['RF',z['RF_V'][:12],z['RF_G'][:12],'W9/t3_heldout_predictions.csv'],['Ridge',z['Ridge_V'][:12],z['Ridge_G'][:12],'W9/t3_heldout_predictions.csv'],['MiniLM + Ridge',z['MiniLM_V'][:12],z['MiniLM_G'][:12],'W10/b2_oof.csv']]
  para(c,'3. RF và Ridge · 4. MiniLM' if walk else 'Dự đoán OOF trên cùng bài',40,y,1120,22)
  y=table(c,data,[280,200,200,440],y-32,size=17,pad=3)
  para(c,f"D = {float(z['D']):.9f}; hạng {z['D_rank']}/{z['fold_n']}; đọc {z['budget']} bài đầu (20%). Không được D chọn.",40,y-12,1120,20)
  para(c,'Nguồn D/hạng/ngưỡng: t3_heldout_predictions.csv; D giảm dần, hòa essay_id chuỗi tăng dần. Đây không phải phân rã mô hình Phase 6.',40,y-44,1120,12)
  if walk:para(c,'5. Kiểm tra trực tiếp: mở 07_kiem_tra_offline.bat → 88/386, kỳ vọng 77,362908 ≈ 77,36; không mô hình, không mạng.',40,y-70,1120,19)
  else:para(c,'Hai dự đoán V gần 2,9 (2,8–3,0).' if essay==IDS[0] else 'RF và Ridge cùng sai lớn ở V dù D nhỏ; không suy luận nguyên nhân thay người đọc.',40,y-70,1120,19)
  foot(c,'W9 = reports/week9; W10 = reports/week10. Số điểm, đặc trưng và dự đoán chỉ trích hồ sơ đã lưu; không có văn bản bài luận. Sai lớn: max sai số tuyệt đối V/G ≥ 1.')
 return draw
newpdf('02_mau_truy_vet.pdf',[sample_page(i) for i in IDS])
feature_overlay=A/'_cong_cu/update_trace_vietnamese.py'
if feature_overlay.exists():subprocess.run([sys.executable,str(feature_overlay)],check=True)
newpdf('14_luot_di_qua.pdf',[sample_page(i,True) for i in IDS])
main=csvrows('04_bang_ket_qua/bang_chinh.csv');models=csvrows('04_bang_ket_qua/bang_mo_hinh.csv')
def result_page(c):
 header(c,'Kết quả chính và baseline mô hình')
 dat=[['Tập / tín hiệu','N','K','Đọc k','Bắt C/K','Ngẫu nhiên','Nguồn từng dòng']]
 sources=['W9/t3_pooled.csv A1','W9/t3_pooled.csv A3','W9/RESULTS_week9.md Week9b','W9/RESULTS_week9.md Task0','W9/tree_spread_official_test_second_use_log_attempt2.json / result']
 for r,s in zip(main,sources):dat.append([r['scope'],r['N'],r['K'],r['budget'],r['caught']+'/'+r['K'],f"{float(r['random']):.2f}",s])
 y=table(c,dat,[240,75,75,85,110,130,405],730,size=17,pad=7)
 para(c,'K là số ca sai lớn; k = ceil(0,20N) từng fold. Phá hòa: essay_id chuỗi tăng dần. Tỷ lệ nền: Dev RF 10,13%; nhóm cùng sai 7,24%; Test 8,26% (nguồn cùng từng dòng).',40,y-14,1120,18)
 para(c,'Baseline và hai họ mô hình · MAE V / G',40,y-82,1120,22)
 modeldata=[['Mô hình','MAE V / G','Giả định / loss huấn luyện','Nguồn từng dòng']]
 for m in models:
  val='chưa có nguồn' if not m['MAE_V'] else f"{float(m['MAE_V']):.3f} / {float(m['MAE_G']):.3f}"
  modeldata.append([m['model'],val,m['assumption']+'; '+m['training_loss'],'W9/t3_regression.csv prompt_disjoint, pooled' if m['MAE_V'] else 'Chưa có nguồn MAE cùng phép chia'])
 y=table(c,modeldata,[160,200,480,280],y-118,size=16,pad=7)
 para(c,'Cây − D trên development: +8 [−11; 27]; bootstrap theo 44 cụm đề, 2.000 lượt seed 42, giữ hàng đợi. Nguồn: W9/RESULTS_week9.md / paired tree spread. Chưa chứng minh hơn D.',40,y-18,1120,18)
 foot(c,'W9 = reports/week9. Test chỉ dùng số tổng hợp đã lưu; Test lần hai là thăm dò. TF-IDF/MiniLM là nguồn đối chiếu, bảng riêng ở 12_mang_theo.pdf. Bản dữ liệu và nguồn đầy đủ trong _phu.')
newpdf('04_bang_ket_qua.pdf',[result_page])
LOCK='d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca';SCRIPT='cc7bdd6efd8c0cf23a4f6dbd5673e17a5c8501aaf72e77fb0b99e96090b31e05'
assert sha(A/'12_mang_theo/signal_lock_tree_spread.md')==LOCK
def history(c):
 header(c,'Lịch sử dùng Test · kết quả đã lưu')
 data=[['Mốc UTC','Sự kiện / kết quả','Nguồn'],['Lần 1: báo cáo tuần 9; ngày chạy đầu chưa xác định','D 47/208; ngẫu nhiên 41,63; exact p 0,1883','RESULTS_week9.md / Task0'],['19/10/2026 05:41:08','Khóa tín hiệu; commit 4e38115','RESULTS_tree_spread_second_use.md; Git commit khóa'],['26/10/2026 07:14:53','Dừng: dự đoán lệch dung sai 1e-12; chưa tính tín hiệu','Log STOPPED; commit b32ad4e3'],['Sau sửa dung sai; chưa có giờ riêng','Từ chối do log tồn tại; không mở Test ở lần gọi này','RESULTS_tree_spread_second_use.md / Sự cố chốt chặn'],['26/10/2026 07:27:32','Hoàn thành: 55/208; E=41,63; p=0,0116 so ngẫu nhiên','Log _attempt2 COMPLETED; run cdc0a6a8; result 97159a6b']]
 y=table(c,data,[285,455,380],730,size=18,pad=9)
 para(c,'SHA-256 khóa · docs/signal_lock_tree_spread.md',40,y-20,1120,17);para(c,LOCK,40,y-48,1120,16)
 para(c,'SHA-256 script · scripts/tree_spread_official_test_second_use.py',40,y-84,1120,17);para(c,SCRIPT,40,y-111,1120,16)
 para(c,'Kết quả sau nhiều lần chọn là thăm dò. Lần hai dùng RF đã lưu từ tuần 9, chỉ tín hiệu khóa; không phải xác nhận độc lập sạch. Chênh 55−47=8 không phải kiểm định hơn D.',40,y-160,1120,21)
 foot(c,'Nguồn (reports/week9): RESULTS_week9.md; RESULTS_tree_spread_second_use.md; tree_spread_official_test_second_use_log.json; tree_spread_official_test_second_use_log_attempt2.json. Không mở Test.')
newpdf('06_lich_su_dung_test.pdf',[history])
def reproduce1(c):
 header(c,'Tái lập · kiểm tra offline từ dự đoán đã lưu')
 items=[('Cách kiểm tra khi phỏng vấn','Nhấp đúp 07_kiem_tra_offline.bat. Hai script trong _phu/07_kiem_tra_offline dùng thư viện chuẩn Python; có chặn socket và đọc repository ngoài gói.'),('Đầu ra cần đối chiếu','D bắt 88/386; ngân sách 764; kỳ vọng 77,362908 ≈ 77,36. Synthetic: N=10, K=3, k=2, bắt 1; E=0,6.'),('Lệnh hiện tại','python _phu/07_kiem_tra_offline/check_d_88_of_386.py<br/>python _phu/07_kiem_tra_offline/check_synthetic_ranking.py'),('Dự đoán và fold','Gốc: reports/week9/t3_heldout_predictions.csv / prompt_disjoint.<br/>Fold: reports/week9/t3_fold_composition.csv.<br/>Bản số kèm: _phu/07_kiem_tra_offline/development_predictions.csv; fold ở _phu/08_tai_lap/nguon/t3_fold_composition.csv.'),('Phiên bản ghi trong hồ sơ','Python 3.14.5; scikit-learn 1.9.1; NumPy 2.4.6; joblib 1.6.0; seed cấu hình 42. Đây là môi trường mô hình đã lưu, không bắt buộc để chỉ xem PDF hoặc chạy kiểm tra CSV.')]
 y=730
 for title,body in items:y=para(c,title,40,y,1120,23)-8;y=para(c,body,48,y,1104,20)-24
 foot(c,'Nguồn: _phu/08_tai_lap/REPRODUCE.md; reports/week9/RESULTS_tree_spread_second_use.md / phiên bản; hai script standard library đã có. BAT không huấn luyện, không chạy Test.')
def reproduce2(c):
 header(c,'Tái lập · hồ sơ tạo bảng và phạm vi nguồn')
 data=[['Bảng / nguồn','Lệnh lịch sử để truy xuất, KHÔNG chạy ở phỏng vấn'],['D và baseline','scripts/week9/t3_evaluate.py --capture; nguồn RESULTS_week9.md / Task3'],['Cây 96/386','scripts/week9b/tree_spread_oof.py --append; có fit fold; ngoài phạm vi lần dựng gói này'],['Khoảng ghép cặp','scripts/week9b/paired_tree_spread.py --append; 44 cụm đề, 2000 lượt, seed 42; giữ hàng đợi'],['Test 47/208 và 55/208','Chỉ trích RESULTS và log tổng hợp. Không cần đầu vào Test để xem hoặc kiểm tra gói.']]
 y=table(c,data,[275,845],730,size=21,pad=12)
 para(c,'File cần có khi dựng lại tài liệu',40,y-24,1120,24)
 para(c,'CSV development predictions, hai CSV kết quả chính/mô hình, hai CSV truy vết mẫu, CSV gec_part_a_68, fold composition, các trích báo cáo và file khóa đầy đủ. Tất cả bản kèm nằm trong _phu; danh sách chuẩn ở _phu/FILE_LIST.md.',40,y-64,1120,21)
 para(c,'Mô hình chỉ cần cho phép phân rã riêng đã lưu; không cần để chiếu, không cần để tính lại 88/386. Các script dựng cũ được giữ làm hồ sơ lịch sử, không phải lệnh chạy trực tiếp của bố cục mới.',40,y-172,1120,21)
 foot(c,'Nguồn: _phu/08_tai_lap/REPRODUCE.md; reports/week9/RESULTS_week9.md / Producer của từng phép phân tích. Chưa có mô hình OOF từng fold được xác nhận để phân rã đúng từng dự đoán.')
newpdf('08_tai_lap.pdf',[reproduce1,reproduce2])
def imagepage(rel):
 def draw(c):
  im=__import__('PIL.Image',fromlist=['Image']).open(A/rel);iw,ih=im.size;scale=min(W/iw,H/ih)
  c.drawImage(str(A/rel),(W-iw*scale)/2,(H-ih*scale)/2,width=iw*scale,height=ih*scale)
 return draw
def historydraft(c):
 header(c,'Câu lịch sử Test · NHÁP để tự viết lại')
 para(c,'Ngày thầy cho phép: ____________________',40,716,1120,26)
 body='Test đã dùng ở lần đánh giá được báo cáo tuần 9 (47/208, kỳ vọng 41,63; ngày truy cập đầu chưa xác định); lần hai thầy cho phép ngày __________, chỉ cho tín hiệu đã khóa (commit 4e38115, SHA-256 d2eabcb7…8eca), dùng lại RF đã lưu từ tuần 9, không thử tín hiệu khác; kết quả 55/208, kỳ vọng 41,63, p 0,0116 so ngẫu nhiên; đây là lần dùng thứ hai nên không phải xác nhận độc lập sạch.'
 para(c,body,48,630,1104,28)
 para(c,'Đây chỉ là một câu nháp theo yêu cầu. Thành viên tự xác nhận ngày và viết lại bằng lời của mình; không phải lời khai đã hoàn tất.',48,334,1104,23)
 foot(c,'Nguồn: reports/week9/RESULTS_week9.md / Task0; RESULTS_tree_spread_second_use.md; tree_spread_official_test_second_use_log_attempt2.json / result; docs/signal_lock_tree_spread.md. Ngày cố ý để trống.')
newpdf('11_ba_cau_giai_thich.pdf',[imagepage('11_ba_cau_giai_thich/nen_ve_giua.png'),imagepage('11_ba_cau_giai_thich/dung_chung_dac_trung.png'),historydraft])
def lockpage(c):
 header(c,'Khóa tín hiệu · định nghĩa và mã băm')
 para(c,'Tín hiệu chính đã khóa',40,730,1120,25)
 para(c,'Với mỗi bài, lấy độ lệch chuẩn tổng thể (ddof=0) của dự đoán 300 cây RF cho từng đích V và G; tín hiệu = max(std_V, std_G). Xếp giảm dần, hòa essay_id chuỗi tăng dần. Ngân sách đọc k = ceil(0,20N) từng fold hoặc tập đánh giá độc lập.',48,682,1104,23)
 para(c,'Giữ RF và tiền xử lý đã khóa; sai lớn = max(|y_V−RF_V|, |y_G−RF_G|) ≥ 1. Không thử tín hiệu khác trên Test trong lần dùng thứ hai.',48,546,1104,23)
 table(c,[['Kiểm tra file khóa','Kết quả'],['File gốc','docs/signal_lock_tree_spread.md'],['Bản đầy đủ mang theo','_phu/12_mang_theo/signal_lock_tree_spread.md'],['SHA-256 hiện tính',sha(A/'12_mang_theo/signal_lock_tree_spread.md')],['SHA-256 kỳ vọng',LOCK],['So sánh','KHỚP · commit khóa 4e381150edf08d49a134505e669058f1e0d27b48']],[280,840],439,size=18,pad=10)
 foot(c,'Nguồn: đoạn Signal definition của file khóa nguyên bản; hash tính trực tiếp trên bản kèm. Dòng “Test not used” trong bản khóa là trạng thái lịch sử lúc viết, không phủ nhận lịch sử Test lần hai đã báo cáo.')
newpdf('12_mang_theo.pdf',[imagepage('12_mang_theo/bang_3_4.png'),lockpage])
def outline(c):
 header(c,'Đề cương báo cáo cuối · không fine-tune encoder')
 data=[['Phần','Trọng tâm','Ánh xạ cấu trúc 6–8 trang'],['(1) So cách đọc ưu tiên','D so ngẫu nhiên, Ridge extremity và bài ngắn nhất; cùng nhãn, ngân sách, phá hòa.','Giới thiệu; Dữ liệu/Phương pháp; Thiết lập; Kết quả'],['(2) Nguồn thông tin','Gộp Ridge, TF-IDF, MiniLM vào một bảng; cùng sai, bắt lỗi, kỳ vọng và nhóm 276.','Phương pháp; Thiết lập; một bảng Kết quả'],['(3) Mọi mô hình cùng sai','Trọng tâm phân tích lỗi: công khai quy tắc chọn; người đọc tự điền nhận xét đã xác nhận. Không coi nhóm 191 là giao cả bốn mô hình.','Kết quả/Phân tích lỗi; Thảo luận/Kết luận'],['(4) Nghiên cứu cùng dữ liệu','Một đoạn ngắn về ELLIPSE; chỉ so số khi nhiệm vụ, nhãn, split tương thích.','Giới thiệu hoặc Thảo luận; Tham khảo']]
 y=table(c,data,[215,560,345],730,size=21,pad=12)
 para(c,'Đưa GECToR, bảng phụ theo fold/vùng điểm, chi tiết CI, lịch sử Test, hash và lệnh tái lập xuống phụ lục.',40,y-22,1120,23)
 para(c,'Chỉ là đề cương; không viết nội dung báo cáo thay nhóm. Khung 6–8 trang theo chỉ dẫn người dùng thuật lại lời thầy; bản trả lời gốc và cách tính trang phụ lục: chưa có nguồn xác nhận.',40,y-105,1120,21)
 foot(c,'Nguồn định hướng: yêu cầu bổ sung của người dùng; bản nguồn _phu/13_cau_truc_bao_cao_cuoi.md. Bằng chứng số: reports/week9/t3_pooled.csv; reports/week10/RESULTS_week10.md. Không có thí nghiệm mới.')
newpdf('13_cau_truc_bao_cao_cuoi.pdf',[outline])
# Data only for the artifact-tool workbook builder.
write(A/'_cong_cu/workbook_input.json',json.dumps({'cases':csvrows('05_ca_loi/5_ca_cho_hai_ban.csv')},ensure_ascii=False,indent=2))
titles=['Mở gói và chọn câu hỏi','8 slide tổng quan','Một hàng dữ liệu và dự đoán','Chia dữ liệu và tiền xử lý','Kết quả so baseline','Ca lỗi và ô thành viên tự điền','Lịch sử Test','Chạy kiểm tra offline','Tái lập từ hồ sơ','Đóng góp và AI mẫu trống','Sổ tay số liệu','Ba câu gợi ý tự giải thích','Bảng 3.4 và khóa tín hiệu','Đề cương báo cáo cuối','Năm bước đi qua hai bài','Review tuần 10 mẫu trống']
names=['00_START_HERE.html','01_trinh_chieu.pdf','02_mau_truy_vet.pdf','03_so_do_chia.pdf','04_bang_ket_qua.pdf','05_ca_loi.xlsx','06_lich_su_dung_test.pdf','07_kiem_tra_offline.bat','08_tai_lap.pdf','09_dong_gop_va_ai.xlsx','10_so_tay_so_lieu.pdf','11_ba_cau_giai_thich.pdf','12_mang_theo.pdf','13_cau_truc_bao_cao_cuoi.pdf','14_luot_di_qua.pdf','15_review_tuan10_mau.docx']
write(A/'_cong_cu/expected_root.json',json.dumps(names+['_phu'],ensure_ascii=False,indent=2))
index='<!doctype html><html lang="vi"><meta charset="utf-8"><title>Nhóm 03 · Gói phỏng vấn</title><style>body{font:19px Arial,sans-serif;max-width:1150px;margin:30px auto;color:#17334b}table{border-collapse:collapse;width:100%}td,th{background:#edf0f2;border:3px solid white;padding:13px;text-align:left}a{color:#087e8b}p{line-height:1.5}</style><h1>Nhóm 03 · ELLIPSE</h1><p>Mỗi mục một file để mở. Tất cả nội dung hoạt động offline; BAT cần Python đã cài.</p><p>Thứ tự gợi ý: 01 → 03 → 04 → 02 → 05 → 11 → 12. Khi hỏi kiểm tra trực tiếp: 07. Các mẫu đóng góp/review: 09 và 15.</p><table><tr><th>Thầy hỏi gì?</th><th>Bấm file nào?</th></tr>'
index+=''.join(f'<tr><td>{html.escape(t)}</td><td><a href="{n}">{n}</a></td></tr>' for n,t in zip(names[1:],titles[1:]))
index+='</table><p>Giữ một bảng và một ca: mở 04 và 02 (bài 0514D25768A0). Thành viên tự giải thích, không đọc thay lời viết sẵn.</p><p>Tài liệu phụ: <a href="_phu/FILE_LIST.md">danh sách file</a> · <a href="_phu/TREE.txt">cây và kích thước</a> · <a href="_phu/BAO_CAO_KIEM_TRA.md">kiểm tra cuối</a>. Kết quả Test dùng lại là thăm dò. Không có văn bản bài luận trong gói.</p></html>'
write(P/'00_START_HERE.html',index)
# Render every current main PDF and retain all QA images.
pdfinfo=[]
for f in sorted(P.glob('*.pdf')):
 with fitz.open(f) as d:
  pdfinfo.append({'file':f.name,'pages':len(d)})
  for j,page in enumerate(d):
   page.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(QA/f'{f.stem}_page{j+1:02}.png')
write(QA/'pdf_pages.json',json.dumps(pdfinfo,ensure_ascii=False,indent=2))
print(json.dumps({'root_pdfs':pdfinfo,'retained_01_03_10':all(sha(P/r['current'])==r['sha256_before'] for r in json.loads(state.read_text(encoding='utf-8'))['files'] if r['current'] in ['01_trinh_chieu.pdf','03_so_do_chia.pdf','10_so_tay_so_lieu.pdf'])},ensure_ascii=False,indent=2))
