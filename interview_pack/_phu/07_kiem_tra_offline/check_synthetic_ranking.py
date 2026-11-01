"""Ten explicitly synthetic records; independent arithmetic example."""
import math
rows=[('S01',.9,True),('S02',.9,False),('S03',.7,True),('S04',.6,False),('S05',.5,False),('S06',.4,False),('S07',.3,False),('S08',.2,False),('S09',.1,False),('S10',.0,True)]
ranked=sorted(reversed(rows),key=lambda r:(-r[1],r[0]))
N=len(rows); K=sum(r[2] for r in rows); k=math.ceil(.2*N)
C=sum(r[2] for r in ranked[:k]); E=k*K/N
assert (N,K,k,C,E)==(10,3,2,1,.6)
assert [r[0] for r in ranked[:2]]==['S01','S02']
print('SYNTHETIC EXAMPLE ONLY - not ELLIPSE measurements')
print('id score large_error selected')
for j,r in enumerate(ranked): print(r[0],f'{r[1]:.1f}',int(r[2]),int(j<k))
print(f'PASS: N={N}; K_large={K}; budget=ceil(0.20*{N})={k}')
print(f'caught={C}/{K}; expected_random=k*K/N={k}*{K}/{N}={E}')
print('Tie at 0.9: S01 then S02, by ascending string ID.')
print('Source: synthetic rows declared in this script.')
