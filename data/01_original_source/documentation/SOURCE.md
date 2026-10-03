# ELLIPSE Corpus Data Sources

- Source repository: https://github.com/scrosseye/ELLIPSE-Corpus
- Pinned source commit: `dc3b8f0b3b4332fc9f64302c4ccfc4ed582f4b43`
- Retrieved: 2026-09-21
- License: CC BY-NC-SA 4.0
- Citation:
  Crossley, S. A., Tian, Y., Baffour, P., Franklin, A., Kim, Y., Morris, W., Benner, B., Picou, A., & Boser, U. (2023).
  Measuring second language proficiency using the English Language Learner Insight, Proficiency and Skills Evaluation (ELLIPSE) Corpus.
  International Journal of Learner Corpus Research, 9 (2), 248-269.
  Preprint: https://zenodo.org/records/11217937

## Local files and checksums

| File | Bytes | SHA-256 | Purpose / Description |
|---|---:|---|---|
| `ELLIPSE_Final_github_train.csv` | 9,861,486 | `782344E99668A3FF508D7410C0EB6E36DA70F3B28F81C96E367F1CA04924B06C` | 3,911 reliable training essays with metadata, demographics, and 6 trait scores + Overall |
| `ELLIPSE_Final_github_test.csv` | 6,383,207 | `7E990C6392A9DF9554D15BDD22F0B568D19095CD6676AD39CB1EAA69C977ED7A` | 2,571 reliable test essays with ground truth scores and demographics |
| `ellipsis_raw_rater_scores_anon_all_essay.csv` | 21,768,627 | `6972B8A960FC9F1986046AACEF18792438BF90326EC55A89272932453E2F519B` | 8,890 unadjudicated raw essays with individual scores from 2 raters |
| `ELL_Rubrics.docx` | 17,420 | `0C0AC5DFA6AE89C9C99FFE483C13EA4A57E8152A1472797E1FE361C2C203EFDC` | Official English Proficiency Scoring Rubric (Holistic + 6 Analytic traits, 1.0 - 5.0) |
| `ELLIPSE_README.md` | 2,666 | `181FE4D9D6EBBCE4A64DE2A56F1A0AFC9DF19989E453DCF7F36DB55614DA0FED` | Upstream repository documentation |

> Note: Upstream source archives (`ELLIPSE_Final_github_test.zip` with password `ellipse_test` and `ellipsis_raw_rater_scores_anon_all_essay.zip` with password `ellipse_raw_data`) were extracted and removed after the original CSV source files were verified.

Treat all files in `data/01_original_source/` as read-only source snapshots and do not edit them in place.
