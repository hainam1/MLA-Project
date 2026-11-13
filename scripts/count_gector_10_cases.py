"""Run GECToR + ERRANT on first 150 whitespace words for the 10 error cases.
Environment: .venv_gec
Deterministic, text-free output manifest.
"""
from pathlib import Path
import csv
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'scripts/week10'))
import gec_compare as g

CASES = [
    '0514D25768A0', '684166ED2438', '2716F5E20A4F', '48EA282A4EAF', '31D67F9A82BA',
    'E70DD00622DB', '2C38B62420C3', '7CAFF57E1775', '9A36D8AB4818', 'D2EBEB5FDA90'
]

def main():
    # Load texts
    selected = set(CASES)
    texts = {}
    for p in ['data/03_clean_ready_to_use/model_train_3128.csv', 'data/03_clean_ready_to_use/validation_783.csv']:
        with open(ROOT / p, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                eid = r['essay_id']
                if eid in selected:
                    texts[eid] = r['essay_text']
    assert set(texts) == selected

    print(f"Loaded texts for {len(texts)} cases. Initializing GECToR counter...", flush=True)
    counter = g.Counter(ROOT / 'reports/week10/gec_assets/model', ROOT / 'reports/week10/gec_assets/verb-form-vocab.txt')

    results = {}
    for i, eid in enumerate(CASES, 1):
        full_text = texts[eid]
        # First 150 whitespace words
        words150 = full_text.split()[:150]
        text150 = ' '.join(words150)
        t0 = time.time()
        counts = counter.count(text150)
        elapsed = time.time() - t0
        results[eid] = {
            'essay_id': eid,
            'words_150': len(words150),
            'edits_grammar': counts['edits_grammar'],
            'edits_all': counts['edits_all'],
            'per_type': counts['per_type'],
            'elapsed_seconds': elapsed
        }
        print(f"[{i}/10] {eid}: edits_grammar={counts['edits_grammar']}, edits_all={counts['edits_all']} ({elapsed:.2f}s)", flush=True)

    out_file = ROOT / 'scripts/gector_10_cases_output.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved GECToR counts to {out_file}")

if __name__ == '__main__':
    main()
