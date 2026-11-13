"""Section D: LanguageTool 6.6 and GECToR on the exact same 150-word window.
Compares both tools against human reader counts on 68 Validation essays
(36 random Validation essays + 32 Week 9 Validation essays).
Strictly uses the same counting function as Section A.
Includes 10-case sanity reproduction assertion before running 68 essays.
"""
from pathlib import Path
import csv
import json
import math
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import language_tool_python

ROOT = Path(__file__).resolve().parents[1]
INPUT_GEC_68 = ROOT / 'reports/week10/gec_part_a_68.csv'
INPUT_A_CSV = ROOT / 'docs/final_evidence/a_doi_chieu_so_lieu.csv'
OUT_COUNTS_CSV = ROOT / 'docs/final_evidence/d_tool_window_counts.csv'
OUT_AGREEMENT_CSV = ROOT / 'docs/final_evidence/d_tool_agreement.csv'

def count_lt_grammar(tool, text):
    """Exact counting function from Section A."""
    first150_words = text.split()[:150]
    first150_text = ' '.join(first150_words)
    matches = tool.check(first150_text)
    grammar_matches = [m for m in matches if getattr(m, 'ruleIssueType', '').casefold() == 'grammar']
    return len(grammar_matches), len(matches), len(first150_words)

def bootstrap_spearman(x, y, n_boot=2000, seed=42):
    """Essay-level paired bootstrap CI for Spearman r (linear percentile)."""
    assert len(x) == len(y)
    n = len(x)
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        r, _ = spearmanr(x[idx], y[idx])
        if np.isfinite(r):
            samples.append(r)
        else:
            samples.append(0.0)
    samples = np.asarray(samples)
    ci_low = float(np.percentile(samples, 2.5))
    ci_high = float(np.percentile(samples, 97.5))
    return ci_low, ci_high

def main():
    # 1. Load texts
    texts = {}
    for p in ['data/03_clean_ready_to_use/model_train_3128.csv', 'data/03_clean_ready_to_use/validation_783.csv']:
        with open(ROOT / p, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                texts[r['essay_id']] = r['essay_text']

    # 2. Initialize LanguageTool 6.6 offline
    print("Initializing LanguageTool 6.6 offline...", flush=True)
    tool = language_tool_python.LanguageTool('en-US', language_tool_download_version='6.6')

    # 3. Sanity check: Run on the 10 error cases from Section A and compare with a_doi_chieu_so_lieu.csv
    print("--- SANITY CHECK ON 10 SECTION A CASES ---", flush=True)
    df_a = pd.read_csv(INPUT_A_CSV)
    a_dict = df_a.set_index('essay_id').to_dict('index')

    for eid, row in a_dict.items():
        g_count, all_count, n_words = count_lt_grammar(tool, texts[eid])
        assert g_count == row['lt_grammar_matches_first150'], (
            f"MISMATCH on {eid}: expected LT grammar {row['lt_grammar_matches_first150']}, got {g_count}!"
        )
        assert all_count == row['lt_total_matches_first150'], (
            f"MISMATCH on {eid}: expected LT all {row['lt_total_matches_first150']}, got {all_count}!"
        )
        assert n_words == row['words_in_window'], (
            f"MISMATCH on {eid}: expected words {row['words_in_window']}, got {n_words}!"
        )
        print(f"PASS {eid}: words={n_words}, LT grammar={g_count}, LT all={all_count}", flush=True)
    print("ALL 10 SECTION A ESSAYS MATCH EXACTLY! Proceeding to count 68 Validation essays...\n", flush=True)

    # 4. Load 68 essays from gec_part_a_68.csv
    df_68 = pd.read_csv(INPUT_GEC_68)
    assert len(df_68) == 68

    window_rows = []
    print("Counting LanguageTool 6.6 real on first150 for 68 Validation essays...", flush=True)
    for i, r in df_68.iterrows():
        eid = r['essay_id']
        g_count, all_count, n_words = count_lt_grammar(tool, texts[eid])
        window_rows.append({
            'essay_id': eid,
            'sample_group': r['sample_group'],
            'band': r.get('band', ''),
            'words_in_window': n_words,
            'reader_count': float(r['reader']),
            'lt_real_grammar_first150': g_count,
            'lt_real_total_first150': all_count,
            'lt_historical_estimate': float(r['LT_estimate']),
            'gector_grammar_first150': int(r['edits_grammar']),
            'gector_all_first150': int(r['edits_all']),
            'status': 'TÍNH MỚI (dev)',
            'source': 'LanguageTool 6.6 (local offline) + GECToR roberta-base-5k + ERRANT 3.0.2'
        })
        if (i + 1) % 20 == 0 or (i + 1) == 68:
            print(f"Counted {i+1}/68 essays...", flush=True)

    tool.close()
    print("LanguageTool counting completed.\n", flush=True)

    df_window = pd.DataFrame(window_rows)
    OUT_COUNTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_window.to_csv(OUT_COUNTS_CSV, index=False)
    print(f"Saved window counts to {OUT_COUNTS_CSV}\n")

    # 5. Compute agreement metrics separately for random36, week9_32, and pooled68
    groups = [
        ('random36', df_window[df_window['sample_group'] == 'random36']),
        ('week9_32', df_window[df_window['sample_group'] == 'week9_32']),
        ('pooled68', df_window)
    ]

    agreement_rows = []

    print("=== TOOL AGREEMENT WITH HUMAN READER ON FIRST 150 WORDS ===")
    for grp_name, grp_df in groups:
        reader = grp_df['reader_count'].to_numpy(dtype=float)
        n = len(reader)
        reader_mean = float(np.mean(reader))

        tools_to_evaluate = [
            ('LT_real_first150', grp_df['lt_real_grammar_first150'].to_numpy(dtype=float), 'LanguageTool 6.6 real on first 150 words'),
            ('LT_historical_estimate', grp_df['lt_historical_estimate'].to_numpy(dtype=float), 'Historical LT full-essay scaled estimate (Phụ lục B.5)'),
            ('GECToR_grammar_first150', grp_df['gector_grammar_first150'].to_numpy(dtype=float), 'GECToR + ERRANT grammar edits on first 150 words'),
            ('GECToR_all_first150', grp_df['gector_all_first150'].to_numpy(dtype=float), 'GECToR + ERRANT all edits on first 150 words')
        ]

        print(f"\n--- Group: {grp_name} (N = {n}, reader_mean = {reader_mean:.4f}) ---")
        for tool_name, tool_vals, tool_desc in tools_to_evaluate:
            sp_r, sp_p = spearmanr(tool_vals, reader)
            ci_low, ci_high = bootstrap_spearman(tool_vals, reader, n_boot=2000, seed=42)
            
            tool_mean = float(np.mean(tool_vals))
            signed_bias = tool_mean - reader_mean
            mae = float(np.mean(np.abs(tool_vals - reader)))

            row = {
                'group': grp_name,
                'n': n,
                'tool': tool_name,
                'tool_description': tool_desc,
                'spearman_r': float(sp_r),
                'spearman_p': float(sp_p),
                'spearman_95ci_low': ci_low,
                'spearman_95ci_high': ci_high,
                'tool_mean': tool_mean,
                'reader_mean': reader_mean,
                'signed_bias': signed_bias,
                'abs_bias': abs(signed_bias),
                'mae': mae,
                'arithmetic': f"signed_bias={tool_mean:.4f}-{reader_mean:.4f}={signed_bias:.4f}; MAE=mean(|tool-reader|)={mae:.4f}",
                'status': 'TÍNH MỚI (dev)',
                'source': 'reports/week10/reading_sheet_da_danh_gia.xlsx + reports/week9/t4_reading_summary.csv'
            }
            agreement_rows.append(row)
            print(f"[{tool_name}]")
            print(f"  Spearman: {sp_r:.4f} [95% CI: {ci_low:.4f}; {ci_high:.4f}] (p = {sp_p:.4e})")
            print(f"  Mean tool: {tool_mean:.4f} vs Reader mean: {reader_mean:.4f} -> Signed bias: {signed_bias:+.4f} (Abs bias: {abs(signed_bias):.4f})")
            print(f"  MAE: {mae:.4f}")

    df_agreement = pd.DataFrame(agreement_rows)
    df_agreement.to_csv(OUT_AGREEMENT_CSV, index=False)
    print(f"\nSaved agreement metrics to {OUT_AGREEMENT_CSV}")

    # 6. Evaluation of old acceptance criterion on pooled 68 essays
    # Acceptance rule from config:
    # Spearman(GECToR_grammar, reader) > Spearman(LT, reader) AND abs(mean(GECToR_grammar) - mean(reader)) < abs(mean(LT) - mean(reader))
    pooled_stats = df_agreement[df_agreement['group'] == 'pooled68'].set_index('tool').to_dict('index')
    
    gec_sp = pooled_stats['GECToR_grammar_first150']['spearman_r']
    gec_abs_bias = pooled_stats['GECToR_grammar_first150']['abs_bias']
    
    # Check against LT_historical_estimate
    lt_est_sp = pooled_stats['LT_historical_estimate']['spearman_r']
    lt_est_abs_bias = pooled_stats['LT_historical_estimate']['abs_bias']
    pass_vs_historical = (gec_sp > lt_est_sp) and (gec_abs_bias < lt_est_abs_bias)
    
    # Check against LT_real_first150
    lt_real_sp = pooled_stats['LT_real_first150']['spearman_r']
    lt_real_abs_bias = pooled_stats['LT_real_first150']['abs_bias']
    pass_vs_real = (gec_sp > lt_real_sp) and (gec_abs_bias < lt_real_abs_bias)

    print("\n=== ACCEPTANCE CRITERIA EVALUATION (POOLED 68) ===")
    print(f"GECToR grammar: Spearman = {gec_sp:.4f}, Abs bias = {gec_abs_bias:.4f}")
    print(f"LT historical estimate: Spearman = {lt_est_sp:.4f}, Abs bias = {lt_est_abs_bias:.4f}")
    print(f"  Criteria vs historical estimate: Spearman higher? {gec_sp > lt_est_sp}; Abs bias smaller? {gec_abs_bias < lt_est_abs_bias} -> OVERALL: {'PASS' if pass_vs_historical else 'FAIL'}")
    print(f"LT real first 150: Spearman = {lt_real_sp:.4f}, Abs bias = {lt_real_abs_bias:.4f}")
    print(f"  Criteria vs LT real: Spearman higher? {gec_sp > lt_real_sp}; Abs bias smaller? {gec_abs_bias < lt_real_abs_bias} -> OVERALL: {'PASS' if pass_vs_real else 'FAIL'}")

if __name__ == '__main__':
    main()
