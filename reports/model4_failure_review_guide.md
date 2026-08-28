# Model 4 Failure Review Guide

Updated: 2026-08-27

## Purpose

`data/review/model4_failure_candidates.csv` contains real held-out outputs selected
for human review. Automatic reasons are triage signals only. They must not be used
as Model 4 labels without a human verdict.

## Review fields

- `human_verdict`: `acceptable` or `failure`.
- `failure_category`: `lexical_constraint`, `cefr_mismatch`, `meaning_loss`,
  `no_simplification`, `fluency`, `repetition`, or `other`.
- `reviewer`: a stable reviewer identifier, not a display name if privacy matters.
- `reviewer_notes`: concise evidence for the decision.
- `reviewed_at`: populated automatically by the review CLI.

Use `acceptable` when the output is useful and preserves the requested contract,
even if it differs from the reference. Use `failure` when a learner should not see
the output without correction.

## Commands

```powershell
python -m src.quality.failure_review list --limit 20
python -m src.quality.failure_review review <candidate_id> `
  --verdict failure --category fluency --reviewer reviewer-1 `
  --notes "The output is incomplete and unnatural."
```

Re-running `build` preserves rows already marked `reviewed` by candidate ID.

## Model 4 readiness gate

Training remains blocked until both conditions are true:

- at least 100 reviewed candidates;
- at least 50 human-confirmed failures.

The queue currently contains source material derived from non-commercial corpora.
It is not cleared for commercial model training or deployment.
