"""Cluster bootstrap for TF-IDF (B1) and MiniLM (B2) versus D_old and Random Expectation.
Method: 44 prompt clusters sampled with replacement, 44 draws per resample,
2000 resamples, default_rng(42), exactly as in scripts/week9b/paired_tree_spread.py.
Fixed queues, fixed scores, duplicate all essays of sampled prompt.
"""
from pathlib import Path
import csv
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T3_PATH = ROOT / 'reports/week9/t3_heldout_predictions.csv'
B2_PATH = ROOT / 'reports/week10/b2_oof.csv'
OUT_CSV = ROOT / 'docs/final_evidence/c_cluster_bootstrap.csv'

def main():
    # 1. Load data
    df_t3 = pd.read_csv(T3_PATH)
    df_t3 = df_t3[df_t3['split_type'] == 'prompt_disjoint'].reset_index(drop=True)
    df_b2 = pd.read_csv(B2_PATH)

    m = pd.merge(
        df_t3[['essay_id', 'normalised_prompt', 'fold', 'selected_D', 'A1_RF']],
        df_b2[['essay_id', 'RF_V', 'RF_G', 'Ridge_V', 'Ridge_G', 'B1_V', 'B1_G', 'B2_V', 'B2_G', 'Vocabulary', 'Grammar']],
        on='essay_id'
    )
    assert len(m) == 3812

    # Check A1_RF
    rf_v_err = np.abs(m['RF_V'] - m['Vocabulary'])
    rf_g_err = np.abs(m['RF_G'] - m['Grammar'])
    a1 = (np.maximum(rf_v_err, rf_g_err) >= 1.0).to_numpy()
    assert np.array_equal(a1, m['A1_RF'].to_numpy())
    assert a1.sum() == 386

    ids = m['essay_id'].to_numpy()
    folds = m['fold'].to_numpy()

    # Scores
    d_old_score = np.maximum(np.abs(m['RF_V'] - m['Ridge_V']), np.abs(m['RF_G'] - m['Ridge_G'])).to_numpy()
    d_b1_score = np.maximum(np.abs(m['RF_V'] - m['B1_V']), np.abs(m['RF_G'] - m['B1_G'])).to_numpy()
    d_b2_score = np.maximum(np.abs(m['RF_V'] - m['B2_V']), np.abs(m['RF_G'] - m['B2_G'])).to_numpy()

    # Select queues
    def select_queue(ids, scores, folds):
        selected = np.zeros(len(ids), dtype=bool)
        probabilities = np.zeros(len(ids))
        for fold in range(1, 6):
            index = np.flatnonzero(folds == fold)
            k = math.ceil(0.2 * len(index))
            order = np.lexsort((ids[index], -scores[index]))
            selected[index[order[:k]]] = True
            probabilities[index] = k / len(index)
        return selected, probabilities

    q_old, prob = select_queue(ids, d_old_score, folds)
    q_b1, _ = select_queue(ids, d_b1_score, folds)
    q_b2, _ = select_queue(ids, d_b2_score, folds)

    assert np.array_equal(q_old, m['selected_D'].to_numpy())

    # Observed point estimates
    label = a1
    caught_old = int((q_old & label).sum())
    caught_b1 = int((q_b1 & label).sum())
    caught_b2 = int((q_b2 & label).sum())
    expected = float(np.dot(label, prob))

    obs = {
        'D_MiniLM - D_cũ': caught_b2 - caught_old,
        'D_TF-IDF - D_cũ': caught_b1 - caught_old,
        'D_MiniLM - kỳ vọng ngẫu nhiên': caught_b2 - expected,
        'D_TF-IDF - kỳ vọng ngẫu nhiên': caught_b1 - expected,
    }

    print("=== OBSERVED POINT ESTIMATES (BASELINE CHECK) ===")
    print(f"caught_old (D_old): {caught_old}")
    print(f"caught_b1 (D_TF-IDF): {caught_b1}")
    print(f"caught_b2 (D_MiniLM): {caught_b2}")
    print(f"expected random: {expected:.12f}")
    for k, v in obs.items():
        if isinstance(v, int):
            print(f"{k}: {v:+d}")
        else:
            print(f"{k}: {v:.12f}")

    # Check observed values match required target figures
    assert obs['D_MiniLM - D_cũ'] == 5, f"Expected +5, got {obs['D_MiniLM - D_cũ']}"
    assert obs['D_TF-IDF - D_cũ'] == -7, f"Expected -7, got {obs['D_TF-IDF - D_cũ']}"
    assert abs(obs['D_MiniLM - kỳ vọng ngẫu nhiên'] - 15.637091570419) < 1e-6, f"Expected ~15.637, got {obs['D_MiniLM - kỳ vọng ngẫu nhiên']}"
    assert abs(obs['D_TF-IDF - kỳ vọng ngẫu nhiên'] - 3.637091570419) < 1e-6, f"Expected ~3.637, got {obs['D_TF-IDF - kỳ vọng ngẫu nhiên']}"
    print("ALL OBSERVED TARGETS MATCH EXACTLY. Proceeding with prompt-cluster bootstrap...\n")

    # 44 prompt clusters
    prompt_codes, prompts = pd.factorize(m['normalised_prompt'], sort=True)
    assert len(prompts) == 44

    # Bootstrap sampling
    rng = np.random.default_rng(42)
    samples = {
        'D_MiniLM - D_cũ': [],
        'D_TF-IDF - D_cũ': [],
        'D_MiniLM - kỳ vọng ngẫu nhiên': [],
        'D_TF-IDF - kỳ vọng ngẫu nhiên': [],
    }

    for _ in range(2000):
        counts = np.bincount(rng.integers(0, len(prompts), len(prompts)), minlength=len(prompts))
        weights = counts[prompt_codes]

        ct_b2 = float(np.dot(weights, label & q_b2))
        ct_b1 = float(np.dot(weights, label & q_b1))
        ct_old = float(np.dot(weights, label & q_old))
        exp_val = float(np.dot(weights, label * prob))

        samples['D_MiniLM - D_cũ'].append(ct_b2 - ct_old)
        samples['D_TF-IDF - D_cũ'].append(ct_b1 - ct_old)
        samples['D_MiniLM - kỳ vọng ngẫu nhiên'].append(ct_b2 - exp_val)
        samples['D_TF-IDF - kỳ vọng ngẫu nhiên'].append(ct_b1 - exp_val)

    # Compile results
    rows = []
    print("=== BOOTSTRAP RESULTS (2,000 RESAMPLES, seed=42) ===")
    for metric_name in [
        'D_MiniLM - D_cũ',
        'D_TF-IDF - D_cũ',
        'D_MiniLM - kỳ vọng ngẫu nhiên',
        'D_TF-IDF - kỳ vọng ngẫu nhiên'
    ]:
        vals = np.asarray(samples[metric_name])
        ci_low = float(np.percentile(vals, 2.5))
        ci_high = float(np.percentile(vals, 97.5))
        ci_width = ci_high - ci_low
        pos = int((vals > 0).sum())
        zero = int((vals == 0).sum())
        neg = int((vals < 0).sum())
        valid = len(vals)
        share_pos = pos / valid
        observed_val = obs[metric_name]

        row = {
            'metric': metric_name,
            'observed': observed_val,
            'CI_low_95': ci_low,
            'CI_high_95': ci_high,
            'CI_width': ci_width,
            'valid_resamples': valid,
            'skipped_resamples': 2000 - valid,
            'positive_resamples': pos,
            'zero_resamples': zero,
            'negative_resamples': neg,
            'share_positive': share_pos,
            'share_positive_str': f"{share_pos*100:.2f}%",
            'arithmetic': f"{pos}/{valid}={share_pos:.6f}",
            'status': 'TÍNH MỚI (dev)',
            'source': 'reports/week10/b2_oof.csv + reports/week9/t3_heldout_predictions.csv'
        }
        rows.append(row)
        print(f"[{metric_name}]")
        print(f"  Quan sát: {observed_val if isinstance(observed_val, int) else f'{observed_val:.6f}'}")
        print(f"  95% CI (percentile): [{ci_low:.6f}; {ci_high:.6f}] (độ rộng = {ci_width:.6f})")
        print(f"  Lượt hợp lệ: {valid}/2000; Dương: {pos}, Bằng 0: {zero}, Âm: {neg}")
        print(f"  Tỷ lệ lượt dương: {share_pos*100:.2f}%\n")

    # Save to CSV
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved results to {OUT_CSV}")

if __name__ == '__main__':
    main()
