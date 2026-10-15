"""Exploratory extension designed after Official Test was used."""
from pathlib import Path
import hashlib
import os
import subprocess
import sys

import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/week9'
LABEL='Exploratory extension designed after Official Test was used.'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(name,rows,echo=False):
    df=rows.copy() if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    if 'task_label' not in df:
        df.insert(0,'task_label',LABEL)
    df.to_csv(OUT/name,index=False,float_format='%.17g',lineterminator='\n')
    if echo:
        print('CSV '+name,flush=True)
        print((OUT/name).read_text(),end='',flush=True)
    return df

def repeat(script,tag,title,narrative,summary_files=()):
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'logs').mkdir(exist_ok=True)
    prior=(OUT/'RESULTS_week9.md').read_bytes()
    outputs=[]
    env=os.environ.copy()
    env.update(PYTHONHASHSEED='42',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    for i in (1,2):
        path=OUT/f'logs/{tag}_run{i}.log'
        # Stream raw bytes to file while executing, so progress and failures survive interruption.
        with path.open('wb') as log:
            proc=subprocess.Popen([sys.executable,'-u',str(ROOT/'scripts/week9'/script)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            for line in iter(proc.stdout.readline,b''):
                log.write(line); log.flush()
                sys.stdout.buffer.write(line); sys.stdout.buffer.flush()
            code=proc.wait()
        outputs.append(path.read_bytes())
        if code:
            (OUT/f'logs/{tag}.log').write_bytes((LABEL+'\n').encode()+b'\n'.join(outputs))
            raise SystemExit(f'STOP: {tag} failed. Raw output saved; no successful results appended.')
    proof=f'RUN1_SHA256={sha(outputs[0])}\nRUN2_SHA256={sha(outputs[1])}\nIDENTICAL_RAW_OUTPUT={outputs[0]==outputs[1]}\n'
    combined=(LABEL+'\nRUN 1\n').encode()+outputs[0]+b'RUN 2\n'+outputs[1]+proof.encode()
    (OUT/f'logs/{tag}.log').write_bytes(combined)
    print(proof,end='',flush=True)
    assert outputs[0]==outputs[1], 'STOP: determinism failed'
    sections=[f'\n### {title}\n',f'**{LABEL}**\n',narrative+'\n',f'Producer: `scripts/week9/{script}`. Exact command: `.venv/Scripts/python.exe scripts/week9/{script} --capture`. Each fresh child: `.venv/Scripts/python.exe -u scripts/week9/{script}`. Environment: `PYTHONHASHSEED=42`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`.\n']
    for filename in summary_files:
        table=pd.read_csv(OUT/filename)
        sections += [f'[{filename}]({filename}):\n','```csv\n'+(OUT/filename).read_text()+'```\n',f'[src: reports/week9/{filename} data rows 1–{len(table)}; reports/week9/logs/{tag}_run1.log CSV {filename} block]\n']
    sections += ['Raw terminal output, first fresh process:\n','```text\n'+outputs[0].decode('utf-8')+'```\n',f'[src: reports/week9/logs/{tag}_run1.log exact quoted lines; every CSV block names its source file]\n','Fresh-process repeat proof:\n','```text\n'+proof+'```\n',f'[src: reports/week9/logs/{tag}.log final hash lines]\n']
    result=OUT/'RESULTS_week9.md'
    assert result.read_bytes()==prior, 'STOP: results file changed during execution'
    result.write_bytes(prior+'\n'.join(sections).encode('utf-8'))
    assert result.read_bytes()[:len(prior)]==prior
    # Keep the original preflight transcript in t3.log and append later evidence, without truncation.
    if tag!='t3':
        with (OUT/'logs/t3.log').open('ab') as stream:
            stream.write(('\n'+LABEL+'\n'+title+'\n').encode()+combined)
