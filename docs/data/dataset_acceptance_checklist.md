# Dataset Acceptance Checklist

Status: accepted for inventory and the frozen Phase 1 scope on 2026-09-23; training approval is
conditional on resolving the Phase 2 identifying-information finding.

- [x] Texts were written by English learners in grades 8–12.
- [x] Each retained essay was scored by two trained human raters.
- [x] `essay_id`, `essay_text`, `Vocabulary`, and `Grammar` map directly from ELLIPSE fields.
- [x] The official analytic and holistic scoring rubric is available at `data/01_original_source/documentation/ELL_Rubrics.docx`.
- [x] The observed range and valid values are documented: 1.0–5.0 in aggregate 0.5 increments.
- [x] The meaning of the integer rubric levels is documented in the official rubric.
- [x] Regression is accepted as an explicit approximate-continuity modeling assumption; equal
  proficiency distance between adjacent levels is not claimed.
- [x] Dataset size and score coverage are adequate for the planned low-dimensional feature set:
  3,911 official-train essays and 2,571 official-test essays.
- [x] Prompt and demographic metadata availability is recorded. No stable `learner_id` is available,
  so repeated learners cannot be grouped or quantified and remain a documented limitation.
- [x] The two final files contain 44 observed prompt values and no missing prompt.
- [x] Exact normalized-text and ID audit across both final files found 0 duplicate text groups and 0
  duplicate ID groups among 6,482 rows. Near-duplicate risk remains for later audit.
- [x] Official source, pinned commit, citation, license, retrieval date, file sizes, and checksums are
  recorded in `data/01_original_source/documentation/SOURCE.md`.
- [x] Dataset files are ignored by Git and submission must not redistribute raw learner text unless
  the CC BY-NC-SA terms and institutional rules are satisfied.
- [x] Privacy status is documented. The raw-rater file contains `Identifying_Info` flags; 138
  exactly linkable final rows are flagged by at least one rater. Free text requires protected
  handling and an exclusion/redaction decision before training or qualitative reporting.
- [x] Untouched local raw snapshots and SHA-256 checksums are retained.

## Candidate decision

| Candidate | Human learner text | Human score | Rubric | Group metadata | Size/coverage | License | Privacy | Decision |
|---|---|---|---|---|---|---|---|---|
| ELLIPSE v1.0 | Yes | Two trained raters; final aggregate scores | Official 1–5 holistic and analytic rubric | Prompt and demographics; no stable learner ID | 6,482 reliable final essays | CC BY-NC-SA 4.0 | Anonymized IDs; learner text remains sensitive | Accepted with documented limits |

## Acceptance conditions carried forward

1. Use only `Vocabulary` and `Grammar` as targets for the current project.
2. Do not use prompt, demographics, source-provided scores, or other target-derived columns as features.
3. Keep official test untouched until the frozen final evaluation.
4. Report the approximate-continuity assumption and the absence of a stable learner grouping key.
5. Audit near duplicates and cross-partition overlap before model fitting.
6. Resolve the Phase 2 identifying-information finding before feature extraction or training.
