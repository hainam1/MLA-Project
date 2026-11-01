# Development-only unseen-prompt evaluation design

Post-midterm supplementary research requested by instructor. Current status: BLOCKED pending authoritative canonical prompt mapping. No grouped models were fitted and no unseen-prompt performance numbers are available.

## Population and group identity

Use the 3812 privacy-eligible development essays (3050 original model_train + 762 original Validation). Official Test rows/labels/features/predictions must not enter fitting or evaluation. Require an authoritative essay-ID-to-canonical-prompt mapping covering every eligible development essay and preserving variants within the same group. Do not substitute project `prompt_id` strings for canonical identity silently.

Check exact-text hashes. If duplicate texts occur across canonical groups, resolve/document grouping or exclusions before fitting; no duplicate text may bridge training and holdout. Group held-out prompts entirely; no essay-level prompt stratification.

## Fixed plan once mapping is available

Five-fold GroupKFold by canonical prompt, with deterministic input sorted by string essay ID and groups ordered consistently. Every essay receives one out-of-fold prediction from a model that never saw its canonical prompt. Save fold assignments and canonical mapping hashes before fitting. Groups, not individual essays, define the holdout.

Use the same frozen 14-feature matrix and four independently fitted target/model pairs. Use frozen parameters, no new search:

- Ridge Vocabulary alpha=100.0; Ridge Grammar alpha=.1.
- RF Vocabulary: n_estimators=300, max_depth=10, max_features=sqrt, min_samples_leaf=2.
- RF Grammar: same except min_samples_leaf=5.
- Preserve frozen random-state/single-worker conventions. Imputer and Ridge scaler are fitted only inside each training fold.

Frozen baseline hyperparameters were originally developed on the development set. Reusing them makes this a supplementary fixed-configuration stress test, not a fully nested unbiased estimate of a model-selection process. State this limitation; do not perform test-driven retuning.

## Reporting

For each family/target report saved seen-category Validation MAE, pooled grouped out-of-fold MAE, and delta (unseen minus seen). Add RMSE and QWK with the frozen half-up/clipped .5-grid convention. Across canonical held-out groups report per-group N/MAE plus unweighted mean, SD, min/max; state whether each summary is essay-weighted or group-weighted. Show fold/group variability; do not choose favorable holdouts.

Seen-Validation and grouped evaluations have different training populations/sizes, so delta is descriptive and not a pure isolated causal prompt effect. Store all new assignments, metrics and optional models under `outputs/post_midterm/unseen_prompt/` and `docs/data/post_midterm/`. Never replace baseline joblib files or official metrics.

## Length by prompt

The current operational-only development table has N, mean, median, SD, Q1/Q3 and IQR per category. It can support a cautious description of observed length differences, but a canonical version must be recomputed after mapping is supplied. Do not treat between-category variation as evidence that prompt causes length.
