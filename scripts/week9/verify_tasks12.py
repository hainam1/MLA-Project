"""Independent checks of Task 1/2 artifacts; reads only new reports and Validation sample."""
from pathlib import Path
import hashlib
import subprocess
import sys
import numpy as np
import pandas as pd
from scipy.stats import hypergeom
from sklearn.metrics import roc_auc_score
from validation_common import OUT, ROOT, SIGNALS

def main():
    print('COMMAND: .venv/Scripts/python.exe scripts/week9/verify_tasks12.py')
    f=pd.read_csv(OUT/'t1_essay_level.csv',dtype={'essay_id':str})
    assert len(f)==762 and f.essay_id.is_unique
    assert f.selected_by_Disagreement.sum()==153
    assert (f.selected_by_Disagreement & f.large_error).sum()==15
    assert set(f.split)=={'validation'} and set(f.source_partition)=={'official_train'}
    short=pd.read_csv(OUT/'t1_shortlists.csv',dtype={'essay_id':str})
    assert len(short)==20
    for name,large,asc in [('large_error_lowest_D',True,True),('non_large_error_highest_D',False,False)]:
        expected=f.loc[f.large_error.eq(large)].sort_values(['D','essay_id'],ascending=[asc,True]).head(10).essay_id.tolist()
        assert short.loc[short.shortlist.eq(name),'essay_id'].tolist()==expected
    for task in ('t1','t2'):
        sources=pd.read_csv(OUT/(task+'_sources.csv'))
        for r in sources.itertuples():
            assert hashlib.sha256((ROOT/r.path).read_bytes()).hexdigest()==r.sha256
        for r in pd.read_csv(OUT/(task+'_output_hashes.csv')).itertuples():
            assert hashlib.sha256((ROOT/r.path).read_bytes()).hexdigest()==r.sha256
    sample=pd.read_csv(ROOT/'docs/data/error_analysis/manual_error_review.csv',usecols=['essay_id'],dtype=str)
    assert len(sample)==32 and set(f.loc[f.in_32_sample.eq('yes'),'essay_id'])==set(sample.essay_id)
    labels={'A1_RF':f.RF_magnitude.ge(1).to_numpy(),'A2_Ridge':f.Ridge_magnitude.ge(1).to_numpy()}
    labels['A3_Both_wrong']=labels['A1_RF']&labels['A2_Ridge']
    for task in ('t1','t2'):
        table=pd.read_csv(OUT/(task+'_auroc.csv'))
        for row in table.itertuples():
            y=labels['A1_RF' if task=='t1' else row.anchor]
            independent=roc_auc_score(y,f[row.score])
            assert np.isclose(independent,row.auroc,atol=1e-14,rtol=0)
            boot=pd.read_csv(OUT/('t1_bootstrap.csv' if task=='t1' else 't2_'+row.anchor+'_bootstrap.csv'))
            b=boot.loc[boot.ranking.eq(row.ranking),'auroc']
            assert len(b)==2000
            assert np.allclose(np.percentile(b.dropna(),[2.5,97.5]),[row.ci_low,row.ci_high],atol=1e-14,rtol=0)
    draws=pd.read_csv(OUT/'t2_random_draws.csv')
    for r in pd.read_csv(OUT/'t2_anchor.csv').itertuples():
        y=labels[r.anchor]; K=int(y.sum()); assert K==r.K
        if r.ranking=='Random':
            d=draws.loc[draws.anchor.eq(r.anchor)]
            assert len(d)==1000 and np.isclose(d.caught.mean(),r.caught)
            assert np.allclose(np.percentile(d.caught,[2.5,97.5]),[r.random_p2_5,r.random_p97_5])
            assert np.allclose(hypergeom.sf(d.caught-1,762,K,153),d.exact_hypergeom_p)
        else:
            ids=f.sort_values([SIGNALS[r.ranking],'essay_id'],ascending=[False,True]).head(153).index
            assert int(y[ids].sum())==r.caught
            assert np.isclose(hypergeom.sf(r.caught-1,762,K,153),r.exact_hypergeom_p)
        assert np.isclose(r.capture,r.caught/K)
        assert np.isclose(r.precision,r.caught/153)
        assert np.isclose(r.lift,(r.caught/153)/(K/762))
        assert np.isclose(r.expected_random,153*K/762)
    result=(OUT/'RESULTS_week9.md').read_text(encoding='utf-8')
    assert result.count('## Task 0')==result.count('## Task 1\n')==result.count('## Task 2\n')==1
    for task in ('t1','t2'):
        assert (OUT/f'logs/{task}_run1.log').read_bytes()==(OUT/f'logs/{task}_run2.log').read_bytes()
    print('PASS: Validation population, frozen capture gate, shortlists, existing sample membership and source/output hashes.')
    print('PASS: independent sklearn AUROC matches every Task 1/2 estimate; every bootstrap interval recomputed from saved replicates.')
    print('PASS: deterministic catches, all metric arithmetic, random means/percentiles and each random draw exact hypergeometric p.')
    print('PASS: both task raw outputs repeat identically; exactly one section per task. No Official Test files opened.')

if __name__=='__main__':
    if '--capture' not in sys.argv:
        main()
    else:
        outputs=[]
        for i in (1,2):
            p=subprocess.run([sys.executable,str(Path(__file__).resolve())],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            outputs.append(p.stdout)
            sys.stdout.buffer.write(p.stdout); sys.stdout.buffer.flush()
            (OUT/f'logs/t12_verification_run{i}.log').write_bytes(p.stdout)
            if p.returncode:
                (OUT/'logs/t12_verification.log').write_bytes(b'\n'.join(outputs))
                raise SystemExit(p.returncode)
        proof=''.join(f'RUN{i+1}_SHA256={hashlib.sha256(x).hexdigest()}\n' for i,x in enumerate(outputs))+f'IDENTICAL_RAW_OUTPUT={outputs[0]==outputs[1]}\n'
        (OUT/'logs/t12_verification.log').write_bytes(b'RUN 1\n'+outputs[0]+b'RUN 2\n'+outputs[1]+proof.encode())
        print(proof,end=''); assert outputs[0]==outputs[1]
