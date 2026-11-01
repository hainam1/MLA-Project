"""Summarise human readings of the locked Week 10 set A, without printing text.

Run: .venv/Scripts/python.exe -B scripts/week10/unexplained_summary.py
Checks: same command with --check or --self-test. No fitting or data search.
"""
from pathlib import Path
from collections import Counter
from decimal import Decimal, InvalidOperation
import argparse
import io
import json
import os
import posixpath
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / 'reports/week10/five_unexplained_sheet.xlsx'
SET_A_IDS = ('51DA4BA94C7C', 'D1D770AF6855', '4032ED0063E4',
             '0FFB44B5D0C2', '277A95AC0190')
READERS = ('A', 'B')
SUFFIXES = ('cause_group', 'rubric_evidence_position', 'notes', 'name', 'submitted_at')
HUMAN = tuple(f'reader{r}_{s}' for r in READERS for s in SUFFIXES)
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def column_number(reference):
    result = 0
    for char in reference.rstrip('0123456789'):
        result = result * 26 + ord(char) - ord('A') + 1
    return result


def shared_values(archive, needed):
    """Resolve only selected strings; essay text is never requested."""
    values = {}
    if not needed:
        return values
    with archive.open('xl/sharedStrings.xml') as stream:
        index = 0
        for _, element in ET.iterparse(stream, events=['end']):
            if element.tag.endswith('}si'):
                if index in needed:
                    values[index] = ''.join(t.text or '' for t in element.iter()
                                            if t.tag.endswith('}t'))
                index += 1
                element.clear()
                if len(values) == len(needed):
                    break
    if set(values) != needed:
        raise ValueError('MISSING_SHARED_STRINGS')
    return values


def selected_values(archive, cells):
    refs = {int(c.find('s:v', NS).text) for c in cells if c.get('t') == 's'}
    strings = shared_values(archive, refs)
    output = {}
    for cell in cells:
        if cell.find('s:f', NS) is not None:
            raise ValueError('FORMULA_IN_READER_INPUT_OR_ID: cell=' + cell.get('r', ''))
        if cell.get('t') == 's':
            value = strings[int(cell.find('s:v', NS).text)]
        elif cell.get('t') == 'inlineStr':
            value = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
        else:
            node = cell.find('s:v', NS)
            value = '' if node is None else node.text or ''
        output[column_number(cell.get('r'))] = value
    return output


def read_sheet(source):
    with zipfile.ZipFile(source) as archive:
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheets = workbook.find('s:sheets', NS)
        matches = [s for s in sheets if s.get('name') == 'reading_sheet']
        if len(matches) != 1:
            raise ValueError('EXPECTED_ONE_READING_SHEET')
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(
            archive.read('xl/_rels/workbook.xml.rels'))}
        target = rels[matches[0].get(
            '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        rows = ET.fromstring(archive.read(target)).findall('s:sheetData/s:row', NS)
        if not rows:
            raise ValueError('EMPTY_READING_SHEET')
        header_map = selected_values(archive, list(rows[0]))
        names = list(header_map.values())
        if len(names) != len(set(names)):
            raise ValueError('DUPLICATE_HEADERS')
        required = {'essay_id', *HUMAN}
        if required - set(names):
            raise ValueError('MISSING_HEADERS: ' + ','.join(sorted(required - set(names))))
        selected = {column: name for column, name in header_map.items() if name in required}
        result = []
        for row in rows[1:]:
            cells = [c for c in row if column_number(c.get('r')) in selected]
            values = selected_values(archive, cells)
            record = {name: str(values.get(column, '')).strip()
                      for column, name in selected.items()}
            if any(record.values()):
                result.append(record)
    return names, result


def validate_ids(records, expected_ids):
    actual = [r.get('essay_id', '') for r in records]
    if len(actual) != len(expected_ids) or len(set(actual)) != len(actual) or set(actual) != set(expected_ids):
        raise ValueError('EXPECTED_EXACT_LOCKED_IDS_WITHOUT_DUPLICATES')


def category(value, essay_id, reader):
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f'INVALID_CAUSE_GROUP: reader={reader}; essay_id={essay_id}') from None
    if not number.is_finite() or number != number.to_integral_value() or not 1 <= number <= 6:
        raise ValueError(f'INVALID_CAUSE_GROUP: reader={reader}; essay_id={essay_id}')
    return int(number)


def summarise(records, expected_ids=SET_A_IDS):
    validate_ids(records, expected_ids)
    indexed = {r['essay_id']: r for r in records}
    submitted, statuses = {}, {}
    for reader in READERS:
        prefix = 'reader' + reader + '_'
        is_submitted = any(indexed[e].get(prefix + 'submitted_at', '').strip() for e in expected_ids)
        started = any(indexed[e].get(prefix + s, '').strip()
                      for e in expected_ids for s in SUFFIXES)
        if not is_submitted:
            statuses[reader] = 'DRAFT_NOT_SUBMITTED' if started else 'NOT_STARTED'
            continue
        missing = [(e, prefix + s) for e in expected_ids for s in SUFFIXES
                   if not indexed[e].get(prefix + s, '').strip()]
        if missing:
            raise ValueError('INCOMPLETE_SUBMITTED_READER: reader=' + reader + '; missing=' +
                             ','.join(e + ':' + field for e, field in missing))
        if len({indexed[e][prefix + 'name'].strip() for e in expected_ids}) != 1:
            raise ValueError('INCONSISTENT_READER_NAME: reader=' + reader)
        submitted[reader] = {e: category(indexed[e][prefix + 'cause_group'], e, reader)
                             for e in expected_ids}
        statuses[reader] = 'COMPLETE_SUBMITTED'
    if not submitted:
        raise ValueError('WAITING_FOR_HUMAN_READERS: neither reader has submitted all five cases; no result computed')
    result = {'n_essays': len(expected_ids), 'reader_status': statuses, 'readers': {}}
    for reader, groups in submitted.items():
        counts = Counter(groups.values())
        result['readers'][reader] = {
            'n': len(groups), 'cause_counts': {str(i): counts[i] for i in range(1, 7)},
            'group5_ids': [e for e in expected_ids if groups[e] == 5]}
    if len(submitted) == 2:
        pairs = [(e, submitted['A'][e], submitted['B'][e]) for e in expected_ids]
        same = sum(a == b for _, a, b in pairs)
        result['agreement'] = {'computed': True, 'same': same, 'n': len(pairs),
                               'arithmetic': f'{same}/{len(pairs)}={same / len(pairs):.17g}'}
        result['paired_groups'] = pairs
    else:
        result['agreement'] = {'computed': False, 'reason': 'ONE_READER_ONLY; no two-reader agreement computed'}
    result['group5_union_ids'] = [e for e in expected_ids
                                  if any(groups[e] == 5 for groups in submitted.values())]
    return result


def print_result(result, label):
    print(label)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('TEXT_OUTPUT_CHECK essay_text=NOT_PRINTED; evidence=NOT_PRINTED; notes=NOT_PRINTED; names=NOT_PRINTED')


def synthetic_book(records):
    """Minimal in-memory OOXML fixture; no synthetic or real sheet is written."""
    root = ET.Element('worksheet', xmlns=NS['s'])
    data = ET.SubElement(root, 'sheetData')
    fields = ['essay_id', *HUMAN]
    def letter(index):
        text = ''
        while index:
            index, rem = divmod(index - 1, 26)
            text = chr(65 + rem) + text
        return text
    for row_number, values in enumerate([fields] + [[r.get(k, '') for k in fields] for r in records], 1):
        row = ET.SubElement(data, 'row', r=str(row_number))
        for col, value in enumerate(values, 1):
            if value == '':
                continue
            c = ET.SubElement(row, 'c', r=letter(col) + str(row_number), t='inlineStr')
            ET.SubElement(ET.SubElement(c, 'is'), 't').text = str(value)
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, 'w') as z:
        z.writestr('xl/workbook.xml', '<workbook xmlns="' + NS['s'] + '" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="reading_sheet" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/></Relationships>')
        z.writestr('xl/worksheets/sheet1.xml', ET.tostring(root))
    payload.seek(0)
    return payload


def self_test():
    print('SYNTHETIC ONLY; no real workbook, essay or reader values loaded')
    ids = tuple(f'SYNTHETIC_{i:02d}' for i in range(1, 6))
    rows = []
    groups = {'A': [1, 2, 5, 6, 3], 'B': [1, 3, 5, 6, 4]}
    for i, essay_id in enumerate(ids):
        record = {'essay_id': essay_id}
        for r in READERS:
            vals = [str(groups[r][i]), 'SYNTHETIC rubric and position',
                    'SYNTHETIC note', 'SYNTHETIC reader ' + r,
                    'SYNTHETIC 2026-01-01T12:00:00+07:00']
            record.update({f'reader{r}_{s}': v for s, v in zip(SUFFIXES, vals)})
        rows.append(record)
    _, parsed = read_sheet(synthetic_book(rows))
    result = summarise(parsed, ids)
    assert result['agreement']['same'] == 3 and result['agreement']['n'] == 5
    assert result['readers']['A']['cause_counts'] == {'1': 1, '2': 1, '3': 1, '4': 0, '5': 1, '6': 1}
    assert result['readers']['B']['cause_counts'] == {'1': 1, '2': 0, '3': 1, '4': 1, '5': 1, '6': 1}
    assert result['group5_union_ids'] == ['SYNTHETIC_03']
    print_result(result, 'SYNTHETIC complete two-reader fixture')
    print('PASS SYNTHETIC two readers; same=3/5=0.6; group5_union=SYNTHETIC_03')
    one = [dict(r) for r in rows]
    for row in one:
        for s in SUFFIXES:
            row['readerB_' + s] = ''
    _, parsed = read_sheet(synthetic_book(one))
    assert not summarise(parsed, ids)['agreement']['computed']
    print('PASS SYNTHETIC one reader; agreement=NOT_COMPUTED')
    for name, alter in [
        ('missing submitted-reader note', lambda r: r[0].update(readerA_notes='')),
        ('invalid group', lambda r: r[0].update(readerA_cause_group='7')),
        ('duplicate ID', lambda r: r[0].update(essay_id=ids[1])),
    ]:
        bad = [dict(r) for r in rows]
        alter(bad)
        try:
            _, parsed = read_sheet(synthetic_book(bad))
            summarise(parsed, ids)
        except ValueError as error:
            print('PASS SYNTHETIC rejected ' + name + ': ' + str(error))
        else:
            raise AssertionError('Synthetic invalid input was accepted')
    blank = [{'essay_id': e, **{k: '' for k in HUMAN}} for e in ids]
    try:
        summarise(blank, ids)
    except ValueError as error:
        assert str(error).startswith('WAITING_FOR_HUMAN_READERS')
        print('PASS SYNTHETIC blank sheet; no result fabricated')
    else:
        raise AssertionError('Synthetic blank sheet was accepted')
    print('SYNTHETIC_SELF_TEST_PASS=6/6; synthetic workbook data stayed in memory')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--check', action='store_true', help='Check real sheet structure/blanks without computing human results')
    args = parser.parse_args()
    print('READ_AUDIT scripts/week10/unexplained_summary.py')
    if args.self_test:
        self_test()
        return 0
    print('READ_AUDIT reports/week10/five_unexplained_sheet.xlsx')
    headers, records = read_sheet(SHEET)
    validate_ids(records, SET_A_IDS)
    print('READ_COLUMNS=' + json.dumps(['essay_id', *HUMAN], ensure_ascii=False))
    if args.check:
        nonempty = {key: sum(bool(r.get(key, '').strip()) for r in records) for key in HUMAN}
        print('SHEET_NAMES_EXPECTED=reading_sheet,cause_groups')
        print('HEADERS=' + json.dumps(headers, ensure_ascii=False))
        print('N_ESSAYS=5; UNIQUE_LOCKED_IDS=5')
        print('HUMAN_NONEMPTY_COUNTS=' + json.dumps(nonempty))
        print('CAUSE_CELLS_NONEMPTY=' + str(sum(nonempty[f'reader{r}_cause_group'] for r in READERS)) + '/10')
        print('CHECK_ONLY=True; human results not computed; essay text not printed')
        return 0
    print_result(summarise(records), 'EXPLORATORY HUMAN READING SUMMARY')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ValueError as error:
        print('ERROR ' + str(error))
        raise SystemExit(2)
