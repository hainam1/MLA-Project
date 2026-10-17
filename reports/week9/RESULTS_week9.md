# Week 9 results

## Task 0 — PARTIAL: numerical reproduction complete; chronology unresolved

Disagreement is **not demonstrated better than random**. These are reproductions of the frozen primary evaluation, using saved predictions and fixed human target means; no models were fitted or predictions regenerated.

Producer: `scripts/week9/t0_provenance.py`.

Exact command from the repository root:

```text
.venv/Scripts/python.exe scripts/week9/t0_provenance.py --capture
```

The command launches the following command twice, each in a fresh Python process:

```text
.venv/Scripts/python.exe scripts/week9/t0_provenance.py
```

| Split | N | Large errors | Budget k | Shortest caught | Extremity caught | Disagreement caught | Random mean | Random percentile interval | Empirical tail | Exact hypergeometric p | Expected random caught |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|
| Validation | 762 | 69 | 153 | 15 | 10 | 15 | 13.946 | [8, 20] | 415/1000 = 0.415 | 0.40980554727071455 | 153*69/762 = 13.854330708661417 |
| Test | 2518 | 208 | 504 | 37 | 43 | 47 | 41.427 | [32, 52.02499999999998] | 165/1000 = 0.165 | 0.18832467136922115 | 504*208/2518 = 41.6330420969023 |

Validation row: [src: reports/week9/t0_metrics.csv row 1]. Test row: [src: reports/week9/t0_metrics.csv row 2]. Random reference intervals are the empirical 2.5th and 97.5th percentiles, using NumPy linear interpolation; they are not confidence intervals. [src: reports/week9/logs/t0_run1.log seed and RESULT lines; scripts/week9/t0_provenance.py percentile calculation]

Relevant **raw terminal output**, copied verbatim:

```text
seed=42; draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending
ARITHMETIC Validation: random_mean=13946/1000=13.946; empirical_p=415/1000=0.415; expected=153*69/762=13.8543307087; capture=15/69=0.217391304348; exact_p=hypergeom.sf(14,762,69,153)=0.409805547271
ARITHMETIC Test: random_mean=41427/1000=41.427; empirical_p=165/1000=0.165; expected=504*208/2518=41.6330420969; capture=47/208=0.225961538462; exact_p=hypergeom.sf(46,2518,208,504)=0.188324671369
INTEGRITY: all inventoried source files unchanged after reproduction.
```

[src: reports/week9/logs/t0_run1.log seed, ARITHMETIC and INTEGRITY lines]. Both raw runs and their combined output are saved under `reports/week9/logs/`. Each recomputed random draw was compared with its corresponding saved draw, and deterministic catches were compared with the saved strategy tables; a mismatch stops the script.

The reported Test random mean rounds as `41427/1000 = 41.427`, rounded to one decimal place `41.4`. [src: reports/week9/t0_metrics.csv row 2; reports/week9/logs/t0_run1.log ARITHMETIC Test line]

Repeat proof, copied verbatim:

```text
RUN1_SHA256=19df129db25042ddd6e6c47d02ed000ba97f0fe30b532ebea75912d22e40b3b4
RUN2_SHA256=19df129db25042ddd6e6c47d02ed000ba97f0fe30b532ebea75912d22e40b3b4
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t0.log final hash lines]

The artifact inventory, sizes, modification times, Git first/last history, hashes, full requested Git stat output, and exhaustive committed path list are linked from `t0_provenance.md`. Missing for complete provenance: independent evidence of first Test execution and defensible before/after classifications. The script reports this limitation verbatim:

```text
CHRONOLOGY: first Test evaluation date cannot be determined from available Git history; file mtimes are not execution timestamps.
STATUS: PARTIAL provenance chronology; numerical reproduction complete. Missing: independently established first Test execution date and before/after classification of changes.
```

[src: reports/week9/logs/t0_run1.log CHRONOLOGY and STATUS lines]

## Task 1

The Week 8 median statement is confirmed: `36/69 = 0.52173913043478259` large-error essays have D below `0.13398965515499994` (rounded `0.134`). [src: reports/week9/t1_quadrants.csv row 1; reports/week9/logs/t1_run1.log MEDIAN and WEEK8_CHECK lines]

Shared errors explain a limitation of disagreement: on the triggering target, `50/69 = 0.72463768115942029` have both models wrong in the same direction by at least one point. Agreement between the models can therefore coexist with a large error against the human mean. The remaining categories are `18/69 = 0.2608695652173913` same-direction errors with Ridge below threshold, and `1/69 = 0.014492753623188406` opposite-sign errors. [src: reports/week9/t1_categories.csv rows 1–3]

The signed-error Spearman correlations are `0.95627711721871844` for Vocabulary and `0.95185418999444549` for Grammar, whereas D versus RF error magnitude is `−0.0047812728275811421`; each uses `n=762`. These descriptive associations support the shared-error explanation without establishing a causal mechanism. [src: reports/week9/t1_correlations.csv rows 1, 3–4]

| Ranking score | AUROC | Bootstrap interval | Source |
|---|---:|---|---|
| D | 0.5106761193717716 | [0.43233628915262678, 0.58520847657981367] | [src: reports/week9/t1_auroc.csv row 1] |
| Frozen Ridge extremity | 0.51636447288621201 | [0.44597757375821473, 0.57889204277768336] | [src: reports/week9/t1_auroc.csv row 2] |
| −word_count | 0.51133488090009827 | [0.4379145899854337, 0.5826460972310793] | [src: reports/week9/t1_auroc.csv row 3] |

Each interval includes the no-discrimination value `0.5`. These are `95%` percentile intervals from the prescribed `2000` resamples. [src: reports/week9/t1_auroc.csv rows 1–3; reports/week9/logs/t1_run1.log METHOD AUROC line]

The score-band table shows overprediction at low reference scores and underprediction at high reference scores for both models and targets. It is consistent with predictions drawn toward the middle of the scale. D itself has little monotonic association with reference distance from the scale centre: Spearman rho `0.014761686811391577` for Vocabulary and `0.0060897865808967533` for Grammar, each `n=762`. [src: reports/week9/t1_bands.csv rows 1, 3–4, 6; reports/week9/t1_correlations.csv rows 5–6]

Output index: [essay-level records](t1_essay_level.csv), [quadrants](t1_quadrants.csv), [error categories](t1_categories.csv), [correlations](t1_correlations.csv), [AUROC](t1_auroc.csv), [score bands](t1_bands.csv), [shortlists](t1_shortlists.csv), [bootstrap replicates](t1_bootstrap.csv), [raw log](logs/t1.log). The shortlists contain no interpretation or human judgement.

Validation-only diagnostics under the frozen RF anchor. Disagreement remains not demonstrated better than random. The median split uses strictly below versus at-or-above; any exact median ties are printed. The triggering target with larger RF absolute error is used for categories; ties use Vocabulary. A zero Ridge error has its own explicit category rather than being assigned an invented sign. Shortlists contain no interpretation. Human reference values are the saved two-rater means, checked against the Validation clean table. The complete numeric summaries and their arithmetic follow as raw output; bootstrap replicates and essay-level records are preserved in CSV files. Source tags identify CSV data rows excluding headers.

Producer: `scripts/week9/t1_analysis.py`; shared calculations: `scripts/week9/validation_common.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t1_analysis.py --capture`; each child command: `.venv/Scripts/python.exe scripts/week9/t1_analysis.py`.

Raw terminal output (first fresh process), including explicit arithmetic and CSV filenames:

```text
COMMAND: .venv/Scripts/python.exe scripts/week9/t1_analysis.py
A1_ASSERT_PASS K=69; Disagreement=15; Shortest-first=15; Ridge Extremity=10; N=762; budget=153
SEED=42; bootstrap_resamples=2000; random_draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending; centers=(3.26941940240918, 3.124225726952784)
SAMPLE existing docs/data/error_analysis/manual_error_review.csv; 32 unique Validation IDs; membership only; no human judgement read or written
METHOD y_V/y_G are saved human two-rater means, reused without re-anchoring; equal to Validation clean-table targets. Both-trigger RF-error ties use V deterministically.
METHOD only allowlisted Validation predictions, development table, Validation clean table and existing Validation sample IDs are read; no Official Test file is opened.
MEDIAN D=0.13398965515499994; below means D < median; complement means D >= median; exact ties=0
CSV t1_quadrants.csv
large_error,D_group,D_median,count,row_total,fraction,arithmetic
True,below,0.13398965515499994,36,69,0.52173913043478259,36/69=0.52173913043478259
True,at_or_above,0.13398965515499994,33,69,0.47826086956521741,33/69=0.47826086956521741
False,below,0.13398965515499994,345,693,0.49783549783549785,345/693=0.49783549783549785
False,at_or_above,0.13398965515499994,348,693,0.50216450216450215,348/693=0.50216450216450215
WEEK8_CHECK below_median_large_errors=36/69; median rounded to 3 decimals=0.134
CSV t1_categories.csv
category,n,D_min,D_median,D_max,fraction,arithmetic
a_both_wrong_same_direction,50,0.0096960744499998697,0.11253391692000014,0.63717550656999977,0.72463768115942029,50/69=0.72463768115942029
b_same_direction_Ridge_below_threshold,18,0.075521092140000246,0.16660895791000008,0.56740913816999994,0.2608695652173913,18/69=0.2608695652173913
c_opposite_sign,1,1.3982103584150001,1.3982103584150001,1.3982103584150001,0.014492753623188406,1/69=0.014492753623188406
zero_Ridge_error,0,,,,0,0/69=0
CSV t1_correlations.csv
x,y,n,spearman_rho
D,RF_magnitude,762,-0.0047812728275811421
D,Ridge_magnitude,762,0.031764852706531795
e_RF_V,e_Ridge_V,762,0.95627711721871844
e_RF_G,e_Ridge_G,762,0.95185418999444549
D,distance_y_V,762,0.014761686811391577
D,distance_y_G,762,0.0060897865808967533
METHOD Spearman rho = Pearson correlation of average ranks, all Validation essays; no thresholding or subgroup selection.
CSV t1_auroc.csv
anchor,ranking,score,n,positives,negatives,auroc,ci_low,ci_high,bootstrap_resamples,valid_resamples,skipped_resamples,seed,u,auroc_arithmetic
A1,Disagreement,D,762,69,693,0.5106761193717716,0.43233628915262678,0.58520847657981367,2000,2000,0,42,24419,24419.0/(69*693)=0.5106761193717716
A1,Ridge Extremity,extremity,762,69,693,0.51636447288621201,0.44597757375821473,0.57889204277768336,2000,2000,0,42,24691,24691.0/(69*693)=0.51636447288621201
A1,Shortest-first,negative_word_count,762,69,693,0.51133488090009827,0.4379145899854337,0.5826460972310793,2000,2000,0,42,24450.5,24450.5/(69*693)=0.51133488090009827
METHOD AUROC=U/(n_positive*n_negative), ties receive half credit; paired ordinary essay bootstrap with replacement, 2000 draws from default_rng(42), percentile CI [2.5,97.5], NumPy linear interpolation; single-class replicates skipped and counted. Ranking scores unchanged.
CSV t1_bands.csv
target,band,n,target_large_errors,large_error_rate,rate_arithmetic,mean_D,mean_D_sum,mean_D_arithmetic,mean_signed_RF_error,mean_signed_RF_error_sum,mean_signed_RF_error_arithmetic,mean_signed_Ridge_error,mean_signed_Ridge_error_sum,mean_signed_Ridge_error_arithmetic
V,y<2.5,29,15,0.51724137931034486,15/29=0.51724137931034486,0.25395891545224136,7.3648085481149996,7.3648085481149996/29=0.25395891545224136,0.9930014122624139,28.797040955610004,28.797040955610004/29=0.9930014122624139,0.91632284054999991,26.573362375949998,26.573362375949998/29=0.91632284054999991
V,2.5<=y<=4.0,708,6,0.0084745762711864406,6/708=0.0084745762711864406,0.14649203206668079,103.71635870321001,103.71635870321001/708=0.14649203206668079,-0.0057274414490113027,-4.0550285459000026,-4.0550285459000026/708=-0.0057274414490113027,0.0020990845758757154,1.4861518797200066,1.4861518797200066/708=0.0020990845758757154
V,y>4.0,25,13,0.52000000000000002,13/25=0.52000000000000002,0.170069841216,4.2517460303999997,4.2517460303999997/25=0.170069841216,-0.97959325552919996,-24.489831388229998,-24.489831388229998/25=-0.97959325552919996,-0.99362835611320011,-24.840708902830002,-24.840708902830002/25=-0.99362835611320011
G,y<2.5,113,20,0.17699115044247787,20/113=0.17699115044247787,0.1716866558494248,19.400592110985002,19.400592110985002/113=0.1716866558494248,0.73086164548486732,82.587365939790004,82.587365939790004/113=0.73086164548486732,0.70778732727871696,79.979967982495012,79.979967982495012/113=0.70778732727871696
G,2.5<=y<=4.0,622,16,0.025723472668810289,16/622=0.025723472668810289,0.14723839674355307,91.582282774490011,91.582282774490011/622=0.14723839674355307,-0.11010688411853696,-68.48648192172999,-68.48648192172999/622=-0.11010688411853696,-0.092172741201720268,-57.331445027470004,-57.331445027470004/622=-0.092172741201720268
G,y>4.0,27,11,0.40740740740740738,11/27=0.40740740740740738,0.16111253319444443,4.3500383962499996,4.3500383962499996/27=0.16111253319444443,-0.9826855861914815,-26.53251082717,-26.53251082717/27=-0.9826855861914815,-1.0475573029648146,-28.284047180049996,-28.284047180049996/27=-1.0475573029648146
SHORTLISTS: t1_shortlists.csv data rows 1-10 large_error_lowest_D; 11-20 non_large_error_highest_D; no interpretation or human judgement added.
ESSAYS: t1_essay_level.csv contains every eligible Validation essay and computed target, signed-error, disagreement, trigger and selection fields.
CSV t1_sources.csv
path,sha256
outputs/phase6/validation_predictions.csv,6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
data/05_model_features/development_features_with_targets.csv,cafb1bca27423e0a8b6fb2d282fb7bd87fb703fc637a3a15778855caf0817a5b
data/03_clean_ready_to_use/validation_783.csv,7b80be5447dd8adadbecf6f492a4320f3e74c7290f91a99e11d43f5951a80e8e
docs/data/error_analysis/manual_error_review.csv,2bee7a27cc2654857f2ee345e8cfb987d74e15652b93edfce19b3d97dedf3113
CSV t1_output_hashes.csv
path,sha256
reports/week9/t1_auroc.csv,139a534d82fa527f7cd8fbf09d89a816f941ad72c24c776776235444db68f699
reports/week9/t1_bands.csv,dad5aa79753423e4d975db7687fd648034ae743f27b0f090fb6093a561ceaedb
reports/week9/t1_bootstrap.csv,4dd915bc3a0be23c9386162360f8d2ef1d70e9ddebfbbffd6bf383089a91a49c
reports/week9/t1_categories.csv,7c5f381e9d5fdd1502b0c5b7501bead769b460cbf2e8f9b46b1f21ac8059dfe0
reports/week9/t1_correlations.csv,dee066e5c292f7ec20b7e985ed17dd36c29b8e46b05ba95ecb27c2b2cdd1d8f9
reports/week9/t1_essay_level.csv,525c5fdaef3f36d40201d79fc75dc61629254c1f1513d0c38784d4abc892f966
reports/week9/t1_quadrants.csv,13e0290a64b1bb28d432df7d7709649a28d76b6660b637bdb4ece12ebd486b32
reports/week9/t1_shortlists.csv,3420ad7a6a2c880a63a4e6e14c9d102cacd60409da3821fb68e1f1ad85df51ce
reports/week9/t1_sources.csv,91c67a2690f0b7367cd4de92753718b1bd073c585928b15f0cb7350492295366
INTEGRITY: all allowlisted source hashes unchanged; existing sample untouched; no model fit/predict; Task 0 section preserved by append-only writer.
```

[src: reports/week9/logs/t1_run1.log; CSV data rows in each named CSV block, excluding its header]

Repeat proof:

```text
RUN1_SHA256=7aaf2f0611925efaa8695fdc4915b94d22965297a9f65c0a39b6b016d2ffcc79
RUN2_SHA256=7aaf2f0611925efaa8695fdc4915b94d22965297a9f65c0a39b6b016d2ffcc79
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t1.log final hash lines]

## Task 2

All anchors are reported; none is selected as preferable.

| Anchor | Positive essays K | Disagreement caught / K | Random mean caught | Disagreement exact p | Source |
|---|---:|---|---:|---:|---|
| A1 RF | 69 | 15/69 = 0.21739130434782608 | 13.946 | 0.40980554727071455 | [src: reports/week9/t2_anchor.csv rows 1–2] |
| A2 Ridge | 77 | 19/77 = 0.24675324675324675 | 15.556 | 0.1797140826453642 | [src: reports/week9/t2_anchor.csv rows 5–6] |
| A3 Both wrong | 51 | 9/51 = 0.17647058823529413 | 10.299 | 0.72893826141471885 | [src: reports/week9/t2_anchor.csv rows 9–10] |

The positive-set overlap is `|A1 ∩ A2| = 51`, `|A1 only| = 18`, `|A2 only| = 26`; the total checks are `51+18 = 69` and `51+26 = 77`. A3 requires both models to be wrong on an essay; their triggering targets may differ. [src: reports/week9/t2_overlap.csv row 1; reports/week9/logs/t2_run1.log METHOD all three anchors line]

All deterministic ranking AUROC intervals include `0.5` under every anchor; these sensitivity analyses do not establish better-than-random discrimination. [src: reports/week9/t2_auroc.csv rows 1–9]

Under A2, Ridge Extremity is scored against labels derived from Ridge itself (self-referential), mirroring the A1/Disagreement issue: RF is both the anchor and part of D. This dependence limits interpretation of anchor comparisons.

Output index: [all anchor × ranking metrics and arithmetic](t2_anchor.csv), [positive overlap](t2_overlap.csv), [all AUROC intervals](t2_auroc.csv), [individual random draws and exact p values](t2_random_draws.csv), [raw log](logs/t2.log). For Random, aggregate exact p is explicitly NA: a mean caught count is not an integer hypergeometric observation. Every actual random draw has its exact p in the draw table. The deterministic ranking signals receive bootstrap AUROC intervals; Random has no fixed ranking score.

Validation-only sensitivity to all predeclared anchors; no anchor is chosen. The A1 reproduction assertion runs before A2/A3 are computed. Under A2, Ridge Extremity is scored against labels derived from Ridge itself (self-referential), mirroring the A1/Disagreement issue: RF is both the anchor and part of D. Random results aggregate draws; exact p values are reported for each integer draw, with aggregate p marked NA because a mean caught count is not a hypergeometric observation. Random has no fixed score to bootstrap; the three deterministic ranking signals receive AUROC intervals. Complete raw summaries, explicit metric arithmetic and source CSV filenames follow.

Producer: `scripts/week9/t2_analysis.py`; shared calculations: `scripts/week9/validation_common.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t2_analysis.py --capture`; each child command: `.venv/Scripts/python.exe scripts/week9/t2_analysis.py`.

Raw terminal output (first fresh process), including explicit arithmetic and CSV filenames:

```text
COMMAND: .venv/Scripts/python.exe scripts/week9/t2_analysis.py
A1_ASSERT_PASS K=69; Disagreement=15; Shortest-first=15; Ridge Extremity=10; N=762; budget=153
SEED=42; bootstrap_resamples=2000; random_draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending; centers=(3.26941940240918, 3.124225726952784)
SAMPLE existing docs/data/error_analysis/manual_error_review.csv; 32 unique Validation IDs; membership only; no human judgement read or written
METHOD y_V/y_G are saved human two-rater means, reused without re-anchoring; equal to Validation clean-table targets. Both-trigger RF-error ties use V deterministically.
METHOD only allowlisted Validation predictions, development table, Validation clean table and existing Validation sample IDs are read; no Official Test file is opened.
CSV t2_overlap.csv
A1_intersection_A2,A1_only,A2_only,A1_total,A2_total
51,18,26,69,77
CSV t2_anchor.csv
anchor,ranking,N,K,k,caught,capture,precision,lift,exact_hypergeom_p,expected_random,capture_arithmetic,precision_arithmetic,lift_arithmetic,expected_arithmetic,p_expression,seed,random_draws,random_mean,random_p2_5,random_p97_5,random_mean_arithmetic
A1_RF,Random,762,69,153,13.946,0.2021159420289855,0.09115032679738562,1.0066166524580846,,13.854330708661417,13.946/69=0.2021159420289855,13.946/153=0.09115032679738562,(13.946/153)/(69/762)=1.0066166524580846,153*69/762=13.854330708661417,NA: Random caught is a noninteger mean; exact p is provided separately for every integer draw in t2_random_draws.csv,42,1000,13.946,8,20,13946/1000=13.946
A1_RF,Disagreement,762,69,153,15,0.21739130434782608,0.098039215686274508,1.0826939471440749,0.40980554727071455,13.854330708661417,15/69=0.21739130434782608,15/153=0.098039215686274508,(15/153)/(69/762)=1.0826939471440749,153*69/762=13.854330708661417,"hypergeom.sf(14,762,69,153)=0.40980554727071455",42,0,,,,
A1_RF,Ridge Extremity,762,69,153,10,0.14492753623188406,0.06535947712418301,0.72179596476271668,0.91931830033862283,13.854330708661417,10/69=0.14492753623188406,10/153=0.06535947712418301,(10/153)/(69/762)=0.72179596476271668,153*69/762=13.854330708661417,"hypergeom.sf(9,762,69,153)=0.91931830033862283",42,0,,,,
A1_RF,Shortest-first,762,69,153,15,0.21739130434782608,0.098039215686274508,1.0826939471440749,0.40980554727071455,13.854330708661417,15/69=0.21739130434782608,15/153=0.098039215686274508,(15/153)/(69/762)=1.0826939471440749,153*69/762=13.854330708661417,"hypergeom.sf(14,762,69,153)=0.40980554727071455",42,0,,,,
A2_Ridge,Random,762,77,153,15.555999999999999,0.20202597402597403,0.10167320261437908,1.0061685765215176,,15.460629921259843,15.556/77=0.20202597402597403,15.556/153=0.10167320261437908,(15.556/153)/(77/762)=1.0061685765215176,153*77/762=15.460629921259843,NA: Random caught is a noninteger mean; exact p is provided separately for every integer draw in t2_random_draws.csv,42,1000,15.555999999999999,9,22,15556/1000=15.555999999999999
A2_Ridge,Disagreement,762,77,153,19,0.24675324675324675,0.12418300653594772,1.2289279348102877,0.1797140826453642,15.460629921259843,19/77=0.24675324675324675,19/153=0.12418300653594772,(19/153)/(77/762)=1.2289279348102877,153*77/762=15.460629921259843,"hypergeom.sf(18,762,77,153)=0.1797140826453642",42,0,,,,
A2_Ridge,Ridge Extremity,762,77,153,6,0.07792207792207792,0.039215686274509803,0.38808250572956454,0.99948135275324623,15.460629921259843,6/77=0.07792207792207792,6/153=0.039215686274509803,(6/153)/(77/762)=0.38808250572956454,153*77/762=15.460629921259843,"hypergeom.sf(5,762,77,153)=0.99948135275324623",42,0,,,,
A2_Ridge,Shortest-first,762,77,153,15,0.19480519480519481,0.098039215686274508,0.97020626432391133,0.60474206287299836,15.460629921259843,15/77=0.19480519480519481,15/153=0.098039215686274508,(15/153)/(77/762)=0.97020626432391133,153*77/762=15.460629921259843,"hypergeom.sf(14,762,77,153)=0.60474206287299836",42,0,,,,
A3_Both_wrong,Random,762,51,153,10.298999999999999,0.20194117647058824,0.067313725490196069,1.005746251441753,,10.240157480314961,10.299/51=0.20194117647058824,10.299/153=0.067313725490196069,(10.299/153)/(51/762)=1.005746251441753,153*51/762=10.240157480314961,NA: Random caught is a noninteger mean; exact p is provided separately for every integer draw in t2_random_draws.csv,42,1000,10.298999999999999,5,16,10299/1000=10.298999999999999
A3_Both_wrong,Disagreement,762,51,153,9,0.17647058823529413,0.058823529411764705,0.87889273356401376,0.72893826141471885,10.240157480314961,9/51=0.17647058823529413,9/153=0.058823529411764705,(9/153)/(51/762)=0.87889273356401376,153*51/762=10.240157480314961,"hypergeom.sf(8,762,51,153)=0.72893826141471885",42,0,,,,
A3_Both_wrong,Ridge Extremity,762,51,153,4,0.078431372549019607,0.026143790849673203,0.39061899269511724,0.99633002456318109,10.240157480314961,4/51=0.078431372549019607,4/153=0.026143790849673203,(4/153)/(51/762)=0.39061899269511724,153*51/762=10.240157480314961,"hypergeom.sf(3,762,51,153)=0.99633002456318109",42,0,,,,
A3_Both_wrong,Shortest-first,762,51,153,12,0.23529411764705882,0.078431372549019607,1.1718569780853516,0.31552286295970838,10.240157480314961,12/51=0.23529411764705882,12/153=0.078431372549019607,(12/153)/(51/762)=1.1718569780853516,153*51/762=10.240157480314961,"hypergeom.sf(11,762,51,153)=0.31552286295970838",42,0,,,,
CSV t2_auroc.csv
anchor,ranking,score,n,positives,negatives,auroc,ci_low,ci_high,bootstrap_resamples,valid_resamples,skipped_resamples,seed,u,auroc_arithmetic
A1_RF,Disagreement,D,762,69,693,0.5106761193717716,0.43233628915262678,0.58520847657981367,2000,2000,0,42,24419,24419.0/(69*693)=0.5106761193717716
A1_RF,Ridge Extremity,extremity,762,69,693,0.51636447288621201,0.44597757375821473,0.57889204277768336,2000,2000,0,42,24691,24691.0/(69*693)=0.51636447288621201
A1_RF,Shortest-first,negative_word_count,762,69,693,0.51133488090009827,0.4379145899854337,0.5826460972310793,2000,2000,0,42,24450.5,24450.5/(69*693)=0.51133488090009827
A2_Ridge,Disagreement,D,762,77,685,0.52708313584225996,0.45437192402964638,0.59653318911402187,2000,2000,0,42,27801,27801.0/(77*685)=0.52708313584225996
A2_Ridge,Ridge Extremity,extremity,762,77,685,0.46085884918001707,0.39852780463546322,0.52256702640915065,2000,2000,0,42,24308,24308.0/(77*685)=0.46085884918001707
A2_Ridge,Shortest-first,negative_word_count,762,77,685,0.48659588586595887,0.41900813148545002,0.55555209669142713,2000,2000,0,42,25665.5,25665.5/(77*685)=0.48659588586595887
A3_Both_wrong,Disagreement,D,762,51,711,0.45023579051873913,0.35914516817379682,0.53642769497011256,2000,2000,0,42,16326,16326.0/(51*711)=0.45023579051873913
A3_Both_wrong,Ridge Extremity,extremity,762,51,711,0.48881718650892142,0.41501526773346525,0.55894764135339936,2000,2000,0,42,17725,17725.0/(51*711)=0.48881718650892142
A3_Both_wrong,Shortest-first,negative_word_count,762,51,711,0.51595377954275945,0.43561624860358267,0.59634314141002576,2000,2000,0,42,18709,18709.0/(51*711)=0.51595377954275945
METHOD all three anchors reported without choosing among them. A3 is essay-level A1 AND A2; targets may differ. Threshold=1.0; same queues and score order for every anchor.
METHOD Random has no fixed discriminative ranking score; its theoretical AUROC is 0.5, so no empirical bootstrap AUROC is assigned. AUROC CIs for the three fixed signals use paired ordinary essay bootstrap, 2000 resamples, seed=42, percentile [2.5,97.5] with linear interpolation. Undefined single-class replicates are skipped and counted.
METHOD Random caught/capture/precision/lift are means over 1000 selections. A noninteger mean is not a hypergeometric observation; no aggregate p is fabricated. Each actual random draw has an exact one-sided hypergeometric p in t2_random_draws.csv. Percentiles describe captured counts, not confidence intervals.
SELF_REFERENCE: Under A2, Ridge Extremity is scored against labels derived from Ridge itself (self-referential), mirroring the A1/Disagreement issue: RF is both the anchor and part of D. These anchor sensitivities do not select a preferred anchor or establish better-than-random generalisation.
CSV t2_sources.csv
path,sha256
outputs/phase6/validation_predictions.csv,6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
data/05_model_features/development_features_with_targets.csv,cafb1bca27423e0a8b6fb2d282fb7bd87fb703fc637a3a15778855caf0817a5b
data/03_clean_ready_to_use/validation_783.csv,7b80be5447dd8adadbecf6f492a4320f3e74c7290f91a99e11d43f5951a80e8e
docs/data/error_analysis/manual_error_review.csv,2bee7a27cc2654857f2ee345e8cfb987d74e15652b93edfce19b3d97dedf3113
CSV t2_output_hashes.csv
path,sha256
reports/week9/t2_A1_RF_bootstrap.csv,bafa066460b5140ccd2656907aeeafa0727b6d5b345952054fdacac9028ae407
reports/week9/t2_A2_Ridge_bootstrap.csv,c3b80b7a977bc36e47454daf85fe5b4314ef202f533ea568213988db3cb8f37b
reports/week9/t2_A3_Both_wrong_bootstrap.csv,e66b9d3fb727fda354878d033a48e9605a62efd471232fc2645c5f21ed690320
reports/week9/t2_anchor.csv,214754b96ba06badfe4a21611884a7e0f739edd0e4ccc268ac63f9a04288eae7
reports/week9/t2_auroc.csv,73c35e6414e22eb5602e90015cb1b0306dcccb2ee3049d8fa9d34e9657d3f3f8
reports/week9/t2_overlap.csv,790018f1bb03be6871e4019636d671004676f0431aeaa46f0bb1be8421709b71
reports/week9/t2_random_draws.csv,8bbc75fb42ae10afb35abbe443e85893bb0b7e358c8f61565b01a9ef91d1e5b8
reports/week9/t2_sources.csv,91c67a2690f0b7367cd4de92753718b1bd073c585928b15f0cb7350492295366
INTEGRITY: all allowlisted source hashes unchanged; existing sample untouched; no model fit/predict; Task 0 section preserved by append-only writer.
```

[src: reports/week9/logs/t2_run1.log; CSV data rows in each named CSV block, excluding its header]

Repeat proof:

```text
RUN1_SHA256=12deb7f051676b674aff5c48319382b71110191f994cd33f3e41a56929de1a42
RUN2_SHA256=12deb7f051676b674aff5c48319382b71110191f994cd33f3e41a56929de1a42
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t2.log final hash lines]

Additional artifact verification: producer `scripts/week9/verify_tasks12.py`, exact command `.venv/Scripts/python.exe scripts/week9/verify_tasks12.py --capture`. This independently checks AUROC against scikit-learn, reconstructs intervals from saved bootstrap replicates, verifies metric arithmetic and random-draw p values, and checks source/output hashes and existing sample membership. Raw terminal lines:

```text
PASS: Validation population, frozen capture gate, shortlists, existing sample membership and source/output hashes.
PASS: independent sklearn AUROC matches every Task 1/2 estimate; every bootstrap interval recomputed from saved replicates.
PASS: deterministic catches, all metric arithmetic, random means/percentiles and each random draw exact hypergeometric p.
PASS: both task raw outputs repeat identically; exactly one section per task. No Official Test files opened.
RUN1_SHA256=4c2c9517eb2a89b2b786a7106f6ac6cb9ac7f923ddcac940c84ec7382b6b2f00
RUN2_SHA256=4c2c9517eb2a89b2b786a7106f6ac6cb9ac7f923ddcac940c84ec7382b6b2f00
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t12_verification.log PASS and final hash lines]

## Task 3

**Exploratory extension designed after Official Test was used.**

**PARTIAL — stopped at the population gate, as instructed.** The supplied development feature table contains `3911` essays rather than the expected `3812`. Normalised prompt groups are `44`, matching the expected `44`. The split counts are `3128` model-train and `783` Validation; `3128+783 = 3911`. No population filtering or prompt merging was applied. [src: reports/week9/t3_preflight.csv row 1]

Producer: `scripts/week9/t3_preflight.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t3_preflight.py --capture`; each child command: `.venv/Scripts/python.exe scripts/week9/t3_preflight.py`. The preflight was repeated in a fresh process.

Raw terminal output:

```text
Exploratory extension designed after Official Test was used.
COMMAND: .venv/Scripts/python.exe scripts/week9/t3_preflight.py
SEED=42; population preflight only; no random sampling or training executed
CSV t3_preflight.csv
task_label,status,source,observed_essays,expected_essays,observed_prompt_groups,expected_prompt_groups,model_train_essays,validation_essays,normalisation,population_filter
Exploratory extension designed after Official Test was used.,PARTIAL_STOP_POPULATION_MISMATCH,data/05_model_features/development_features_with_targets.csv,3911,3812,44,44,3128,783,lowercase + whitespace collapse; no merging,none; source table as supplied
POPULATION observed_essays=3911; expected_essays=3812; observed_normalised_prompt_groups=44; expected_prompt_groups=44
METHOD prompts sourced from development-only clean train/Validation tables; normalisation=str.lower then whitespace split/join; no prompt merging or population filtering
CSV t3_sources.csv
task_label,path,sha256
Exploratory extension designed after Official Test was used.,data/05_model_features/development_features_with_targets.csv,cafb1bca27423e0a8b6fb2d282fb7bd87fb703fc637a3a15778855caf0817a5b
Exploratory extension designed after Official Test was used.,data/03_clean_ready_to_use/model_train_3128.csv,a56c0f3d195a3708f8ec74ca8dfabe125325050af14868a59ea571290658884e
Exploratory extension designed after Official Test was used.,data/03_clean_ready_to_use/validation_783.csv,7b80be5447dd8adadbecf6f492a4320f3e74c7290f91a99e11d43f5951a80e8e
INTEGRITY: all read source files unchanged; no Official Test or mixed-corpus/manifest file opened
STATUS: PARTIAL. STOP: supplied development essay count or prompt count differs from the requested population. No filtering, retraining, splits, held-out predictions, evaluation or bootstrap performed.
MISSING: Task 3 steps 2-7 and their requested fold, regression, ranking, AUROC, pooled and held-out prediction outputs. Population discrepancy requires clarification before proceeding.
```

[src: reports/week9/logs/t3_run1.log POPULATION, CSV, STATUS and MISSING lines; reports/week9/t3_preflight.csv row 1; reports/week9/t3_sources.csv rows 1–3]

Repeat proof:

```text
RUN1_SHA256=514cab06862d77a956888e810392b4c73db984f03eb1e8c9b96deb573dc5fbb3
RUN2_SHA256=514cab06862d77a956888e810392b4c73db984f03eb1e8c9b96deb573dc5fbb3
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t3.log initial preflight RUN1_SHA256 and RUN2_SHA256 lines]

Missing: steps 2–7, including both split designs, model retraining, fold composition, regression metrics, anchor/ranking metrics, AUROC intervals, pooled comparison and held-out predictions. Training determinism was not assessed because training was not run; only the preflight outputs are confirmed identical. The requested downstream CSVs were not created with empty or invented results. The earlier Task sections were preserved byte-for-byte by appending this section. No Official Test file was opened.

### Eligibility diagnosis (before training)

**Exploratory extension designed after Official Test was used.**

The earlier population stop counted the cleaned development table before the documented privacy gate. This diagnosis applies the existing `prepare_training_data(..., eligible_status="not_flagged")` function unchanged. Exact source lines and all counts are quoted in the raw transcript. The shared administrative manifest is used only to retain development-ID metadata; no Official Test feature, label, prediction or source file is opened. Training-ID evidence combines the saved frozen training-summary input hashes and refit declarations with exact saved training OOF ID/fold equality. No filter is invented or tuned. The decision gate must pass before training.

Producer: `scripts/week9/t3_eligibility.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t3_eligibility.py --capture`. Each fresh child: `.venv/Scripts/python.exe -u scripts/week9/t3_eligibility.py`. Environment: `PYTHONHASHSEED=42`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`.

[t3_eligibility_counts.csv](t3_eligibility_counts.csv):

```csv
task_label,split,source_essays,eligible_essays,excluded_essays,arithmetic
Exploratory extension designed after Official Test was used.,model_train,3128,3050,78,3128-78=3050
Exploratory extension designed after Official Test was used.,validation,783,762,21,783-21=762
Exploratory extension designed after Official Test was used.,TOTAL,3911,3812,99,3911-99=3812
```

[src: reports/week9/t3_eligibility_counts.csv data rows 1–3; reports/week9/logs/t3_eligibility_run1.log CSV t3_eligibility_counts.csv block]

[t3_eligibility_reasons.csv](t3_eligibility_reasons.csv):

```csv
task_label,split,privacy_review_status,eligible,n
Exploratory extension designed after Official Test was used.,model_train,flagged_by_rater,False,68
Exploratory extension designed after Official Test was used.,model_train,not_flagged,True,3050
Exploratory extension designed after Official Test was used.,model_train,unresolved_raw_id_link,False,10
Exploratory extension designed after Official Test was used.,validation,flagged_by_rater,False,17
Exploratory extension designed after Official Test was used.,validation,not_flagged,True,762
Exploratory extension designed after Official Test was used.,validation,unresolved_raw_id_link,False,4
```

[src: reports/week9/t3_eligibility_reasons.csv data rows 1–6; reports/week9/logs/t3_eligibility_run1.log CSV t3_eligibility_reasons.csv block]

[t3_eligibility_checks.csv](t3_eligibility_checks.csv):

```csv
task_label,check,source,eligible_n,saved_n,missing,extra,passed
Exploratory extension designed after Official Test was used.,eligible Validation ID equality,outputs/phase6/validation_predictions.csv,762,762,0,0,True
Exploratory extension designed after Official Test was used.,eligible Validation ID equality,reports/week9/t1_essay_level.csv,762,762,0,0,True
Exploratory extension designed after Official Test was used.,eligible train ID equality with saved OOF,outputs/improvement_study/train_oof_predictions.csv,3050,3050,0,0,True
```

[src: reports/week9/t3_eligibility_checks.csv data rows 1–3; reports/week9/logs/t3_eligibility_run1.log CSV t3_eligibility_checks.csv block]

Raw terminal output, first fresh process:

```text
Exploratory extension designed after Official Test was used.
COMMAND: .venv/Scripts/python.exe -u scripts/week9/t3_eligibility.py
SEED=42; diagnosis only; no fitting or sampling
CSV t3_eligibility_counts.csv
task_label,split,source_essays,eligible_essays,excluded_essays,arithmetic
Exploratory extension designed after Official Test was used.,model_train,3128,3050,78,3128-78=3050
Exploratory extension designed after Official Test was used.,validation,783,762,21,783-21=762
Exploratory extension designed after Official Test was used.,TOTAL,3911,3812,99,3911-99=3812
CSV t3_eligibility_reasons.csv
task_label,split,privacy_review_status,eligible,n
Exploratory extension designed after Official Test was used.,model_train,flagged_by_rater,False,68
Exploratory extension designed after Official Test was used.,model_train,not_flagged,True,3050
Exploratory extension designed after Official Test was used.,model_train,unresolved_raw_id_link,False,10
Exploratory extension designed after Official Test was used.,validation,flagged_by_rater,False,17
Exploratory extension designed after Official Test was used.,validation,not_flagged,True,762
Exploratory extension designed after Official Test was used.,validation,unresolved_raw_id_link,False,4
PROMPTS before=44; after=44; groups_losing_all_essays=0; lost_groups=[]
FROZEN_FIT_RECORD model=random_forest_grammar; eligible_fit_rows=3050; refit_on_all_eligible_rows=True
FROZEN_FIT_RECORD model=random_forest_vocabulary; eligible_fit_rows=3050; refit_on_all_eligible_rows=True
FROZEN_FIT_RECORD model=ridge_grammar; eligible_fit_rows=3050; refit_on_all_eligible_rows=True
FROZEN_FIT_RECORD model=ridge_vocabulary; eligible_fit_rows=3050; refit_on_all_eligible_rows=True
CSV t3_eligibility_checks.csv
task_label,check,source,eligible_n,saved_n,missing,extra,passed
Exploratory extension designed after Official Test was used.,eligible Validation ID equality,outputs/phase6/validation_predictions.csv,762,762,0,0,True
Exploratory extension designed after Official Test was used.,eligible Validation ID equality,reports/week9/t1_essay_level.csv,762,762,0,0,True
Exploratory extension designed after Official Test was used.,eligible train ID equality with saved OOF,outputs/improvement_study/train_oof_predictions.csv,3050,3050,0,0,True
CODE src/mla_project/pipelines/training_pipeline.py:72:     if eligible_status != "not_flagged":
CODE src/mla_project/pipelines/training_pipeline.py:73:         raise ValueError("The frozen privacy gate permits only not_flagged rows.")
CODE src/mla_project/pipelines/training_pipeline.py:101:     manifest_metadata = manifest[
CODE src/mla_project/pipelines/training_pipeline.py:102:         ["essay_id", "source_partition", "split", "cv_fold", "privacy_review_status"]
CODE src/mla_project/pipelines/training_pipeline.py:103:     ].rename(
CODE src/mla_project/pipelines/training_pipeline.py:104:         columns={
CODE src/mla_project/pipelines/training_pipeline.py:105:             "source_partition": "manifest_source_partition",
CODE src/mla_project/pipelines/training_pipeline.py:106:             "split": "manifest_split",
CODE src/mla_project/pipelines/training_pipeline.py:107:             "cv_fold": "manifest_cv_fold",
CODE src/mla_project/pipelines/training_pipeline.py:108:         }
CODE src/mla_project/pipelines/training_pipeline.py:109:     )
CODE src/mla_project/pipelines/training_pipeline.py:110:     merged = development.merge(manifest_metadata, on="essay_id", how="left", validate="one_to_one")
CODE src/mla_project/pipelines/training_pipeline.py:111:     if merged["privacy_review_status"].isna().any():
CODE src/mla_project/pipelines/training_pipeline.py:112:         raise ValueError("Every development essay must have a privacy status in the manifest.")
CODE src/mla_project/pipelines/training_pipeline.py:113:     metadata_matches = (
CODE src/mla_project/pipelines/training_pipeline.py:114:         _metadata_equal(merged["source_partition"], merged["manifest_source_partition"])
CODE src/mla_project/pipelines/training_pipeline.py:115:         and _metadata_equal(merged["split"], merged["manifest_split"])
CODE src/mla_project/pipelines/training_pipeline.py:116:         and _metadata_equal(merged["cv_fold"], merged["manifest_cv_fold"], numeric=True)
CODE src/mla_project/pipelines/training_pipeline.py:117:     )
CODE src/mla_project/pipelines/training_pipeline.py:118:     if not metadata_matches:
CODE src/mla_project/pipelines/training_pipeline.py:119:         raise ValueError("Development metadata does not match the frozen split manifest.")
CODE src/mla_project/pipelines/training_pipeline.py:127:     eligible = merged.loc[merged["privacy_review_status"].eq(eligible_status)].copy()
CODE src/mla_project/pipelines/training_pipeline.py:128:     eligible = eligible.drop(
CODE src/mla_project/pipelines/training_pipeline.py:129:         columns=["manifest_source_partition", "manifest_split", "manifest_cv_fold"]
CODE scripts/phase8_evaluate_review_prioritization.py:60: def _load_validation_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
CODE scripts/phase8_evaluate_review_prioritization.py:61:     development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
CODE scripts/phase8_evaluate_review_prioritization.py:62:     manifest = pd.read_csv(MANIFEST_PATH, dtype={"essay_id": "string"})
CODE scripts/phase8_evaluate_review_prioritization.py:63:     prepared = prepare_training_data(development, manifest, eligible_status="not_flagged")
CODE scripts/phase8_evaluate_review_prioritization.py:64:     if (
CODE scripts/phase8_evaluate_review_prioritization.py:65:         len(prepared.train) != EXPECTED_TRAIN_ROWS
CODE scripts/phase8_evaluate_review_prioritization.py:66:         or len(prepared.validation) != EXPECTED_VALIDATION_ROWS
CODE scripts/phase8_evaluate_review_prioritization.py:67:     ):
CODE scripts/phase8_evaluate_review_prioritization.py:68:         raise ValueError(
CODE scripts/phase8_evaluate_review_prioritization.py:69:             "Phase 8 population does not match the frozen 3,050/762 development split."
CODE scripts/phase8_evaluate_review_prioritization.py:85:         raise ValueError("Phase 6 validation predictions contain duplicate essay IDs.")
CODE scripts/phase8_evaluate_review_prioritization.py:86:     expected_ids = set(prepared.validation["essay_id"].astype(str))
CODE scripts/phase8_evaluate_review_prioritization.py:87:     if set(predictions["essay_id"].astype(str)) != expected_ids:
CODE scripts/phase8_evaluate_review_prioritization.py:88:         raise ValueError("Phase 6 predictions do not exactly match eligible validation IDs.")
CODE configs/phase6_training.yaml:1: privacy:
CODE configs/phase6_training.yaml:2:   eligible_status: not_flagged
CODE configs/phase6_training.yaml:3:   excluded_statuses: [flagged_by_rater, unresolved_raw_id_link]
CODE docs/evaluation_protocol_freeze.md:54: - Shortest-first: rank recomputed `word_count` ascending.
CODE docs/evaluation_protocol_freeze.md:55: - Ridge extremity: first compute the median of Ridge Vocabulary predictions and the median of
CODE docs/evaluation_protocol_freeze.md:56:   Ridge Grammar predictions over the 3,050 eligible model-train essays. For validation essay (i),
CODE docs/evaluation_protocol_freeze.md:57:   \[
CODE docs/evaluation_protocol_freeze.md:58:   E_i=\max\left(
CODE docs/evaluation_protocol_freeze.md:59:   |\hat y^{Ridge}_{i,V}-\operatorname{median}(\hat y^{Ridge}_{train,V})|,
CODE docs/evaluation_protocol_freeze.md:60:   |\hat y^{Ridge}_{i,G}-\operatorname{median}(\hat y^{Ridge}_{train,G})|
CODE docs/evaluation_protocol_freeze.md:61:   \right).
CODE docs/evaluation_protocol_freeze.md:62:   \]
CODE docs/evaluation_protocol_freeze.md:63:   Rank raw rubric-point distance descending; do not standardize the primary baseline.
CODE docs/evaluation_protocol_freeze.md:64: - Ridge-RF disagreement:
TRAIN_CROSSCHECK: saved training summary and development/manifest hashes identify the original fit population; all model records say refit on all eligible rows; saved train OOF IDs and cv_fold values match exactly. No separate per-model fit-ID list exists in the artifact manifest.
MANIFEST_ACCESS: shared administrative split metadata only, retained by development ID allowlist before prepare_training_data; no Official Test source, features, labels, predictions or evaluation outputs opened.
CSV t3_eligibility_sources.csv
task_label,path,sha256
Exploratory extension designed after Official Test was used.,data/05_model_features/development_features_with_targets.csv,cafb1bca27423e0a8b6fb2d282fb7bd87fb703fc637a3a15778855caf0817a5b
Exploratory extension designed after Official Test was used.,data/02_split_manifest/essay_split_manifest.csv,a998e6ed7edd1361de31739f4e3474a248a3eda7f705ee8e2a8eba36d396cc96
Exploratory extension designed after Official Test was used.,outputs/phase6/validation_predictions.csv,6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
Exploratory extension designed after Official Test was used.,outputs/phase6/training_summary.json,7183a8e76a3dc95bc51d7a0c9085069e2127cb93e1794ec513a4707dadac57d9
Exploratory extension designed after Official Test was used.,outputs/phase6/artifact_manifest.json,41b7a59e78636eb52c3e0ea3a0a5d9e91a399adaa93126ef366a5fbcdfd3ea25
Exploratory extension designed after Official Test was used.,outputs/improvement_study/train_oof_predictions.csv,69f7bb6ffcd4039071885f5f7ae028f962d9e4a3f0b0a73d67554d756892b313
Exploratory extension designed after Official Test was used.,reports/week9/t1_essay_level.csv,525c5fdaef3f36d40201d79fc75dc61629254c1f1513d0c38784d4abc892f966
Exploratory extension designed after Official Test was used.,src/mla_project/pipelines/training_pipeline.py,d6da02e3e66682914726c1aa016243c9781b2ad8f708f034cd0034a43b3e0134
Exploratory extension designed after Official Test was used.,scripts/phase8_evaluate_review_prioritization.py,9b29be681e19ab5c436c4d8dcd9fa5a09d38d60dbb36ebcde4a333ff23e3e563
Exploratory extension designed after Official Test was used.,configs/phase6_training.yaml,d0f844ba3e70ea7158eafce82bb5ee336d0886f9745f3da6f45f92c6c30812a5
Exploratory extension designed after Official Test was used.,docs/evaluation_protocol_freeze.md,48514edeedc14b2acd074b4abb85a69b74065c53fd1da654ab85afb87c521f28
OUTPUT_SHA256 t3_eligible_development.csv=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
OUTPUT_SHA256 t3_development_eligibility_ids.csv=75118d14de51a5b30edaf902cc1be0004a4e09534ac9ff45d6694dcb46ead366
OUTPUT_SHA256 t3_eligibility_prompts.csv=24eb2ebc94f8ab148195dc625ad6a698e57a73402f99884f5ff91e6a78a75643
OUTPUT_SHA256 t3_eligibility_code.csv=68fa40cf1fb308ceea82ebae9ef6cd28f93a50ee50355364c4637062bd6fcebd
DECISION: PASS. Documented unchanged not_flagged rule yields 3050 model_train + 762 Validation = 3812 eligible essays and 44 normalised prompt groups; exact Validation and saved OOF training ID equality asserted. Task 3 training is now authorised by the supplied decision rule.
INTEGRITY: all sources unchanged; diagnosis appended before any new training results.
```

[src: reports/week9/logs/t3_eligibility_run1.log exact quoted lines; every CSV block names its source file]

Fresh-process repeat proof:

```text
RUN1_SHA256=b250e34fa307cd834124ddd75d6bd468b4424531afd5480dc2672eedbaf56639
RUN2_SHA256=b250e34fa307cd834124ddd75d6bd468b4424531afd5480dc2672eedbaf56639
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t3_eligibility.log final hash lines]

### Eligible-development evaluation results

**Exploratory extension designed after Official Test was used.**

The diagnosis above passed before fitting. Both split designs use the identical documented eligible development population. All model factories and preprocessing come from the project; parameters are fixed and verified against the saved selected-parameter file. The table reports numbers only. Fold-level regression, labels, rankings, AUROC intervals and essay predictions are supplied in the linked CSVs. Pooled selection sums within-fold queues. Pooled expected counts sum fold expectations, pooled lift is caught divided by this expectation, and pooled p uses independent-fold joint random draws. Per-fold standalone random references reset the prescribed seed; the joint reference uses a separate master stream with that seed. Random aggregate p is NA, with actual per-fold integer-draw p values preserved. AUROC uses the exact three ranking scores; pooled AUROC uses concatenated raw scores and does not change queue selection. Identical fresh-process stdout includes hashes of every output, including all held-out predictions, confirming training-output determinism.

Producer: `scripts/week9/t3_evaluate.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t3_evaluate.py --capture`. Each fresh child: `.venv/Scripts/python.exe -u scripts/week9/t3_evaluate.py`. Environment: `PYTHONHASHSEED=42`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`.

[t3_summary.csv](t3_summary.csv):

```csv
task_label,split_type,anchor,n,K,budget_k,Disagreement_caught,expected_random,pooled_joint_random_p,Ridge_V_pooled_MAE,Ridge_V_MAE_arithmetic,Ridge_G_pooled_MAE,Ridge_G_MAE_arithmetic,RF_V_pooled_MAE,RF_V_MAE_arithmetic,RF_G_pooled_MAE,RF_G_MAE_arithmetic,caught_arithmetic,expected_arithmetic,p_arithmetic
Exploratory extension designed after Official Test was used.,prompt_disjoint,A1_RF,3812,386,764,88,77.362908429580997,0.105,0.37342443714543022,1423.4939543983801/3812=0.37342443714543022,0.46303653771248415,1765.0952817599896/3812=0.46303653771248415,0.37216506904049607,1418.6932431823709/3812=0.37216506904049607,0.45540371959591663,1735.9989790996342/3812=0.45540371959591663,15+22+20+17+14=88,14.618985695708712+17.645833333333332+15.078843626806833+15.199999999999999+14.819245773732119=77.362908429580997,105/1000=0.105
Exploratory extension designed after Official Test was used.,prompt_disjoint,A2_Ridge,3812,384,764,93,76.962119968393054,0.021999999999999999,0.37342443714543022,1423.4939543983801/3812=0.37342443714543022,0.46303653771248415,1765.0952817599896/3812=0.46303653771248415,0.37216506904049607,1418.6932431823709/3812=0.37216506904049607,0.45540371959591663,1735.9989790996342/3812=0.45540371959591663,20+24+18+15+16=93,13.617685305591678+18.447916666666668+14.877792378449408+15.6+14.418725617685306=76.962119968393054,22/1000=0.021999999999999999
Exploratory extension designed after Official Test was used.,prompt_disjoint,A3_Both_wrong,3812,276,764,44,55.321856877023137,0.96999999999999997,0.37342443714543022,1423.4939543983801/3812=0.37342443714543022,0.46303653771248415,1765.0952817599896/3812=0.46303653771248415,0.37216506904049607,1418.6932431823709/3812=0.37216506904049607,0.45540371959591663,1735.9989790996342/3812=0.45540371959591663,10+12+9+7+6=44,10.413524057217165+14.236979166666666+11.258869908015768+9.8000000000000007+9.6124837451235372=55.321856877023137,970/1000=0.96999999999999997
Exploratory extension designed after Official Test was used.,ordinary_KFold,A1_RF,3812,376,765,86,75.454484473844445,0.086999999999999994,0.37230494010695886,1419.2264316877272/3812=0.37230494010695886,0.46147110095779442,1759.1278368511123/3812=0.46147110095779442,0.37166317701951734,1416.7800307984/3812=0.37166317701951734,0.45439074799896872,1732.1375313720687/3812=0.45439074799896872,22+19+17+17+11=86,14.638269986893841+17.044560943643514+15.661417322834646+14.858267716535433+13.251968503937007=75.454484473844445,87/1000=0.086999999999999994
Exploratory extension designed after Official Test was used.,ordinary_KFold,A2_Ridge,3812,383,765,93,76.860785750405057,0.012999999999999999,0.37230494010695886,1419.2264316877272/3812=0.37230494010695886,0.46147110095779442,1759.1278368511123/3812=0.46147110095779442,0.37166317701951734,1416.7800307984/3812=0.37166317701951734,0.45439074799896872,1732.1375313720687/3812=0.45439074799896872,18+24+17+20+14=93,14.036697247706423+17.044560943643514+15.661417322834646+16.464566929133859+13.653543307086615=76.860785750405057,13/1000=0.012999999999999999
Exploratory extension designed after Official Test was used.,ordinary_KFold,A3_Both_wrong,3812,271,765,40,54.384438757081966,0.99299999999999999,0.37230494010695886,1419.2264316877272/3812=0.37230494010695886,0.46147110095779442,1759.1278368511123/3812=0.46147110095779442,0.37166317701951734,1416.7800307984/3812=0.37166317701951734,0.45439074799896872,1732.1375313720687/3812=0.45439074799896872,7+11+8+8+6=40,9.6251638269986888+12.432503276539974+11.244094488188976+11.244094488188976+9.8385826771653537=54.384438757081966,993/1000=0.99299999999999999
```

[src: reports/week9/t3_summary.csv data rows 1–6; reports/week9/logs/t3_training_run1.log CSV t3_summary.csv block]

Raw terminal output, first fresh process:

```text
Exploratory extension designed after Official Test was used.
COMMAND: .venv/Scripts/python.exe -u scripts/week9/t3_evaluate.py
VERSIONS Python=3.14.5; numpy=2.4.6; pandas=2.3.3; scipy=1.18.1; sklearn=1.9.1
SEEDS RF=42; ordinary_KFold=42; per-fold_random=42; joint_random=42; bootstrap=42; PYTHONHASHSEED=42; n_jobs=1; numeric threadpools=1
POPULATION eligible_model_train=3050; eligible_Validation=762; total=3812; normalised_prompt_groups=44; both designs use identical essay_id string ascending order
BUDGET_RULE k=ceil(0.20*n), as frozen; centres=median of fold-trained Ridge predictions on fold training essays, separately per target; no held-out values used for centres
PREPROCESSING project build_ridge: median imputation -> StandardScaler -> Ridge; project build_random_forest: median imputation -> RF; each pipeline is fitted on fold training rows only; no search
POOLING selections are made within folds and summed, never re-ranked across folds; pooled expected=sum(k_f*K_f/n_f); pooled lift=caught/pooled expected; pooled p from independent-fold joint draws
BOOTSTRAP ordinary essay resampling with replacement, 2000 resamples, default_rng(42) reset per scope, paired across anchors/signals; percentile CI with linear interpolation; single-class resamples skipped and counted; pooled AUROC uses concatenated raw scores, without changing within-fold selections
FOLD split=prompt_disjoint; fold=1; train_essays=3043; heldout_essays=769; train_prompts=35; heldout_prompts=9; overlapping_prompts=0; disjoint=True; k=ceil(0.20*769)=154
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="curfews for teenagers"; heldout_essays=54; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="distance learning"; heldout_essays=280; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="enjoyable educational activities"; heldout_essays=57; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="honesty"; heldout_essays=29; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="individuality"; heldout_essays=143; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="influences of character"; heldout_essays=90; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="learning from the experience of others"; heldout_essays=30; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="letter to employer"; heldout_essays=44; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=1; prompt="mandatory extracurricular activities"; heldout_essays=42; train_essays=0
CENTRES split=prompt_disjoint; fold=1; median_ridge_vocabulary=3.2672207073754627; median_ridge_grammar=3.1233889507514099; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=prompt_disjoint; fold=1; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=prompt_disjoint; fold=2; train_essays=3044; heldout_essays=768; train_prompts=35; heldout_prompts=9; overlapping_prompts=0; disjoint=True; k=ceil(0.20*768)=154
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="career commitment"; heldout_essays=222; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="creative arts requirement"; heldout_essays=51; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="future accomplishments"; heldout_essays=33; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="influencing behavior"; heldout_essays=62; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="places to visit"; heldout_essays=42; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="setting our aim"; heldout_essays=26; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="spending time outdoors"; heldout_essays=54; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="three-year high school program"; heldout_essays=147; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=2; prompt="working with a group or alone"; heldout_essays=131; train_essays=0
CENTRES split=prompt_disjoint; fold=2; median_ridge_vocabulary=3.2493237823471053; median_ridge_grammar=3.0892602479782738; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=prompt_disjoint; fold=2; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=prompt_disjoint; fold=3; train_essays=3051; heldout_essays=761; train_prompts=35; heldout_prompts=9; overlapping_prompts=0; disjoint=True; k=ceil(0.20*761)=153
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="benefits of a problem"; heldout_essays=33; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="cell phones at school"; heldout_essays=43; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="controlling extracurricular involvement"; heldout_essays=52; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="extended school day"; heldout_essays=88; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="internships and shadowing"; heldout_essays=55; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="lunch menus"; heldout_essays=92; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="success and failure"; heldout_essays=212; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="summer projects"; heldout_essays=19; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=3; prompt="trying something beyond what you have mastered"; heldout_essays=167; train_essays=0
CENTRES split=prompt_disjoint; fold=3; median_ridge_vocabulary=3.2778394390403531; median_ridge_grammar=3.1282922657786227; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=prompt_disjoint; fold=3; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=prompt_disjoint; fold=4; train_essays=3067; heldout_essays=745; train_prompts=36; heldout_prompts=8; overlapping_prompts=0; disjoint=True; k=ceil(0.20*745)=149
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="being busy"; heldout_essays=204; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="cell phones in classrooms"; heldout_essays=59; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="first impressions"; heldout_essays=168; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="grades for extracurricular activities"; heldout_essays=37; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="imagination"; heldout_essays=55; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="seeking multiple opinions"; heldout_essays=50; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="self-reliance"; heldout_essays=130; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=4; prompt="talents and skills"; heldout_essays=42; train_essays=0
CENTRES split=prompt_disjoint; fold=4; median_ridge_vocabulary=3.2729898308645557; median_ridge_grammar=3.1183359900379122; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=prompt_disjoint; fold=4; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=prompt_disjoint; fold=5; train_essays=3043; heldout_essays=769; train_prompts=35; heldout_prompts=9; overlapping_prompts=0; disjoint=True; k=ceil(0.20*769)=154
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="afterschool homework club"; heldout_essays=54; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="benefits of a good attitude"; heldout_essays=30; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="community service"; heldout_essays=43; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="four-day work week"; heldout_essays=134; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="impact of technology"; heldout_essays=174; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="lessons with elementary school students"; heldout_essays=38; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="positive attitudes"; heldout_essays=175; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="praising student work"; heldout_essays=56; train_essays=0
HELDOUT_PROMPT split=prompt_disjoint; fold=5; prompt="year-round school"; heldout_essays=65; train_essays=0
CENTRES split=prompt_disjoint; fold=5; median_ridge_vocabulary=3.2657763527471189; median_ridge_grammar=3.1215692827876667; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=prompt_disjoint; fold=5; training_predictions_rankings_and_bootstrap_finished=True
SPLIT_COMPLETE split=prompt_disjoint; pooled_n=3812; no_cross_fold_queue_reranking=True
FOLD split=ordinary_KFold; fold=1; train_essays=3049; heldout_essays=763; train_prompts=44; heldout_prompts=44; overlapping_prompts=44; disjoint=False; k=ceil(0.20*763)=153
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="afterschool homework club"; heldout_essays=10; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="being busy"; heldout_essays=44; train_essays=160
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="benefits of a good attitude"; heldout_essays=3; train_essays=27
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="benefits of a problem"; heldout_essays=11; train_essays=22
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="career commitment"; heldout_essays=52; train_essays=170
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="cell phones at school"; heldout_essays=10; train_essays=33
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="cell phones in classrooms"; heldout_essays=11; train_essays=48
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="community service"; heldout_essays=11; train_essays=32
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="controlling extracurricular involvement"; heldout_essays=7; train_essays=45
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="creative arts requirement"; heldout_essays=13; train_essays=38
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="curfews for teenagers"; heldout_essays=10; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="distance learning"; heldout_essays=41; train_essays=239
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="enjoyable educational activities"; heldout_essays=11; train_essays=46
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="extended school day"; heldout_essays=17; train_essays=71
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="first impressions"; heldout_essays=29; train_essays=139
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="four-day work week"; heldout_essays=23; train_essays=111
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="future accomplishments"; heldout_essays=6; train_essays=27
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="grades for extracurricular activities"; heldout_essays=5; train_essays=32
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="honesty"; heldout_essays=6; train_essays=23
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="imagination"; heldout_essays=13; train_essays=42
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="impact of technology"; heldout_essays=29; train_essays=145
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="individuality"; heldout_essays=31; train_essays=112
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="influences of character"; heldout_essays=22; train_essays=68
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="influencing behavior"; heldout_essays=16; train_essays=46
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="internships and shadowing"; heldout_essays=13; train_essays=42
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="learning from the experience of others"; heldout_essays=3; train_essays=27
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="lessons with elementary school students"; heldout_essays=12; train_essays=26
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="letter to employer"; heldout_essays=6; train_essays=38
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="lunch menus"; heldout_essays=20; train_essays=72
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="mandatory extracurricular activities"; heldout_essays=9; train_essays=33
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="places to visit"; heldout_essays=9; train_essays=33
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="positive attitudes"; heldout_essays=39; train_essays=136
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="praising student work"; heldout_essays=11; train_essays=45
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="seeking multiple opinions"; heldout_essays=11; train_essays=39
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="self-reliance"; heldout_essays=22; train_essays=108
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="setting our aim"; heldout_essays=6; train_essays=20
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="spending time outdoors"; heldout_essays=15; train_essays=39
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="success and failure"; heldout_essays=40; train_essays=172
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="summer projects"; heldout_essays=1; train_essays=18
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="talents and skills"; heldout_essays=9; train_essays=33
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="three-year high school program"; heldout_essays=31; train_essays=116
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="trying something beyond what you have mastered"; heldout_essays=29; train_essays=138
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="working with a group or alone"; heldout_essays=25; train_essays=106
HELDOUT_PROMPT split=ordinary_KFold; fold=1; prompt="year-round school"; heldout_essays=21; train_essays=44
CENTRES split=ordinary_KFold; fold=1; median_ridge_vocabulary=3.254934831968701; median_ridge_grammar=3.1006562731813578; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=ordinary_KFold; fold=1; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=ordinary_KFold; fold=2; train_essays=3049; heldout_essays=763; train_prompts=44; heldout_prompts=44; overlapping_prompts=44; disjoint=False; k=ceil(0.20*763)=153
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="afterschool homework club"; heldout_essays=8; train_essays=46
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="being busy"; heldout_essays=40; train_essays=164
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="benefits of a good attitude"; heldout_essays=9; train_essays=21
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="benefits of a problem"; heldout_essays=7; train_essays=26
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="career commitment"; heldout_essays=47; train_essays=175
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="cell phones at school"; heldout_essays=8; train_essays=35
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="cell phones in classrooms"; heldout_essays=15; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="community service"; heldout_essays=6; train_essays=37
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="controlling extracurricular involvement"; heldout_essays=10; train_essays=42
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="creative arts requirement"; heldout_essays=9; train_essays=42
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="curfews for teenagers"; heldout_essays=15; train_essays=39
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="distance learning"; heldout_essays=55; train_essays=225
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="enjoyable educational activities"; heldout_essays=10; train_essays=47
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="extended school day"; heldout_essays=14; train_essays=74
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="first impressions"; heldout_essays=37; train_essays=131
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="four-day work week"; heldout_essays=27; train_essays=107
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="future accomplishments"; heldout_essays=3; train_essays=30
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="grades for extracurricular activities"; heldout_essays=10; train_essays=27
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="honesty"; heldout_essays=9; train_essays=20
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="imagination"; heldout_essays=4; train_essays=51
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="impact of technology"; heldout_essays=46; train_essays=128
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="individuality"; heldout_essays=27; train_essays=116
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="influences of character"; heldout_essays=15; train_essays=75
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="influencing behavior"; heldout_essays=11; train_essays=51
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="internships and shadowing"; heldout_essays=7; train_essays=48
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="learning from the experience of others"; heldout_essays=10; train_essays=20
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="lessons with elementary school students"; heldout_essays=7; train_essays=31
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="letter to employer"; heldout_essays=6; train_essays=38
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="lunch menus"; heldout_essays=22; train_essays=70
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="mandatory extracurricular activities"; heldout_essays=10; train_essays=32
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="places to visit"; heldout_essays=8; train_essays=34
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="positive attitudes"; heldout_essays=33; train_essays=142
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="praising student work"; heldout_essays=17; train_essays=39
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="seeking multiple opinions"; heldout_essays=10; train_essays=40
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="self-reliance"; heldout_essays=33; train_essays=97
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="setting our aim"; heldout_essays=8; train_essays=18
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="spending time outdoors"; heldout_essays=10; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="success and failure"; heldout_essays=42; train_essays=170
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="summer projects"; heldout_essays=7; train_essays=12
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="talents and skills"; heldout_essays=8; train_essays=34
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="three-year high school program"; heldout_essays=27; train_essays=120
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="trying something beyond what you have mastered"; heldout_essays=34; train_essays=133
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="working with a group or alone"; heldout_essays=13; train_essays=118
HELDOUT_PROMPT split=ordinary_KFold; fold=2; prompt="year-round school"; heldout_essays=9; train_essays=56
CENTRES split=ordinary_KFold; fold=2; median_ridge_vocabulary=3.2707725136726014; median_ridge_grammar=3.1262122558573657; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=ordinary_KFold; fold=2; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=ordinary_KFold; fold=3; train_essays=3050; heldout_essays=762; train_prompts=44; heldout_prompts=44; overlapping_prompts=44; disjoint=False; k=ceil(0.20*762)=153
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="afterschool homework club"; heldout_essays=10; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="being busy"; heldout_essays=37; train_essays=167
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="benefits of a good attitude"; heldout_essays=9; train_essays=21
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="benefits of a problem"; heldout_essays=8; train_essays=25
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="career commitment"; heldout_essays=45; train_essays=177
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="cell phones at school"; heldout_essays=14; train_essays=29
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="cell phones in classrooms"; heldout_essays=9; train_essays=50
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="community service"; heldout_essays=6; train_essays=37
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="controlling extracurricular involvement"; heldout_essays=15; train_essays=37
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="creative arts requirement"; heldout_essays=8; train_essays=43
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="curfews for teenagers"; heldout_essays=10; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="distance learning"; heldout_essays=60; train_essays=220
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="enjoyable educational activities"; heldout_essays=5; train_essays=52
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="extended school day"; heldout_essays=15; train_essays=73
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="first impressions"; heldout_essays=43; train_essays=125
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="four-day work week"; heldout_essays=24; train_essays=110
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="future accomplishments"; heldout_essays=9; train_essays=24
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="grades for extracurricular activities"; heldout_essays=10; train_essays=27
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="honesty"; heldout_essays=5; train_essays=24
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="imagination"; heldout_essays=13; train_essays=42
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="impact of technology"; heldout_essays=29; train_essays=145
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="individuality"; heldout_essays=33; train_essays=110
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="influences of character"; heldout_essays=14; train_essays=76
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="influencing behavior"; heldout_essays=12; train_essays=50
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="internships and shadowing"; heldout_essays=11; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="learning from the experience of others"; heldout_essays=2; train_essays=28
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="lessons with elementary school students"; heldout_essays=7; train_essays=31
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="letter to employer"; heldout_essays=11; train_essays=33
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="lunch menus"; heldout_essays=21; train_essays=71
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="mandatory extracurricular activities"; heldout_essays=8; train_essays=34
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="places to visit"; heldout_essays=11; train_essays=31
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="positive attitudes"; heldout_essays=38; train_essays=137
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="praising student work"; heldout_essays=8; train_essays=48
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="seeking multiple opinions"; heldout_essays=10; train_essays=40
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="self-reliance"; heldout_essays=24; train_essays=106
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="setting our aim"; heldout_essays=3; train_essays=23
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="spending time outdoors"; heldout_essays=10; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="success and failure"; heldout_essays=50; train_essays=162
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="summer projects"; heldout_essays=3; train_essays=16
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="talents and skills"; heldout_essays=5; train_essays=37
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="three-year high school program"; heldout_essays=33; train_essays=114
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="trying something beyond what you have mastered"; heldout_essays=27; train_essays=140
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="working with a group or alone"; heldout_essays=31; train_essays=100
HELDOUT_PROMPT split=ordinary_KFold; fold=3; prompt="year-round school"; heldout_essays=6; train_essays=59
CENTRES split=ordinary_KFold; fold=3; median_ridge_vocabulary=3.2737772070142324; median_ridge_grammar=3.1260329409470682; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=ordinary_KFold; fold=3; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=ordinary_KFold; fold=4; train_essays=3050; heldout_essays=762; train_prompts=44; heldout_prompts=44; overlapping_prompts=44; disjoint=False; k=ceil(0.20*762)=153
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="afterschool homework club"; heldout_essays=8; train_essays=46
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="being busy"; heldout_essays=39; train_essays=165
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="benefits of a good attitude"; heldout_essays=5; train_essays=25
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="benefits of a problem"; heldout_essays=3; train_essays=30
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="career commitment"; heldout_essays=35; train_essays=187
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="cell phones at school"; heldout_essays=6; train_essays=37
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="cell phones in classrooms"; heldout_essays=10; train_essays=49
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="community service"; heldout_essays=9; train_essays=34
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="controlling extracurricular involvement"; heldout_essays=8; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="creative arts requirement"; heldout_essays=8; train_essays=43
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="curfews for teenagers"; heldout_essays=12; train_essays=42
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="distance learning"; heldout_essays=68; train_essays=212
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="enjoyable educational activities"; heldout_essays=14; train_essays=43
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="extended school day"; heldout_essays=16; train_essays=72
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="first impressions"; heldout_essays=26; train_essays=142
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="four-day work week"; heldout_essays=30; train_essays=104
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="future accomplishments"; heldout_essays=7; train_essays=26
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="grades for extracurricular activities"; heldout_essays=7; train_essays=30
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="honesty"; heldout_essays=3; train_essays=26
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="imagination"; heldout_essays=11; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="impact of technology"; heldout_essays=39; train_essays=135
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="individuality"; heldout_essays=27; train_essays=116
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="influences of character"; heldout_essays=19; train_essays=71
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="influencing behavior"; heldout_essays=14; train_essays=48
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="internships and shadowing"; heldout_essays=12; train_essays=43
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="learning from the experience of others"; heldout_essays=8; train_essays=22
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="lessons with elementary school students"; heldout_essays=8; train_essays=30
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="letter to employer"; heldout_essays=7; train_essays=37
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="lunch menus"; heldout_essays=10; train_essays=82
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="mandatory extracurricular activities"; heldout_essays=6; train_essays=36
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="places to visit"; heldout_essays=7; train_essays=35
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="positive attitudes"; heldout_essays=41; train_essays=134
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="praising student work"; heldout_essays=8; train_essays=48
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="seeking multiple opinions"; heldout_essays=11; train_essays=39
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="self-reliance"; heldout_essays=32; train_essays=98
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="setting our aim"; heldout_essays=7; train_essays=19
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="spending time outdoors"; heldout_essays=8; train_essays=46
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="success and failure"; heldout_essays=40; train_essays=172
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="summer projects"; heldout_essays=6; train_essays=13
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="talents and skills"; heldout_essays=9; train_essays=33
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="three-year high school program"; heldout_essays=26; train_essays=121
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="trying something beyond what you have mastered"; heldout_essays=46; train_essays=121
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="working with a group or alone"; heldout_essays=30; train_essays=101
HELDOUT_PROMPT split=ordinary_KFold; fold=4; prompt="year-round school"; heldout_essays=16; train_essays=49
CENTRES split=ordinary_KFold; fold=4; median_ridge_vocabulary=3.2728949663778479; median_ridge_grammar=3.1352866218241129; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=ordinary_KFold; fold=4; training_predictions_rankings_and_bootstrap_finished=True
FOLD split=ordinary_KFold; fold=5; train_essays=3050; heldout_essays=762; train_prompts=44; heldout_prompts=44; overlapping_prompts=44; disjoint=False; k=ceil(0.20*762)=153
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="afterschool homework club"; heldout_essays=18; train_essays=36
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="being busy"; heldout_essays=44; train_essays=160
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="benefits of a good attitude"; heldout_essays=4; train_essays=26
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="benefits of a problem"; heldout_essays=4; train_essays=29
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="career commitment"; heldout_essays=43; train_essays=179
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="cell phones at school"; heldout_essays=5; train_essays=38
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="cell phones in classrooms"; heldout_essays=14; train_essays=45
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="community service"; heldout_essays=11; train_essays=32
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="controlling extracurricular involvement"; heldout_essays=12; train_essays=40
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="creative arts requirement"; heldout_essays=13; train_essays=38
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="curfews for teenagers"; heldout_essays=7; train_essays=47
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="distance learning"; heldout_essays=56; train_essays=224
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="enjoyable educational activities"; heldout_essays=17; train_essays=40
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="extended school day"; heldout_essays=26; train_essays=62
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="first impressions"; heldout_essays=33; train_essays=135
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="four-day work week"; heldout_essays=30; train_essays=104
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="future accomplishments"; heldout_essays=8; train_essays=25
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="grades for extracurricular activities"; heldout_essays=5; train_essays=32
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="honesty"; heldout_essays=6; train_essays=23
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="imagination"; heldout_essays=14; train_essays=41
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="impact of technology"; heldout_essays=31; train_essays=143
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="individuality"; heldout_essays=25; train_essays=118
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="influences of character"; heldout_essays=20; train_essays=70
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="influencing behavior"; heldout_essays=9; train_essays=53
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="internships and shadowing"; heldout_essays=12; train_essays=43
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="learning from the experience of others"; heldout_essays=7; train_essays=23
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="lessons with elementary school students"; heldout_essays=4; train_essays=34
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="letter to employer"; heldout_essays=14; train_essays=30
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="lunch menus"; heldout_essays=19; train_essays=73
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="mandatory extracurricular activities"; heldout_essays=9; train_essays=33
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="places to visit"; heldout_essays=7; train_essays=35
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="positive attitudes"; heldout_essays=24; train_essays=151
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="praising student work"; heldout_essays=12; train_essays=44
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="seeking multiple opinions"; heldout_essays=8; train_essays=42
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="self-reliance"; heldout_essays=19; train_essays=111
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="setting our aim"; heldout_essays=2; train_essays=24
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="spending time outdoors"; heldout_essays=11; train_essays=43
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="success and failure"; heldout_essays=40; train_essays=172
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="summer projects"; heldout_essays=2; train_essays=17
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="talents and skills"; heldout_essays=11; train_essays=31
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="three-year high school program"; heldout_essays=30; train_essays=117
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="trying something beyond what you have mastered"; heldout_essays=31; train_essays=136
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="working with a group or alone"; heldout_essays=32; train_essays=99
HELDOUT_PROMPT split=ordinary_KFold; fold=5; prompt="year-round school"; heldout_essays=13; train_essays=52
CENTRES split=ordinary_KFold; fold=5; median_ridge_vocabulary=3.2585867719412143; median_ridge_grammar=3.0949126422726652; fit_scaler_on_train_only=True; rf_random_state=42
FOLD_COMPLETE split=ordinary_KFold; fold=5; training_predictions_rankings_and_bootstrap_finished=True
SPLIT_COMPLETE split=ordinary_KFold; pooled_n=3812; no_cross_fold_queue_reranking=True
CSV t3_pooled.csv
task_label,split_type,fold,anchor,ranking,n,K,k,caught,capture,precision,lift,expected_random,exact_hypergeom_p,pooled_joint_random_p,capture_arithmetic,precision_arithmetic,lift_arithmetic,expected_arithmetic,p_expression,random_mean,random_p2_5,random_p97_5,random_mean_arithmetic,seed,joint_draws_ge_observed,caught_arithmetic,K_arithmetic
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A1_RF,Random,3812,386,764,77.781999999999996,0.20150777202072537,0.1018089005235602,1.0054172158069843,77.362908429580997,,,77.782/386=0.20150777202072537,77.782/764=0.1018089005235602,77.782/77.362908429580997=1.0054172158069843,14.618985695708712+17.645833333333332+15.078843626806833+15.199999999999999+14.819245773732119=77.362908429580997,NA Random mean is not an integer observation,77.781999999999996,64,93,77782/1000=77.781999999999996,42,,77782/1000=77.781999999999996,73+88+75+76+74=386
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A1_RF,Disagreement,3812,386,764,88,0.22797927461139897,0.11518324607329843,1.1374960143865498,77.362908429580997,,0.105,88/386=0.22797927461139897,88/764=0.11518324607329843,88/77.362908429580997=1.1374960143865498,14.618985695708712+17.645833333333332+15.078843626806833+15.199999999999999+14.819245773732119=77.362908429580997,105/1000=0.105,,,,,42,105,15+22+20+17+14=88,73+88+75+76+74=386
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A1_RF,Ridge Extremity,3812,386,764,65,0.16839378238341968,0.085078534031413619,0.84019591971733787,77.362908429580997,,0.96399999999999997,65/386=0.16839378238341968,65/764=0.085078534031413619,65/77.362908429580997=0.84019591971733787,14.618985695708712+17.645833333333332+15.078843626806833+15.199999999999999+14.819245773732119=77.362908429580997,964/1000=0.96399999999999997,,,,,42,964,13+18+11+12+11=65,73+88+75+76+74=386
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A1_RF,Shortest-first,3812,386,764,85,0.22020725388601037,0.11125654450261781,1.0987177411688265,77.362908429580997,,0.186,85/386=0.22020725388601037,85/764=0.11125654450261781,85/77.362908429580997=1.0987177411688265,14.618985695708712+17.645833333333332+15.078843626806833+15.199999999999999+14.819245773732119=77.362908429580997,186/1000=0.186,,,,,42,186,16+16+20+15+18=85,73+88+75+76+74=386
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A2_Ridge,Random,3812,384,764,77.260999999999996,0.20120052083333331,0.10112696335078533,1.0038834693187986,76.962119968393054,,,77.261/384=0.20120052083333331,77.261/764=0.10112696335078533,77.261/76.962119968393054=1.0038834693187986,13.617685305591678+18.447916666666668+14.877792378449408+15.6+14.418725617685306=76.962119968393054,NA Random mean is not an integer observation,77.260999999999996,63.975000000000001,92,77261/1000=77.260999999999996,42,,77261/1000=77.260999999999996,68+92+74+78+72=384
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A2_Ridge,Disagreement,3812,384,764,93,0.2421875,0.12172774869109948,1.2083866717573972,76.962119968393054,,0.021999999999999999,93/384=0.2421875,93/764=0.12172774869109948,93/76.962119968393054=1.2083866717573972,13.617685305591678+18.447916666666668+14.877792378449408+15.6+14.418725617685306=76.962119968393054,22/1000=0.021999999999999999,,,,,42,22,20+24+18+15+16=93,68+92+74+78+72=384
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A2_Ridge,Ridge Extremity,3812,384,764,67,0.17447916666666666,0.087696335078534027,0.87055813986823238,76.962119968393054,,0.92500000000000004,67/384=0.17447916666666666,67/764=0.087696335078534027,67/76.962119968393054=0.87055813986823238,13.617685305591678+18.447916666666668+14.877792378449408+15.6+14.418725617685306=76.962119968393054,925/1000=0.92500000000000004,,,,,42,925,12+21+14+8+12=67,68+92+74+78+72=384
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A2_Ridge,Shortest-first,3812,384,764,71,0.18489583333333334,0.09293193717277487,0.92253176015887306,76.962119968393054,,0.82099999999999995,71/384=0.18489583333333334,71/764=0.09293193717277487,71/76.962119968393054=0.92253176015887306,13.617685305591678+18.447916666666668+14.877792378449408+15.6+14.418725617685306=76.962119968393054,821/1000=0.82099999999999995,,,,,42,821,14+14+18+10+15=71,68+92+74+78+72=384
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A3_Both_wrong,Random,3812,276,764,55.579000000000001,0.2013731884057971,0.072747382198952881,1.0046481289221452,55.321856877023137,,,55.579/276=0.2013731884057971,55.579/764=0.072747382198952881,55.579/55.321856877023137=1.0046481289221452,10.413524057217165+14.236979166666666+11.258869908015768+9.8000000000000007+9.6124837451235372=55.321856877023137,NA Random mean is not an integer observation,55.579000000000001,43,69,55579/1000=55.579000000000001,42,,55579/1000=55.579000000000001,52+71+56+49+48=276
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A3_Both_wrong,Disagreement,3812,276,764,44,0.15942028985507245,0.057591623036649213,0.79534568222843849,55.321856877023137,,0.96999999999999997,44/276=0.15942028985507245,44/764=0.057591623036649213,44/55.321856877023137=0.79534568222843849,10.413524057217165+14.236979166666666+11.258869908015768+9.8000000000000007+9.6124837451235372=55.321856877023137,970/1000=0.96999999999999997,,,,,42,970,10+12+9+7+6=44,52+71+56+49+48=276
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A3_Both_wrong,Ridge Extremity,3812,276,764,43,0.15579710144927536,0.056282722513089002,0.77726964399597398,55.321856877023137,,0.98199999999999998,43/276=0.15579710144927536,43/764=0.056282722513089002,43/55.321856877023137=0.77726964399597398,10.413524057217165+14.236979166666666+11.258869908015768+9.8000000000000007+9.6124837451235372=55.321856877023137,982/1000=0.98199999999999998,,,,,42,982,8+17+7+6+5=43,52+71+56+49+48=276
Exploratory extension designed after Official Test was used.,prompt_disjoint,pooled,A3_Both_wrong,Shortest-first,3812,276,764,51,0.18478260869565216,0.066753926701570682,0.92187794985569005,55.321856877023137,,0.79100000000000004,51/276=0.18478260869565216,51/764=0.066753926701570682,51/55.321856877023137=0.92187794985569005,10.413524057217165+14.236979166666666+11.258869908015768+9.8000000000000007+9.6124837451235372=55.321856877023137,791/1000=0.79100000000000004,,,,,42,791,10+11+11+7+12=51,52+71+56+49+48=276
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A1_RF,Random,3812,376,765,75.307000000000002,0.20028457446808512,0.098440522875816991,0.99804538491154138,75.454484473844445,,,75.307/376=0.20028457446808512,75.307/765=0.098440522875816991,75.307/75.454484473844445=0.99804538491154138,14.638269986893841+17.044560943643514+15.661417322834646+14.858267716535433+13.251968503937007=75.454484473844445,NA Random mean is not an integer observation,75.307000000000002,60.975000000000001,90,75307/1000=75.307000000000002,42,,75307/1000=75.307000000000002,73+85+78+74+66=376
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A1_RF,Disagreement,3812,376,765,86,0.22872340425531915,0.11241830065359477,1.1397599572734614,75.454484473844445,,0.086999999999999994,86/376=0.22872340425531915,86/765=0.11241830065359477,86/75.454484473844445=1.1397599572734614,14.638269986893841+17.044560943643514+15.661417322834646+14.858267716535433+13.251968503937007=75.454484473844445,87/1000=0.086999999999999994,,,,,42,87,22+19+17+17+11=86,73+85+78+74+66=376
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A1_RF,Ridge Extremity,3812,376,765,59,0.15691489361702127,0.077124183006535951,0.7819283427806305,75.454484473844445,,0.99299999999999999,59/376=0.15691489361702127,59/765=0.077124183006535951,59/75.454484473844445=0.7819283427806305,14.638269986893841+17.044560943643514+15.661417322834646+14.858267716535433+13.251968503937007=75.454484473844445,993/1000=0.99299999999999999,,,,,42,993,12+17+11+11+8=59,73+85+78+74+66=376
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A1_RF,Shortest-first,3812,376,765,81,0.21542553191489361,0.10588235294117647,1.0734948434784928,75.454484473844445,,0.25,81/376=0.21542553191489361,81/765=0.10588235294117647,81/75.454484473844445=1.0734948434784928,14.638269986893841+17.044560943643514+15.661417322834646+14.858267716535433+13.251968503937007=75.454484473844445,250/1000=0.25,,,,,42,250,18+18+14+20+11=81,73+85+78+74+66=376
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A2_Ridge,Random,3812,383,765,76.744,0.20037597911227154,0.10031895424836601,0.99848055482044762,76.860785750405057,,,76.744/383=0.20037597911227154,76.744/765=0.10031895424836601,76.744/76.860785750405057=0.99848055482044762,14.036697247706423+17.044560943643514+15.661417322834646+16.464566929133859+13.653543307086615=76.860785750405057,NA Random mean is not an integer observation,76.744,62.975000000000001,91,76744/1000=76.744,42,,76744/1000=76.744,70+85+78+82+68=383
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A2_Ridge,Disagreement,3812,383,765,93,0.24281984334203655,0.12156862745098039,1.2099798238077457,76.860785750405057,,0.012999999999999999,93/383=0.24281984334203655,93/765=0.12156862745098039,93/76.860785750405057=1.2099798238077457,14.036697247706423+17.044560943643514+15.661417322834646+16.464566929133859+13.653543307086615=76.860785750405057,13/1000=0.012999999999999999,,,,,42,13,18+24+17+20+14=93,70+85+78+82+68=383
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A2_Ridge,Ridge Extremity,3812,383,765,64,0.16710182767624021,0.083660130718954243,0.8326742873515669,76.860785750405057,,0.96799999999999997,64/383=0.16710182767624021,64/765=0.083660130718954243,64/76.860785750405057=0.8326742873515669,14.036697247706423+17.044560943643514+15.661417322834646+16.464566929133859+13.653543307086615=76.860785750405057,968/1000=0.96799999999999997,,,,,42,968,12+17+15+12+8=64,70+85+78+82+68=383
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A2_Ridge,Shortest-first,3812,383,765,72,0.18798955613577023,0.094117647058823528,0.93675857327051282,76.860785750405057,,0.754,72/383=0.18798955613577023,72/765=0.094117647058823528,72/76.860785750405057=0.93675857327051282,14.036697247706423+17.044560943643514+15.661417322834646+16.464566929133859+13.653543307086615=76.860785750405057,754/1000=0.754,,,,,42,754,15+15+13+17+12=72,70+85+78+82+68=383
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A3_Both_wrong,Random,3812,271,765,54.276000000000003,0.20028044280442805,0.070949019607843139,0.99800607012667131,54.384438757081966,,,54.276/271=0.20028044280442805,54.276/765=0.070949019607843139,54.276/54.384438757081966=0.99800607012667131,9.6251638269986888+12.432503276539974+11.244094488188976+11.244094488188976+9.8385826771653537=54.384438757081966,NA Random mean is not an integer observation,54.276000000000003,42,67.024999999999977,54276/1000=54.276000000000003,42,,54276/1000=54.276000000000003,48+62+56+56+49=271
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A3_Both_wrong,Disagreement,3812,271,765,40,0.14760147601476015,0.052287581699346407,0.73550451037414044,54.384438757081966,,0.99299999999999999,40/271=0.14760147601476015,40/765=0.052287581699346407,40/54.384438757081966=0.73550451037414044,9.6251638269986888+12.432503276539974+11.244094488188976+11.244094488188976+9.8385826771653537=54.384438757081966,993/1000=0.99299999999999999,,,,,42,993,7+11+8+8+6=40,48+62+56+56+49=271
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A3_Both_wrong,Ridge Extremity,3812,271,765,38,0.14022140221402213,0.049673202614379082,0.6987292848554334,54.384438757081966,,0.999,38/271=0.14022140221402213,38/765=0.049673202614379082,38/54.384438757081966=0.6987292848554334,9.6251638269986888+12.432503276539974+11.244094488188976+11.244094488188976+9.8385826771653537=54.384438757081966,999/1000=0.999,,,,,42,999,7+10+8+9+4=38,48+62+56+56+49=271
Exploratory extension designed after Official Test was used.,ordinary_KFold,pooled,A3_Both_wrong,Shortest-first,3812,271,765,55,0.2029520295202952,0.071895424836601302,1.0113187017644432,54.384438757081966,,0.47799999999999998,55/271=0.2029520295202952,55/765=0.071895424836601302,55/54.384438757081966=1.0113187017644432,9.6251638269986888+12.432503276539974+11.244094488188976+11.244094488188976+9.8385826771653537=54.384438757081966,478/1000=0.47799999999999998,,,,,42,478,11+12+10+15+7=55,48+62+56+56+49=271
CSV t3_summary.csv
task_label,split_type,anchor,n,K,budget_k,Disagreement_caught,expected_random,pooled_joint_random_p,Ridge_V_pooled_MAE,Ridge_V_MAE_arithmetic,Ridge_G_pooled_MAE,Ridge_G_MAE_arithmetic,RF_V_pooled_MAE,RF_V_MAE_arithmetic,RF_G_pooled_MAE,RF_G_MAE_arithmetic,caught_arithmetic,expected_arithmetic,p_arithmetic
Exploratory extension designed after Official Test was used.,prompt_disjoint,A1_RF,3812,386,764,88,77.362908429580997,0.105,0.37342443714543022,1423.4939543983801/3812=0.37342443714543022,0.46303653771248415,1765.0952817599896/3812=0.46303653771248415,0.37216506904049607,1418.6932431823709/3812=0.37216506904049607,0.45540371959591663,1735.9989790996342/3812=0.45540371959591663,15+22+20+17+14=88,14.618985695708712+17.645833333333332+15.078843626806833+15.199999999999999+14.819245773732119=77.362908429580997,105/1000=0.105
Exploratory extension designed after Official Test was used.,prompt_disjoint,A2_Ridge,3812,384,764,93,76.962119968393054,0.021999999999999999,0.37342443714543022,1423.4939543983801/3812=0.37342443714543022,0.46303653771248415,1765.0952817599896/3812=0.46303653771248415,0.37216506904049607,1418.6932431823709/3812=0.37216506904049607,0.45540371959591663,1735.9989790996342/3812=0.45540371959591663,20+24+18+15+16=93,13.617685305591678+18.447916666666668+14.877792378449408+15.6+14.418725617685306=76.962119968393054,22/1000=0.021999999999999999
Exploratory extension designed after Official Test was used.,prompt_disjoint,A3_Both_wrong,3812,276,764,44,55.321856877023137,0.96999999999999997,0.37342443714543022,1423.4939543983801/3812=0.37342443714543022,0.46303653771248415,1765.0952817599896/3812=0.46303653771248415,0.37216506904049607,1418.6932431823709/3812=0.37216506904049607,0.45540371959591663,1735.9989790996342/3812=0.45540371959591663,10+12+9+7+6=44,10.413524057217165+14.236979166666666+11.258869908015768+9.8000000000000007+9.6124837451235372=55.321856877023137,970/1000=0.96999999999999997
Exploratory extension designed after Official Test was used.,ordinary_KFold,A1_RF,3812,376,765,86,75.454484473844445,0.086999999999999994,0.37230494010695886,1419.2264316877272/3812=0.37230494010695886,0.46147110095779442,1759.1278368511123/3812=0.46147110095779442,0.37166317701951734,1416.7800307984/3812=0.37166317701951734,0.45439074799896872,1732.1375313720687/3812=0.45439074799896872,22+19+17+17+11=86,14.638269986893841+17.044560943643514+15.661417322834646+14.858267716535433+13.251968503937007=75.454484473844445,87/1000=0.086999999999999994
Exploratory extension designed after Official Test was used.,ordinary_KFold,A2_Ridge,3812,383,765,93,76.860785750405057,0.012999999999999999,0.37230494010695886,1419.2264316877272/3812=0.37230494010695886,0.46147110095779442,1759.1278368511123/3812=0.46147110095779442,0.37166317701951734,1416.7800307984/3812=0.37166317701951734,0.45439074799896872,1732.1375313720687/3812=0.45439074799896872,18+24+17+20+14=93,14.036697247706423+17.044560943643514+15.661417322834646+16.464566929133859+13.653543307086615=76.860785750405057,13/1000=0.012999999999999999
Exploratory extension designed after Official Test was used.,ordinary_KFold,A3_Both_wrong,3812,271,765,40,54.384438757081966,0.99299999999999999,0.37230494010695886,1419.2264316877272/3812=0.37230494010695886,0.46147110095779442,1759.1278368511123/3812=0.46147110095779442,0.37166317701951734,1416.7800307984/3812=0.37166317701951734,0.45439074799896872,1732.1375313720687/3812=0.45439074799896872,7+11+8+8+6=40,9.6251638269986888+12.432503276539974+11.244094488188976+11.244094488188976+9.8385826771653537=54.384438757081966,993/1000=0.99299999999999999
CSV t3_training_output_hashes.csv
task_label,path,sha256
Exploratory extension designed after Official Test was used.,reports/week9/t3_fold_composition.csv,de596a84028e42b8aa0c605c523ee98eef87b6b74127a63b0c8e822d0e0629ea
Exploratory extension designed after Official Test was used.,reports/week9/t3_regression.csv,ed9202cdb2aee24b514d4ce52fdd464d60adf9a92aae33d3f909f3bffb238795
Exploratory extension designed after Official Test was used.,reports/week9/t3_rankings.csv,d87dd509d7276d1e77a8496d6324d5053491e535e6680a7d95df8527289fc936
Exploratory extension designed after Official Test was used.,reports/week9/t3_auroc.csv,908594bb01eab0f47d87fc0f2e31030347753214efc91c97891c94fb95b274b9
Exploratory extension designed after Official Test was used.,reports/week9/t3_pooled.csv,d7b54638becf5957bd75fe66c8870094567c9108e5111a3cb82c0ec910513322
Exploratory extension designed after Official Test was used.,reports/week9/t3_heldout_predictions.csv,15cedfabd362b0b956084fcf3cbda1ef1c502ed6979755c19274cf22d55c64c9
Exploratory extension designed after Official Test was used.,reports/week9/t3_bootstrap.csv,61026222f6aa748a5925a0e783afc8ed7e54628046dc425be15975a12397fc88
Exploratory extension designed after Official Test was used.,reports/week9/t3_training_audit.csv,2c9af49fedd13ec44d3c60de14f29eb80ddcfa6c81930234c833ed037ea928da
Exploratory extension designed after Official Test was used.,reports/week9/t3_random_draws.csv,358456f7a22f0de97eda7fd21d75d513280b9b3476d4298e1e13b3bb5e48df4d
Exploratory extension designed after Official Test was used.,reports/week9/t3_joint_random_draws.csv,f16a1b400253446e52d072ce6483bb68dbece6c002f01bee4d9ad38d15fb3a15
Exploratory extension designed after Official Test was used.,reports/week9/t3_summary.csv,62d073e5864b3b7373166544bc2f0199a94ae970275ef0208420649fceb01e22
Exploratory extension designed after Official Test was used.,reports/week9/t3_training_sources.csv,97a74b02cf353d68784052256f8d25e26f90ed6ca70718a93256d20b647a462b
STATUS: Task 3 COMPLETE on documented eligible development population. All outputs exploratory; no interpretation beyond numbers. No tuning, Test files, existing model writes or manual sample changes.
```

[src: reports/week9/logs/t3_training_run1.log exact quoted lines; every CSV block names its source file]

Fresh-process repeat proof:

```text
RUN1_SHA256=7e6f6d96fdf4627276f35c89273166beed47ba155a4a1fea1124020dce614ee3
RUN2_SHA256=7e6f6d96fdf4627276f35c89273166beed47ba155a4a1fea1124020dce614ee3
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t3_training.log final hash lines]

### Artifact verification

**Exploratory extension designed after Official Test was used.**

Independent artifact checks use saved eligible-development and new Task 3 outputs only; no fitting or Official Test file access. Every AUROC is checked against scikit-learn, and initial bootstrap replicates are checked independently to validate the weighted-count implementation. All fold assignments, queue selections, random draws and pooled tail counts are reconstructed. Raw checks and fresh-process hashes follow.

Producer: `scripts/week9/t3_verify.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t3_verify.py --capture`. Each fresh child: `.venv/Scripts/python.exe -u scripts/week9/t3_verify.py`. Environment: `PYTHONHASHSEED=42`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`.

Raw terminal output, first fresh process:

```text
Exploratory extension designed after Official Test was used.
COMMAND: .venv/Scripts/python.exe -u scripts/week9/t3_verify.py
SEED=42; verification only; no fitting
PASS source/output hashes and exact eligible population; reconstructed GroupKFold/KFold memberships; prompt separation/overlap and training-ID/scaler-fit audits.
PASS all held-out labels, exact queue selections, captured counts, per-fold hypergeometric p values, every standalone random draw and every independent-fold joint draw.
PASS all pooled sums, expectations and empirical joint p values; no cross-fold queue reranking; all regression metrics independently recomputed.
PASS every AUROC checked with sklearn; every interval recomputed from saved bootstrap replicates; initial bootstrap replicates independently checked with sklearn.
PASS diagnosis and training each have identical fresh-process raw outputs; all recorded prediction/artifact hashes match.
```

[src: reports/week9/logs/t3_verification_run1.log exact quoted lines; every CSV block names its source file]

Fresh-process repeat proof:

```text
RUN1_SHA256=22e342ccff783aaed5bace3a57a3c660887d17b3a7eb5901967db1d35f02611a
RUN2_SHA256=22e342ccff783aaed5bace3a57a3c660887d17b3a7eb5901967db1d35f02611a
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t3_verification.log final hash lines]

### Completed Task 3 output index and summary

**Exploratory extension designed after Official Test was used.**

**COMPLETE following the eligibility diagnosis.** The initial preflight stop remains above as historical evidence. Applying the documented privacy rule unchanged yielded the authorized population; both split designs, fresh-process retraining and artifact verification are now complete. The earlier Task sections have not been edited.

| Model / target | Prompt-disjoint pooled MAE | Ordinary KFold pooled MAE | Source |
|---|---:|---:|---|
| Ridge Vocabulary | 0.37342443714543022 | 0.37230494010695886 | [src: reports/week9/t3_summary.csv rows 1, 4] |
| Ridge Grammar | 0.46303653771248415 | 0.46147110095779442 | [src: reports/week9/t3_summary.csv rows 1, 4] |
| RF Vocabulary | 0.37216506904049607 | 0.37166317701951734 | [src: reports/week9/t3_summary.csv rows 1, 4] |
| RF Grammar | 0.45540371959591663 | 0.45439074799896872 | [src: reports/week9/t3_summary.csv rows 1, 4] |

| Split | Anchor | K | Disagreement caught | Expected random caught | Joint random p | Source |
|---|---|---:|---:|---:|---:|---|
| Prompt-disjoint | A1 RF | 386 | 88 | 77.362908429580997 | 0.105 | [src: reports/week9/t3_summary.csv row 1] |
| Prompt-disjoint | A2 Ridge | 384 | 93 | 76.962119968393054 | 0.021999999999999999 | [src: reports/week9/t3_summary.csv row 2] |
| Prompt-disjoint | A3 Both wrong | 276 | 44 | 55.321856877023137 | 0.96999999999999997 | [src: reports/week9/t3_summary.csv row 3] |
| Ordinary KFold | A1 RF | 376 | 86 | 75.454484473844445 | 0.086999999999999994 | [src: reports/week9/t3_summary.csv row 4] |
| Ordinary KFold | A2 Ridge | 383 | 93 | 76.860785750405057 | 0.012999999999999999 | [src: reports/week9/t3_summary.csv row 5] |
| Ordinary KFold | A3 Both wrong | 271 | 40 | 54.384438757081966 | 0.99299999999999999 | [src: reports/week9/t3_summary.csv row 6] |

Explicit arithmetic for each summary entry is preserved in the same source rows: MAE is summed absolute error divided by population size; caught and K are sums over folds; expected random is the sum of fold expectations; joint p is the count of joint draws at least as high divided by the number of joint draws. The full source CSV is quoted verbatim before the raw training transcript above.

Requested outputs: [fold composition and prompt overlaps](t3_fold_composition.csv), [fold and pooled regression](t3_regression.csv), [fold ranking metrics](t3_rankings.csv), [fold and pooled AUROC intervals](t3_auroc.csv), [pooled ranking metrics](t3_pooled.csv), [held-out predictions for both designs](t3_heldout_predictions.csv), and [summary](t3_summary.csv).

Additional evidence: [eligibility counts](t3_eligibility_counts.csv), [exclusion reasons](t3_eligibility_reasons.csv), [prompt preservation](t3_eligibility_prompts.csv), [ID equality checks](t3_eligibility_checks.csv), [exact source-code quotations with line numbers](t3_eligibility_code.csv), [training audit and centers](t3_training_audit.csv), [bootstrap replicates](t3_bootstrap.csv), [fold random draws](t3_random_draws.csv), [joint random draws](t3_joint_random_draws.csv), [output hashes](t3_training_output_hashes.csv), and [complete cumulative raw log](logs/t3.log).

Both fresh-process training-output hashes are printed in `logs/t3_training.log` and quoted above; they include the hashes of every saved prediction and numeric output. Training-output determinism is confirmed by equality of those raw outputs and their embedded artifact hashes. No Official Test feature, label, prediction, evaluation or source file was opened. The shared administrative manifest was used solely to recover development eligibility metadata, as documented in the diagnosis.

## Task 4

### Current reading status - AI PRE-ANNOTATION; team review pending

The fixed 32-essay reading was an AI pre-annotation in two passes: Pass 1 was blind in an isolated context and locked by SHA256 `556bf72fa3ca97fa5ad198129592cf215a9a715b9532e09fe2b2c2776fef15cf`; Pass 2 was unblinded. Team verification is pending: 0/32 verdicts filled; agree 0 / edited 0 / disagree 0. These are AI pre-annotations, not team-verified reading results. The team must verify every row and takes responsibility for the reading results it subsequently approves and reports.

Source: `reports/week9/t4_reading_sheet.xlsx`, `AI_preannotation`, Excel rows 2-33, `team_verdict`. The SHA256 above identifies the locked Pass 1 records preserved in `pass1_record_json` and `pass1_lock_sha256`. [src: reports/week9/t4_reading_sheet.xlsx AI_preannotation rows 2-33]

The planned [text-free reading summary](t4_reading_summary.csv) does not yet exist. Export remains blocked by the empty team verdicts. No team judgement was filled by the AI. Authoritative full assignment wording remains unavailable, so off-topic values are unclear. The earlier workbook-preparation logs and original result sections below are historical evidence and have not been rewritten.

### Original Task 4 workbook preparation - historical evidence

Deliverable: [private reading workbook](t4_reading_sheet.xlsx), with the fixed reading sheet and criterion rubric. The full source essay values are retained in wrapped cells; rendered workbook, rubric, team-input and essay-text views were visually inspected. Sources: [selection reproduction](t4_selection_check.csv), [sample-group × quadrant counts](t4_group_quadrant_counts.csv), [Task 1 category counts](t4_category_counts.csv), [workbook hash](t4_output_hashes.csv), and [raw log](logs/t4.log).

The existing sample already contains `7` non-large-error essays at-or-above median D, so the conditional supplementary proposal is not needed and no supplementary sheet was added. Task 1 categories within the fixed sample are `a=19`, `b=3`, `c=0`, `none=10`. No human coding has been filled. [src: reports/week9/logs/t4_run1.log EXAMPLE_B line; reports/week9/t4_category_counts.csv rows 1–4]

Exploratory extension designed after Official Test was used.

PARTIAL: the workbook is complete for available source fields, but authoritative full assignment wording is absent. The released short prompt name is preserved and full_prompt_text is blank; the team must obtain the assignment before coding off-topic. All existing human cells are copied verbatim into source_ columns; requested new team columns and rubric how_to_decide remain empty. The sample reproduction, counts and workbook verification are evidenced below. The original sample is unchanged. Private text-bearing intermediates/previews and the workbook are ignored by Git. Authoring uses the bundled artifact-tool; verification inspects the exported XLSX XML directly with the standard library. ZIP timestamps, document timestamps and randomly assigned package relationship IDs are canonicalized solely for deterministic serialization; cell values and relationship targets are unchanged. Initial attempt logs are preserved: logs/t4_attempt1.log records the missing openpyxl verification dependency; logs/t4_attempt2.log records differing serialized hashes despite identical payloads, traced to random relationship IDs. No statistical result, text or sample changed to resolve these packaging issues.

Producer: `scripts/week9/t4_reading_sheet.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t4_reading_sheet.py --capture`. Child command: `.venv/Scripts/python.exe -u scripts/week9/t4_reading_sheet.py`.

Raw terminal output:

```text
Exploratory extension designed after Official Test was used.
COMMAND: .venv/Scripts/python.exe -u scripts/week9/t4_reading_sheet.py
SEED=42; fixed existing sample; no sampling or human judgement
A1_ASSERT_PASS K=69; Disagreement=15; Shortest-first=15; Ridge Extremity=10; N=762; budget=153
SEED=42; bootstrap_resamples=2000; random_draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending; centers=(3.26941940240918, 3.124225726952784)
SAMPLE existing docs/data/error_analysis/manual_error_review.csv; 32 unique Validation IDs; membership only; no human judgement read or written
METHOD y_V/y_G are saved human two-rater means, reused without re-anchoring; equal to Validation clean-table targets. Both-trigger RF-error ties use V deterministically.
METHOD only allowlisted Validation predictions, development table, Validation clean table and existing Validation sample IDs are read; no Official Test file is opened.
CSV t4_selection_check.csv
existing_n,reproduced_n,same_ids,same_groups,missing,extra,action
32,32,True,True,0,0,existing sample retained unchanged
SELECTION rule script lines 148-169; exact sequential highest-error, low-D large-error and low-error-control selection; source IDs are retained regardless of reproduction status.
CODE scripts/post_midterm_teacher_analysis.py:148:     for group, mask, count, columns in [
CODE scripts/post_midterm_teacher_analysis.py:149:         ("highest_rf_error", frame.large_error, 12, ["max_rf_error", "essay_id"]),
CODE scripts/post_midterm_teacher_analysis.py:150:         ("shared_blind_spot", frame.large_error & frame.D_max.lt(threshold), 10, ["essay_id"]),
CODE scripts/post_midterm_teacher_analysis.py:151:         ("low_rf_error_comparison", frame.max_rf_error.lt(0.5), 10, ["max_rf_error", "essay_id"]),
CODE scripts/post_midterm_teacher_analysis.py:152:     ]:
CODE scripts/post_midterm_teacher_analysis.py:153:         ascending = [False, True] if group == "highest_rf_error" else True
CODE scripts/post_midterm_teacher_analysis.py:154:         sample = (
CODE scripts/post_midterm_teacher_analysis.py:155:             frame[mask & ~frame.essay_id.isin(already)]
CODE scripts/post_midterm_teacher_analysis.py:156:             .sort_values(columns, ascending=ascending)
CODE scripts/post_midterm_teacher_analysis.py:157:             .head(count)
CODE scripts/post_midterm_teacher_analysis.py:158:             .copy()
CODE scripts/post_midterm_teacher_analysis.py:159:         )
CODE scripts/post_midterm_teacher_analysis.py:160:         assert len(sample) == count
CODE scripts/post_midterm_teacher_analysis.py:161:         sample["sample_group"] = group
CODE scripts/post_midterm_teacher_analysis.py:162:         already.update(sample.essay_id)
CODE scripts/post_midterm_teacher_analysis.py:163:         samples.append(sample)
CODE scripts/post_midterm_teacher_analysis.py:164:     manual = pd.concat(samples)
CODE scripts/post_midterm_teacher_analysis.py:165:     for col in [
CODE scripts/post_midterm_teacher_analysis.py:166:         "reviewer",
CODE scripts/post_midterm_teacher_analysis.py:167:         "off_topic_task_response",
CODE scripts/post_midterm_teacher_analysis.py:168:         "unusual_vocabulary",
CODE scripts/post_midterm_teacher_analysis.py:169:         "grammar_checker_mismatch",
CODE scripts/post_midterm_teacher_analysis.py:170:         "coherence_content",
CSV t4_group_quadrant_counts.csv
sample_group,quadrant,n
highest_rf_error,large_error=yes; D at-or-above median,6
highest_rf_error,large_error=yes; D below median,6
low_rf_error_comparison,large_error=no; D at-or-above median,7
low_rf_error_comparison,large_error=no; D below median,3
shared_blind_spot,large_error=yes; D below median,10
CSV t4_category_counts.csv
task1_category,n
a,19
b,3
c,0
none,10
EXAMPLE_B high_disagreement_no_large_error_in_existing_sample=7; high_disagreement means D >= 0.13398965515499994; supplement_proposed=0; supplementary rows never added to original sample
HUMAN_FIELDS legacy_nonempty_cells=0; copied verbatim in source_ columns; new_team_columns=11; all new team cells empty
WORKBOOK_INSPECT {"kind":"table","sheet":"reading_sheet","address":"A1:B3","rows":3,"cols":2,"values":[["essay_id","sample_group"],["48EA282A4EAF","highest_rf_error"],["0AFC8CE27321","highest_rf_error"]]}
Inspect result written to file: D:\03_Education\học trên trường\mla project\reports\week9\t4_private\reading_sheet_export.xlsx.inspect.ndjson
WORKBOOK_EXPORT reading_sheet; rubric; blank team input cells; previews saved privately
XLSX_CHECK rows, IDs, all source values and verbatim notes match payload; new human fields and rubric how_to_decide blank; essay text wrapped; headers/ID panes frozen; confidence validation present
CSV t4_output_hashes.csv
path,sha256
reports/week9/t4_reading_sheet.xlsx,06f4b392abec64a1b2b13b4bb87546517d737884dc935d4ab361e29e8b88a80e
workbook_source_payload_semantics,33f9b556d8fe6880c238b0eca259363b2c13565ca7d3f7781716a074e2925fb7
LIMITATION: authoritative full prompt wording is not available in released development metadata; prompt_text preserves the source short name, full_prompt_text is empty. Off-topic coding requires the team to obtain the full assignment.
STATUS: PARTIAL only for authoritative full-prompt wording; fixed-sample reading workbook, rater-score mean checks, source-note preservation and requested counts complete. No human judgement filled. No Official Test data file opened; shared raw-rater source retained only allowlisted Validation IDs.
```

[src: reports/week9/logs/t4_run1.log exact lines; each CSV block names its source file and data rows exclude headers]

Fresh-process output hashes:

```text
RUN1_SHA256=682a96c7b142fa0f0f797e0a8d9dee685d5c6fdc1c139672ed9ae91b2e9b421e
RUN2_SHA256=682a96c7b142fa0f0f797e0a8d9dee685d5c6fdc1c139672ed9ae91b2e9b421e
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t4.log hash lines]

## Task 5

Deliverables: [descriptive group captures and explicit arithmetic](t5_fairness.csv), [group inclusion/omission audit](t5_group_coverage.csv), [all group results for the global random draws](t5_random_draws.csv), and [raw log](logs/t5.log). Rows flagged for sparse large-error cases must not be interpreted. No significance tests or fairness claims are supplied.

Exploratory extension designed after Official Test was used.

Descriptive Validation A1 capture within the requested demographic groups. Only groups meeting the requested population-size floor are reported in t5_fairness.csv; t5_group_coverage.csv lists included and omitted group counts. Random means use the same fixed global draws as the frozen Validation random reference. Group budgets are not independently assigned. Rows below the requested large-error-case floor carry the exact do-not-interpret label. Every reported ratio includes explicit arithmetic; no significance tests or fairness claims are made.

Producer: `scripts/week9/t5_fairness.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t5_fairness.py --capture`. Child command: `.venv/Scripts/python.exe -u scripts/week9/t5_fairness.py`.

Raw terminal output:

```text
Exploratory extension designed after Official Test was used.
COMMAND: .venv/Scripts/python.exe -u scripts/week9/t5_fairness.py
SEED=42; Random=1000 global uniform selections without replacement, each 153 of 762; group summaries use those same selections, not separate group budgets
A1_ASSERT_PASS K=69; Disagreement=15; Shortest-first=15; Ridge Extremity=10; N=762; budget=153
SEED=42; bootstrap_resamples=2000; random_draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending; centers=(3.26941940240918, 3.124225726952784)
SAMPLE existing docs/data/error_analysis/manual_error_review.csv; 32 unique Validation IDs; membership only; no human judgement read or written
METHOD y_V/y_G are saved human two-rater means, reused without re-anchoring; equal to Validation clean-table targets. Both-trigger RF-error ties use V deterministically.
METHOD only allowlisted Validation predictions, development table, Validation clean table and existing Validation sample IDs are read; no Official Test file is opened.
FROZEN_REFERENCE_ASSERT selected=153; A1 positives=69; Disagreement caught=15; Random total_caught=13946; Random mean=13946/1000=13.946
CSV t5_fairness.csv
attribute,group,N,K,disagreement_selected,disagreement_caught,capture,selection_rate,random_mean_caught,random_mean_capture,random_mean_selected,random_mean_selection_rate,interpretation_note,capture_arithmetic,selection_rate_arithmetic,random_mean_caught_arithmetic,random_mean_capture_arithmetic,random_mean_selected_arithmetic,random_mean_selection_rate_arithmetic,random_draws,seed
Gender,Female,327,31,58,7,0.22580645161290322,0.17737003058103976,6.1669999999999998,0.19893548387096774,65.605000000000004,0.20062691131498472,descriptive only; no fairness claim,7/31=0.22580645161290322,58/327=0.17737003058103976,6167/1000=6.1669999999999998,6167/(1000*31)=0.19893548387096774,65605/1000=65.605000000000004,65605/(1000*327)=0.20062691131498472,1000,42
Gender,Male,435,38,95,8,0.21052631578947367,0.21839080459770116,7.7789999999999999,0.20471052631578948,87.394999999999996,0.20090804597701148,descriptive only; no fairness claim,8/38=0.21052631578947367,95/435=0.21839080459770116,7779/1000=7.7789999999999999,7779/(1000*38)=0.20471052631578948,87395/1000=87.394999999999996,87395/(1000*435)=0.20090804597701148,1000,42
Grade,10,34,3,9,2,0.66666666666666663,0.26470588235294118,0.626,0.20866666666666667,6.8490000000000002,0.20144117647058823,too few large-error cases — do not interpret,2/3=0.66666666666666663,9/34=0.26470588235294118,626/1000=0.626,626/(1000*3)=0.20866666666666667,6849/1000=6.8490000000000002,6849/(1000*34)=0.20144117647058823,1000,42
Grade,11,266,23,62,3,0.13043478260869565,0.23308270676691728,4.5890000000000004,0.19952173913043481,53.436,0.20088721804511278,descriptive only; no fairness claim,3/23=0.13043478260869565,62/266=0.23308270676691728,4589/1000=4.5890000000000004,4589/(1000*23)=0.19952173913043481,53436/1000=53.436,53436/(1000*266)=0.20088721804511278,1000,42
Grade,12,266,26,52,6,0.23076923076923078,0.19548872180451127,5.2720000000000002,0.20276923076923078,53.436999999999998,0.20089097744360901,descriptive only; no fairness claim,6/26=0.23076923076923078,52/266=0.19548872180451127,5272/1000=5.2720000000000002,5272/(1000*26)=0.20276923076923078,53437/1000=53.436999999999998,53437/(1000*266)=0.20089097744360901,1000,42
Grade,8,192,17,29,4,0.23529411764705882,0.15104166666666666,3.4590000000000001,0.20347058823529413,38.468000000000004,0.20035416666666669,descriptive only; no fairness claim,4/17=0.23529411764705882,29/192=0.15104166666666666,3459/1000=3.4590000000000001,3459/(1000*17)=0.20347058823529413,38468/1000=38.468000000000004,38468/(1000*192)=0.20035416666666669,1000,42
Race/Ethnicity,Asian/Pacific Islander,98,14,22,6,0.42857142857142855,0.22448979591836735,2.8610000000000002,0.20435714285714288,19.690000000000001,0.2009183673469388,descriptive only; no fairness claim,6/14=0.42857142857142855,22/98=0.22448979591836735,2861/1000=2.8610000000000002,2861/(1000*14)=0.20435714285714288,19690/1000=19.690000000000001,19690/(1000*98)=0.2009183673469388,1000,42
Race/Ethnicity,Black/African American,70,4,15,0,0,0.21428571428571427,0.77200000000000002,0.193,14.058,0.20082857142857144,too few large-error cases — do not interpret,0/4=0,15/70=0.21428571428571427,772/1000=0.77200000000000002,772/(1000*4)=0.193,14058/1000=14.058,14058/(1000*70)=0.20082857142857144,1000,42
Race/Ethnicity,Hispanic/Latino,527,42,102,6,0.14285714285714285,0.19354838709677419,8.5190000000000001,0.20283333333333334,105.80200000000001,0.20076280834914612,descriptive only; no fairness claim,6/42=0.14285714285714285,102/527=0.19354838709677419,8519/1000=8.5190000000000001,8519/(1000*42)=0.20283333333333334,105802/1000=105.80200000000001,105802/(1000*527)=0.20076280834914612,1000,42
Race/Ethnicity,White,59,7,12,2,0.2857142857142857,0.20338983050847459,1.3979999999999999,0.19971428571428571,11.843,0.20072881355932204,too few large-error cases — do not interpret,2/7=0.2857142857142857,12/59=0.20338983050847459,1398/1000=1.3979999999999999,1398/(1000*7)=0.19971428571428571,11843/1000=11.843,11843/(1000*59)=0.20072881355932204,1000,42
SES,Economically disadvantaged,512,50,102,9,0.17999999999999999,0.19921875,10.125999999999999,0.20251999999999998,102.614,0.20041796875000001,descriptive only; no fairness claim,9/50=0.17999999999999999,102/512=0.19921875,10126/1000=10.125999999999999,10126/(1000*50)=0.20251999999999998,102614/1000=102.614,102614/(1000*512)=0.20041796875000001,1000,42
SES,Not economically disadvantaged,250,19,51,6,0.31578947368421051,0.20399999999999999,3.8199999999999998,0.20105263157894737,50.386000000000003,0.201544,descriptive only; no fairness claim,6/19=0.31578947368421051,51/250=0.20399999999999999,3820/1000=3.8199999999999998,3820/(1000*19)=0.20105263157894737,50386/1000=50.386000000000003,50386/(1000*250)=0.201544,1000,42
CSV t5_group_coverage.csv
attribute,group,N,K,reported,reason
Gender,Female,327,31,True,N >= 20
Gender,Male,435,38,True,N >= 20
Grade,10,34,3,True,N >= 20
Grade,11,266,23,True,N >= 20
Grade,12,266,26,True,N >= 20
Grade,8,192,17,True,N >= 20
Grade,9,4,0,False,N < 20
Race/Ethnicity,American Indian/Alaskan Native,2,0,False,N < 20
Race/Ethnicity,Asian/Pacific Islander,98,14,True,N >= 20
Race/Ethnicity,Black/African American,70,4,True,N >= 20
Race/Ethnicity,Hispanic/Latino,527,42,True,N >= 20
Race/Ethnicity,Two or more races/Other,6,2,False,N < 20
Race/Ethnicity,White,59,7,True,N >= 20
SES,Economically disadvantaged,512,50,True,N >= 20
SES,Not economically disadvantaged,250,19,True,N >= 20
CSV t5_output_hashes.csv
path,sha256
reports/week9/t5_fairness.csv,582c23765a6f68fd17540535b14d06159a9e620ac8155f5be65f289004ba695a
reports/week9/t5_group_coverage.csv,62a9cbb6f956efcfa0a3048f9f5c9c007c5baf77da8e8c9d9365e55bc960ee25
reports/week9/t5_random_draws.csv,06953b702695caf74fae40538868678e9587af70ef18bc2a07f3dcd9585191a1
reports/week9/t5_sources.csv,9fac3105c752d42c7aa8c261f8065b69d3f1ced02624b329df2ee11c73dc3a51
STATUS: COMPLETE descriptive Validation A1 group captures. No significance tests, subgroup retuning or fairness claims. No Official Test file opened. All source hashes unchanged.
```

[src: reports/week9/logs/t5_run1.log exact lines; each CSV block names its source file and data rows exclude headers]

Fresh-process output hashes:

```text
RUN1_SHA256=856c5542ab9ca7ea3849ae9c051c0b2afbbadf482e0522148bcae4c906474ac4
RUN2_SHA256=856c5542ab9ca7ea3849ae9c051c0b2afbbadf482e0522148bcae4c906474ac4
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t5.log hash lines]

### Reading workbook and group-table verification

Exploratory extension designed after Official Test was used.

The group table is independently checked against saved Task 1 essays, Validation demographics and recreated global random selections. Workbook/source hashes, Git ignore coverage and both task repeat logs are checked. The exported workbook is imported with artifact-tool to render the wrapped full-essay column privately; text is not printed to logs.

Producer: `scripts/week9/t45_verify.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t45_verify.py --capture`. Child command: `.venv/Scripts/python.exe -u scripts/week9/t45_verify.py`.

Raw terminal output:

```text
COMMAND: .venv/Scripts/python.exe -u scripts/week9/t45_verify.py
SEED=42; verification only; no fitting or human coding
PASS all included/omitted group memberships, deterministic numerator/denominator counts, every global-random group draw and every reported group ratio independently checked.
GIT_IGNORE_PASS reports/week9/t4_reading_sheet.xlsx
GIT_IGNORE_PASS reports/week9/t4_private/payload.json
GIT_IGNORE_PASS scripts/week9/node_modules/
RENDER_CHECK exported workbook essay_text column rendered privately; no essay text printed to logs
PASS fixed reading workbook/source hashes and Task 4/5 repeat-output hashes; no source sample or human entries modified.
```

[src: reports/week9/logs/t45_verification_run1.log exact lines; each CSV block names its source file and data rows exclude headers]

Fresh-process output hashes:

```text
RUN1_SHA256=a4c80a7b6a1f168f0f5052acaf697c539b47319561308d1d83e3eaa3d2a80d22
RUN2_SHA256=a4c80a7b6a1f168f0f5052acaf697c539b47319561308d1d83e3eaa3d2a80d22
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t45_verification.log hash lines]

## Task 6

Exploratory extension designed after Official Test was used.

README diff only: README.md is not modified. The full proposed section is saved as t6_README_section.md; the complete working-copy-based proposal is t6_README_proposed.md; the applicable patch is t6_README.diff. The expressly authorized .gitignore edit is already applied and its full diff is t6_gitignore.diff. The draft distinguishes tracked Test result tables, which entered the recorded snapshot together, from untracked prediction CSVs. It preserves the actual PARTIAL limitations rather than declaring chronology or missing authoritative prompt wording complete. All Test numbers, dates and hashes are read solely from saved Task 0 evidence. The original Task sections are retained. Full diffs follow in the raw transcript; no commit, push or Git configuration change is performed. An initial terminal-encoding failure while printing the already-generated diff is preserved verbatim in logs/t6_attempt1.log; UTF-8 output resolves it without changing the draft.

Producer: `scripts/week9/t6_readme_draft.py`. Exact command: `.venv/Scripts/python.exe scripts/week9/t6_readme_draft.py --capture`. Child command: `.venv/Scripts/python.exe -u scripts/week9/t6_readme_draft.py`.

Raw terminal output:

```text
Exploratory extension designed after Official Test was used.
COMMAND: .venv/Scripts/python.exe -u scripts/week9/t6_readme_draft.py
SEED=42; documentation only; no statistical computation or model evaluation
CSV t6_prediction_tracking.csv
path,tracked,sha256_from_task0,task0_inventory_data_row
outputs/phase6/validation_predictions.csv,False,6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab,2
outputs/predictions/phase7_validation_regression_predictions.csv,False,da86cf4be3b05790db65ceb6381d75ad77fce695694e8c62a9a03dcf7493c1d0,3
outputs/predictions/official_test_predictions.csv,False,48eb85d8bda27dd6261179d839fd5377d694741c5740f94ac88029b0593393e8,4
CSV t6_commit_checks.csv
path,first_commit,first_author_date,first_committer_date,last_commit
docs/evaluation_protocol_freeze.md,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d,2026-10-03T19:24:28+07:00,2026-10-03T19:24:28+07:00,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d
scripts/phase8_evaluate_review_prioritization.py,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d,2026-10-03T19:24:28+07:00,2026-10-03T19:24:28+07:00,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d
scripts/phase9_official_test_evaluation.py,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d,2026-10-03T19:24:28+07:00,2026-10-03T19:24:28+07:00,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d
docs/data/phase9_tables/artifact_manifest.json,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d,2026-10-03T19:24:28+07:00,2026-10-03T19:24:28+07:00,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d
docs/data/phase9_tables/large_error_labels.csv,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d,2026-10-03T19:24:28+07:00,2026-10-03T19:24:28+07:00,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d
docs/data/phase9_tables/random_reference_distribution.csv,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d,2026-10-03T19:24:28+07:00,2026-10-03T19:24:28+07:00,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d
docs/data/phase9_tables/review_strategy_comparison.csv,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d,2026-10-03T19:24:28+07:00,2026-10-03T19:24:28+07:00,2c7982ed5d1183f40ea5db2a8daab4ea7ba4279d
CSV t6_mtime_sequence.csv
path,modified_utc_from_task0,task0_inventory_data_row
docs/data/phase8_tables/review_strategy_comparison.csv,2026-10-01T16:22:52.212306+00:00,16
docs/data/phase8_tables/random_reference_distribution.csv,2026-10-01T16:22:52.257898+00:00,14
docs/data/phase8_tables/large_error_labels.csv,2026-10-01T16:22:52.272121+00:00,12
docs/evaluation_protocol_freeze.md,2026-10-01T16:27:59.175393+00:00,1
scripts/phase9_official_test_evaluation.py,2026-10-01T16:44:55.498529+00:00,6
outputs/predictions/official_test_predictions.csv,2026-10-01T16:45:24.436881+00:00,4
CSV t6_headline_provenance.csv
headline,value,script,output,data_rows
Frozen Test disagreement,47/208,scripts/week9/t0_provenance.py,reports/week9/t0_metrics.csv,2
Frozen Test random mean,41.427 (41.4 rounded to one decimal),scripts/week9/t0_provenance.py,reports/week9/t0_metrics.csv,2
Frozen Test empirical p,165/1000 = 0.165,scripts/week9/t0_provenance.py,reports/week9/t0_metrics.csv,2
Frozen Test exact hypergeometric p,0.188324671369221 (0.188 rounded),scripts/week9/t0_provenance.py,reports/week9/t0_metrics.csv,2
Frozen Validation disagreement,15/69,scripts/week9/t0_provenance.py,reports/week9/t0_metrics.csv,1
Validation large errors below median,36/69; median D=0.13398965515499994,scripts/week9/t1_analysis.py,reports/week9/t1_quadrants.csv,1
"Validation both wrong, same direction",50/69,scripts/week9/t1_analysis.py,reports/week9/t1_categories.csv,1
Validation signed-error correlations,V=0.956277117218718; G=0.951854189994445,scripts/week9/t1_analysis.py,reports/week9/t1_correlations.csv,3-4
Validation D versus RF error magnitude,-0.00478127282758114,scripts/week9/t1_analysis.py,reports/week9/t1_correlations.csv,1
Validation AUROC Disagreement,"0.510676119371772; CI [0.432336289152627, 0.585208476579814]",scripts/week9/t1_analysis.py,reports/week9/t1_auroc.csv,1
Validation AUROC Ridge Extremity,"0.516364472886212; CI [0.445977573758215, 0.578892042777683]",scripts/week9/t1_analysis.py,reports/week9/t1_auroc.csv,2
Validation AUROC Shortest-first,"0.511334880900098; CI [0.437914589985434, 0.582646097231079]",scripts/week9/t1_analysis.py,reports/week9/t1_auroc.csv,3
Validation A1_RF disagreement,15/69; p=0.409805547270715,scripts/week9/t2_analysis.py,reports/week9/t2_anchor.csv,2
Validation A2_Ridge disagreement,19/77; p=0.179714082645364,scripts/week9/t2_analysis.py,reports/week9/t2_anchor.csv,6
Validation A3_Both_wrong disagreement,9/51; p=0.728938261414719,scripts/week9/t2_analysis.py,reports/week9/t2_anchor.csv,10
Pooled MAE Ridge V,prompt-disjoint=0.37342443714543; ordinary KFold=0.372304940106959,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,"1,4"
Pooled MAE Ridge G,prompt-disjoint=0.463036537712484; ordinary KFold=0.461471100957794,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,"1,4"
Pooled MAE RF V,prompt-disjoint=0.372165069040496; ordinary KFold=0.371663177019517,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,"1,4"
Pooled MAE RF G,prompt-disjoint=0.455403719595917; ordinary KFold=0.454390747998969,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,"1,4"
prompt_disjoint A1_RF pooled disagreement,88/386; expected=77.362908429581; joint p=0.105,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,1
prompt_disjoint A2_Ridge pooled disagreement,93/384; expected=76.9621199683931; joint p=0.022,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,2
prompt_disjoint A3_Both_wrong pooled disagreement,44/276; expected=55.3218568770231; joint p=0.97,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,3
ordinary_KFold A1_RF pooled disagreement,86/376; expected=75.4544844738444; joint p=0.087,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,4
ordinary_KFold A2_Ridge pooled disagreement,93/383; expected=76.8607857504051; joint p=0.013,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,5
ordinary_KFold A3_Both_wrong pooled disagreement,40/271; expected=54.384438757082; joint p=0.993,scripts/week9/t3_evaluate.py,reports/week9/t3_summary.csv,6
CSV t6_output_hashes.csv
path,sha256
reports/week9/t6_README.diff,1a14ebd33e8a5582534edcdb5ab4434337373bb30f407b14c29dd8368c7948ce
reports/week9/t6_gitignore.diff,ce3cad676392acb0594389dafbda96ed75d7b42837b13a62e2a6424c22b1bd54
reports/week9/t6_README_proposed.md,f38b8263b50f57dc455401760dc0e659e197635ad9b21834cbf244f9963b36c5
reports/week9/t6_README_section.md,72872ea0496247684dea894b96843acf605b5e7d81b1df009de93b2da23e3510
reports/week9/t6_headline_provenance.csv,dd46eb1dfef2d4b1826e85b6ed1d56d4e696bc15ce2026b0aa0a1cfc9418aff9
reports/week9/t6_prediction_tracking.csv,b49744746df1df42f73e1b5580a1165335913ac0fb9da1dd5ccaa06b212dc01e
reports/week9/t6_commit_checks.csv,2ff5b577d5e07db1428f0a3a3cb679fca9ecbe390717e874e2a864174629abd9
reports/week9/t6_mtime_sequence.csv,6f5c71dcf8bce9c53d35349b7709c24bf3762c9eb3bd3d14acf5230b1f564f6b
reports/week9/t6_sources.csv,2daf84f7d04afb1dc31d352492a80e3b26aa32a78fa28b31f7ff4c7edd3b6929
CHECK README.md preserved byte-for-byte; proposed text and full diff only; no Git config change, staging, commit or push; no Official Test file opened
STATUS: documentation draft complete with explicit Task 0 chronology and Task 4 full-prompt limitations. Existing README is unchanged; .gitignore change is applied as expressly requested.
FULL_GITIGNORE_DIFF
diff --git a/.gitignore b/.gitignore
index 6f37fab..adc88af 100644
--- a/.gitignore
+++ b/.gitignore
@@ -136,4 +136,10 @@ mlruns/
 scratch/
 *.parquet
 
+# Private Week 9 reading workbook and text-bearing build/preview files
+/reports/week9/t4_reading_sheet.xlsx
+/reports/week9/t4_private/
+# Local junction to the bundled spreadsheet runtime (not project dependencies)
+/scripts/week9/node_modules/
+
 
FULL_README_PROPOSED_DIFF
--- a/README.md
+++ b/README.md
@@ -12,6 +12,87 @@
 RF Official Test MAE is 0.364197 for Vocabulary and 0.433587 for Grammar. At Top-20%, disagreement captured 47/208 large RF errors (22.596%). It had the highest observed capture among tested strategies, but empirical one-sided p=.165 does not establish statistical superiority over random. Disagreement is a ranking signal, not calibrated confidence or error probability.
 
 Top-20% means **review first**. The remaining essays also require teacher grading; the teacher retains all official grading authority. ELLIPSE results do not establish validity for HANU; local validation and domain adaptation would be required.
+
+## Current status & result provenance
+
+Week 9 Tasks 0–5 have produced their computational deliverables. Task 0 remains PARTIAL because first Test access and edit chronology cannot be established. Task 4 remains PARTIAL for authoritative full assignment wording: only released short prompt names are available. The fixed reading workbook is prepared and manual reading is in progress; no human judgements have been filled. Tasks 1–3 and the descriptive Task 5 table are complete. Task 6 is a documentation draft. See [Week 9 evidence](reports/week9/RESULTS_week9.md), [reading-sheet checks](reports/week9/t4_selection_check.csv), and [descriptive group captures](reports/week9/t5_fairness.csv).
+
+The primary frozen RF-anchor result does not demonstrate that disagreement is better than random. The original ranking/draw implementation is `scripts/phase9_official_test_evaluation.py` with `src/mla_project/evaluation/phase8.py`; Task 0 reproduces its saved-prediction results without retraining.
+
+### Freeze and chronology limitations
+
+The [protocol](docs/evaluation_protocol_freeze.md) states that it was frozen on **2026-10-01**, after the primary Validation evaluation and before Test access. Its statement and filesystem mtimes are weak evidence, not proof of execution order. Task 0 recorded this UTC mtime sequence:
+
+| Artifact | Filesystem mtime UTC, recorded by Task 0 |
+|---|---|
+| `docs/data/phase8_tables/review_strategy_comparison.csv` | `2026-10-01T16:22:52.212306+00:00` |
+| `docs/data/phase8_tables/random_reference_distribution.csv` | `2026-10-01T16:22:52.257898+00:00` |
+| `docs/data/phase8_tables/large_error_labels.csv` | `2026-10-01T16:22:52.272121+00:00` |
+| `docs/evaluation_protocol_freeze.md` | `2026-10-01T16:27:59.175393+00:00` |
+| `scripts/phase9_official_test_evaluation.py` | `2026-10-01T16:44:55.498529+00:00` |
+| `outputs/predictions/official_test_predictions.csv` | `2026-10-01T16:45:24.436881+00:00` |
+
+The Validation result tables precede the protocol mtime; the Test script and saved Test predictions follow it. Filesystem clocks, copying and later edits can change mtimes. The first Test evaluation date cannot be established from these timestamps. Source: [Task 0 inventory](reports/week9/t0_inventory.csv) and [provenance limitations](reports/week9/t0_provenance.md).
+
+The frozen evaluation code, protocol and **tracked Test result tables** first appear together in commit `2c7982e` (`2026-10-03T19:24:28+07:00`, both author and committer date). Git therefore cannot establish their order before that snapshot. The saved prediction CSVs listed below never entered Git; they are excluded from this statement about tracked artifacts. Source: [commit checks from the Task 0 inventory](reports/week9/t6_commit_checks.csv).
+
+### Retrospective and exploratory analyses
+
+Week 8 additions prepared after Test access—rater agreement, max-versus-mean disagreement sensitivity, prompt-length descriptions and the fairness table—are exploratory. See `scripts/post_midterm_teacher_analysis.py`, `docs/data/post_midterm/` and [teacher-feedback results](docs/post_midterm/teacher_feedback_results.md). All Week 9 tasks were designed after Test was used and are retrospective/exploratory work; Task 0 is a provenance reproduction rather than new confirmatory evidence. Task 3 is explicitly labelled **“Exploratory extension designed after Official Test was used.”** Exact access chronology remains unresolved.
+
+All declared anchor results are retained. A2 derives its error label from Ridge; Ridge Extremity therefore shares the label-generating model. Under A1, RF is both the anchor and part of disagreement. These dependencies and the exploratory design must accompany the results. No anchor, threshold, model setting or ranking was selected on a new Test evaluation.
+
+### Eligible population
+
+The existing rule is `privacy_review_status == "not_flagged"` (`configs/phase6_training.yaml`, lines 1–3; `src/mla_project/pipelines/training_pipeline.py`, lines 72–73 and 127). It excludes both `flagged_by_rater` and `unresolved_raw_id_link`. Development has `3,911 − 99 = 3,812` eligible essays: `3,128 − 78 = 3,050` model-train and `783 − 21 = 762` Validation. All 44 normalized prompt groups remain. Eligible Validation IDs equal the saved prediction IDs exactly; train IDs and fold assignments match the saved OOF table. [Eligibility evidence](reports/week9/t3_eligibility_counts.csv), [exclusion reasons](reports/week9/t3_eligibility_reasons.csv), [ID checks](reports/week9/t3_eligibility_checks.csv).
+
+The frozen eligible Test population is **2,518**, as reproduced in [Task 0 metrics, Test row](reports/week9/t0_metrics.csv). No new Test evaluation was used for the later Week 9 analyses.
+
+### Headline numbers and their producers
+
+Values below are displayed to at most 15 significant digits unless a rounding is explicitly labelled; full precision, explicit derived-metric arithmetic and raw terminal evidence are in the linked outputs and [Week 9 results](reports/week9/RESULTS_week9.md). CSV row numbers count data rows, excluding headers.
+
+| Headline | Value | Producing script | Output and data row(s) |
+|---|---|---|---|
+| Frozen Test disagreement | 47/208 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
+| Frozen Test random mean | 41.427 (41.4 rounded to one decimal) | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
+| Frozen Test empirical p | 165/1000 = 0.165 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
+| Frozen Test exact hypergeometric p | 0.188324671369221 (0.188 rounded) | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 2 |
+| Frozen Validation disagreement | 15/69 | `scripts/week9/t0_provenance.py` | `reports/week9/t0_metrics.csv`, row(s) 1 |
+| Validation large errors below median | 36/69; median D=0.13398965515499994 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_quadrants.csv`, row(s) 1 |
+| Validation both wrong, same direction | 50/69 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_categories.csv`, row(s) 1 |
+| Validation signed-error correlations | V=0.956277117218718; G=0.951854189994445 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_correlations.csv`, row(s) 3-4 |
+| Validation D versus RF error magnitude | -0.00478127282758114 | `scripts/week9/t1_analysis.py` | `reports/week9/t1_correlations.csv`, row(s) 1 |
+| Validation AUROC Disagreement | 0.510676119371772; CI [0.432336289152627, 0.585208476579814] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 1 |
+| Validation AUROC Ridge Extremity | 0.516364472886212; CI [0.445977573758215, 0.578892042777683] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 2 |
+| Validation AUROC Shortest-first | 0.511334880900098; CI [0.437914589985434, 0.582646097231079] | `scripts/week9/t1_analysis.py` | `reports/week9/t1_auroc.csv`, row(s) 3 |
+| Validation A1_RF disagreement | 15/69; p=0.409805547270715 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 2 |
+| Validation A2_Ridge disagreement | 19/77; p=0.179714082645364 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 6 |
+| Validation A3_Both_wrong disagreement | 9/51; p=0.728938261414719 | `scripts/week9/t2_analysis.py` | `reports/week9/t2_anchor.csv`, row(s) 10 |
+| Pooled MAE Ridge V | prompt-disjoint=0.37342443714543; ordinary KFold=0.372304940106959 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
+| Pooled MAE Ridge G | prompt-disjoint=0.463036537712484; ordinary KFold=0.461471100957794 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
+| Pooled MAE RF V | prompt-disjoint=0.372165069040496; ordinary KFold=0.371663177019517 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
+| Pooled MAE RF G | prompt-disjoint=0.455403719595917; ordinary KFold=0.454390747998969 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1,4 |
+| prompt_disjoint A1_RF pooled disagreement | 88/386; expected=77.362908429581; joint p=0.105 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 1 |
+| prompt_disjoint A2_Ridge pooled disagreement | 93/384; expected=76.9621199683931; joint p=0.022 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 2 |
+| prompt_disjoint A3_Both_wrong pooled disagreement | 44/276; expected=55.3218568770231; joint p=0.97 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 3 |
+| ordinary_KFold A1_RF pooled disagreement | 86/376; expected=75.4544844738444; joint p=0.087 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 4 |
+| ordinary_KFold A2_Ridge pooled disagreement | 93/383; expected=76.8607857504051; joint p=0.013 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 5 |
+| ordinary_KFold A3_Both_wrong pooled disagreement | 40/271; expected=54.384438757082; joint p=0.993 | `scripts/week9/t3_evaluate.py` | `reports/week9/t3_summary.csv`, row(s) 6 |
+
+### Local artifacts and replication limits
+
+The following prediction CSVs inventoried in Task 0 are **not tracked in Git**. Hashes are copied from that saved inventory, including the Test hash; Task 6 does not reopen Test predictions.
+
+| Local prediction CSV | SHA-256 recorded in Task 0 |
+|---|---|
+| `outputs/phase6/validation_predictions.csv` | `6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab` |
+| `outputs/predictions/phase7_validation_regression_predictions.csv` | `da86cf4be3b05790db65ceb6381d75ad77fce695694e8c62a9a03dcf7493c1d0` |
+| `outputs/predictions/official_test_predictions.csv` | `48eb85d8bda27dd6261179d839fd5377d694741c5740f94ac88029b0593393e8` |
+
+Source: [Task 0 artifact inventory](reports/week9/t0_inventory.csv) and [current Git-index checks](reports/week9/t6_prediction_tracking.csv). The repository alone does not reproduce the Test numbers: the approved private data and saved prediction artifacts must also be supplied and checked against their hashes. An identical rerun of local artifacts checks reproducibility within this environment; a public repository is **not an independent replication**. Independent replication requires a separate execution and audit of the data, split, code and provenance.
+
+The student-text reading workbook and its private intermediates/previews are excluded by `.gitignore`. The original manual sample remains unchanged.
 
 ## Data and reproducibility
 
```

[src: reports/week9/logs/t6_run1.log exact lines; each CSV block names its source file and data rows exclude headers]

Fresh-process output hashes:

```text
RUN1_SHA256=2f005afff1444e154cc6b1b2e29955a7b4315b07e6b4f2afa1d339a27c265cd0
RUN2_SHA256=2f005afff1444e154cc6b1b2e29955a7b4315b07e6b4f2afa1d339a27c265cd0
IDENTICAL_RAW_OUTPUT=True
```

[src: reports/week9/logs/t6.log hash lines]


## Week 9b — exploratory development/Validation diagnosis

Producer: `scripts/week9b/diagnose.py`; command: `.venv/Scripts/python.exe -u scripts/week9b/diagnose.py --append`. No Test input is used. The error-model results have the second-stage cross-fitting limitation printed below. Existing report bytes are preserved by opening in append-only mode.

```text
EXPLORATORY ONLY; development and Validation; seed=42; no search; no frozen-model fitting.
L=max(abs(y_V-RF_V),abs(y_G-RF_G))>=1; D=max(abs(RF_V-Ridge_V),abs(RF_G-Ridge_G)); k=ceil(.20*N); ties=essay_id string ascending.
FROZEN_MODEL_VALIDATION max_abs_saved_prediction_difference={"random_forest_grammar": 4.999112235282155e-12, "random_forest_vocabulary": 4.988454094245753e-12, "ridge_grammar": 4.988010005035903e-12, "ridge_vocabulary": 4.998668146072305e-12}
RIDGE_TRAIN_CENTERS n=3050; recomputed from frozen Ridge predictions={"grammar": 3.124225726952784, "vocabulary": 3.26941940240918}
STEP1A anchors
anchor,count,share_of_RF_K
A1 RF,69,69/69=1
A2 Ridge,77,77/69=1.1159420289855073
A3 both,51,51/69=0.73913043478260865
union,95,95/69=1.3768115942028984
STEP1B D population median=0.13398965515499994; below means strict <; all shares within group unless labelled /K.
STEP1AB partition
group,count,share_of_RF_K,median_D,D_below_population_median,D_below_0_1
RF-only (A1 minus A2),18,18/69=0.2608695652173913,0.18241118549500013,6/18=0.33333333333333331,3/18=0.16666666666666666
Ridge-only (A2 minus A1; outside K),26,26/69=0.37681159420289856,0.18070331967000008,7/26=0.26923076923076922,3/26=0.11538461538461539
both (A3),51,51/69=0.73913043478260865,0.11270482242000002,30/51=0.58823529411764708,24/51=0.47058823529411764
PARTITION RF_K=18+51=69; union=18+26+51=95; Ridge-only is not part of RF K.
STEP1C direction (strict above/below; between/equality retained)
target,scope,n,above_both,below_both,between_or_equal,true_mean_group,true_mean_overall,group_mean_arithmetic,overall_mean_arithmetic
vocabulary,RF-large essays (either target),69,31/69=0.44927536231884058,36/69=0.52173913043478259,2/69=0.028985507246376812,3.1956521739130435,3.2178477690288716,220.5/69,2452/762
vocabulary,RF-large on this target,34,15/34=0.44117647058823528,19/34=0.55882352941176472,0/34=0,3.1617647058823528,3.2178477690288716,107.5/34,2452/762
grammar,RF-large essays (either target),69,31/69=0.44927536231884058,37/69=0.53623188405797106,1/69=0.014492753623188406,3.0652173913043477,3.0203412073490812,211.5/69,2301.5/762
grammar,RF-large on this target,47,23/47=0.48936170212765956,23/47=0.48936170212765956,1/47=0.021276595744680851,3.0957446808510638,3.0203412073490812,145.5/47,2301.5/762
STEP1D fixed D cutoff
N,K,k,kth_D,caught_by_D,below_cutoff,large_equal_cutoff,large_above_cutoff,eligible_large_at_or_above,optimistic_cap_within_cutoff,capture
762,69,153,0.20932248053000002,15,54/69=0.78260869565217395,0,15,15,15,15/69=0.21739130434782608
CUTOFF arithmetic: 69-54=15 large errors at/above cutoff; upper bound=min(153,15)=15; fixed D ranking caught=15; excluded=54/69=0.78260869565217395. Below-cutoff exclusion applies to this fixed ranking/budget, not an arbitrary replacement signal.
STEP2 Validation signals
signal,N,K,k,caught,capture,expected_random,expected_arithmetic,p,p_formula
Disagreement,762,69,153,15,15/69=0.21739130434782608,13.854330708661417,153*69/762=13.854330708661417,0.40980554727071455,"hypergeom.sf(14,762,69,153)"
RF tree std (ddof=0; max targets),762,69,153,25,25/69=0.36231884057971014,13.854330708661417,153*69/762=13.854330708661417,0.00077659032543159505,"hypergeom.sf(24,762,69,153)"
RF extremity vs Ridge-train medians,762,69,153,11,11/69=0.15942028985507245,13.854330708661417,153*69/762=13.854330708661417,0.85573731111227214,"hypergeom.sf(10,762,69,153)"
Shortest-first,762,69,153,15,15/69=0.21739130434782608,13.854330708661417,153*69/762=13.854330708661417,0.40980554727071455,"hypergeom.sf(14,762,69,153)"
Longest-first,762,69,153,12,12/69=0.17391304347826086,13.854330708661417,153*69/762=13.854330708661417,0.76723165097323176,"hypergeom.sf(11,762,69,153)"
STEP3 GroupKFold(5) error-model folds
fold,training_n,heldout_n,overlapping_prompts
1,3043,769,0
2,3044,768,0
3,3051,761,0
4,3067,745,0
5,3043,769,0
STEP3 saved-base-OOF exploratory error model
signal,N,K,k,caught,capture,expected_random,expected_arithmetic,p,p_formula,AUROC,CI_low,CI_high,bootstrap_resamples,valid_resamples,skipped_resamples
Error-model OOF; pooled global top20%,3812,386,763,91,91/386=0.23575129533678757,77.260755508919203,763*386/3812=77.260755508919203,0.039586256097498329,"hypergeom.sf(90,3812,386,763)",0.57458886479194449,0.54682217212938722,0.60245139101102596,2000,2000,0
STEP3 BUDGET: concatenate 5 meta-heldout score sets, then global k=ceil(.20*3812)=763; hypergeometric p uses that global uniform-selection reference.
STEP3 LIMITATION: this is second-stage GroupKFold on existing base OOF predictions, not fully nested cross-fitting. Base models generating meta-training rows can have seen the meta-heldout groups. Therefore this error-model result is potentially optimistic and is not an unbiased estimate for unseen prompts. Fully nested evaluation would require refitting base models and was not performed.
BOOTSTRAP: 2000 ordinary essay resamples with replacement, seed=42, percentile 95% CI; does not account for prompt clustering or cross-fitting dependence.
STEP2 p<0.05 (uncorrected multiple exploratory comparisons): ['RF tree std (ddof=0; max targets)']
STEP3 nominal p<0.05=True; subject to the nested-cross-fitting limitation above.
READ_AUDIT data/05_model_features/development_features_with_targets.csv SHA256=cafb1bca27423e0a8b6fb2d282fb7bd87fb703fc637a3a15778855caf0817a5b
READ_AUDIT outputs/phase6/artifact_manifest.json SHA256=41b7a59e78636eb52c3e0ea3a0a5d9e91a399adaa93126ef366a5fbcdfd3ea25
READ_AUDIT outputs/phase6/feature_schema.json SHA256=77204d8b647522a497e459ce797fc1a433e0e5547993a9ddf83af5d8273ab620
READ_AUDIT outputs/phase6/random_forest_grammar.joblib SHA256=bc285a202de126247240982696ca94c16dbee82bf15906d8e75ebdf4405a8f91
READ_AUDIT outputs/phase6/random_forest_vocabulary.joblib SHA256=899e9283e2eb01b4df6913eadd6cf8a4a823df0298ddfe820d14ba5912ffe7be
READ_AUDIT outputs/phase6/ridge_grammar.joblib SHA256=812885caab21dac6508835c83dc91de75b23d622577ba15a8e37e207e59b085f
READ_AUDIT outputs/phase6/ridge_vocabulary.joblib SHA256=14591a1822ffa4fc7c9006a5abd270928401721739bea3f9fe5a76852780ef64
READ_AUDIT outputs/phase6/validation_predictions.csv SHA256=6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
READ_AUDIT reports/week9/t3_heldout_predictions.csv SHA256=15cedfabd362b0b956084fcf3cbda1ef1c502ed6979755c19274cf22d55c64c9
READ_GUARD artifact_reads=10; allowlisted_only=True; blocked_attempts=0; source_hashes_unchanged=True; no Test file opened.
```


## Week 9b — RF tree spread on held-out development prompts

Exploratory development-only GroupKFold(5) evaluation. Producer: `scripts/week9b/tree_spread_oof.py`; command: `.venv/Scripts/python.exe -u scripts/week9b/tree_spread_oof.py --append`. No Test prediction or label file was opened.

```text
EXPLORATORY development only; seed=42; no search; models refitted within folds; no frozen artifacts changed.
VERSIONS Python=3.14.5; numpy=2.4.6; pandas=2.3.3; scipy=1.18.1; sklearn=1.9.1
PARAMETERS RF trees=300; max_features=sqrt; max_depth=10; min_samples_leaf V=2,G=5; random_state=42; n_jobs=1. Ridge alpha V=100,G=0.1; train-only median imputation; Ridge train-only StandardScaler.
DEFINITIONS tree_std=max(target population tree std,ddof=0); D=max(abs(RF-Ridge)); RF_error=max(abs(y-RF)); L=RF_error>=1; k=ceil(.20*n_fold); score descending, essay_id string ascending.
FIT_COMPLETE fold=1; training_n=3043; heldout_n=769; K=73; k=ceil(.20*769)=154; matching_saved_prompt_composition=True
FIT_COMPLETE fold=2; training_n=3044; heldout_n=768; K=88; k=ceil(.20*768)=154; matching_saved_prompt_composition=True
FIT_COMPLETE fold=3; training_n=3051; heldout_n=761; K=75; k=ceil(.20*761)=153; matching_saved_prompt_composition=True
FIT_COMPLETE fold=4; training_n=3067; heldout_n=745; K=76; k=ceil(.20*745)=149; matching_saved_prompt_composition=True
FIT_COMPLETE fold=5; training_n=3043; heldout_n=769; K=74; k=ceil(.20*769)=154; matching_saved_prompt_composition=True
FOLD_CHECKS
fold,train_n,n,heldout_prompts,overlapping_prompts,matches_t3_fold_composition,heldout_id_sha256
1,3043,769,9,0,True,5cedcbd4b839308e20e09e066bcf38a53c82f98d43c5ab0490ee2f1273f866f9
2,3044,768,9,0,True,7ecc3d39eeae833ab6e1b0e645e7f464d2237d67f646f4a536510945b8a757ea
3,3051,761,9,0,True,4f8ea16e980b6ef933a1782cea40427d41b622692972bad93a9e9b8d25a7f105
4,3067,745,8,0,True,ee91755ec2a43b3de0af4962883212bda66beec7a0317eba003439f4e7692593
5,3043,769,9,0,True,49ac62d22682d6b16b7e5f0c76ae4fcd0bf3a8783bf7df0d0c66c2f2ef0b5d5e
CAPTURE_METRICS (pooled selections sum fold queues; no global reranking)
scope,signal,n,K,k,caught,capture,expected,expected_arithmetic,exact_p,p_formula,global_formula_p,global_formula,global_expected
fold1,tree_std,769,73,154,21,21/73=0.28767123287671231,14.618985695708712,154*73/769=14.618985695708712,0.039028039750596738,"hypergeom.sf(20,769,73,154)",,,
fold1,D,769,73,154,15,15/73=0.20547945205479451,14.618985695708712,154*73/769=14.618985695708712,0.50454768821846441,"hypergeom.sf(14,769,73,154)",,,
fold2,tree_std,768,88,154,20,20/88=0.22727272727272727,17.645833333333332,154*88/768=17.645833333333332,0.29455430308993114,"hypergeom.sf(19,768,88,154)",,,
fold2,D,768,88,154,22,22/88=0.25,17.645833333333332,154*88/768=17.645833333333332,0.13838981922873914,"hypergeom.sf(21,768,88,154)",,,
fold3,tree_std,761,75,153,22,22/75=0.29333333333333333,15.078843626806833,153*75/761=15.078843626806833,0.029135245039491456,"hypergeom.sf(21,761,75,153)",,,
fold3,D,761,75,153,20,20/75=0.26666666666666666,15.078843626806833,153*75/761=15.078843626806833,0.092467509248828822,"hypergeom.sf(19,761,75,153)",,,
fold4,tree_std,745,76,149,19,19/76=0.25,15.199999999999999,149*76/745=15.199999999999999,0.15874981948373659,"hypergeom.sf(18,745,76,149)",,,
fold4,D,745,76,149,17,17/76=0.22368421052631579,15.199999999999999,149*76/745=15.199999999999999,0.33962947986356462,"hypergeom.sf(16,745,76,149)",,,
fold5,tree_std,769,74,154,14,14/74=0.1891891891891892,14.819245773732119,154*74/769=14.819245773732119,0.64862117609057512,"hypergeom.sf(13,769,74,154)",,,
fold5,D,769,74,154,14,14/74=0.1891891891891892,14.819245773732119,154*74/769=14.819245773732119,0.64862117609057512,"hypergeom.sf(13,769,74,154)",,,
pooled,tree_std,3812,386,764,96,96/386=0.24870466321243523,77.362908429580997,154*73/769+154*88/768+153*75/761+149*76/745+154*74/769=77.362908429580997,0.0085360709265048448,P(sum independent fold Hypergeom>= 96); exact PMF convolution,0.0085190843457175168,"hypergeom.sf(95,3812,386,764); different global-uniform null",77.362014690451204
pooled,D,3812,386,764,88,88/386=0.22797927461139897,77.362908429580997,154*73/769+154*88/768+153*75/761+149*76/745+154*74/769=77.362908429580997,0.088356842158423293,P(sum independent fold Hypergeom>= 88); exact PMF convolution,0.088283926658051945,"hypergeom.sf(87,3812,386,764); different global-uniform null",77.362014690451204
AUROC (ordinary essay bootstrap, 2000 resamples, seed=42, percentile 95% CI)
scope,signal,AUROC,CI_low,CI_high,arithmetic,bootstrap_resamples,valid_resamples,skipped_resamples
fold1,tree_std,0.55176350181073852,0.47405735724222359,0.62404246494249382,28034/(73*696)=0.55176350181073852,2000,2000,0
fold1,D,0.49584711069122972,0.42262485265270316,0.56788093410242457,25193/(73*696)=0.49584711069122972,2000,2000,0
fold2,tree_std,0.53892045454545456,0.47592265794361727,0.60711056187477375,32249/(88*680)=0.53892045454545456,2000,2000,0
fold2,D,0.50132018716577542,0.4328475091811928,0.56992016939351497,29999/(88*680)=0.50132018716577542,2000,2000,0
fold3,tree_std,0.58573372206025265,0.51635548512559026,0.65081841549861774,30136/(75*686)=0.58573372206025265,2000,2000,0
fold3,D,0.55317784256559765,0.47966248145149076,0.62607292304551942,28461/(75*686)=0.55317784256559765,2000,2000,0
fold4,tree_std,0.53361261899142476,0.45878115078236625,0.60862206375758909,27131/(76*669)=0.53361261899142476,2000,2000,0
fold4,D,0.53221619070096771,0.46144934998056508,0.60419087950505967,27060/(76*669)=0.53221619070096771,2000,2000,0
fold5,tree_std,0.53799338907252581,0.46908624021854195,0.60484568515497839,27669/(74*695)=0.53799338907252581,2000,2000,0
fold5,D,0.50056387322574369,0.43159797066155786,0.56938176754458847,25744/(74*695)=0.50056387322574369,2000,2000,0
pooled,tree_std,0.54705558529864584,0.5152834023276035,0.57783614919452653,723446/(386*3426)=0.54705558529864584,2000,2000,0
pooled,D,0.51630929587518792,0.48505673888990986,0.54778324074339224,682786/(386*3426)=0.51630929587518792,2000,2000,0
SPEARMAN (average ranks; RF_error=max target absolute RF error)
scope,n,x,y,spearman_rho
fold1,769,tree_std,RF_error,0.07805731532771519
fold1,769,tree_std,D,0.1975448011838617
fold1,769,tree_std,word_count,-0.093797300507328665
fold2,768,tree_std,RF_error,0.087713310815278472
fold2,768,tree_std,D,0.12891775371594527
fold2,768,tree_std,word_count,-0.070108370449256135
fold3,761,tree_std,RF_error,0.050422345453585017
fold3,761,tree_std,D,0.28339693066411514
fold3,761,tree_std,word_count,-0.15636512761796706
fold4,745,tree_std,RF_error,0.032361263391040736
fold4,745,tree_std,D,0.12107030234716495
fold4,745,tree_std,word_count,-0.24256257905075004
fold5,769,tree_std,RF_error,0.012511373135966767
fold5,769,tree_std,D,0.12595705862732848
fold5,769,tree_std,word_count,-0.11242632132124583
pooled,3812,tree_std,RF_error,0.050255134725666006
pooled,3812,tree_std,D,0.17213548243066826
pooled,3812,tree_std,word_count,-0.13436664407050286
POOLING: k=sum ceil(.20*n_fold), expected=sum(k_fold*K_fold/n_fold). Pooled exact p is the convolution of the five fold-specific hypergeometric distributions. The additional pooled global-formula p ignores the fixed fold quotas and is labelled separately.
LIMITATIONS: exploratory unadjusted comparisons; OOF models share training rows, so fold independence is a reference-null assumption. Essay bootstrap does not account for prompt clustering or training dependence. Marginal length correlation cannot establish signal independence from length.
READ_AUDIT outputs/phase6/feature_schema.json SHA256=77204d8b647522a497e459ce797fc1a433e0e5547993a9ddf83af5d8273ab620
READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
READ_AUDIT reports/week9/t3_fold_composition.csv SHA256=de596a84028e42b8aa0c605c523ee98eef87b6b74127a63b0c8e822d0e0629ea
READ_GUARD artifact_reads=3; allowlisted_only=True; blocked_attempts=0; no Test prediction/label file opened; inputs_unchanged=True
ALL_NUMBERS_PRINTED=True
```
