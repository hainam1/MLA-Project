# Frozen Specification of the 14 Features

> **Phase:** 4  
> **Frozen:** 2026-09-23  
> **Input:** one non-empty learner essay; prompt is not an input feature  
> **Output:** exactly 14 finite numeric values in the order below

## Shared preprocessing

The extractor normalizes Unicode with NFKC, collapses whitespace, and trims the result. It does not
spell-correct, grammar-correct, lowercase the stored essay, remove stop words, or use a prompt.
spaCy `en_core_web_sm` supplies tokenization, sentence boundaries, lemmas, POS tags, and dependency
parses. A **word** is operationally an alphabetic spaCy token (`token.is_alpha`); punctuation and
numeric-only tokens are excluded. This denominator is shared across all applicable features.

LanguageTool 6.6 runs locally with locale `en-US`. Only matches whose `ruleIssueType` is `grammar`
are counted. Spelling, typography, style, and other match types are excluded.

## Feature table

Let `W` be the alphabetic word-token sequence, `S` the spaCy sentence spans, `N` the noun/proper-noun
tokens, `C` the estimated clause heads, `U` the subordinate clause heads, and `G` LanguageTool
matches classified as grammar.

| # | Feature | Definition / formula | Empty or short-text policy |
|---:|---|---|---|
| 1 | `word_count` | `|W|` | Non-empty text may still yield 0 words; return 0 |
| 2 | `sentence_count` | `|S|` | Fail loudly if the NLP pipeline supplies no sentence boundaries |
| 3 | `mean_sentence_length` | `|W| / |S|` | 0 if the sentence contains no alphabetic token |
| 4 | `mtld` | Bidirectional Measure of Textual Lexical Diversity at TTR threshold 0.72, from `lexicalrichness` | Return 0 for fewer than 10 words or an undefined computation |
| 5 | `mattr` | Mean TTR over moving windows of `min(50, |W|)` | Return 0 for fewer than 2 words; for 2–49 words this equals whole-text TTR |
| 6 | `mean_word_frequency` | Mean English Zipf frequency of lowercased surface words from `wordfreq` | Return 0 when `W` is empty; unknown words contribute the library's 0 value |
| 7 | `mean_word_length` | Mean number of Unicode characters in lowercased surface words | Return 0 when `W` is empty |
| 8 | `lexical_density` | Count of `NOUN`, `PROPN`, `VERB`, `ADJ`, or `ADV` tokens divided by `|W|` | Return 0 when `W` is empty |
| 9 | `noun_diversity` | Unique casefolded noun/proper-noun lemmas divided by `|N|` | Return 0 when no noun is detected |
| 10 | `detected_grammar_errors_per_100_words` | `100 × |G| / max(|W|, 1)` | Uses denominator 1 if `W` is empty |
| 11 | `detected_error_free_sentence_ratio` | Sentences with no overlapping match in `G`, divided by `|S|` | Sentence overlap uses LanguageTool character offsets |
| 12 | `complex_sentence_ratio` | Sentences containing at least one estimated subordinate clause, divided by `|S|` | Return 0 when none is detected |
| 13 | `estimated_clauses_per_sentence` | `|C| / |S|` | Return 0 when no clause head is detected |
| 14 | `subordinate_clause_ratio` | `|U| / |C|` | Return 0 when no clause head is detected |

## Operational syntax rules

A clause head is a spaCy `VERB` or `AUX` token whose dependency is one of:

- main/coordinated: `ROOT`, `conj`;
- subordinate: `advcl`, `ccomp`, `xcomp`, `acl`, `relcl`, `csubj`, `csubjpass`.

These are reproducible parser-based estimates, not gold syntactic annotations. In particular,
`conj` can sometimes join verbs inside one predicate, while fragments or parser errors can miss a
clause. The tests include one simple sentence and one `advcl` sentence to freeze the intended
counting behavior.

## Interpretation limits

- Diversity and frequency do not establish that a word is precise, appropriate, or correct in
  context.
- Lexical density and noun diversity depend on automatic POS and lemma predictions.
- A complex sentence is not necessarily a correct or effective sentence.
- LanguageTool matches are **tool-detected issues**, not errors confirmed by a teacher or ELLIPSE
  rater. False positives and false negatives are expected, and dialect-sensitive behavior is
  possible.
- None of the 14 values is a human score, confidence, error probability, or complete measurement of
  Vocabulary or Grammar quality.

The two model targets remain the human-provided `Vocabulary` and `Grammar` scores. No target,
Overall score, other rubric score, demographic field, prompt, ID, privacy flag, or source-computed
feature is an input to these 14 computations.

## Privacy handling during Phase 4

The frozen manifest contains 138 rows marked by a rater as potentially identifying and 14 rows
whose raw-ID privacy linkage is unresolved. The user's Phase 4 request authorizes local feature
processing, but no policy has yet authorized those rows for model training. Therefore Phase 4
retains their numeric features to preserve the frozen split while exporting no essay text or
identifying fragment. Phase 5 subsequently resolved the gate by excluding every row not marked
`not_flagged` from fitting and evaluation while preserving the frozen manifest.
