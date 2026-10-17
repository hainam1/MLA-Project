"""Exploratory tree-spread evaluation on held-out development prompts.

Run with --append to append stdout to the existing results document.
Artifact reads are explicitly allowlisted; no model or prediction files are saved.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import math
import os
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.stats import hypergeom, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'reports/week9/RESULTS_week9.md'
INPUTS = ['reports/week9/t3_eligible_development.csv',
          'reports/week9/t3_fold_composition.csv',
          'outputs/phase6/feature_schema.json']
ALLOWED = {(ROOT / p).resolve() for p in INPUTS}
READS = set()
BLOCKED = []
HEADING = '## Week 9b — RF tree spread on held-out development prompts'


def audit(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    p = Path(os.fsdecode(args[0])).resolve()
    try:
        rel = p.relative_to(ROOT)
    except ValueError:
        return
    if not rel.parts or rel.parts[0] not in {'data', 'outputs', 'docs', 'reports'}:
        return
    mode = args[1]
    if p == DEST and isinstance(mode, str) and mode.startswith('a') and args[2] & os.O_APPEND and not args[2] & os.O_TRUNC:
        return
    if p not in ALLOWED or (isinstance(mode, str) and any(c in mode for c in 'wax+')):
        BLOCKED.append(rel.as_posix())
        raise PermissionError('Artifact outside read allowlist: ' + rel.as_posix())
    READS.add(rel.as_posix())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def table(title, rows):
    print(title)
    print(pd.DataFrame(rows).to_csv(index=False, float_format='%.17g', lineterminator='\n'), end='', flush=True)


def top(frame, col, k):
    return frame.sort_values([col, 'essay_id'], ascending=[False, True], kind='stable').head(k).index


def auc_boot(y, scores):
    """Weighted rank AUC; paired essay bootstrap, identical draws across scores."""
    y = np.asarray(y, dtype=bool)
    specs = {name: np.unique(score, return_inverse=True)[1] for name, score in scores.items()}

    def auc(inv, weights):
        pos = np.bincount(inv, weights=weights*y)
        neg = np.bincount(inv, weights=weights*(~y), minlength=len(pos))
        npos, nneg = float(pos.sum()), float(neg.sum())
        if npos == 0 or nneg == 0:
            return np.nan, np.nan
        u = float(np.dot(pos, np.cumsum(neg)-.5*neg))
        return u/(npos*nneg), u

    samples = {name: [] for name in scores}
    rng = np.random.default_rng(42)
    for _ in range(2000):
        w = np.bincount(rng.integers(0, len(y), len(y)), minlength=len(y))
        for name, inv in specs.items():
            value, _ = auc(inv, w)
            if np.isfinite(value):
                samples[name].append(value)
    rows = []
    for name, inv in specs.items():
        value, u = auc(inv, np.ones(len(y)))
        lo, hi = np.percentile(samples[name], [2.5, 97.5])
        rows.append(dict(signal=name, AUROC=value, CI_low=lo, CI_high=hi,
                         arithmetic=f'{u:.17g}/({int(y.sum())}*{int((~y).sum())})={value:.17g}',
                         bootstrap_resamples=2000, valid_resamples=len(samples[name]),
                         skipped_resamples=2000-len(samples[name])))
    return rows


def main():
    print('EXPLORATORY development only; seed=42; no search; models refitted within folds; no frozen artifacts changed.')
    print(f'VERSIONS Python={sys.version.split()[0]}; numpy={np.__version__}; pandas={pd.__version__}; scipy={scipy.__version__}; sklearn={sklearn.__version__}')
    print('PARAMETERS RF trees=300; max_features=sqrt; max_depth=10; min_samples_leaf V=2,G=5; random_state=42; n_jobs=1. Ridge alpha V=100,G=0.1; train-only median imputation; Ridge train-only StandardScaler.')
    print('DEFINITIONS tree_std=max(target population tree std,ddof=0); D=max(abs(RF-Ridge)); RF_error=max(abs(y-RF)); L=RF_error>=1; k=ceil(.20*n_fold); score descending, essay_id string ascending.')
    before = {p: sha(p) for p in INPUTS}
    f = pd.read_csv(ROOT / INPUTS[0], dtype={'essay_id': str}).sort_values('essay_id', kind='stable').reset_index(drop=True)
    composition = pd.read_csv(ROOT / INPUTS[1])
    composition = composition.loc[composition.split_type.eq('prompt_disjoint')]
    features = json.loads((ROOT / INPUTS[2]).read_text())
    assert len(features) == 14 and len(f) == 3812 and f.essay_id.is_unique
    assert f.normalised_prompt.nunique() == 44
    assert f.privacy_review_status.eq('not_flagged').all()
    assert f.source_partition.eq('official_train').all()
    assert set(f.split) == {'model_train', 'validation'}
    assert f.eligible.all() and np.isfinite(f[features+['Vocabulary','Grammar']].to_numpy()).all()
    frames, checks, metrics, aurocs, correlations = [], [], [], [], []
    for fold, (tr, held) in enumerate(GroupKFold(5).split(f, groups=f.normalised_prompt), 1):
        train, val = f.iloc[tr], f.iloc[held]
        saved = composition.loc[composition.fold.eq(fold)]
        actual = val.groupby('normalised_prompt').size().to_dict()
        expected = saved.set_index('heldout_prompt').heldout_prompt_essays.to_dict()
        assert actual == expected
        assert saved.train_essays.eq(len(train)).all() and saved.heldout_essays.eq(len(val)).all()
        assert not set(train.normalised_prompt) & set(val.normalised_prompt)
        n, k = len(val), math.ceil(.2*len(val))
        assert saved.k.eq(k).all()
        checks.append(dict(fold=fold, train_n=len(train), n=n, heldout_prompts=len(actual),
                           overlapping_prompts=0, matches_t3_fold_composition=True,
                           heldout_id_sha256=hashlib.sha256('\n'.join(val.essay_id).encode()).hexdigest()))
        out = val[['essay_id','word_count']].reset_index(drop=True).copy()
        stds, errors, differences = [], [], []
        for target, alpha, leaf in [('Vocabulary',100.,2),('Grammar',.1,5)]:
            rf = make_pipeline(SimpleImputer(strategy='median'), RandomForestRegressor(
                n_estimators=300, max_features='sqrt', max_depth=10,
                min_samples_leaf=leaf, random_state=42, n_jobs=1))
            ridge = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), Ridge(alpha=alpha))
            rf.fit(train[features],train[target]); ridge.fit(train[features],train[target])
            xheld = rf[:-1].transform(val[features])
            trees = np.array([tree.predict(xheld) for tree in rf[-1].estimators_])
            rf_pred = rf.predict(val[features]); ridge_pred = ridge.predict(val[features])
            assert trees.shape == (300,n) and np.allclose(trees.mean(axis=0),rf_pred,rtol=0,atol=1e-12)
            stds.append(trees.std(axis=0,ddof=0))
            errors.append(abs(val[target].to_numpy()-rf_pred))
            differences.append(abs(rf_pred-ridge_pred))
        out['tree_std'] = np.maximum(*stds)
        out['D'] = np.maximum(*differences)
        out['RF_error'] = np.maximum(*errors)
        out['L'] = out.RF_error.ge(1.)
        out['fold'] = fold
        out['selected_tree_std'] = out.index.isin(top(out,'tree_std',k))
        out['selected_D'] = out.index.isin(top(out,'D',k))
        frames.append(out)
        print(f'FIT_COMPLETE fold={fold}; training_n={len(train)}; heldout_n={n}; K={int(out.L.sum())}; k=ceil(.20*{n})={k}; matching_saved_prompt_composition=True', flush=True)
    table('FOLD_CHECKS', checks)
    all_frames = [('fold'+str(i),frame) for i,frame in enumerate(frames,1)]
    pooled = pd.concat(frames,ignore_index=True)
    all_frames.append(('pooled',pooled))
    for scope, out in all_frames:
        n, K = len(out), int(out.L.sum())
        for name in ['tree_std','D']:
            k = int(out['selected_'+name].sum())
            caught = int((out.L & out['selected_'+name]).sum())
            base = dict(scope=scope,signal=name,n=n,K=K,k=k,caught=caught,
                        capture=f'{caught}/{K}={caught/K:.17g}')
            if scope != 'pooled':
                expected = k*K/n
                p = float(hypergeom.sf(caught-1,n,K,k))
                base.update(expected=expected, expected_arithmetic=f'{k}*{K}/{n}={expected:.17g}',
                            exact_p=p,p_formula=f'hypergeom.sf({caught-1},{n},{K},{k})')
            else:
                # Exact null for the actual fold-specific budgets is a convolution.
                dist = np.array([1.])
                terms = []
                for frame in frames:
                    nf,Kf,kf = len(frame),int(frame.L.sum()),int(frame['selected_'+name].sum())
                    terms.append((kf,Kf,nf))
                    pmf = hypergeom.pmf(np.arange(min(Kf,kf)+1),nf,Kf,kf)
                    dist = np.convolve(dist,pmf)
                expected = sum(kf*Kf/nf for kf,Kf,nf in terms)
                assert abs(dist.sum()-1.) < 1e-12
                base.update(expected=expected,
                    expected_arithmetic='+'.join(f'{kf}*{Kf}/{nf}' for kf,Kf,nf in terms)+f'={expected:.17g}',
                    exact_p=float(dist[caught:].sum()),p_formula=f'P(sum independent fold Hypergeom>= {caught}); exact PMF convolution',
                    global_formula_p=float(hypergeom.sf(caught-1,n,K,k)),
                    global_formula=f'hypergeom.sf({caught-1},{n},{K},{k}); different global-uniform null',
                    global_expected=k*K/n)
            metrics.append(base)
        scores = {name:out[name].to_numpy() for name in ['tree_std','D']}
        aurocs.extend(dict(scope=scope,**row) for row in auc_boot(out.L,scores))
        for other in ['RF_error','D','word_count']:
            rho = float(spearmanr(out.tree_std,out[other]).statistic)
            correlations.append(dict(scope=scope,n=n,x='tree_std',y=other,spearman_rho=rho))
    table('CAPTURE_METRICS (pooled selections sum fold queues; no global reranking)',metrics)
    table('AUROC (ordinary essay bootstrap, 2000 resamples, seed=42, percentile 95% CI)',aurocs)
    table('SPEARMAN (average ranks; RF_error=max target absolute RF error)',correlations)
    print('POOLING: k=sum ceil(.20*n_fold), expected=sum(k_fold*K_fold/n_fold). Pooled exact p is the convolution of the five fold-specific hypergeometric distributions. The additional pooled global-formula p ignores the fixed fold quotas and is labelled separately.')
    print('LIMITATIONS: exploratory unadjusted comparisons; OOF models share training rows, so fold independence is a reference-null assumption. Essay bootstrap does not account for prompt clustering or training dependence. Marginal length correlation cannot establish signal independence from length.')
    assert before == {p:sha(p) for p in INPUTS}
    for p in sorted(READS):
        print('READ_AUDIT '+p+' SHA256='+before[p])
    print(f'READ_GUARD artifact_reads={len(READS)}; allowlisted_only={READS<=set(INPUTS)}; blocked_attempts={len(BLOCKED)}; no Test prediction/label file opened; inputs_unchanged=True')
    print('ALL_NUMBERS_PRINTED=True')


if __name__ == '__main__':
    sys.addaudithook(audit)
    capture = io.StringIO()
    class Tee:
        def write(self, text):
            sys.__stdout__.write(text)
            capture.write(text)
        def flush(self):
            sys.__stdout__.flush()
    with threadpool_limits(limits=1), contextlib.redirect_stdout(Tee()):
        main()
    if '--append' in sys.argv:
        text = '\n\n'+HEADING+'\n\nExploratory development-only GroupKFold(5) evaluation. Producer: `scripts/week9b/tree_spread_oof.py`; command: `.venv/Scripts/python.exe -u scripts/week9b/tree_spread_oof.py --append`. No Test prediction or label file was opened.\n\n```text\n'+capture.getvalue()+'```\n'
        with DEST.open('ab') as stream:
            stream.write(text.encode('utf-8'))
        print('APPENDED_RESULTS_ONLY=True')
