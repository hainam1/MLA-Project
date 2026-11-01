# Nguồn: docs/data_card.md
SHA256 toàn file: 8738709e7fc556247a51190ebf2e1abe79690ba09423f79f4714881e223a5091

Trích chọn metadata/số liệu; không chứa bài luận.

1: # Data Card — English Learner Writing Scores (ELLIPSE Corpus)
2: 
3: > Status: Approved. Dataset accepted on 2026-09-21 from official upstream repository `scrosseye/ELLIPSE-Corpus`.
4: 
5: ## Identity and provenance
6: 
7: | Item | Value |
8: |---|---|
9: | Dataset name/version | ELLIPSE Corpus (v1.0, 2023) |
12: | License / terms | CC BY-NC-SA 4.0 |
15: | Redistribution permitted | Yes, with Attribution, NonCommercial, ShareAlike |
19: - Unit of analysis: one English learner writing sample (grades 8–12).
20: - Author population and learning context: Adolescent English language learners in US schools, grades 8–12, across diverse economic and racial/ethnic backgrounds.
22:   analytic and holistic scoring rubrics. The final files provide aggregate/average scores for texts
26: - Valid score range: 1.0 to 5.0 in 0.5 increments.
28:   ordered, and the aggregate scores occur in 0.5 increments. The project treats them as
29:   approximately continuous regression targets for MAE/RMSE analysis, without claiming that every
41: - Demographics available: `gender`, `grade`, `race_ethnicity`, `SES`
45: - Final reliable training set: 3,911 essays (`ELLIPSE_Final_github_train.csv`).
46: - Final reliable test set: 2,571 essays (`ELLIPSE_Final_github_test.csv`).
47: - Total reliable corpus: 6,482 essays.
59: - Rater variance exists; the final score is an aggregate/average of human ratings.
61:   final rows flagged by at least one rater; learner text therefore requires protected handling and
