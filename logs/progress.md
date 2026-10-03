# Project Progress

## 2026-09-20 — Repository reset and Phase 0–2 foundation

- Replaced the obsolete sentence-level CEFR classification structure with the approved essay-level
  writing-score regression structure.
- Preserved the full plan and task list under `docs/planning/`.
- Recorded fixed scope, research questions, models, feature conditions, metrics, seed, risks, and
  decision history.
- Added canonical data-schema checks, leakage-aware split helpers, regression pipelines, evaluation
  helpers, and smoke tests.
- Removed historical CEFR code, reports, figures, and dataset-source notes from the active project.

## 2026-09-21 — Phase 1 Dataset Acceptance and ELLIPSE Corpus Ingestion

- Ingested official ELLIPSE Corpus datasets from `scrosseye/ELLIPSE-Corpus`:
  - `ELLIPSE_Final_github_train.csv` (3,911 essays, 26 columns, train set with rubric scores and demographics)
  - `ELLIPSE_Final_github_test.csv` (2,571 essays, 26 columns, decrypted test set with ground-truth scores)
  - `ellipsis_raw_rater_scores_anon_all_essay.csv` (8,890 unadjudicated raw essays with 2 rater scores)
  - `ELL_Rubrics.docx` (Official scoring rubric for Overall and 6 analytic traits)
- Cleaned directory structure: removed obsolete CEFR folders (`cefr_sentence`, `cefr_wordlist`).
- Formally updated `data/README.md` and `docs/data_card.md` to document ELLIPSE acceptance, schema mapping, rater process, and licenses.
- Updated `configs/experiment.yaml` and `src/data.py` with automatic schema adapter mapping for ELLIPSE fields.
- Verified with 11 automated test cases, black formatting, and flake8 linting.

## 2026-09-23 — Phase 1 Problem Definition and Success Criteria Sign-off

- Completed Task 1.1: Fixed primary research question (model disagreement review ranking vs. random selection).
- Completed Task 1.2: Specified use case (English teacher review triage queue for learner essays).
- Completed Task 1.3: Specified input text format and locked prompt boundary (prompt for splitting/slices, never a feature).
- Completed Task 1.4: Verified two target traits (`Vocabulary` and `Grammar`) on actual ELLIPSE data (1.0 to 5.0, 0.5 step).
- Completed Task 1.5: Finalized responsible use statement (scores are estimates, disagreement is a review signal, teacher has final authority).
- Completed Task 1.6: Pinned evaluation protocol (Ridge vs. RF, MAE/RMSE/R², Large Error Capture Rate@K vs. random baseline).
- Output document: `docs/phase1_problem_definition.md`.
- Re-audited and fully froze Phase 1 protocol on 2026-09-23: one essay-level priority score,
  consensus-error definition, K=20% primary budget, random/bootstrapped comparison, official-test
  freeze, approximate-continuity caveat, completed dataset acceptance checklist, and archived labels
  on the obsolete 6-target/DeBERTa planning documents.
- Completed Phase 2 local dataset audit on 2026-09-23. Verified all file hashes, 3,911 official
  train rows, 2,571 official test rows, 8,890 raw-rater rows, target distributions, text lengths,
  exact/near duplicates, split metadata, rubric mapping, and allowed columns. Recorded a blocking
  privacy finding: 138 exactly linkable final rows carry an identifying-information flag from at
  least one rater. Reproducible outputs are in `docs/data_inventory.md`, `docs/data/phase2_tables/`,
  `docs/assets/`, and `scripts/phase2_dataset_audit.py`.
- Completed Phase 3 split and leakage-control audit on 2026-09-23. Frozen 3,128 model-train,
  783 validation, and 2,571 untouched official-test rows; assigned five prompt-stratified,
  exact-text-grouped CV folds; verified zero duplicate IDs, zero cross-split exact hashes, and zero
  near-duplicate pairs at cosine >=0.95. The split script deliberately loads no official-test score
  columns. Manifest SHA-256 is
  `A998E6ED7EDD1361DE31739F4E3474A248A3EDA7F705EE8E2A8EBA36D396CC96`.

## 2026-09-23 â€” Phase 4 frozen 14-feature extractor

- Replaced the provisional 18-feature schema with exactly 14 predeclared length, vocabulary,
  detected-grammar, and syntax features.
- Added shared Unicode/whitespace cleaning, spaCy token/sentence/POS/dependency processing,
  LanguageTool 6.6 grammar-only filtering, short-text policies, and a reusable
  `extract_features(essay)` API.
- Extracted all 6,482 rows: 3,128 model-train, 783 validation, and 2,571 official test. Verified
  zero duplicate IDs, zero missing/non-finite features, and a one-to-one development target join.
- Kept official-test targets unloaded and exported no essay text, prompt, demographic, privacy, or
  prohibited human-score columns.
- Reviewed a text-free 25-row edge/random checklist; no blocking defect was found. Fixed numeric
  CSV serialization at 12 significant digits so output hashes remain stable after checkpoint
  reload.
- Added `docs/feature_specification.md`, `docs/phase4_feature_extraction_report.md`,
  `scripts/phase4_extract_features.py`, and Phase 4 QA tables.

## 2026-09-23 â€” Phase 5 feature audit and validation baselines

- Recorded a conservative privacy rule before modeling: only `not_flagged` rows are eligible. This
  leaves 3,050 model-train and 762 validation essays; split assignments are unchanged.
- Audited all 14 features: zero missing/infinite values, zero near-constant features, and zero
  train-validation stability failures under the frozen SMD/PSI/KS thresholds.
- Flagged one highly related pair: `mean_sentence_length` and
  `estimated_clauses_per_sentence` (Pearson 0.9728).
- Evaluated train-mean, length-only Ridge, length-only Random Forest, and length consensus on
  validation for Vocabulary and Grammar.
- At the 20% review budget, length-only disagreement captured 19.23% of large errors with lift
  0.958; 1,000 same-size random selections averaged 20.23% capture and lift 1.008.
- Kept official test unopened. Added reproducible CSV tables, a distribution figure, and a
  reader-facing Phase 5 workbook.

## 2026-09-24 — Phase 6 training readiness

- Replaced the stale raw-text training function with a guarded pipeline over the frozen 14-feature
  development table.
- Added exact schema, metadata-alignment, privacy, target-range, finite-value, split, and CV-fold
  checks. Official-test rows are rejected.
- Added separate fixed-fold MAE searches for Ridge Vocabulary, Ridge Grammar, Random Forest
  Vocabulary, and Random Forest Grammar.
- Added fold-level CV MAE, selected parameters, and text-free validation predictions. Validation
  metrics, disagreement queue, and error analysis remain deferred to Task 7.
- Added joblib model saving, selected parameters, text-free prediction tables, input/config
  hashes, package versions, integrity verification, and reload support.
- Full Task 6 training passed with 3,050 model-train rows, 762 validation predictions, 14 features,
  and fold sizes 609/610/610/611/610. Official test was not loaded.
- Closed the Phase 6 audit gaps: `training_summary.json` now contains explicit per-model metadata,
  code/config provenance (Git state plus source/config SHA-256 IDs), and the regression suite covers
  reload-prediction equality and Vocabulary/Grammar target isolation. Tests pass (`26 passed`), and
  two identical runs produced byte-identical model, CV, prediction, metadata, and manifest files.

## 2026-09-24 — Phase 7 validation regression evaluation

- Evaluated the four saved Phase 6 predictions on exactly 762 eligible validation essays after strict
  ID/label/split checks; official test remained unopened.
- Verified Phase 5 baseline hashes and recomputed baseline metrics before calculating signed
  full-feature MAE improvements.
- Random Forest was selected as the validation point predictor for both Vocabulary and Grammar under
  the frozen lower-MAE/Ridge-tie rule. Added text-free predictions, metrics, error tables, figures,
  and the reproducible report in `docs/phase7_regression_evaluation.md`.
- Phase 7 tests and evaluator reruns pass. Disagreement queue, error-capture comparison, ablation,
  and official-test evaluation remain future work.
- Closed the Phase 7 audit gaps by comparing against all four Phase 5 baselines, documenting the
  regression-to-the-middle error pattern and raw out-of-rubric prediction, ordering length bands
  Q1–Q4, and expanding plot bounds so the unclipped prediction remains visible.

## Next gate

Proceed to the separately specified disagreement/review evaluation task while keeping official test frozen.

## 2026-09-24 — Baseline-v1 improvement study

- Froze Phase 6–7 baseline v1: RF validation MAE 0.372977 Vocabulary and 0.447710 Grammar.
- Added development-ID-allowlisted raw-rater reliability audit; retained 3,812 eligible
  development rows and zero official-test IDs.
- Human–human MAE on the 762-row validation audit population is 0.416010 Vocabulary and 0.536745
  Grammar; RF-versus-individual-rater MAE is 0.457250 and 0.556102 respectively.
- Created a controlled 30-row large-error/good-prediction audit plus a git-ignored text-bearing
  review copy. Re-extraction reproduced every frozen feature within 1e-8.
- Ran ten train-only OOF variants on the 3,050 rows and five frozen folds. Validation rows used: 0;
  official-test rows used: 0. No challenger passed all predeclared tail-bias acceptance rules.
- Ordinal logistic improved OOF MAE to 0.366556 Vocabulary and 0.451838 Grammar but did not meet
  macro-band or tail-bias thresholds. Feature-v2 exploration is therefore gated on.

## 2026-09-24 — Human-machine comparison figures

- Regenerated four text-free validation figures for score distributions, calibration by human
  score, signed bias by human score, and human-human versus machine-human MAE.
- Figures use the same 762 privacy-eligible Phase 7 validation rows and raw continuous predictions;
  no retraining, clipping, rounding, or official-test access occurred.
- Added a SHA-256 figure manifest at
  `docs/data/improvement_tables/human_machine_figure_manifest.json`.
