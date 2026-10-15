"""Task 1: Validation-only disagreement diagnostics."""
import sys
import numpy as np
from scipy.stats import spearmanr
from validation_common import *

def main():
    snapshot=integrity_start('t1')
    f=load()
    median=float(f.D.median())
    f['D_median_group']=np.where(f.D<median,'below','at_or_above')
    print(f'MEDIAN D={median:.17g}; below means D < median; complement means D >= median; exact ties={int(f.D.eq(median).sum())}')
    quadrants=[]
    for large in (True,False):
        for group in ('below','at_or_above'):
            count=int((f.large_error.eq(large)&f.D_median_group.eq(group)).sum())
            denom=int(f.large_error.eq(large).sum())
            quadrants.append(dict(large_error=large,D_group=group,D_median=median,count=count,row_total=denom,fraction=count/denom,arithmetic=f'{count}/{denom}={count/denom:.17g}'))
    save('t1_quadrants.csv',quadrants)
    print(f'WEEK8_CHECK below_median_large_errors={int((f.large_error & f.D.lt(median)).sum())}/69; median rounded to 3 decimals={median:.3f}')
    f['error_category']='not_large_error'
    for i,r in f.loc[f.large_error].iterrows():
        t=r.analysis_target; a,b=r['e_RF_'+t],r['e_Ridge_'+t]
        if a*b>0:
            category='a_both_wrong_same_direction' if abs(b)>=1 else 'b_same_direction_Ridge_below_threshold'
        elif a*b<0:
            category='c_opposite_sign'
        else:
            category='zero_Ridge_error'
        f.loc[i,'error_category']=category
    categories=[]
    for c in ('a_both_wrong_same_direction','b_same_direction_Ridge_below_threshold','c_opposite_sign','zero_Ridge_error'):
        sub=f.loc[f.error_category.eq(c)]
        categories.append(dict(category=c,n=len(sub),D_min=sub.D.min(),D_median=sub.D.median(),D_max=sub.D.max(),fraction=len(sub)/69,arithmetic=f'{len(sub)}/69={len(sub)/69:.17g}'))
    assert sum(r['n'] for r in categories)==69
    save('t1_categories.csv',categories)
    corr=[]
    pairs=[('D','RF_magnitude'),('D','Ridge_magnitude'),('e_RF_V','e_Ridge_V'),('e_RF_G','e_Ridge_G')]
    for t in ('V','G'):
        f['distance_y_'+t]=abs(f['y_'+t]-3)
        pairs.append(('D','distance_y_'+t))
    for a,b in pairs:
        rho=spearmanr(f[a],f[b]).statistic
        corr.append(dict(x=a,y=b,n=len(f),spearman_rho=rho))
    save('t1_correlations.csv',corr)
    print('METHOD Spearman rho = Pearson correlation of average ranks, all Validation essays; no thresholding or subgroup selection.')
    save('t1_auroc.csv',boot_aucs(f,f.large_error,'A1','t1'))
    print('METHOD AUROC=U/(n_positive*n_negative), ties receive half credit; paired ordinary essay bootstrap with replacement, 2000 draws from default_rng(42), percentile CI [2.5,97.5], NumPy linear interpolation; single-class replicates skipped and counted. Ranking scores unchanged.')
    bands=[]
    for t in ('V','G'):
        y=f['y_'+t]
        for band,mask in [('y<2.5',y<2.5),('2.5<=y<=4.0',y.between(2.5,4)),('y>4.0',y>4)]:
            sub=f.loc[mask]; n=len(sub); count=int(abs(sub['e_RF_'+t]).ge(1).sum())
            row=dict(target=t,band=band,n=n,target_large_errors=count,large_error_rate=count/n if n else np.nan,rate_arithmetic=f'{count}/{n}={count/n:.17g}' if n else 'NA empty band')
            for col,name in [('D','mean_D'),('e_RF_'+t,'mean_signed_RF_error'),('e_Ridge_'+t,'mean_signed_Ridge_error')]:
                total=float(sub[col].sum()); value=float(sub[col].mean())
                row[name]=value; row[name+'_sum']=total; row[name+'_arithmetic']=f'{total:.17g}/{n}={value:.17g}' if n else 'NA empty band'
            bands.append(row)
    save('t1_bands.csv',bands)
    columns=['essay_id','prompt','y_V','y_G','RF_V','RF_G','Ridge_V','Ridge_G','e_RF_V','e_RF_G','e_Ridge_V','e_Ridge_G','D','word_count','in_32_sample']
    low=f.loc[f.large_error].sort_values(['D','essay_id'],ascending=[True,True],kind='stable').head(10)[columns].copy()
    high=f.loc[~f.large_error].sort_values(['D','essay_id'],ascending=[False,True],kind='stable').head(10)[columns].copy()
    low.insert(0,'shortlist','large_error_lowest_D'); high.insert(0,'shortlist','non_large_error_highest_D')
    save('t1_shortlists.csv',pd.concat([low,high],ignore_index=True),echo=False)
    save('t1_essay_level.csv',f,echo=False)
    print('SHORTLISTS: t1_shortlists.csv data rows 1-10 large_error_lowest_D; 11-20 non_large_error_highest_D; no interpretation or human judgement added.')
    print('ESSAYS: t1_essay_level.csv contains every eligible Validation essay and computed target, signed-error, disagreement, trigger and selection fields.')
    integrity_end('t1',snapshot)

if __name__=='__main__':
    if '--capture' in sys.argv:
        run_capture('t1','t1_analysis.py','Validation-only diagnostics under the frozen RF anchor. Disagreement remains not demonstrated better than random. The median split uses strictly below versus at-or-above; any exact median ties are printed. The triggering target with larger RF absolute error is used for categories; ties use Vocabulary. A zero Ridge error has its own explicit category rather than being assigned an invented sign. Shortlists contain no interpretation. Human reference values are the saved two-rater means, checked against the Validation clean table. The complete numeric summaries and their arithmetic follow as raw output; bootstrap replicates and essay-level records are preserved in CSV files. Source tags identify CSV data rows excluding headers.')
    else:
        main()
