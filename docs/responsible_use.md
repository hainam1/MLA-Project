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
