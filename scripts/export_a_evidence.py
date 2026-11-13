"""Export text-free tool comparison metrics for the 10 error cases (Section A)
and document SHA-256 baseline hashes.
"""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / 'docs/final_evidence/a_doi_chieu_so_lieu.csv'
OUT_HASH = ROOT / 'docs/final_evidence/a_reading_pack_hashes.txt'
GECTOR_JSON = ROOT / 'scripts/gector_10_cases_output.json'
MAPPING_CSV = ROOT / 'local_only/doc_10_ca/2_doi_chieu/anh_xa_ma_ca.csv'
DIR_DOC_TRUOC = ROOT / 'local_only/doc_10_ca/1_doc_truoc'
EXCEL_PATH = ROOT / 'local_only/doc_10_ca/phieu_doc_10_ca.xlsx'

CASES = [
    '0514D25768A0', '684166ED2438', '2716F5E20A4F', '48EA282A4EAF', '31D67F9A82BA',
    'E70DD00622DB', '2C38B62420C3', '7CAFF57E1775', '9A36D8AB4818', 'D2EBEB5FDA90'
]

def main():
    # 1. Load mapping & doi_chieu to get LT counts
    with open(MAPPING_CSV) as f:
        mapping = {r['ma_ca']: r['essay_id'] for r in csv.DictReader(f)}
    eid_to_ca = {v: k for k, v in mapping.items()}

    # Load GECToR
    with open(GECTOR_JSON) as f:
        gector = json.load(f)

    # Load LT counts from CAxx_doi_chieu.txt
    lt_grammar = {}
    lt_all = {}
    for ca, eid in mapping.items():
        text = (ROOT / f'local_only/doc_10_ca/2_doi_chieu/{ca}_doi_chieu.txt').read_text(encoding='utf-8')
        lt_line = [l for l in text.splitlines() if 'Số cảnh báo ngữ pháp' in l][0]
        lt_all_line = [l for l in text.splitlines() if 'Tổng số cảnh báo mọi loại' in l][0]
        lt_grammar[eid] = int(lt_line.split(':')[-1].strip())
        lt_all[eid] = int(lt_all_line.split(':')[-1].strip())

    rows = []
    for eid in sorted(CASES):
        gec_rec = gector[eid]
        rows.append({
            'essay_id': eid,
            'window': 'first150_whitespace_words',
            'words_in_window': gec_rec['words_150'],
            'lt_grammar_matches_first150': lt_grammar[eid],
            'lt_total_matches_first150': lt_all[eid],
            'gector_edits_grammar_first150': gec_rec['edits_grammar'],
            'gector_edits_all_first150': gec_rec['edits_all'],
            'status': 'TÍNH MỚI (dev)',
            'source': 'LanguageTool 6.6 (local) + GECToR roberta-base-5k + ERRANT 3.0.2',
            'command': '.venv/Scripts/python.exe scripts/build_a_reading_pack.py'
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved text-free tool comparison to {OUT_CSV}")

    # 2. Generate a_reading_pack_hashes.txt
    excel_sha = hashlib.sha256(EXCEL_PATH.read_bytes()).hexdigest()
    doc_truoc_files = sorted(DIR_DOC_TRUOC.glob('*.txt'))
    
    file_hashes = {}
    combined_hasher = hashlib.sha256()
    for f in doc_truoc_files:
        f_sha = hashlib.sha256(f.read_bytes()).hexdigest()
        file_hashes[f.name] = f_sha
        combined_hasher.update(f"{f.name}:{f_sha}\n".encode('utf-8'))
    folder_sha = combined_hasher.hexdigest()

    hash_doc = [
        "# BẰNG CHỨNG MÃ BĂM TRẠNG THÁI BAN ĐẦU - BỘ ĐỌC 10 CA LỖI (MỤC A)",
        "",
        "Thời điểm tạo: Trước khi giao bài cho hai người đọc độc lập (Giang và Linh).",
        "Trạng thái: Phiếu đọc hoàn toàn trống mọi ô đánh giá; Thư mục đọc trước chỉ chứa văn bản đọc mù.",
        "",
        "## 1. Hai mã băm SHA-256 cốt lõi",
        f"- SHA-256 phiếu đọc trống (`local_only/doc_10_ca/phieu_doc_10_ca.xlsx`):",
        f"  {excel_sha}",
        f"- SHA-256 băm gộp thư mục đọc trước (`local_only/doc_10_ca/1_doc_truoc/`):",
        f"  {folder_sha}",
        "",
        "## 2. Chi tiết SHA-256 từng tệp trong `1_doc_truoc/` (10 bài đã ẩn danh CA01..CA10)",
    ]
    for fname, fsha in file_hashes.items():
        hash_doc.append(f"- {fname}: {fsha}")

    hash_doc.extend([
        "",
        "## 3. Quy cách tính mã băm gộp của thư mục `1_doc_truoc/`",
        "Mã băm gộp được tính bằng SHA-256 trên chuỗi nối các dòng định dạng:",
        "`<tên_tệp>:<sha256_tệp>\\n`",
        "với các tệp được sắp xếp theo thứ tự bảng chữ cái tên tệp (CA01.txt đến CA10.txt, mã hóa UTF-8).",
        "",
        "## 4. Cam kết bảo mật dữ liệu",
        "- Thư mục `local_only/` nằm trong `.gitignore` và không bao giờ được đưa lên repo công khai.",
        "- Tệp này là tệp text-free duy nhất lưu vết kiểm toán trạng thái ban đầu của bộ đọc."
    ])

    OUT_HASH.write_text('\n'.join(hash_doc) + '\n', encoding='utf-8')
    print(f"Saved initial state hashes to {OUT_HASH}")

if __name__ == '__main__':
    main()
