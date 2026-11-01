# Future transformer experiment plan - not implemented

Post-midterm supplementary research plan only. Wait until transformers are covered in the course and implementation is explicitly authorized by the instructor.

Raw essay -> fine-tuned transformer -> independently assessed Vocabulary/Grammar predictions.

Scientific motivation: Ridge and RF share the same 14-dimensional representation; a raw-text transformer could provide a different error pattern. It is a hypothesis about representational diversity, not a promise of higher accuracy or calibrated uncertainty.

Compare Ridge-RF, Ridge-Transformer, RF-Transformer and a prespecified ensemble disagreement on development data, using the same fixed RF reference labels and equal review budgets. Prespecify aggregation and avoid broad search for favorable capture. Define licensing, compute budget and privacy handling before training. Use development CV for model selection; prefer canonical prompt groups if a crosswalk becomes available. The already-opened Official Test cannot become a new untouched confirmatory set; any later test analysis is post-hoc, or a new independently held-out dataset is needed.

Store models/results separately under `outputs/post_midterm/transformer/`. Keep all frozen baseline models, predictions and official results. No model, tokenizer, transformer training or new dependency was implemented for this plan.
