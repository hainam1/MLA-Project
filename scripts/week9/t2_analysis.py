"""Task 2: predeclared Validation-only anchor sensitivity; no anchor selection."""
import sys
from scipy.stats import hypergeom
from validation_common import *

def main():
    snapshot=integrity_start('t2')
    f=load()  # Mandatory A1 assertion precedes A2/A3 calculations.
    a1=f.large_error.to_numpy(); a2=f.Ridge_magnitude.ge(1).to_numpy(); a3=a1&a2
    save('t2_overlap.csv',[dict(A1_intersection_A2=int(a3.sum()),A1_only=int((a1&~a2).sum()),A2_only=int((a2&~a1).sum()),A1_total=int(a1.sum()),A2_total=int(a2.sum()))])
    rows=[]; aucrows=[]; all_draws=[]
    for anchor,y in [('A1_RF',a1),('A2_Ridge',a2),('A3_Both_wrong',a3)]:
        K=int(y.sum()); n=len(f); k=153
        rng=np.random.default_rng(42)
        draws=np.array([int(y[rng.choice(n,size=k,replace=False)].sum()) for _ in range(1000)])
        expected=k*K/n
        for ranking,col in [('Random',None),*SIGNALS.items()]:
            caught=float(draws.mean()) if col is None else int(y[top(f,col)].sum())
            capture=caught/K if K else np.nan; precision=caught/k; lift=precision/(K/n) if K else np.nan
            p=float(hypergeom.sf(caught-1,n,K,k)) if col else np.nan
            row=dict(anchor=anchor,ranking=ranking,N=n,K=K,k=k,caught=caught,capture=capture,precision=precision,lift=lift,exact_hypergeom_p=p,expected_random=expected,
                capture_arithmetic=f'{caught}/{K}={capture:.17g}' if K else 'NA K=0',precision_arithmetic=f'{caught}/{k}={precision:.17g}',lift_arithmetic=f'({caught}/{k})/({K}/{n})={lift:.17g}' if K else 'NA K=0',expected_arithmetic=f'{k}*{K}/{n}={expected:.17g}',p_expression=f'hypergeom.sf({caught-1},{n},{K},{k})={p:.17g}' if col else 'NA: Random caught is a noninteger mean; exact p is provided separately for every integer draw in t2_random_draws.csv',
                seed=42,random_draws=1000 if col is None else 0,random_mean=float(draws.mean()) if col is None else np.nan,random_p2_5=float(np.percentile(draws,2.5)) if col is None else np.nan,random_p97_5=float(np.percentile(draws,97.5)) if col is None else np.nan,random_mean_arithmetic=f'{int(draws.sum())}/1000={draws.mean():.17g}' if col is None else '')
            rows.append(row)
        for i,x in enumerate(draws):
            all_draws.append(dict(anchor=anchor,draw=i+1,K=K,caught=int(x),exact_hypergeom_p=float(hypergeom.sf(x-1,n,K,k)),capture=x/K if K else np.nan,precision=x/k,lift=(x/k)/(K/n) if K else np.nan))
        aucrows.extend(boot_aucs(f,y,anchor,'t2_'+anchor))
    save('t2_anchor.csv',rows)
    save('t2_auroc.csv',aucrows)
    save('t2_random_draws.csv',all_draws,echo=False)
    print('METHOD all three anchors reported without choosing among them. A3 is essay-level A1 AND A2; targets may differ. Threshold=1.0; same queues and score order for every anchor.')
    print('METHOD Random has no fixed discriminative ranking score; its theoretical AUROC is 0.5, so no empirical bootstrap AUROC is assigned. AUROC CIs for the three fixed signals use paired ordinary essay bootstrap, 2000 resamples, seed=42, percentile [2.5,97.5] with linear interpolation. Undefined single-class replicates are skipped and counted.')
    print('METHOD Random caught/capture/precision/lift are means over 1000 selections. A noninteger mean is not a hypergeometric observation; no aggregate p is fabricated. Each actual random draw has an exact one-sided hypergeometric p in t2_random_draws.csv. Percentiles describe captured counts, not confidence intervals.')
    print('SELF_REFERENCE: Under A2, Ridge Extremity is scored against labels derived from Ridge itself (self-referential), mirroring the A1/Disagreement issue: RF is both the anchor and part of D. These anchor sensitivities do not select a preferred anchor or establish better-than-random generalisation.')
    integrity_end('t2',snapshot)

if __name__=='__main__':
    if '--capture' in sys.argv:
        run_capture('t2','t2_analysis.py','Validation-only sensitivity to all predeclared anchors; no anchor is chosen. The A1 reproduction assertion runs before A2/A3 are computed. Under A2, Ridge Extremity is scored against labels derived from Ridge itself (self-referential), mirroring the A1/Disagreement issue: RF is both the anchor and part of D. Random results aggregate draws; exact p values are reported for each integer draw, with aggregate p marked NA because a mean caught count is not a hypergeometric observation. Random has no fixed score to bootstrap; the three deterministic ranking signals receive AUROC intervals. Complete raw summaries, explicit metric arithmetic and source CSV filenames follow.')
    else:
        main()
