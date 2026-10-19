"""Read-only reader agreement, or an explicitly synthetic in-memory self-test.

Run after the second reader fills reader2_sheet.xlsx. Blank counts stop the
script before the mapping or first-reader workbook is opened.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import os
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / 'reports/week10/reader2_sheet.xlsx'
MAPPING = ROOT / 'reports/week10/reader2_id_map.csv'
READER1 = ROOT / 'reports/week10/reading_sheet_da_danh_gia.xlsx'
IDS = ROOT / 'reports/week10/random_sample_ids.csv'
HEADERS = ['essay_id', 'first150_words', 'reader2_errors_first150', 'notes']
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
READS, ALLOWED = set(), {SHEET.resolve(), MAPPING.resolve(), READER1.resolve(), IDS.resolve()}


def choose_sample():
    """IDs/bands only; seeded selection and independently shuffled reading order."""
    assert hashlib.sha256(IDS.read_bytes()).hexdigest() == '8472794fb01eae511da497577b312bfdc0e4181c7b67eb860b610f83fcae0818'
    with IDS.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ['essay_id', 'band']
        population = list(reader)
    assert len(population) == 36 and len({r['essay_id'] for r in population}) == 36
    rng = np.random.default_rng(2026)
    selected = []
    for band in ['<2.5', '2.5-4.0', '>4.0']:
        pool = sorted(r['essay_id'] for r in population if r['band'] == band)
        assert len(pool) == 12
        for essay_id in rng.choice(pool, size=2, replace=False):
            selected.append(dict(essay_id=str(essay_id), band=band, selection_index=len(selected)+1))
    canonical = ('\n'.join(r['essay_id'] for r in selected)+'\n').encode('ascii')
    digest = hashlib.sha256(canonical).hexdigest()
    order = np.random.default_rng(2026).permutation(6)
    mapping = [dict(anonymous_id=f'r2_{i:02}', **selected[j]) for i, j in enumerate(order, 1)]
    return selected, mapping, digest


def audit(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return
    if not rel.parts or rel.parts[0] not in {'reports', 'data', 'outputs', 'docs'}:
        return
    mode = args[1]
    if path not in ALLOWED or (isinstance(mode, str) and any(c in mode for c in 'wax+')):
        raise PermissionError('Read-only artifact outside allowlist: ' + rel.as_posix())
    READS.add(rel.as_posix())


def xlsx_fields(path, sheet_name, keep):
    """Resolve only requested cell fields, never essay-text values for agreement."""
    with zipfile.ZipFile(path) as z:
        strings = ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS) if 'xl/sharedStrings.xml' in z.namelist() else []
        def value(cell):
            v = cell.find('s:v', NS)
            v = v.text if v is not None else ''
            if cell.attrib.get('t') == 's':
                return ''.join(strings[int(v)].itertext())
            if cell.attrib.get('t') == 'inlineStr':
                return ''.join(cell.find('s:is', NS).itertext())
            return v
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets = ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS)
        selected = [s for s in sheets if s.attrib['name'] == sheet_name]
        if len(selected) != 1:
            raise ValueError('Required sheet missing or ambiguous: ' + sheet_name)
        sheet = selected[0]
        target = rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        rows = ET.fromstring(z.read(member)).findall('s:sheetData/s:row', NS)
        if not rows:
            raise ValueError('Required sheet is empty')
        header = {re.sub(r'\d', '', c.attrib['r']): value(c).strip() for c in rows[0].findall('s:c', NS)}
        records = []
        for row in rows[1:]:
            record = {}
            for cell in row.findall('s:c', NS):
                key = header.get(re.sub(r'\d', '', cell.attrib['r']))
                if key in keep:
                    if cell.find('s:f', NS) is not None:
                        raise ValueError('Count/ID fields must be saved values, not formulas')
                    record[key] = str(value(cell)).strip()
            if record.get('essay_id'):
                records.append(record)
        return list(header.values()), records


def count_value(value):
    if value is None or str(value).strip() == '':
        raise ValueError('Blank count; waiting for human reader')
    try:
        numeric = float(value)
    except (ValueError, TypeError):
        raise ValueError('Count must be a nonnegative integer') from None
    if not np.isfinite(numeric) or numeric < 0 or numeric != np.floor(numeric):
        raise ValueError('Count must be a nonnegative integer')
    return int(numeric)


def agreement(ids, reader1, reader2, label):
    if len(ids) != 6 or len(set(ids)) != 6 or len(reader1) != 6 or len(reader2) != 6:
        raise ValueError('Exactly six unique paired essays are required')
    a = np.array([count_value(v) for v in reader1], dtype=float)
    b = np.array([count_value(v) for v in reader2], dtype=float)
    delta = b-a
    absolute = abs(delta)
    print(label)
    print('PAIR_DIFFERENCE_DEFINITION reader2-reader1')
    print('anonymous_id,reader1,reader2,difference,absolute_difference')
    for code, av, bv, d, ad in zip(ids, a, b, delta, absolute):
        print(f'{code},{int(av)},{int(bv)},{int(d)},{int(ad)}')
    print(f'N=6; mean_absolute_difference={absolute.mean():.17g}; arithmetic={absolute.sum():.17g}/6={absolute.mean():.17g}')
    print(f'BIAS_reader2_minus_reader1={delta.mean():.17g}; arithmetic={delta.sum():.17g}/6={delta.mean():.17g}')
    print(f'ABS_DIFFERENCE_GE_2={int((absolute >= 2).sum())}; arithmetic={int((absolute >= 2).sum())}/6={(absolute >= 2).mean():.17g}')
    for name, x, y in [('Pearson', a, b), ('Spearman', rankdata(a), rankdata(b))]:
        x, y = x-x.mean(), y-y.mean()
        xy, xx, yy = float(np.dot(x, y)), float(np.dot(x, x)), float(np.dot(y, y))
        if xx == 0 or yy == 0:
            print(name + '=UNDEFINED; constant counts or ranks; n=6, reference only')
        else:
            rho = xy/np.sqrt(xx*yy)
            direct = np.corrcoef(a, b)[0, 1] if name == 'Pearson' else spearmanr(a, b).statistic
            assert np.isclose(rho, direct, rtol=0, atol=1e-14)
            print(f'{name}={rho:.17g}; arithmetic={xy:.17g}/sqrt({xx:.17g}*{yy:.17g})={rho:.17g}; n=6, reference only (chi de tham khao)')
    return dict(n=6, sum_absolute_difference=int(absolute.sum()), bias=float(delta.mean()),
                absolute_difference_ge_2=int((absolute >= 2).sum()))


def self_test():
    print('SYNTHETIC SELF-TEST ONLY: fixed artificial numbers; no real essay, reader sheet, mapping or reader1 count is read. These are not human results.')
    result = agreement([f'synthetic_{i:02}' for i in range(1, 7)], [2, 5, 8, 11, 14, 17], [3, 3, 8, 14, 13, 19], 'SYNTHETIC_PAIRS')
    assert result == dict(n=6, sum_absolute_difference=9, bias=.5, absolute_difference_ge_2=3)
    print('PASS synthetic_expected_arithmetic: sum_abs=9; mean_abs=9/6=1.5; sum_difference=3; bias=3/6=0.5; abs_difference_ge_2=3/6=0.5')
    for name, values in [('blank', [3, None, 8, 14, 13, 19]), ('negative', [3, -1, 8, 14, 13, 19]),
                         ('fractional', [3, 1.5, 8, 14, 13, 19])]:
        try:
            [count_value(v) for v in values]
        except ValueError:
            print('PASS synthetic_' + name + '_count_rejected=True')
        else:
            raise AssertionError('Invalid synthetic count accepted')


def real_agreement():
    headers, second = xlsx_fields(SHEET, 'reader2', {'essay_id', 'reader2_errors_first150'})
    if headers != HEADERS:
        raise ValueError('Reader2 sheet must retain exactly the four approved columns')
    if len(second) != 6 or len({r['essay_id'] for r in second}) != 6:
        raise ValueError('Reader2 sheet must contain exactly six unique anonymous IDs')
    missing = [r['essay_id'] for r in second if not r.get('reader2_errors_first150', '').strip()]
    if missing:
        raise ValueError('WAITING_FOR_READER2: blank reader2_errors_first150 for ' + ','.join(missing) + '; reader1 workbook not opened')
    for row in second:
        count_value(row['reader2_errors_first150'])
    with MAPPING.open(encoding='utf-8-sig', newline='') as stream:
        mapping = list(csv.DictReader(stream))
    if len(mapping) != 6 or len({r['anonymous_id'] for r in mapping}) != 6 or len({r['essay_id'] for r in mapping}) != 6:
        raise ValueError('Mapping must contain six unique IDs on each side')
    if {r['anonymous_id'] for r in mapping} != {r['essay_id'] for r in second}:
        raise ValueError('Anonymous IDs do not match the locked mapping')
    _, expected_mapping, digest = choose_sample()
    expected = {r['anonymous_id']: (r['essay_id'], r['band'], r['selection_index']) for r in expected_mapping}
    observed = {r['anonymous_id']: (r['essay_id'], r['band'], int(r['selection_index'])) for r in mapping}
    if observed != expected:
        raise ValueError('Mapping differs from the locked seed-2026 selection and order')
    print('LOCKED_SELECTION_AND_MAPPING_VERIFIED=True; selected_ID_list_SHA256=' + digest)
    actual = {r['anonymous_id']: r['essay_id'] for r in mapping}
    _, first = xlsx_fields(READER1, 'reading_sheet', {'essay_id', 'Số lỗi ngữ pháp (150 từ đầu)', 'reader_errors_first150'})
    if len({r['essay_id'] for r in first}) != len(first):
        raise ValueError('Duplicate IDs in first-reader workbook')
    lookup = {r['essay_id']: r for r in first}
    ids, a, b = [], [], []
    for row in second:
        anonymous = row['essay_id']
        source = lookup.get(actual[anonymous])
        if source is None:
            raise ValueError('A selected ID is missing from the first-reader workbook')
        available = [source[k] for k in ['Số lỗi ngữ pháp (150 từ đầu)', 'reader_errors_first150'] if k in source]
        if len(available) != 1:
            raise ValueError('First-reader count header is missing or ambiguous')
        ids.append(anonymous)
        a.append(available[0])
        b.append(row['reader2_errors_first150'])
    agreement(ids, a, b, 'REAL_HUMAN_COUNTS (only after both readers have filled their own counts)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    sys.addaudithook(audit)
    status = 0
    try:
        self_test() if args.self_test else real_agreement()
    except (ValueError, FileNotFoundError) as error:
        print('ERROR ' + str(error), file=sys.stderr)
        status = 2
    finally:
        for path in sorted(READS):
            print('READ_AUDIT ' + path)
        print(f'READ_GUARD artifact_reads={len(READS)}; allowlisted_only=True; no Test file opened; read_only=True; reader1_not_opened={READER1.relative_to(ROOT).as_posix() not in READS}; no essay text printed.')
    raise SystemExit(status)
