# Final Results Summary

## Key numbers

- Official test: 2,571 essays total; 2,518 privacy-eligible.
- Frozen primary review budget: 20%, or 504 essays.
- Large errors at the 1.0-point threshold: 208 (8.26%).
- Random Forest official-test MAE: 0.364 Vocabulary and 0.434 Grammar, the lowest MAE for both
  traits.
- Disagreement: 47 errors captured; 22.596% Capture Rate; 9.325% Precision; 1.129 Lift.
- Ridge Extremity: 43 captured; 20.673% Capture Rate.
- Shortest-First: 37 captured; 17.789% Capture Rate.
- Random: mean 41.427 captured; mean 19.917% Capture Rate; empirical interval
  15.385%–25.012%.
- Shared blind spot: 97 low-disagreement large errors, equal to 46.63% of all 208 large errors.

## Research-question answers

**RQ1.** Both full-feature models improved on the mean-score and frozen length-only baselines in
official-test MAE. Random Forest retained the lowest MAE for Vocabulary and Grammar, although Ridge
was close and had slightly higher Vocabulary QWK.

**RQ2.** Disagreement had the highest frozen official-test point-estimate Capture Rate at the 20%
budget. Its 22.596% rate nevertheless remained inside the empirical random-selection interval, so
the evidence is **moderate/supportive**, not statistically established superiority.

**RQ3.** The main failure mode was shared error under low disagreement. Nearly half of all large
errors occurred when the models were relatively close, so model agreement does not imply
correctness or confidence.

**RQ4.** MAE, large-error prevalence, review selection, and within-group Capture Rate differed
descriptively across gender, race/ethnicity, and SES. These observed differences do not establish
causes, bias, or fairness. Official-test groups with N<20 were American Indian/Alaskan Native
(N=4), Two or more races/Other (N=10), and missing SES (N=1).

## Limitations

- ELLIPSE represents English learners in US Grades 8–12, not HANU students. HANU use would require
  local essays, local human ratings, and local validation.
- Aggregate labels and human-rater disagreement indicate label uncertainty; human–human and
  model–aggregate errors have different reference structures and are not a human-versus-model
  competition.
- No stable writer ID was available.
- Disagreement is not calibrated uncertainty, and two models can share blind spots.
- Fairness results are descriptive and include small groups.
- Random ranges are empirical selection intervals, not population-effect confidence intervals.
- Sensitivity results were mixed and the 1.5 threshold involved only 19 large errors.

## Final conclusions

On the frozen official test, Ridge–Random Forest disagreement achieved the highest point-estimate
Capture Rate among Random, Shortest-First, Ridge Extremity, and Disagreement. The improvement was
modest, remained inside the empirical random-selection reference interval, and nearly half of large
errors occurred under low model disagreement.

The appropriate use boundary is:

- **System:** Predict → Compare → Prioritize
- **Teacher:** Review → Interpret → Decide

No automated official grades, automatic proficiency classification, automatic placement, or
replacement of teacher judgment is supported. No direct generalization to HANU is established.
