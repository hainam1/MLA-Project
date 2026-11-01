# Finalization Changelog

Date: 2026-10-03. Scope: completion of the existing two-target project, with frozen experiments unchanged.

| Change | Why | Teacher feedback addressed | Scientific impact |
|---|---|---|---|
| `src/mla_project/pipelines/inference_pipeline.py`: threshold default None; explicit legacy reference behavior | Remove arbitrary production decision while retaining explicit callers | Budget review workflow | Predictions/features/models unchanged |
| Same file: `prioritize_essay_batch` with string-ID ties, ceil budget, zero/empty behavior and validation | Implement research queue at batch level | Budget review workflow | Matches frozen ranking convention |
| `tests/test_inference.py`: ranking, max-target score, budget, ties, determinism, bad inputs, empty/single, legacy/current contracts | Verify actual ranking logic | Technical reliability | No experimental changes |
| `configs/paths.yaml`: models -> outputs/phase6 | Correct latent/stale configuration inconsistency | Reproducibility | No previously crashing runtime bug claimed |
| `scripts/finalization_supplement.py` and `docs/data/finalization_tables/*` | Reproduce crosstabs, fixed Validation rules, saved-prediction overlap/p, manual sample | Prompt ambiguity, practical baseline, distinct rankings, blind spots | Exploratory/supplementary only; no model calls or retuning |
| `docs/finalization_evidence.md` | Explain operational strings vs canonical prompts, split coverage and quantitative supplement | Prompt/generalization and evidence depth | Unresolved mapping stated honestly |
| `data/DATA_DICTIONARY.md`, `docs/data/data_dictionary.md` | Explain renamed prompt string | Prompt terminology | Prevent canonical-ID claim |
| `docs/data/dataset_acceptance_checklist.md`, `docs/phase6_training_readiness.md` | Separate deterministic test-text processing from held-back test evaluation | Test-boundary accuracy | No leakage-free absolute or altered history |
| `README.md`, `docs/setup.md` | Current status, real usage, tested versions, Java/parser/cache and artifact setup | Reproducibility and communication | No unverified clean-machine claim |
| `docs/methodology.md`, `docs/responsible_use.md`, `docs/oral_defense.md` | RF error reference, p=.165, subgroup/rater/HANU limits and teacher authority | Statistical and responsible-use interpretation | No stronger scientific claim |
| `report/final_report.md`, `report/final_results_summary.md` | Synchronize restrained conclusions and supplementary evidence | All interpretation themes | Frozen result numbers unchanged |
| `docs/phase1_problem_definition.md`, `docs/decision_log.md` | Mark superseded proposal assumptions as historical | Provenance integrity | Original hypotheses preserved |
| `docs/instructor_requirements.md` | Correct stale three-model/feature-condition comparison | Scope consistency | Existing two-family protocol remains |
| `scripts/finalization_smoke.py` | Real frozen-model synthetic single/batch check | Technical reliability | No Official Test inference or training |
| `docs/project_freeze_status.md`, this changelog | Consolidate acceptance/evidence and weekly-report material | Project completion | No scope expansion |

## Verification

- Before edits: `.venv\Scripts\python.exe -m pytest` -> 72 passed.
- After implementation: `.venv\Scripts\python.exe -m pytest` -> 88 passed.
- `.venv\Scripts\python.exe scripts/finalization_smoke.py` -> four frozen models loaded, real spaCy/LanguageTool extraction, single schema and N=10/budget=.20/K=2 passed.
- `.venv\Scripts\python.exe scripts/finalization_supplement.py` -> both prompt crosstabs reproduced; Validation-only heuristic metrics; overlap 179, p=.165 and 97 blind spots; original Phase 9 output hashes verified.
- `.venv\Scripts\python.exe -m black --check src/mla_project/pipelines/inference_pipeline.py tests/test_inference.py scripts/finalization_supplement.py scripts/finalization_smoke.py` -> four files unchanged after formatting.
- `git diff --check` -> passed. Contextual `rg` search covered active .md/.py excluding .git, .venv, nested duplicate repository and node_modules. Residual matches are historical/negated claims, immutable source descriptions, or explicit legacy compatibility tests.
- Read-only SHA-256 comparison -> 44 protected local artifacts unchanged; original Phase 9 output/model hashes matched. No training or official metric-generation command was run.

No original untracked nested repository or scratch file was removed. Dependencies/Java/parser were inspected locally; no clean-machine installation was executed. The eight feedback themes in the freeze document are mapped from the supplied request, rather than invented verbatim teacher quotations.
