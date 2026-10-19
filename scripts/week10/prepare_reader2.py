"""Lock six IDs, then create a blind, empty second-reader sheet. Never read reader1."""
from pathlib import Path
import contextlib
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from reader2_agreement import choose_sample, xlsx_fields, HEADERS, IDS, MAPPING, SHEET, ROOT, NS

DEST = ROOT / 'reports/week10/RESULTS_week10.md'
TEXT = ROOT / 'data/03_clean_ready_to_use/validation_783.csv'
READS, BLOCKED = set(), []
LOCKED = False
ALLOWED = {IDS.resolve(), TEXT.resolve(), MAPPING.resolve(), SHEET.resolve()}


def audit(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return
    if not rel.parts or rel.parts[0] not in {'data', 'outputs', 'reports', 'docs'}:
        return
    mode = args[1]
    if path == DEST and isinstance(mode, str) and (mode in {'r', 'rb'} or
            (mode.startswith('a') and args[2] & os.O_APPEND and not args[2] & os.O_TRUNC)):
        return
    if path == MAPPING.resolve() and mode == 'x':
        return
    if path not in ALLOWED or (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (path == TEXT.resolve() and not LOCKED):
        BLOCKED.append(rel.as_posix())
        raise PermissionError('Preparation artifact outside stage-specific read allowlist: ' + rel.as_posix())
    READS.add(rel.as_posix())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append(text):
    with DEST.open('ab') as stream:
        stream.write(text.encode('utf-8'))


def verify(mapping, payload):
    headers, actual = xlsx_fields(SHEET, 'reader2', set(HEADERS))
    assert headers == HEADERS and len(actual) == 6
    assert [r['essay_id'] for r in actual] == [r['anonymous_id'] for r in mapping]
    for row, expected in zip(actual, payload):
        assert row['first150_words'] == expected['first150_words']
        assert row.get('reader2_errors_first150', '') == '' and row.get('notes', '') == ''
        assert 0 < len(row['first150_words'].split()) <= 150
    forbidden = {'band', 'y_V', 'y_G', 'Vocabulary', 'Grammar', 'RF_V', 'RF_G', 'Ridge_V', 'Ridge_G',
                 'word_count', 'detected_grammar_errors_per_100_words', 'tool_grammar_error_count_recovered',
                 'reader_errors_first150', 'Số lỗi ngữ pháp (150 từ đầu)', 'reader_low_mid_high_V', 'reader_low_mid_high_G'}
    assert not set(headers) & forbidden
    with zipfile.ZipFile(SHEET) as z:
        sheets = ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS)
        assert [(s.attrib['name'], s.attrib.get('state', 'visible')) for s in sheets] == [('reader2', 'visible')]
        assert not any('externalLink' in name or 'comment' in name.casefold() for name in z.namelist())
        for name in z.namelist():
            if name.endswith('.xml'):
                content = z.read(name)
                assert not any(r['essay_id'].encode('ascii') in content for r in mapping)
            if name.startswith('xl/worksheets/') and name.endswith('.xml'):
                node = ET.fromstring(z.read(name))
                assert not node.findall('.//s:f', NS)
                assert not node.findall('.//s:col[@hidden="1"]', NS)
                assert not node.findall('.//s:row[@hidden="1"]', NS)
    print('SHEET_CHECK sheets=[reader2]; rows=6; headers=' + json.dumps(headers))
    print('PASS banned_columns_absent=True; extra_sheets=0; hidden_rows_or_columns=0; formulas=0; external_links_or_comments=0; real_essay_IDs_in_package=0')
    print('PASS reader1_counts_absent=True; truth_absent=True; predictions_absent=True; tool_counts_absent=True; bands_absent=True')
    print('PASS reader2_count_cells_blank=6/6; notes_blank=6/6; no counts generated or filled by agent')
    print('FIRST150_TOKEN_RULE whitespace-delimited tokens from original Validation essay_text, first min(150,N), whitespace normalized to one space; no text printed.')
    print('FIRST150_CHECK anonymous_id,words_in_sheet,exact_source_prefix_match')
    for row in actual:
        print(f'{row["essay_id"]},{len(row["first150_words"].split())},True')


def main():
    global LOCKED
    heading = '## Week 10 second-reader agreement preparation'
    previous = DEST.read_bytes()
    assert heading.encode() not in previous and not MAPPING.exists() and not SHEET.exists(), 'Refusing to overwrite a selection or reader sheet'
    print('SELECTION_INPUT reports/week10/random_sample_ids.csv; only essay_id and band; no reader1 workbook opened.')
    selected, mapping, digest = choose_sample()
    print('SELECTION_RULE default_rng(2026); bands in <2.5,2.5-4.0,>4.0 order; essay_id-sorted pool within each band; choice(size=2,replace=False). Separate default_rng(2026).permutation(6) shuffles all six before assigning r2_01..r2_06.')
    print('SELECTED_IDS selection_index,essay_id,band')
    for row in selected:
        print(f'{row["selection_index"]},{row["essay_id"]},{row["band"]}')
    print('SELECTION_ARITHMETIC source=12+12+12=36; selected=2+2+2=6; unique_selected=6')
    print('SELECTED_ID_HASH_ENCODING ASCII essay IDs in selection_index order, one ID per line, including final LF')
    print('SELECTED_ID_LIST_SHA256=' + digest, flush=True)
    with MAPPING.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['anonymous_id', 'essay_id', 'band', 'selection_index'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(mapping)
    # Persist IDs/hash before opening essay text, and never open reader1 data.
    lock_text = ('\n\n' + heading + '\n\nTrạng thái: **chờ người đếm thứ hai điền**. '
                 'Hai bài mỗi vùng từ 36 ID Validation, seed 2026; chỉ ID và vùng điểm được dùng để chọn. '
                 'Danh sách và hash được ghi trước khi mở bài viết; script chuẩn bị không mở workbook người đếm thứ nhất. '
                 'Bảng ánh xạ riêng nội bộ: `reports/week10/reader2_id_map.csv`; chỉ gửi `reader2_sheet.xlsx` cho người đếm thứ hai.\n\n'
                 '```text\nselection_index,essay_id,band\n' +
                 ''.join(f'{r["selection_index"]},{r["essay_id"]},{r["band"]}\n' for r in selected) +
                 'seed=2026; within-band pools sorted by essay_id; 2 per band without replacement; all-six reading order independently shuffled with seed 2026.\n'
                 'canonical_ID_list=ASCII IDs in selection_index order, LF-separated, final LF included\n'
                 'SELECTED_ID_LIST_SHA256=' + digest + '\n'
                 'PRIVATE_MAPPING_SHA256=' + sha(MAPPING) + '\n```\n')
    append(lock_text)
    LOCKED = True
    print('SELECTION_LOCK_PERSISTED_BEFORE_TEXT_AND_ANY_READER1_DATA=True; private_mapping_SHA256=' + sha(MAPPING), flush=True)
    text_sha = sha(TEXT)
    texts = pd.read_csv(TEXT, usecols=['essay_id', 'essay_text'], dtype=str, keep_default_na=False)
    assert texts.essay_id.is_unique
    lookup = texts.set_index('essay_id').essay_text.to_dict()
    payload = []
    for row in mapping:
        assert row['essay_id'] in lookup
        first150 = ' '.join(lookup[row['essay_id']].split()[:150])
        assert first150
        payload.append(dict(essay_id=row['anonymous_id'], first150_words=first150, reader2_errors_first150='', notes=''))
    runtime = Path('C:/Users/LEGION/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')
    assert (runtime / '@oai/artifact-tool').is_dir()
    scratch = Path(tempfile.mkdtemp(prefix='mla-reader2-'))
    link = scratch / 'node_modules'
    command = "New-Item -ItemType Junction -Path '" + str(link).replace("'", "''") + "' -Target '" + str(runtime).replace("'", "''") + "' | Out-Null"
    subprocess.run(['powershell', '-NoProfile', '-Command', command], check=True)
    marker = Path('C:/Users/LEGION/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.1015.12040/skills/spreadsheets/container_tools/mark_artifact_operation_started.mjs')
    try:
        subprocess.run(['node', str(marker), '--operation-kind', 'create', '--expected-output-count', '1', '--output-format', 'xlsx'], check=True)
        env = dict(os.environ, R2_RUNTIME=str(scratch), R2_OUTPUT=str(SHEET))
        result = subprocess.run(['node', str(ROOT / 'scripts/week10/reader2_workbook.cjs')],
                                input=json.dumps(dict(rows=payload), ensure_ascii=False), text=True, encoding='utf-8',
                                env=env, capture_output=True)
        if result.returncode:
            raise RuntimeError('Reader2 workbook authoring failed; payload/text not printed')
    finally:
        os.rmdir(link)  # Remove only the junction, never its target recursively.
    verify(mapping, payload)
    print('HEADER_PREVIEW_TEMP_DIR=' + str(scratch))
    print('SYNTHETIC_SCRIPT_TEST_COMMAND .venv/Scripts/python.exe -B scripts/week10/reader2_agreement.py --self-test')
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/week10/reader2_agreement.py'), '--self-test'], capture_output=True)
    print(result.stdout.decode('utf-8'), end='')
    assert result.returncode == 0, 'Synthetic agreement test failed'
    print('EMPTY_REAL_SHEET_GUARD_TEST (no reader1 data may be read)')
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/week10/reader2_agreement.py')], capture_output=True)
    print(result.stderr.decode('utf-8'), end='')
    print(result.stdout.decode('utf-8'), end='')
    assert result.returncode == 2 and b'WAITING_FOR_READER2' in result.stderr and b'reader1_not_opened=True' in result.stdout
    print('PASS actual_empty_sheet_rejected=True; exit_code=2; reader1_workbook_not_opened=True')
    assert sha(TEXT) == text_sha
    for path in sorted(READS):
        print('READ_AUDIT ' + path + ' SHA256=' + sha(ROOT / path))
    print(f'READ_GUARD prepare_artifact_reads={len(READS)}; allowlisted_only=True; blocked_attempts={len(BLOCKED)}; no Test file opened; reader1_workbook_never_opened=True; no essay text printed.')
    print('STATUS chờ người đếm thứ hai điền; no real agreement statistic computed; no reader2 count filled.')
    print('OUTPUT_SHEET reports/week10/reader2_sheet.xlsx SHA256=' + sha(SHEET))
    print('PRIVATE_MAPPING reports/week10/reader2_id_map.csv SHA256=' + sha(MAPPING))
    assert DEST.read_bytes().startswith(previous)
    return lock_text


if __name__ == '__main__':
    sys.addaudithook(audit)
    capture = io.StringIO()
    class Tee:
        def write(self, text):
            sys.__stdout__.write(text)
            capture.write(text)
        def flush(self):
            sys.__stdout__.flush()
    with contextlib.redirect_stdout(Tee()):
        main()
    append('\nPreparation command: `.venv/Scripts/python.exe -B -u scripts/week10/prepare_reader2.py`. '
           'Future agreement command (only after human counts are complete): `.venv/Scripts/python.exe -B scripts/week10/reader2_agreement.py`.\n\n'
           '```text\n' + capture.getvalue() + '```\n')
