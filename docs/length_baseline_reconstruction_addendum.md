# Protocol Addendum: Length-Only Baseline Artifact Reconstruction

> Authorized before the one-time official-test evaluation. No official-test data were accessed to
> create this addendum.

The Phase 5 length-only baseline estimators were fitted under a frozen specification, but the
estimators themselves were not serialized. Only their validation predictions and metrics were
retained. To restore the missing artifacts, the estimators will be reconstructed once using only
the 3,050 privacy-eligible `model_train` essays.

The reconstruction is fixed as follows:

- Features, in order: `word_count`, `sentence_count`, `mean_sentence_length`.
- Length-only Ridge: the original preprocessing pipeline with `alpha = 1.0`.
- Length-only Random Forest: the original preprocessing pipeline with `n_estimators = 300`,
  `max_depth = None`, `min_samples_leaf = 2`, `max_features = "sqrt"`, and random seed 42.
- Separate estimators are reconstructed for Vocabulary and Grammar.
- No hyperparameter search, alternative specification, validation selection, or official-test
  fitting is permitted.

Before serialization, reconstructed validation predictions and metrics must reproduce the
historical Phase 5 artifacts within numerical tolerance. A mismatch stops the workflow before any
official-test access. Successful artifacts will be stored under `outputs/phase5/reconstructed/`.

## Reconstruction result

Status: **reproduction check passed; artifacts serialized before official-test access**.

- Maximum absolute validation-prediction difference across the four estimators:
  `4.997779967652605e-12`, below the frozen tolerance `1e-10`.
- Maximum absolute historical metric difference: `4.8654172357665004e-09`, below the frozen
  tolerance `1e-8`.
- Development-only reconstruction affirmed `official_test_loaded: false`.

| Reconstructed artifact | SHA-256 |
|---|---|
| `length_ridge_vocabulary.joblib` | `AA069D615F77BE8CCE8561E6044A4D73F22805537DBFDBD79D8DC38876187FBA` |
| `length_random_forest_vocabulary.joblib` | `EBA39122B5F2A7209954D9D7B44C59BBB71D6F5C4EA707F14CEBA7A14C7E3324` |
| `length_ridge_grammar.joblib` | `1F7A2DB84DC086860B6EFC4A75BB8ECFB418EDDF89C6D7643B9C7ADD296B60B5` |
| `length_random_forest_grammar.joblib` | `73B16013F4AE9B043E1A8FCE688AD39AFC3ACA85D070A89FFE29E0BD30B55CF6` |
