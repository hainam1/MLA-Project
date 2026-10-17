"""Exploratory development/Validation diagnosis; stdout only, optional append.

Run: .venv/Scripts/python.exe -u scripts/week9b/diagnose.py --append
No frozen model is fitted. A read allowlist guards repository artifact access.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import math
import os
import sys

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
import joblib
import numpy as np
import pandas as pd
from scipy.stats import hypergeom
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "reports/week9/RESULTS_week9.md"
MODEL_NAMES = [f"{m}_{t}.joblib" for m in ("ridge", "random_forest")
               for t in ("vocabulary", "grammar")]
INPUTS = ["outputs/phase6/validation_predictions.csv",
          "outputs/phase6/artifact_manifest.json", "outputs/phase6/feature_schema.json",
          "data/05_model_features/development_features_with_targets.csv",
          "reports/week9/t3_eligible_development.csv",
          "reports/week9/t3_heldout_predictions.csv",
          *["outputs/phase6/" + name for name in MODEL_NAMES]]
ALLOWED = {str((ROOT / p).resolve()).casefold() for p in INPUTS}
READS, BLOCKED = set(), []


def audit(event, args):
    if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return
    if not rel.parts or rel.parts[0] not in {"data", "outputs", "docs", "reports"}:
        return  # Interpreter/library code is outside the artifact guard.
    mode = args[1]
    writing = isinstance(mode, str) and any(c in mode for c in "wax+")
    if path == DEST and isinstance(mode, str) and mode.startswith("a") and args[2] & os.O_APPEND and not args[2] & os.O_TRUNC:
        return  # Append only; existing report contents are never read.
    if writing or str(path).casefold() not in ALLOWED:
        BLOCKED.append(rel.as_posix())
        raise PermissionError("Artifact access outside allowlist: " + rel.as_posix())
    READS.add(rel.as_posix())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def read(path):
    return pd.read_csv(ROOT / path, dtype={"essay_id": str})


def table(title, rows):
    print(title)
    print(pd.DataFrame(rows).to_csv(index=False, float_format="%.17g", lineterminator="\n"), end="", flush=True)


def fraction(a, b):
    return f"{a}/{b}={a/b:.17g}" if b else f"{a}/{b}=undefined"


def ranked(frame, score, k):
    return frame.assign(score=np.asarray(score)).sort_values(
        ["score", "essay_id"], ascending=[False, True], kind="stable").head(k).index


def metric(frame, large, score, signal):
    n, K = len(frame), int(np.sum(large))
    k = math.ceil(.20*n)
    caught = int(np.asarray(large)[ranked(frame, score, k)].sum())
    return dict(signal=signal, N=n, K=K, k=k, caught=caught,
                capture=fraction(caught, K), expected_random=k*K/n,
                expected_arithmetic=f"{k}*{K}/{n}={k*K/n:.17g}",
                p=float(hypergeom.sf(caught-1, n, K, k)),
                p_formula=f"hypergeom.sf({caught-1},{n},{K},{k})")


def main():
    print("EXPLORATORY ONLY; development and Validation; seed=42; no search; no frozen-model fitting.")
    print("L=max(abs(y_V-RF_V),abs(y_G-RF_G))>=1; D=max(abs(RF_V-Ridge_V),abs(RF_G-Ridge_G)); k=ceil(.20*N); ties=essay_id string ascending.")
    before = {p: sha(p) for p in INPUTS}
    manifest = json.loads((ROOT / INPUTS[1]).read_text())
    features = json.loads((ROOT / INPUTS[2]).read_text())
    assert len(features) == 14
    models = {}
    for name in MODEL_NAMES:
        path = "outputs/phase6/" + name
        assert before[path].upper() == manifest["sha256"][name]
        models[name[:-7]] = joblib.load(ROOT / path)
    dev = read(INPUTS[3])
    assert dev.essay_id.is_unique and dev.source_partition.eq("official_train").all()
    assert set(dev.split) == {"model_train", "validation"}
    eligible=read(INPUTS[4]).sort_values('essay_id',kind='stable').reset_index(drop=True)
    assert len(eligible)==3812 and eligible.essay_id.is_unique
    assert eligible.privacy_review_status.eq('not_flagged').all()
    dev=dev.loc[dev.essay_id.isin(set(eligible.essay_id))].copy()
    pred = read(INPUTS[0])
    f = pred.merge(dev, on="essay_id", validate="one_to_one", sort=False).reset_index(drop=True)
    assert len(f) == 762 and f.split.eq("validation").all()
    assert np.isfinite(f[features + ["Vocabulary", "Grammar"]].to_numpy()).all()
    train = dev.loc[dev.split.eq("model_train")]
    assert len(train) == 3050
    centers, tree_stds, max_deltas = {}, [], {}
    for target in ("vocabulary", "grammar"):
        rf, ridge = models["random_forest_"+target], models["ridge_"+target]
        assert len(rf.named_steps["model"].estimators_) == 300
        x = rf[:-1].transform(f[features])
        trees = np.array([tree.predict(x) for tree in rf.named_steps["model"].estimators_])
        tree_stds.append(trees.std(axis=0, ddof=0))
        for name, values in [("random_forest", trees.mean(axis=0)),
                             ("ridge", ridge.predict(f[features]))]:
            delta = float(np.max(abs(values-f[name+"_"+target].to_numpy())))
            assert delta < 1e-9, (name, target, delta)
            max_deltas[name+"_"+target] = delta
        centers[target] = float(np.median(ridge.predict(train[features])))
    print("FROZEN_MODEL_VALIDATION max_abs_saved_prediction_difference="+json.dumps(max_deltas, sort_keys=True))
    print("RIDGE_TRAIN_CENTERS n=3050; recomputed from frozen Ridge predictions="+json.dumps(centers, sort_keys=True))
    a1 = np.maximum(abs(f.Vocabulary-f.random_forest_vocabulary), abs(f.Grammar-f.random_forest_grammar)) >= 1
    a2 = np.maximum(abs(f.Vocabulary-f.ridge_vocabulary), abs(f.Grammar-f.ridge_grammar)) >= 1
    D = np.maximum(abs(f.random_forest_vocabulary-f.ridge_vocabulary), abs(f.random_forest_grammar-f.ridge_grammar))
    n, K, k, med = len(f), int(a1.sum()), math.ceil(.2*len(f)), float(np.median(D))
    assert (n,K,k) == (762,69,153)
    groups = {"RF-only (A1 minus A2)": a1 & ~a2,
              "Ridge-only (A2 minus A1; outside K)": a2 & ~a1,
              "both (A3)": a1 & a2}
    table("STEP1A anchors", [dict(anchor=name, count=int(mask.sum()), share_of_RF_K=fraction(int(mask.sum()),K))
                                 for name,mask in [("A1 RF",a1),("A2 Ridge",a2),("A3 both",a1&a2),("union",a1|a2)]])
    print(f"STEP1B D population median={med:.17g}; below means strict <; all shares within group unless labelled /K.")
    table("STEP1AB partition", [dict(group=name, count=int(mask.sum()), share_of_RF_K=fraction(int(mask.sum()),K),
          median_D=float(np.median(D[mask])) if mask.any() else np.nan,
          D_below_population_median=fraction(int((mask & (D < med)).sum()),int(mask.sum())),
          D_below_0_1=fraction(int((mask & (D < .1)).sum()),int(mask.sum()))) for name,mask in groups.items()])
    print(f"PARTITION RF_K={int((a1&~a2).sum())}+{int((a1&a2).sum())}={K}; union={int((a1&~a2).sum())}+{int((a2&~a1).sum())}+{int((a1&a2).sum())}={int((a1|a2).sum())}; Ridge-only is not part of RF K.")
    direction = []
    for t,y in [("vocabulary",f.Vocabulary),("grammar",f.Grammar)]:
        above = (y > f["ridge_"+t]) & (y > f["random_forest_"+t])
        below = (y < f["ridge_"+t]) & (y < f["random_forest_"+t])
        for scope,mask in [("RF-large essays (either target)",a1),
                           ("RF-large on this target",abs(y-f["random_forest_"+t])>=1)]:
            den=int(mask.sum()); upper=int((mask&above).sum()); lower=int((mask&below).sum())
            direction.append(dict(target=t,scope=scope,n=den,above_both=fraction(upper,den),below_both=fraction(lower,den),
                  between_or_equal=fraction(den-upper-lower,den),
                  true_mean_group=float(y[mask].mean()),true_mean_overall=float(y.mean()),
                  group_mean_arithmetic=f"{float(y[mask].sum()):.17g}/{den}",
                  overall_mean_arithmetic=f"{float(y.sum()):.17g}/{n}"))
    table("STEP1C direction (strict above/below; between/equality retained)",direction)
    selected=ranked(f,D,k); cutoff=float(D.loc[selected].iloc[-1])
    caught=int(a1.loc[selected].sum()); low=int((a1 & (D<cutoff)).sum()); equal=int((a1 & (D==cutoff)).sum())
    table("STEP1D fixed D cutoff", [dict(N=n,K=K,k=k,kth_D=cutoff,caught_by_D=caught,
          below_cutoff=fraction(low,K),large_equal_cutoff=equal,
          large_above_cutoff=int((a1&(D>cutoff)).sum()),
          eligible_large_at_or_above=int((a1&(D>=cutoff)).sum()),
          optimistic_cap_within_cutoff=min(k,int((a1&(D>=cutoff)).sum())),
          capture=fraction(caught,K))])
    print(f"CUTOFF arithmetic: {K}-{low}={K-low} large errors at/above cutoff; upper bound=min({k},{K-low})={min(k,K-low)}; fixed D ranking caught={caught}; excluded={fraction(low,K)}. Below-cutoff exclusion applies to this fixed ranking/budget, not an arbitrary replacement signal.")
    rf_ext=np.maximum(abs(f.random_forest_vocabulary-centers['vocabulary']),abs(f.random_forest_grammar-centers['grammar']))
    signals={"Disagreement":D,"RF tree std (ddof=0; max targets)":np.maximum(*tree_stds),
             "RF extremity vs Ridge-train medians":rf_ext,"Shortest-first":-f.word_count,"Longest-first":f.word_count}
    rows=[metric(f,a1,score,name) for name,score in signals.items()]
    assert rows[0]['caught']==15
    table("STEP2 Validation signals",rows)
    # Optional error model: reuse saved base OOF values, never fit either base model.
    oof=read(INPUTS[5]); oof=oof.loc[oof.split_type.eq('prompt_disjoint')].copy()
    assert len(eligible)==len(oof)==3812 and eligible.essay_id.is_unique and oof.essay_id.is_unique
    assert eligible.privacy_review_status.eq('not_flagged').all()
    assert eligible.source_partition.eq('official_train').all()
    g=eligible.merge(oof[['essay_id','fold','normalised_prompt','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G']],
                     on=['essay_id','normalised_prompt'],validate='one_to_one',sort=False).reset_index(drop=True)
    assert len(g)==3812 and g.normalised_prompt.nunique()==44
    assert np.array_equal(g.Vocabulary,g.y_V) and np.array_equal(g.Grammar,g.y_G)
    x=g[features+['RF_V','RF_G','Ridge_V','Ridge_G']]
    error=np.maximum(abs(g.y_V-g.RF_V),abs(g.y_G-g.RF_G)).to_numpy()
    score=np.full(len(g),np.nan)
    fold_rows=[]
    for fold,(tr,held) in enumerate(GroupKFold(5).split(g,groups=g.normalised_prompt),1):
        assert (g.loc[held,'fold']==fold).all()
        assert not set(g.loc[tr,'normalised_prompt']) & set(g.loc[held,'normalised_prompt'])
        meta=RandomForestRegressor(n_estimators=300,max_depth=6,random_state=42,n_jobs=1)
        meta.fit(x.iloc[tr],error[tr]); score[held]=meta.predict(x.iloc[held])
        fold_rows.append(dict(fold=fold,training_n=len(tr),heldout_n=len(held),overlapping_prompts=0))
    assert np.isfinite(score).all()
    table("STEP3 GroupKFold(5) error-model folds",fold_rows)
    large=error>=1; auc=float(roc_auc_score(large,score)); rng=np.random.default_rng(42)
    boots=[]
    for _ in range(2000):
        ix=rng.integers(0,len(g),len(g))
        if 0<int(large[ix].sum())<len(ix):
            boots.append(roc_auc_score(large[ix],score[ix]))
    row=metric(g,large,score,'Error-model OOF; pooled global top20%')
    row.update(AUROC=auc,CI_low=float(np.percentile(boots,2.5)),CI_high=float(np.percentile(boots,97.5)),
               bootstrap_resamples=2000,valid_resamples=len(boots),skipped_resamples=2000-len(boots))
    table("STEP3 saved-base-OOF exploratory error model",[row])
    print("STEP3 BUDGET: concatenate 5 meta-heldout score sets, then global k=ceil(.20*3812)=763; hypergeometric p uses that global uniform-selection reference.")
    print("STEP3 LIMITATION: this is second-stage GroupKFold on existing base OOF predictions, not fully nested cross-fitting. Base models generating meta-training rows can have seen the meta-heldout groups. Therefore this error-model result is potentially optimistic and is not an unbiased estimate for unseen prompts. Fully nested evaluation would require refitting base models and was not performed.")
    print("BOOTSTRAP: 2000 ordinary essay resamples with replacement, seed=42, percentile 95% CI; does not account for prompt clustering or cross-fitting dependence.")
    significant=[r['signal'] for r in rows if r['p']<.05]
    print("STEP2 p<0.05 (uncorrected multiple exploratory comparisons): "+repr(significant))
    print("STEP3 nominal p<0.05="+str(row['p']<.05)+"; subject to the nested-cross-fitting limitation above.")
    assert before=={p:sha(p) for p in INPUTS}
    for p in sorted(READS):
        print('READ_AUDIT '+p+' SHA256='+before[p])
    print(f"READ_GUARD artifact_reads={len(READS)}; allowlisted_only={READS<=set(INPUTS)}; blocked_attempts={len(BLOCKED)}; source_hashes_unchanged=True; no Test file opened.")


if __name__ == '__main__':
    sys.addaudithook(audit)
    output=io.StringIO()
    with threadpool_limits(limits=1), contextlib.redirect_stdout(output):
        main()
    raw=output.getvalue()
    print(raw,end='',flush=True)
    if '--append' in sys.argv:
        section='\n\n## Week 9b — exploratory development/Validation diagnosis\n\nProducer: `scripts/week9b/diagnose.py`; command: `.venv/Scripts/python.exe -u scripts/week9b/diagnose.py --append`. No Test input is used. The error-model results have the second-stage cross-fitting limitation printed below. Existing report bytes are preserved by opening in append-only mode.\n\n```text\n'+raw+'```\n'
        with DEST.open('ab') as stream:
            stream.write(section.encode('utf-8'))
        print('APPEND_ONLY reports/week9/RESULTS_week9.md; no extra report files written.')
