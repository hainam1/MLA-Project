"""Independent, text-free audit of the filled random Validation reading sample.

The user's selected evaluated copy is read without modifying either workbook.
Only --append writes results, and it opens RESULTS_week10.md in append mode.
"""
from pathlib import Path
import argparse
import contextlib
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import io
import json
import os
import posixpath
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
import scipy
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'reports/week10/RESULTS_week10.md'
ORIGINAL = 'reports/week10/reading_sheet_random.xlsx'
EVALUATED = 'reports/week10/reading_sheet_da_danh_gia.xlsx'
INPUTS = [ORIGINAL, EVALUATED, 'reports/week10/random_sample_ids.csv',
          'reports/week9/t4_reading_summary.csv', 'reports/week9/t4_manifest.csv',
          'reports/week9/t3_eligible_development.csv']
ALLOWED = {(ROOT / p).resolve() for p in INPUTS}
READS, BLOCKED, CHECKS = set(), [], []
BANDS = ['<2.5', '2.5-4.0', '>4.0']
GROUPS = ['above', 'below', 'not_large']
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
READER_ALIASES = {
    'reader': ['Số lỗi ngữ pháp (150 từ đầu)', 'reader_errors_first150'],
    'reader_V': ['Vocabulary', 'reader_low_mid_high_V'],
    'reader_G': ['Grammar', 'reader_low_mid_high_G'],
}
UNBLIND = ['essay_id', 'y_V', 'y_G', 'RF_V', 'RF_G', 'Ridge_V', 'Ridge_G',
           'word_count', 'detected_grammar_errors_per_100_words']


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
    if path not in ALLOWED or (isinstance(mode, str) and any(c in mode for c in 'wax+')):
        BLOCKED.append(rel.as_posix())
        raise PermissionError('Artifact outside read allowlist: ' + rel.as_posix())
    READS.add(rel.as_posix())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def num(value):
    return format(float(value), '.17g')


def table(title, rows):
    print(title)
    print(pd.DataFrame(rows).to_csv(index=False, float_format='%.17g', lineterminator='\n'), end='', flush=True)


def check(name, actual, expected):
    """Compare counts exactly and reported decimals at the user's precision."""
    if isinstance(expected, str) and isinstance(actual, (float, np.floating)):
        places = len(expected.split('.')[1]) if '.' in expected else 0
        rounded = Decimal(str(float(actual))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
        ok = np.isfinite(actual) and rounded == Decimal(expected)
        shown, comparison = num(actual), f'rounded_HALF_UP({places})={rounded}'
    else:
        ok = bool(actual == expected)
        shown, comparison = str(actual), 'exact'
    status = 'PASS' if ok else 'MISMATCH'
    line = f'{status} {name}: actual={shown}; expected={expected}; {comparison}'
    CHECKS.append((status, line))
    print(line)


def workbook(path):
    """Read selected fields only; never resolve essay_text shared-string values."""
    result, metadata = {}, []
    with zipfile.ZipFile(ROOT / path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)
        def cell_value(cell):
            value = cell.find('s:v', NS)
            value = value.text if value is not None else ''
            if cell.attrib.get('t') == 's':
                return ''.join(strings[int(value)].itertext())
            if cell.attrib.get('t') == 'inlineStr':
                return ''.join(cell.find('s:is', NS).itertext())
            return value
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets = ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS)
        for sheet in sheets:
            name = sheet.attrib['name']
            if name not in {'reading_sheet', 'unblind_after'}:
                continue
            rel_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = rels[rel_id]
            member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            rows = ET.fromstring(z.read(member)).findall('s:sheetData/s:row', NS)
            header = {''.join(c for c in cell.attrib['r'] if c.isalpha()): cell_value(cell).strip()
                      for cell in rows[0].findall('s:c', NS)}
            allowed = {'essay_id', 'band'} | {h for values in READER_ALIASES.values() for h in values} if name == 'reading_sheet' else set(UNBLIND)
            records = []
            for row in rows[1:]:
                record = {}
                for cell in row.findall('s:c', NS):
                    col = ''.join(c for c in cell.attrib['r'] if c.isalpha())
                    key = header.get(col)
                    if key in allowed:
                        assert cell.find('s:f', NS) is None, 'Required audit fields must be saved values, not formulas'
                        record[key] = cell_value(cell).strip()
                if record.get('essay_id'):
                    records.append(record)
            result[name] = pd.DataFrame(records).fillna('')
            metadata.append(dict(sheet=name, state=sheet.attrib.get('state', 'visible'), n=len(records),
                                 selected_headers=json.dumps([h for h in header.values() if h in allowed], ensure_ascii=False)))
    assert set(result) == {'reading_sheet', 'unblind_after'}
    return result, metadata


def reader_columns(frame):
    mapping = {}
    for new, aliases in READER_ALIASES.items():
        available = [a for a in aliases if a in frame.columns]
        assert len(available) == 1, 'Missing or ambiguous reader header: ' + new
        mapping[available[0]] = new
    return frame.rename(columns=mapping)


def truth_band(value):
    value = np.asarray(value)
    return np.where(value < 2.5, BANDS[0], np.where(value <= 4.0, BANDS[1], BANDS[2]))


def level(value):
    return np.where(np.asarray(value) < 2.5, 'low', np.where(np.asarray(value) > 4.0, 'high', 'mid'))


def add_derived(frame):
    f = frame.copy()
    f['tool_estimate'] = f.detected_grammar_errors_per_100_words * np.minimum(150, f.word_count)/100
    f['diff'] = f.reader - f.tool_estimate
    f['e_V'], f['e_G'] = f.RF_V - f.y_V, f.RF_G - f.y_G
    # Vocabulary is the predetermined deterministic tie-break.
    v = abs(f.e_V) >= abs(f.e_G)
    f['chosen_target'] = np.where(v, 'V', 'G')
    f['signed_RF_error'] = np.where(v, f.e_V, f.e_G)
    f['large_error'] = np.maximum(abs(f.e_V), abs(f.e_G)) >= 1.0
    f['group'] = np.where(~f.large_error, 'not_large', np.where(f.signed_RF_error > 0, 'above', 'below'))
    f['truth_band'] = truth_band((f.y_V + f.y_G)/2)
    return f


def rho_arithmetic(reader, tool):
    a, b = rankdata(reader, method='average'), rankdata(tool, method='average')
    aa, bb = np.dot(a-a.mean(), a-a.mean()), np.dot(b-b.mean(), b-b.mean())
    ab = np.dot(a-a.mean(), b-b.mean())
    if len(a) < 2 or aa == 0 or bb == 0:
        return np.nan, 'cannot compute: n<2 or constant ranks'
    rho = float(ab/np.sqrt(aa*bb))
    assert np.isclose(rho, spearmanr(reader, tool).statistic, rtol=0, atol=1e-14)
    return rho, f'{num(ab)}/sqrt({num(aa)}*{num(bb)})={num(rho)}'


def summaries(f, column, labels):
    rows = []
    for label in labels:
        g = f if column is None else f.loc[f[column].eq(label)]
        n = len(g)
        assert n > 0
        ordered = np.sort(g.reader.to_numpy())
        median = float(np.median(ordered))
        median_formula = f'({num(ordered[n//2-1])}+{num(ordered[n//2])})/2={num(median)}' if n % 2 == 0 else f'sorted[{n//2}]={num(median)} (zero based)'
        rho, rho_formula = rho_arithmetic(g.reader.to_numpy(), g.tool_estimate.to_numpy())
        rows.append(dict(scope=label, n=n, median_reader=median, mean_reader=float(g.reader.mean()),
            mean_tool_estimate=float(g.tool_estimate.mean()), mean_reader_minus_tool=float(g['diff'].mean()),
            tool_estimate_lt_0_5=int(g.tool_estimate.lt(.5).sum()), Spearman_reader_tool=rho,
            median_arithmetic=median_formula,
            mean_reader_arithmetic=f'{num(g.reader.sum())}/{n}={num(g.reader.mean())}',
            mean_tool_arithmetic=f'{num(g.tool_estimate.sum())}/{n}={num(g.tool_estimate.mean())}',
            mean_diff_arithmetic=f'{num(g["diff"].sum())}/{n}={num(g["diff"].mean())}',
            Spearman_arithmetic=rho_formula))
    return rows


def ols(y, design):
    coefficient, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank < design.shape[1]:
        return None
    residual = y - design @ coefficient
    sse = float(np.dot(residual, residual))
    sst = float(np.dot(y-y.mean(), y-y.mean()))
    return dict(beta=coefficient, rank=int(rank), SSE=sse, SST=sst, R2=1-sse/sst)


def regressions(f):
    y, x = f.signed_RF_error.to_numpy(), f['diff'].to_numpy()
    band = np.column_stack([np.ones(len(f)), f.truth_band.eq(BANDS[1]), f.truth_band.eq(BANDS[2])]).astype(float)
    simple = np.column_stack([np.ones(len(f)), x])
    full = np.column_stack([band, x])
    fits = {'diff_only': ols(y, simple), 'band_only': ols(y, band), 'band_plus_diff': ols(y, full)}
    rng = np.random.default_rng(42)
    boot = {'diff_only': [], 'band_plus_diff': []}
    skipped = dict.fromkeys(boot, 0)
    direct_max_difference = dict.fromkeys(boot, 0.)
    for _ in range(2000):
        index = rng.integers(0, len(f), size=len(f))
        for name, design in [('diff_only', simple), ('band_plus_diff', full)]:
            result = ols(y[index], design[index])
            if result is None or not np.isfinite(result['beta'][-1]):
                skipped[name] += 1
            else:
                slope = float(result['beta'][-1])
                xb, yb = x[index].copy(), y[index].copy()
                if name == 'diff_only':
                    xb -= xb.mean()
                    yb -= yb.mean()
                else:
                    # Independent FWL calculation using group means, not matrix fitting.
                    labels = f.truth_band.to_numpy()[index]
                    for label in BANDS:
                        mask = labels == label
                        xb[mask] -= xb[mask].mean()
                        yb[mask] -= yb[mask].mean()
                direct = float(np.dot(xb, yb)/np.dot(xb, xb))
                direct_max_difference[name] = max(direct_max_difference[name], abs(direct-slope))
                assert abs(direct-slope) < 1e-10
                boot[name].append(slope)
    rows = []
    for name, fit in fits.items():
        assert fit is not None
        design = simple if name == 'diff_only' else band if name == 'band_only' else full
        # Independent centered/FWL coefficient arithmetic checks the design fit.
        if name == 'diff_only':
            xr, yr = x-x.mean(), y-y.mean()
        elif name == 'band_plus_diff':
            xr = x-band @ np.linalg.lstsq(band, x, rcond=None)[0]
            yr = y-band @ np.linalg.lstsq(band, y, rcond=None)[0]
        if name != 'band_only':
            numerator, denominator = float(np.dot(xr, yr)), float(np.dot(xr, xr))
            assert np.isclose(numerator/denominator, fit['beta'][-1], rtol=0, atol=1e-12)
            lo, hi = np.percentile(boot[name], [2.5, 97.5], method='linear')
            fit.update(slope=float(fit['beta'][-1]), CI_low=float(lo), CI_high=float(hi))
        rows.append(dict(model=name, n=len(f), rank=fit['rank'], coefficients=json.dumps(fit['beta'].tolist()),
            slope_diff=fit.get('slope'), CI_low=fit.get('CI_low'), CI_high=fit.get('CI_high'), R2=fit['R2'],
            slope_arithmetic=f'{num(numerator)}/{num(denominator)}={num(numerator/denominator)}' if name != 'band_only' else 'not included',
            R2_arithmetic=f'1-{num(fit["SSE"])}/{num(fit["SST"])}={num(fit["R2"])}',
            bootstrap_resamples=2000 if name != 'band_only' else None,
            bootstrap_valid=len(boot[name]) if name != 'band_only' else None,
            bootstrap_skipped=skipped[name] if name != 'band_only' else None))
    print('OLS_METHOD signed error=RF-truth at larger absolute-error target; V on ties; intercept included. Band reference=<2.5, dummies=2.5-4.0 and >4.0. Coefficient order: diff_only=[intercept,diff]; band_only=[intercept,mid,high]; band_plus_diff=[intercept,mid,high,diff].')
    print('BOOTSTRAP_METHOD primary order=reading_sheet physical row order, preserved by the one-to-one left merge; ordinary paired essay rows, n=36 with replacement, 2000 resamples, default_rng(42), identical draws for both models; percentile 95% CI [2.5,97.5], linear interpolation; rank-deficient replicates skipped and counted. Bands are not stratified; no refit of RF or Ridge.')
    table('OLS_SIGNED_RF_ERROR_ON_READER_MINUS_TOOL', rows)
    table('BOOTSTRAP_INDEPENDENT_SLOPE_CHECK (lstsq vs covariance or within-band FWL)',
          [dict(model=name, valid=len(boot[name]), max_absolute_difference=direct_max_difference[name]) for name in boot])
    for name, expected in [('diff_only', ('0.172', '0.086', '0.257', '0.298')),
                           ('band_plus_diff', ('0.003', '-0.053', '0.082', '0.7746'))]:
        fit = fits[name]
        for field, value in zip(['slope', 'CI_low', 'CI_high', 'R2'], expected):
            check(name + '.' + field, fit[field], value)
    check('band_only.R2', fits['band_only']['R2'], '0.7745')
    # Explicit sensitivity: same RNG and algorithm, with ID-sorted rows instead.
    # This documents the first preflight result rather than silently discarding it.
    ordered = np.argsort(f.essay_id.to_numpy(), kind='stable')
    rng = np.random.default_rng(42)
    sensitivity = {name: [] for name in boot}
    for _ in range(2000):
        index = ordered[rng.integers(0, len(f), size=len(f))]
        for name, design in [('diff_only', simple), ('band_plus_diff', full)]:
            result = ols(y[index], design[index])
            if result is not None:
                sensitivity[name].append(float(result['beta'][-1]))
    sensitivity_rows = []
    for name in sensitivity:
        lo, hi = np.percentile(sensitivity[name], [2.5, 97.5], method='linear')
        sensitivity_rows.append(dict(model=name, row_order='essay_id ascending', seed=42,
            resamples=2000, valid=len(sensitivity[name]), CI_low=lo, CI_high=hi,
            primary_sheet_order_CI_low=fits[name]['CI_low'], primary_sheet_order_CI_high=fits[name]['CI_high']))
    table('BOOTSTRAP_ROW_ORDER_SENSITIVITY (same finite RNG draws map to different essays after reordering)', sensitivity_rows)


def main(selected):
    print('EXPLORATORY READING AUDIT; saved Validation values and human annotations only; no model refit/predict; no essay text printed; no Test artifacts opened.')
    print(f'VERSIONS Python={sys.version.split()[0]}; numpy={np.__version__}; pandas={pd.__version__}; scipy={scipy.__version__}')
    print('EXPECTED_VALUE_COMPARISON counts exact; hand-reported decimals rounded to their supplied decimal places with ROUND_HALF_UP; all computed values printed at 17 significant digits.')
    before = {p: sha(p) for p in INPUTS}
    original, original_meta = workbook(ORIGINAL)
    chosen, chosen_meta = workbook(selected)
    print('INPUT_RESOLUTION requested reading_sheet_random.xlsx is the original blank workbook; user explicitly selected reading_sheet_da_danh_gia.xlsx after clarification. Neither workbook is modified.')
    table('ORIGINAL_WORKBOOK_METADATA (only selected non-text fields)', original_meta)
    original_readers = reader_columns(original['reading_sheet'])
    for col in ['reader', 'reader_V', 'reader_G']:
        check('original_requested_workbook.' + col + '.nonempty', int(original_readers[col].str.strip().ne('').sum()), 36)
    table('SELECTED_WORKBOOK_METADATA (only selected non-text fields)', chosen_meta)
    readers = reader_columns(chosen['reading_sheet'])
    unblind = chosen['unblind_after']
    assert readers.essay_id.is_unique and unblind.essay_id.is_unique
    saved_ids = pd.read_csv(ROOT / INPUTS[2], dtype=str)
    assert saved_ids.essay_id.is_unique
    print('JOIN_AUDIT reading_ids=' + str(len(readers)) + '; unblind_ids=' + str(len(unblind)) +
          '; missing_in_unblind=' + str(len(set(readers.essay_id)-set(unblind.essay_id))) +
          '; extra_in_unblind=' + str(len(set(unblind.essay_id)-set(readers.essay_id))))
    assert set(readers.essay_id) == set(unblind.essay_id) == set(saved_ids.essay_id) == set(original_readers.essay_id)
    numeric = UNBLIND[1:]
    for col in numeric:
        unblind[col] = pd.to_numeric(unblind[col], errors='raise')
    original_truth = original['unblind_after'].set_index('essay_id')
    selected_truth = unblind.set_index('essay_id').loc[original_truth.index]
    maximum = max(float(np.max(np.abs(pd.to_numeric(original_truth[c]).to_numpy()-selected_truth[c].to_numpy()))) for c in numeric)
    assert maximum <= 1e-12
    print('UNBLIND_SOURCE_PRESERVATION max_absolute_numeric_difference_from_original=' + num(maximum) + '; tolerance=1e-12; same_ID_set=True')
    for col in ['reader', 'reader_V', 'reader_G']:
        check('selected_workbook.' + col + '.nonempty', int(readers[col].str.strip().ne('').sum()), 36)
    readers['reader'] = pd.to_numeric(readers.reader, errors='raise')
    assert np.isfinite(readers.reader).all() and readers.reader.ge(0).all() and np.equal(readers.reader, np.floor(readers.reader)).all()
    mapping = {'thấp': 'low', 'trung bình': 'mid', 'cao': 'high', 'low': 'low', 'mid': 'mid', 'middle': 'mid', 'high': 'high'}
    print('READER_LEVEL_MAPPING ' + json.dumps(mapping, ensure_ascii=False))
    for col in ['reader_V', 'reader_G']:
        readers[col] = readers[col].str.strip().str.casefold().map(mapping)
        assert readers[col].notna().all(), 'Unknown reader category'
    f = readers.merge(unblind, on='essay_id', validate='one_to_one', sort=False).reset_index(drop=True)
    assert f.essay_id.tolist() == readers.essay_id.tolist()
    print('BOOTSTRAP_PRIMARY_ORDER physical reading_sheet row order; ordered_ID_SHA256=' + hashlib.sha256('\n'.join(f.essay_id).encode()).hexdigest())
    check('joined_n', len(f), 36)
    assert np.isfinite(f[numeric+['reader']].to_numpy(dtype=float)).all()
    f = add_derived(f)
    assert np.array_equal(f.band, f.truth_band)
    assert f.set_index('essay_id').truth_band.to_dict() == saved_ids.set_index('essay_id').band.to_dict()
    print('BAND_DEFINITION mean truth=(y_V+y_G)/2; <2.5 low, 2.5<=mean<=4 middle, >4 high; saved band and fixed IDs CSV match recomputed bands.')
    print('TOOL_FORMULA tool_estimate=detected_grammar_errors_per_100_words*min(150,word_count)/100. This is the specified estimate for the reading window, not an observed tool count in the first 150 words.')
    alternative = f.detected_grammar_errors_per_100_words/100*np.minimum(150, f.word_count)
    difference = float(np.max(np.abs(alternative-f.tool_estimate)))
    print('TOOL_FORMULA_ARITHMETIC max_abs_difference_between_rate*window/100_and_rate/100*window=' + num(difference))
    assert difference < 1e-12
    print('PASS tool_estimate_formula: all 36 rows verified; shorter_than_150_words=' + str(int(f.word_count.lt(150).sum())))
    print('RF_GROUP_DEFINITION large=max(abs(RF_V-y_V),abs(RF_G-y_G))>=1; signed_error=RF-truth at larger abs error; exact ties use V; above=signed_error>0 among large; below=signed_error<0 among large; not_large otherwise.')
    print('TARGET_TIES n=' + str(int(abs(f.e_V).eq(abs(f.e_G)).sum())))
    band_rows = summaries(f, 'truth_band', BANDS)
    group_rows = summaries(f, 'group', GROUPS)
    overall = summaries(f, None, ['overall'])
    table('RANDOM_SAMPLE_PER_BAND', band_rows)
    table('RANDOM_SAMPLE_PER_RF_GROUP', group_rows)
    table('RANDOM_SAMPLE_OVERALL', overall)
    expected_bands = [(12, '11.5', '2.59', '8.16', 0, '0.41'),
                      (12, '6.5', '0.89', '6.11', 2, '0.58'),
                      (12, '4.5', '0.23', '4.02', 11, '0.01')]
    for band_name, row, expected in zip(BANDS, band_rows, expected_bands):
        for field, value in zip(['n', 'median_reader', 'mean_tool_estimate', 'mean_reader_minus_tool', 'tool_estimate_lt_0_5', 'Spearman_reader_tool'], expected):
            check('band[' + band_name + '].' + field, row[field], value)
    for row, n in zip(group_rows, [6, 6, 24]):
        check('group[' + row['scope'] + '].n', row['n'], n)
    for field, value in [('n', 36), ('mean_reader', '7.33'), ('mean_tool_estimate', '1.24'), ('Spearman_reader_tool', '0.73')]:
        check('overall.' + field, overall[0][field], value)
    recognition = []
    expected_recognition = {'V': {'low': (4, 7), 'mid': (13, 23), 'high': (3, 6)},
                            'G': {'low': (10, 13), 'mid': (7, 11), 'high': (6, 12)}}
    confusion = []
    for target in ['V', 'G']:
        truth = level(f['y_' + target])
        reader = f['reader_' + target].to_numpy()
        for truth_level in ['low', 'mid', 'high']:
            mask = truth == truth_level
            n, correct = int(mask.sum()), int((mask & (reader == truth_level)).sum())
            recognition.append(dict(target=target, truth_level=truth_level, n=n, correct=correct, share=correct/n,
                                    arithmetic=f'{correct}/{n}={num(correct/n)}'))
            wanted_correct, wanted_n = expected_recognition[target][truth_level]
            check(f'recognition[{target},{truth_level}].correct', correct, wanted_correct)
            check(f'recognition[{target},{truth_level}].n', n, wanted_n)
            for reader_level in ['low', 'mid', 'high']:
                confusion.append(dict(target=target, truth_level=truth_level, reader_level=reader_level, n=int((mask & (reader == reader_level)).sum())))
    table('BLIND_RECOGNITION_PER_TRUE_TARGET_LEVEL', recognition)
    table('BLIND_RECOGNITION_CONFUSION_COUNTS', confusion)
    regressions(f)
    purposive = pd.read_csv(ROOT / INPUTS[3], dtype={'essay_id': str}, keep_default_na=False)
    manifest = pd.read_csv(ROOT / INPUTS[4], dtype={'essay_id': str})
    assert len(purposive) == 32 and purposive.essay_id.is_unique and set(purposive.essay_id) == set(manifest.essay_id)
    purposive = purposive.rename(columns={'reader_error_count_first150': 'reader'})
    for col in ['reader', 'approx_tool_count', 'word_count', 'y_V', 'y_G', 'RF_V', 'RF_G']:
        purposive[col] = pd.to_numeric(purposive[col], errors='raise')
        assert np.isfinite(purposive[col]).all()
    rates = pd.read_csv(ROOT / INPUTS[5], usecols=['essay_id', 'word_count', 'detected_grammar_errors_per_100_words'], dtype={'essay_id': str})
    rates = rates.loc[rates.essay_id.isin(purposive.essay_id)].rename(columns={'word_count': 'saved_feature_word_count'})
    assert len(rates) == 32 and rates.essay_id.is_unique
    purposive = purposive.merge(rates, on='essay_id', validate='one_to_one')
    assert np.array_equal(purposive.word_count, purposive.saved_feature_word_count)
    purposive = add_derived(purposive)
    print('PURPOSIVE_PROVENANCE 32 IDs and reader counts from text-free t4_reading_summary.csv, verified against t4_manifest.csv; tool_estimate independently recomputed with the same window formula from saved eligible-development rates and matching word_count. The CSV approx_tool_count is also reported separately.')
    saved_difference = abs(purposive.approx_tool_count-purposive.tool_estimate)
    print('PURPOSIVE_SAVED_TOOL_ESTIMATE_CHECK exact_equal_rows=' + str(int(saved_difference.eq(0).sum())) + '/32; max_absolute_difference=' + num(saved_difference.max()))
    p_rows = summaries(purposive, 'group', GROUPS)
    table('PURPOSIVE_SAMPLE_PER_RF_GROUP', p_rows)
    side_by_side = []
    for random_row, purp_row in zip(group_rows, p_rows):
        group = random_row['scope']
        g = purposive.loc[purposive.group.eq(group)]
        side_by_side.append(dict(group='control_not_large' if group == 'not_large' else group,
            random_n=random_row['n'], random_median_reader=random_row['median_reader'], random_mean_tool=random_row['mean_tool_estimate'],
            purposive_n=purp_row['n'], purposive_median_reader=purp_row['median_reader'], purposive_mean_tool=purp_row['mean_tool_estimate'],
            purposive_mean_saved_approx_tool=float(g.approx_tool_count.mean())))
    table('RANDOM_VS_32_PURPOSIVE_SIDE_BY_SIDE', side_by_side)
    table('PURPOSIVE_SELECTION_GROUP_VS_RF_GROUP', purposive.groupby(['sample_group', 'group']).size().reset_index(name='n').to_dict('records'))
    print('RANDOM_PURPOSIVE_ID_OVERLAP=' + str(len(set(f.essay_id) & set(purposive.essay_id))))
    assert before == {p: sha(p) for p in INPUTS}, 'An input changed while analysis ran'
    for path in sorted(READS):
        print('READ_AUDIT ' + path + ' SHA256=' + before[path])
    print(f'READ_GUARD artifact_reads={len(READS)}; allowlisted_only={READS <= set(INPUTS)}; blocked_attempts={len(BLOCKED)}; no Test file opened; inputs_unchanged=True; essay_text_values_not_resolved_or_printed=True')
    print('EXPECTED_VALUE_CHECK_TOTAL pass=' + str(sum(status == 'PASS' for status, _ in CHECKS)) + '; mismatch=' + str(sum(status == 'MISMATCH' for status, _ in CHECKS)))
    print('MISMATCH_LINES')
    for status, line in CHECKS:
        if status == 'MISMATCH':
            print(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook', default=EVALUATED, choices=[EVALUATED])
    parser.add_argument('--append', action='store_true')
    args = parser.parse_args()
    sys.addaudithook(audit)
    previous = DEST.read_bytes()
    heading = '## Week 10 filled random reading audit and purposive comparison'
    if args.append:
        assert heading.encode() not in previous, 'Refusing duplicate append'
    captured = io.StringIO()
    class Tee:
        def write(self, text):
            sys.__stdout__.write(text)
            captured.write(text)
        def flush(self):
            sys.__stdout__.flush()
    with contextlib.redirect_stdout(Tee()):
        main(args.workbook)
    if args.append:
        section = ('\n\n' + heading + '\n\nUser-selected input: `reports/week10/reading_sheet_da_danh_gia.xlsx`; the originally named workbook still has blank reader cells. '
                   'Exploratory annotations and descriptive comparisons; no confirmatory claim. Producer: `scripts/week10/reading_compare.py`. '
                   'Command: `.venv/Scripts/python.exe -B -u scripts/week10/reading_compare.py --workbook reports/week10/reading_sheet_da_danh_gia.xlsx --append`.\n\n```text\n'
                   + captured.getvalue() + '```\n')
        with DEST.open('ab') as stream:
            stream.write(section.encode('utf-8'))
        assert DEST.read_bytes().startswith(previous)
        print('APPEND_PREFIX_UNCHANGED=True; prefix_sha256=' + hashlib.sha256(previous).hexdigest())
