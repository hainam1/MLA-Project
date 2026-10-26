"""Create independent development-only packets; never print essay text."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / 'outputs/independent_readers_20261026'
TEMPLATE = ROOT / 'docs/templates/independent_reader_blank.xlsx'
RENDERER = Path(__file__).with_name('reader_packets.mjs')
SEED = 42
# Confirmed by the project owner in chat on 26/10/2026, after source clarification.
LOCKED = {'51DA4BA94C7C': 'Grammar', 'D1D770AF6855': 'Vocabulary',
          '4032ED0063E4': 'Grammar', '0FFB44B5D0C2': 'Vocabulary',
          '277A95AC0190': 'Grammar'}
FEATURES = ('word_count', 'sentence_count', 'mean_sentence_length', 'mtld', 'mattr',
            'mean_word_frequency', 'mean_word_length', 'lexical_density', 'noun_diversity',
            'detected_grammar_errors_per_100_words', 'detected_error_free_sentence_ratio',
            'complex_sentence_ratio', 'estimated_clauses_per_sentence', 'subordinate_clause_ratio')
CAUSES = ('công cụ đếm lỗi thiếu', 'bài ngắn', 'từ vựng/ý hay nhưng đặc trưng không đo',
          'lỗi ngữ pháp không được tính', 'bài lạc đề hoặc theo đề đặc biệt',
          'nghi điểm người chấm lệch', 'không giải thích được', 'khác (ghi rõ)')
SOURCES = ('data/03_clean_ready_to_use/validation_783.csv',
           'data/05_model_features/development_features_with_targets.csv',
           'outputs/phase6/validation_predictions.csv', 'reports/week9/t4_reading_summary.csv')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class PacketError(ValueError):
    """Diagnostics contain fixed messages and paths only."""


def require(condition, message):
    if not condition:
        raise PacketError(message)


def index_rows(relative, columns):
    """Explicit source allowlist and columns; values never enter diagnostics."""
    require(relative in SOURCES, 'Source outside development allowlist')
    with (ROOT / relative).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        require(set(columns) <= set(reader.fieldnames or []), f'Missing columns: {relative}')
        rows = {}
        for row in reader:
            eid = row['essay_id']
            if eid in LOCKED:
                require(eid not in rows, f'Duplicate ID: {relative}')
                rows[eid] = {k: row[k] for k in columns}
    require(set(rows) == set(LOCKED), f'Incomplete locked set: {relative}')
    return rows


def records():
    text = index_rows(SOURCES[0], ['essay_id', 'essay_text', 'prompt', 'vocabulary', 'grammar'])
    feat = index_rows(SOURCES[1], ['essay_id', 'split', 'source_partition', 'Vocabulary', 'Grammar', *FEATURES])
    pred = index_rows(SOURCES[2], ['essay_id', 'random_forest_vocabulary', 'random_forest_grammar',
                                  'ridge_vocabulary', 'ridge_grammar'])
    audit = index_rows(SOURCES[3], ['essay_id', 'y_V', 'y_G', 'RF_V', 'RF_G'])
    result = {}
    for eid, target in LOCKED.items():
        f, p, t, a = feat[eid], pred[eid], text[eid], audit[eid]
        require(f['split'] == 'validation' and f['source_partition'] == 'official_train',
                'Locked ID outside Validation development')
        require(bool(t['essay_text'].strip()), 'Missing essay text')
        numeric = {k: float(f[k]) for k in FEATURES}
        values = {k: float(p[k]) for k in p if k != 'essay_id'}
        for trait, short in [('Vocabulary', 'V'), ('Grammar', 'G')]:
            truth = float(f[trait])
            require(truth == float(t[trait.lower()]) == float(a['y_' + short]), 'Target mismatch')
            require(abs(values['random_forest_' + trait.lower()] - float(a['RF_' + short])) <= 1e-11,
                    'Stored RF predictions do not match audit source')
        require(float(f[target]) >= 4 and float(f[target])-values['random_forest_'+target.lower()] >= 1,
                'Confirmed target does not satisfy the locked criterion')
        result[eid] = dict(text=t['essay_text'], prompt=t['prompt'], target=target,
                           Vocabulary=float(f['Vocabulary']), Grammar=float(f['Grammar']),
                           features=numeric, predictions=values,
                           old_tool_first150_estimate=numeric['detected_grammar_errors_per_100_words']
                           * min(150, numeric['word_count']) / 100)
    return result


def render(payload):
    """Text travels only through an in-memory pipe; no text-bearing JSON or logs."""
    node = os.environ.get('READER_NODE') or shutil.which('node')
    if not node:
        node = str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
    proc = subprocess.run([node, str(RENDERER)], input=json.dumps(payload, ensure_ascii=True).encode(),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Do not echo dependency exceptions: they might contain a cell value.
    require(proc.returncode == 0, 'Workbook renderer failed; private stderr suppressed')


def require_ignored(path):
    result = subprocess.run(['git', 'check-ignore', '-q', '--', str(path)], cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    require(result.returncode == 0, 'Private output must be covered by .gitignore')


def create():
    paths = [PRIVATE/'doc_reader_A.xlsx', PRIVATE/'doc_reader_B.xlsx', PRIVATE/'reader_id_map.json']
    for path in paths:
        require_ignored(path)
        require(not path.exists(), 'Output exists; originals must not be overwritten')
    require(not TEMPLATE.exists(), 'Blank template already exists; do not overwrite')
    before = {s: sha(ROOT/s) for s in SOURCES}
    data = records()
    rng = random.Random(SEED)
    orders = {}
    for reader in ('A', 'B'):
        order = sorted(LOCKED)
        rng.shuffle(order)
        orders[reader] = order
    require(orders['A'] != orders['B'], 'Reader order must differ')
    PRIVATE.mkdir(parents=True, exist_ok=True)
    mapping = dict(schema_version=1, seed=SEED, group='điểm từ 4,0 trở lên ở đích bị sai',
                   confirmation='Five IDs explicitly confirmed by project owner, 26/10/2026',
                   source_sha256=before, readers={})
    # Render into a private staging area; only finalized workbooks are published.
    with tempfile.TemporaryDirectory(prefix='build_', dir=PRIVATE) as stage:
        stage = Path(stage)
        for reader in ('A', 'B'):
            items = [dict(data[eid], code=f'R{i+1}') for i, eid in enumerate(orders[reader])]
            render(dict(mode='packet', reader=reader, seed=SEED, causes=CAUSES, features=FEATURES,
                        items=items, output=str(stage/f'doc_reader_{reader}.xlsx')))
            mapping['readers'][reader] = {
                f'R{i+1}': dict(essay_id=eid, target=data[eid]['target'],
                               Vocabulary=data[eid]['Vocabulary'], Grammar=data[eid]['Grammar'])
                for i, eid in enumerate(orders[reader])}
        render(dict(mode='template', seed=SEED, causes=CAUSES, features=FEATURES,
                    items=[dict(code=f'R{i+1}', target='') for i in range(5)],
                    output=str(stage/'independent_reader_blank.xlsx'), preview_dir=str(stage/'previews')))
        verify_blank_packets(stage, data, mapping)
        require(before == {s: sha(ROOT/s) for s in SOURCES}, 'Source changed during creation')
        mapping['original_workbook_sha256'] = {
            r: sha(stage/f'doc_reader_{r}.xlsx') for r in ('A', 'B')}
        for reader in ('A', 'B'):
            (stage/f'doc_reader_{reader}.xlsx').rename(PRIVATE/f'doc_reader_{reader}.xlsx')
        TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
        (stage/'independent_reader_blank.xlsx').rename(TEMPLATE)
        shutil.copytree(stage/'previews', PRIVATE/'template_previews', dirs_exist_ok=False)
    (PRIVATE/'reader_id_map.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2)+'\n',
                                            encoding='utf-8')
    for reader, digest in mapping['original_workbook_sha256'].items():
        print(f'doc_reader_{reader}.xlsx SHA256={digest}')
    print('PASS: 5 confirmed development IDs; all reader inputs blank; ignored private files; no essay text printed.')


def verify_blank_packets(stage, data, mapping):
    from compare_readers import read_cells, input_layout
    for reader in ('A', 'B'):
        path = stage/f'doc_reader_{reader}.xlsx'
        needed = {sheet: refs for sheet, refs in input_layout().items()}
        cells = read_cells(path, needed)
        require(all(v in (None, '') for rows in cells.values() for v in rows.values()),
                'Reader fields must all remain blank')
        # Read only the essay cells for this internal equality check; never print them.
        import zipfile
        from compare_readers import sheet_cells
        essays = sheet_cells(path, 'Bài và điểm', None)
        for code, meta in mapping['readers'][reader].items():
            marker = f'{code} — '
            start = next(int(ref[1:]) for ref, value in essays.items()
                         if ref.startswith('A') and isinstance(value, str) and value.startswith(marker))
            chunks = []
            row = start + 4
            while f'A{row}' in essays and essays[f'A{row}'] not in ('', None):
                chunks.append(str(essays[f'A{row}']))
                row += 1
            require(''.join(chunks) == data[meta['essay_id']]['text'], 'Essay text completeness check failed')
        # No real IDs anywhere in the workbook, including model information.
        with zipfile.ZipFile(path) as z:
            blob = b''.join(z.read(n) for n in z.namelist() if n.endswith('.xml'))
        require(all(eid.encode() not in blob for eid in LOCKED), 'Real ID leaked into reader workbook')


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        create()
    except Exception as exc:
        # Error messages are constant or filenames, never underlying essay cell values.
        print('STOP: ' + (str(exc) if isinstance(exc, PacketError) else type(exc).__name__), file=sys.stderr)
        sys.exit(2)
