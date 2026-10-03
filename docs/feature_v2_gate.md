# Feature Extractor v2 Gate

## Decision

Proceed to a versioned feature-v2 experiment, but do not replace the frozen 14-feature baseline
yet. None of the train-only challengers passed every predeclared acceptance rule. Validation remains
historical audit evidence only, and official test remains unopened.

The first nine-feature v2 train-only ablation is now complete. It improved MAE for both Ridge and
Random Forest on both targets but did not pass the predeclared tail-bias and macro-band thresholds.
See [feature_v2_train_only_results.md](feature_v2_train_only_results.md). The v1 deployment schema
and saved model artifacts remain unchanged.

## Evidence from the 30-essay controlled audit

- All 30 essays reproduced all 14 stored features within `1e-8` tolerance.
- Maximum absolute re-extraction difference: `4.93e-11`.
- LanguageTool returned 772 total detections.
- The current extractor used 113 detections classified as `grammar` (14.6%).
- It excluded 659 non-grammar detections, including 341 misspelling, 122 whitespace, 90
  uncategorized, 65 typographical, and 35 style detections.

This confirms implementation reproducibility; it does not establish that every LanguageTool match
is correct. False-positive and false-negative judgment remains a manual rubric task. The large
excluded share is evidence that the current two LanguageTool aggregates discard potentially useful
error-type information, not evidence that all excluded detections should become model features.

## Train-only challenger outcome

The strongest overall challenger was cumulative ordinal logistic regression:

| Trait | RF baseline OOF MAE | Ordinal OOF MAE | Improved folds | Macro-band improvement | Accepted? |
|---|---:|---:|---:|---:|---|
| Vocabulary | 0.372617 | 0.366556 | 4/5 | 4.14% | No |
| Grammar | 0.457694 | 0.451838 | 5/5 | 1.53% | No |

Inverse-square-root weighting reduced maximum tail bias by approximately 8–10% in its best RF
variants, but worsened the central band and improved only one of five folds. Linear and isotonic
OOF calibration corrected global calibration slope without materially resolving conditional tail
bias. No challenger reached the required 10% macro-band improvement and 20% tail-bias reduction.

## Feature-v2 candidates

The first nine implemented candidates are documented in
[feature_v2_train_only_results.md](feature_v2_train_only_results.md). The remaining items below
are research options; none should overwrite a v1 definition without a new train-only test.

Vocabulary candidates:

- lemma-based moving-average diversity;
- low-frequency content-word ratio and content-word frequency quantiles;
- spelling and word-form detections per 100 words;
- repeated lexical-error ratio, separated from unique error types.

Grammar candidates:

- LanguageTool grammar counts by stable rule family (agreement, verb form, determiner/article,
  preposition, word order);
- grammar-rule diversity and repeated-error concentration;
- error-free clause/T-unit proxy rather than sentence-only aggregation.

Syntax candidates:

- dependency distance and sentence-tree depth;
- T-unit count and clauses per T-unit;
- parser-failure and fragment indicators for audit, not automatic exclusion.

Highly correlated v1 pairs must be tested as replacement candidates: MTLD/MATTR,
mean-sentence-length/estimated-clauses, and the two existing LanguageTool aggregates.

## Next gate

The deterministic nine-feature schema, synthetic tests, 30-essay technical pilot, 3,050-row train
extraction, and train-only ablation have been completed. No candidate passed the original
acceptance gate. Before another feature iteration, a rubric-trained reviewer should assess
false positives, false negatives, word-form accuracy, and contextual word choice in the controlled
sample. Any resulting feature definition must be frozen before another train-only comparison.
Phase 4–7 artifacts remain baseline v1 and are not overwritten.
