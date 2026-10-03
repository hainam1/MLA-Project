# Final Report: Interpretable Essay-Score Prediction and Review Prioritization

## Abstract

This study examined whether interpretable linguistic features can support prediction of human
Vocabulary and Grammar scores and whether disagreement between Ridge Regression and Random Forest
Regression can prioritize essays with large prediction errors for human review. The analysis used
the ELLIPSE Corpus, which contains writing by English learners in US Grades 8–12. Models used a
frozen set of 14 length, lexical, detected-grammar, and syntactic features. The official test was
accessed once after the models and evaluation protocol were frozen; 2,518 of 2,571 test essays were
privacy-eligible.

Random Forest had the lowest official-test mean absolute error (MAE) for both Vocabulary (0.364)
and Grammar (0.434), improving on the corresponding mean-score and frozen length-only baselines.
At the frozen 20% review budget (504 essays), Ridge–Random Forest disagreement captured 47 of 208
large errors: a 22.596% Capture Rate, 9.325% Precision, and 1.129 Lift. This was the highest frozen
official-test point estimate among Random, Shortest-First, Ridge Extremity, and Disagreement, but
the improvement was modest and the Capture Rate remained inside the empirical random-selection
reference interval of 15.385%–25.012%. Moreover, 97 large-error essays had low model disagreement,
representing 46.63% of all 208 large errors. The evidence is therefore **moderate/supportive**, not
statistically established superiority. Disagreement can be treated only as an imperfect triage
signal: model agreement does not imply correctness or confidence.

Descriptive subgroup analysis found differences across gender, race/ethnicity, and socioeconomic
status (SES), but these results do not establish causes, bias, or fairness. The results also do not
establish direct validity for Hanoi University (HANU) students. Responsible use is limited to
supporting teacher review, with no automated official grades, proficiency classifications,
placement decisions, or replacement of teacher judgment.

## 1. Introduction

Automated essay-score prediction may help organize human review, but a useful regression model is
not necessarily reliable at identifying its own consequential errors. This project therefore
studied two related tasks: predicting two analytic writing scores and prioritizing essays for
review when two different model families disagree.

The system concept is deliberately limited:

- **System:** Predict → Compare → Prioritize
- **Teacher:** Review → Interpret → Decide

The project is an academic prototype, not an autonomous scoring system. Its outputs are reference
estimates and review rankings rather than official decisions.

## 2. Research questions

**RQ1.** How well do Ridge and Random Forest predict human Vocabulary and Grammar scores compared
with simple prediction baselines?

**RQ2.** At a fixed 20% review budget, does Ridge–RF disagreement identify more large prediction
errors than Random, Shortest-First, and Ridge Extremity?

**RQ3.** What failure modes remain, especially shared blind spots where both models agree but
predictions are substantially wrong?

**RQ4.** What subgroup performance differences are observed across gender, race/ethnicity, and
SES?

## 3. Dataset and study boundary

ELLIPSE v1.0 contains learner essays scored on a 1.0–5.0 grid in 0.5-point increments. The target
labels are aggregate human ratings for Vocabulary and Grammar. The source population is adolescent
English learners in US schools, Grades 8–12, writing standardized prompt-based essays. The unit of
analysis is an essay, not a comprehensive measure of a learner's English proficiency.

The official training file contained 3,911 essays. A frozen 80/20 development split produced 3,128
model-train rows and 783 validation rows before the privacy filter. Only rows marked `not_flagged`
were used from Phase 5 onward, leaving 3,050 model-train and 762 validation essays. The official
test contained 2,571 essays, of which 2,518 were privacy-eligible and evaluated. No stable writer
identifier was available, so separation by writer could not be verified.

## 4. Methods

### 4.1 Frozen features

The models used the following 14 features, in fixed order:

1. `word_count`
2. `sentence_count`
3. `mean_sentence_length`
4. `mtld`
5. `mattr`
6. `mean_word_frequency`
7. `mean_word_length`
8. `lexical_density`
9. `noun_diversity`
10. `detected_grammar_errors_per_100_words`
11. `detected_error_free_sentence_ratio`
12. `complex_sentence_ratio`
13. `estimated_clauses_per_sentence`
14. `subordinate_clause_ratio`

Prompt and demographic attributes were not model predictors. This design choice prevents their
direct use as inputs, but it does not by itself demonstrate fairness.

### 4.2 Models and baselines

Separate Ridge and Random Forest regressors were fitted for Vocabulary and Grammar. Model selection
within the development data minimized cross-validated MAE, and the chosen pipelines were fitted on
the 3,050 eligible model-train essays. Under the predeclared lower-validation-MAE rule, Random
Forest was the reference predictor for both traits.

The comparison conditions were:

- a mean-score baseline using the eligible training mean;
- frozen length-only Ridge and Random Forest models using only `word_count`, `sentence_count`, and
  `mean_sentence_length`; and
- the historical length-only consensus, the mean of the two length-model predictions.

The Phase 5 length estimators had not originally been serialized. Before official-test access they
were deterministically reconstructed from the 3,050 eligible model-train essays. Their validation
predictions and metrics matched the historical artifacts within the frozen tolerances, after which
the reconstructed estimators were hashed and frozen. No model was retrained during Phase 9.

### 4.3 Frozen evaluation protocol

For essay \(i\), the Random Forest large-error indicator was

\[
L_i=\mathbf 1\left[\max\left(
|\hat y^{RF}_{i,V}-y_{i,V}|,
|\hat y^{RF}_{i,G}-y_{i,G}|
\right)\ge 1.0\right].
\]

The primary review budget was 20%, with queue size \(K=\lceil 0.20N\rceil\). Sensitivity budgets
were 10% and 30%; sensitivity large-error thresholds were 0.5 and 1.5 points. The review strategies
were frozen as follows:

- **Random:** 1,000 uniform samples without replacement, using seed 42.
- **Shortest-First:** ascending recomputed word count.
- **Ridge Extremity:** descending maximum raw rubric-point distance of the two Ridge predictions
  from their respective medians on the 3,050 eligible model-train essays.
- **Ridge–RF Disagreement:** descending
  \(D_i=\max(|\hat y^{Ridge}_{i,V}-\hat y^{RF}_{i,V}|,
  |\hat y^{Ridge}_{i,G}-\hat y^{RF}_{i,G}|)\).

Deterministic ties used ascending string essay ID. With selected indicator \(S_i\), total large
errors \(M=\sum_i L_i\), and queue size \(K\):

\[
\text{Capture Rate}=\frac{\sum_iS_iL_i}{M},\qquad
\text{Precision}=\frac{\sum_iS_iL_i}{K},\qquad
\text{Lift}=\frac{\text{Precision}}{M/N}.
\]

For QWK only, continuous predictions were rounded half-up to the nearest 0.5, clipped to [1.0,
5.0], encoded on the fixed ordered ELLIPSE levels, and evaluated with quadratic-weighted Cohen
kappa. MAE, RMSE, and \(R^2\) used continuous predictions.

## 5. Results

### 5.1 Validation results

Validation results were used to select the reference predictors and then to freeze the review
protocol; they are reported separately from the one-time official-test results.

| Model | Trait | N | MAE | RMSE | R² |
|---|---|---:|---:|---:|---:|
| Ridge | Vocabulary | 762 | 0.374814 | 0.478538 | 0.304342 |
| Random Forest | Vocabulary | 762 | 0.372977 | 0.480023 | 0.300018 |
| Ridge | Grammar | 762 | 0.456298 | 0.560330 | 0.324042 |
| Random Forest | Grammar | 762 | 0.447710 | 0.554622 | 0.337743 |

At the primary threshold, validation contained 69 large errors among 762 essays (9.055%). At a 20%
budget, \(K=153\). Disagreement and Shortest-First each captured 15 errors (21.739%), Random
captured a mean of 13.946 (20.212%), and Ridge Extremity captured 10 (14.493%). Thus the validation
result was a tie between the two leading deterministic strategies, not evidence that disagreement
was uniquely best.

The validation error-quadrant analysis identified 36 low-disagreement large errors, equal to 52.17%
of the 69 validation large errors. This failure pattern was already present before the official test.

### 5.2 Official-test regression results — RQ1

The following table reports the one-time frozen official-test evaluation on all 2,518 eligible
essays. The length-only consensus is included for completeness, while RQ1 focuses on Ridge, Random
Forest, and the simple mean and length baselines.

| Model | Trait | MAE | RMSE | R² | QWK |
|---|---|---:|---:|---:|---:|
| Ridge | Vocabulary | 0.367881 | 0.467167 | 0.338246 | 0.484352 |
| Random Forest | Vocabulary | **0.364197** | **0.462448** | **0.351546** | 0.478500 |
| Mean-score baseline | Vocabulary | 0.471199 | 0.574540 | -0.000908 | 0.000000 |
| Length-only Ridge | Vocabulary | 0.430174 | 0.545681 | 0.097119 | 0.209612 |
| Length-only Random Forest | Vocabulary | 0.457027 | 0.578527 | -0.014846 | 0.210388 |
| Length-only consensus | Vocabulary | 0.432209 | 0.549125 | 0.085685 | 0.214684 |
| Ridge | Grammar | 0.443020 | 0.550719 | 0.328181 | 0.504522 |
| Random Forest | Grammar | **0.433587** | **0.537710** | **0.359545** | **0.505689** |
| Mean-score baseline | Grammar | 0.531507 | 0.672112 | -0.000632 | 0.000000 |
| Length-only Ridge | Grammar | 0.531556 | 0.661097 | 0.031896 | 0.043688 |
| Length-only Random Forest | Grammar | 0.585616 | 0.725139 | -0.164753 | 0.065648 |
| Length-only consensus | Grammar | 0.548777 | 0.676852 | -0.014796 | 0.075342 |

Random Forest retained the lowest MAE for both traits. Both full-feature models improved on the
mean and corresponding length-only baselines in MAE. The two model families performed similarly,
and metric ordering was not completely uniform: Ridge's Vocabulary QWK (0.484) was slightly above
Random Forest's (0.478), even though Random Forest had lower Vocabulary MAE. The evidence supports
the usefulness of the full feature set relative to simple prediction baselines, without implying
that the scores fully represent writing proficiency.

### 5.3 Official-test primary review comparison — RQ2

There were 208 large errors among 2,518 eligible test essays, a prevalence of 8.26%. Of these, 61
were Vocabulary-only, 126 Grammar-only, and 21 involved both traits. At the frozen 20% budget,
\(K=504\).

| Strategy | Selected | Captured | Capture Rate | Precision | Lift |
|---|---:|---:|---:|---:|---:|
| Random, mean of 1,000 draws | 504 | 41.427 | 19.917% | 8.220% | 0.995 |
| Shortest-First | 504 | 37 | 17.789% | 7.341% | 0.889 |
| Ridge Extremity | 504 | 43 | 20.673% | 8.532% | 1.033 |
| Ridge–RF Disagreement | 504 | **47** | **22.596%** | **9.325%** | **1.129** |

Disagreement had the highest frozen official-test point estimate. It captured four more errors than
Ridge Extremity, ten more than Shortest-First, and 5.573 more than the random mean. However, its
22.596% Capture Rate lies inside the empirical random-selection reference interval of
15.385%–25.012%. That interval describes the middle 95% of the 1,000 frozen random draws; it is not
a bootstrap confidence interval. The observed advantage is modest, and no inferential analysis
establishes superiority over random selection. The evidence for added prioritization value is
therefore **moderate/supportive**.

Validation and official-test results also differed in the relative ordering of the non-random
baselines: Shortest-First tied Disagreement on validation, whereas Ridge Extremity was second on
the official test. This variation reinforces the need to avoid conclusions based only on a single
point-estimate ordering.

### 5.4 Failure modes and shared blind spots — RQ3

The quadrant threshold was fixed before official-test access at the validation median disagreement,
\(D=0.133989655155\).

| Official-test quadrant | N | Population share | Mean D | Mean max RF error | Mean words |
|---|---:|---:|---:|---:|---:|
| High disagreement + Large error | 111 | 4.408% | 0.230810 | 1.203798 | 475.48 |
| High disagreement + No large error | 1,057 | 41.978% | 0.228007 | 0.487965 | 442.41 |
| Low disagreement + Large error | 97 | 3.852% | 0.082000 | 1.190247 | 427.77 |
| Low disagreement + No large error | 1,253 | 49.762% | 0.081223 | 0.482869 | 400.15 |

The 97 low-disagreement large-error essays were **46.63% of all 208 large-error cases**. These are
shared blind spots in the operational sense that the Ridge and Random Forest predictions were
relatively close while the Random Forest reference prediction was wrong by at least one point on
one or both traits. Their mean maximum RF error (1.190 points) was close to that of high-
disagreement large errors (1.204 points). Thus model agreement does not imply correctness or
confidence.

Other frozen diagnostics were also weak: Spearman correlations were 0.022 between disagreement and
actual maximum RF error, 0.107 between disagreement and Ridge extremity, and 0.045 between
disagreement and word count. These are descriptive associations, not causal evidence. The error
composition further shows that Grammar-only cases (126) were more common than Vocabulary-only
cases (61), with 21 cases large on both traits.

### 5.5 Predeclared sensitivity analyses

The primary result remains the 1.0-point threshold and 20% budget. The following are the complete
predeclared threshold-by-budget combinations, summarized as Capture Rate. They were not searched to
select a favorable setting.

| Error threshold | Budget | Large errors | Random mean | Shortest-First | Ridge Extremity | Disagreement |
|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | 10% | 1,275 | 10.012% | 10.902% | 7.451% | 10.510% |
| 0.5 | 20% | 1,275 | 20.025% | 19.137% | 17.882% | 20.549% |
| 0.5 | 30% | 1,275 | 30.050% | 29.255% | 29.176% | 30.980% |
| 1.0 | 10% | 208 | 9.973% | 10.577% | 7.692% | 11.058% |
| **1.0** | **20%** | **208** | **19.917%** | **17.789%** | **20.673%** | **22.596%** |
| 1.0 | 30% | 208 | 30.000% | 25.000% | 33.654% | 33.173% |
| 1.5 | 10% | 19 | 10.437% | 15.789% | 10.526% | 21.053% |
| 1.5 | 20% | 19 | 19.705% | 21.053% | 26.316% | 31.579% |
| 1.5 | 30% | 19 | 29.842% | 26.316% | 31.579% | 52.632% |

At the 0.5 threshold, Disagreement was close to the random mean across budgets and was not the
highest deterministic strategy at 10%. At the 1.0 threshold, it led at 10% and 20%, while Ridge
Extremity was slightly higher at 30%. The 1.5-threshold rates are based on only 19 large errors and
are consequently unstable; their larger differences should not be treated as a basis for changing
the primary protocol. Overall, the sensitivity results are mixed rather than uniformly favoring
one review strategy.

### 5.6 Descriptive fairness analysis — RQ4

The following results are descriptive official-test subgroup estimates. Random expected selection
was 20.016% for every group because sampling was uniform over the full eligible population.

| Attribute | Group | N | Vocab MAE | Grammar MAE | Large-error prevalence | Disagreement selected | Within-group capture | Shortest selected | N<20 |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| Gender | Female | 1,101 | 0.375846 | 0.446728 | 10.082% | 21.708% | 22.523% | 16.712% | No |
| Gender | Male | 1,417 | 0.355147 | 0.423376 | 6.845% | 18.701% | 22.680% | 22.583% | No |
| Race/ethnicity | American Indian/Alaskan Native | 4 | 0.281769 | 0.410734 | 0.000% | 25.000% | NA | 25.000% | **Yes** |
| Race/ethnicity | Asian/Pacific Islander | 301 | 0.365085 | 0.404708 | 6.977% | 19.601% | 19.048% | 13.953% | No |
| Race/ethnicity | Black/African American | 189 | 0.348331 | 0.441090 | 8.995% | 17.989% | 17.647% | 14.286% | No |
| Race/ethnicity | Hispanic/Latino | 1,832 | 0.367109 | 0.441348 | 8.624% | 20.142% | 22.785% | 21.943% | No |
| Race/ethnicity | Two or more races/Other | 10 | 0.325904 | 0.354038 | 10.000% | 0.000% | 0.000% | 10.000% | **Yes** |
| Race/ethnicity | White | 182 | 0.353810 | 0.400306 | 6.044% | 22.527% | 36.364% | 17.033% | No |
| SES | Economically disadvantaged | 1,764 | 0.359880 | 0.430447 | 7.880% | 20.125% | 21.583% | 20.408% | No |
| SES | Not economically disadvantaged | 753 | 0.374747 | 0.441018 | 9.163% | 19.788% | 24.638% | 19.124% | No |
| SES | Missing | 1 | 0.035389 | 0.376291 | 0.000% | 0.000% | NA | 0.000% | **Yes** |

Observed gender differences included higher MAE and large-error prevalence for female essays than
for male essays, while within-group Capture Rates were very similar. Across race/ethnicity, MAE,
large-error prevalence, selection rates, and Capture Rates varied; the White-group Capture Rate of
36.364%, for example, corresponds to only 11 large errors. SES differences were smaller in review
selection rate than in large-error prevalence and within-group capture. These patterns are subgroup
disparities or observed differences only. They do not establish cause, bias, or fairness.

Three official-test groups had fewer than 20 essays and must be treated as especially unstable:
American Indian/Alaskan Native (N=4), Two or more races/Other (N=10), and missing SES (N=1).
Validation showed additional instability and some different subgroup orderings; two validation
race/ethnicity groups also had N<20. Demographic exclusion from the predictors limits one direct
path of influence but does not prove equitable performance.

### 5.7 Human-rater context

The validation-only rater analysis reported human–human MAE of 0.416 for Vocabulary and 0.537 for
Grammar, with QWK of 0.502 and 0.514. Random Forest MAE against aggregate labels was 0.373 and
0.448, while mean model-to-individual-rater MAE was 0.457 and 0.556.

These quantities have different reference structures. Human–human MAE compares two individual
ratings; model–aggregate MAE compares a prediction with the released aggregate label; and
model–individual MAE compares a prediction with each individual rating. The results provide context
for label uncertainty and cannot support a human-versus-model competition.

## 6. Discussion by research question

### RQ1: Predictive performance

Both full-feature model families outperformed the simple mean and frozen length-only baselines in
official-test MAE. Random Forest retained the lowest MAE for both Vocabulary (0.364) and Grammar
(0.434), although the Ridge results were close and Ridge had slightly higher Vocabulary QWK. The
answer is therefore that the full interpretable feature set added predictive information beyond
essay length and a constant prediction, with modest differences between the two trained model
families.

### RQ2: Review prioritization

Yes at the level of the frozen official-test point estimates: Disagreement captured 47 large errors
(22.596%), compared with 43 for Ridge Extremity, 37 for Shortest-First, and a random mean of 41.427.
However, Disagreement's Capture Rate remained inside the random empirical interval. The result is
moderate/supportive evidence, not statistically established superiority.

### RQ3: Remaining failure modes

The main failure mode is shared error under low disagreement. Ninety-seven official-test essays,
46.63% of all large errors, fell into the low-disagreement large-error quadrant. Disagreement also
had almost no monotonic association with actual maximum RF error. Review triage based solely on
model disagreement will therefore miss many consequential errors.

### RQ4: Subgroup differences

MAE, large-error prevalence, review selection, and within-group capture differed descriptively
across gender, race/ethnicity, and SES. Several estimates were based on very small groups. These
results motivate cautious monitoring and better-powered local validation but do not establish
causes, bias, or fairness.

## 7. Limitations and external validity

The study has several important limitations:

- ELLIPSE contains standardized-prompt writing by English learners in US Grades 8–12. Findings do
  not directly generalize to HANU students, university writing, other genres, or other educational
  contexts.
- A local HANU deployment would require local essays, local human ratings, and local validation
  before any operational use.
- The released targets are aggregate human ratings. Rater disagreement shows label uncertainty,
  while the absence of independent adjudication limits claims about a uniquely correct score.
- No stable writer ID was available, so repeated-writer grouping could not be guaranteed.
- Detected grammar features can reflect tool errors, dialect variation, and stylistic suggestions.
- The subgroup audit is descriptive, lacks causal identification, and includes very small groups.
- The random intervals are empirical reference intervals for the frozen simulation, not confidence
  intervals for a population effect.
- Only two model families were compared. Their shared representations and training labels can
  produce shared blind spots.
- A 20% review queue still had 9.325% Precision: most selected essays were not large-error cases
  under the frozen definition, and most large errors were not captured.

## 8. Responsible use

The allowed workflow remains:

- **System:** Predict → Compare → Prioritize
- **Teacher:** Review → Interpret → Decide

The system must not assign automated official grades, automatically classify proficiency, make
automatic placement decisions, or replace teacher judgment. Predictions and disagreement rankings
should be presented with their documented limitations, including the fact that agreement is not a
confidence measure and disagreement is not a calibrated probability of error. Learner text and
demographic data must be handled under the dataset license, privacy controls, and institutional
requirements.

## 9. Conclusion

The frozen experiment supports two restrained conclusions. First, Ridge and Random Forest models
using 14 interpretable features predicted Vocabulary and Grammar more accurately in MAE than simple
mean and length-only baselines, with Random Forest recording the lowest MAE for both targets.
Second, Ridge–Random Forest disagreement achieved the highest official-test point-estimate Capture
Rate at a 20% review budget. The gain was modest, remained inside the empirical random-selection
reference interval, and coexisted with a substantial shared-blind-spot group: 97 essays, or 46.63%
of all large errors, had low disagreement.

Accordingly, disagreement may be useful as one limited prioritization signal, but it is neither
proof of uncertainty nor assurance that agreeing models are correct. The experiment supports
continued human-centered investigation, not autonomous scoring or direct deployment at HANU.

## 10. Source artifacts and verification record

This report was synthesized without rerunning model evaluation. A read-only audit verified every
reported number against the following frozen artifacts:

- Protocol and methods: [`evaluation_protocol_freeze.md`](../docs/evaluation_protocol_freeze.md),
  [`length_baseline_reconstruction_addendum.md`](../docs/length_baseline_reconstruction_addendum.md),
  [`methodology.md`](../docs/methodology.md),
  [`feature_specification.md`](../docs/feature_specification.md), and
  [`responsible_use.md`](../docs/responsible_use.md).
- Dataset and split provenance: [`data_card.md`](../docs/data_card.md), the upstream
  [`ELLIPSE_README.md`](../data/01_original_source/documentation/ELLIPSE_README.md),
  [`split_audit_summary.json`](../docs/data/phase3_tables/split_audit_summary.json),
  [`privacy_status_by_split.csv`](../docs/data/phase3_tables/privacy_status_by_split.csv), and
  [`phase5_audit_summary.json`](../docs/data/phase5_tables/phase5_audit_summary.json).
- Validation regression and baselines:
  [`regression_metrics.csv`](../docs/data/phase7_tables/regression_metrics.csv),
  [`baseline_comparisons.csv`](../docs/data/phase7_tables/baseline_comparisons.csv), and
  [`review_strategy_comparison.csv`](../docs/data/phase8_tables/review_strategy_comparison.csv).
- Validation error, fairness, and rater context:
  [`phase8_error_fairness_analysis.md`](../docs/phase8_error_fairness_analysis.md),
  [`error_quadrants.csv`](../docs/data/phase8_tables/error_quadrants.csv),
  [`fairness_audit.csv`](../docs/data/phase8_tables/fairness_audit.csv), and
  [`human_machine_reliability.csv`](../docs/data/improvement_tables/human_machine_reliability.csv).
- Official-test results: [`artifact_manifest.json`](../docs/data/phase9_tables/artifact_manifest.json),
  [`regression_metrics.csv`](../docs/data/phase9_tables/regression_metrics.csv),
  [`review_strategy_comparison.csv`](../docs/data/phase9_tables/review_strategy_comparison.csv),
  [`error_quadrants.csv`](../docs/data/phase9_tables/error_quadrants.csv),
  [`fairness_audit.csv`](../docs/data/phase9_tables/fairness_audit.csv),
  [`sensitivity_analysis.csv`](../docs/data/phase9_tables/sensitivity_analysis.csv), and
  [`validation_vs_test.csv`](../docs/data/phase9_tables/validation_vs_test.csv).

All Phase 9 output hashes listed in the artifact manifest matched the files during synthesis.
Population, error, quadrant, and subgroup totals also reconciled.

### Documentation consistency note

The data card says that 14 “final IDs” could not be linked to the raw-rater data but does not state
their split. The frozen split artifacts resolve this wording ambiguity: all 14 unresolved links are
in development data (10 model-train and 4 validation), while the official-test privacy counts are
53 `flagged_by_rater` and 2,518 `not_flagged`, with no unresolved official-test links. This does not
alter the official-test analysis. A second interpretive difference is that the Phase 9 narrative
used the category “supports added value of disagreement”; the present report constrains that label
to point-estimate evidence because the observed Capture Rate remains inside the random reference
interval.

One display-rounding inconsistency remains in the frozen reporting. The authoritative counts give
Shortest-First Capture Rate as \(37/208=17.7884615\%\), which rounds directly to 17.788% at three
decimal places. The frozen Phase 9 narrative and the required headline presentation show 17.789%
because the stored proportion was first displayed as 0.177885 and then converted to a percentage.
The report preserves the required 17.789% headline while disclosing the exact count-derived value;
no substantive result changes.

## References

Crossley, S. A., Tian, Y., Baffour, P., Franklin, A., Kim, Y., Morris, W., Benner, B., Picou, A.,
and Boser, U. (2023). Measuring second language proficiency using the English Language Learner
Insight, Proficiency and Skills Evaluation (ELLIPSE) Corpus. *International Journal of Learner
Corpus Research, 9*(2), 248–269.
