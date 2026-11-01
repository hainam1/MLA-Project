"""Verify one development ID, relocate QA bytes intact, repair pack navigation.
Only repository input: the explicitly authorized eligible-development CSV.
"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit, unquote
import csv, hashlib, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parents[1];R=P.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with (P/'07_kiem_tra_offline/development_predictions.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.reader(f))
target=rows[1750][rows[0].index('essay_id')]
source=R/'reports/week9/t3_eligible_development.csv'
with source.open(encoding='utf-8-sig',newline='') as f:
 ids=[r['essay_id'] for r in csv.DictReader(f)]
if ids.count(target)!=1:raise SystemExit('STOP: target ID not uniquely found in eligible development. No move performed.')
assert len(target)==10 and target.isdigit()
assert len(ids)==len(set(ids))==3812
check={'source':'reports/week9/t3_eligible_development.csv / essay_id','source_sha256':sha(source),'checked_pack_file':'07_kiem_tra_offline/development_predictions.csv','line':1751,'exact_matches':ids.count(target),'target_length':len(target),'target_format':'numeric_only','target_value_not_printed':True,'development_ids':len(ids),'length_distribution':dict(Counter(map(len,ids))),'formats':dict(Counter('numeric_only' if s.isdigit() else 'hex_with_letters' if re.fullmatch('[0-9A-Fa-f]+',s) else 'other' for s in ids)),'numeric_lengths':dict(Counter(map(len,(s for s in ids if s.isdigit()))))}
old=(P/'11_kiem_dinh_hien_thi').resolve();new=(P/'_kiem_tra/hien_thi').resolve()
assert old.parent==P and new.is_relative_to(P/'_kiem_tra')
assert old.is_dir() and not new.exists(),'Expected original QA directory and absent destination; refusing overwrite.'
before={f.relative_to(old).as_posix():sha(f) for f in old.rglob('*') if f.is_file()}
old.rename(new)
after={f.relative_to(new).as_posix():sha(f) for f in new.rglob('*') if f.is_file()}
assert before==after
check['moved_files']=len(before);check['moved_content_hashes_unchanged']=True
check['moved_file_sha256']=before
# Update scripts and navigation documents, preserving ALL moved files byte-for-byte.
for f in P.rglob('*'):
 if not f.is_file() or f.is_relative_to(new) or f.name in ['reorganize_pack.py','MANIFEST.sha256']:continue
 if f.suffix not in ['.md','.txt','.py','.html','.json','.csv']:continue
 s=f.read_text(encoding='utf-8-sig')
 if '11_kiem_dinh_hien_thi' not in s:continue
 s=s.replace('11_kiem_dinh_hien_thi','_kiem_tra/hien_thi')
 if f.name=='build_pack.py':
  s=s.replace("if p.parent.name!='_kiem_tra/hien_thi'","if not p.is_relative_to(P/'_kiem_tra')")
 f.write_text(s,encoding='utf-8')
# Five pre-existing links in copied source excerpts point into the original repo,
# not the self-contained pack. Keep their locator as text rather than a broken link.
repairs=[]
for f in (P/'08_tai_lap/nguon').glob('*.md'):
 s=f.read_text(encoding='utf-8-sig')
 def repair(m):
  label,url=m.groups();u=urlsplit(url.strip('<>'))
  if u.scheme or u.netloc or not u.path or (f.parent/unquote(u.path)).exists():return m.group()
  repairs.append({'file':f.relative_to(P).as_posix(),'original_reference':url})
  return label+' (nguồn gốc trong repository: `'+url+'`)'
 updated=re.sub(r'\[([^\]]*)\]\(([^)]+)\)',repair,s)
 if updated!=s:f.write_text(updated,encoding='utf-8')
check['source_reference_links_converted_to_text']=repairs
(P/'_kiem_tra/doi_chieu_id_va_di_chuyen.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf-8')
assert before=={f.relative_to(new).as_posix():sha(f) for f in new.rglob('*') if f.is_file()}
print(json.dumps({k:v for k,v in check.items() if k not in ['moved_file_sha256']},ensure_ascii=False,indent=2))
