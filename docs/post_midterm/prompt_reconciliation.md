# Prompt identity investigation: post-midterm supplementary research

Date checked: 2026-10-03. Status: authoritative sources checked; canonical mapping unresolved.

## Evidence in requested priority order

| Source | Direct finding | What it does not establish |
|---|---|---|
| Local original corpus metadata | Both final CSVs have a single `prompt` name field with 44 values; `task` has one value. No separate canonical ID/full-task mapping. | No relation mapping names to 29 canonical tasks |
| Supplied local/upstream README | Describes files and links the original publication; no canonical prompt inventory | No name-to-ID crosswalk |
| Canonical fields | `prompt_id` is a project rename of `prompt`; raw rater data has no prompt field | It is not an additional identifier |
| Raw released CSVs | All 44 names survive strip/casefold normalization; every category appears in development and Official Test metadata | Simple whitespace/case variants do not explain 44 vs 29 |
| Original publisher abstract | Explicitly describes 29 independent prompts | Does not list their IDs or reconcile the released categories |
| Author preprint, p.1 and p.5 | Describes 29 prompts | No crosswalk |
| Same preprint, section 2.1, p.9 | Initial corpus: 8890 essays, 44 prompts | Does not define a 44-to-29 collapse |
| Same preprint, section 2.2.1, p.15 and Figure 3, p.16 | Final corpus prompt mean size 147.318; chart shows released operational names. 6482/147.318 is approximately 44. | Does not resolve why abstract says 29 |

This is a specific inconsistency between the publication's summary and its detailed/released operational categories. It is NOT evidence that 29 canonical prompts have known variants. Neither an erratum nor a canonical crosswalk was found in the checked supplied documentation/publication. We do not invent one or declare which source count is the uniquely correct canonical count.

The lecturer's 29 statement is supported by the original publication. The project's 44 operational names are supported by direct CSV counts and the preprint's detailed distribution. Canonical identity remains unresolved, not merely the ability to count strings.

## Question prepared for lecturer

The original abstract says 29 prompts, while the released `prompt` field and detailed Figure 3 correspond to 44 categories. Could you identify the authoritative 29-prompt list/crosswalk, or confirm whether the released name categories should be treated as separate prompts for a supplementary grouped evaluation? Until then, the canonical unseen-prompt experiment is blocked; no substitute grouping is claimed to answer it.

## Sources and reproduction

- Original publisher: https://www.benjamins.com/catalog/ijlcr.22026.cro (DOI 10.1075/ijlcr.22026.cro).
- Author preprint record: https://zenodo.org/records/11217937 ; source PDF https://zenodo.org/records/11217937/files/ellipse_pre_print.pdf?download=1 .
- Original repository: https://github.com/scrosseye/ELLIPSE-Corpus ; local source snapshot pinned to dc3b8f0b3b4332fc9f64302c4ccfc4ed582f4b43.
- PDF downloaded separately to ignored `data/04_intermediate_work/post_midterm_sources/ellipse_pre_print.pdf`; Figure 3 was rendered and visually inspected. Original source files were not replaced.
- `docs/data/post_midterm/prompt_reconciliation_inventory.csv` lists operational categories/counts with canonical-ID fields blank. It is an unresolved inventory, NOT a mapping.
