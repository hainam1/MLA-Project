# Nguồn: reports/week9/RESULTS_week9.md
SHA256 toàn file: 03921a62b35e96499336c9119c3b0fb4dfa27b73788f61ad42daf73a05243f1d

Trích chọn metadata/số liệu; không chứa bài luận.

23: | Validation | 762 | 69 | 153 | 15 | 10 | 15 | 13.946 | [8, 20] | 415/1000 = 0.415 | 0.40980554727071455 | 153*69/762 = 13.854330708661417 |
24: | Test | 2518 | 208 | 504 | 37 | 43 | 47 | 41.427 | [32, 52.02499999999998] | 165/1000 = 0.165 | 0.18832467136922115 | 504*208/2518 = 41.6330420969023 |
32: ARITHMETIC Validation: random_mean=13946/1000=13.946; empirical_p=415/1000=0.415; expected=153*69/762=13.8543307087; capture=15/69=0.217391304348; exact_p=hypergeom.sf(14,762,69,153)=0.409805547271
33: ARITHMETIC Test: random_mean=41427/1000=41.427; empirical_p=165/1000=0.165; expected=504*208/2518=41.6330420969; capture=47/208=0.225961538462; exact_p=hypergeom.sf(46,2518,208,504)=0.188324671369
1403: ## Week 9b — RF tree spread on held-out development prompts
1404: 
1405: Exploratory development-only GroupKFold(5) evaluation. Producer: `scripts/week9b/tree_spread_oof.py`; command: `.venv/Scripts/python.exe -u scripts/week9b/tree_spread_oof.py --append`. No Test prediction or label file was opened.
1406: 
1407: ```text
1408: EXPLORATORY development only; seed=42; no search; models refitted within folds; no frozen artifacts changed.
1409: VERSIONS Python=3.14.5; numpy=2.4.6; pandas=2.3.3; scipy=1.18.1; sklearn=1.9.1
1410: PARAMETERS RF trees=300; max_features=sqrt; max_depth=10; min_samples_leaf V=2,G=5; random_state=42; n_jobs=1. Ridge alpha V=100,G=0.1; train-only median imputation; Ridge train-only StandardScaler.
1411: DEFINITIONS tree_std=max(target population tree std,ddof=0); D=max(abs(RF-Ridge)); RF_error=max(abs(y-RF)); L=RF_error>=1; k=ceil(.20*n_fold); score descending, essay_id string ascending.
1412: FIT_COMPLETE fold=1; training_n=3043; heldout_n=769; K=73; k=ceil(.20*769)=154; matching_saved_prompt_composition=True
1413: FIT_COMPLETE fold=2; training_n=3044; heldout_n=768; K=88; k=ceil(.20*768)=154; matching_saved_prompt_composition=True
1414: FIT_COMPLETE fold=3; training_n=3051; heldout_n=761; K=75; k=ceil(.20*761)=153; matching_saved_prompt_composition=True
1415: FIT_COMPLETE fold=4; training_n=3067; heldout_n=745; K=76; k=ceil(.20*745)=149; matching_saved_prompt_composition=True
1416: FIT_COMPLETE fold=5; training_n=3043; heldout_n=769; K=74; k=ceil(.20*769)=154; matching_saved_prompt_composition=True
1417: FOLD_CHECKS
1418: fold,train_n,n,heldout_prompts,overlapping_prompts,matches_t3_fold_composition,heldout_id_sha256
1419: 1,3043,769,9,0,True,5cedcbd4b839308e20e09e066bcf38a53c82f98d43c5ab0490ee2f1273f866f9
1420: 2,3044,768,9,0,True,7ecc3d39eeae833ab6e1b0e645e7f464d2237d67f646f4a536510945b8a757ea
1421: 3,3051,761,9,0,True,4f8ea16e980b6ef933a1782cea40427d41b622692972bad93a9e9b8d25a7f105
1422: 4,3067,745,8,0,True,ee91755ec2a43b3de0af4962883212bda66beec7a0317eba003439f4e7692593
1423: 5,3043,769,9,0,True,49ac62d22682d6b16b7e5f0c76ae4fcd0bf3a8783bf7df0d0c66c2f2ef0b5d5e
1424: CAPTURE_METRICS (pooled selections sum fold queues; no global reranking)
1425: scope,signal,n,K,k,caught,capture,expected,expected_arithmetic,exact_p,p_formula,global_formula_p,global_formula,global_expected
1426: fold1,tree_std,769,73,154,21,21/73=0.28767123287671231,14.618985695708712,154*73/769=14.618985695708712,0.039028039750596738,"hypergeom.sf(20,769,73,154)",,,
1427: fold1,D,769,73,154,15,15/73=0.20547945205479451,14.618985695708712,154*73/769=14.618985695708712,0.50454768821846441,"hypergeom.sf(14,769,73,154)",,,
1428: fold2,tree_std,768,88,154,20,20/88=0.22727272727272727,17.645833333333332,154*88/768=17.645833333333332,0.29455430308993114,"hypergeom.sf(19,768,88,154)",,,
1429: fold2,D,768,88,154,22,22/88=0.25,17.645833333333332,154*88/768=17.645833333333332,0.13838981922873914,"hypergeom.sf(21,768,88,154)",,,
1430: fold3,tree_std,761,75,153,22,22/75=0.29333333333333333,15.078843626806833,153*75/761=15.078843626806833,0.029135245039491456,"hypergeom.sf(21,761,75,153)",,,
1431: fold3,D,761,75,153,20,20/75=0.26666666666666666,15.078843626806833,153*75/761=15.078843626806833,0.092467509248828822,"hypergeom.sf(19,761,75,153)",,,
1432: fold4,tree_std,745,76,149,19,19/76=0.25,15.199999999999999,149*76/745=15.199999999999999,0.15874981948373659,"hypergeom.sf(18,745,76,149)",,,
1433: fold4,D,745,76,149,17,17/76=0.22368421052631579,15.199999999999999,149*76/745=15.199999999999999,0.33962947986356462,"hypergeom.sf(16,745,76,149)",,,
1434: fold5,tree_std,769,74,154,14,14/74=0.1891891891891892,14.819245773732119,154*74/769=14.819245773732119,0.64862117609057512,"hypergeom.sf(13,769,74,154)",,,
1435: fold5,D,769,74,154,14,14/74=0.1891891891891892,14.819245773732119,154*74/769=14.819245773732119,0.64862117609057512,"hypergeom.sf(13,769,74,154)",,,
1436: pooled,tree_std,3812,386,764,96,96/386=0.24870466321243523,77.362908429580997,154*73/769+154*88/768+153*75/761+149*76/745+154*74/769=77.362908429580997,0.0085360709265048448,P(sum independent fold Hypergeom>= 96); exact PMF convolution,0.0085190843457175168,"hypergeom.sf(95,3812,386,764); different global-uniform null",77.362014690451204
1437: pooled,D,3812,386,764,88,88/386=0.22797927461139897,77.362908429580997,154*73/769+154*88/768+153*75/761+149*76/745+154*74/769=77.362908429580997,0.088356842158423293,P(sum independent fold Hypergeom>= 88); exact PMF convolution,0.088283926658051945,"hypergeom.sf(87,3812,386,764); different global-uniform null",77.362014690451204
1438: AUROC (ordinary essay bootstrap, 2000 resamples, seed=42, percentile 95% CI)
1439: scope,signal,AUROC,CI_low,CI_high,arithmetic,bootstrap_resamples,valid_resamples,skipped_resamples
1440: fold1,tree_std,0.55176350181073852,0.47405735724222359,0.62404246494249382,28034/(73*696)=0.55176350181073852,2000,2000,0
1490: FIT_COMPLETE fold=1; n=769; k=154; matching_t3_prompt_composition=True; overlapping_prompts=0
1491: FIT_COMPLETE fold=2; n=768; k=154; matching_t3_prompt_composition=True; overlapping_prompts=0
1492: FIT_COMPLETE fold=3; n=761; k=153; matching_t3_prompt_composition=True; overlapping_prompts=0
1493: FIT_COMPLETE fold=4; n=745; k=149; matching_t3_prompt_composition=True; overlapping_prompts=0
1494: FIT_COMPLETE fold=5; n=769; k=154; matching_t3_prompt_composition=True; overlapping_prompts=0
1495: PAIRED_CAUGHT_AND_OVERLAP (A1)
1496: scope,n,K,k,caught_tree,caught_D,difference,both,only_tree,only_D,neither,arithmetic
1497: fold1,769,73,154,21,15,6,10,11,5,47,21-15=6; 11-5=6; K=10+11+5+47=73
1498: fold2,768,88,154,20,22,-2,9,11,13,55,20-22=-2; 11-13=-2; K=9+11+13+55=88
1499: fold3,761,75,153,22,20,2,9,13,11,42,22-20=2; 13-11=2; K=9+13+11+42=75
1500: fold4,745,76,149,19,17,2,7,12,10,47,19-17=2; 12-10=2; K=7+12+10+47=76
1501: fold5,769,74,154,14,14,0,8,6,6,54,14-14=0; 6-6=0; K=8+6+6+54=74
1502: pooled,3812,386,764,96,88,8,43,53,45,245,96-88=8; 53-45=8; K=43+53+45+245=386
1503: FOLD_SIGN_CHECK: report fold differences only; an exact paired permutation/sign check on five fold differences is not meaningful here (n=5); no sign-test p value computed.
1504: BOOTSTRAP_CHOICE: 44 normalised-prompt clusters sampled with replacement, 44 draws per resample, 2000 resamples, default_rng(42). Keep fold queues and scores fixed; duplicate all essays of each sampled prompt. No reranking, refitting or budget recomputation. Resampled N and caught totals can vary.
1505: PAIRED_PROMPT_CLUSTER_BOOTSTRAP (95% percentile CI; linear interpolation)
1506: metric,observed,arithmetic,CI_low,CI_high,positive_resamples,valid_resamples,skipped,share_positive,share_arithmetic,zero_resamples,negative_resamples
1507: caught_tree-caught_D,8,96-88=8,-11,27,1571,2000,0,0.78549999999999998,1571/2000=0.78549999999999998,66,363
1508: AUROC_tree-AUROC_D,0.030746289423457918,0.54705558529864584-0.51630929587518792=0.030746289423457918,-0.010705059404945169,0.077289787514988426,1845,2000,0,0.92249999999999999,1845/2000=0.92249999999999999,0,155
1509: A3_INTERPRETATION: evaluate the same whole-fold fixed queues against A3 labels (K=276); do not rank only the already-known positives, which would make capture tautological. N and per-fold budgets remain unchanged.
1510: A3_CAPTURE (same queues; pooled exact p respects fold budgets)
1511: scope,signal,n,K,k,caught,capture,expected,expected_arithmetic,exact_p,p_formula,global_formula_p,global_formula
1512: fold1,tree_std,769,52,154,16,16/52=0.30769230769230771,10.413524057217165,154*52/769=10.413524057217165,0.038462141517799482,"hypergeom.sf(15,769,52,154)",,
1513: fold1,D,769,52,154,10,10/52=0.19230769230769232,10.413524057217165,154*52/769=10.413524057217165,0.61749888441481582,"hypergeom.sf(9,769,52,154)",,
1514: fold2,tree_std,768,71,154,17,17/71=0.23943661971830985,14.236979166666666,154*71/768=14.236979166666666,0.23676089580477322,"hypergeom.sf(16,768,71,154)",,
1515: fold2,D,768,71,154,12,12/71=0.16901408450704225,14.236979166666666,154*71/768=14.236979166666666,0.80079949848094367,"hypergeom.sf(11,768,71,154)",,
1516: fold3,tree_std,761,56,153,16,16/56=0.2857142857142857,11.258869908015768,153*56/761=11.258869908015768,0.074656028198244836,"hypergeom.sf(15,761,56,153)",,
1517: fold3,D,761,56,153,9,9/56=0.16071428571428573,11.258869908015768,153*56/761=11.258869908015768,0.82989644813375862,"hypergeom.sf(8,761,56,153)",,
1518: fold4,tree_std,745,49,149,9,9/49=0.18367346938775511,9.8000000000000007,149*49/745=9.8000000000000007,0.67515080181585552,"hypergeom.sf(8,745,49,149)",,
1519: fold4,D,745,49,149,7,7/49=0.14285714285714285,9.8000000000000007,149*49/745=9.8000000000000007,0.89248187962259462,"hypergeom.sf(6,745,49,149)",,
1520: fold5,tree_std,769,48,154,7,7/48=0.14583333333333334,9.6124837451235372,154*48/769=9.6124837451235372,0.87986500917562971,"hypergeom.sf(6,769,48,154)",,
1521: fold5,D,769,48,154,6,6/48=0.125,9.6124837451235372,154*48/769=9.6124837451235372,0.94412003186099236,"hypergeom.sf(5,769,48,154)",,
1522: pooled,tree_std,3812,276,764,65,65/276=0.23550724637681159,55.321856877023137,154*52/769+154*71/768+153*56/761+149*49/745+154*48/769=55.321856877023137,0.077702897957475925,P(sum fold Hypergeom >= 65); exact convolution,0.077631873891110828,"hypergeom.sf(64,3812,276,764); global-uniform reference"
1523: pooled,D,3812,276,764,44,44/276=0.15942028985507245,55.321856877023137,154*52/769+154*71/768+153*56/761+149*49/745+154*48/769=55.321856877023137,0.97012334566057801,P(sum fold Hypergeom >= 44); exact convolution,0.97001982421249178,"hypergeom.sf(43,3812,276,764); global-uniform reference"
1524: A3_ONLY_SPEARMAN (RF_error=max target abs RF error)
1525: scope,A3_n,spearman_tree_std_RF_error
1526: fold1,52,0.071373687355929305
1527: fold2,71,0.16817572099262237
1528: fold3,56,0.13561175666438827
1529: fold4,49,-0.036530612244897953
1530: fold5,48,0.032132001736864958
1531: pooled,276,0.073057176695538018
1532: CAVEATS: exploratory comparisons; fixed-score prompt bootstrap conditions on fitted OOF models and queues, without modeling retraining variability. Shared training data induces cross-fold dependence. Share of bootstrap differences >0 is not a permutation p value. A3 membership may arise from different triggering targets for the two models.
1533: READ_AUDIT outputs/phase6/feature_schema.json SHA256=77204d8b647522a497e459ce797fc1a433e0e5547993a9ddf83af5d8273ab620
1534: READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
1535: READ_AUDIT reports/week9/t3_fold_composition.csv SHA256=de596a84028e42b8aa0c605c523ee98eef87b6b74127a63b0c8e822d0e0629ea
1536: READ_GUARD artifact_reads=3; allowlisted_only=True; blocked_attempts=0; no Test prediction/label file opened; inputs_unchanged=True
1537: ALL_NUMBERS_PRINTED=True
1538: ```
