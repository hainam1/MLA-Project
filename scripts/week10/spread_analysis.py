"""Exploratory Validation and fixed GroupKFold development spread diagnostics.

No prediction artifacts are written. The development refit is the explicitly
authorized exception to saved-predictions-only analysis in Part B.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.stats import rankdata, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'reports/week10/RESULTS_week10.md'
INPUTS = ['reports/week9/t3_eligible_development.csv',
          'reports/week9/t3_fold_composition.csv',
          'outputs/phase6/feature_schema.json',
          'outputs/phase6/validation_predictions.csv']
ALLOWED = {(ROOT / p).resolve() for p in INPUTS}
READS, BLOCKED = set(), []
CENTERS = {'V': 3.26941940240918, 'G': 3.124225726952784}
BANDS = ['<2.5', '2.5-4.0', '>4.0']


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


def num(x):
    return format(float(x), '.17g')


def table(title, rows):
    print(title)
    print(pd.DataFrame(rows).to_csv(index=False, float_format='%.17g', lineterminator='\n'), end='', flush=True)


def bands(y):
    return np.where(y < 2.5, BANDS[0], np.where(y <= 4.0, BANDS[1], BANDS[2]))


def validation(f):
    p = pd.read_csv(ROOT / INPUTS[3], dtype={'essay_id': str}).rename(columns={
        'ridge_vocabulary': 'Ridge_V', 'ridge_grammar': 'Ridge_G',
        'random_forest_vocabulary': 'RF_V', 'random_forest_grammar': 'RF_G'})
    out = f.loc[f.essay_id.isin(p.essay_id), ['essay_id', 'split', 'Vocabulary', 'Grammar']].copy()
    assert len(out) == len(p) == 762 and out.split.eq('validation').all()
    assert out.essay_id.is_unique and p.essay_id.is_unique
    return out.merge(p, on='essay_id', validate='one_to_one').rename(columns={'Vocabulary': 'y_V', 'Grammar': 'y_G'})


def development(f):
    features = json.loads((ROOT / INPUTS[2]).read_text())
    composition = pd.read_csv(ROOT / INPUTS[1])
    composition = composition.loc[composition.split_type.eq('prompt_disjoint')]
    assert len(features) == 14 and f.normalised_prompt.nunique() == 44
    assert np.isfinite(f[features + ['Vocabulary', 'Grammar']].to_numpy()).all()
    frames = []
    for fold, (tr, held) in enumerate(GroupKFold(5).split(f, groups=f.normalised_prompt), 1):
        train, val = f.iloc[tr], f.iloc[held]
        saved = composition.loc[composition.fold.eq(fold)]
        assert val.groupby('normalised_prompt').size().to_dict() == saved.set_index('heldout_prompt').heldout_prompt_essays.to_dict()
        assert saved.train_essays.eq(len(train)).all() and saved.heldout_essays.eq(len(val)).all()
        assert not set(train.normalised_prompt) & set(val.normalised_prompt)
        out = val[['essay_id', 'Vocabulary', 'Grammar']].rename(columns={'Vocabulary': 'y_V', 'Grammar': 'y_G'}).copy()
        for target, t, alpha, leaf in [('Vocabulary', 'V', 100., 2), ('Grammar', 'G', .1, 5)]:
            rf = make_pipeline(SimpleImputer(strategy='median'), RandomForestRegressor(
                n_estimators=300, max_features='sqrt', max_depth=10,
                min_samples_leaf=leaf, random_state=42, n_jobs=1))
            ridge = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), Ridge(alpha=alpha))
            rf.fit(train[features], train[target])
            ridge.fit(train[features], train[target])
            out['RF_' + t] = rf.predict(val[features])
            out['Ridge_' + t] = ridge.predict(val[features])
        out['fold'] = fold
        frames.append(out)
        print(f'FIT_COMPLETE fold={fold}; train_n={len(train)}; heldout_n={len(val)}; matches_week9b_composition=True; prompt_overlap=0; heldout_id_sha256=' + hashlib.sha256('\n'.join(val.essay_id).encode()).hexdigest(), flush=True)
    out = pd.concat(frames, ignore_index=True)
    assert len(out) == 3812 and out.essay_id.is_unique
    return out


def analyze(name, f):
    n = len(f)
    assert np.isfinite(f[['y_V', 'y_G', 'Ridge_V', 'Ridge_G', 'RF_V', 'RF_G']].to_numpy()).all()
    large = np.maximum(abs(f.y_V - f.RF_V), abs(f.y_G - f.RF_G)) >= 1.0
    assert int(large.sum()) == (69 if name == 'Validation' else 386)
    ext = np.maximum(abs(f.Ridge_V - CENTERS['V']), abs(f.Ridge_G - CENTERS['G'])).to_numpy()
    summary, arithmetic, means, extremes, aucs, rhos = [], [], [], [], [], []
    for t, target in [('V', 'Vocabulary'), ('G', 'Grammar')]:
        y = f['y_' + t].to_numpy()
        band = bands(y)
        for model in ['Ridge', 'RF']:
            p = f[model + '_' + t].to_numpy()
            ym, pm = y.mean(), p.mean()
            yy, pp, yp = float(np.dot(y-ym, y-ym)), float(np.dot(p-pm, p-pm)), float(np.dot(y-ym, p-pm))
            sy, sp = np.sqrt(yy/n), np.sqrt(pp/n)
            ratio, r, slope = sp/sy, yp/np.sqrt(yy*pp), yp/pp
            assert np.isclose(r, np.corrcoef(y, p)[0, 1], atol=1e-14, rtol=0)
            assert np.isclose(slope, np.polyfit(p, y, 1)[0], atol=1e-12, rtol=0)
            qy, qp = np.quantile(y, [.05, .95], method='linear'), np.quantile(p, [.05, .95], method='linear')
            summary.append(dict(target=target, model=model, n=n, SD_true=sy, SD_pred=sp, ratio=ratio,
                about_0_5=bool(.45 <= ratio <= .55), true_min=y.min(), true_max=y.max(), true_p05=qy[0], true_p95=qy[1],
                pred_min=p.min(), pred_max=p.max(), pred_p05=qp[0], pred_p95=qp[1], Pearson_r=r, OLS_truth_on_pred_slope=slope))
            arithmetic.append(dict(target=target, model=model,
                SD_true=f'sqrt({num(yy)}/{n})={num(sy)}', SD_pred=f'sqrt({num(pp)}/{n})={num(sp)}',
                ratio=f'{num(sp)}/{num(sy)}={num(ratio)}', Pearson=f'{num(yp)}/sqrt({num(yy)}*{num(pp)})={num(r)}',
                slope=f'{num(yp)}/{num(pp)}={num(slope)}',
                true_range=f'{num(y.max())}-{num(y.min())}={num(y.max()-y.min())}',
                pred_range=f'{num(p.max())}-{num(p.min())}={num(p.max()-p.min())}'))
            for b in BANDS:
                mask = band == b
                k = int(mask.sum())
                means.append(dict(target=target, model=model, truth_band=b, n=k,
                    mean_true=float(y[mask].mean()) if k else None, mean_pred=float(p[mask].mean()) if k else None,
                    arithmetic=f'truth {num(y[mask].sum())}/{k}={num(y[mask].mean())}; pred {num(p[mask].sum())}/{k}={num(p[mask].mean())}' if k else 'cannot compute: empty band'))
            for tail, mask in [('>=4.5', y >= 4.5), ('<=2.0', y <= 2.0)]:
                k = int(mask.sum())
                middle = int((mask & (p >= 2.5) & (p <= 4.)).sum())
                extremes.append(dict(target=target, model=model, truth_tail=tail, n=k, predicted_in_2_5_to_4_0=middle,
                    share=middle/k if k else None, arithmetic=f'{middle}/{k}={num(middle/k)}' if k else 'cannot compute: empty tail'))
        own_ext = abs(f['Ridge_' + t].to_numpy() - CENTERS[t])
        for ename, score in [('frozen_max', ext), ('target_distance', own_ext)]:
            for b in BANDS:
                mask = band == b
                label = large.to_numpy()[mask]
                pos, neg = int(label.sum()), int((~label).sum())
                if pos and neg:
                    ranks = rankdata(score[mask], method='average')
                    rank_sum = float(ranks[label].sum())
                    u = rank_sum - pos*(pos+1)/2
                    auc = u/(pos*neg)
                    formula = f'({num(rank_sum)}-{pos}*({pos}+1)/2)/({pos}*{neg})={num(auc)}'
                else:
                    auc, formula = None, 'cannot compute: band lacks both error classes'
                aucs.append(dict(target=target, extremity=ename, truth_band=b, n=int(mask.sum()), large_errors=pos, other=neg, AUROC=auc, arithmetic=formula))
            a, b = rankdata(score), rankdata(abs(y-3.0))
            aa, bb = float(np.dot(a-a.mean(), a-a.mean())), float(np.dot(b-b.mean(), b-b.mean()))
            ab = float(np.dot(a-a.mean(), b-b.mean()))
            rho = ab/np.sqrt(aa*bb)
            assert np.isclose(rho, spearmanr(score, abs(y-3.0)).statistic, atol=1e-14, rtol=0)
            rhos.append(dict(target=target, extremity=ename, n=n, Spearman_extremity_vs_abs_truth_minus_3=rho,
                arithmetic=f'{num(ab)}/sqrt({num(aa)}*{num(bb)})={num(rho)}'))
    print(f'\nSET={name}; N={n}; joint_RF_large_errors={int(large.sum())}')
    table('SMALL_SUMMARY_TABLE (population SD; about_0_5 means 0.45<=ratio<=0.55)', summary)
    table('ARITHMETIC (centered sums; OLS includes an intercept)', arithmetic)
    print('QUANTILE_ARITHMETIC linear interpolation: h=(N-1)*q; j=floor(h); x[j]+(h-j)*(x[j+1]-x[j]); zero-based sorted x.')
    for q in [.05, .95]:
        h = (n-1)*q
        print(f'QUANTILE_INDEX q={num(q)}; h=({n}-1)*{num(q)}={num(h)}; j={int(np.floor(h))}; fraction={num(h-np.floor(h))}')
    table('TRUTH_BAND_MEANS (2.5 and 4.0 included in middle band)', means)
    table('EXTREME_TRUTH_MIDDLE_PREDICTION_SHARES (prediction endpoints inclusive)', extremes)
    table('RIDGE_EXTREMITY_WITHIN_BAND_AUROC (joint RF error >=1; average ranks)', aucs)
    table('RIDGE_EXTREMITY_SPEARMAN (truth distance is per target; average ranks)', rhos)


def main():
    print('PART B: EXPLORATORY ONLY; no new confirmatory evidence; no Test prediction/label file access.')
    print(f'VERSIONS Python={sys.version.split()[0]}; numpy={np.__version__}; pandas={pd.__version__}; scipy={scipy.__version__}; sklearn={sklearn.__version__}')
    print('Validation: saved predictions only, no fit. Development: explicitly authorized same GroupKFold(5)-by-prompt refit as scripts/week9b/tree_spread_oof.py; predictions held only in memory, no new artifacts. Pooled OOF statistics, not fold averages.')
    print('PARAMETERS: sorted essay_id string; 14 frozen features; RF n_estimators=300,max_features=sqrt,max_depth=10,min_samples_leaf V=2/G=5,random_state=42,n_jobs=1; Ridge alpha V=100/G=0.1; training-only median imputation and Ridge StandardScaler.')
    print('METHOD: ddof=0; OLS truth~prediction includes intercept; Pearson uses centered cross-products; quantiles linear. About 0.5 is prospectively operationalized as [0.45,0.55]. No interpretation beyond numbers.')
    print('EXTREMITY: frozen Ridge medians V=' + num(CENTERS['V']) + ', G=' + num(CENTERS['G']) + '; frozen_max=max(abs(Ridge_V-median_V),abs(Ridge_G-median_G)); target_distance=abs(Ridge_target-median_target). Same frozen medians for both sets; no OOF recentering. Large error is joint RF max absolute error>=1. Truth bands and distance from 3 are target-specific in Part B.')
    before = {p: sha(p) for p in INPUTS}
    f = pd.read_csv(ROOT / INPUTS[0], dtype={'essay_id': str}).sort_values('essay_id', kind='stable').reset_index(drop=True)
    assert len(f) == 3812 and f.essay_id.is_unique
    assert f.source_partition.eq('official_train').all() and f.privacy_review_status.eq('not_flagged').all() and f.eligible.all()
    assert set(f.split) == {'model_train', 'validation'}
    analyze('Validation', validation(f))
    analyze('Development_OOF', development(f))
    assert before == {p: sha(p) for p in INPUTS}
    for path in sorted(READS):
        print('READ_AUDIT ' + path + ' SHA256=' + before[path])
    print(f'READ_GUARD artifact_reads={len(READS)}; allowlisted_only={READS <= set(INPUTS)}; blocked_attempts={len(BLOCKED)}; no Test prediction/label file opened; inputs_unchanged=True')


if __name__ == '__main__':
    sys.addaudithook(audit)
    old = DEST.read_bytes()
    heading = '## Part B: exploratory prediction and truth spread'
    assert heading.encode() not in old, 'Refusing duplicate results append'
    captured = io.StringIO()
    class Tee:
        def write(self, text):
            sys.__stdout__.write(text)
            captured.write(text)
        def flush(self):
            sys.__stdout__.flush()
    with threadpool_limits(limits=1), contextlib.redirect_stdout(Tee()):
        main()
    with DEST.open('ab') as stream:
        stream.write(('\n\n' + heading + '\n\nCommand: `.venv/Scripts/python.exe -B -u scripts/week10/spread_analysis.py`\n\n```text\n' + captured.getvalue() + '```\n').encode('utf-8'))
    assert DEST.read_bytes().startswith(old)
    print('APPEND_PREFIX_UNCHANGED=True; prefix_sha256=' + hashlib.sha256(old).hexdigest())
