# Tree-spread signal lock

## Signal definition

For each essay, compute the population standard deviation (ddof=0) of the predictions of the 300 frozen RF trees for each target, Vocabulary and Grammar. The signal is max(std_V, std_G). Rank the signal descending; break ties by essay_id string ascending. Review budget k=ceil(0.20*N) in each evaluation fold (or the single independent evaluation set).

RF parameters are frozen: n_estimators=300, max_features="sqrt", max_depth=10, min_samples_leaf=2 for Vocabulary and 5 for Grammar, random_state=42, n_jobs=1; the frozen 14-feature schema and training-only median imputation are unchanged. For fold evaluation, fit these fixed pipelines only on the other folds. Large error is max(|y_V-RF_V|, |y_G-RF_G|) >= 1.0.

## Future confirmation protocol

Use a new independently obtained, privacy-eligible labeled essay cohort whose labels and signal performance have not been inspected for signal selection. The reused development and Validation data cannot provide clean confirmation. Do not access Test during this Week 10 work. Before opening any future confirmation labels, record the cohort identity, eligibility, file hashes, and fold membership; do not tune or select signals on that cohort.

For prompt-held-out evaluation, sort essay_id strings ascending and use GroupKFold(n_splits=5) grouped by normalised_prompt, with the same frozen feature schema, RF parameters, Ridge alpha=100 for Vocabulary and 0.1 for Grammar, training-only median imputation, and training-only StandardScaler for Ridge, as scripts/week9b/tree_spread_oof.py. Prompts must be disjoint between training and the held-out fold. Report each fold's N_f, K_f (large errors), k_f=ceil(0.20*N_f), and caught C_f. Pool the fixed fold queues without global reranking: caught C=sum(C_f), total large errors K=sum(K_f), expected E=sum(k_f*K_f/N_f), and capture C/K. The one-sided exact reference p is P(sum(H_f)>=C), computed by convolution of H_f~Hypergeom(N_f,K_f,k_f). For a single independent holdout, use k*K/N and the one-sided hypergeometric tail. State the independent-fold reference-null assumption when OOF training sets overlap.

Compare with D=max(|RF_V-Ridge_V|, |RF_G-Ridge_G|), using the same held-out predictions, budgets, and essay_id tie-break. Report paired caught counts, both/only-tree/only-D/neither among large errors, caught_tree-caught_D, and AUROC_tree-AUROC_D. Use the fixed-queue paired prompt-cluster bootstrap from scripts/week9b/paired_tree_spread.py: 2,000 resamples of all prompt clusters with replacement, default_rng(42), percentile 95% intervals, no reranking/refitting or budget recomputation. Report valid/skipped draws; the fraction of positive bootstrap differences is not an exact p value. Make no signal or threshold changes after confirmation labels are viewed.

## Status

Signal chosen after viewing Validation (25/69, p=0.00078); checked once on development GroupKFold-by-prompt (96/386, p=0.0085) which is not a clean confirmation because development was reused; Test not used.

## Provenance

Written at git commit: 3e6f0d80e0f9228d12328f8c16d4c1f947f9ee31

UTC date/time (`date -u`): Mon Oct 19 05:41:03 UTC 2026

SHA256 scripts/week9b/tree_spread_oof.py: ccc8524cccc50b7d78b2680428bd188cd84587c31ab6bddb9af9f006aef9546d

SHA256 reports/week9/RESULTS_week9.md: 03921a62b35e96499336c9119c3b0fb4dfa27b73788f61ad42daf73a05243f1d
