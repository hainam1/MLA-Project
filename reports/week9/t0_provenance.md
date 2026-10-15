# Task 0 — PARTIAL (chronology limitation)

Numerical reproduction complete. Disagreement is NOT demonstrated better than random. The date Test was first evaluated cannot be established from the available history; therefore committed and uncommitted changes cannot honestly be classified before/after first access.

## Reproduction and evidence

Script: `scripts/week9/t0_provenance.py`. Exact entry command: `.venv/Scripts/python.exe scripts/week9/t0_provenance.py --capture`. Each child command: `.venv/Scripts/python.exe scripts/week9/t0_provenance.py`. Saved predictions only; no fitting, model loading or prediction. Test reads are confined to this Task 0 reproduction. Frozen primary definitions only.

Raw combined terminal output: `logs/t0.log`; individual fresh-process outputs: `logs/t0_run1.log`, `logs/t0_run2.log`. CSV row references below mean data rows, excluding the header.

```text
seed=42; draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending
Python=3.14.5; numpy=2.4.6; pandas=2.3.3; scipy=1.18.1
CHRONOLOGY: first Test evaluation date cannot be determined from available Git history; file mtimes are not execution timestamps.
CHRONOLOGY: docs/phase9_official_test_evaluation.md first/last history:
INTEGRITY: frozen protocol, saved Test outputs, Test feature/label sources and split manifest match saved manifest SHA256.
RESULT {"K": 69, "N": 762, "disagreement": 15, "draws": 1000, "expected_random": 13.854330708661417, "hypergeom_p": 0.40980554727071455, "k": 153, "random_first_draw": 16, "random_mean": 13.946, "random_p2_5": 8.0, "random_p97_5": 20.0, "ridge_extremity": 10, "seed": 42, "shortest": 15, "split": "Validation", "tail_draws": 415}
ARITHMETIC Validation: random_mean=13946/1000=13.946; empirical_p=415/1000=0.415; expected=153*69/762=13.8543307087; capture=15/69=0.217391304348; exact_p=hypergeom.sf(14,762,69,153)=0.409805547271
RESULT {"K": 208, "N": 2518, "disagreement": 47, "draws": 1000, "expected_random": 41.6330420969023, "hypergeom_p": 0.18832467136922115, "k": 504, "random_first_draw": 41, "random_mean": 41.427, "random_p2_5": 32.0, "random_p97_5": 52.02499999999998, "ridge_extremity": 43, "seed": 42, "shortest": 37, "split": "Test", "tail_draws": 165}
ARITHMETIC Test: random_mean=41427/1000=41.427; empirical_p=165/1000=0.165; expected=504*208/2518=41.6330420969; capture=47/208=0.225961538462; exact_p=hypergeom.sf(46,2518,208,504)=0.188324671369
INTEGRITY: all inventoried source files unchanged after reproduction.
STATUS: PARTIAL provenance chronology; numerical reproduction complete. Missing: independently established first Test execution date and before/after classification of changes.
```

[src: reports/week9/logs/t0_run1.log RESULT, ARITHMETIC, CHRONOLOGY, INTEGRITY and STATUS lines]

Random is represented by the mean over the frozen draws; the first draw is also provided in the metrics CSV. Percentiles use NumPy's default linear interpolation. Exact p is the hypergeometric survival function, not the empirical tail proportion. Arithmetic for means, capture, expected counts and empirical p is printed verbatim above. No new Test design or sensitivity analysis was run.

Validation: see the verbatim RESULT and ARITHMETIC lines above. [src: reports/week9/t0_metrics.csv row 1]

Test: see the verbatim RESULT and ARITHMETIC lines above. [src: reports/week9/t0_metrics.csv row 2]

## Artifact inventory

Dates are filesystem modification times in UTC and Git author/committer timestamps. Git first/last means oldest/newest entry from `git log --follow`, not an execution date. Empty history is explicitly reported. The original scripts are inventoried but were not executed, because the Test script generates predictions and existing outputs.

| Path | Bytes | Modified UTC | First commit (hash, author, committer, subject) | Last commit | Evidence |
|---|---:|---|---|---|---|
| `docs/evaluation_protocol_freeze.md` | 4154 | 2026-10-01T16:27:59.175393+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 1] |
| `outputs/phase6/validation_predictions.csv` | 53077 | 2026-09-24T06:07:09.695033+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 2] |
| `outputs/predictions/phase7_validation_regression_predictions.csv` | 57514 | 2026-09-24T06:54:58.967934+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 3] |
| `outputs/predictions/official_test_predictions.csv` | 455602 | 2026-10-01T16:45:24.436881+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 4] |
| `scripts/phase8_evaluate_review_prioritization.py` | 16590 | 2026-10-01T16:22:36.857168+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 5] |
| `scripts/phase9_official_test_evaluation.py` | 25571 | 2026-10-01T16:44:55.498529+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 6] |
| `src/mla_project/evaluation/phase8.py` | 5339 | 2026-10-01T16:22:36.759684+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 7] |
| `src/mla_project/evaluation/phase9.py` | 5545 | 2026-10-01T16:44:42.864264+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 8] |
| `src/mla_project/review/baselines.py` | 3221 | 2026-10-01T16:19:14.179678+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 9] |
| `scripts/finalization_supplement.py` | 7586 | 2026-10-03T14:06:27.970125+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 10] |
| `docs/data/phase9_tables/artifact_manifest.json` | 3631 | 2026-10-01T16:45:24.647011+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 11] |
| `docs/data/phase8_tables/large_error_labels.csv` | 72626 | 2026-10-01T16:22:52.272121+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 12] |
| `docs/data/phase9_tables/large_error_labels.csv` | 277878 | 2026-10-01T16:45:24.529960+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 13] |
| `docs/data/phase8_tables/random_reference_distribution.csv` | 653948 | 2026-10-01T16:22:52.257898+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 14] |
| `docs/data/phase9_tables/random_reference_distribution.csv` | 751771 | 2026-10-01T16:45:24.511375+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 15] |
| `docs/data/phase8_tables/review_strategy_comparison.csv` | 4894 | 2026-10-01T16:22:52.212306+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 16] |
| `docs/data/phase9_tables/review_strategy_comparison.csv` | 891 | 2026-10-01T16:45:24.438892+00:00 | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | 2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d / 2026-10-03T19:24:28+07:00 / 2026-10-03T19:24:28+07:00 / feat: rebuild project around ELLIPSE scoring pipeline | [src: reports/week9/t0_inventory.csv row 17] |
| `data/05_model_features/development_features_with_targets.csv` | 814571 | 2026-09-23T10:56:53.345080+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 18] |
| `data/05_model_features/official_test_features.csv` | 520631 | 2026-09-23T10:56:53.379178+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 19] |
| `data/03_clean_ready_to_use/official_test_2571.csv` | 11940606 | 2026-09-25T09:30:00.332540+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 20] |
| `data/02_split_manifest/essay_split_manifest.csv` | 920231 | 2026-09-23T10:20:52.295739+00:00 | NO GIT HISTORY | NO GIT HISTORY | [src: reports/week9/t0_inventory.csv row 21] |

SHA256 values for all listed sources are in the same inventory. Validation's Phase 6 file is the prediction source used by the original ranking script; the Phase 7 copy is inventoried for discovery completeness. Saved large-error tables supply human target means; error flags are recomputed directly from the saved RF predictions. Saved manifest medians supply the frozen Ridge extremity centers.

## Changes since freeze and chronology

Full requested Git stat output is preserved in `t0_git_since_freeze.txt` and printed verbatim in both raw runs. Every committed changed path is enumerated in `t0_committed_changes.csv`, with classification UNKNOWN because first Test access is undated. The Test report's first/last commit evidence is in the CHRONOLOGY section of the raw log. A commit containing an existing Test report establishes report presence at that commit; it does not date first Test access or order edits within that commit. The protocol's stated freeze date is a document assertion rather than independently timestamped execution evidence.

`t0_worktree_status.txt` separately records current tracked edits and untracked paths, including pre-existing work. Git log cannot date those changes; filesystem mtimes cannot prove whether they precede Test access. No before/after labels have been guessed. No existing result, protocol, README or manual sample was modified; no commit or push was performed.

## Fresh-process repeat proof

```text
RUN1_SHA256=19df129db25042ddd6e6c47d02ed000ba97f0fe30b532ebea75912d22e40b3b4
RUN2_SHA256=19df129db25042ddd6e6c47d02ed000ba97f0fe30b532ebea75912d22e40b3b4
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t0.log final hash lines]

Missing for full completion: independent evidence of the first Test evaluation timestamp and a defensible before/after classification of each change. All numerical checks and frozen saved-output comparisons passed, as shown by the raw logs.
