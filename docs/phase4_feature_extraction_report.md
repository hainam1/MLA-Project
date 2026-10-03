# Phase 4 Feature Extraction Report

> **Completed:** 2026-09-23  
> **Result:** Passed all Phase 4 integrity checks. The privacy hold recorded at completion was
> resolved before Phase 5 by excluding non-`not_flagged` rows.

## Outcome

The repository now has one reusable `extract_features(essay) -> dict[str, float]` API and a batch
pipeline that creates exactly the same ordered 14-feature schema for model-train, validation,
official test, and a new essay. The implementation uses spaCy `en_core_web_sm`, `lexicalrichness`,
`wordfreq`, and a local LanguageTool 6.6 server.

| Output partition | Rows | Feature columns | Targets attached |
|---|---:|---:|---|
| Model train | 3,128 | 14 | Vocabulary and Grammar in development table |
| Validation | 783 | 14 | Vocabulary and Grammar in development table |
| Official test | 2,571 | 14 | No; test targets were not loaded |
| **Total** | **6,482** | **14** | â€” |

The final validation checks found **0 duplicate feature IDs**, **0 missing feature values**, and
**0 non-finite feature values**. The development target join contains exactly 3,911 rows and was
validated one-to-one by essay ID. No text, prompt, demographics, privacy status, source-computed
feature, Overall score, or other human score is present in any feature table.

## Observed feature ranges

These ranges are descriptive QA, not feature-selection evidence and not model performance.

| Feature | Min | Mean | Max |
|---|---:|---:|---:|
| `word_count` | 13.0000 | 427.9576 | 1290.0000 |
| `sentence_count` | 1.0000 | 19.0747 | 107.0000 |
| `mean_sentence_length` | 6.4000 | 26.7551 | 508.0000 |
| `mtld` | 13.7369 | 53.5671 | 204.1200 |
| `mattr` | 0.4400 | 0.7333 | 0.9630 |
| `mean_word_frequency` | 4.0654 | 6.0733 | 6.4470 |
| `mean_word_length` | 3.1495 | 4.2068 | 5.5455 |
| `lexical_density` | 0.2750 | 0.4754 | 0.7783 |
| `noun_diversity` | 0.0823 | 0.4609 | 1.0000 |
| `detected_grammar_errors_per_100_words` | 0.0000 | 0.9950 | 8.3527 |
| `detected_error_free_sentence_ratio` | 0.0000 | 0.7948 | 1.0000 |
| `complex_sentence_ratio` | 0.0000 | 0.8573 | 1.0000 |
| `estimated_clauses_per_sentence` | 1.0000 | 4.9085 | 78.0000 |
| `subordinate_clause_ratio` | 0.0000 | 0.6061 | 0.8958 |

Very high sentence length and clause-per-sentence values occur in essays with run-on or missing
sentence punctuation. They are retained because they follow the frozen parser-based definition;
they are not silently clipped or corrected.

## Manual review of 25 essays

The checklist intentionally covers five shortest texts, five longest texts, the highest detected
grammar-error rates, the highest estimated clause rates, and a seed-42 random remainder. All 25
selected essays have `privacy_review_status=not_flagged`; neither text nor privacy status is copied
into the checklist.

- All 25 passed finite-value and `[0, 1]` ratio checks.
- Alphabetic word counts were cross-checked against an independent regex count. Differences on
  long essays were attributable to the documented tokenization rule, especially punctuation and
  token boundaries; no row-alignment defect was found.
- Sentence counts were cross-checked against punctuation patterns and the source audit count.
  Extreme clause rates corresponded to one-sentence/run-on patterns rather than join errors.
- LanguageTool edge cases remain detector outputs only; high rates were not relabeled as confirmed
  human errors.
- No blocking extractor defect was found. The only implementation-level reproducibility issue
  encountered was floating-point CSV serialization changing hashes after checkpoint reload; it
  was fixed by freezing output precision to 12 significant digits. Hashes are stable on rerun.

The row-level, text-free record is
[`manual_feature_review.csv`](data/phase4_tables/manual_feature_review.csv).

## Reproducibility and hashes

Run `uv run python scripts/phase4_extract_features.py`. Extraction checkpoints every 100 essays;
rerunning after completion performs integrity checks and recreates final tables without calling the
grammar service again.

| Local generated file | SHA-256 |
|---|---|
| `data/05_model_features/essay_features.csv` | `0BC057E3E528D4C1E07304A88B8BBB103596FD473A85761C0360BE06E319C246` |
| `data/05_model_features/development_features_with_targets.csv` | `CAFB1BCA27423E0A8B6FB2D282FB7BD87FB703FC637A3A15778855CAF0817A5B` |
| `data/05_model_features/official_test_features.csv` | `DC7F7D03A9210A87F834B99CE5ABD202296455D7C65871C52AB8FA2DEA4A1967` |

The generated data files and checkpoint are Git-ignored. Their hashes and aggregate evidence are
tracked in `docs/data/phase4_tables/phase4_audit_summary.json`.

## Phase gate

Tasks 4.1â€“4.9 are complete. At Phase 4 completion, the 138 linkable essays flagged for possible
identifying information and 14 unresolved raw-ID links still blocked modeling. Before any Phase 5
metric was computed, the project recorded a conservative rule: only `not_flagged` rows are eligible
for fitting and evaluation. The numeric tables remain complete for auditability, while downstream
scripts apply the frozen privacy filter.
