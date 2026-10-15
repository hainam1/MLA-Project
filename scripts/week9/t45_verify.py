"""Independent checks for the fixed reading workbook and descriptive group table."""
import sys
import subprocess
import numpy as np
import pandas as pd
from t456_evidence import *

def main():
    print('COMMAND: .venv/Scripts/python.exe -u scripts/week9/t45_verify.py')
    print('SEED=42; verification only; no fitting or human coding')
    for task in ['t4','t5']:
        for row in pd.read_csv(OUT/(task+'_sources.csv')).itertuples():
            assert sha((ROOT/row.path).read_bytes())==row.sha256
        hashes=pd.read_csv(OUT/(task+'_output_hashes.csv'))
        for row in hashes.itertuples():
            if row.path.startswith('reports/'):
                assert sha((ROOT/row.path).read_bytes())==row.sha256
        assert (OUT/f'logs/{task}_run1.log').read_bytes()==(OUT/f'logs/{task}_run2.log').read_bytes()
    f=pd.read_csv(OUT/'t1_essay_level.csv',dtype={'essay_id':str})
    demographics=pd.read_csv(ROOT/'data/03_clean_ready_to_use/validation_783.csv',usecols=['essay_id','gender','grade','race_ethnicity','ses'],dtype={'essay_id':str,'grade':str},keep_default_na=False)
    f=f.merge(demographics,on='essay_id',validate='one_to_one',how='left',sort=False)
    rng=np.random.default_rng(42); selections=np.zeros((1000,len(f)),dtype=bool)
    for i in range(1000): selections[i,rng.choice(len(f),153,replace=False)]=True
    table=pd.read_csv(OUT/'t5_fairness.csv',dtype={'group':str},float_precision='round_trip')
    saved_draws=pd.read_csv(OUT/'t5_random_draws.csv',dtype={'group':str})
    columns={'Gender':'gender','Grade':'grade','Race/Ethnicity':'race_ethnicity','SES':'ses'}
    expected_groups=set()
    for attribute,column in columns.items():
        for group,sub in f.groupby(column):
            if len(sub)>=20: expected_groups.add((attribute,str(group)))
    assert set(zip(table.attribute,table.group))==expected_groups
    for r in table.itertuples():
        sub=f.loc[f[columns[r.attribute]].astype(str).eq(r.group)]
        ids=sub.index.to_numpy(); positives=sub.loc[sub.large_error].index.to_numpy()
        assert r.N==len(sub) and r.K==int(sub.large_error.sum())
        assert r.disagreement_selected==int(sub.selected_by_Disagreement.sum())
        assert r.disagreement_caught==int((sub.selected_by_Disagreement&sub.large_error).sum())
        d=saved_draws.loc[saved_draws.attribute.eq(r.attribute)&saved_draws.group.eq(r.group)]
        assert len(d)==1000
        assert np.array_equal(d.caught,selections[:,positives].sum(axis=1))
        assert np.array_equal(d.selected,selections[:,ids].sum(axis=1))
        assert np.isclose(r.random_mean_caught,d.caught.mean())
        assert np.isclose(r.selection_rate,r.disagreement_selected/r.N)
        assert np.isclose(r.random_mean_selection_rate,d.selected.mean()/r.N)
        if r.K:
            assert np.isclose(r.capture,r.disagreement_caught/r.K)
            assert np.isclose(r.random_mean_capture,d.caught.mean()/r.K)
        else: assert np.isnan(r.capture) and np.isnan(r.random_mean_capture)
        if r.K<10: assert r.interpretation_note=='too few large-error cases — do not interpret'
    print('PASS all included/omitted group memberships, deterministic numerator/denominator counts, every global-random group draw and every reported group ratio independently checked.')
    for target in ['reports/week9/t4_reading_sheet.xlsx','reports/week9/t4_private/payload.json','scripts/week9/node_modules/']:
        p=subprocess.run(['git','check-ignore','--',target],cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0,target
        print('GIT_IGNORE_PASS '+target)
    result=subprocess.run(['node',str(ROOT/'scripts/week9/t4_visual_check.mjs')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    sys.stdout.buffer.write(result.stdout); sys.stdout.buffer.flush()
    assert result.returncode==0
    print('PASS fixed reading workbook/source hashes and Task 4/5 repeat-output hashes; no source sample or human entries modified.')

if __name__=='__main__':
    if '--capture' in sys.argv:
        capture('t45_verification','t45_verify.py','The group table is independently checked against saved Task 1 essays, Validation demographics and recreated global random selections. Workbook/source hashes, Git ignore coverage and both task repeat logs are checked. The exported workbook is imported with artifact-tool to render the wrapped full-essay column privately; text is not printed to logs.',section_heading='### Reading workbook and group-table verification')
    else: main()
