"""Append-only evidence capture for Tasks 4-6. No protected task edits."""
import os
import subprocess
import sys
from pathlib import Path
import hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/week9'
LABEL='Exploratory extension designed after Official Test was used.'

def sha(data): return hashlib.sha256(data).hexdigest()

def save(name,rows,echo=True):
    df=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    df.to_csv(OUT/name,index=False,lineterminator='\n',float_format='%.17g')
    if echo:
        print('CSV '+name,flush=True); print((OUT/name).read_text(),end='',flush=True)
    return df

def capture(task,script,narrative,twice=True,section_heading=None):
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'logs').mkdir(exist_ok=True)
    result=OUT/'RESULTS_week9.md'; before=result.read_bytes()
    heading=section_heading or f'## Task {task[1:]}'
    assert heading.encode() not in before, 'Refusing to overwrite accepted results'
    outputs=[]
    env=os.environ.copy(); env.update(PYTHONHASHSEED='42',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    for i in range(1,3 if twice else 2):
        run_env=env.copy(); run_env['T4_FIRST_EXPORT']='1' if i==1 else '0'
        path=OUT/f'logs/{task}_run{i}.log'
        with path.open('wb') as log:
            process=subprocess.Popen([sys.executable,'-u',str(ROOT/'scripts/week9'/script)],cwd=ROOT,env=run_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            for line in iter(process.stdout.readline,b''):
                log.write(line); log.flush(); sys.stdout.buffer.write(line); sys.stdout.buffer.flush()
            code=process.wait()
        outputs.append(path.read_bytes())
        if code:
            (OUT/f'logs/{task}.log').write_bytes(b'\n'.join(outputs))
            raise SystemExit(f'STOP {task}: see raw logs; no successful section appended')
    proof=''.join(f'RUN{i+1}_SHA256={sha(x)}\n' for i,x in enumerate(outputs))
    if twice: proof+=f'IDENTICAL_RAW_OUTPUT={outputs[0]==outputs[1]}\n'
    (OUT/f'logs/{task}.log').write_bytes(b'\n'.join([f'RUN {i+1}\n'.encode()+x for i,x in enumerate(outputs)])+proof.encode())
    print(proof,end='',flush=True)
    if twice: assert outputs[0]==outputs[1], 'STOP: fresh-process outputs differ'
    section=f'\n{heading}\n\n{LABEL}\n\n{narrative}\n\nProducer: `scripts/week9/{script}`. Exact command: `.venv/Scripts/python.exe scripts/week9/{script} --capture`. Child command: `.venv/Scripts/python.exe -u scripts/week9/{script}`.\n\nRaw terminal output:\n\n```text\n{outputs[0].decode("utf-8")}```\n\n[src: reports/week9/logs/{task}_run1.log exact lines; each CSV block names its source file and data rows exclude headers]\n\nFresh-process output hashes:\n\n```text\n{proof}```\n\n[src: reports/week9/logs/{task}.log hash lines]\n'
    assert result.read_bytes()==before
    result.write_bytes(before+section.encode('utf-8'))
    assert result.read_bytes()[:len(before)]==before
