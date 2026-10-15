"""Exploratory extension designed after Official Test was used.

Task 3 population gate only. No training or population correction on a mismatch.
No Official Test or mixed-corpus/manifest file is read.
"""
from pathlib import Path
import hashlib
import subprocess
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/week9'
LABEL = 'Exploratory extension designed after Official Test was used.'
PATHS = [
    'data/05_model_features/development_features_with_targets.csv',
    'data/03_clean_ready_to_use/model_train_3128.csv',
    'data/03_clean_ready_to_use/validation_783.csv',
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(LABEL)
    print('COMMAND: .venv/Scripts/python.exe scripts/week9/t3_preflight.py')
    print('SEED=42; population preflight only; no random sampling or training executed')
    snapshots={p:sha((ROOT/p).read_bytes()) for p in PATHS}
    development=pd.read_csv(ROOT/PATHS[0],usecols=['essay_id','split','source_partition'],dtype={'essay_id':str})
    assert development.essay_id.is_unique and development.essay_id.notna().all()
    assert set(development.split)=={'model_train','validation'}
    assert development.source_partition.eq('official_train').all()
    # Development feature table has no prompt field. Join prompt names from the
    # two development-only clean tables, never a mixed corpus or split manifest.
    prompts=pd.concat([pd.read_csv(ROOT/p,usecols=['essay_id','prompt'],dtype={'essay_id':str}) for p in PATHS[1:]],ignore_index=True)
    assert prompts.essay_id.is_unique
    frame=development.merge(prompts,on='essay_id',how='left',validate='one_to_one',sort=False)
    assert frame.prompt.notna().all()
    frame['normalised_prompt']=frame.prompt.str.lower().str.split().str.join(' ')
    observed_n=len(frame); observed_prompts=frame.normalised_prompt.nunique()
    status='PASS' if (observed_n,observed_prompts)==(3812,44) else 'PARTIAL_STOP_POPULATION_MISMATCH'
    rows=[dict(task_label=LABEL,status=status,source=PATHS[0],observed_essays=observed_n,expected_essays=3812,observed_prompt_groups=observed_prompts,expected_prompt_groups=44,model_train_essays=int(frame.split.eq('model_train').sum()),validation_essays=int(frame.split.eq('validation').sum()),normalisation='lowercase + whitespace collapse; no merging',population_filter='none; source table as supplied')]
    table=pd.DataFrame(rows)
    table.to_csv(OUT/'t3_preflight.csv',index=False,lineterminator='\n')
    print('CSV t3_preflight.csv')
    print((OUT/'t3_preflight.csv').read_text(),end='')
    print(f'POPULATION observed_essays={observed_n}; expected_essays=3812; observed_normalised_prompt_groups={observed_prompts}; expected_prompt_groups=44')
    print('METHOD prompts sourced from development-only clean train/Validation tables; normalisation=str.lower then whitespace split/join; no prompt merging or population filtering')
    assert snapshots=={p:sha((ROOT/p).read_bytes()) for p in PATHS}
    sources=pd.DataFrame([dict(task_label=LABEL,path=p,sha256=h) for p,h in snapshots.items()])
    sources.to_csv(OUT/'t3_sources.csv',index=False,lineterminator='\n')
    print('CSV t3_sources.csv')
    print((OUT/'t3_sources.csv').read_text(),end='')
    print('INTEGRITY: all read source files unchanged; no Official Test or mixed-corpus/manifest file opened')
    if status!='PASS':
        print('STATUS: PARTIAL. STOP: supplied development essay count or prompt count differs from the requested population. No filtering, retraining, splits, held-out predictions, evaluation or bootstrap performed.')
        print('MISSING: Task 3 steps 2-7 and their requested fold, regression, ranking, AUROC, pooled and held-out prediction outputs. Population discrepancy requires clarification before proceeding.')
    else:
        print('STATUS: population gate PASS; training not part of this preflight script.')

def capture():
    (OUT/'logs').mkdir(parents=True,exist_ok=True)
    outputs=[]
    for i in (1,2):
        p=subprocess.run([sys.executable,str(Path(__file__).resolve())],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        outputs.append(p.stdout)
        (OUT/f'logs/t3_run{i}.log').write_bytes(p.stdout)
        sys.stdout.buffer.write(p.stdout); sys.stdout.buffer.flush()
        if p.returncode:
            (OUT/'logs/t3.log').write_bytes((LABEL+'\n').encode()+b'\n'.join(outputs))
            raise SystemExit(p.returncode)
    proof=f'RUN1_SHA256={sha(outputs[0])}\nRUN2_SHA256={sha(outputs[1])}\nIDENTICAL_RAW_OUTPUT={outputs[0]==outputs[1]}\n'
    (OUT/'logs/t3.log').write_bytes((LABEL+'\nRUN 1\n').encode()+outputs[0]+b'RUN 2\n'+outputs[1]+proof.encode())
    print(proof,end='')
    assert outputs[0]==outputs[1], 'STOP: fresh-process preflight outputs differ'
    result=OUT/'RESULTS_week9.md'; previous=result.read_bytes()
    assert b'## Task 3' not in previous, 'Refusing to overwrite an existing Task 3 section'
    row=pd.read_csv(OUT/'t3_preflight.csv').iloc[0]
    if row.status=='PASS':
        return
    text=f'\n## Task 3\n\n**{LABEL}**\n\n**PARTIAL — stopped at the population gate, as instructed.** The supplied development feature table contains `{row.observed_essays}` essays rather than the expected `{row.expected_essays}`. Normalised prompt groups are `{row.observed_prompt_groups}`, matching the expected `{row.expected_prompt_groups}`. The split counts are `{row.model_train_essays}` model-train and `{row.validation_essays}` Validation; `{row.model_train_essays}+{row.validation_essays} = {row.observed_essays}`. No population filtering or prompt merging was applied. [src: reports/week9/t3_preflight.csv row 1]\n\nProducer: `scripts/week9/t3_preflight.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t3_preflight.py --capture`; each child command: `.venv/Scripts/python.exe scripts/week9/t3_preflight.py`. The preflight was repeated in a fresh process.\n\nRaw terminal output:\n\n```text\n{outputs[0].decode()}```\n\n[src: reports/week9/logs/t3_run1.log POPULATION, CSV, STATUS and MISSING lines; reports/week9/t3_preflight.csv row 1; reports/week9/t3_sources.csv rows 1–3]\n\nRepeat proof:\n\n```text\n{proof}```\n\n[src: reports/week9/logs/t3.log final hash lines]\n\nMissing: steps 2–7, including both split designs, model retraining, fold composition, regression metrics, anchor/ranking metrics, AUROC intervals, pooled comparison and held-out predictions. Training determinism was not assessed because training was not run; only the preflight outputs are confirmed identical. The requested downstream CSVs were not created with empty or invented results. The earlier Task sections were preserved byte-for-byte by appending this section. No Official Test file was opened.\n'
    result.write_bytes(previous+text.encode('utf-8'))
    assert result.read_bytes()[:len(previous)]==previous

if __name__=='__main__':
    capture() if '--capture' in sys.argv else main()
