# Risk Register

| Risk | Likelihood | Impact | Mitigation | Trigger / evidence | Status |
|---|---|---|---|---|---|
| Dataset target is ordinal and regression assumes approximate continuity | Medium | High | State the assumption; use MAE/RMSE without claiming equal proficiency intervals; discuss ordinal alternatives as a limitation | Phase 1 and dataset acceptance review | Mitigated; monitor |
| Learner, prompt, or duplicate leakage | High | High | Prefer grouped splits; freeze IDs; add overlap tests | Repeated authors/prompts/texts | Open |
| Parser errors on learner language | Medium | Medium | Manually inspect a sample; log failures; remove unreliable features before test use | Feature QA report | Open |
| Essay length becomes a shortcut | High | Medium | Compare Surface-only, Linguistic-only, and All conditions | Feature-condition experiment | Open |
| Restricted data or PII is committed | Medium | High | Ignore data contents; document license and anonymization; audit before submission | Data license/privacy review | Open |
| Identifying information may remain in learner text | Medium | High | Never publish raw examples; use raw-rater flags to define an approved exclusion/redaction policy before feature extraction | Phase 2 found 138 exactly linkable final rows flagged by either rater | Open; blocks training |
| Time or compute limits optional work | Medium | Low | Complete the core before generalization or ablation extensions | Milestone slippage | Open |
