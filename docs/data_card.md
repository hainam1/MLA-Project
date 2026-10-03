# Data Card — English Learner Writing Scores (ELLIPSE Corpus)

> Status: Approved. Dataset accepted on 2026-09-21 from official upstream repository `scrosseye/ELLIPSE-Corpus`.

## Identity and provenance

| Item | Value |
|---|---|
| Dataset name/version | ELLIPSE Corpus (v1.0, 2023) |
| Official source URL | https://github.com/scrosseye/ELLIPSE-Corpus |
| Citation | Crossley et al. (2023), *Measuring second language proficiency using the ELLIPSE Corpus*, IJLCR 9(2): 248-269 |
| License / terms | CC BY-NC-SA 4.0 |
| Access date | 2026-09-21 |
| Raw snapshot checksum | `782344E99668A3FF508D7410C0EB6E36DA70F3B28F81C96E367F1CA04924B06C` (`ELLIPSE_Final_github_train.csv`) |
| Redistribution permitted | Yes, with Attribution, NonCommercial, ShareAlike |

## Population, unit, and target

- Unit of analysis: one English learner writing sample (grades 8–12).
- Author population and learning context: Adolescent English language learners in US schools, grades 8–12, across diverse economic and racial/ethnic backgrounds.
- Human-rating process: Each essay was independently scored by two trained human raters using
  analytic and holistic scoring rubrics. The final files provide aggregate/average scores for texts
  retained as reliable; the project does not label these scores as adjudicated without additional
  source evidence.
- Rubric and score interpretation: Official scoring rubric (`ELL_Rubrics.docx`) covering 1 Holistic trait (`Overall`) and 6 Analytic traits (`Cohesion`, `Syntax`, `Vocabulary`, `Phraseology`, `Grammar`, `Conventions`).
- Valid score range: 1.0 to 5.0 in 0.5 increments.
- Regression-validity decision: Accepted with a stated modeling assumption. Rubric levels are
  ordered, and the aggregate scores occur in 0.5 increments. The project treats them as
  approximately continuous regression targets for MAE/RMSE analysis, without claiming that every
  adjacent rubric level represents an equal proficiency distance.
- Important boundary: the target is a score for a specific writing sample, not automatically a comprehensive assessment of overall English language proficiency.

## Canonical schema mapping

Required fields are mapped to ELLIPSE columns as follows:
- `essay_id` $\leftarrow$ `text_id_kaggle`
- `essay_text` $\leftarrow$ `full_text`
- `Vocabulary` $\leftarrow$ `Vocabulary`
- `Grammar` $\leftarrow$ `Grammar`
- `prompt_id` $\leftarrow$ `prompt`
- Demographics available: `gender`, `grade`, `race_ethnicity`, `SES`

## Data quality and size

- Final reliable training set: 3,911 essays (`ELLIPSE_Final_github_train.csv`).
- Final reliable test set: 2,571 essays (`ELLIPSE_Final_github_test.csv`).
- Total reliable corpus: 6,482 essays.
- Raw unadjudicated corpus: 8,890 essays (`ellipsis_raw_rater_scores_anon_all_essay.csv`).
- Missing values: None in text or score columns in the final reliable sets.

## Intended and prohibited use

- Intended: Academic research into interpretable linguistic features, Vocabulary/Grammar score prediction, model disagreement, and teacher-review prioritization.
- Prohibited: High-stakes automated grading, consequential placement decisions, commercial exploitation without separate license, or claiming complete learner proficiency.

## Known limitations

- Writing samples are drawn from standardized school prompt tasks (independent essays) and may not generalize to technical, creative, or conversational writing.
- Rater variance exists; the final score is an aggregate/average of human ratings.
- The raw-rater file contains `Identifying_Info` flags. The Phase 2 audit found 138 exactly linkable
  final rows flagged by at least one rater; learner text therefore requires protected handling and
  a documented exclusion/redaction decision before training or qualitative reporting.
- No stable writer/learner identifier is available, so repeated-writer grouping cannot be verified.
- Fourteen final IDs cannot be joined exactly to raw-rater IDs because the raw file stores the
  corresponding identifiers in lossy scientific notation.
