# Data Dictionary

The selected source is ELLIPSE. Original field names remain untouched in raw CSV files; loading
maps only identifiers and text into the canonical in-memory schema.

| Canonical field | Source field | Type | Required | Definition | Allowed values / range | Missing-value rule |
|---|---|---|---|---|---|---|
| `essay_id` | `text_id_kaggle` | string | Yes | Unique writing-sample identifier | Unique, non-empty | Reject row |
| `essay_text` | `full_text` | string | Yes | Original learner-written text | Non-empty | Reject row |
| `Vocabulary` | `Vocabulary` | numeric | Yes | Human analytic vocabulary score | 1.0–5.0 | Reject row |
| `Grammar` | `Grammar` | numeric | Yes | Human analytic grammar score | 1.0–5.0 | Reject row |
| `prompt_id` | `prompt` | string | Preferred | Writing prompt/task identifier | Dataset-defined | Document absence |
