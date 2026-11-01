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
the evidence is **limited/directional**, not statistically established superiority.

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


## Finalization interpretation and supplementary evidence (2026-10-03)

No test target labels or test evaluation metrics were used for model selection or hyperparameter tuning. The development source had 3911 essays (3128 model_train + 783 Validation), with a separate 2571-row Official Test; privacy filtering leaves 3050/762/2518.

Splitting was prompt-stratified across the prompt categories available in the dataset. Current evaluation primarily measures generalization to new essays under prompt categories represented during development, rather than generalization to completely unseen prompts. Operational prompt counts and the unresolved lecturer terminology discrepancy are documented separately in [finalization evidence](../docs/finalization_evidence.md); neither numerical count defines the study's generalization claim.

There are two supervised regression targets implemented with independently trained single-target models. Large error is exactly `max(abs(true_Vocabulary - RF_Vocabulary), abs(true_Grammar - RF_Grammar)) >= 1.0` for the frozen Random Forest reference predictor selected on Validation. Triage evaluation therefore measures detection of large errors of that RF predictor. Auxiliary consensus inference is not a new confirmed winning model; any test-performance comparison of consensus would be exploratory/post-hoc.

Disagreement produced the highest observed capture rate among the tested strategies, but the evidence was insufficient to establish statistical superiority over random selection. The empirical one-sided tail proportion from saved random draws is **p=.165**, not significant at alpha=.05.

Random alone is an insufficient practical comparator. Shortest-first is a transparent teacher-observable comparator in the frozen study. A grammar-error-rate-first rule specified before supplementary execution captured 11/69 Validation large errors at 153 selected (15.942%), versus 15/69 (21.739%) for shortest-first and frozen disagreement. This is **exploratory validation-only analysis added after teacher feedback**, outside Phase 9. No heuristic was tuned or evaluated anew on Official Test.

Saved-prediction supplementary overlap at Top-20% is 179/504 (35.516%), with Jaccard 0.215923. Of the 208 RF large errors, both rankings caught 18; disagreement alone caught 29, extremity alone 25, and neither 136. The two rankings provide partially different signals; these diagnostics do not prove independent superiority.

One possible explanation is that both models share the same feature representation, but the project has not yet established the qualitative causes of these shared blind spots. A text-free reproducible sample with blank manual notes is available for future qualitative review.

The preserved Gender, Race/Ethnicity and SES results constitute a **descriptive subgroup performance audit**; Grade is not covered by the frozen fairness table. Small subgroup estimates are unstable. Aggregate labels reduce rater variance, so model-to-aggregate error is not directly comparable with human-to-human disagreement.

Top-20% is review-first, and the remaining 80% are also teacher graded. Teachers retain 100% of official grading authority. HANU deployment requires local validation/domain adaptation. Historical proposals preserve original hypotheses; final results supersede their assumptions.
