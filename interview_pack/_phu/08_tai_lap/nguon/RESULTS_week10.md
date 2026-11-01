# Nguồn: reports/week10/RESULTS_week10.md
SHA256 toàn file: 6c6d346cfd8db7615e421b2ecf6baa4767466920f61adfae403d410cc3e20801

Trích chọn metadata/số liệu; không chứa bài luận.

1410: 
1411: | Sample | Tool | Spearman [95% CI] | Pearson [95% CI] | Reader mean | Tool mean | Absolute mean gap |
1412: |---|---|---|---|---|---|---|
1413: | pooled68 | LT_estimate | 0.607703 [0.423207, 0.761990] | 0.523958 [0.315931, 0.735525] | 8.323529 | 1.323504 | 7.000025 |
1414: | pooled68 | edits_grammar | 0.798451 [0.646819, 0.891324] | 0.735506 [0.592253, 0.851524] | 8.323529 | 14.323529 | 6.000000 |
1415: | random36 | LT_estimate | 0.731912 [0.494983, 0.877675] | 0.721492 [0.484700, 0.869605] | 7.333333 | 1.236789 | 6.096544 |
1416: | random36 | edits_grammar | 0.760366 [0.506861, 0.903222] | 0.714785 [0.423824, 0.873741] | 7.333333 | 14.333333 | 7.000000 |
1417: | week9_32 | LT_estimate | 0.489694 [0.162796, 0.733594] | 0.408764 [0.113733, 0.709531] | 9.437500 | 1.421059 | 8.016441 |
1418: | week9_32 | edits_grammar | 0.877230 [0.714853, 0.945867] | 0.889981 [0.778704, 0.949244] | 9.437500 | 14.312500 | 4.875000 |
1419: ACCEPTANCE {"accepted": true, "arithmetic": "(0.79845148650510833>0.60770288365497704) AND (6<7.0000249649968751) = True", "condition_i": true, "condition_ii": true, "definition": "edits_grammar is PRIMARY; edits_all is sensitivity only; pooled 68"}
1420: RANDOM_BAND {"band": "<2.5", "n": 12, "reader_mean": 10.75, "LT_estimate_mean": 2.589405095144, "edits_grammar_mean": 26.5, "arithmetic": {"reader": "129/12=10.75", "LT_estimate": "31.072861141728001/12=2.589405095144", "edits_grammar": "318/12=26.5"}}
1421: RANDOM_BAND {"band": "2.5-4.0", "n": 12, "reader_mean": 7.0, "LT_estimate_mean": 0.8890443055925, "edits_grammar_mean": 10.916666666666666, "arithmetic": {"reader": "84/12=7", "LT_estimate": "10.668531667110001/12=0.88904430559250003", "edits_grammar": "131/12=10.916666666666666"}}
1422: RANDOM_BAND {"band": ">4.0", "n": 12, "reader_mean": 4.25, "LT_estimate_mean": 0.23191808529174998, "edits_grammar_mean": 5.583333333333333, "arithmetic": {"reader": "51/12=4.25", "LT_estimate": "2.7830170235009999/12=0.23191808529174998", "edits_grammar": "67/12=5.583333333333333"}}
1423: BOOTSTRAP paired ordinary essay resamples, default_rng(42), reset per group; 2000; percentile linear 95%; tied ranks recalculated on every draw; undefined correlations skipped and counted. No prompt clustering. No OOF model was fitted in Part A; downstream OOF CIs, if later run, condition on fitted models.
1424: READ_GUARD allowlisted development inputs only; offline inference; no Test or combined corpus opened; no essay text printed; no fits
1425: ```
1426: 
1427: 
1428: Part A evidence-only interpretation: the pre-registered pooled criterion is met: Spearman(new, reader)=0.7984514865 > Spearman(LT estimate, reader)=0.6077028837, and |mean(new)-mean(reader)|=|974/68-566/68|=6 < |89.9983023802125/68-566/68|=7.000024965. The new counter overcounts the reader mean (14.323529 vs 8.323529), while LT undercounts (1.323504). The random36 subset does not meet both conditions: Spearman is higher (0.760366 vs 0.731912), but its mean gap is worse (7 vs 6.096544). The week9_32 subset meets both (Spearman 0.877230 vs 0.489694; gap 4.875 vs 8.016441). This is an exploratory, pooled point-estimate criterion, not evidence that improvement holds on every sample or is statistically significant. Bootstrap intervals use essays, not prompt clusters. No OOF models were fitted; the limitation that downstream CIs condition on fitted OOF models remains applicable to any later Part B. Part B and full-development counting were not executed.
1429: 
1430: Verification: 68/68 essays, 36 random + 32 week9, unique IDs, zero failures, text-free records; 2,000/2,000 valid bootstrap draws for each reported correlation; correlations independently checked with SciPy. The previous report prefix is byte-for-byte preserved (SHA256 02f00bd847dd1e74c7d607e1d410065119c3cbf541c0c11a73c688b93b723b76). Restricted audit grep command: `rg -n -i "^READ_AUDIT .*(test|full_clean_corpus|combined)" reports/week10/gec_part_a_run.log reports/week10/gec_part_a_analysis.log`; zero matches. This corroborates the Python read guard and is not a universal OS access proof. Additional READ_AUDIT for verification: RESULTS_week10.md; gec_part_a_report_prefix.json; gec_part_a_statistics.json; gec_part_a_counts.jsonl; gec_part_a_run.log; gec_part_a_analysis.log; gec_part_a_68.csv (all under reports/week10). Preflight code reads were scripts/week10/gec_compare.py, scripts/week10/gec_part_a.py and the authorized supporting scripts/week10/reading_compare.py.
1680: 
1681: B2 concise result tables (raw outputs and arithmetic above):
1682: 
1683: | Model | V MAE | V R2 | G MAE | G R2 |
1684: |---|---:|---:|---:|---:|
1685: | RF | 0.372165 | 0.342085 | 0.455404 | 0.342986 |
1686: | Ridge | 0.373424 | 0.342212 | 0.463037 | 0.326617 |
1687: | B1 | 0.406626 | 0.222279 | 0.506841 | 0.215785 |
1688: | B2 | 0.404448 | 0.211500 | 0.507500 | 0.204629 |
1689: 
1690: | B2 vs | Target | Spearman [95% CI] | Pearson [95% CI] |
1691: |---|---|---|---|
1692: | RF | V | 0.844016 [0.832885, 0.855088] | 0.863626 [0.855205, 0.871501] |
1693: | RF | G | 0.830739 [0.820530, 0.841014] | 0.832744 [0.823954, 0.841468] |
1694: | Ridge | V | 0.833841 [0.821715, 0.845830] | 0.854161 [0.844020, 0.863989] |
1695: | Ridge | G | 0.834488 [0.822681, 0.845617] | 0.841026 [0.829479, 0.850961] |
1696: | B1 | V | 0.940038 [0.934910, 0.944279] | 0.954289 [0.951172, 0.957170] |
1697: | B1 | G | 0.949660 [0.945834, 0.952920] | 0.952116 [0.949074, 0.954902] |
1698: 
1699: | Anchor | Signal | K | k | Caught | Expected | Exact p | AUROC [95% CI] |
1700: |---|---|---:|---:|---:|---:|---:|---|
1701: | A1_RF | D_old | 386 | 764 | 88 | 77.362908 | 0.08835684 | 0.516309 [0.484326, 0.546506] |
1702: | A1_RF | D_B1 | 386 | 764 | 81 | 77.362908 | 0.33383425 | 0.512340 [0.482408, 0.543407] |
1703: | A1_RF | D_B2 | 386 | 764 | 93 | 77.362908 | 0.02277502 | 0.546324 [0.515909, 0.576590] |
1704: | A3_RF_B2 | D_old | 217 | 764 | 42 | 43.495178 | 0.63108101 | 0.471484 [0.431389, 0.512080] |
1705: | A3_RF_B2 | D_B1 | 217 | 764 | 37 | 43.495178 | 0.89076439 | 0.467491 [0.428202, 0.506398] |
1706: | A3_RF_B2 | D_B2 | 217 | 764 | 36 | 43.495178 | 0.92120570 | 0.462336 [0.422871, 0.501789] |
1707: 
1708: | Source | Old shared-error set | Remain wrong | Both source targets error <1 |
1709: |---|---:|---:|---:|
1710: | B1 | 276 | 203 | 73 |
1711: | B2 | 276 | 191 | 85 |
1712: 
1713: Evidence-only interpretation: B2 errors are less correlated with RF and feature Ridge than 0.95 on both targets under both Pearson and Spearman; all corresponding 95% CIs lie below 0.95. B2 is not uniformly below 0.95 versus B1: Vocabulary Pearson=0.954289 [0.951172,0.957170], Grammar Pearson=0.952116 [0.949074,0.954902]; Grammar Spearman=0.949660 has CI [0.945834,0.952920]. B2 does not improve MAE/R2 over feature baselines; compared with B1, V MAE is slightly lower but both R2 values and G MAE are worse. On A1, D_B2 catches 93 versus exact random-queue expectation 77.362908, p=0.022775, AUROC=0.546324 [0.515909,0.576590]. The paired count difference versus D_old is 93-88=5, CI [-16.025,27], and paired AUC difference is 0.030015 [-0.011455,0.071975]; superiority over D_old is not established. The paired AUC difference versus D_B1 is 0.033984 [0.004509,0.063763], while the count difference 93-81=12 has CI [-5,29]. The A1 D_B2 excess-count essay-bootstrap CI [-0.374980,31.636714] includes zero despite the conditional exact random-queue p; these quantify different reference uncertainties. On the same 217 A3_RF_B2 labels, D_B2 catches only 36 versus 43.495178 expected, p=0.921206, AUROC=0.462336 [0.422871,0.501789]; it does not improve detection of these shared errors. Of the old 276 RF/Ridge shared errors, B2 remains wrong on 191 and fixes its own two targets on 85 (191+85=276), versus B1 203+73=276; B2 fixes 85-73=12 more by count. RF is still wrong on those old cases; "fixed" here refers only to the replacement source. Encoder uses native 256-token truncation and mean pooling followed by native L2 normalization; normalize_embeddings=False remains unchanged. All results are exploratory reused development; 2000 seed-42 essay-bootstrap draws condition on fitted OOF models and fixed queues, with no prompt clustering. Pooled exact p uses independent fold reference draws; OOF training sets overlap.
