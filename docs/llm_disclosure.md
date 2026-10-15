# LLM Use Disclosure — Working Record

## Permitted supporting uses

- Project scoping, repository organization, and checklist preparation.
- Code review, debugging suggestions, and test-case suggestions.
- Editing documentation and presentation language.
- Explaining established metrics or implementation choices for study purposes.

## Prohibited uses

- Creating or changing human-score ground-truth labels.
- Replacing the required trained regression models with LLM-only scoring.
- Inventing, modifying, or interpreting experimental results without saved evidence.
- Sending restricted learner writing or personal information to an unauthorized service.

## Usage log

| Date | Tool/model | Purpose | Artifact affected | Human verification |
|---|---|---|---|---|
| 2026-09-20 | Codex | Align repository structure with the approved writing-score plan and task list | Repository scaffold, configuration, documentation, and tests | Project author to review before the next phase |

Add every material use before submission and describe how generated suggestions were independently
checked.

## Week 9

Reading notes for the fixed 32-essay sample were organised with support tools (an AI coding agent) following a two-pass protocol (pass 1 blind: prompt name and essay text only; pass 2: scores, predictions, errors and D revealed) and a 7-criterion rubric agreed before reading. The team re-read the essays and adopted these notes as its reading results; t4_reading_summary.csv is the text-free export. Support tools were also used to write analysis scripts and compute summary tables.

See the [text-free reading summary](../reports/week9/t4_reading_summary.csv) and [Week 9 evidence log](../reports/week9/RESULTS_week9.md). The full reading sheet stays private and gitignored.
