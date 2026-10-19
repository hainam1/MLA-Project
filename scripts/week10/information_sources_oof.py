"""Exploratory prompt-held-out comparison of feature and text information sources.

Only the --append option writes an artifact: append-only Week 10 results.
All predictions, bootstrap draws and fitted models remain in memory.
"""
from pathlib import Path
import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import math
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'reports/week10/RESULTS_week10.md'
INPUTS = ['reports/week9/t3_eligible_development.csv',
          'reports/week9/t3_fold_composition.csv', 'outputs/phase6/feature_schema.json',
          'data/03_clean_ready_to_use/model_train_3128.csv',
          'data/03_clean_ready_to_use/validation_783.csv']
ALLOWED = {(ROOT / p).resolve() for p in INPUTS}
READS, BLOCKED = set(), []
SEED, N_BOOT = 42, 2000
CONFIG = {
    'status': 'exploratory development only; no hyperparameter search',
    'folds': 'GroupKFold(5), normalised_prompt, input sorted by essay_id string ascending',
    'seed': SEED, 'bootstrap_resamples': N_BOOT,
    'feature_RF': dict(n_estimators=300, max_features='sqrt', max_depth=10,
                       min_samples_leaf={'V': 2, 'G': 5}, random_state=42, n_jobs=1,
                       preprocessing='train-only median imputation'),
    'feature_Ridge': dict(alpha={'V': 100., 'G': .1},
                          preprocessing='train-only median imputation and StandardScaler'),
    'B1_TFIDF': dict(analyzer='word', ngram_range=[1, 2], min_df=5, max_df=1.,
                     sublinear_tf=True, lowercase=True, strip_accents=None,
                     stop_words=None, token_pattern=r'(?u)\b\w\w+\b',
                     norm='l2', use_idf=True, smooth_idf=True, max_features=None,
                     dtype='float64', input='essay_text only; no prompt name or engineered features'),
    'B1_Ridge': dict(alpha=10., fit_intercept=True, solver='lsqr', tol=1e-6, max_iter=10000),
    'B2_encoder_if_offline': dict(model='sentence-transformers/all-MiniLM-L6-v2',
                                device='cpu', local_files_only=True, trust_remote_code=False,
                                batch_size=32, normalize_embeddings=False),
    'B2_Ridge_if_offline': dict(alpha=10., fit_intercept=True, solver='lsqr', tol=1e-6, max_iter=10000),
    'large_error': 'max target absolute error >= 1.0',
    'queue': 'score descending, essay_id string ascending; ceil(0.20*n_fold)',
    'bootstrap': 'paired ordinary essay bootstrap, percentile [2.5,97.5], linear; no tuning/refitting/reranking',
}


def audit(event, args):
    if event == 'socket.connect':
        raise PermissionError('This analysis is offline; network connections are disabled')
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


def packages_first():
    print('EXPLORATORY DEVELOPMENT ONLY. Installed-package check runs before importing analysis libraries or fitting any model.', flush=True)
    print('COMMAND: ' + sys.executable + ' -m pip list', flush=True)
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True)
    print(result.stdout.decode('utf-8', errors='replace'), end='')
    print(result.stderr.decode('utf-8', errors='replace'), end='')
    print('PIP_LIST_EXIT_CODE=' + str(result.returncode))
    if result.returncode:
        uv = shutil.which('uv')
        assert uv, 'pip unavailable and uv not found; cannot verify environment'
        print('FALLBACK_REASON venv has no pip module; uv pip list reads the same venv metadata offline; nothing installed.')
        print('COMMAND: uv pip list --python ' + sys.executable + ' --offline', flush=True)
        result = subprocess.run([uv, 'pip', 'list', '--python', sys.executable, '--offline'], capture_output=True, check=True)
        print(result.stdout.decode('utf-8', errors='replace'), end='')
        print(result.stderr.decode('utf-8', errors='replace'), end='')
    availability = {}
    for name in ['sentence-transformers', 'transformers', 'torch', 'huggingface-hub',
                 'language-tool-python', 'gramformer', 'gingerit', 'errant', 'stanza', 'spacy', 'textblob']:
        try:
            availability[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            availability[name] = None
        print('PACKAGE ' + name + ' ' + str(availability[name] or 'NOT_INSTALLED'))
    return availability


def offline_encoder(availability):
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_DATASETS_OFFLINE'] = '1'
    base = Path(os.environ.get('HF_HOME', str(Path.home() / '.cache/huggingface')))
    hub = Path(os.environ.get('HUGGINGFACE_HUB_CACHE', str(base / 'hub')))
    print('OFFLINE_CACHE_CHECK path=' + str(hub) + '; exists=' + str(hub.is_dir()))
    torch_cache = Path(os.environ.get('SENTENCE_TRANSFORMERS_HOME', str(Path.home() / '.cache/torch/sentence_transformers')))
    print('OFFLINE_CACHE_CHECK path=' + str(torch_cache) + '; exists=' + str(torch_cache.is_dir()))
    required = ['sentence-transformers', 'transformers', 'torch']
    missing = [p for p in required if availability[p] is None]
    if missing:
        print('SKIP B2 frozen sentence encoder: required installed packages missing=' + ','.join(missing) + '; no encoder substituted; no weights/data downloaded.')
        return None
    candidates = sorted((hub / 'models--sentence-transformers--all-MiniLM-L6-v2' / 'snapshots').glob('*'))
    candidates += sorted(torch_cache.glob('*all-MiniLM-L6-v2*')) if torch_cache.is_dir() else []
    complete = [p for p in candidates if (p / 'modules.json').is_file() and
                ((p / 'model.safetensors').is_file() or (p / 'pytorch_model.bin').is_file())]
    if not complete:
        print('SKIP B2 frozen sentence encoder: exact configured small model is not available in checked offline caches; no encoder substituted; no weights/data downloaded.')
        return None
    from sentence_transformers import SentenceTransformer
    import torch
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    try:
        encoder = SentenceTransformer(str(complete[0]), device='cpu', local_files_only=True, trust_remote_code=False)
        encoder.eval()
    except Exception as error:
        print('SKIP B2 offline loading failed: ' + type(error).__name__ + '; no download or substitute attempted.')
        return None
    print('B2_OFFLINE_MODEL_PATH=' + str(complete[0]))
    return encoder


def optional_counter(availability):
    candidates = ['gramformer', 'gingerit']
    installed = [name for name in candidates if availability[name] is not None]
    if not installed:
        print('SKIP OPTIONAL SECOND GRAMMAR COUNTER: no second grammar-error counter installed (gramformer, gingerit absent). language-tool-python is the existing counter; spaCy and TextBlob are not substituted as independent grammar-error counters. No installation/download; no 32/random-sample text or Test file opened for this optional step.')
    else:
        print('SKIP OPTIONAL SECOND GRAMMAR COUNTER: installed candidates=' + ','.join(installed) + '; no verified independent offline counter resource configured. No installation/download or substitute.')


def load_data():
    f = pd.read_csv(ROOT / INPUTS[0], dtype={'essay_id': str}).sort_values('essay_id', kind='stable').reset_index(drop=True)
    composition = pd.read_csv(ROOT / INPUTS[1])
    composition = composition.loc[composition.split_type.eq('prompt_disjoint')]
    features = json.loads((ROOT / INPUTS[2]).read_text())
    assert len(f) == 3812 and f.essay_id.is_unique and f.normalised_prompt.nunique() == 44
    assert f.source_partition.eq('official_train').all() and f.privacy_review_status.eq('not_flagged').all()
    assert f.eligible.all() and set(f.split) == {'model_train', 'validation'} and len(features) == 14
    assert np.isfinite(f[features + ['Vocabulary', 'Grammar']].to_numpy()).all()
    texts = pd.concat([pd.read_csv(ROOT / p, usecols=['essay_id', 'essay_text', 'vocabulary', 'grammar'],
                                  dtype={'essay_id': str}, keep_default_na=False) for p in INPUTS[3:]], ignore_index=True)
    assert texts.essay_id.is_unique
    texts = texts.loc[texts.essay_id.isin(f.essay_id)].set_index('essay_id').loc[f.essay_id]
    assert len(texts) == 3812 and texts.essay_text.str.strip().ne('').all()
    assert np.array_equal(texts.vocabulary.to_numpy(), f.Vocabulary.to_numpy())
    assert np.array_equal(texts.grammar.to_numpy(), f.Grammar.to_numpy())
    print('DATA_JOIN eligible=3812; prompts=44; text-to-eligible-ID one-to-one=True; saved targets match clean development targets=True; model_train=' + str(int(f.split.eq('model_train').sum())) + '; validation=' + str(int(f.split.eq('validation').sum())))
    return f, composition, features, texts.essay_text.to_numpy()


def fit_oof(f, composition, features, texts, encoder):
    n = len(f)
    predictions = {name: np.full((n, 2), np.nan) for name in ['RF_feature', 'Ridge_feature', 'B1_TFIDF']}
    embeddings = None
    if encoder is not None:
        embeddings = encoder.encode(texts.tolist(), batch_size=32, show_progress_bar=False,
                                    normalize_embeddings=False, convert_to_numpy=True)
        assert embeddings.shape[0] == n and np.isfinite(embeddings).all()
        predictions['B2_embedding'] = np.full((n, 2), np.nan)
        print('B2_FROZEN_EMBEDDINGS shape=' + str(embeddings.shape) + '; encoder not fine-tuned; no score labels used by encoder.')
    folds = np.zeros(n, dtype=int)
    checks = []
    for fold, (train, held) in enumerate(GroupKFold(5).split(f, groups=f.normalised_prompt), 1):
        tr, val = f.iloc[train], f.iloc[held]
        saved = composition.loc[composition.fold.eq(fold)]
        assert val.groupby('normalised_prompt').size().to_dict() == saved.set_index('heldout_prompt').heldout_prompt_essays.to_dict()
        assert saved.train_essays.eq(len(train)).all() and saved.heldout_essays.eq(len(held)).all()
        assert not set(tr.normalised_prompt) & set(val.normalised_prompt)
        k = math.ceil(.2*len(held))
        assert saved.k.eq(k).all()
        # Fit vocabulary and IDF once on training text only; reuse for both targets.
        tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=5, max_df=1., sublinear_tf=True,
                               analyzer='word', lowercase=True, strip_accents=None, stop_words=None,
                               token_pattern=r'(?u)\b\w\w+\b', norm='l2', use_idf=True,
                               smooth_idf=True, max_features=None, dtype=np.float64)
        xtrain = tfidf.fit_transform(texts[train])
        xheld = tfidf.transform(texts[held])
        for j, (target, alpha, leaf) in enumerate([('Vocabulary', 100., 2), ('Grammar', .1, 5)]):
            rf = make_pipeline(SimpleImputer(strategy='median'), RandomForestRegressor(
                n_estimators=300, max_features='sqrt', max_depth=10, min_samples_leaf=leaf,
                random_state=42, n_jobs=1))
            ridge = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), Ridge(alpha=alpha))
            b1 = Ridge(**CONFIG['B1_Ridge'])
            rf.fit(tr[features], tr[target])
            ridge.fit(tr[features], tr[target])
            b1.fit(xtrain, tr[target])
            predictions['RF_feature'][held, j] = rf.predict(val[features])
            predictions['Ridge_feature'][held, j] = ridge.predict(val[features])
            predictions['B1_TFIDF'][held, j] = b1.predict(xheld)
            if embeddings is not None:
                b2 = Ridge(**CONFIG['B2_Ridge_if_offline'])
                b2.fit(embeddings[train], tr[target])
                predictions['B2_embedding'][held, j] = b2.predict(embeddings[held])
        folds[held] = fold
        checks.append(dict(fold=fold, train_n=len(train), n=len(held), heldout_prompts=val.normalised_prompt.nunique(),
            overlapping_prompts=0, k=k, matches_saved_prompt_composition=True, tfidf_vocabulary_size=len(tfidf.vocabulary_),
            heldout_id_sha256=hashlib.sha256('\n'.join(val.essay_id).encode()).hexdigest()))
        print(f'FIT_COMPLETE fold={fold}; train_n={len(train)}; n={len(held)}; k={k}; tfidf_vocabulary_size={len(tfidf.vocabulary_)}; no evaluation-fold vocabulary/IDF fit; frozen feature parameters unchanged.', flush=True)
    assert np.all(folds > 0) and all(np.isfinite(p).all() for p in predictions.values())
    table('FOLD_AND_TEXT_FIT_CHECKS', checks)
    return predictions, folds


def weighted_corr(x, y, weights):
    total = float(weights.sum())
    a, b = x-float(np.dot(weights, x))/total, y-float(np.dot(weights, y))/total
    numerator = float(np.dot(weights, a*b))
    aa, bb = float(np.dot(weights, a*a)), float(np.dot(weights, b*b))
    return numerator/np.sqrt(aa*bb) if aa > 0 and bb > 0 else np.nan


def weighted_ranks(inverse, weights):
    count = np.bincount(inverse, weights=weights)
    return (np.cumsum(count)-.5*count+.5)[inverse]


def intervals(values):
    values = np.asarray(values, dtype=float)
    valid = values[np.isfinite(values)]
    if not len(valid):
        return np.nan, np.nan, 0
    lo, hi = np.percentile(valid, [2.5, 97.5], method='linear')
    return float(lo), float(hi), len(valid)


def metrics_and_correlations(y, predictions):
    errors = {model: pred-y for model, pred in predictions.items()}
    rows = []
    for model, error in errors.items():
        for j, target in enumerate(['Vocabulary', 'Grammar']):
            absolute = float(abs(error[:, j]).sum())
            sse = float(np.dot(error[:, j], error[:, j]))
            centered = y[:, j]-y[:, j].mean()
            sst = float(np.dot(centered, centered))
            rows.append(dict(model=model, target=target, n=len(y), MAE=absolute/len(y), R2=1-sse/sst,
                MAE_arithmetic=f'{num(absolute)}/{len(y)}={num(absolute/len(y))}',
                R2_arithmetic=f'1-{num(sse)}/{num(sst)}={num(1-sse/sst)}'))
    table('OOF_MAE_AND_R_SQUARED (pooled essays, not mean of fold metrics)', rows)
    pairs = [('RF_feature', 'Ridge_feature')]
    for source in predictions:
        if source.startswith('B'):
            pairs.extend([(source, 'RF_feature'), (source, 'Ridge_feature')])
    variables = {(model, j): error[:, j] for model, error in errors.items() for j in range(2)}
    inverse = {key: np.unique(value, return_inverse=True)[1] for key, value in variables.items()}
    specs = [(j, a, b, method) for j in range(2) for a, b in pairs for method in ['Pearson', 'Spearman']]
    samples = {spec: [] for spec in specs}
    n = len(y)
    rng = np.random.default_rng(SEED)
    for resample in range(N_BOOT):
        weights = np.bincount(rng.integers(0, n, n), minlength=n)
        ranks = {key: weighted_ranks(inv, weights) for key, inv in inverse.items()}
        for spec in specs:
            j, a, b, method = spec
            source = variables if method == 'Pearson' else ranks
            samples[spec].append(weighted_corr(source[(a, j)], source[(b, j)], weights))
        if resample == 0:
            # Verify exact equivalence to direct repeated-row bootstrap ranks.
            repeated = np.repeat(np.arange(n), weights)
            for j, a, b, method in specs:
                direct = np.corrcoef(variables[(a, j)][repeated], variables[(b, j)][repeated])[0, 1] if method == 'Pearson' else spearmanr(variables[(a, j)][repeated], variables[(b, j)][repeated]).statistic
                assert np.isclose(direct, samples[(j, a, b, method)][-1], rtol=0, atol=1e-12)
    corr_rows = []
    for spec in specs:
        j, a, b, method = spec
        x, z = variables[(a, j)], variables[(b, j)]
        if method == 'Spearman':
            x, z = rankdata(x, method='average'), rankdata(z, method='average')
        xc, zc = x-x.mean(), z-z.mean()
        xx, zz, xz = float(np.dot(xc, xc)), float(np.dot(zc, zc)), float(np.dot(xc, zc))
        value = xz/np.sqrt(xx*zz)
        lo, hi, valid = intervals(samples[spec])
        corr_rows.append(dict(target=['Vocabulary', 'Grammar'][j], model_a=a, model_b=b, method=method,
            n=n, correlation=value, below_0_95=bool(value < .95), CI_low=lo, CI_high=hi,
            entire_CI_below_0_95=bool(hi < .95), bootstrap_valid=valid, bootstrap_skipped=N_BOOT-valid,
            arithmetic=f'{num(xz)}/sqrt({num(xx)}*{num(zz)})={num(value)}'))
    print('CORRELATION_BOOTSTRAP exact tied average ranks recalculated under repeated observations via weighted ranks; paired essay draws, 2000, default_rng(42), input essay_id ascending; first draw verified against direct repeated-row scipy Spearman / numpy Pearson. No prompt clustering or model refits.')
    table('SIGNED_ERROR_CORRELATIONS_WITH_95_PERCENT_ESSAY_BOOTSTRAP_CI', corr_rows)
    return errors, corr_rows


def select_queue(ids, scores, folds):
    selected = np.zeros(len(ids), dtype=bool)
    probabilities = np.zeros(len(ids))
    for fold in range(1, 6):
        index = np.flatnonzero(folds == fold)
        k = math.ceil(.2*len(index))
        order = np.lexsort((ids[index], -scores[index]))
        selected[index[order[:k]]] = True
        probabilities[index] = k/len(index)
    return selected, probabilities


def auc(y, inverse, weights):
    positive = np.bincount(inverse, weights=weights*y)
    negative = np.bincount(inverse, weights=weights*(~y), minlength=len(positive))
    pos, neg = float(positive.sum()), float(negative.sum())
    if pos == 0 or neg == 0:
        return np.nan
    u = float(np.dot(positive, np.cumsum(negative)-.5*negative))
    return u/(pos*neg)


def capture_rows(source, anchor, y, scores, queues, folds):
    rows = []
    for scope, mask in [('fold'+str(i), folds == i) for i in range(1, 6)] + [('pooled', np.ones(len(y), dtype=bool))]:
        n, K = int(mask.sum()), int(y[mask].sum())
        for signal in ['D_old', 'D_new']:
            selected = queues[signal] & mask
            k, caught = int(selected.sum()), int((selected & y).sum())
            if scope != 'pooled':
                expected = k*K/n
                p = float(hypergeom.sf(caught-1, n, K, k))
                formula = f'hypergeom.sf({caught-1},{n},{K},{k})'
                arithmetic = f'{k}*{K}/{n}={num(expected)}'
            else:
                terms, distribution = [], np.array([1.])
                for fold in range(1, 6):
                    m = folds == fold
                    nf, Kf, kf = int(m.sum()), int(y[m].sum()), int((queues[signal] & m).sum())
                    terms.append((kf, Kf, nf))
                    distribution = np.convolve(distribution, hypergeom.pmf(np.arange(min(kf, Kf)+1), nf, Kf, kf))
                assert abs(distribution.sum()-1) < 1e-12
                expected = sum(kf*Kf/nf for kf, Kf, nf in terms)
                p = float(distribution[caught:].sum())
                formula = f'P(sum fold Hypergeom >= {caught}); exact PMF convolution'
                arithmetic = '+'.join(f'{kf}*{Kf}/{nf}' for kf, Kf, nf in terms) + '=' + num(expected)
            rows.append(dict(source=source, anchor=anchor, scope=scope, signal=signal, n=n, K=K, k=k, caught=caught,
                capture=caught/K if K else None, capture_arithmetic=f'{caught}/{K}={num(caught/K)}' if K else 'undefined: K=0',
                expected=expected, expected_arithmetic=arithmetic, caught_minus_expected=caught-expected,
                exact_p=p, exact_p_formula=formula))
    table('CAPTURE_CAUGHT_VS_EXPECTED_AND_EXACT_P (same labels and rows for both signals)', rows)
    return rows


def paired_queue_bootstrap(source, anchor, label, scores, queues, probabilities, folds):
    auc_rows, comparison_rows = [], []
    for scope, mask in [('fold'+str(i), folds == i) for i in range(1, 6)] + [('pooled', np.ones(len(label), dtype=bool))]:
        y = label[mask]
        n, K = len(y), int(y.sum())
        inverse = {name: np.unique(values[mask], return_inverse=True)[1] for name, values in scores.items()}
        selected = {name: queue[mask] for name, queue in queues.items()}
        rate = probabilities[mask]
        one = np.ones(n)
        point_aucs = {name: auc(y, inv, one) for name, inv in inverse.items()}
        caught = {name: int((queue & y).sum()) for name, queue in selected.items()}
        expected = float(np.dot(y.astype(int), rate))
        samples = {name: [] for name in ['auc_old', 'auc_new', 'delta_auc', 'delta_caught', 'delta_capture', 'new_excess_random', 'old_excess_random']}
        rng = np.random.default_rng(SEED)
        for resample in range(N_BOOT):
            w = np.bincount(rng.integers(0, n, n), minlength=n)
            old_auc, new_auc = auc(y, inverse['D_old'], w), auc(y, inverse['D_new'], w)
            old_caught, new_caught = [float(np.dot(w, y & selected[name])) for name in ['D_old', 'D_new']]
            expected_boot = float(np.dot(w, y*rate))
            Kboot = float(np.dot(w, y))
            for key, value in [('auc_old', old_auc), ('auc_new', new_auc), ('delta_auc', new_auc-old_auc),
                               ('delta_caught', new_caught-old_caught),
                               ('delta_capture', (new_caught-old_caught)/Kboot if Kboot else np.nan),
                               ('new_excess_random', new_caught-expected_boot), ('old_excess_random', old_caught-expected_boot)]:
                samples[key].append(value)
            if resample == 0:
                repeated = np.repeat(np.arange(n), w)
                for name, score in scores.items():
                    yy, ss = y[repeated], score[mask][repeated]
                    if yy.any() and (~yy).any():
                        ranks = rankdata(ss)
                        pos, neg = int(yy.sum()), int((~yy).sum())
                        direct = (float(ranks[yy].sum())-pos*(pos+1)/2)/(pos*neg)
                        assert np.isclose(direct, old_auc if name == 'D_old' else new_auc, rtol=0, atol=1e-12)
        for name, key in [('D_old', 'auc_old'), ('D_new', 'auc_new')]:
            lo, hi, valid = intervals(samples[key])
            ranks = rankdata(scores[name][mask])
            u = float(ranks[y].sum())-K*(K+1)/2
            assert np.isclose(u/(K*(n-K)), point_aucs[name], atol=1e-12, rtol=0)
            auc_rows.append(dict(source=source, anchor=anchor, scope=scope, signal=name, n=n, K=K,
                AUROC=point_aucs[name], CI_low=lo, CI_high=hi, bootstrap_valid=valid, bootstrap_skipped=N_BOOT-valid,
                arithmetic=f'{num(u)}/({K}*{n-K})={num(point_aucs[name])}'))
        points = {'delta_auc': point_aucs['D_new']-point_aucs['D_old'],
                  'delta_caught': caught['D_new']-caught['D_old'],
                  'delta_capture': (caught['D_new']-caught['D_old'])/K if K else np.nan,
                  'new_excess_random': caught['D_new']-expected, 'old_excess_random': caught['D_old']-expected}
        arithmetic = {'delta_auc': f'{num(point_aucs["D_new"])}-{num(point_aucs["D_old"])}',
                      'delta_caught': f'{caught["D_new"]}-{caught["D_old"]}',
                      'delta_capture': f'({caught["D_new"]}-{caught["D_old"]})/{K}',
                      'new_excess_random': f'{caught["D_new"]}-{num(expected)}',
                      'old_excess_random': f'{caught["D_old"]}-{num(expected)}'}
        record = dict(source=source, anchor=anchor, scope=scope, n=n, K=K,
                      caught_new=caught['D_new'], caught_old=caught['D_old'], expected=expected)
        for key, value in points.items():
            lo, hi, valid = intervals(samples[key])
            record.update({key: value, key+'_CI_low': lo, key+'_CI_high': hi,
                           key+'_bootstrap_valid': valid, key+'_arithmetic': arithmetic[key]+'='+num(value)})
        comparison_rows.append(record)
    table('AUROC_95_PERCENT_ESSAY_BOOTSTRAP_CI (both signals; direct rank arithmetic)', auc_rows)
    table('PAIRED_NEW_VS_OLD_AND_RANDOM_REFERENCE_95_PERCENT_CI', comparison_rows)
    print('QUEUE_BOOTSTRAP_METHOD seed=42, 2000 paired essay resamples within each displayed scope; fixed scores and original fold queues; no reranking/refit/budget recomputation. Excess-vs-random uses each original fold rate k_f/n_f times the resampled large-error labels. Pooled essay draws are not stratified by fold. AUC uses exact weighted tied ranks, first draw checked against direct repeated rows. CIs condition on fitted OOF models, not retraining.')
    return auc_rows, comparison_rows


def review_and_shared(f, y, predictions, errors, folds):
    old_large = {name: np.max(abs(error), axis=1) >= 1 for name, error in errors.items()}
    A1 = old_large['RF_feature']
    A3old = A1 & old_large['Ridge_feature']
    assert int(A1.sum()) == 386 and int(A3old.sum()) == 276
    print('BASELINE_REPRODUCTION A1_RF_large_errors=386; A3_old_RF_and_Ridge_large_errors=276; fixed frozen parameters and saved prompt folds reproduce previous counts.')
    ids = f.essay_id.to_numpy()
    old_score = np.max(abs(predictions['RF_feature']-predictions['Ridge_feature']), axis=1)
    old_queue, probabilities = select_queue(ids, old_score, folds)
    assert int((old_queue & A1).sum()) == 88
    all_evidence = []
    for source in predictions:
        if not source.startswith('B'):
            continue
        new_score = np.max(abs(predictions['RF_feature']-predictions[source]), axis=1)
        new_queue, new_rates = select_queue(ids, new_score, folds)
        assert np.array_equal(probabilities, new_rates)
        scores, queues = {'D_old': old_score, 'D_new': new_score}, {'D_old': old_queue, 'D_new': new_queue}
        A3new = A1 & old_large[source]
        print('SOURCE_PAIRING ' + source + '; D_new=max(abs(RF_feature_V-B_V),abs(RF_feature_G-B_G)); D_old=max(abs(RF_feature_V-Ridge_feature_V),abs(RF_feature_G-Ridge_feature_G)); A3_new=A1 and max(abs(B-y))>=1, either target may trigger each model.')
        for anchor, label in [('A1_RF_anchor', A1), ('A3_new_RF_and_B', A3new)]:
            captures = capture_rows(source, anchor, label, scores, queues, folds)
            auc_rows, comparisons = paired_queue_bootstrap(source, anchor, label, scores, queues, probabilities, folds)
            cap = next(r for r in captures if r['scope'] == 'pooled' and r['signal'] == 'D_new')
            old = next(r for r in captures if r['scope'] == 'pooled' and r['signal'] == 'D_old')
            ac = next(r for r in auc_rows if r['scope'] == 'pooled' and r['signal'] == 'D_new')
            comparison = next(r for r in comparisons if r['scope'] == 'pooled')
            all_evidence.append(dict(source=source, anchor=anchor, n=cap['n'], K=cap['K'], k=cap['k'],
                caught_new=cap['caught'], expected=cap['expected'], exact_p_new=cap['exact_p'], caught_old=old['caught'],
                new_excess_random_CI_low=comparison['new_excess_random_CI_low'], new_excess_random_CI_high=comparison['new_excess_random_CI_high'],
                new_minus_old_caught=comparison['delta_caught'], new_minus_old_caught_CI_low=comparison['delta_caught_CI_low'], new_minus_old_caught_CI_high=comparison['delta_caught_CI_high'],
                AUROC_new=ac['AUROC'], AUROC_new_CI_low=ac['CI_low'], AUROC_new_CI_high=ac['CI_high'],
                AUROC_new_minus_old=comparison['delta_auc'], AUROC_delta_CI_low=comparison['delta_auc_CI_low'], AUROC_delta_CI_high=comparison['delta_auc_CI_high']))
        shared_rows = []
        for scope, mask in [('fold'+str(i), folds == i) for i in range(1, 6)] + [('pooled', np.ones(len(y), dtype=bool))]:
            old_shared = A3old & mask
            K = int(old_shared.sum())
            still_wrong = int((old_shared & old_large[source]).sum())
            fixed = int((old_shared & ~old_large[source]).sum())
            equal_boundary = int((old_shared & (np.max(abs(errors[source]), axis=1) == 1.)).sum())
            assert still_wrong+fixed == K
            shared_rows.append(dict(source=source, scope=scope, A3_old=K, also_wrong_under_B=still_wrong,
                fixed_B_max_error_lt_1=fixed, B_max_error_exactly_1=equal_boundary,
                also_wrong_share=still_wrong/K, fixed_share=fixed/K,
                arithmetic=f'{still_wrong}+{fixed}={K}; also_wrong={still_wrong}/{K}={num(still_wrong/K)}; fixed={fixed}/{K}={num(fixed/K)}'))
        table('OLD_SHARED_ERROR_SET_UNDER_NEW_SOURCE (fixed means both B target errors strictly <1; >=1 remains wrong)', shared_rows)
    table('POOLED_EVIDENCE_FOR_FINAL_INTERPRETATION', all_evidence)


def main():
    availability = packages_first()
    config_digest = hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()
    print('FIXED_CONFIGURATION_BEFORE_ANY_FIT ' + json.dumps(CONFIG, sort_keys=True))
    print('FIXED_CONFIGURATION_SHA256=' + config_digest)
    print('SCRIPT_SHA256_BEFORE_FIT=' + sha('scripts/week10/information_sources_oof.py'))
    print('NO_DOWNLOAD_COMMAND_RUN=True; no model weights or data downloaded; only installed packages and offline caches checked.')
    global np, pd, scipy, sklearn, hypergeom, rankdata, spearmanr, GroupKFold
    global TfidfVectorizer, RandomForestRegressor, SimpleImputer, Ridge, make_pipeline, StandardScaler
    import numpy as np
    import pandas as pd
    import scipy
    import sklearn
    from scipy.stats import hypergeom, rankdata, spearmanr
    from sklearn.model_selection import GroupKFold
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits
    np.random.seed(SEED)
    print(f'ANALYSIS_VERSIONS Python={sys.version.split()[0]}; numpy={np.__version__}; pandas={pd.__version__}; scipy={scipy.__version__}; sklearn={sklearn.__version__}')
    encoder = offline_encoder(availability)
    optional_counter(availability)
    before = {p: sha(p) for p in INPUTS}
    with threadpool_limits(limits=1):
        f, composition, features, texts = load_data()
        predictions, folds = fit_oof(f, composition, features, texts, encoder)
        y = f[['Vocabulary', 'Grammar']].to_numpy()
        errors, correlations = metrics_and_correlations(y, predictions)
        review_and_shared(f, y, predictions, errors, folds)
    assert config_digest == hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()
    assert before == {p: sha(p) for p in INPUTS}
    print('LIMITATIONS exploratory, unadjusted comparisons; same development reused. Hypergeometric p uses a random-queue reference conditional on labels and fold budgets; pooled convolution assumes independent fold reference draws. Overlapping OOF training sets and prompt clustering are not modeled by ordinary essay-bootstrap CIs. TF-IDF is a different representation, not proof of statistical independence from feature inputs.')
    for path in sorted(READS):
        print('READ_AUDIT ' + path + ' SHA256=' + before[path])
    print(f'READ_GUARD artifact_reads={len(READS)}; allowlisted_only={READS <= set(INPUTS)}; blocked_attempts={len(BLOCKED)}; no Test file opened; inputs_unchanged=True; configurations_unchanged=True; no prediction/model files saved; no essay text printed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--append', action='store_true')
    args = parser.parse_args()
    sys.addaudithook(audit)
    previous = DEST.read_bytes()
    heading = '## Week 10 exploratory OOF comparison of feature and text information sources'
    if args.append:
        assert heading.encode() not in previous, 'Refusing duplicate results append'
    captured = io.StringIO()
    class Tee:
        def write(self, text):
            sys.__stdout__.write(text)
            captured.write(text)
        def flush(self):
            sys.__stdout__.flush()
    with contextlib.redirect_stdout(Tee()):
        main()
    if args.append:
        section = ('\n\n' + heading + '\n\nExploratory development-only analysis. Producer: `scripts/week10/information_sources_oof.py`. '
                   'Command: `.venv/Scripts/python.exe -B -u scripts/week10/information_sources_oof.py --append`. '
                   'Fixed configurations were printed before fitting; no search, installation or download.\n\n```text\n' + captured.getvalue() + '```\n')
        with DEST.open('ab') as stream:
            stream.write(section.encode('utf-8'))
        assert DEST.read_bytes().startswith(previous)
        print('APPEND_PREFIX_UNCHANGED=True; previous_report_SHA256=' + hashlib.sha256(previous).hexdigest())
