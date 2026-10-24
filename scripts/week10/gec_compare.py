"""Exploratory development-only GECToR/ERRANT comparison; no frozen writes.

Run --preregister, then --benchmark. The four-hour gate precedes the full run.
Essay strings exist in memory only. Counts are resumable, git-ignored JSONL.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import csv
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/week10'
MODEL = 'gotutiyan/gector-roberta-base-5k'
REVISION = 'adaac6fb919431fb5a038b1e449055ae638613a4'
INPUTS = (
    'reports/week9/t3_eligible_development.csv',
    'reports/week9/t3_fold_composition.csv',
    'reports/week9/t4_reading_summary.csv',
    'data/03_clean_ready_to_use/model_train_3128.csv',
    'data/03_clean_ready_to_use/validation_783.csv',
    'outputs/phase6/feature_schema.json',
    'outputs/phase6/validation_predictions.csv',
    'reports/week10/random_sample_ids.csv',
    'reports/week10/reading_sheet_da_danh_gia.xlsx',
)
CONFIG = {
    'status': 'exploratory; development only; no Test or combined corpus',
    'seed': 42, 'model': MODEL, 'revision': REVISION,
    'resources': {'verb_revision': '4ad259f25c6bb408a99788d468cd8958845e647e',
                  'verb_sha256': '5906804ec8a1acd8cbfc2918522bf429ce5edded8bbc46ffc2be861d280d3abf',
                  'base_encoder': 'FacebookAI/roberta-base',
                  'base_revision': 'e2da8e2f811d1448a5b465c236feacd80ffbac7b',
                  'base_use': 'constructor dependency only; overwritten by selected GEC weights',
                  'max_length': 'unchanged checkpoint config; printed before count; tokenizer truncation enabled by upstream'},
    'license': 'GECToR code MIT; checkpoint non-commercial; coursework only',
    'packages': {'gector': '1.2.0', 'errant': '3.0.2',
                 'transformers': '4.51.3', 'torch': '2.6.0'},
    'pipeline': 'en_core_web_sm sentence split; spaCy-tokenized sentences joined with spaces; GECToR; ERRANT original/corrected tokenized pairs',
    'inference': {'n_iteration': 5, 'keep_confidence': 0.0,
                  'min_error_prob': 0.0, 'batch_size': 16,
                  'device': 'cpu', 'torch_threads': 1, 'eval': True},
    'counts': {'primary': 'edits_grammar: exclude ERRANT main types SPELL,PUNCT,ORTH',
               'sensitivity': 'edits_all and each full ERRANT type',
               'rates': '100*edits/N whitespace words; zero if N=0',
               'sentence_ratio': 'sentences with zero grammar edits / spaCy sentences; zero if no sentences',
               'reader_window': 'first min(150,N) whitespace tokens; separately corrected',
               'LT_reader_reference': 'historical estimate: saved LT full-essay rate * min(150,saved word_count)/100; not an observed first150 LT count'},
    'acceptance': 'on pooled 36 random + 32 week9: Spearman(new_grammar,reader)>Spearman(LT_estimate,reader) AND abs(mean(new_grammar)-mean(reader))<abs(mean(LT_estimate)-mean(reader)); no selection using sensitivities',
    'features': {
        'C0': 'frozen 14 features',
        'C1': {'detected_grammar_errors_per_100_words': 'gec_grammar_per_100_whitespace_words',
               'detected_error_free_sentence_ratio': 'gec_grammar_error_free_sentence_ratio'},
        'C2': 'frozen 14 plus the same two new features; 16 total'},
    'folds': 'GroupKFold(5) by normalised_prompt; essay_id string ascending; assert match saved composition',
    'ridge': {'alpha_V': 100.0, 'alpha_G': 0.1,
              'preprocessing': 'training-only median imputation then StandardScaler'},
    'RF': {'n_estimators': 300, 'max_features': 'sqrt', 'max_depth': 10,
           'leaf_V': 2, 'leaf_G': 5, 'random_state': 42, 'n_jobs': 1,
           'preprocessing': 'training-only median imputation'},
    'labels': 'A1=max(abs(RF-truth))>=1; A3=A1 & max(abs(Ridge-truth))>=1; fixed requires all four absolute errors<1',
    'D': 'max(abs(RF_V-Ridge_V),abs(RF_G-Ridge_G))',
    'tree_spread': 'max(population std of 300 RF tree predictions V,G); ddof=0',
    'queues': 'per fold ceil(.20*N), descending score then essay_id ascending; no global reranking',
    'exact_p': 'one-sided hypergeom per fold; pooled exact PMF convolution, independent-fold reference draws',
    'bootstrap': {'draws': 2000, 'seed': 42, 'unit': 'essay',
                  'CI': 'paired percentile 2.5,97.5 linear; recompute tied ranks; skip undefined draws',
                  'limitations': 'condition on fitted OOF models; no refits, reranking, budget recomputation or prompt clustering'},
    'reader_ratio': 'mean(tool)/mean(reader), not mean individual ratios; avoids division by zero reader rows',
    'bands': 'mean(Vocabulary,Grammar): <2.5; [2.5,4.0]; >4.0',
    'benchmark': '20 eligible IDs drawn without replacement using random.Random(42) from sorted IDs; full essays, loading excluded; projected seconds/essay*3812; stop if >14400 seconds',
}


def canonical():
    return json.dumps(CONFIG, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


DIGEST = hashlib.sha256(canonical().encode()).hexdigest()


def preregister():
    print('EXPLORATORY PRE_REGISTRATION BEFORE ANY FIT OR COUNT', flush=True)
    print(canonical(), flush=True)
    print('CONFIG_SHA256=' + DIGEST, flush=True)
    for package in ['torch', 'transformers', 'gector', 'errant', 'spacy', 'en_core_web_sm']:
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = 'NOT_INSTALLED'
        print(f'PACKAGE {package}={version}', flush=True)
    print('PYTHON=' + sys.version.replace('\n', ' '), flush=True)


def audit_read(path):
    path = Path(path).resolve()
    print('READ_AUDIT ' + str(path), flush=True)
    return path


def read_csv(relative, fields=None):
    assert relative in INPUTS
    with audit_read(ROOT / relative).open(encoding='utf-8-sig', newline='') as stream:
        return [{key: value for key, value in row.items() if fields is None or key in fields}
                for row in csv.DictReader(stream)]


def install_read_guard():
    """Block non-allowlisted data/artifact reads including indirect library opens."""
    allowed = {(ROOT / name).resolve() for name in INPUTS}
    def guard(event, args):
        if event == 'socket.connect':
            raise PermissionError('Inference is offline; no essay text may leave the process')
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        mode = args[1]
        reading = not isinstance(mode, str) or not any(c in mode for c in 'wax')
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            return
        if not rel.parts or rel.parts[0] not in {'data', 'outputs', 'reports', 'docs'}:
            return
        generated = path.parent == OUT and path.name.startswith('gec_')
        asset = OUT / 'gec_assets' in path.parents
        if reading and path not in allowed and not generated and not asset:
            raise PermissionError('READ_GUARD blocked non-allowlisted artifact')
        if reading:
            print('READ_AUDIT ' + rel.as_posix(), flush=True)
    sys.addaudithook(guard)


class Counter:
    def __init__(self, model_path, verb_path):
        import torch
        import spacy
        import errant
        from transformers import AutoTokenizer
        from gector import GECToR, predict, load_verb_dict
        from gector.configuration import GECToRConfig
        random.seed(42)
        torch.manual_seed(42)
        torch.set_num_threads(1)
        self.torch = torch
        self.nlp = spacy.load('en_core_web_sm')
        self.annotator = errant.load('en', nlp=self.nlp)
        config = GECToRConfig.from_pretrained(str(model_path), local_files_only=True)
        print('CHECKPOINT_MAX_LENGTH=' + str(config.max_length), flush=True)
        config.model_id = str(OUT / 'gec_assets/roberta-base')
        self.model = GECToR.from_pretrained(str(model_path), config=config, local_files_only=True).to('cpu').eval()
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
        self.encode, self.decode = load_verb_dict(str(audit_read(verb_path)))
        self.predict = predict

    def count(self, text):
        words = text.split()
        original = [' '.join(token.text for token in sent) for sent in self.nlp(text).sents if sent.text.strip()]
        with self.torch.inference_mode(), contextlib.redirect_stdout(io.StringIO()):
            corrected = self.predict(self.model, self.tokenizer, original, self.encode, self.decode,
                                     **{k: CONFIG['inference'][k] for k in
                                        ['n_iteration', 'keep_confidence', 'min_error_prob', 'batch_size']}) if original else []
        assert len(original) == len(corrected)
        types = collections.Counter()
        free = 0
        for src, cor in zip(original, corrected):
            edits = self.annotator.annotate(self.annotator.parse(src, tokenise=False),
                                            self.annotator.parse(cor, tokenise=False))
            local = collections.Counter(edit.type for edit in edits)
            types.update(local)
            free += not any(typ.split(':', 1)[-1].split(':')[0] not in {'SPELL', 'PUNCT', 'ORTH'} for typ in local)
        grammar = sum(count for typ, count in types.items()
                      if typ.split(':', 1)[-1].split(':')[0] not in {'SPELL', 'PUNCT', 'ORTH'})
        return dict(words=len(words), sentences=len(original), edits_all=sum(types.values()),
                    edits_grammar=grammar, per_type=dict(types),
                    gec_grammar_per_100_whitespace_words=100*grammar/len(words) if words else 0.,
                    gec_grammar_error_free_sentence_ratio=free/len(original) if original else 0.)


def load_development():
    eligible = read_csv(INPUTS[0])
    assert len(eligible) == 3812
    ids = sorted(row['essay_id'] for row in eligible)
    assert len(set(ids)) == 3812
    texts = {}
    for relative in INPUTS[3:5]:
        for row in read_csv(relative, {'essay_id', 'essay_text'}):
            if row['essay_id'] in set(ids):
                assert row['essay_id'] not in texts
                texts[row['essay_id']] = row['essay_text']
    assert set(texts) == set(ids)
    return ids, texts


def run_benchmark(counter):
    ids, texts = load_development()
    selected = random.Random(42).sample(ids, 20)
    records = []
    path = OUT / 'gec_benchmark_counts.jsonl'
    if path.exists():
        raise RuntimeError('Benchmark already exists; refusing a second benchmark or parameter adaptation')
    with path.open('x', encoding='utf-8') as stream:
        started = time.perf_counter()
        for i, essay_id in enumerate(selected, 1):
            row_started = time.perf_counter()
            try:
                record = dict(essay_id=essay_id, config_sha256=DIGEST, **counter.count(texts[essay_id]))
            except Exception as error:
                print('COUNT_FAILURE essay_id=' + essay_id + ' exception_type=' + type(error).__name__, flush=True)
                raise RuntimeError('Counter failed; essay text suppressed') from None
            record['seconds'] = time.perf_counter() - row_started
            stream.write(json.dumps(record, sort_keys=True) + '\n')
            stream.flush()
            records.append(record)
            print(f'BENCHMARK_PROGRESS completed={i}/20 elapsed_seconds={time.perf_counter()-started:.6f}', flush=True)
        elapsed = time.perf_counter()-started
    seconds = elapsed / 20
    projected = seconds * 3812
    timing = dict(config_sha256=DIGEST, n=20, total_seconds=elapsed,
                  seconds_per_essay=seconds, projected_3812_seconds=projected,
                  projected_hours=projected/3600, stop=projected > 14400,
                  arithmetic=f'{elapsed:.17g}/20={seconds:.17g}; {seconds:.17g}*3812={projected:.17g}; {projected:.17g}/3600={projected/3600:.17g}')
    (OUT / 'gec_timing.json').write_text(json.dumps(timing, indent=2), encoding='utf-8')
    print('TIMING ' + json.dumps(timing, sort_keys=True), flush=True)
    if timing['stop']:
        print('STOP_FOUR_HOUR_GATE: full run not started. Options requiring a new explicit decision: background run retaining this exact configuration; or smaller checkpoint with a new preregistration. No checkpoint substituted.', flush=True)
    return timing


def run_counts(counter):
    timing = json.loads(audit_read(OUT / 'gec_timing.json').read_text())
    assert timing['config_sha256'] == DIGEST and not timing['stop'], 'Four-hour gate has not passed'
    ids, texts = load_development()
    path = OUT / 'gec_development_counts.jsonl'
    done = set()
    if path.exists():
        with audit_read(path).open(encoding='utf-8') as stream:
            for line in stream:
                row = json.loads(line)
                assert row['config_sha256'] == DIGEST and row['essay_id'] not in done
                done.add(row['essay_id'])
    with path.open('a', encoding='utf-8') as stream:
        for essay_id in ids:
            if essay_id in done:
                continue
            try:
                record = dict(essay_id=essay_id, config_sha256=DIGEST, **counter.count(texts[essay_id]))
            except Exception as error:
                print('COUNT_FAILURE essay_id=' + essay_id + ' exception_type=' + type(error).__name__, flush=True)
                raise RuntimeError('Counter failed; essay text suppressed') from None
            stream.write(json.dumps(record, sort_keys=True)+'\n')
            stream.flush()
            done.add(essay_id)
            print(f'COUNT_PROGRESS completed={len(done)}/3812', flush=True)


def append_stop_report():
    """Record the mandatory timing stop without claiming unrun comparisons."""
    timing = json.loads(audit_read(OUT / 'gec_timing.json').read_text())
    assert timing['config_sha256'] == DIGEST and timing['stop']
    destination = OUT / 'RESULTS_week10.md'
    previous = audit_read(destination).read_bytes()
    heading = '## Exploratory GECToR + ERRANT: environment and mandatory CPU timing stop'
    assert heading.encode() not in previous, 'Refusing duplicate append'
    logs = []
    for name in ['gec_environment.log', 'gec_download.log', 'gec_base_download.log', 'gec_benchmark.log', 'gec_verification.log']:
        path = audit_read(OUT / name)
        raw = path.read_bytes()
        content = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
        logs.append('\n### ' + name + '\n\n```text\n' + content + '\n```\n')
    script_hash = hashlib.sha256(audit_read(Path(__file__)).read_bytes()).hexdigest()
    section = '\n\n' + heading + '\n\n'
    section += ('2026-10-24 (Asia/Saigon). Exploratory development only. '
                'Stopped at Step 0d because the fixed twenty-essay CPU projection exceeds four hours. '
                'No reader alignment outcome or downstream effect can be inferred from this timing benchmark.\n\n')
    section += 'Pre-registration before counts: `' + DIGEST + '`. Producer SHA256: `' + script_hash + '`.\n\n'
    section += ('The first printed configuration (`20a31b1d353d8fbc47529e3f94e5fcbc0de946e602333d3813c565dbdf3368e9`) '
                'was supplemented with resource revisions before any essay count. The final configuration below was printed before the benchmark and has not changed since. '
                'GECToR code is MIT; the selected checkpoint is non-commercial, used for coursework. '
                'Sources: https://pypi.org/project/gector/ and https://huggingface.co/gotutiyan/gector-roberta-base-5k.\n\n')
    section += '```json\n' + json.dumps(CONFIG, sort_keys=True, indent=2) + '\n```\n\n'
    section += '```text\nTIMING ' + json.dumps(timing, sort_keys=True) + '\n```\n\n'
    section += ('| Requested result | Status |\n|---|---|\n'
                '| Part A: 68 reader essays, tables, bootstrap CIs, acceptance | Not run: mandatory timing stop |\n'
                '| Full development coverage, distributions and correlations | Not run: mandatory timing stop |\n'
                '| Part B C0/C1/C2 metrics, deltas and error correlations | Not run; C0 reproduction not tested |\n'
                '| Shared-error persistence and low-end overprediction | Not run |\n'
                '| D and locked tree-spread capture, exact p and AUROC | Not run |\n\n')
    section += ('Options: authorize a background run retaining this exact checkpoint and configuration, '
                'or choose a smaller checkpoint and record a new pre-registration before its evaluation. '
                'Neither option was executed. The full-development count command writes one text-free JSONL record per completed essay and resumes by ID with configuration-hash checks. '
                'Its four-hour guard currently refuses execution. The benchmark is not a replacement for Part A or Part B.\n\n')
    section += ('Method limitations: checkpoint max_length=80 subword tokens with upstream tokenizer truncation; longer sentences may be undercounted. '
                'Historical LT first-150 comparisons used rate-scaled full-essay estimates, not actual counts on the window. '
                'No fitted OOF models or CIs were produced here. Any later essay-bootstrap CIs condition on fitted OOF models and do not account for prompt clustering; '
                'exact pooled queue p-values assume independent fold reference draws although OOF training sets overlap.\n\n')
    section += ('Installation command history (commands printed before execution; package lists and download console output below):\n\n'
                '```text\nuv venv --python 3.12 .venv_gec\n'
                'uv pip install --python .venv_gec/Scripts/python.exe --index-url https://pypi.org/simple gector==1.2.0 errant==3.0.2 transformers==4.51.3 torch==2.6.0\n'
                'uv pip install --python .venv_gec/Scripts/python.exe https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl\n'
                'Using CPython 3.12.13\nCreating virtual environment at: .venv_gec\n'
                'Resolved 64 packages in 40.22s\nPrepared 32 packages in 32.40s\nInstalled 64 packages in 14.55s\n'
                'Resolved 1 package in 393ms\nInstalled 1 package in 91ms\n'
                '+ en-core-web-sm==3.8.0 (from official spaCy release)\n```\n\n'
                'The isolated environment was chosen to preserve main Python 3.14.5 and avoid changing its dependency set; '
                'no installation into the main environment was attempted. ERRANT installs spaCy but its PyPI dependencies do not install en_core_web_sm, so that official model was installed explicitly. '
                'The nonfatal uv hardlink warning fell back to copying. Download processes printed DOWNLOAD_COMPLETE and BASE_DOWNLOAD_COMPLETE; '
                'PowerShell reported pipeline exit 1 after native progress messages on stderr, but local offline model loading and all benchmark counts succeeded. '
                'No install/network block occurred, so the conditional Colab fallback was not triggered.\n')
    section += ''.join(logs)
    section += ('\nREAD_AUDIT additional supporting reads during setup: docs/signal_lock_tree_spread.md; '
                'scripts/week9/t3_evaluate.py; scripts/week9/validation_common.py; '
                'scripts/week10/information_sources_oof.py; scripts/week10/reading_compare.py; '
                'scripts/week10/random_reading.py; scripts/week9/t4_reading_sheet.py. '
                'These supporting reads were explicitly authorized in chat. Workbook reader counts were not opened. '
                'Input headers only were inspected for the other allowlisted CSVs and feature_schema.json was read. '
                'Instruction reads: .agents/skills/using-superpowers/SKILL.md, its references/codex-tools.md, '
                'the pasted request attachment and the system spreadsheets skill. Installed GECToR predict.py and modeling.py were inspected. '
                'No Test or combined corpus content was opened or searched. No frozen files, existing scripts, models, features, configs/paths.yaml or docx report were modified.\n')
    with destination.open('ab') as stream:
        stream.write(section.encode('utf-8'))
    assert audit_read(destination).read_bytes() == previous + section.encode('utf-8')
    print('APPEND_ONLY_VERIFIED previous_bytes=' + str(len(previous)) + ' previous_SHA256=' + hashlib.sha256(previous).hexdigest(), flush=True)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preregister', action='store_true')
    parser.add_argument('--benchmark', action='store_true')
    parser.add_argument('--count-development', action='store_true')
    parser.add_argument('--append-stop-report', action='store_true')
    parser.add_argument('--model-path', default=str(OUT / 'gec_assets/model'))
    parser.add_argument('--verb-path', default=str(OUT / 'gec_assets/verb-form-vocab.txt'))
    args = parser.parse_args()
    preregister()
    if args.append_stop_report:
        append_stop_report()
        return
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    install_read_guard()
    if args.benchmark or args.count_development:
        counter = Counter(args.model_path, args.verb_path)
        if args.benchmark:
            run_benchmark(counter)
        if args.count_development:
            run_counts(counter)
    print('READ_GUARD no Test or combined corpus opened by this process; per-essay counts only in git-ignored reports/week10/gec_*; essay text not emitted', flush=True)


if __name__ == '__main__':
    main()
