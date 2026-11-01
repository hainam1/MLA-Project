"""Offline, standard library only. Recompute from saved DEVELOPMENT predictions."""
import csv, math, pathlib, sys, time, hashlib

def main():
    start=time.perf_counter()
    path=pathlib.Path(__file__).with_name('development_predictions.csv')
    if len(sys.argv)>1:
        path=pathlib.Path(sys.argv[1])
        if path.name!='t3_heldout_predictions.csv':
            raise SystemExit('Only the named saved development source is accepted.')
    with path.open(encoding='utf-8-sig',newline='') as f:
        rows=[r for r in csv.DictReader(f) if r['split_type']=='prompt_disjoint']
    assert len({r['essay_id'] for r in rows})==len(rows)==3812
    total_K=total_k=total_C=0; expected=0.
    print('DEVELOPMENT ONLY | saved predictions | no model / no network')
    print('fold N K_large budget caught expected_random')
    for fold in sorted({r['fold'] for r in rows},key=int):
        group=[r for r in rows if r['fold']==fold]
        for r in group:
            r['_D']=max(abs(float(r['RF_V'])-float(r['Ridge_V'])),abs(float(r['RF_G'])-float(r['Ridge_G'])))
            r['_L']=max(abs(float(r['RF_V'])-float(r['y_V'])),abs(float(r['RF_G'])-float(r['y_G'])))>=1.
        ranked=sorted(group,key=lambda r:(-r['_D'],r['essay_id']))
        n=len(group); K=sum(r['_L'] for r in group); k=math.ceil(.2*n)
        C=sum(r['_L'] for r in ranked[:k]); E=k*K/n
        print(f'{fold:>4} {n} {K:>7} {k:>6} {C:>6} {E:.6f}')
        total_K+=K;total_k+=k;total_C+=C;expected+=E
    assert (total_K,total_k,total_C)==(386,764,88)
    assert abs(expected-77.362908429581)<1e-10
    print(f'PASS: D caught={total_C}/{total_K}; budget={total_k}; expected_random={expected:.6f} (77.36)')
    print('Rules: max-target absolute RF error >= 1; D descending; essay_id string ascending.')
    print('Source: reports/week9/t3_heldout_predictions.csv; prompt_disjoint; sanitized numeric copy.')
    print('Input SHA256:',hashlib.sha256(path.read_bytes()).hexdigest())
    elapsed=time.perf_counter()-start
    print(f'Elapsed: {elapsed:.4f} seconds'); assert elapsed<10

if __name__=='__main__': main()
