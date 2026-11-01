# Responsible use

This repository is an academic prototype for prioritizing human review. Predictions are reference
estimates and must not replace rubric-based teacher judgment, determine grades, or be presented as
complete measures of a learner's proficiency.

ELLIPSE demographic columns can expose subgroup performance differences and potential bias. They
must not be model features. Any subgroup analysis should use adequate sample sizes, report
uncertainty, and avoid deficit framing. Learner text must be handled according to dataset terms and
institutional privacy requirements.

The Phase 2 audit found `Identifying_Info` flags in the raw-rater source and 138 exactly linkable
final essays flagged by at least one rater. Raw learner text and qualitative examples must not be
published. Beginning with Phase 5, only rows whose frozen manifest status is `not_flagged` may be
used for fitting or evaluation. Rows marked `flagged_by_rater` or `unresolved_raw_id_link` remain in
the immutable manifest for auditability but are excluded before any learned preprocessing or model
fit. This conservative rule applies consistently to model-train, validation, and final test.

LanguageTool matches can include false positives, dialect variation, and stylistic suggestions.
Model disagreement can miss cases where both models make the same error. Therefore neither signal
is an error label, confidence value, or substitute for human review.


## Final freeze interpretation

The system has two supervised regression targets implemented with independently trained single-target models. No test target labels or test evaluation metrics were used for model selection or hyperparameter tuning; test input text was processed by deterministic feature extraction before final evaluation. Official evaluation is complete.

Current evaluation primarily measures generalization to new essays under prompt categories represented during development, rather than generalization to completely unseen prompts. The operational 29-vs-44 terminology discrepancy remains explicitly unresolved; see [finalization evidence](finalization_evidence.md).

Disagreement produced the highest observed capture rate among the tested strategies, but the evidence was insufficient to establish statistical superiority over random selection (empirical one-sided p=.165). Large errors refer to the frozen RF predictor. Top-20% means review-first; remaining essays still require teacher grading and teachers retain 100% of official grading authority. Consensus remains auxiliary, without test-driven promotion.

The subgroup results are a descriptive subgroup performance audit, with small groups flagged, and do not establish fairness or causal effects. Aggregate labels reduce rater variance, so model-to-aggregate error is not directly comparable with human-to-human disagreement. The qualitative causes of the 97 shared blind spots have not been established. HANU use requires local validation/domain adaptation. Validation-only teacher heuristics and saved-prediction overlap are supplementary; see [evidence](finalization_evidence.md).
