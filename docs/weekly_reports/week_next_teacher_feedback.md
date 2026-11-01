# Post-Midterm Teacher Update

## 1. What the teacher asked

For the next meeting: (1) final large-error definition; (2) human-rater disagreement; (3) Ridge Validation results for Vocabulary and Grammar. These three items are complete below. Baseline Ridge/RF models and Official Test results remain frozen.

## 2. Final Large-Error Definition

For each essay i: L_i = 1[max(|y_V - RF_V|, |y_G - RF_G|) >= 1.0]. RF is the fixed reference for both targets: its Validation MAE was lower than Ridge (Vocabulary .372977 vs .374814; Grammar .447710 vs .456298). The evaluation protocol records the RF reference and threshold as frozen on 2026-10-01, before Phase 9.

Random, Shortest-first, Ridge Extremity and Ridge-RF Disagreement all select against the SAME RF binary error mask. Strategy changes only queue membership, not the reference errors. This avoids defining the outcome using Ridge, which is also used by Ridge Extremity. It is not a guarantee of statistical independence: the experiment measures detection of RF reference deviations, not universal system errors.

## 3. Human-Rater Disagreement

Eligible Validation paired ratings: N=762 per target. Existing saved reliability artifact:

| Metric | Vocabulary | Grammar |
|---|---:|---:|
| Human-human MAE | .416010498688 | .536745406824 |
| Human-human QWK | .501748272470 | .513990394356 |
| ICC(A,1) | .502076567111 | .514318430705 |
| Agreement within .5 (inclusive) | 59.317585% | 48.818898% |
| Agreement within 1.0 (inclusive) | 99.081365% | 97.506562% |

Important distinction: raw individual ratings here are integers. Exactly one-point differences are common (39.7638% Vocabulary; 48.6877% Grammar), while differences greater than one point are uncommon (.9186% / 2.4934%). We cannot call >=1 human disagreement rare from the within-1 table. The frozen >=1.0 RF-versus-aggregate threshold is a practical large-deviation definition, not proof of an objectively incorrect score. Natural rater variability remains; the threshold is not changed post-hoc.

## 4. Ridge Validation Results

N=762; directly from the saved Phase 7 regression table:

| Target | MAE | RMSE | R-squared | Selected alpha |
|---|---:|---:|---:|---:|
| Vocabulary | .374813522850 | .478537906664 | .304342300545 | 100.0 |
| Grammar | .456297593656 | .560329953630 | .324042341835 | .1 |

Ridge QWK is not recorded in that saved table; it is not fabricated. Alpha was selected by fixed five-fold CV on privacy-eligible model_train, without Official Test tuning.

## 5. Additional Work Started

Completed supplementary Validation sensitivity: mean captured 17/69 vs max 15/69, at the same 153 selected; no frozen strategy change. Original publication says 29 in its abstract but detailed statistics/released categories correspond to 44; canonical mapping remains unresolved, blocking canonical unseen-prompt evaluation. Development length descriptions, 14-feature error comparisons, a real numeric vector and a 32-essay blank human-coding sheet are prepared. Transformer work is a future plan only.

Sources: docs/data/phase7_tables/regression_metrics.csv; outputs/phase6/selected_parameters.json; docs/data/improvement_tables/human_machine_reliability.csv; docs/evaluation_protocol_freeze.md; shared-mask implementations in phase8 and the Phase 9 script. Additional results are recorded in docs/post_midterm/teacher_feedback_results.md. Verification: 93 tests passed; all 48 protected hashes matched.
