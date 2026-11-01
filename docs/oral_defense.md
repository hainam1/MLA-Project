# Oral-defense preparation

## One-minute opening

The input is one ELLIPSE learner essay. Separate regressors estimate the rubric's Vocabulary and
Grammar scores from interpretable length, vocabulary, detected-grammar-issue, and syntax features.
Ridge and Random Forest are compared under one leakage-safe split. Their per-target absolute
prediction difference prioritizes teacher review; it is not confidence, an error probability, or a
replacement for human scoring.

## Questions to be ready to answer

1. How do the ELLIPSE rubric and score scale support separate regression targets?
2. Why are exact duplicates grouped before splitting?
3. Where are imputation and Ridge scaling fitted to prevent leakage?
4. Why is the same feature extractor used for training and new essays?
5. What do lexical richness and Zipf frequency capture, and where can they fail?
6. Why can LanguageTool matches be false positives for learner language?
7. How do Ridge and Random Forest inductive biases differ?
8. Why does Ridge need scaling while Random Forest does not?
9. Why is disagreement useful for triage but not a calibrated confidence score?
10. How does ceil(N * budget) select a review-first queue, with deterministic string-ID ties?
11. Which metrics describe score prediction and which describe review-queue utility?
12. Why must error analysis have human reference scores?
13. How might essay length, prompt, or demographic variables expose shortcuts or bias?
14. What evidence would be needed before deployment beyond this academic prototype?

## Before presenting

- [ ] Every result shown traces to a saved metric or prediction artifact.
- [ ] Split IDs, seed, feature schema, and hyperparameters are frozen.
- [ ] No demographic field is used as a predictor.
- [ ] Example errors contain no identifying information.
- [ ] Limitations and LLM assistance are disclosed.


## Final freeze interpretation

The system has two supervised regression targets implemented with independently trained single-target models. No test target labels or test evaluation metrics were used for model selection or hyperparameter tuning; test input text was processed by deterministic feature extraction before final evaluation. Official evaluation is complete.

Current evaluation primarily measures generalization to new essays under prompt categories represented during development, rather than generalization to completely unseen prompts. The operational 29-vs-44 terminology discrepancy remains explicitly unresolved; see [finalization evidence](finalization_evidence.md).

Disagreement produced the highest observed capture rate among the tested strategies, but the evidence was insufficient to establish statistical superiority over random selection (empirical one-sided p=.165). Large errors refer to the frozen RF predictor. Top-20% means review-first; remaining essays still require teacher grading and teachers retain 100% of official grading authority. Consensus remains auxiliary, without test-driven promotion.

The subgroup results are a descriptive subgroup performance audit, with small groups flagged, and do not establish fairness or causal effects. Aggregate labels reduce rater variance, so model-to-aggregate error is not directly comparable with human-to-human disagreement. The qualitative causes of the 97 shared blind spots have not been established. HANU use requires local validation/domain adaptation. Validation-only teacher heuristics and saved-prediction overlap are supplementary; see [evidence](finalization_evidence.md).
