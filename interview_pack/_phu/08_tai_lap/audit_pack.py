"""Read only pack contents, deny network in offline checks, then seal manifest last.
Does not read repository Test, corpus, models or source writing.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import csv, hashlib, io, json, os, re, subprocess, sys, time
from datetime import datetime, timezone, timedelta
import fitz
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[1]
OUT=P/'_kiem_tra';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,s): (OUT/name).write_text(s,encoding='utf-8')
def inventory():return sorted(p for p in P.rglob('*') if p.is_file())
def manifest_rows():
 rows={}
 for line in (P/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
  h,r=line.split('  ',1);assert r not in rows;rows[r]=h
 return rows
old=manifest_rows()
initial={'entries':len(old),'matched':0,'mismatched':[],'missing':[]}
for rel,h in old.items():
 f=P/rel
 if not f.is_file():initial['missing'].append(rel)
 elif sha(f)==h:initial['matched']+=1
 else:initial['mismatched'].append(rel)
# Every script output is captured; the runner refuses sockets and repository reads outside pack.
runner=r'''import sys, pathlib, runpy
sys.dont_write_bytecode=True
pack=pathlib.Path(sys.argv[1]).resolve(); script=pathlib.Path(sys.argv[2]).resolve()
def guard(event,args):
 if event.startswith(('socket.','urllib.','http.client.')):
  raise RuntimeError('NETWORK_BLOCKED')
 if event=='open' and isinstance(args[0],(str,bytes)):
  p=pathlib.Path(args[0]).resolve()
  if p.is_relative_to(pack.parent) and not p.is_relative_to(pack):
   raise RuntimeError('OUTSIDE_PACK_READ_BLOCKED')
sys.addaudithook(guard)
sys.argv=[str(script)];runpy.run_path(str(script),run_name='__main__')
'''
runs=[]
for name in ['check_d_88_of_386.py','check_synthetic_ranking.py']:
 begin=time.perf_counter()
 res=subprocess.run([sys.executable,'-I','-c',runner,str(P),str(P/'07_kiem_tra_offline'/name)],capture_output=True,text=True,encoding='utf-8',timeout=10)
 elapsed=time.perf_counter()-begin
 assert res.returncode==0,(name,res.stderr)
 assert elapsed<10
 if name.startswith('check_d_'):assert 'caught=88/386' in res.stdout and '77.362908 (77.36)' in res.stdout
 else:assert 'expected_random=k*K/N=2*3/10=0.6' in res.stdout
 put(name.replace('.py','_audit_stdout.txt'),res.stdout)
 runs.append({'script':name,'wall_seconds':round(elapsed,6),'exit_code':res.returncode,'network':'denied by audit hook','repo_reads_outside_pack':'denied by audit hook'})

class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=set();self.unsupported=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:self.ids.add(attrs['id'])
  for key in ['href','src','action','poster','data','srcset']:
   if key in attrs:self.refs.append((tag,key,attrs[key]))
  if tag=='script':self.unsupported.append('script element')
index=(P/'00_START_HERE.html').read_text(encoding='utf-8')
parser=Links();parser.feed(index);link_results=[]
for tag,key,url in parser.refs:
 parts=urlsplit(url);status='OK';target=None
 if parts.scheme or parts.netloc or url.startswith('//'):status='EXTERNAL_OR_ABSOLUTE'
 else:
  target=(P/unquote(parts.path)).resolve()
  if not target.is_relative_to(P):status='OUTSIDE_PACK'
  elif not target.exists():status='BROKEN'
  elif parts.fragment.startswith('page='):
   if target.suffix.lower()!='.pdf':status='BAD_FRAGMENT'
   else:
    with fitz.open(target) as d:
     if not 1<=int(parts.fragment[5:])<=len(d):status='BAD_PAGE'
 link_results.append({'url':url,'status':status,'target_kind':'directory' if target and target.is_dir() else 'file'})
css_dependencies=re.findall(r'url\s*\([^)]*\)|@import\b',index,re.I)
assert not css_dependencies and not parser.unsupported
assert all(x['status']=='OK' for x in link_results),link_results
assert all(any(x['url'].startswith(prefix) for x in link_results) for prefix in ['11_ba_cau_giai_thich/','12_mang_theo/','13_cau_truc_bao_cao_cuoi.md','14_luot_di_qua/','15_review_tuan10_mau/'])
# CSVs with blank answer cells are identified by contents, not size.
templates={};zero=[];csv_shapes=[];texts={};pngs=[];unknown=[]
for f in inventory():
 rel=f.relative_to(P).as_posix()
 if rel.startswith('_kiem_tra/') and not rel.startswith('_kiem_tra/hien_thi/'):continue
 if f.stat().st_size==0:zero.append(rel)
 if f.suffix.lower()=='.csv':
  raw=f.read_text(encoding='utf-8-sig');rd=csv.DictReader(io.StringIO(raw));rs=list(rd)
  csv_shapes.append({'file':rel,'rows':len(rs),'columns':rd.fieldnames})
  if not rs:templates[rel]='MẪU TRỐNG: chỉ có tiêu đề cột'
  elif all(all(v in ['',None] for v in r.values()) for r in rs):templates[rel]=f'MẪU TRỐNG: {len(rs)} dòng, mọi ô trả lời trống'
 if f.suffix.lower()=='.pdf':
  with fitz.open(f) as d:texts[rel]='\n'.join(p.get_text() for p in d)
 elif f.suffix.lower()=='.png':
  with Image.open(f) as im:im.verify()
  pngs.append({'file':rel,'matches_prior_manifest':old.get(rel)==sha(f)})
 elif f.suffix.lower() in ['.md','.txt','.csv','.json','.py','.html','.sha256']:
  texts[rel]=f.read_text(encoding='utf-8-sig')
 else:unknown.append(rel)
for rel in ['09_dong_gop_va_ai/Nam/README.md','09_dong_gop_va_ai/Giang/README.md','09_dong_gop_va_ai/Linh/README.md','09_dong_gop_va_ai/khai_bao_ai.md','15_review_tuan10_mau/README.md']:
 templates[rel]='MẪU TRỐNG / hướng dẫn, không có lời khai đã điền'
partial=['11_ba_cau_giai_thich/cau_lich_su_dung_test.md','05_ca_loi/5_ca_cho_hai_ban.csv']
digit_locations=[];digit_summary=Counter();name_hits=[];payload_hits=[];english_candidates=[]
for rel,s in texts.items():
 for n,line in enumerate(s.splitlines(),1):
  for m in re.finditer(r'(?<!\d)\d{10}(?!\d)',line):
   left=line[:m.start()];right=line[m.end():]
   token=re.search(r'[A-Za-z0-9_.+-]*$',left).group()+m.group()+re.match(r'[A-Za-z0-9_.+-]*',right).group()
   if re.fullmatch(r'[A-Fa-f0-9]{32,}',token):kind='hash_or_commit'
   elif re.fullmatch(r'[A-Fa-f0-9]{12}',token):kind='essay_id_hex'
   elif rel.endswith('.csv') and n>1 and s.splitlines()[0].split(',')[0]=='essay_id' and line.split(',')[0]==m.group():kind='essay_id_numeric_10'
   elif re.search(r'\d+[.,]$',left):kind='decimal_value'
   elif re.fullmatch(r'[+-]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?',token):kind='decimal_value'
   else:kind='REVIEW_REQUIRED'
   digit_summary[kind]+=1
   digit_locations.append({'file':rel,'line':n,'kind':kind})
  if re.search(r'\b(?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý)\s+[A-ZĐÀ-Ỹ][\wÀ-ỹ]+(?:\s+[A-ZĐÀ-Ỹ][\wÀ-ỹ]+){0,3}\s+(?:Nam|Giang|Linh)\b',line):name_hits.append({'file':rel,'line':n,'kind':'member_full_name_pattern'})
  # Only flag stored payload fields, not documentation saying these fields are forbidden.
  if rel!='08_tai_lap/audit_pack.py' and (f'"full_text":' in line or f'"essay_text":' in line or f'"first150_words":' in line):payload_hits.append({'file':rel,'line':n})
 # Long English prose is reported by location only, never printed.
 for i,paragraph in enumerate(s.split('\n\n'),1):
  if rel!='08_tai_lap/audit_pack.py' and len(re.findall(r'\b[A-Za-z]+\b',paragraph))>130 and re.search(r'\b(?:I think|in my opinion|my school|students should|I believe)\b',paragraph,re.I):english_candidates.append({'file':rel,'paragraph':i})
for shape in csv_shapes:
 if set(shape['columns'])&{'essay_text','full_text','first150_words','student_id','student_name','full_name'}:payload_hits.append({'file':shape['file'],'line':1,'kind':'payload_or_personal_column'})
privacy={'text_files_and_pdfs_scanned':len(texts),'png_files_decoded':len(pngs),'png_hashes_matching_prior_manifest':sum(x['matches_prior_manifest'] for x in pngs),'raw_10_digit_runs_by_context':dict(digit_summary),'ten_digit_locations_no_values':digit_locations,'full_name_pattern_hits':name_hits,'payload_field_hits':payload_hits,'long_english_prose_candidates':english_candidates,'unknown_formats':unknown,'limitations':['No corpus/text fingerprint comparison performed because Test/corpus access is prohibited.','No OCR engine available; PNGs decoded and checked against prior manifest/visual QA.','Only first-name labels Nam/Giang/Linh were supplied; arbitrary full names cannot be exhaustively identified without a reference list.','Regex matches are candidates, not proof of student IDs. Numeric decimal/hash/essay-ID matches are classified separately.']}
put('privacy_scan.json',json.dumps(privacy,ensure_ascii=False,indent=2))
put('links.json',json.dumps({'total':len(link_results),'broken':[],'external':[],'results':link_results,'browser_open':'BLOCKED: CUA could not confidently determine Windows browser URL; no successful UI open claimed','css_or_script_dependencies':css_dependencies+parser.unsupported},ensure_ascii=False,indent=2))
put('offline_runs.json',json.dumps(runs,ensure_ascii=False,indent=2))
put('manifest_before.json',json.dumps(initial,ensure_ascii=False,indent=2))
put('README.md','''# Kiểm tra kỹ thuật - không cần chiếu khi phỏng vấn
Thư mục này chứa kết quả rà soát mới: link, quét riêng tư, thời gian script, cây file và báo cáo kiểm tra. Có thể giữ để đối chiếu, không phải nội dung trả lời của thành viên.
`_kiem_tra/hien_thi/`: 13 PNG render từng trang PDF, 4 ảnh ghép có tên file, pdf_pages.csv và VERIFICATION.md. Đã di chuyển 19 file vào đây, giữ nguyên byte và kiểm hash từng file; không cần mở khi phỏng vấn. Bản ghi: doi_chieu_id_va_di_chuyen.json. Tên đường dẫn cũ trong chữ trên ảnh là nhãn lịch sử, không phải liên kết cần mở.
Audit chỉ đọc nội dung trong gói; không mở Test/corpus, không nạp mô hình hoặc chạy lại suy luận. Không lưu văn bản nghi là bài luận vào kết quả quét; chỉ lưu file/vị trí/loại phát hiện.
''')
missing=(P/'08_tai_lap/THIEU_VA_DOI_CHIEU.md').read_text(encoding='utf-8')
notes='\n'.join(l for l in missing.splitlines() if any(k in l.lower() for k in ['chưa xác định','chưa có nguồn','chưa có bản','chưa đủ','chưa có nguồn gốc','thiếu mô hình','cần thành viên','chưa rõ']))
findings=f'''# Kết quả rà soát interview_pack

## 1. Manifest và FILE_LIST
Trước lần chốt hiện tại (so với manifest của lượt kiểm tra trước): {initial['matched']}/{initial['entries']} mục khớp; {len(initial['mismatched'])} lệch; {len(initial['missing'])} mất file. Chi tiết ở manifest_before.json; script audit vừa sửa cũng thuộc danh sách được băm, nên hash cũ của chính script có thể khác.
Sau audit: mọi file trừ MANIFEST.sha256 được ghi hash. FILE_LIST.md liệt kê đúng tập mục trong manifest, không liệt kê chính manifest như một mục tự băm. Manifest được ghi sau tất cả nội dung; bước cuối xác minh toàn bộ hash, tập đường dẫn và mtime nghiêm ngặt. Hash manifest được in ra console và báo trong chat, không ghi vào file bên trong để tránh vòng tự tham chiếu.

## 2. Thư mục kiểm định hiển thị
_kiem_tra/hien_thi có {len(list((P/'_kiem_tra/hien_thi').glob('*.png')))} PNG (13 render trang PDF + 4 ảnh ghép), pdf_pages.csv và VERIFICATION.md. Đã gom 19 file vào đây và xác minh toàn bộ nội dung giữ nguyên theo hash trước/sau; không cần cho phần trình chiếu phỏng vấn.

## 3. Trang mở đầu
Đã đọc và phân tích toàn bộ HTML: {len(link_results)} liên kết tương đối, 0 hỏng, 0 liên kết mạng; fragment page của PDF hợp lệ; đủ mục 11–15. Không script, CDN, @import hoặc url CSS; không cần máy chủ khi mở file trực tiếp. links.json có danh sách đầy đủ.
Mở bằng trình duyệt UI: CHƯA XÁC NHẬN. Công cụ CUA tự chặn vì không xác định đủ tin cậy URL hiện tại trên Windows; không tiếp tục thao tác UI. Kết quả trên là xác minh tĩnh đích file, không phải tuyên bố đã mở trang thành công.

## 4. Cây và mẫu
TREE.txt liệt kê toàn bộ cây, kích thước byte, file rỗng và mẫu trống. File rỗng vật lý: {len(zero)}. Mẫu CSV/hướng dẫn trống: {len(templates)}; thêm hai file dữ liệu có ô cố ý để trống được đánh dấu riêng. Không điền thay thành viên.

## 5. Quét riêng tư
Quét {len(texts)} file text/PDF; giải mã {len(pngs)} PNG, {sum(x['matches_prior_manifest'] for x in pngs)} PNG khớp manifest trước audit. Không OCR PNG; ảnh dựa trên QA trực quan và tính toàn vẹn.
Số chuỗi 10 chữ số theo regex, phân loại ngữ cảnh: {dict(digit_summary)}. Không in giá trị/đoạn bài luận. Xem privacy_scan.json để lấy vị trí từng match; các số thập phân và hash không được tự gọi là mã sinh viên.
Một ID bài toàn số 10 chữ số: 07_kiem_tra_offline/development_predictions.csv, dòng 1751, cột essay_id. Đã đối chiếu với reports/week9/t3_eligible_development.csv / essay_id: xuất hiện đúng một lần. Trong 3812 ID duy nhất: 3809 ID dài 12 ký tự hex có chữ; 2 ID toàn số dài 11 chữ số; 1 ID toàn số dài 10 chữ số. Nguồn và hash nguồn trong doi_chieu_id_va_di_chuyen.json. Không thay ID để tránh thay phép xếp hạng. Các literal định nghĩa quy tắc của chính audit_pack.py không được xem là payload bài luận; đã kiểm tra các false positive đó theo vị trí, không in nội dung bài.
Trường chứa payload hoặc cột dữ liệu riêng tư: {len(payload_hits)}; mẫu họ tên đầy đủ thành viên: {len(name_hits)}; đoạn English dài cần xem xét: {len(english_candidates)}; định dạng chưa xử lý: {len(unknown)}.
Không phát hiện payload bài luận theo các kiểm tra trên. Không thể chứng minh tuyệt đối không có bài luận bằng đối chiếu corpus vì không được mở corpus; cũng không có danh sách họ tên đầy đủ chuẩn để so khớp toàn bộ tên bất kỳ. Nhãn thư mục Nam/Giang/Linh là ba nhãn đã được yêu cầu.

## 6. Chạy offline
Hai tiến trình Python -I có audit hook chặn socket/network và mọi đọc repository ngoài gói. Cả hai return code 0, dưới 10 giây. Thời gian là toàn tiến trình, không chỉ đồng hồ nội bộ script.
{chr(10).join('- '+x['script']+': '+str(x['wall_seconds'])+' giây' for x in runs)}
D in 88/386; expected_random=77.362908 (77.36), tổng budget=764. Script synthetic có N=10, K=3, k=2, caught=1, E=0,6; không phải script synthetic cũng in 88/386. Stdout được lưu riêng, không sửa ảnh đầu ra đã có.

## 7. Những phần còn thiếu nguồn/xác nhận
{notes}

15,0% và 16,6% đã có nguồn 35/233 và 36/217 ở tuần 10; không còn là số thiếu nguồn. File khóa được đối chiếu bằng hai bản trong gói, không mở nguồn ngoài gói.
'''
put('KET_QUA_KIEM_TRA.md',findings)
# Check every real Markdown navigation link as well as START_HERE.
markdown_links=[]
for f in P.rglob('*.md'):
 for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)',f.read_text(encoding='utf-8-sig')):
  u=urlsplit(raw.strip('<>'))
  if u.scheme or u.netloc or not u.path:continue
  target=(f.parent/unquote(u.path)).resolve()
  assert target.is_relative_to(P) and target.exists(),(str(f.relative_to(P)),raw)
  markdown_links.append({'file':f.relative_to(P).as_posix(),'url':raw,'status':'OK'})
put('markdown_links.json',json.dumps({'broken':[],'links':markdown_links},ensure_ascii=False,indent=2))
move=json.loads((OUT/'doi_chieu_id_va_di_chuyen.json').read_text(encoding='utf-8'))
assert all(sha(P/'_kiem_tra/hien_thi'/rel)==h for rel,h in move['moved_file_sha256'].items())
# No content writes after sealing. Tree file sizes solve a fixed point; width is fixed.
tree=OUT/'TREE.txt';tree.write_text('',encoding='utf-8')
paths=sorted(p.relative_to(P).as_posix() for p in inventory() if p.name!='MANIFEST.sha256')
filelist='# Danh sách file khớp MANIFEST.sha256\n\nMỗi mục dưới đây có một hash trong manifest. MANIFEST.sha256 không tự chứa hash của chính nó.\n\n'+''.join(f'- [{rel}]({rel})\n' for rel in paths)
(P/'FILE_LIST.md').write_text(filelist,encoding='utf-8')
assert 'FILE_LIST.md' in paths
manifest_size=sum(len((('0'*64)+'  '+rel+'\n').encode('utf-8')) for rel in paths)
for iteration in range(8):
 result=['interview_pack/  (kích thước: byte; RỖNG=0 byte; MẪU TRỐNG=có hướng dẫn/tiêu đề nhưng ô trả lời trống)']
 for f in inventory():
  rel=f.relative_to(P).as_posix();depth=len(Path(rel).parts)-1
  size=manifest_size if rel=='MANIFEST.sha256' else f.stat().st_size
  flag=templates.get(rel,'')
  if size==0 and f!=tree:flag='RỖNG'
  if rel in partial:flag='DỮ LIỆU + Ô TRỐNG CÓ CHỦ Ý'
  result.append('  '*depth+f'{rel} | {size:12d} bytes'+(' | '+flag if flag else ''))
 value='\n'.join(result)+'\n';previous=tree.read_text(encoding='utf-8');tree.write_text(value,encoding='utf-8')
 if previous==value:break
else:raise RuntimeError('Tree size did not stabilize')
assert sorted(p.relative_to(P).as_posix() for p in inventory() if p.name!='MANIFEST.sha256')==paths
manifest=P/'MANIFEST.sha256'
manifest.write_text(''.join(f'{sha(P/rel)}  {rel}\n' for rel in paths),encoding='utf-8',newline='\n')
assert manifest.stat().st_size==manifest_size
latest=max((P/rel).stat().st_mtime_ns for rel in paths)
os.utime(manifest,ns=(time.time_ns(),max(time.time_ns(),latest+1_000_000)))
sealed=manifest_rows();mismatches=[rel for rel,h in sealed.items() if sha(P/rel)!=h]
listed=set(re.findall(r'^- \[([^\]]+)\]\(', (P/'FILE_LIST.md').read_text(encoding='utf-8'),re.M))
assert set(sealed)==set(paths)==listed
assert not mismatches
assert manifest.stat().st_mtime_ns>latest
lock=P/'12_mang_theo/signal_lock_tree_spread.md'
assert sha(lock)=='d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca'
print(json.dumps({'initial':initial,'sealed_matches':len(sealed),'sealed_mismatches':len(mismatches),'file_list_exact':True,'manifest_newer_than_all':True,'manifest_time_vietnam':datetime.fromtimestamp(manifest.stat().st_mtime,timezone(timedelta(hours=7))).isoformat(),'latest_other_time_vietnam':datetime.fromtimestamp(latest/1e9,timezone(timedelta(hours=7))).isoformat(),'manifest_sha256':sha(manifest),'links':len(link_results),'broken_links':0,'external_index_links':0,'zero_byte_files':zero,'templates':templates,'privacy_summary':dict(digit_summary),'payload_candidates':payload_hits,'full_name_candidates':name_hits,'long_english_candidates':english_candidates,'runs':runs},ensure_ascii=False,indent=2))
