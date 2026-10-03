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
10. How will the review threshold be selected without using the test set?
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
