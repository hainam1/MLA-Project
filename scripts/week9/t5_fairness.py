"""Validation A1 descriptive capture within groups. No tests or fairness claims."""
import sys
import numpy as np
import pandas as pd
from t456_evidence import *
from validation_common import load

def main():
    print(LABEL,flush=True)
    print('COMMAND: .venv/Scripts/python.exe -u scripts/week9/t5_fairness.py')
    print('SEED=42; Random=1000 global uniform selections without replacement, each 153 of 762; group summaries use those same selections, not separate group budgets')
    paths=['data/03_clean_ready_to_use/validation_783.csv','outputs/phase6/validation_predictions.csv','data/05_model_features/development_features_with_targets.csv','docs/data/error_analysis/manual_error_review.csv']
    before={p:sha((ROOT/p).read_bytes()) for p in paths}
    f=load()
    demographics=pd.read_csv(ROOT/paths[0],usecols=['essay_id','gender','grade','race_ethnicity','ses'],dtype={'essay_id':str,'grade':str},keep_default_na=False)
    assert demographics.essay_id.is_unique
    f=f.merge(demographics,on='essay_id',how='left',validate='one_to_one',sort=False)
    assert len(f)==762 and all(f[c].notna().all() for c in ['gender','grade','race_ethnicity','ses'])
    y=f.large_error.to_numpy(dtype=bool)
    rng=np.random.default_rng(42)
    selections=np.zeros((1000,762),dtype=bool)
    for i in range(1000): selections[i,rng.choice(762,size=153,replace=False)]=True
    assert (selections.sum(axis=1)==153).all()
    global_caught=selections[:,y].sum(axis=1)
    assert int(global_caught.sum())==13946 and int(f.loc[f.selected_by_Disagreement,'large_error'].sum())==15
    print('FROZEN_REFERENCE_ASSERT selected=153; A1 positives=69; Disagreement caught=15; Random total_caught=13946; Random mean=13946/1000=13.946')
    rows=[]; drawrows=[]; coverage=[]
    for attribute,column in [('Gender','gender'),('Grade','grade'),('Race/Ethnicity','race_ethnicity'),('SES','ses')]:
        for group,sub in f.groupby(column,dropna=False,sort=True):
            N=len(sub); ids=sub.index.to_numpy(); K=int(sub.large_error.sum())
            if N<20:
                coverage.append(dict(attribute=attribute,group=group,N=N,K=K,reported=False,reason='N < 20'))
                continue
            coverage.append(dict(attribute=attribute,group=group,N=N,K=K,reported=True,reason='N >= 20'))
            selected=int(sub.selected_by_Disagreement.sum()); caught=int((sub.selected_by_Disagreement & sub.large_error).sum())
            random_selected=selections[:,ids].sum(axis=1)
            random_caught=selections[:,ids[y[ids]]].sum(axis=1)
            total_caught=int(random_caught.sum()); total_selected=int(random_selected.sum())
            mean_caught=float(random_caught.mean()); mean_selected=float(random_selected.mean())
            capture_value=caught/K if K else np.nan
            random_capture=mean_caught/K if K else np.nan
            selection_rate=selected/N
            random_rate=mean_selected/N
            note='too few large-error cases — do not interpret' if K<10 else 'descriptive only; no fairness claim'
            rows.append(dict(attribute=attribute,group=group,N=N,K=K,disagreement_selected=selected,disagreement_caught=caught,capture=capture_value,selection_rate=selection_rate,random_mean_caught=mean_caught,random_mean_capture=random_capture,random_mean_selected=mean_selected,random_mean_selection_rate=random_rate,interpretation_note=note,
                capture_arithmetic=f'{caught}/{K}={capture_value:.17g}' if K else 'NA K=0',selection_rate_arithmetic=f'{selected}/{N}={selection_rate:.17g}',random_mean_caught_arithmetic=f'{total_caught}/1000={mean_caught:.17g}',random_mean_capture_arithmetic=f'{total_caught}/(1000*{K})={random_capture:.17g}' if K else 'NA K=0',random_mean_selected_arithmetic=f'{total_selected}/1000={mean_selected:.17g}',random_mean_selection_rate_arithmetic=f'{total_selected}/(1000*{N})={random_rate:.17g}',random_draws=1000,seed=42))
            drawrows.extend(dict(attribute=attribute,group=group,draw=i+1,caught=int(random_caught[i]),selected=int(random_selected[i])) for i in range(1000))
            assert np.isclose(random_capture,np.mean(random_caught/K)) if K else np.isnan(random_capture)
            assert np.isclose(random_rate,np.mean(random_selected/N))
    save('t5_fairness.csv',rows)
    save('t5_group_coverage.csv',coverage)
    save('t5_random_draws.csv',drawrows,False)
    assert before=={p:sha((ROOT/p).read_bytes()) for p in paths}
    save('t5_sources.csv',[dict(path=p,sha256=h) for p,h in before.items()],False)
    save('t5_output_hashes.csv',[dict(path='reports/week9/'+p,sha256=sha((OUT/p).read_bytes())) for p in ['t5_fairness.csv','t5_group_coverage.csv','t5_random_draws.csv','t5_sources.csv']])
    print('STATUS: COMPLETE descriptive Validation A1 group captures. No significance tests, subgroup retuning or fairness claims. No Official Test file opened. All source hashes unchanged.')

if __name__=='__main__':
    if '--capture' in sys.argv:
        capture('t5','t5_fairness.py','Descriptive Validation A1 capture within the requested demographic groups. Only groups meeting the requested population-size floor are reported in t5_fairness.csv; t5_group_coverage.csv lists included and omitted group counts. Random means use the same fixed global draws as the frozen Validation random reference. Group budgets are not independently assigned. Rows below the requested large-error-case floor carry the exact do-not-interpret label. Every reported ratio includes explicit arithmetic; no significance tests or fairness claims are made.')
    else: main()
