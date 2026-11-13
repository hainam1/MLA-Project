"""Calculate MiniLM L6 v2 truncation statistics on development essays (3,812 essays).
Execution environment: .venv_gec
Deterministic, offline, text-free artifact output.
"""
from pathlib import Path
import csv
import json
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
INPUT_ELIGIBLE = ROOT / 'reports/week9/t3_eligible_development.csv'
INPUT_TRAIN = ROOT / 'data/03_clean_ready_to_use/model_train_3128.csv'
INPUT_VAL = ROOT / 'data/03_clean_ready_to_use/validation_783.csv'
INPUT_B2_OOF = ROOT / 'reports/week10/b2_oof.csv'
MODEL_PATH = ROOT / 'reports/week10/b2_assets/model'
OUT_CSV = ROOT / 'docs/final_evidence/b_minilm_truncation.csv'

def main():
    # 1. Load eligible IDs
    with open(INPUT_ELIGIBLE, encoding='utf-8-sig') as f:
        ids = sorted(r['essay_id'] for r in csv.DictReader(f))
    assert len(ids) == len(set(ids)) == 3812
    selected = set(ids)

    # 2. Load texts
    texts = {}
    for p in [INPUT_TRAIN, INPUT_VAL]:
        with open(p, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                eid = r['essay_id']
                if eid in selected:
                    assert eid not in texts
                    texts[eid] = r['essay_text']
    assert set(texts) == selected

    # 3. Load error groups from b2_oof.csv
    a1_rf = set()
    a3_rf_b2 = set()
    with open(INPUT_B2_OOF, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            eid = r['essay_id']
            y_v = float(r['Vocabulary'])
            y_g = float(r['Grammar'])
            rf_v = float(r['RF_V'])
            rf_g = float(r['RF_G'])
            b2_v = float(r['B2_V'])
            b2_g = float(r['B2_G'])
            rf_large = max(abs(rf_v - y_v), abs(rf_g - y_g)) >= 1.0
            b2_large = max(abs(b2_v - y_v), abs(b2_g - y_g)) >= 1.0
            if rf_large:
                a1_rf.add(eid)
                if b2_large:
                    a3_rf_b2.add(eid)

    assert len(a1_rf) == 386
    assert len(a3_rf_b2) == 217

    # 4. Tokenize with SentenceTransformer tokenizer
    print(f"Loading SentenceTransformer tokenizer from {MODEL_PATH}...", flush=True)
    model = SentenceTransformer(str(MODEL_PATH), local_files_only=True)
    tokenizer = model.tokenizer

    token_counts = {}
    for i, eid in enumerate(ids):
        tokens = tokenizer(texts[eid], truncation=False, add_special_tokens=True)['input_ids']
        token_counts[eid] = len(tokens)
        if (i + 1) % 1000 == 0:
            print(f"Tokenized {i+1}/3812 essays...", flush=True)

    # Convert to arrays
    all_lens = np.array([token_counts[eid] for eid in ids], dtype=np.int32)
    truncated_mask = all_lens > 256
    n_truncated = int(truncated_mask.sum())
    trunc_rate = n_truncated / len(all_lens)

    # Percentiles
    # method='linear' is default in numpy
    median_tokens = float(np.median(all_lens))
    p90_tokens = float(np.percentile(all_lens, 90))
    p90_nearest = float(np.percentile(all_lens, 90, method='nearest'))
    max_tokens = int(np.max(all_lens))
    min_tokens = int(np.min(all_lens))

    # A1_RF truncation
    a1_lens = np.array([token_counts[eid] for eid in ids if eid in a1_rf], dtype=np.int32)
    a1_truncated = int((a1_lens > 256).sum())
    a1_trunc_rate = a1_truncated / len(a1_lens)

    # A3_RF_B2 truncation
    a3_lens = np.array([token_counts[eid] for eid in ids if eid in a3_rf_b2], dtype=np.int32)
    a3_truncated = int((a3_lens > 256).sum())
    a3_trunc_rate = a3_truncated / len(a3_lens)

    # Mean truncation fraction among truncated essays
    trunc_lens = all_lens[truncated_mask]
    trunc_fractions = (trunc_lens - 256) / trunc_lens
    mean_trunc_fraction = float(np.mean(trunc_fractions))
    median_trunc_fraction = float(np.median(trunc_fractions))
    max_trunc_fraction = float(np.max(trunc_fractions))

    print("\n--- RESULTS FOR B ---")
    print(f"Total essays: {len(all_lens)}")
    print(f"Truncated essays (>256 tokens): {n_truncated} / {len(all_lens)} = {trunc_rate*100:.4f}% ({trunc_rate:.6f})")
    print(f"Token count stats: Min = {min_tokens}, Median = {median_tokens}, P90 = {p90_tokens} (nearest={p90_nearest}), Max = {max_tokens}")
    print(f"A1_RF (386 essays) truncated: {a1_truncated} / {len(a1_lens)} = {a1_trunc_rate*100:.4f}% ({a1_trunc_rate:.6f})")
    print(f"A3_RF_B2 (217 essays) truncated: {a3_truncated} / {len(a3_lens)} = {a3_trunc_rate*100:.4f}% ({a3_trunc_rate:.6f})")
    print(f"Truncated fraction among truncated essays: Mean = {mean_trunc_fraction*100:.4f}% ({mean_trunc_fraction:.6f}), Median = {median_trunc_fraction*100:.4f}%, Max = {max_trunc_fraction*100:.4f}%")

    # Write output CSV
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            'metric': 'truncated_count_all_dev',
            'subset': 'all_dev_3812',
            'n_subset': len(all_lens),
            'count': n_truncated,
            'rate': trunc_rate,
            'percent_str': f"{trunc_rate*100:.4f}%",
            'details': f"{n_truncated}/{len(all_lens)} essays exceed 256 tokens",
            'arithmetic': f"{n_truncated}/{len(all_lens)}={trunc_rate:.10f}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'SentenceTransformer tokenizer (reports/week10/b2_assets/model)'
        },
        {
            'metric': 'median_token_count',
            'subset': 'all_dev_3812',
            'n_subset': len(all_lens),
            'count': '',
            'rate': median_tokens,
            'percent_str': '',
            'details': f"median={median_tokens}",
            'arithmetic': f"np.median(all_lens)={median_tokens}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'SentenceTransformer tokenizer (reports/week10/b2_assets/model)'
        },
        {
            'metric': 'p90_token_count',
            'subset': 'all_dev_3812',
            'n_subset': len(all_lens),
            'count': '',
            'rate': p90_tokens,
            'percent_str': '',
            'details': f"p90={p90_tokens}",
            'arithmetic': f"np.percentile(all_lens, 90)={p90_tokens}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'SentenceTransformer tokenizer (reports/week10/b2_assets/model)'
        },
        {
            'metric': 'max_token_count',
            'subset': 'all_dev_3812',
            'n_subset': len(all_lens),
            'count': '',
            'rate': max_tokens,
            'percent_str': '',
            'details': f"max={max_tokens}, min={min_tokens}",
            'arithmetic': f"np.max(all_lens)={max_tokens}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'SentenceTransformer tokenizer (reports/week10/b2_assets/model)'
        },
        {
            'metric': 'truncated_count_a1_rf',
            'subset': 'A1_RF_large_errors',
            'n_subset': len(a1_lens),
            'count': a1_truncated,
            'rate': a1_trunc_rate,
            'percent_str': f"{a1_trunc_rate*100:.4f}%",
            'details': f"{a1_truncated}/{len(a1_lens)} essays exceed 256 tokens",
            'arithmetic': f"{a1_truncated}/{len(a1_lens)}={a1_trunc_rate:.10f}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'SentenceTransformer tokenizer (reports/week10/b2_assets/model)'
        },
        {
            'metric': 'truncated_count_a3_rf_b2',
            'subset': 'A3_RF_B2_joint_large_errors',
            'n_subset': len(a3_lens),
            'count': a3_truncated,
            'rate': a3_trunc_rate,
            'percent_str': f"{a3_trunc_rate*100:.4f}%",
            'details': f"{a3_truncated}/{len(a3_lens)} essays exceed 256 tokens",
            'arithmetic': f"{a3_truncated}/{len(a3_lens)}={a3_trunc_rate:.10f}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'SentenceTransformer tokenizer (reports/week10/b2_assets/model)'
        },
        {
            'metric': 'mean_truncated_fraction_in_truncated',
            'subset': 'truncated_essays_only',
            'n_subset': n_truncated,
            'count': '',
            'rate': mean_trunc_fraction,
            'percent_str': f"{mean_trunc_fraction*100:.4f}%",
            'details': f"mean fraction of text cut = {mean_trunc_fraction*100:.4f}%",
            'arithmetic': f"sum((L-256)/L)/{n_truncated}={mean_trunc_fraction:.10f}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'SentenceTransformer tokenizer (reports/week10/b2_assets/model)'
        }
    ]

    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote results to {OUT_CSV}")

if __name__ == '__main__':
    main()
