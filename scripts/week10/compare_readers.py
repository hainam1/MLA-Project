"""Compare submitted human annotations literally; never infer causes or print essays."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import posixpath
import re
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

from create_reader_packets import CAUSES, FEATURES, PRIVATE, ROOT, render, require_ignored

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
SHEETS = ['Hướng dẫn', 'Bài và điểm', 'Phần A', 'Thông tin mô hình', 'Phần B', 'Xác nhận']
COLUMNS = ['Mã bài', 'Từ vựng thật', 'Ngữ pháp thật', 'Nhận xét Phần A người A',
           'Nhận xét Phần B người A', 'Nhận xét Phần A người B', 'Nhận xét Phần B người B',
           'Nguyên nhân A', 'Nguyên nhân B', 'Đồng ý / khác nhau', 'Tự tin A / B']


def norm(value):
    return unicodedata.normalize('NFC', str(value)).strip()


def sheet_cells(path, sheet_name, wanted):
    """Read selected cells only; shared essay strings are not resolved for comparison."""
    with zipfile.ZipFile(path) as archive:
        book = ET.fromstring(archive.read('xl/workbook.xml'))
        sheets = book.find('s:sheets', NS)
        if [s.get('name') for s in sheets] != SHEETS:
            raise ValueError('Invalid sheet order or missing sheets')
        sheet = next(s for s in sheets if s.get('name') == sheet_name)
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        target = rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
        selected = [c for c in ET.fromstring(archive.read(target)).findall('.//s:sheetData/s:row/s:c', NS)
                    if wanted is None or c.get('r') in wanted]
        refs = {int(c.find('s:v', NS).text) for c in selected if c.get('t') == 's'}
        strings = {}
        if refs:
            with archive.open('xl/sharedStrings.xml') as stream:
                index = 0
                for _, element in ET.iterparse(stream, events=['end']):
                    if element.tag.endswith('}si'):
                        if index in refs:
                            strings[index] = ''.join(t.text or '' for t in element.iter()
                                                     if t.tag.endswith('}t'))
                        index += 1
                        element.clear()
                        if len(strings) == len(refs):
                            break
        result = {ref: None for ref in wanted} if wanted is not None else {}
        for cell in selected:
            ref = cell.get('r')
            if cell.find('s:f', NS) is not None:
                raise ValueError(f'Formula not accepted in selected field: {sheet_name}!{ref}')
            v = cell.find('s:v', NS)
            raw = None if v is None else v.text
            kind = cell.get('t')
            if kind == 's':
                value = strings[int(raw)]
            elif kind == 'inlineStr':
                value = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
            elif kind == 'b':
                value = raw == '1'
            elif kind == 'str':
                value = raw
            elif raw is not None:
                value = float(raw)
            else:
                value = None
            result[ref] = value
        return result


def read_cells(path, needed):
    return {sheet: sheet_cells(path, sheet, refs) for sheet, refs in needed.items()}


def input_layout():
    part = [f'B{5+7*i+j}' for i in range(5) for j in range(1, 5)]
    return {'Phần A': part, 'Phần B': part, 'Xác nhận': [f'B{i}' for i in range(5, 11)]}


def validate_mapping(mapping):
    if mapping.get('schema_version') != 1 or set(mapping.get('readers', {})) != {'A', 'B'}:
        raise ValueError('Invalid mapping version/readers')
    sets = []
    for role in ('A', 'B'):
        rows = mapping['readers'][role]
        if set(rows) != {f'R{i}' for i in range(1, 6)}:
            raise ValueError('Mapping must have exactly R1..R5 for each reader')
        ids = [r['essay_id'] for r in rows.values()]
        if len(set(ids)) != 5:
            raise ValueError('Mapping has duplicate real IDs')
        sets.append(set(ids))
    if sets[0] != sets[1]:
        raise ValueError('Reader mappings do not cover the same five essays')
    for eid in sets[0]:
        a, b = [next(r for r in mapping['readers'][role].values() if r['essay_id'] == eid) for role in ('A', 'B')]
        if a != b:
            raise ValueError('Targets or target identity differ between reader mappings')


def parse_causes(value, location):
    text = norm(value)
    if not re.fullmatch(r'[1-8](?:\s*[,;]\s*[1-8])*', text):
        raise ValueError('Invalid cause codes: '+location)
    return frozenset(int(x) for x in re.split(r'\s*[,;]\s*', text))


def read_submission(path, role, mapping):
    needed = input_layout()
    fields = read_cells(path, needed)
    missing = [f'{role}:{sheet}!{ref}' for sheet, cells in fields.items()
               for ref, value in cells.items() if value is None or norm(value) == '']
    # Collect every blank input first, without printing the values of other cells.
    errors = list(missing)
    confirm = fields['Xác nhận']
    if confirm.get('B9') not in (True, '☑'):
        errors.append(f'{role}:Xác nhận!B9 (thiếu xác nhận độc lập)')
    identity = sheet_cells(path, 'Hướng dẫn', ['A2'])['A2']
    if identity != 'Phiếu đọc độc lập — người '+role:
        errors.append(f'{role}:Hướng dẫn!A2 (không đúng file người đọc)')
    times = []
    for ref in ('B6', 'B7', 'B8'):
        try:
            dt = datetime.fromisoformat(norm(confirm[ref]))
            times.append(dt.replace(tzinfo=timezone(timedelta(hours=7))) if dt.tzinfo is None else dt)
        except (ValueError, TypeError):
            errors.append(f'{role}:Xác nhận!{ref} (thời gian không hợp lệ)')
    if len(times) == 3 and not times[0] <= times[1] <= times[2]:
        errors.append(f'{role}:Xác nhận!B6:B8 (thứ tự thời gian không hợp lệ)')
    rows = {}
    for i in range(5):
        row, code = 5+7*i, f'R{i+1}'
        for part in ('Phần A', 'Phần B'):
            header = sheet_cells(path, part, [f'A{row}'])[f'A{row}']
            if not isinstance(header, str) or not header.startswith(code+' — '):
                errors.append(f'{role}:{part}!A{row} (mã tạm bị sửa/thiếu)')
        a = [fields['Phần A'][f'B{row+j}'] for j in range(1, 5)]
        b = [fields['Phần B'][f'B{row+j}'] for j in range(1, 5)]
        if a[0] not in ('hợp lý', 'hơi cao', 'hơi thấp', 'không chắc'):
            errors.append(f'{role}:Phần A!B{row+1} (lựa chọn không hợp lệ)')
        try:
            count = float(a[2])
            if count < 0 or not count.is_integer():
                raise ValueError()
        except (ValueError, TypeError, OverflowError):
            errors.append(f'{role}:Phần A!B{row+3} (số lỗi phải là số nguyên ≥0)')
        if b[0] not in ('dự đoán thấp hơn điểm thật ở Từ vựng', 'dự đoán thấp hơn điểm thật ở Ngữ pháp', 'cả hai', 'khác'):
            errors.append(f'{role}:Phần B!B{row+1} (lựa chọn không hợp lệ)')
        if b[2] not in ('cao', 'vừa', 'thấp'):
            errors.append(f'{role}:Phần B!B{row+3} (mức tự tin không hợp lệ)')
        try:
            causes = parse_causes(b[1], f'{role}:Phần B!B{row+2}')
            if 8 in causes and (not isinstance(b[3], str) or not norm(b[3]).startswith('Khác:')):
                errors.append(f'{role}:Phần B!B{row+4} (chọn 8 cần giải thích bắt đầu Khác:)')
        except ValueError:
            causes = frozenset()
            errors.append(f'{role}:Phần B!B{row+2} (mã nguyên nhân không hợp lệ)')
        meta = mapping['readers'][role][code]
        rows[meta['essay_id']] = dict(a=a, b=b, causes=causes, meta=meta)
    return rows, confirm, errors


def compare(a_path, b_path, mapping):
    validate_mapping(mapping)
    a, ac, ae = read_submission(a_path, 'A', mapping)
    b, bc, be = read_submission(b_path, 'B', mapping)
    errors = ae+be
    if ac.get('B5') and bc.get('B5') and norm(ac['B5']).casefold() == norm(bc['B5']).casefold():
        errors.append('Xác nhận!B5: hai người đọc phải là hai thành viên khác nhau')
    if errors:
        raise ValueError('THIẾU / KHÔNG HỢP LỆ:\n'+'\n'.join(dict.fromkeys(errors)))
    rows = []
    for eid in sorted(a):
        ra, rb = a[eid], b[eid]
        sa, sb = ra['causes'], rb['causes']
        agreement = 'giống nhau hoàn toàn' if sa == sb else 'một phần' if sa & sb else 'khác'
        def summary_a(r):
            return '\n'.join([str(r['a'][0]), 'Lý do: '+str(r['a'][1]),
                              'Lỗi 150 từ: '+str(r['a'][2]), 'Từ vựng: '+str(r['a'][3])])
        def summary_b(r):
            return str(r['b'][0])+'\n'+str(r['b'][3])
        label = lambda codes: '; '.join(CAUSES[i-1] for i in sorted(codes))
        rows.append([eid, ra['meta']['Vocabulary'], ra['meta']['Grammar'], summary_a(ra), summary_b(ra),
                     summary_a(rb), summary_b(rb), label(sa), label(sb), agreement,
                     str(ra['b'][2])+' / '+str(rb['b'][2])])
    return rows


def export(rows, out):
    out = Path(out)
    if out.with_suffix('.md').exists() or out.with_suffix('.xlsx').exists():
        raise ValueError('Comparison output exists; refusing to overwrite')
    def escape(v):
        return str(v).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '\\|').replace('\n', '<br>')
    content = ['# So sánh hai bản đọc độc lập', '',
               'Phân loại chỉ dựa trên tập mã nguyên nhân do người đọc chọn; không suy luận nguyên nhân.', '',
               '| '+' | '.join(COLUMNS)+' |', '|'+'---|'*len(COLUMNS)]
    content.extend('| '+' | '.join(escape(v) for v in row)+' |' for row in rows)
    render(dict(mode='comparison', columns=COLUMNS, rows=rows, output=str(out.with_suffix('.xlsx'))))
    out.with_suffix('.md').write_text('\n'.join(content)+'\n', encoding='utf-8')


def self_test():
    """All fixtures are synthetic and removed when the temporary context closes."""
    with tempfile.TemporaryDirectory(prefix='FAKE_reader_comparison_') as temp:
        temp = Path(temp)
        mapping = dict(schema_version=1, readers={})
        fixtures = {}
        for role, order in [('A', [1, 2, 3, 4, 5]), ('B', [3, 5, 1, 4, 2])]:
            mapping['readers'][role] = {f'R{i+1}': dict(essay_id=f'FAKE{n}', target='Vocabulary', Vocabulary=4.5, Grammar=4)
                                       for i, n in enumerate(order)}
            responses = {'Phần A': {}, 'Phần B': {}, 'Xác nhận': dict(zip(
                [f'B{i}' for i in range(5, 11)], ['FAKE person '+role, '2026-10-26 08:00', '2026-10-26 08:30',
                                                '2026-10-26 09:00', '☑', 'FAKE signature '+role]))}
            for i, n in enumerate(order):
                row = 5+7*i
                for j, value in enumerate(['hợp lý', 'FAKE reason.', 0, 'FAKE vocabulary.'], 1):
                    responses['Phần A'][f'B{row+j}'] = value
                causes = '1;2' if role == 'A' else {1:'2;1', 2:'2;3', 3:'4', 4:'1;2', 5:'1;2'}[n]
                for j, value in enumerate(['cả hai', causes, 'vừa', 'FAKE note.'], 1):
                    responses['Phần B'][f'B{row+j}'] = value
            items = [dict(code=f'R{i+1}', target='Vocabulary', Vocabulary=4.5, Grammar=4) for i in range(5)]
            fixtures[role] = dict(mode='fixture', synthetic_data=True, reader=role, seed=42, features=FEATURES,
                                  causes=CAUSES, items=items, responses=responses, output=str(temp/f'{role}.xlsx'))
            render(fixtures[role])
        rows = compare(temp/'A.xlsx', temp/'B.xlsx', mapping)
        assert [r[9] for r in rows[:3]] == ['giống nhau hoàn toàn', 'một phần', 'khác']
        assert rows[0][3].endswith('FAKE vocabulary.') and rows[0][0] == 'FAKE1'
        export(rows, temp/'FAKE_comparison')
        # Create actual missing cells in a separate synthetic workbook, never in real packets.
        bad = json.loads(json.dumps(fixtures['A']))
        bad['output'] = str(temp/'FAKE_missing.xlsx')
        bad['responses']['Phần A']['B7'] = None
        bad['responses']['Xác nhận']['B9'] = None
        render(bad)
        try:
            compare(temp/'FAKE_missing.xlsx', temp/'B.xlsx', mapping)
        except ValueError as exc:
            assert 'A:Phần A!B7' in str(exc) and 'A:Xác nhận!B9' in str(exc)
        else:
            raise AssertionError('Missing entries accepted')
        # A complete A submission with an absent independence tick also must stop.
        bad['output'] = str(temp/'FAKE_no_confirmation.xlsx')
        bad['responses']['Phần A']['B7'] = 'FAKE reason.'
        render(bad)
        try:
            compare(temp/'FAKE_no_confirmation.xlsx', temp/'B.xlsx', mapping)
        except ValueError as exc:
            assert 'A:Xác nhận!B9' in str(exc)
        else:
            raise AssertionError('Absent independent confirmation accepted')
    assert not temp.exists()
    print('PASS: DỮ LIỆU GIẢ — mapping with different orders; exact/partial/different causes; missing inputs stop; fake files removed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--a', type=Path, default=PRIVATE/'doc_reader_A.xlsx')
    parser.add_argument('--b', type=Path, default=PRIVATE/'doc_reader_B.xlsx')
    parser.add_argument('--map', type=Path, default=PRIVATE/'reader_id_map.json')
    parser.add_argument('--out', type=Path, default=PRIVATE/'reader_comparison')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    require_ignored(args.out.with_suffix('.md'))
    require_ignored(args.out.with_suffix('.xlsx'))
    mapping = json.loads(args.map.read_text(encoding='utf-8'))
    rows = compare(args.a, args.b, mapping)
    export(rows, args.out)
    print('PASS: compared five submitted entries; no essay text or reader response printed.')


if __name__ == '__main__':
    try:
        main()
    except ValueError as exc:
        print('STOP: '+str(exc), file=sys.stderr)
        sys.exit(2)
    except Exception as exc:
        print('STOP: '+type(exc).__name__+' (cell values suppressed)', file=sys.stderr)
        sys.exit(2)
