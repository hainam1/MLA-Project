"""Seeded truth-band-only sampling, then blind reading workbook construction."""
from pathlib import Path
import contextlib
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
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
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/week10'
DEST = OUT / 'RESULTS_week10.md'
CSV = OUT / 'random_sample_ids.csv'
XLSX = OUT / 'reading_sheet_random.xlsx'
INPUTS = ['reports/week9/t3_eligible_development.csv', 'reports/week9/t4_manifest.csv',
          'data/03_clean_ready_to_use/validation_783.csv', 'outputs/phase6/validation_predictions.csv']
ALLOWED = {(ROOT / p).resolve() for p in INPUTS}
READS, BLOCKED = set(), []
BANDS = ['<2.5', '2.5-4.0', '>4.0']
READING = ['essay_id', 'band', 'reading_order', 'essay_text', 'prompt_name',
           'reader_errors_first150', 'reader_low_mid_high_V', 'reader_low_mid_high_G']
UNBLIND = ['essay_id', 'y_V', 'y_G', 'Ridge_V', 'Ridge_G', 'RF_V', 'RF_G',
           'word_count', 'detected_grammar_errors_per_100_words',
           'tool_grammar_error_count_recovered', 'detected_error_free_sentence_ratio']
SELECTION_FIXED = False


def audit(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return
    if not rel.parts or rel.parts[0] not in {'data', 'outputs', 'docs', 'reports'}:
        return
    mode = args[1]
    if path == DEST and isinstance(mode, str) and (mode in {'r', 'rb'} or
            (mode.startswith('a') and args[2] & os.O_APPEND and not args[2] & os.O_TRUNC)):
        return
    if path in {CSV, XLSX}:
        return
    if path not in ALLOWED or (isinstance(mode, str) and any(c in mode for c in 'wax+')):
        BLOCKED.append(rel.as_posix())
        raise PermissionError('Artifact outside read allowlist: ' + rel.as_posix())
    if path == (ROOT / INPUTS[3]).resolve() and not SELECTION_FIXED:
        raise PermissionError('Prediction read before sample was fixed')
    READS.add(rel.as_posix())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(title, rows):
    print(title)
    print(pd.DataFrame(rows).to_csv(index=False, lineterminator='\n'), end='', flush=True)


def recover_count(rate_text, words):
    """Unique integer consistent with the producer's %.12g rate serialization.

    extract_grammar.py: rate=100*count/word_count.
    phase4_extract_features.py serializes with float_format='%.12g'.
    Do not replace a non-identifiable count with an estimate.
    """
    # Week 9's CSV reserializes parsed phase4 %.12g rates at %.17g.
    # Restore the producer's decimal token before checking integer uniqueness.
    rate = Decimal(format(float(rate_text), '.12g'))
    assert abs(Decimal(rate_text)-rate) < Decimal('1e-10')
    if rate == 0:
        return 0
    quantum = Decimal(10) ** (rate.adjusted() - 11)
    low = (rate - quantum/2) * Decimal(words)/100
    high = (rate + quantum/2) * Decimal(words)/100
    a = int(low.to_integral_value(rounding=ROUND_CEILING))
    b = int(high.to_integral_value(rounding=ROUND_FLOOR))
    if a != b or Decimal(format(100*a/max(words, 1), '.12g')) != rate:
        raise ValueError('Cannot compute a unique exact tool count from the saved rate')
    return a


def verify(payload):
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(XLSX) as z:
        book = ET.fromstring(z.read('xl/workbook.xml'))
        sheets = book.findall('s:sheets/s:sheet', ns)
        assert [(s.attrib['name'], s.attrib.get('state', 'visible')) for s in sheets] == [('reading_sheet', 'visible'), ('unblind_after', 'hidden')]
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', ns)]
        for index, (name, headers, expected) in enumerate([
                ('reading_sheet', READING, payload['reading']), ('unblind_after', UNBLIND, payload['unblind'])], 1):
            sheet = ET.fromstring(z.read(f'xl/worksheets/sheet{index}.xml'))
            actual = {}
            for cell in sheet.findall('s:sheetData/s:row/s:c', ns):
                value = cell.find('s:v', ns)
                value = value.text if value is not None else None
                if cell.attrib.get('t') == 's':
                    value = strings[int(value)]
                elif cell.attrib.get('t') == 'inlineStr':
                    value = ''.join(cell.find('s:is', ns).itertext())
                elif value is not None and cell.attrib.get('t') not in {'str', 'e'}:
                    value = float(value)
                actual[cell.attrib['r']] = value
            def letter(i):
                result = ''
                while i:
                    i, rem = divmod(i-1, 26)
                    result = chr(65+rem) + result
                return result
            assert [actual.get(letter(j+1)+'1') for j in range(len(headers))] == headers
            for i, record in enumerate(expected, 2):
                for j, key in enumerate(headers, 1):
                    seen, value = actual.get(letter(j)+str(i)), record[key]
                    assert seen == value or (value == '' and seen is None) or (
                        isinstance(value, (int, float)) and isinstance(seen, (int, float)) and
                        np.isclose(value, seen, rtol=0, atol=1e-12)), (name, i, key)
            assert len(sheet.findall('s:sheetData/s:row', ns)) == len(expected)+1
            assert sheet.find('s:sheetViews/s:sheetView/s:pane', ns) is not None
            assert not sheet.findall('s:sheetData/s:row/s:c/s:f', ns)
            # Workbook content remains private; print names and headers only.
            print('SHEET ' + name + ' HEADERS=' + json.dumps(headers))
        assert all(record[c] == '' for record in payload['reading'] for c in READING[-3:])


def main():
    global SELECTION_FIXED
    print('PART C: RANDOM VALIDATION READING SAMPLE; exploratory; seed=2026; no errors, predictions, or tool counts used for selection.')
    f = pd.read_csv(ROOT / INPUTS[0], usecols=['essay_id', 'split', 'source_partition', 'Vocabulary', 'Grammar'], dtype={'essay_id': str})
    f = f.loc[f.split.eq('validation')].copy().sort_values('essay_id', kind='stable')
    assert len(f) == 762 and f.essay_id.is_unique and f.source_partition.eq('official_train').all()
    truth_mean = (f.Vocabulary + f.Grammar)/2
    f['band'] = np.where(truth_mean < 2.5, BANDS[0], np.where(truth_mean <= 4., BANDS[1], BANDS[2]))
    old = pd.read_csv(ROOT / INPUTS[1], usecols=['essay_id'], dtype={'essay_id': str})
    assert len(old) == 32 and old.essay_id.is_unique and set(old.essay_id) <= set(f.essay_id)
    rng = np.random.default_rng(2026)
    sample, counts = [], []
    for band in BANDS:
        all_ids = f.loc[f.band.eq(band), 'essay_id']
        pool = all_ids.loc[~all_ids.isin(old.essay_id)].to_numpy()
        n = min(12, len(all_ids))
        draw = rng.choice(pool, size=min(n, len(pool)), replace=False).tolist()
        if len(draw) < n:
            fallback = all_ids.loc[all_ids.isin(old.essay_id)].to_numpy()
            draw += rng.choice(fallback, size=n-len(draw), replace=False).tolist()
        sample += [dict(essay_id=e, band=band) for e in draw]
        counts.append(dict(band=band, Validation_n=len(all_ids), old_sample_excluded_from_pool=int(all_ids.isin(old.essay_id).sum()),
                           available_after_exclusion=len(pool), sampled=len(draw)))
    table('VALIDATION_BAND_AND_DRAW_COUNTS (mean truth; 2.5 and 4 included in middle)', counts)
    print('VALIDATION_ARITHMETIC ' + '+'.join(str(c['Validation_n']) for c in counts) + '=762')
    chosen = pd.DataFrame(sample)
    assert len(chosen) == 36 and chosen.essay_id.is_unique
    overlap = int(chosen.essay_id.isin(old.essay_id).sum())
    print(f'EXCLUDED_EXISTING_IDS=32; final_overlap_with_existing_32={overlap}; no_fallback_needed={overlap == 0}')
    csv_bytes = chosen.to_csv(index=False, lineterminator='\n').encode('utf-8')
    if CSV.exists():
        assert CSV.read_bytes() == csv_bytes, 'Resume must retain the already fixed sample'
    else:
        with CSV.open('xb') as stream:
            stream.write(csv_bytes)
    selected_hash = sha(CSV)
    SELECTION_FIXED = True
    print('SELECTION_FIXED_BEFORE_PREDICTIONS_AND_TOOL_COUNTS=True; random_sample_ids.csv SHA256=' + selected_hash)
    # Separate freshly seeded generator; all 36 records receive one shuffled order.
    order = np.random.default_rng(2026).permutation(len(chosen))
    chosen = chosen.iloc[order].reset_index(drop=True)
    chosen['reading_order'] = np.arange(1, len(chosen)+1)
    print('RANDOMIZATION default_rng(2026), choice without replacement per band in <2.5,2.5-4.0,>4.0 order from essay_id-sorted pools; separate default_rng(2026).permutation(36) for reading order.')
    # Only after fixing the IDs: obtain essay text, prompt name and unblinding data.
    text = pd.read_csv(ROOT / INPUTS[2], usecols=['essay_id', 'essay_text', 'prompt'], dtype=str, keep_default_na=False)
    text = text.loc[text.essay_id.isin(chosen.essay_id)].rename(columns={'prompt': 'prompt_name'})
    features = pd.read_csv(ROOT / INPUTS[0], usecols=['essay_id', 'Vocabulary', 'Grammar', 'word_count',
                          'detected_grammar_errors_per_100_words', 'detected_error_free_sentence_ratio'], dtype=str)
    features = features.loc[features.essay_id.isin(chosen.essay_id)].copy()
    features['tool_grammar_error_count_recovered'] = [recover_count(r.detected_grammar_errors_per_100_words, int(r.word_count)) for r in features.itertuples()]
    for col in ['Vocabulary', 'Grammar', 'word_count', 'detected_grammar_errors_per_100_words', 'detected_error_free_sentence_ratio']:
        features[col] = pd.to_numeric(features[col])
    features = features.rename(columns={'Vocabulary': 'y_V', 'Grammar': 'y_G'})
    predictions = pd.read_csv(ROOT / INPUTS[3], dtype={'essay_id': str}).rename(columns={
        'ridge_vocabulary': 'Ridge_V', 'ridge_grammar': 'Ridge_G',
        'random_forest_vocabulary': 'RF_V', 'random_forest_grammar': 'RF_G'})
    joined = chosen.merge(text, on='essay_id', validate='one_to_one').merge(features, on='essay_id', validate='one_to_one').merge(predictions, on='essay_id', validate='one_to_one')
    assert len(joined) == 36 and joined.reading_order.tolist() == list(range(1, 37))
    for col in READING[-3:]:
        joined[col] = ''
    payload = {'reading_headers': READING, 'unblind_headers': UNBLIND,
               'reading': joined[READING].to_dict('records'), 'unblind': joined[UNBLIND].to_dict('records')}
    print('TOOL_COUNT_METHOD restore phase4 %.12g rate tokens from Week 9 %.17g reserialization; recover unique integer c consistent with rate=100*c/word_count. Decimal rounding-interval, unique-integer and producer-format round-trip checks passed for all 36 selected records. No count estimated and no tool rerun.')
    if '--resume-export' in sys.argv:
        assert XLSX.exists()
        scratch = Path(os.environ['W10_RESUME_PREVIEW'])
        assert scratch.is_dir() and (scratch / 'reading_sheet_headers.png').exists() and (scratch / 'unblind_after_headers.png').exists()
        print('RESUMED_COMPLETED_EXPORT=True; same fixed sample; no resampling or second authoring operation. Initial recovery corrected %.12g/%.17g rate-token representation; export then completed before console encoding failure. Full exported cell verification follows.')
    else:
        runtime = Path('C:/Users/LEGION/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')
        assert runtime.joinpath('@oai/artifact-tool').is_dir()
        scratch = Path(tempfile.mkdtemp(prefix='mla-week10-reading-'))
        link = scratch / 'node_modules'
        # A local junction points to bundled dependencies without modifying them.
        ps = "New-Item -ItemType Junction -Path '" + str(link).replace("'", "''") + "' -Target '" + str(runtime).replace("'", "''") + "' | Out-Null"
        subprocess.run(['powershell', '-NoProfile', '-Command', ps], check=True)
        env = dict(os.environ, W10_RUNTIME=str(scratch), W10_PREVIEW=str(scratch), W10_XLSX=str(XLSX))
        marker = Path('C:/Users/LEGION/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.1015.12040/skills/spreadsheets/container_tools/mark_artifact_operation_started.mjs')
        try:
            subprocess.run(['node', str(marker), '--operation-kind', 'create', '--expected-output-count', '1', '--output-format', 'xlsx'], check=True)
            result = subprocess.run(['node', str(ROOT / 'scripts/week10/reading_workbook.cjs')], input=json.dumps(payload, ensure_ascii=False, allow_nan=False),
                                    text=True, encoding='utf-8', env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout, end='')
            if result.returncode:
                raise RuntimeError(result.stderr)
        finally:
            os.rmdir(link)  # Remove junction only; never recursively delete its target.
    # artifact-tool's documented surface has no worksheet visibility setter.
    # Apply only the native hidden state in the exported OOXML package.
    buffer = io.BytesIO()
    with zipfile.ZipFile(XLSX) as source, zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as dest:
        for info in source.infolist():
            content = source.read(info.filename)
            if info.filename == 'xl/workbook.xml':
                node = ET.fromstring(content)
                ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                sheets = node.findall('s:sheets/s:sheet', ns)
                assert [s.attrib['name'] for s in sheets] == ['reading_sheet', 'unblind_after']
                sheets[1].set('state', 'hidden')
                content = ET.tostring(node, encoding='utf-8', xml_declaration=True)
            dest.writestr(info, content)
    XLSX.write_bytes(buffer.getvalue())
    verify(payload)
    print('WORKBOOK_VERIFIED row counts, IDs, all source values, shuffled order, blank reader fields, frozen headers and ID column, no formulas, and hidden unblind_after sheet.')
    print('HEADER_PREVIEWS_TEMP_DIR=' + str(scratch))
    table('FINAL_SAMPLE_COUNTS', [dict(band=b, essays=int(chosen.band.eq(b).sum())) for b in BANDS])
    print('FINAL_SAMPLE_ARITHMETIC 12+12+12=36')
    for path in sorted(READS):
        print('READ_AUDIT ' + path + ' SHA256=' + sha(ROOT / path))
    print(f'READ_GUARD artifact_reads={len(READS)}; allowlisted_only={READS <= set(INPUTS)}; blocked_attempts={len(BLOCKED)}; no Test prediction/label file opened')
    assert sha(CSV) == selected_hash
    print('SHA256 reports/week10/random_sample_ids.csv ' + selected_hash)
    print('SHA256 reports/week10/reading_sheet_random.xlsx ' + sha(XLSX))
    print('FILE_LIST reports/week10/reading_sheet_random.xlsx (internal; git-ignored); reports/week10/random_sample_ids.csv (IDs and band only; committed); scripts/week10/random_reading.py; scripts/week10/reading_workbook.cjs; reports/week10/RESULTS_week10.md (append only); .gitignore (requested path appended)')


if __name__ == '__main__':
    sys.addaudithook(audit)
    old = DEST.read_bytes()
    heading = '## Part C: random Validation reading sample'
    assert heading.encode() not in old and (not XLSX.exists() or '--resume-export' in sys.argv), 'Refusing to overwrite Part C outputs'
    capture = io.StringIO()
    class Tee:
        def write(self, text):
            sys.__stdout__.write(text)
            capture.write(text)
        def flush(self):
            sys.__stdout__.flush()
    with contextlib.redirect_stdout(Tee()):
        main()
    with DEST.open('ab') as stream:
        stream.write(('\n\n' + heading + '\n\nCommand: `.venv/Scripts/python.exe -B -u scripts/week10/random_reading.py`; the completed export was resumed with `--resume-export` following a console encoding failure.\n\n```text\n' + capture.getvalue() + '```\n').encode('utf-8'))
    assert DEST.read_bytes().startswith(old)
    print('APPEND_PREFIX_UNCHANGED=True; prefix_sha256=' + hashlib.sha256(old).hexdigest())
