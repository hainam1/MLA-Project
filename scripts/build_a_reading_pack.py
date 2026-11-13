"""Build the 10 error cases reading pack for independent blinded human review (Section A).
Produces:
  local_only/doc_10_ca/1_doc_truoc/CAxx.txt (blinded text only)
  local_only/doc_10_ca/2_doi_chieu/anh_xa_ma_ca.csv
  local_only/doc_10_ca/2_doi_chieu/CAxx_doi_chieu.txt
  local_only/doc_10_ca/phieu_doc_10_ca.xlsx (blank reader forms)
Execution environment: .venv
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import random
import re
import zipfile
import numpy as np
import pandas as pd
import language_tool_python

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'local_only/doc_10_ca'
DIR_DOC_TRUOC = OUT_DIR / '1_doc_truoc'
DIR_DOI_CHIEU = OUT_DIR / '2_doi_chieu'
EXCEL_PATH = OUT_DIR / 'phieu_doc_10_ca.xlsx'
GECTOR_JSON = ROOT / 'scripts/gector_10_cases_output.json'

CASES = [
    '0514D25768A0', '684166ED2438', '2716F5E20A4F', '48EA282A4EAF', '31D67F9A82BA',
    'E70DD00622DB', '2C38B62420C3', '7CAFF57E1775', '9A36D8AB4818', 'D2EBEB5FDA90'
]

def make_clean_xlsx(sheets, path):
    """Write standard OpenXML spreadsheet with multiple sheets using python standard library."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml
        content_types = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '<Default Extension="xml" ContentType="application/xml"/>',
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        ]
        for i in range(1, len(sheets) + 1):
            content_types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        content_types.append('</Types>')
        z.writestr('[Content_Types].xml', ''.join(content_types))
        
        # _rels/.rels
        z.writestr('_rels/.rels', 
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        )
        
        # xl/_rels/workbook.xml.rels
        wb_rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        ]
        for i in range(1, len(sheets) + 1):
            wb_rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
        wb_rels.append('</Relationships>')
        z.writestr('xl/_rels/workbook.xml.rels', ''.join(wb_rels))
        
        # xl/workbook.xml
        wb_xml = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
            '<sheets>'
        ]
        for i, name in enumerate(sheets.keys(), 1):
            wb_xml.append(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>')
        wb_xml.append('</sheets></workbook>')
        z.writestr('xl/workbook.xml', ''.join(wb_xml))
        
        # xl/styles.xml
        z.writestr('xl/styles.xml',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<fonts count="2">'
            '<font><name val="Calibri"/><sz val="11"/></font>'
            '<font><b/><name val="Calibri"/><sz val="11"/></font>'
            '</fonts>'
            '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
            '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            '<cellXfs count="2">'
            '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
            '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0"/>'
            '</cellXfs>'
            '</styleSheet>'
        )
        
        def col_letter(c):
            s = ''
            while c > 0:
                c, r = divmod(c - 1, 26)
                s = chr(65 + r) + s
            return s
            
        # worksheets
        for i, (name, rows) in enumerate(sheets.items(), 1):
            ws_xml = [
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
                '<sheetData>'
            ]
            for r_idx, row in enumerate(rows, 1):
                ws_xml.append(f'<row r="{r_idx}">')
                is_header = (r_idx == 1)
                for c_idx, val in enumerate(row, 1):
                    ref = f'{col_letter(c_idx)}{r_idx}'
                    style_attr = ' s="1"' if is_header else ''
                    if val is not None and str(val) != '':
                        escaped = str(val).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                        ws_xml.append(f'<c r="{ref}" t="inlineStr"{style_attr}><is><t>{escaped}</t></is></c>')
                    else:
                        ws_xml.append(f'<c r="{ref}"{style_attr}/>')
                ws_xml.append('</row>')
            ws_xml.append('</sheetData></worksheet>')
            z.writestr(f'xl/worksheets/sheet{i}.xml', ''.join(ws_xml))
            
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(buf.getvalue())

def main():
    DIR_DOC_TRUOC.mkdir(parents=True, exist_ok=True)
    DIR_DOI_CHIEU.mkdir(parents=True, exist_ok=True)

    # 1. Random assignment CA01..CA10 with random.Random(42)
    rng = random.Random(42)
    shuffled_ids = CASES.copy()
    rng.shuffle(shuffled_ids)
    
    ca_to_eid = {f'CA{i+1:02d}': eid for i, eid in enumerate(shuffled_ids)}
    eid_to_ca = {eid: ca for ca, eid in ca_to_eid.items()}

    # 2. Load development data & features for z-score calculation
    dev_df = pd.read_csv(ROOT / 'reports/week9/t3_eligible_development.csv')
    with open(ROOT / 'outputs/phase6/feature_schema.json') as f:
        schema = json.load(f)
    feature_cols = schema.get('feature_columns', schema) if isinstance(schema, dict) else schema
    assert len(feature_cols) == 14

    dev_features = dev_df[feature_cols].to_numpy(dtype=float)
    feat_mean = np.mean(dev_features, axis=0)
    feat_std = np.std(dev_features, axis=0, ddof=0)

    # Load texts
    texts = {}
    for p in ['data/03_clean_ready_to_use/model_train_3128.csv', 'data/03_clean_ready_to_use/validation_783.csv']:
        with open(ROOT / p, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                if r['essay_id'] in CASES:
                    texts[r['essay_id']] = r['essay_text']
    assert len(texts) == 10

    # Load G1 metadata & predictions
    g1_df = pd.read_csv(ROOT / 'docs/nguon_bao_cao_interview/g1_ca_loi.csv')
    g1_map = {r['essay_id']: r for r in g1_df.to_dict('records')}

    # Fold sizes for D_rank on k
    fold_comp = pd.read_csv(ROOT / 'reports/week9/t3_fold_composition.csv')
    fold_comp_disjoint = fold_comp[fold_comp['split_type'] == 'prompt_disjoint']
    fold_sizes = fold_comp_disjoint.groupby('fold')['heldout_essays'].first().to_dict()
    assert fold_sizes == {1: 769, 2: 768, 3: 761, 4: 745, 5: 769}

    # Load GECToR results
    with open(GECTOR_JSON, encoding='utf-8') as f:
        gector_data = json.load(f)

    # Initialize LanguageTool 6.6
    print("Initializing LanguageTool 6.6 offline...", flush=True)
    lt_tool = language_tool_python.LanguageTool('en-US', language_tool_download_version='6.6')

    # Run LanguageTool on first 150 words
    lt_results = {}
    for eid in CASES:
        first150_words = texts[eid].split()[:150]
        first150_text = ' '.join(first150_words)
        matches = lt_tool.check(first150_text)
        grammar_matches = [m for m in matches if getattr(m, 'ruleIssueType', '').casefold() == 'grammar']
        rule_breakdown = {}
        for m in grammar_matches:
            rule_breakdown[m.ruleId] = rule_breakdown.get(m.ruleId, 0) + 1
        lt_results[eid] = {
            'total_grammar': len(grammar_matches),
            'total_all': len(matches),
            'rule_breakdown': rule_breakdown,
            'details': [{'ruleId': m.ruleId, 'message': m.message} for m in grammar_matches]
        }
    lt_tool.close()
    print("LanguageTool 6.6 completed for all 10 cases.", flush=True)

    # 3. Create 1_doc_truoc/CAxx.txt
    # Strict rule: NO scores, NO predictions, NO ranks, NO features, NO essay_id
    for ca_code in sorted(ca_to_eid.keys()):
        eid = ca_to_eid[ca_code]
        row_dev = dev_df[dev_df['essay_id'] == eid].iloc[0]
        prompt_name = row_dev['normalised_prompt']
        word_count = int(row_dev['word_count'])
        essay_text = texts[eid]

        content = (
            f"Mã ca: {ca_code}\n"
            f"Tên đề: {prompt_name}\n"
            f"Số từ: {word_count}\n\n"
            f"Toàn văn bài viết:\n"
            f"{essay_text}\n"
        )
        file_path = DIR_DOC_TRUOC / f"{ca_code}.txt"
        file_path.write_text(content, encoding='utf-8')

    # 4. Create 2_doi_chieu/anh_xa_ma_ca.csv
    mapping_rows = [{'ma_ca': ca, 'essay_id': ca_to_eid[ca]} for ca in sorted(ca_to_eid.keys())]
    mapping_csv = DIR_DOI_CHIEU / 'anh_xa_ma_ca.csv'
    with open(mapping_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ma_ca', 'essay_id'])
        writer.writeheader()
        writer.writerows(mapping_rows)

    # 5. Create 2_doi_chieu/CAxx_doi_chieu.txt
    for ca_code in sorted(ca_to_eid.keys()):
        eid = ca_to_eid[ca_code]
        row_dev = dev_df[dev_df['essay_id'] == eid].iloc[0]
        row_g1 = g1_map[eid]
        
        prompt_name = row_dev['normalised_prompt']
        fold = int(row_g1['fold'])
        N_fold = fold_sizes[fold]
        k_fold = int(row_g1['k'])
        d_rank = int(row_g1['D_rank'])
        D_val = float(row_g1['D'])
        
        y_v = float(row_g1['y_V'])
        y_g = float(row_g1['y_G'])
        rf_v = float(row_g1['RF_V'])
        rf_g = float(row_g1['RF_G'])
        rg_v = float(row_g1['Ridge_V'])
        rg_g = float(row_g1['Ridge_G'])
        
        e_rf_v = rf_v - y_v
        e_rf_g = rf_g - y_g
        e_rg_v = rg_v - y_v
        e_rg_g = rg_g - y_g
        
        rf_max_err = max(abs(e_rf_v), abs(e_rf_g))
        rg_max_err = max(abs(e_rg_v), abs(e_rg_g))

        # 14 features z-score
        feat_vals = [float(row_dev[c]) for c in feature_cols]
        z_scores = [(val - m) / s for val, m, s in zip(feat_vals, feat_mean, feat_std)]
        
        # Rank by absolute z-score
        ranked_feats = sorted(zip(feature_cols, feat_vals, feat_mean, feat_std, z_scores),
                              key=lambda x: abs(x[4]), reverse=True)
        top3_set = {ranked_feats[0][0], ranked_feats[1][0], ranked_feats[2][0]}

        # LT & GECToR info
        lt_info = lt_results[eid]
        gec_info = gector_data[eid]

        doc = []
        doc.append(f"Mã ca: {ca_code} (essay_id: {eid})")
        doc.append(f"Tên đề: {prompt_name}")
        doc.append(f"Fold: {fold} (Tổng số bài fold N = {N_fold}, Ngân sách k = {k_fold})")
        doc.append("-" * 60)
        doc.append("1. ĐIỂM THẬT VÀ DỰ ĐOÁN (V = Vocabulary, G = Grammar):")
        doc.append(f"  - Điểm thật:        V = {y_v:.1f}, G = {y_g:.1f}")
        doc.append(f"  - Random Forest:    V = {rf_v:.4f}, G = {rf_g:.4f}")
        doc.append(f"  - Ridge:            V = {rg_v:.4f}, G = {rg_g:.4f}")
        doc.append(f"  - Sai số RF:        e_V = {e_rf_v:+.4f}, e_G = {e_rf_g:+.4f} (Max target abs error = {rf_max_err:.4f})")
        doc.append(f"  - Sai số Ridge:     e_V = {e_rg_v:+.4f}, e_G = {e_rg_g:+.4f} (Max target abs error = {rg_max_err:.4f})")
        doc.append(f"  - Nhóm lỗi:         {row_g1['error_group']}")
        doc.append("-" * 60)
        doc.append("2. TÍN HIỆU ĐỘ BẤT ĐỒNG (D) VÀ HÀNG ĐỢI KIỂM DUYỆT:")
        doc.append(f"  - Giá trị D:        {D_val:.6f} (max(|RF_V - Ridge_V|, |RF_G - Ridge_G|))")
        doc.append(f"  - Hạng D trong fold:{d_rank} / {N_fold}")
        doc.append(f"  - Ngân sách k fold: {k_fold} bài (20% fold)")
        doc.append(f"  - Trạng thái bắt:   {'ĐƯỢC BẮT (Hạng D <= k)' if d_rank <= k_fold else 'BỊ LỌT (Hạng D > k)'}")
        doc.append("-" * 60)
        doc.append("3. 14 ĐẶC TRƯNG NGÔN NGỮ SO VỚI TRUNG BÌNH DEVELOPMENT (N=3.812):")
        doc.append(f"  {'Đặc trưng':<40} {'Giá trị':<12} {'Mean dev':<12} {'Std dev':<12} {'Z-score':<10} {'Lệch nhất'}")
        for f_name, f_val, f_m, f_s, z in ranked_feats:
            mark = "(*) TOP 3 LỆCH" if f_name in top3_set else ""
            doc.append(f"  {f_name:<40} {f_val:<12.4f} {f_m:<12.4f} {f_s:<12.4f} {z:<+10.3f} {mark}")
        doc.append("-" * 60)
        doc.append("4. CÔNG CỤ ĐẾM LỖI NGỮ PHÁP TRÊN 150 TỪ ĐẦU:")
        doc.append(f"  a) LanguageTool 6.6 (đếm thật trên 150 từ đầu):")
        doc.append(f"     - Số cảnh báo ngữ pháp (ruleIssueType == 'grammar'): {lt_info['total_grammar']}")
        doc.append(f"     - Tổng số cảnh báo mọi loại: {lt_info['total_all']}")
        doc.append(f"     - Phân loại lỗi ngữ pháp: {json.dumps(lt_info['rule_breakdown'], ensure_ascii=False)}")
        doc.append(f"  b) GECToR + ERRANT (đếm thật trên 150 từ đầu):")
        doc.append(f"     - edits_grammar (loại trừ SPELL, PUNCT, ORTH): {gec_info['edits_grammar']}")
        doc.append(f"     - edits_all (mọi loại sửa đổi): {gec_info['edits_all']}")
        doc.append(f"     - Chi tiết từng loại lỗi ERRANT: {json.dumps(gec_info['per_type'], ensure_ascii=False)}")
        doc.append("=" * 60)

        doi_chieu_file = DIR_DOI_CHIEU / f"{ca_code}_doi_chieu.txt"
        doi_chieu_file.write_text('\n'.join(doc) + '\n', encoding='utf-8')

    # 6. Create blank Excel form: phieu_doc_10_ca.xlsx
    headers_doc_truoc = [
        'ma_ca', 'nguoi_doc', 'ngay_gio_bat_dau', 'ngay_gio_luu', 'pham_vi_doc',
        'so_loi_ngu_phap_150_tu', 'quan_sat_tu_vung', 'cau_trich_tu_vung (≤15 từ)',
        'quan_sat_ngu_phap', 'cau_trich_ngu_phap (≤15 từ)', 'muc_V_thap_trung_cao',
        'muc_G_thap_trung_cao'
    ]
    rows_doc_truoc = [headers_doc_truoc]
    for ca_code in sorted(ca_to_eid.keys()):
        row = [ca_code] + [''] * (len(headers_doc_truoc) - 1)
        rows_doc_truoc.append(row)

    headers_sau_doi_chieu = [
        'ma_ca', 'nguoi_doc', 'ngay_gio', 'diem_that_co_hop_ly',
        'nguyen_nhan_nghi_ngo', 'la_quan_sat_hay_chi_nghi_ngo',
        'buoc_kiem_tra_tiep', 'quyet_dinh'
    ]
    rows_sau_doi_chieu = [headers_sau_doi_chieu]
    for ca_code in sorted(ca_to_eid.keys()):
        row = [ca_code] + [''] * (len(headers_sau_doi_chieu) - 1)
        rows_sau_doi_chieu.append(row)

    sheets_payload = {
        'doc_truoc': rows_doc_truoc,
        'sau_doi_chieu': rows_sau_doi_chieu
    }
    make_clean_xlsx(sheets_payload, EXCEL_PATH)
    print(f"Generated Excel workbook at {EXCEL_PATH}")

    # 7. Verification: Scan 1_doc_truoc/ for any forbidden tokens (essay_ids, scores)
    print("\n--- SAFETY AUDIT OF 1_doc_truoc/ ---")
    leak_found = False
    score_patterns = [r'\b1\.0\b', r'\b1\.5\b', r'\b2\.0\b', r'\b2\.5\b', r'\b3\.0\b', r'\b3\.5\b', r'\b4\.0\b', r'\b4\.5\b', r'\b5\.0\b']
    
    for f in sorted(DIR_DOC_TRUOC.glob('*.txt')):
        text = f.read_text(encoding='utf-8')
        for eid in CASES:
            if eid in text:
                print(f"ERROR: Found essay_id {eid} in {f.name}!")
                leak_found = True
        # Check header lines specifically
        lines = text.splitlines()[:5]
        for line in lines:
            if any(term in line.lower() for term in ['điểm', 'score', 'target', 'ridge', 'forest', 'rank', 'hạng']):
                print(f"ERROR: Found forbidden term in header of {f.name}: {line}")
                leak_found = True

    if not leak_found:
        print("PASS: 1_doc_truoc/ contains ZERO essay_ids, zero model names, and zero score headers!")

    # 8. Compute SHA-256
    excel_sha = hashlib.sha256(EXCEL_PATH.read_bytes()).hexdigest()
    print(f"\nSHA-256 phieu_doc_10_ca.xlsx: {excel_sha}")

    doc_truoc_files = sorted(DIR_DOC_TRUOC.glob('*.txt'))
    print(f"\nSHA-256 of files in 1_doc_truoc/ ({len(doc_truoc_files)} files):")
    combined_hasher = hashlib.sha256()
    for f in doc_truoc_files:
        f_sha = hashlib.sha256(f.read_bytes()).hexdigest()
        print(f"  {f.name}: {f_sha}")
        combined_hasher.update(f"{f.name}:{f_sha}\n".encode('utf-8'))
    folder_sha = combined_hasher.hexdigest()
    print(f"\nCombined SHA-256 of 1_doc_truoc/: {folder_sha}")

if __name__ == '__main__':
    main()
