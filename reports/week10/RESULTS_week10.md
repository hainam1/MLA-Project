# Week 10 results

## Part A: immutable signal lock

Exploratory signal; future confirmation is separate. The status sentence in the lock is retained verbatim as requested.

Written at commit `3e6f0d80e0f9228d12328f8c16d4c1f947f9ee31`.

```text
$ date -u
Mon Oct 19 05:41:03 UTC 2026
SHA256 scripts/week9b/tree_spread_oof.py ccc8524cccc50b7d78b2680428bd188cd84587c31ab6bddb9af9f006aef9546d
SHA256 reports/week9/RESULTS_week9.md 03921a62b35e96499336c9119c3b0fb4dfa27b73788f61ad42daf73a05243f1d
$ sha256sum docs/signal_lock_tree_spread.md
d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca *docs/signal_lock_tree_spread.md
```


## Part B: exploratory prediction and truth spread

Command: `.venv/Scripts/python.exe -B -u scripts/week10/spread_analysis.py`

```text
PART B: EXPLORATORY ONLY; no new confirmatory evidence; no Test prediction/label file access.
VERSIONS Python=3.14.5; numpy=2.4.6; pandas=2.3.3; scipy=1.18.1; sklearn=1.9.1
Validation: saved predictions only, no fit. Development: explicitly authorized same GroupKFold(5)-by-prompt refit as scripts/week9b/tree_spread_oof.py; predictions held only in memory, no new artifacts. Pooled OOF statistics, not fold averages.
PARAMETERS: sorted essay_id string; 14 frozen features; RF n_estimators=300,max_features=sqrt,max_depth=10,min_samples_leaf V=2/G=5,random_state=42,n_jobs=1; Ridge alpha V=100/G=0.1; training-only median imputation and Ridge StandardScaler.
METHOD: ddof=0; OLS truth~prediction includes intercept; Pearson uses centered cross-products; quantiles linear. About 0.5 is prospectively operationalized as [0.45,0.55]. No interpretation beyond numbers.
EXTREMITY: frozen Ridge medians V=3.2694194024091798, G=3.1242257269527842; frozen_max=max(abs(Ridge_V-median_V),abs(Ridge_G-median_G)); target_distance=abs(Ridge_target-median_target). Same frozen medians for both sets; no OOF recentering. Large error is joint RF max absolute error>=1. Truth bands and distance from 3 are target-specific in Part B.

SET=Validation; N=762; joint_RF_large_errors=69
SMALL_SUMMARY_TABLE (population SD; about_0_5 means 0.45<=ratio<=0.55)
target,model,n,SD_true,SD_pred,ratio,about_0_5,true_min,true_max,true_p05,true_p95,pred_min,pred_max,pred_p05,pred_p95,Pearson_r,OLS_truth_on_pred_slope
Vocabulary,Ridge,762,0.57374451585758102,0.33622241102880079,0.58601416089571889,False,1,5,2.5,4,1.6942349112299999,4.0942289057799996,2.6150591668719998,3.7111561900729999,0.55272478544273485,0.94319356480720307
Vocabulary,RF,762,0.57374451585758102,0.30978469004999171,0.53993490393011212,True,1,5,2.5,4,2.3497676679300001,4.1913925567600003,2.7193409021234998,3.7267624234099999,0.54779531590676678,1.0145580734259625
Grammar,Ridge,762,0.68152861158350608,0.40216739622981246,0.59009613007352935,False,1,5,2,4,0.774876419825,3.8689403442899999,2.2809318303150001,3.5498378108490001,0.56971526190491972,0.96546178303851937
Grammar,RF,762,0.68152861158350608,0.38816174016620841,0.56954577338188228,False,1,5,2,4,2.1730867782400001,4.0458362177499998,2.3850464076584998,3.6233655782339995,0.58177833047836458,1.0214777418570717
ARITHMETIC (centered sums; OLS includes an intercept)
target,model,SD_true,SD_pred,ratio,Pearson,slope,true_range,pred_range
Vocabulary,Ridge,sqrt(250.83727034120733/762)=0.57374451585758102,sqrt(86.140678374651131/762)=0.33622241102880079,0.33622241102880079/0.57374451585758102=0.58601416089571889,81.247333511097949/sqrt(250.83727034120733*86.140678374651131)=0.55272478544273485,81.247333511097949/86.140678374651131=0.94319356480720307,5-1=4,4.0942289057799996-1.6942349112299999=2.39999399455
Vocabulary,RF,sqrt(250.83727034120733/762)=0.57374451585758102,sqrt(73.126514292299504/762)=0.30978469004999171,0.30978469004999171/0.57374451585758102=0.53993490393011212,74.191095456751498/sqrt(250.83727034120733*73.126514292299504)=0.54779531590676678,74.191095456751498/73.126514292299504=1.0145580734259625,5-1=4,4.1913925567600003-2.3497676679300001=1.8416248888300002
Grammar,Ridge,sqrt(353.9347112860894/762)=0.68152861158350608,sqrt(123.24482431778341/762)=0.40216739622981246,0.40216739622981246/0.68152861158350608=0.59009613007352935,118.98816783611625/sqrt(353.9347112860894*123.24482431778341)=0.56971526190491972,118.98816783611625/123.24482431778341=0.96546178303851937,5-1=4,3.8689403442899999-0.774876419825=3.0940639244649999
Grammar,RF,sqrt(353.9347112860894/762)=0.68152861158350608,sqrt(114.81018683499063/762)=0.38816174016620841,0.38816174016620841/0.68152861158350608=0.56954577338188228,117.27605039039473/sqrt(353.9347112860894*114.81018683499063)=0.58177833047836458,117.27605039039473/114.81018683499063=1.0214777418570717,5-1=4,4.0458362177499998-2.1730867782400001=1.8727494395099997
QUANTILE_ARITHMETIC linear interpolation: h=(N-1)*q; j=floor(h); x[j]+(h-j)*(x[j+1]-x[j]); zero-based sorted x.
QUANTILE_INDEX q=0.050000000000000003; h=(762-1)*0.050000000000000003=38.050000000000004; j=38; fraction=0.050000000000004263
QUANTILE_INDEX q=0.94999999999999996; h=(762-1)*0.94999999999999996=722.94999999999993; j=722; fraction=0.94999999999993179
TRUTH_BAND_MEANS (2.5 and 4.0 included in middle band)
target,model,truth_band,n,mean_true,mean_pred,arithmetic
Vocabulary,Ridge,<2.5,29,1.9310344827586208,2.84735732330862,truth 56/29=1.9310344827586208; pred 82.573362375949984/29=2.84735732330862
Vocabulary,Ridge,2.5-4.0,708,3.2203389830508473,3.2224380676267232,truth 2280/708=3.2203389830508473; pred 2281.4861518797202/708=3.2224380676267232
Vocabulary,Ridge,>4.0,25,4.6399999999999997,3.6463716438868001,truth 116/25=4.6399999999999997; pred 91.159291097169998/25=3.6463716438868001
Vocabulary,RF,<2.5,29,1.9310344827586208,2.9240358950210346,truth 56/29=1.9310344827586208; pred 84.797040955610001/29=2.9240358950210346
Vocabulary,RF,2.5-4.0,708,3.2203389830508473,3.2146115416018359,truth 2280/708=3.2203389830508473; pred 2275.9449714540997/708=3.2146115416018359
Vocabulary,RF,>4.0,25,4.6399999999999997,3.6604067444707997,truth 116/25=4.6399999999999997; pred 91.510168611769998/25=3.6604067444707997
Grammar,Ridge,<2.5,113,1.9690265486725664,2.6768138759512827,truth 222.5/113=1.9690265486725664; pred 302.47996798249494/113=2.6768138759512827
Grammar,Ridge,2.5-4.0,622,3.1438906752411575,3.0517179340394374,truth 1955.5/622=3.1438906752411575; pred 1898.16855497253/622=3.0517179340394374
Grammar,Ridge,>4.0,27,4.5740740740740744,3.5265167711092595,truth 123.5/27=4.5740740740740744; pred 95.215952819950004/27=3.5265167711092595
Grammar,RF,<2.5,113,1.9690265486725664,2.6998881941574338,truth 222.5/113=1.9690265486725664; pred 305.08736593979/113=2.6998881941574338
Grammar,RF,2.5-4.0,622,3.1438906752411575,3.0337837911226204,truth 1955.5/622=3.1438906752411575; pred 1887.01351807827/622=3.0337837911226204
Grammar,RF,>4.0,27,4.5740740740740744,3.5913884878825928,truth 123.5/27=4.5740740740740744; pred 96.96748917283/27=3.5913884878825928
EXTREME_TRUTH_MIDDLE_PREDICTION_SHARES (prediction endpoints inclusive)
target,model,truth_tail,n,predicted_in_2_5_to_4_0,share,arithmetic
Vocabulary,Ridge,>=4.5,25,24,0.95999999999999996,24/25=0.95999999999999996
Vocabulary,Ridge,<=2.0,29,23,0.7931034482758621,23/29=0.7931034482758621
Vocabulary,RF,>=4.5,25,22,0.88,22/25=0.88
Vocabulary,RF,<=2.0,29,28,0.96551724137931039,28/29=0.96551724137931039
Grammar,Ridge,>=4.5,27,27,1,27/27=1
Grammar,Ridge,<=2.0,113,82,0.72566371681415931,82/113=0.72566371681415931
Grammar,RF,>=4.5,27,26,0.96296296296296291,26/27=0.96296296296296291
Grammar,RF,<=2.0,113,81,0.7168141592920354,81/113=0.7168141592920354
RIDGE_EXTREMITY_WITHIN_BAND_AUROC (joint RF error >=1; average ranks)
target,extremity,truth_band,n,large_errors,other,AUROC,arithmetic
Vocabulary,frozen_max,<2.5,29,15,14,0.23333333333333334,(169-15*(15+1)/2)/(15*14)=0.23333333333333334
Vocabulary,frozen_max,2.5-4.0,708,39,669,0.47092867272239469,(13067-39*(39+1)/2)/(39*669)=0.47092867272239469
Vocabulary,frozen_max,>4.0,25,15,10,0.44,(186-15*(15+1)/2)/(15*10)=0.44
Vocabulary,target_distance,<2.5,29,15,14,0.21428571428571427,(165-15*(15+1)/2)/(15*14)=0.21428571428571427
Vocabulary,target_distance,2.5-4.0,708,39,669,0.42988003526120117,(11996-39*(39+1)/2)/(39*669)=0.42988003526120117
Vocabulary,target_distance,>4.0,25,15,10,0.38,(177-15*(15+1)/2)/(15*10)=0.38
Grammar,frozen_max,<2.5,113,26,87,0.27718832891246686,(978-26*(26+1)/2)/(26*87)=0.27718832891246686
Grammar,frozen_max,2.5-4.0,622,29,593,0.56213293016223764,(10102-29*(29+1)/2)/(29*593)=0.56213293016223764
Grammar,frozen_max,>4.0,27,14,13,0.39010989010989011,(176-14*(14+1)/2)/(14*13)=0.39010989010989011
Grammar,target_distance,<2.5,113,26,87,0.24801061007957559,(912-26*(26+1)/2)/(26*87)=0.24801061007957559
Grammar,target_distance,2.5-4.0,622,29,593,0.54724661278129905,(9846-29*(29+1)/2)/(29*593)=0.54724661278129905
Grammar,target_distance,>4.0,27,14,13,0.38461538461538464,(175-14*(14+1)/2)/(14*13)=0.38461538461538464
RIDGE_EXTREMITY_SPEARMAN (truth distance is per target; average ranks)
target,extremity,n,Spearman_extremity_vs_abs_truth_minus_3,arithmetic
Vocabulary,frozen_max,762,0.046493783742841688,1602773.5/sqrt(36870830.5*32230838.5)=0.046493783742841688
Vocabulary,target_distance,762,0.07763226869878706,2676206/sqrt(36870830.5*32230838.5)=0.07763226869878706
Grammar,frozen_max,762,0.16318947549908558,5608984/sqrt(36870830.5*32040640.5)=0.16318947549908558
Grammar,target_distance,762,0.18321133053445049,6297155/sqrt(36870830.5*32040640.5)=0.18321133053445049
FIT_COMPLETE fold=1; train_n=3043; heldout_n=769; matches_week9b_composition=True; prompt_overlap=0; heldout_id_sha256=5cedcbd4b839308e20e09e066bcf38a53c82f98d43c5ab0490ee2f1273f866f9
FIT_COMPLETE fold=2; train_n=3044; heldout_n=768; matches_week9b_composition=True; prompt_overlap=0; heldout_id_sha256=7ecc3d39eeae833ab6e1b0e645e7f464d2237d67f646f4a536510945b8a757ea
FIT_COMPLETE fold=3; train_n=3051; heldout_n=761; matches_week9b_composition=True; prompt_overlap=0; heldout_id_sha256=4f8ea16e980b6ef933a1782cea40427d41b622692972bad93a9e9b8d25a7f105
FIT_COMPLETE fold=4; train_n=3067; heldout_n=745; matches_week9b_composition=True; prompt_overlap=0; heldout_id_sha256=ee91755ec2a43b3de0af4962883212bda66beec7a0317eba003439f4e7692593
FIT_COMPLETE fold=5; train_n=3043; heldout_n=769; matches_week9b_composition=True; prompt_overlap=0; heldout_id_sha256=49ac62d22682d6b16b7e5f0c76ae4fcd0bf3a8783bf7df0d0c66c2f2ef0b5d5e

SET=Development_OOF; N=3812; joint_RF_large_errors=386
SMALL_SUMMARY_TABLE (population SD; about_0_5 means 0.45<=ratio<=0.55)
target,model,n,SD_true,SD_pred,ratio,about_0_5,true_min,true_max,true_p05,true_p95,pred_min,pred_max,pred_p05,pred_p95,Pearson_r,OLS_truth_on_pred_slope
Vocabulary,Ridge,3812,0.58418124574940056,0.33972202232549153,0.58153531082581855,False,1,5,2.5,4,1.3546612852790658,4.2824012181125077,2.6423563768900102,3.7359198437643482,0.58499941072607864,1.0059568178161715
Vocabulary,RF,3812,0.58418124574940056,0.31141189996342539,0.53307411394889848,True,1,5,2.5,4,2.2718632519311512,4.6219077135673317,2.7465823766222464,3.7459238035206521,0.58741819225005643,1.1019446956420165
Grammar,Ridge,3812,0.70114536288724338,0.40682977820592525,0.58023599632841139,False,1,5,2,4,0.64457772494369969,3.9392193650308935,2.2704944636649538,3.5609086795456375,0.57157207975545277,0.98506828837269322
Grammar,RF,3812,0.70114536288724338,0.39293536076158342,0.56041925335356513,False,1,5,2,4,2.096973039382303,4.3341562492899293,2.4060908510014265,3.6624245899465402,0.58622550535190632,1.0460481181613868
ARITHMETIC (centered sums; OLS includes an intercept)
target,model,SD_true,SD_pred,ratio,Pearson,slope,true_range,pred_range
Vocabulary,Ridge,sqrt(1300.9125786988457/3812)=0.58418124574940056,sqrt(439.94693195053782/3812)=0.33972202232549153,0.33972202232549153/0.58418124574940056=0.58153531082581855,442.56761567295075/sqrt(1300.9125786988457*439.94693195053782)=0.58499941072607864,442.56761567295075/439.94693195053782=1.0059568178161715,5-1=4,4.2824012181125077-1.3546612852790658=2.9277399328334419
Vocabulary,RF,sqrt(1300.9125786988457/3812)=0.58418124574940056,sqrt(369.67773992482171/3812)=0.31141189996342539,0.31141189996342539/0.58418124574940056=0.53307411394889848,407.36442460708616/sqrt(1300.9125786988457*369.67773992482171)=0.58741819225005643,407.36442460708616/369.67773992482171=1.1019446956420165,5-1=4,4.6219077135673317-2.2718632519311512=2.3500444616361804
Grammar,Ridge,sqrt(1873.9975734522591/3812)=0.70114536288724338,sqrt(630.92590567453396/3812)=0.40682977820592525,0.40682977820592525/0.70114536288724338=0.58023599632841139,621.5051019928045/sqrt(1873.9975734522591*630.92590567453396)=0.57157207975545277,621.5051019928045/630.92590567453396=0.98506828837269322,5-1=4,3.9392193650308935-0.64457772494369969=3.2946416400871938
Grammar,RF,sqrt(1873.9975734522591/3812)=0.70114536288724338,sqrt(588.56592977281764/3812)=0.39293536076158342,0.39293536076158342/0.70114536288724338=0.56041925335356513,615.66828325276276/sqrt(1873.9975734522591*588.56592977281764)=0.58622550535190632,615.66828325276276/588.56592977281764=1.0460481181613868,5-1=4,4.3341562492899293-2.096973039382303=2.2371832099076263
QUANTILE_ARITHMETIC linear interpolation: h=(N-1)*q; j=floor(h); x[j]+(h-j)*(x[j+1]-x[j]); zero-based sorted x.
QUANTILE_INDEX q=0.050000000000000003; h=(3812-1)*0.050000000000000003=190.55000000000001; j=190; fraction=0.55000000000001137
QUANTILE_INDEX q=0.94999999999999996; h=(3812-1)*0.94999999999999996=3620.4499999999998; j=3620; fraction=0.4499999999998181
TRUTH_BAND_MEANS (2.5 and 4.0 included in middle band)
target,model,truth_band,n,mean_true,mean_pred,arithmetic
Vocabulary,Ridge,<2.5,137,1.937956204379562,2.7506789450697542,truth 265.5/137=1.937956204379562; pred 376.8430154745563/137=2.7506789450697542
Vocabulary,Ridge,2.5-4.0,3520,3.2241477272727272,3.2355528952166495,truth 11349/3520=3.2241477272727272; pred 11389.146191162607/3520=3.2355528952166495
Vocabulary,Ridge,>4.0,155,4.6322580645161286,3.6501354745857819,truth 718/155=4.6322580645161286; pred 565.77099856079622/155=3.6501354745857819
Vocabulary,RF,<2.5,137,1.937956204379562,2.8580846744608865,truth 265.5/137=1.937956204379562; pred 391.55760040114149/137=2.8580846744608865
Vocabulary,RF,2.5-4.0,3520,3.2241477272727272,3.2331430118597622,truth 11349/3520=3.2241477272727272; pred 11380.663401746362/3520=3.2331430118597622
Vocabulary,RF,>4.0,155,4.6322580645161286,3.6811370020157965,truth 718/155=4.6322580645161286; pred 570.57623531244849/155=3.6811370020157965
Grammar,Ridge,<2.5,555,1.9693693693693695,2.6295306578522695,truth 1093/555=1.9693693693693695; pred 1459.3895151080096/555=2.6295306578522695
Grammar,Ridge,2.5-4.0,3094,3.1468972204266321,3.0886967503077738,truth 9736.5/3094=3.1468972204266321; pred 9556.4277454522526/3094=3.0886967503077738
Grammar,Ridge,>4.0,163,4.5889570552147241,3.4720238113333837,truth 748/163=4.5889570552147241; pred 565.93988124734153/163=3.4720238113333837
Grammar,RF,<2.5,555,1.9693693693693695,2.6911542476393224,truth 1093/555=1.9693693693693695; pred 1493.590607439824/555=2.6911542476393224
Grammar,RF,2.5-4.0,3094,3.1468972204266321,3.0736738838739099,truth 9736.5/3094=3.1468972204266321; pred 9509.9469967058776/3094=3.0736738838739099
Grammar,RF,>4.0,163,4.5889570552147241,3.5680458632771024,truth 748/163=4.5889570552147241; pred 581.5914757141677/163=3.5680458632771024
EXTREME_TRUTH_MIDDLE_PREDICTION_SHARES (prediction endpoints inclusive)
target,model,truth_tail,n,predicted_in_2_5_to_4_0,share,arithmetic
Vocabulary,Ridge,>=4.5,155,141,0.9096774193548387,141/155=0.9096774193548387
Vocabulary,Ridge,<=2.0,137,105,0.76642335766423353,105/137=0.76642335766423353
Vocabulary,RF,>=4.5,155,131,0.84516129032258069,131/155=0.84516129032258069
Vocabulary,RF,<=2.0,137,131,0.95620437956204385,131/137=0.95620437956204385
Grammar,Ridge,>=4.5,163,163,1,163/163=1
Grammar,Ridge,<=2.0,555,374,0.67387387387387387,374/555=0.67387387387387387
Grammar,RF,>=4.5,163,147,0.90184049079754602,147/163=0.90184049079754602
Grammar,RF,<=2.0,555,384,0.69189189189189193,384/555=0.69189189189189193
RIDGE_EXTREMITY_WITHIN_BAND_AUROC (joint RF error >=1; average ranks)
target,extremity,truth_band,n,large_errors,other,AUROC,arithmetic
Vocabulary,frozen_max,<2.5,137,60,77,0.23030303030303031,(2894-60*(60+1)/2)/(60*77)=0.23030303030303031
Vocabulary,frozen_max,2.5-4.0,3520,246,3274,0.44949863670903051,(392409-246*(246+1)/2)/(246*3274)=0.44949863670903051
Vocabulary,frozen_max,>4.0,155,80,75,0.24233333333333335,(4694-80*(80+1)/2)/(80*75)=0.24233333333333335
Vocabulary,target_distance,<2.5,137,60,77,0.22207792207792207,(2856-60*(60+1)/2)/(60*77)=0.22207792207792207
Vocabulary,target_distance,2.5-4.0,3520,246,3274,0.4834244677205477,(419733-246*(246+1)/2)/(246*3274)=0.4834244677205477
Vocabulary,target_distance,>4.0,155,80,75,0.21533333333333332,(4532-80*(80+1)/2)/(80*75)=0.21533333333333332
Grammar,frozen_max,<2.5,555,124,431,0.26102088167053367,(21700-124*(124+1)/2)/(124*431)=0.26102088167053367
Grammar,frozen_max,2.5-4.0,3094,173,2921,0.49645085517866439,(265924-173*(173+1)/2)/(173*2921)=0.49645085517866439
Grammar,frozen_max,>4.0,163,89,74,0.21879744913452778,(5446-89*(89+1)/2)/(89*74)=0.21879744913452778
Grammar,target_distance,<2.5,555,124,431,0.22941770825537011,(20011-124*(124+1)/2)/(124*431)=0.22941770825537011
Grammar,target_distance,2.5-4.0,3094,173,2921,0.47819754498518796,(256700-173*(173+1)/2)/(173*2921)=0.47819754498518796
Grammar,target_distance,>4.0,163,89,74,0.18174916489523232,(5202-89*(89+1)/2)/(89*74)=0.18174916489523232
RIDGE_EXTREMITY_SPEARMAN (truth distance is per target; average ranks)
target,extremity,n,Spearman_extremity_vs_abs_truth_minus_3,arithmetic
Vocabulary,frozen_max,3812,0.092844978639316053,401353594.5/sqrt(4616123293*4048182400.5)=0.092844978639316053
Vocabulary,target_distance,3812,0.14132902597995775,610942168.5/sqrt(4616123293*4048182400.5)=0.14132902597995775
Grammar,frozen_max,3812,0.18795377163055091,813965070/sqrt(4616123293*4062861768)=0.18795377163055091
Grammar,target_distance,3812,0.19714769653388478,853780891/sqrt(4616123293*4062861768)=0.19714769653388478
READ_AUDIT outputs/phase6/feature_schema.json SHA256=77204d8b647522a497e459ce797fc1a433e0e5547993a9ddf83af5d8273ab620
READ_AUDIT outputs/phase6/validation_predictions.csv SHA256=6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
READ_AUDIT reports/week9/t3_fold_composition.csv SHA256=de596a84028e42b8aa0c605c523ee98eef87b6b74127a63b0c8e822d0e0629ea
READ_GUARD artifact_reads=4; allowlisted_only=True; blocked_attempts=0; no Test prediction/label file opened; inputs_unchanged=True
```


## Part C: random Validation reading sample

Command: `.venv/Scripts/python.exe -B -u scripts/week10/random_reading.py`; the completed export was resumed with `--resume-export` following a console encoding failure.

```text
PART C: RANDOM VALIDATION READING SAMPLE; exploratory; seed=2026; no errors, predictions, or tool counts used for selection.
VALIDATION_BAND_AND_DRAW_COUNTS (mean truth; 2.5 and 4 included in middle)
band,Validation_n,old_sample_excluded_from_pool,available_after_exclusion,sampled
<2.5,63,6,57,12
2.5-4.0,672,19,653,12
>4.0,27,7,20,12
VALIDATION_ARITHMETIC 63+672+27=762
EXCLUDED_EXISTING_IDS=32; final_overlap_with_existing_32=0; no_fallback_needed=True
SELECTION_FIXED_BEFORE_PREDICTIONS_AND_TOOL_COUNTS=True; random_sample_ids.csv SHA256=8472794fb01eae511da497577b312bfdc0e4181c7b67eb860b610f83fcae0818
RANDOMIZATION default_rng(2026), choice without replacement per band in <2.5,2.5-4.0,>4.0 order from essay_id-sorted pools; separate default_rng(2026).permutation(36) for reading order.
TOOL_COUNT_METHOD restore phase4 %.12g rate tokens from Week 9 %.17g reserialization; recover unique integer c consistent with rate=100*c/word_count. Decimal rounding-interval, unique-integer and producer-format round-trip checks passed for all 36 selected records. No count estimated and no tool rerun.
RESUMED_COMPLETED_EXPORT=True; same fixed sample; no resampling or second authoring operation. Initial recovery corrected %.12g/%.17g rate-token representation; export then completed before console encoding failure. Full exported cell verification follows.
SHEET reading_sheet HEADERS=["essay_id", "band", "reading_order", "essay_text", "prompt_name", "reader_errors_first150", "reader_low_mid_high_V", "reader_low_mid_high_G"]
SHEET unblind_after HEADERS=["essay_id", "y_V", "y_G", "Ridge_V", "Ridge_G", "RF_V", "RF_G", "word_count", "detected_grammar_errors_per_100_words", "tool_grammar_error_count_recovered", "detected_error_free_sentence_ratio"]
WORKBOOK_VERIFIED row counts, IDs, all source values, shuffled order, blank reader fields, frozen headers and ID column, no formulas, and hidden unblind_after sheet.
HEADER_PREVIEWS_TEMP_DIR=C:\Users\LEGION\AppData\Local\Temp\mla-week10-reading-av9ioe85
FINAL_SAMPLE_COUNTS
band,essays
<2.5,12
2.5-4.0,12
>4.0,12
FINAL_SAMPLE_ARITHMETIC 12+12+12=36
READ_AUDIT data/03_clean_ready_to_use/validation_783.csv SHA256=7b80be5447dd8adadbecf6f492a4320f3e74c7290f91a99e11d43f5951a80e8e
READ_AUDIT outputs/phase6/validation_predictions.csv SHA256=6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
READ_AUDIT reports/week9/t4_manifest.csv SHA256=a0815d53c4a584825992dc274722045294b5e755cdb326e81c302f53a85de192
READ_GUARD artifact_reads=4; allowlisted_only=True; blocked_attempts=0; no Test prediction/label file opened
SHA256 reports/week10/random_sample_ids.csv 8472794fb01eae511da497577b312bfdc0e4181c7b67eb860b610f83fcae0818
SHA256 reports/week10/reading_sheet_random.xlsx 6f3b16689fbd8c61a74b25a22b6460328f7b7ab5fb9d3161d79d5a1ea3a48e4c
FILE_LIST reports/week10/reading_sheet_random.xlsx (internal; git-ignored); reports/week10/random_sample_ids.csv (IDs and band only; committed); scripts/week10/random_reading.py; scripts/week10/reading_workbook.cjs; reports/week10/RESULTS_week10.md (append only); .gitignore (requested path appended)
```

### Final integrity and access audit

```text
PART_A_LOCK_UNCHANGED=True; SHA256=d2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca
PART_B_REPORT_PREFIX_UNCHANGED=True; SHA256=8bf063d9bd71f8cc0aa4714d09ed0b0d4e91c101ce03c0be2b6f57d54eff91ce
SOURCE_UNCHANGED scripts/week9b/tree_spread_oof.py SHA256=ccc8524cccc50b7d78b2680428bd188cd84587c31ab6bddb9af9f006aef9546d
SOURCE_UNCHANGED reports/week9/RESULTS_week9.md SHA256=03921a62b35e96499336c9119c3b0fb4dfa27b73788f61ad42daf73a05243f1d
COMMAND: grep -n '^READ_AUDIT ' reports/week10/RESULTS_week10.md
157:READ_AUDIT outputs/phase6/feature_schema.json SHA256=77204d8b647522a497e459ce797fc1a433e0e5547993a9ddf83af5d8273ab620
158:READ_AUDIT outputs/phase6/validation_predictions.csv SHA256=6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
159:READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
160:READ_AUDIT reports/week9/t3_fold_composition.csv SHA256=de596a84028e42b8aa0c605c523ee98eef87b6b74127a63b0c8e822d0e0629ea
192:READ_AUDIT data/03_clean_ready_to_use/validation_783.csv SHA256=7b80be5447dd8adadbecf6f492a4320f3e74c7290f91a99e11d43f5951a80e8e
193:READ_AUDIT outputs/phase6/validation_predictions.csv SHA256=6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab
194:READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
195:READ_AUDIT reports/week9/t4_manifest.csv SHA256=a0815d53c4a584825992dc274722045294b5e755cdb326e81c302f53a85de192
COMMAND: grep -Eic '^READ_AUDIT .*test' reports/week10/RESULTS_week10.md
0
GREP_NO_TEST_PATH_MATCHES=True; both analysis runs enforced explicit read allowlists with blocked_attempts=0. File-name discovery did not open data files. One-time header inspection of phase4_feature_checkpoint.csv read feature column names only, not Test predictions or labels.
COMMAND: git check-ignore -v -- reports/week10/reading_sheet_random.xlsx
.gitignore:148:/reports/week10/reading_sheet_random.xlsx	reports/week10/reading_sheet_random.xlsx
GITIGNORE_EXISTING_CONTENT_PRESERVED=True
VISUAL_QA both sheets header previews inspected; no essay text or unblinding values printed. All 36 exported essay-text and source-value cells were checked in memory against the selected source records. unblind_after is natively hidden in the exported XLSX.
```

### Part C export housekeeping

The spreadsheet runtime generated `reading_sheet_random.xlsx.inspect.ndjson` as an export sidecar. It was deleted without opening its contents; the builder now removes that automatic sidecar after saving. Only the requested workbook, IDs CSV, and results document remain under reports/week10. The workbook and sample IDs did not change.


## Week 10 filled random reading audit and purposive comparison

User-selected input: `reports/week10/reading_sheet_da_danh_gia.xlsx`; the originally named workbook still has blank reader cells. Exploratory annotations and descriptive comparisons; no confirmatory claim. Producer: `scripts/week10/reading_compare.py`. Command: `.venv/Scripts/python.exe -B -u scripts/week10/reading_compare.py --workbook reports/week10/reading_sheet_da_danh_gia.xlsx --append`.

```text
EXPLORATORY READING AUDIT; saved Validation values and human annotations only; no model refit/predict; no essay text printed; no Test artifacts opened.
VERSIONS Python=3.14.5; numpy=2.4.6; pandas=2.3.3; scipy=1.18.1
EXPECTED_VALUE_COMPARISON counts exact; hand-reported decimals rounded to their supplied decimal places with ROUND_HALF_UP; all computed values printed at 17 significant digits.
INPUT_RESOLUTION requested reading_sheet_random.xlsx is the original blank workbook; user explicitly selected reading_sheet_da_danh_gia.xlsx after clarification. Neither workbook is modified.
ORIGINAL_WORKBOOK_METADATA (only selected non-text fields)
sheet,state,n,selected_headers
reading_sheet,visible,36,"[""essay_id"", ""band"", ""reader_errors_first150"", ""reader_low_mid_high_V"", ""reader_low_mid_high_G""]"
unblind_after,hidden,36,"[""essay_id"", ""y_V"", ""y_G"", ""Ridge_V"", ""Ridge_G"", ""RF_V"", ""RF_G"", ""word_count"", ""detected_grammar_errors_per_100_words""]"
MISMATCH original_requested_workbook.reader.nonempty: actual=0; expected=36; exact
MISMATCH original_requested_workbook.reader_V.nonempty: actual=0; expected=36; exact
MISMATCH original_requested_workbook.reader_G.nonempty: actual=0; expected=36; exact
SELECTED_WORKBOOK_METADATA (only selected non-text fields)
sheet,state,n,selected_headers
reading_sheet,visible,36,"[""essay_id"", ""band"", ""Số lỗi ngữ pháp (150 từ đầu)"", ""Vocabulary"", ""Grammar""]"
unblind_after,visible,36,"[""essay_id"", ""y_V"", ""y_G"", ""Ridge_V"", ""Ridge_G"", ""RF_V"", ""RF_G"", ""word_count"", ""detected_grammar_errors_per_100_words""]"
JOIN_AUDIT reading_ids=36; unblind_ids=36; missing_in_unblind=0; extra_in_unblind=0
UNBLIND_SOURCE_PRESERVATION max_absolute_numeric_difference_from_original=0; tolerance=1e-12; same_ID_set=True
PASS selected_workbook.reader.nonempty: actual=36; expected=36; exact
PASS selected_workbook.reader_V.nonempty: actual=36; expected=36; exact
PASS selected_workbook.reader_G.nonempty: actual=36; expected=36; exact
READER_LEVEL_MAPPING {"thấp": "low", "trung bình": "mid", "cao": "high", "low": "low", "mid": "mid", "middle": "mid", "high": "high"}
BOOTSTRAP_PRIMARY_ORDER physical reading_sheet row order; ordered_ID_SHA256=2b6f7409b0ade09f4ca45bccc3f4dcc97e90c75663129da16fb1a9028a25e7cb
PASS joined_n: actual=36; expected=36; exact
BAND_DEFINITION mean truth=(y_V+y_G)/2; <2.5 low, 2.5<=mean<=4 middle, >4 high; saved band and fixed IDs CSV match recomputed bands.
TOOL_FORMULA tool_estimate=detected_grammar_errors_per_100_words*min(150,word_count)/100. This is the specified estimate for the reading window, not an observed tool count in the first 150 words.
TOOL_FORMULA_ARITHMETIC max_abs_difference_between_rate*window/100_and_rate/100*window=4.4408920985006262e-16
PASS tool_estimate_formula: all 36 rows verified; shorter_than_150_words=1
RF_GROUP_DEFINITION large=max(abs(RF_V-y_V),abs(RF_G-y_G))>=1; signed_error=RF-truth at larger abs error; exact ties use V; above=signed_error>0 among large; below=signed_error<0 among large; not_large otherwise.
TARGET_TIES n=0
RANDOM_SAMPLE_PER_BAND
scope,n,median_reader,mean_reader,mean_tool_estimate,mean_reader_minus_tool,tool_estimate_lt_0_5,Spearman_reader_tool,median_arithmetic,mean_reader_arithmetic,mean_tool_arithmetic,mean_diff_arithmetic,Spearman_arithmetic
<2.5,12,11.5,10.75,2.589405095144,8.1605949048559996,0,0.41476850661831122,(11+12)/2=11.5,129/12=10.75,31.072861141727998/12=2.589405095144,97.927138858272002/12=8.1605949048559996,59/sqrt(141.5*143)=0.41476850661831122
2.5-4.0,12,6.5,7,0.88904430559249981,6.1109556944075001,2,0.57804689508361007,(6+7)/2=6.5,84/12=7,10.668531667109997/12=0.88904430559249981,73.331468332889997/12=6.1109556944075001,81.5/sqrt(139.5*142.5)=0.57804689508361007
>4.0,12,4.5,4.25,0.23191808529174998,4.01808191470825,11,0.011483385035264292,(4+5)/2=4.5,51/12=4.25,2.7830170235009999/12=0.23191808529174998,48.216982976499004/12=4.01808191470825,1.5/sqrt(136.5*125)=0.011483385035264292
RANDOM_SAMPLE_PER_RF_GROUP
scope,n,median_reader,mean_reader,mean_tool_estimate,mean_reader_minus_tool,tool_estimate_lt_0_5,Spearman_reader_tool,median_arithmetic,mean_reader_arithmetic,mean_tool_arithmetic,mean_diff_arithmetic,Spearman_arithmetic
above,6,9,9,1.7852949139154999,7.2147050860844999,1,0.17393131069573453,(9+9)/2=9,54/6=9,10.711769483492999/6=1.7852949139154999,43.288230516506999/6=7.2147050860844999,3/sqrt(17*17.5)=0.17393131069573453
below,6,5,4.5,0.34810939301574995,4.1518906069842503,5,-0.3126526997403612,(5+5)/2=5,27/6=4.5,2.0886563580944997/6=0.34810939301574995,24.9113436419055/6=4.1518906069842503,-5/sqrt(15.5*16.5)=-0.3126526997403612
not_large,24,6.5,7.625,1.3218326662813125,6.3031673337186875,7,0.79842072550237675,(6+7)/2=6.5,183/24=7.625,31.723983990751499/24=1.3218326662813125,151.27601600924851/24=6.3031673337186875,910/sqrt(1139.5*1140)=0.79842072550237675
RANDOM_SAMPLE_OVERALL
scope,n,median_reader,mean_reader,mean_tool_estimate,mean_reader_minus_tool,tool_estimate_lt_0_5,Spearman_reader_tool,median_arithmetic,mean_reader_arithmetic,mean_tool_arithmetic,mean_diff_arithmetic,Spearman_arithmetic
overall,36,6.5,7.333333333333333,1.2367891620094167,6.0965441713239166,13,0.73191211210102969,(6+7)/2=6.5,264/36=7.333333333333333,44.524409832339003/36=1.2367891620094167,219.47559016766101/36=6.0965441713239166,2814.75/sqrt(3849*3842.5)=0.73191211210102969
PASS band[<2.5].n: actual=12; expected=12; exact
PASS band[<2.5].median_reader: actual=11.5; expected=11.5; rounded_HALF_UP(1)=11.5
PASS band[<2.5].mean_tool_estimate: actual=2.589405095144; expected=2.59; rounded_HALF_UP(2)=2.59
PASS band[<2.5].mean_reader_minus_tool: actual=8.1605949048559996; expected=8.16; rounded_HALF_UP(2)=8.16
PASS band[<2.5].tool_estimate_lt_0_5: actual=0; expected=0; exact
PASS band[<2.5].Spearman_reader_tool: actual=0.41476850661831122; expected=0.41; rounded_HALF_UP(2)=0.41
PASS band[2.5-4.0].n: actual=12; expected=12; exact
PASS band[2.5-4.0].median_reader: actual=6.5; expected=6.5; rounded_HALF_UP(1)=6.5
PASS band[2.5-4.0].mean_tool_estimate: actual=0.88904430559249981; expected=0.89; rounded_HALF_UP(2)=0.89
PASS band[2.5-4.0].mean_reader_minus_tool: actual=6.1109556944075001; expected=6.11; rounded_HALF_UP(2)=6.11
PASS band[2.5-4.0].tool_estimate_lt_0_5: actual=2; expected=2; exact
PASS band[2.5-4.0].Spearman_reader_tool: actual=0.57804689508361007; expected=0.58; rounded_HALF_UP(2)=0.58
PASS band[>4.0].n: actual=12; expected=12; exact
PASS band[>4.0].median_reader: actual=4.5; expected=4.5; rounded_HALF_UP(1)=4.5
PASS band[>4.0].mean_tool_estimate: actual=0.23191808529174998; expected=0.23; rounded_HALF_UP(2)=0.23
PASS band[>4.0].mean_reader_minus_tool: actual=4.01808191470825; expected=4.02; rounded_HALF_UP(2)=4.02
PASS band[>4.0].tool_estimate_lt_0_5: actual=11; expected=11; exact
PASS band[>4.0].Spearman_reader_tool: actual=0.011483385035264292; expected=0.01; rounded_HALF_UP(2)=0.01
PASS group[above].n: actual=6; expected=6; exact
PASS group[below].n: actual=6; expected=6; exact
PASS group[not_large].n: actual=24; expected=24; exact
PASS overall.n: actual=36; expected=36; exact
PASS overall.mean_reader: actual=7.333333333333333; expected=7.33; rounded_HALF_UP(2)=7.33
PASS overall.mean_tool_estimate: actual=1.2367891620094167; expected=1.24; rounded_HALF_UP(2)=1.24
PASS overall.Spearman_reader_tool: actual=0.73191211210102969; expected=0.73; rounded_HALF_UP(2)=0.73
PASS recognition[V,low].correct: actual=4; expected=4; exact
PASS recognition[V,low].n: actual=7; expected=7; exact
PASS recognition[V,mid].correct: actual=13; expected=13; exact
PASS recognition[V,mid].n: actual=23; expected=23; exact
PASS recognition[V,high].correct: actual=3; expected=3; exact
PASS recognition[V,high].n: actual=6; expected=6; exact
PASS recognition[G,low].correct: actual=10; expected=10; exact
PASS recognition[G,low].n: actual=13; expected=13; exact
PASS recognition[G,mid].correct: actual=7; expected=7; exact
PASS recognition[G,mid].n: actual=11; expected=11; exact
PASS recognition[G,high].correct: actual=6; expected=6; exact
PASS recognition[G,high].n: actual=12; expected=12; exact
BLIND_RECOGNITION_PER_TRUE_TARGET_LEVEL
target,truth_level,n,correct,share,arithmetic
V,low,7,4,0.5714285714285714,4/7=0.5714285714285714
V,mid,23,13,0.56521739130434778,13/23=0.56521739130434778
V,high,6,3,0.5,3/6=0.5
G,low,13,10,0.76923076923076927,10/13=0.76923076923076927
G,mid,11,7,0.63636363636363635,7/11=0.63636363636363635
G,high,12,6,0.5,6/12=0.5
BLIND_RECOGNITION_CONFUSION_COUNTS
target,truth_level,reader_level,n
V,low,low,4
V,low,mid,2
V,low,high,1
V,mid,low,7
V,mid,mid,13
V,mid,high,3
V,high,low,0
V,high,mid,3
V,high,high,3
G,low,low,10
G,low,mid,2
G,low,high,1
G,mid,low,3
G,mid,mid,7
G,mid,high,1
G,high,low,0
G,high,mid,6
G,high,high,6
OLS_METHOD signed error=RF-truth at larger absolute-error target; V on ties; intercept included. Band reference=<2.5, dummies=2.5-4.0 and >4.0. Coefficient order: diff_only=[intercept,diff]; band_only=[intercept,mid,high]; band_plus_diff=[intercept,mid,high,diff].
BOOTSTRAP_METHOD primary order=reading_sheet physical row order, preserved by the one-to-one left merge; ordinary paired essay rows, n=36 with replacement, 2000 resamples, default_rng(42), identical draws for both models; percentile 95% CI [2.5,97.5], linear interpolation; rank-deficient replicates skipped and counted. Bands are not stratified; no refit of RF or Ridge.
OLS_SIGNED_RF_ERROR_ON_READER_MINUS_TOOL
model,n,rank,coefficients,slope_diff,CI_low,CI_high,R2,slope_arithmetic,R2_arithmetic,bootstrap_resamples,bootstrap_valid,bootstrap_skipped
diff_only,36,2,"[-1.0545264273562112, 0.1724781851589315]",0.17247818515893151,0.086382337627726777,0.25691329625556447,0.29814919583257971,46.783481097798187/271.24288822200396=0.1724781851589316,1-18.994937430823633/27.064067345989045=0.29814919583257971,2000,2000,0
band_only,36,3,"[0.8675099775400003, -0.7534420421116674, -1.8581045493433344]",,,,0.7745334971274076,not included,1-6.1020406180084743/27.064067345989045=0.7745334971274076,,,
band_plus_diff,36,4,"[0.8398785340423669, -0.746502046842408, -1.844078168306167, 0.0033859594575868994]",0.0033859594575868994,-0.053183306767282917,0.08219139940154517,0.77460478150175205,0.5697779705108319/168.27666652479027=0.0033859594575870269,1-6.100111372900499/27.064067345989045=0.77460478150175205,2000,2000,0
BOOTSTRAP_INDEPENDENT_SLOPE_CHECK (lstsq vs covariance or within-band FWL)
model,valid,max_absolute_difference
diff_only,2000,3.3306690738754696e-16
band_plus_diff,2000,2.5539466375068542e-15
PASS diff_only.slope: actual=0.17247818515893151; expected=0.172; rounded_HALF_UP(3)=0.172
PASS diff_only.CI_low: actual=0.086382337627726777; expected=0.086; rounded_HALF_UP(3)=0.086
PASS diff_only.CI_high: actual=0.25691329625556447; expected=0.257; rounded_HALF_UP(3)=0.257
PASS diff_only.R2: actual=0.29814919583257971; expected=0.298; rounded_HALF_UP(3)=0.298
PASS band_plus_diff.slope: actual=0.0033859594575868994; expected=0.003; rounded_HALF_UP(3)=0.003
PASS band_plus_diff.CI_low: actual=-0.053183306767282917; expected=-0.053; rounded_HALF_UP(3)=-0.053
PASS band_plus_diff.CI_high: actual=0.08219139940154517; expected=0.082; rounded_HALF_UP(3)=0.082
PASS band_plus_diff.R2: actual=0.77460478150175205; expected=0.7746; rounded_HALF_UP(4)=0.7746
PASS band_only.R2: actual=0.7745334971274076; expected=0.7745; rounded_HALF_UP(4)=0.7745
BOOTSTRAP_ROW_ORDER_SENSITIVITY (same finite RNG draws map to different essays after reordering)
model,row_order,seed,resamples,valid,CI_low,CI_high,primary_sheet_order_CI_low,primary_sheet_order_CI_high
diff_only,essay_id ascending,42,2000,2000,0.086827820173436904,0.25221024119916874,0.086382337627726777,0.25691329625556447
band_plus_diff,essay_id ascending,42,2000,2000,-0.054498964598173445,0.072971624179440517,-0.053183306767282917,0.08219139940154517
PURPOSIVE_PROVENANCE 32 IDs and reader counts from text-free t4_reading_summary.csv, verified against t4_manifest.csv; tool_estimate independently recomputed with the same window formula from saved eligible-development rates and matching word_count. The CSV approx_tool_count is also reported separately.
PURPOSIVE_SAVED_TOOL_ESTIMATE_CHECK exact_equal_rows=23/32; max_absolute_difference=4.4408920985006262e-16
PURPOSIVE_SAMPLE_PER_RF_GROUP
scope,n,median_reader,mean_reader,mean_tool_estimate,mean_reader_minus_tool,tool_estimate_lt_0_5,Spearman_reader_tool,median_arithmetic,mean_reader_arithmetic,mean_tool_arithmetic,mean_diff_arithmetic,Spearman_arithmetic
above,11,12,12.454545454545455,0.9680864243374091,11.486459030208046,4,0.15632555673600285,sorted[5]=12 (zero based),137/11=12.454545454545455,10.6489506677115/11=0.9680864243374091,126.3510493322885/11=11.486459030208046,17/sqrt(109.5*108)=0.15632555673600285
below,11,5,6.3636363636363633,1.0946721953738181,5.2689641682625457,6,0.69451271784082691,sorted[5]=5 (zero based),70/11=6.3636363636363633,12.041394149112/11=1.0946721953738181,57.958605850888006/11=5.2689641682625457,72.75/sqrt(104.5*105)=0.69451271784082691
not_large,10,9,9.5,2.2783547731049998,7.2216452268950011,2,0.65023270994496629,(9+9)/2=9,95/10=9.5,22.78354773105/10=2.2783547731049998,72.216452268950007/10=7.2216452268950011,52.5/sqrt(79.5*82)=0.65023270994496629
RANDOM_VS_32_PURPOSIVE_SIDE_BY_SIDE
group,random_n,random_median_reader,random_mean_tool,purposive_n,purposive_median_reader,purposive_mean_tool,purposive_mean_saved_approx_tool
above,6,9,1.7852949139154999,11,12,0.9680864243374091,0.96808642433740921
below,6,5,0.34810939301574995,11,5,1.0946721953738181,1.0946721953738181
control_not_large,24,6.5,1.3218326662813125,10,9,2.2783547731049998,2.2783547731049998
PURPOSIVE_SELECTION_GROUP_VS_RF_GROUP
sample_group,group,n
highest_rf_error,above,5
highest_rf_error,below,7
low_rf_error_comparison,not_large,10
shared_blind_spot,above,6
shared_blind_spot,below,4
RANDOM_PURPOSIVE_ID_OVERLAP=0
READ_AUDIT reports/week10/random_sample_ids.csv SHA256=8472794fb01eae511da497577b312bfdc0e4181c7b67eb860b610f83fcae0818
READ_AUDIT reports/week10/reading_sheet_da_danh_gia.xlsx SHA256=b9141f072b6a5f843e9d9e5fa3c9fb2b7b27c0212cf84d8cf988e00806201b27
READ_AUDIT reports/week10/reading_sheet_random.xlsx SHA256=6f3b16689fbd8c61a74b25a22b6460328f7b7ab5fb9d3161d79d5a1ea3a48e4c
READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
READ_AUDIT reports/week9/t4_manifest.csv SHA256=a0815d53c4a584825992dc274722045294b5e755cdb326e81c302f53a85de192
READ_AUDIT reports/week9/t4_reading_summary.csv SHA256=1f3bd89eeb30d8162d1d10a745dda2f8b86af959e1590afce95095562dda016c
READ_GUARD artifact_reads=6; allowlisted_only=True; blocked_attempts=0; no Test file opened; inputs_unchanged=True; essay_text_values_not_resolved_or_printed=True
EXPECTED_VALUE_CHECK_TOTAL pass=50; mismatch=3
MISMATCH_LINES
MISMATCH original_requested_workbook.reader.nonempty: actual=0; expected=36; exact
MISMATCH original_requested_workbook.reader_V.nonempty: actual=0; expected=36; exact
MISMATCH original_requested_workbook.reader_G.nonempty: actual=0; expected=36; exact
```


## Week 10 exploratory OOF comparison of feature and text information sources

Exploratory development-only analysis. Producer: `scripts/week10/information_sources_oof.py`. Command: `.venv/Scripts/python.exe -B -u scripts/week10/information_sources_oof.py --append`. Fixed configurations were printed before fitting; no search, installation or download.

```text
EXPLORATORY DEVELOPMENT ONLY. Installed-package check runs before importing analysis libraries or fitting any model.
COMMAND: D:\03_Education\học trên trường\mla project\.venv\Scripts\python.exe -m pip list
D:\03_Education\h\u1ecdc tr�n tr\u01b0\u1eddng\mla project\.venv\Scripts\python.exe: No module named pip
PIP_LIST_EXIT_CODE=1
FALLBACK_REASON venv has no pip module; uv pip list reads the same venv metadata offline; nothing installed.
COMMAND: uv pip list --python D:\03_Education\học trên trường\mla project\.venv\Scripts\python.exe --offline
Package                   Version      Editable project location
------------------------- ------------ -------------------------------------------
annotated-doc             0.0.5
annotated-types           0.8.0
anyio                     4.15.1
argon2-cffi               25.1.0
argon2-cffi-bindings      26.1.0
arrow                     1.4.0
asttokens                 3.0.2
async-lru                 2.3.0
attrs                     26.1.0
babel                     2.18.0
beautifulsoup4            4.15.0
black                     26.5.1
bleach                    6.4.0
blis                      1.3.3
catalogue                 2.0.10
certifi                   2026.7.22
cffi                      2.1.1
charset-normalizer        3.5.1
click                     8.5.0
cloudpathlib              0.25.0
cloudpickle               3.1.2
colorama                  0.4.6
comm                      0.2.3
confection                1.3.3
contourpy                 1.4.0
coverage                  7.16.1
cycler                    0.12.1
cymem                     2.0.13
debugpy                   1.8.22
defusedxml                0.7.1
en-core-web-sm            3.8.0
executing                 2.2.1
fastjsonschema            2.22.2
flake8                    7.3.0
fonttools                 4.65.0
fqdn                      1.5.1
ftfy                      6.3.1
h11                       0.16.0
httpcore                  1.0.9
httpx                     0.28.1
idna                      3.20
iniconfig                 2.3.0
ipykernel                 7.3.0
ipython                   9.17.1
ipython-pygments-lexers   1.1.1
ipywidgets                8.1.9
isoduration               20.11.0
jedi                      0.20.0
jinja2                    3.1.6
joblib                    1.6.0
json5                     0.15.0
jsonpointer               3.1.1
jsonschema                4.26.0
jsonschema-specifications 2025.9.1
jupyter                   1.1.1
jupyter-builder           1.2.3
jupyter-client            8.10.0
jupyter-console           6.6.3
jupyter-core              5.9.1
jupyter-events            0.12.1
jupyter-lsp               2.3.1
jupyter-server            2.21.1
jupyter-server-terminals  0.5.4
jupyterlab                4.6.4
jupyterlab-pygments       0.3.0
jupyterlab-server         2.28.1
jupyterlab-widgets        3.0.17
kiwisolver                1.5.1
langcodes                 3.5.1
language-tool-python      2.9.5
lark                      1.3.1
lexicalrichness           0.5.1
locate                    1.1.1
markdown-it-py            4.2.0
markupsafe                3.0.3
matplotlib                3.11.2
matplotlib-inline         0.2.2
mccabe                    0.7.0
mdurl                     0.1.2
mistune                   3.3.4
mla-project               0.1.0        D:\03_Education\học trên trường\mla project
msgpack                   1.2.2
murmurhash                1.0.15
mypy-extensions           1.1.0
narwhals                  2.26.0
nbclient                  0.11.0
nbconvert                 7.17.1
nbformat                  5.11.1
nest-asyncio2             1.7.2
nltk                      3.10.3
notebook                  7.6.3
notebook-shim             0.2.4
numpy                     2.4.6
packaging                 26.3
pandas                    2.3.3
pandocfilters             1.5.1
parso                     0.8.7
pathspec                  1.1.1
pillow                    12.3.0
platformdirs              4.11.12
pluggy                    1.6.0
preshed                   3.0.13
prometheus-client         0.26.0
prompt-toolkit            3.0.53
psutil                    7.2.2
pure-eval                 0.2.4
pycodestyle               2.14.0
pycparser                 3.0
pydantic                  2.13.5
pydantic-core             2.46.5
pyflakes                  3.4.0
pygments                  2.21.0
pyparsing                 3.3.3
pytest                    9.1.1
pytest-cov                7.1.0
python-dateutil           2.9.0.post0
python-json-logger        4.2.0
pytokens                  0.4.1
pytz                      2026.3.post1
pywinpty                  3.0.5
pyyaml                    6.0.3
pyzmq                     27.2.0
referencing               0.37.0
regex                     2026.9.10
requests                  2.34.2
rfc3339-validator         0.1.4
rfc3986-validator         0.1.1
rfc3987-syntax            1.1.0
rich                      15.0.0
rpds-py                   2026.6.3
scikit-learn              1.9.1
scipy                     1.18.1
seaborn                   0.13.2
send2trash                2.1.0
setuptools                84.0.0
shellingham               1.5.4
six                       1.17.0
smart-open                8.0.1
soupsieve                 2.9.2
spacy                     3.8.16
spacy-legacy              3.0.12
spacy-loggers             1.0.5
srsly                     2.5.3
stack-data                0.6.3
terminado                 0.18.1
textblob                  0.20.1
thinc                     8.3.13
threadpoolctl             3.7.0
tinycss2                  1.5.1
toml                      0.10.2
tornado                   6.5.10
tqdm                      4.70.1
traitlets                 5.16.1
typer                     0.27.2
typing-extensions         4.16.0
typing-inspection         0.4.4
tzdata                    2026.4
uri-template              1.3.0
urllib3                   2.8.0
wasabi                    1.1.3
wcwidth                   0.8.4
weasel                    1.0.0
webcolors                 25.10.0
webencodings              0.6.1
websocket-client          1.9.2
widgetsnbextension        4.0.16
wordfreq                  3.1.1
wrapt                     2.4.1
PACKAGE sentence-transformers NOT_INSTALLED
PACKAGE transformers NOT_INSTALLED
PACKAGE torch NOT_INSTALLED
PACKAGE huggingface-hub NOT_INSTALLED
PACKAGE language-tool-python 2.9.5
PACKAGE gramformer NOT_INSTALLED
PACKAGE gingerit NOT_INSTALLED
PACKAGE errant NOT_INSTALLED
PACKAGE stanza NOT_INSTALLED
PACKAGE spacy 3.8.16
PACKAGE textblob 0.20.1
FIXED_CONFIGURATION_BEFORE_ANY_FIT {"B1_Ridge": {"alpha": 10.0, "fit_intercept": true, "max_iter": 10000, "solver": "lsqr", "tol": 1e-06}, "B1_TFIDF": {"analyzer": "word", "dtype": "float64", "input": "essay_text only; no prompt name or engineered features", "lowercase": true, "max_df": 1.0, "max_features": null, "min_df": 5, "ngram_range": [1, 2], "norm": "l2", "smooth_idf": true, "stop_words": null, "strip_accents": null, "sublinear_tf": true, "token_pattern": "(?u)\\b\\w\\w+\\b", "use_idf": true}, "B2_Ridge_if_offline": {"alpha": 10.0, "fit_intercept": true, "max_iter": 10000, "solver": "lsqr", "tol": 1e-06}, "B2_encoder_if_offline": {"batch_size": 32, "device": "cpu", "local_files_only": true, "model": "sentence-transformers/all-MiniLM-L6-v2", "normalize_embeddings": false, "trust_remote_code": false}, "bootstrap": "paired ordinary essay bootstrap, percentile [2.5,97.5], linear; no tuning/refitting/reranking", "bootstrap_resamples": 2000, "feature_RF": {"max_depth": 10, "max_features": "sqrt", "min_samples_leaf": {"G": 5, "V": 2}, "n_estimators": 300, "n_jobs": 1, "preprocessing": "train-only median imputation", "random_state": 42}, "feature_Ridge": {"alpha": {"G": 0.1, "V": 100.0}, "preprocessing": "train-only median imputation and StandardScaler"}, "folds": "GroupKFold(5), normalised_prompt, input sorted by essay_id string ascending", "large_error": "max target absolute error >= 1.0", "queue": "score descending, essay_id string ascending; ceil(0.20*n_fold)", "seed": 42, "status": "exploratory development only; no hyperparameter search"}
FIXED_CONFIGURATION_SHA256=3e717c9b69aaf25e1e6e25a0ce5e584ea427e34ffd97dc203f1b2abd97fe81fd
SCRIPT_SHA256_BEFORE_FIT=28a1063e6ab2111318bf275876a98f5b28d63d073d0320c0ee9ebe4f22da44ac
NO_DOWNLOAD_COMMAND_RUN=True; no model weights or data downloaded; only installed packages and offline caches checked.
ANALYSIS_VERSIONS Python=3.14.5; numpy=2.4.6; pandas=2.3.3; scipy=1.18.1; sklearn=1.9.1
OFFLINE_CACHE_CHECK path=C:\Users\LEGION\.cache\huggingface\hub; exists=False
OFFLINE_CACHE_CHECK path=C:\Users\LEGION\.cache\torch\sentence_transformers; exists=False
SKIP B2 frozen sentence encoder: required installed packages missing=sentence-transformers,transformers,torch; no encoder substituted; no weights/data downloaded.
SKIP OPTIONAL SECOND GRAMMAR COUNTER: no second grammar-error counter installed (gramformer, gingerit absent). language-tool-python is the existing counter; spaCy and TextBlob are not substituted as independent grammar-error counters. No installation/download; no 32/random-sample text or Test file opened for this optional step.
DATA_JOIN eligible=3812; prompts=44; text-to-eligible-ID one-to-one=True; saved targets match clean development targets=True; model_train=3050; validation=762
FIT_COMPLETE fold=1; train_n=3043; n=769; k=154; tfidf_vocabulary_size=32335; no evaluation-fold vocabulary/IDF fit; frozen feature parameters unchanged.
FIT_COMPLETE fold=2; train_n=3044; n=768; k=154; tfidf_vocabulary_size=32695; no evaluation-fold vocabulary/IDF fit; frozen feature parameters unchanged.
FIT_COMPLETE fold=3; train_n=3051; n=761; k=153; tfidf_vocabulary_size=32675; no evaluation-fold vocabulary/IDF fit; frozen feature parameters unchanged.
FIT_COMPLETE fold=4; train_n=3067; n=745; k=149; tfidf_vocabulary_size=33031; no evaluation-fold vocabulary/IDF fit; frozen feature parameters unchanged.
FIT_COMPLETE fold=5; train_n=3043; n=769; k=154; tfidf_vocabulary_size=32560; no evaluation-fold vocabulary/IDF fit; frozen feature parameters unchanged.
FOLD_AND_TEXT_FIT_CHECKS
fold,train_n,n,heldout_prompts,overlapping_prompts,k,matches_saved_prompt_composition,tfidf_vocabulary_size,heldout_id_sha256
1,3043,769,9,0,154,True,32335,5cedcbd4b839308e20e09e066bcf38a53c82f98d43c5ab0490ee2f1273f866f9
2,3044,768,9,0,154,True,32695,7ecc3d39eeae833ab6e1b0e645e7f464d2237d67f646f4a536510945b8a757ea
3,3051,761,9,0,153,True,32675,4f8ea16e980b6ef933a1782cea40427d41b622692972bad93a9e9b8d25a7f105
4,3067,745,8,0,149,True,33031,ee91755ec2a43b3de0af4962883212bda66beec7a0317eba003439f4e7692593
5,3043,769,9,0,154,True,32560,49ac62d22682d6b16b7e5f0c76ae4fcd0bf3a8783bf7df0d0c66c2f2ef0b5d5e
OOF_MAE_AND_R_SQUARED (pooled essays, not mean of fold metrics)
model,target,n,MAE,R2,MAE_arithmetic,R2_arithmetic
RF_feature,Vocabulary,3812,0.37216506904049595,0.34208547212760032,1418.6932431823707/3812=0.37216506904049595,1-855.88928501791725/1300.9125786988459=0.34208547212760032
RF_feature,Grammar,3812,0.45540371959591663,0.34298623301972808,1735.9989790996342/3812=0.45540371959591663,1-1231.2422050457576/1873.9975734522593=0.34298623301972808
Ridge_feature,Vocabulary,3812,0.37342443714543022,0.34221220019923604,1423.4939543983801/3812=0.37342443714543022,1-855.72442287545198/1300.9125786988459=0.34221220019923604
Ridge_feature,Grammar,3812,0.46303653771248415,0.32661704194151464,1765.0952817599896/3812=0.46303653771248415,1-1261.918029405706/1873.9975734522593=0.32661704194151464
B1_TFIDF,Vocabulary,3812,0.40662621823241968,0.22227921561866248,1550.0591439019838/3812=0.40662621823241968,1-1011.7467511172149/1300.9125786988459=0.22227921561866248
B1_TFIDF,Grammar,3812,0.50684121395714821,0.21578498887911601,1932.078707604649/3812=0.50684121395714821,1-1469.6170279053731/1873.9975734522593=0.21578498887911601
CORRELATION_BOOTSTRAP exact tied average ranks recalculated under repeated observations via weighted ranks; paired essay draws, 2000, default_rng(42), input essay_id ascending; first draw verified against direct repeated-row scipy Spearman / numpy Pearson. No prompt clustering or model refits.
SIGNED_ERROR_CORRELATIONS_WITH_95_PERCENT_ESSAY_BOOTSTRAP_CI
target,model_a,model_b,method,n,correlation,below_0_95,CI_low,CI_high,entire_CI_below_0_95,bootstrap_valid,bootstrap_skipped,arithmetic
Vocabulary,RF_feature,Ridge_feature,Pearson,3812,0.95236815626875215,False,0.94746120955999857,0.95662804638694066,False,2000,0,815.02987928069138/sqrt(855.86146940949493*855.72427930348226)=0.95236815626875215
Vocabulary,RF_feature,Ridge_feature,Spearman,3812,0.94734621400416741,True,0.94171243106803337,0.95239166356040861,False,2000,0,4373066925/sqrt(4616123293*4616123293)=0.94734621400416741
Vocabulary,B1_TFIDF,RF_feature,Pearson,3812,0.89955820257966845,True,0.8932413375798246,0.90559885606120549,True,2000,0,836.80619085756541/sqrt(1011.0852108896599*855.86146940949493)=0.89955820257966845
Vocabulary,B1_TFIDF,RF_feature,Spearman,3812,0.88738393929202186,True,0.87863230310549434,0.89538796399246612,True,2000,0,4096273672/sqrt(4616123293*4616123293)=0.88738393929202186
Vocabulary,B1_TFIDF,Ridge_feature,Pearson,3812,0.87580249884195915,True,0.86528321295442268,0.88515226552269144,True,2000,0,814.64235485540371/sqrt(1011.0852108896599*855.72427930348226)=0.87580249884195915
Vocabulary,B1_TFIDF,Ridge_feature,Spearman,3812,0.86310834765651911,True,0.85183633475184728,0.87400106236587949,True,2000,0,3984214548/sqrt(4616123293*4616123293)=0.86310834765651911
Grammar,RF_feature,Ridge_feature,Pearson,3812,0.94911635818182327,True,0.94309066982127543,0.95440985557091795,False,2000,0,1183.0504561844584/sqrt(1231.2269367195481*1261.913275141181)=0.94911635818182327
Grammar,RF_feature,Ridge_feature,Spearman,3812,0.94714901411538188,True,0.94114830307990061,0.9522580426599061,False,2000,0,4372156626/sqrt(4616123293*4616123293)=0.94714901411538188
Grammar,B1_TFIDF,RF_feature,Pearson,3812,0.86770863128358211,True,0.86051930503074681,0.87468174154330591,True,2000,0,1167.080409085557/sqrt(1469.3173758143989*1231.2269367195481)=0.86770863128358211
Grammar,B1_TFIDF,RF_feature,Spearman,3812,0.864747977389,True,0.85620172666431948,0.87292505190964087,True,2000,0,3991783281/sqrt(4616123293*4616123293)=0.864747977389
Grammar,B1_TFIDF,Ridge_feature,Pearson,3812,0.85770796057177867,True,0.84547678230589596,0.86859900104119292,True,2000,0,1167.9170609636024/sqrt(1469.3173758143989*1261.913275141181)=0.85770796057177867
Grammar,B1_TFIDF,Ridge_feature,Spearman,3812,0.85026391863316286,True,0.83731803381198155,0.86179285373573344,True,2000,0,3924923080/sqrt(4616123293*4616123293)=0.85026391863316286
BASELINE_REPRODUCTION A1_RF_large_errors=386; A3_old_RF_and_Ridge_large_errors=276; fixed frozen parameters and saved prompt folds reproduce previous counts.
SOURCE_PAIRING B1_TFIDF; D_new=max(abs(RF_feature_V-B_V),abs(RF_feature_G-B_G)); D_old=max(abs(RF_feature_V-Ridge_feature_V),abs(RF_feature_G-Ridge_feature_G)); A3_new=A1 and max(abs(B-y))>=1, either target may trigger each model.
CAPTURE_CAUGHT_VS_EXPECTED_AND_EXACT_P (same labels and rows for both signals)
source,anchor,scope,signal,n,K,k,caught,capture,capture_arithmetic,expected,expected_arithmetic,caught_minus_expected,exact_p,exact_p_formula
B1_TFIDF,A1_RF_anchor,fold1,D_old,769,73,154,15,0.20547945205479451,15/73=0.20547945205479451,14.618985695708712,154*73/769=14.618985695708712,0.38101430429128769,0.50454768821846441,"hypergeom.sf(14,769,73,154)"
B1_TFIDF,A1_RF_anchor,fold1,D_new,769,73,154,15,0.20547945205479451,15/73=0.20547945205479451,14.618985695708712,154*73/769=14.618985695708712,0.38101430429128769,0.50454768821846441,"hypergeom.sf(14,769,73,154)"
B1_TFIDF,A1_RF_anchor,fold2,D_old,768,88,154,22,0.25,22/88=0.25,17.645833333333332,154*88/768=17.645833333333332,4.3541666666666679,0.13838981922873914,"hypergeom.sf(21,768,88,154)"
B1_TFIDF,A1_RF_anchor,fold2,D_new,768,88,154,18,0.20454545454545456,18/88=0.20454545454545456,17.645833333333332,154*88/768=17.645833333333332,0.35416666666666785,0.50768829623842204,"hypergeom.sf(17,768,88,154)"
B1_TFIDF,A1_RF_anchor,fold3,D_old,761,75,153,20,0.26666666666666666,20/75=0.26666666666666666,15.078843626806833,153*75/761=15.078843626806833,4.9211563731931669,0.092467509248828822,"hypergeom.sf(19,761,75,153)"
B1_TFIDF,A1_RF_anchor,fold3,D_new,761,75,153,14,0.18666666666666668,14/75=0.18666666666666668,15.078843626806833,153*75/761=15.078843626806833,-1.0788436268068331,0.67707655193591809,"hypergeom.sf(13,761,75,153)"
B1_TFIDF,A1_RF_anchor,fold4,D_old,745,76,149,17,0.22368421052631579,17/76=0.22368421052631579,15.199999999999999,149*76/745=15.199999999999999,1.8000000000000007,0.33962947986356462,"hypergeom.sf(16,745,76,149)"
B1_TFIDF,A1_RF_anchor,fold4,D_new,745,76,149,18,0.23684210526315788,18/76=0.23684210526315788,15.199999999999999,149*76/745=15.199999999999999,2.8000000000000007,0.23937543733161318,"hypergeom.sf(17,745,76,149)"
B1_TFIDF,A1_RF_anchor,fold5,D_old,769,74,154,14,0.1891891891891892,14/74=0.1891891891891892,14.819245773732119,154*74/769=14.819245773732119,-0.81924577373211882,0.64862117609057512,"hypergeom.sf(13,769,74,154)"
B1_TFIDF,A1_RF_anchor,fold5,D_new,769,74,154,16,0.21621621621621623,16/74=0.21621621621621623,14.819245773732119,154*74/769=14.819245773732119,1.1807542262678812,0.40846767773698267,"hypergeom.sf(15,769,74,154)"
B1_TFIDF,A1_RF_anchor,pooled,D_old,3812,386,764,88,0.22797927461139897,88/386=0.22797927461139897,77.362908429580997,154*73/769+154*88/768+153*75/761+149*76/745+154*74/769=77.362908429580997,10.637091570419003,0.088356842158423293,P(sum fold Hypergeom >= 88); exact PMF convolution
B1_TFIDF,A1_RF_anchor,pooled,D_new,3812,386,764,81,0.20984455958549222,81/386=0.20984455958549222,77.362908429580997,154*73/769+154*88/768+153*75/761+149*76/745+154*74/769=77.362908429580997,3.6370915704190026,0.33383425043706638,P(sum fold Hypergeom >= 81); exact PMF convolution
AUROC_95_PERCENT_ESSAY_BOOTSTRAP_CI (both signals; direct rank arithmetic)
source,anchor,scope,signal,n,K,AUROC,CI_low,CI_high,bootstrap_valid,bootstrap_skipped,arithmetic
B1_TFIDF,A1_RF_anchor,fold1,D_old,769,73,0.49584711069122972,0.42262485265270316,0.56788093410242457,2000,0,25193/(73*696)=0.49584711069122972
B1_TFIDF,A1_RF_anchor,fold1,D_new,769,73,0.48795465281058104,0.41692564090476975,0.56457099878627059,2000,0,24792/(73*696)=0.48795465281058104
B1_TFIDF,A1_RF_anchor,fold2,D_old,768,88,0.50132018716577542,0.4328475091811928,0.56992016939351497,2000,0,29999/(88*680)=0.50132018716577542
B1_TFIDF,A1_RF_anchor,fold2,D_new,768,88,0.52865975935828879,0.46638489990075371,0.58766312428319922,2000,0,31635/(88*680)=0.52865975935828879
B1_TFIDF,A1_RF_anchor,fold3,D_old,761,75,0.55317784256559765,0.47966248145149076,0.62607292304551942,2000,0,28461/(75*686)=0.55317784256559765
B1_TFIDF,A1_RF_anchor,fold3,D_new,761,75,0.50999028182701656,0.44061724267048175,0.57911792299304721,2000,0,26239/(75*686)=0.50999028182701656
B1_TFIDF,A1_RF_anchor,fold4,D_old,745,76,0.53221619070096771,0.46144934998056508,0.60419087950505967,2000,0,27060/(76*669)=0.53221619070096771
B1_TFIDF,A1_RF_anchor,fold4,D_new,745,76,0.53552041538824635,0.46653400662979183,0.60347232268770179,2000,0,27228/(76*669)=0.53552041538824635
B1_TFIDF,A1_RF_anchor,fold5,D_old,769,74,0.50056387322574369,0.43159797066155786,0.56938176754458847,2000,0,25744/(74*695)=0.50056387322574369
B1_TFIDF,A1_RF_anchor,fold5,D_new,769,74,0.49966945362628817,0.43078758984873505,0.56860278374482154,2000,0,25698/(74*695)=0.49966945362628817
B1_TFIDF,A1_RF_anchor,pooled,D_old,3812,386,0.51630929587518792,0.48432591186512125,0.54650602561085737,2000,0,682786/(386*3426)=0.51630929587518792
B1_TFIDF,A1_RF_anchor,pooled,D_new,3812,386,0.51234010568375332,0.48240820631542469,0.54340708629504686,2000,0,677537/(386*3426)=0.51234010568375332
PAIRED_NEW_VS_OLD_AND_RANDOM_REFERENCE_95_PERCENT_CI
source,anchor,scope,n,K,caught_new,caught_old,expected,delta_auc,delta_auc_CI_low,delta_auc_CI_high,delta_auc_bootstrap_valid,delta_auc_arithmetic,delta_caught,delta_caught_CI_low,delta_caught_CI_high,delta_caught_bootstrap_valid,delta_caught_arithmetic,delta_capture,delta_capture_CI_low,delta_capture_CI_high,delta_capture_bootstrap_valid,delta_capture_arithmetic,new_excess_random,new_excess_random_CI_low,new_excess_random_CI_high,new_excess_random_bootstrap_valid,new_excess_random_arithmetic,old_excess_random,old_excess_random_CI_low,old_excess_random_CI_high,old_excess_random_bootstrap_valid,old_excess_random_arithmetic
B1_TFIDF,A1_RF_anchor,fold1,769,73,15,15,14.618985695708712,-0.0078924578806486845,-0.11000209258766085,0.096956038320977572,2000,0.48795465281058104-0.49584711069122972=-0.0078924578806486845,0,-9,9,2000,15-15=0,0,-0.11942995864053227,0.13157894736842105,2000,(15-15)/73=0,0.38101430429128769,-5.6190182054616402,7.1820871261378407,2000,15-14.618985695708712=0.38101430429128769,0.38101430429128769,-6.4187581274382337,7.1868985695708449,2000,15-14.618985695708712=0.38101430429128769
B1_TFIDF,A1_RF_anchor,fold2,768,88,18,22,17.645833333333336,0.027339572192513373,-0.048528028489140389,0.10661290835373646,2000,0.52865975935828879-0.50132018716577542=0.027339572192513373,-4,-14,6,2000,18-22=-4,-0.045454545454545456,-0.16250000000000001,0.063846945778997841,2000,(18-22)/88=-0.045454545454545456,0.3541666666666643,-6.6380208333333357,7.7624999999999744,2000,18-17.645833333333336=0.3541666666666643,4.3541666666666643,-3.2572916666666676,12.950585937499998,2000,22-17.645833333333336=4.3541666666666643
B1_TFIDF,A1_RF_anchor,fold3,761,75,14,20,15.078843626806833,-0.043187560738581099,-0.12723410260645834,0.041104673377357598,2000,0.50999028182701656-0.55317784256559765=-0.043187560738581099,-6,-16,3,2000,14-20=-6,-0.080000000000000002,-0.2073289515362686,0.044956588355464691,2000,(14-20)/75=-0.080000000000000002,-1.0788436268068331,-7.4862023653088023,5.3327529566359821,2000,14-15.078843626806833=-1.0788436268068331,4.9211563731931669,-2.475821287779238,12.52431011826544,2000,20-15.078843626806833=4.9211563731931669
B1_TFIDF,A1_RF_anchor,fold4,745,76,18,17,15.199999999999999,0.0033042246872786452,-0.093284737432489551,0.10865907029267516,2000,0.53552041538824635-0.53221619070096771=0.0033042246872786452,1,-9,11,2000,18-17=1,0.013157894736842105,-0.11766640866873064,0.14866377571601444,2000,(18-17)/76=0.013157894736842105,2.8000000000000007,-4.5999999999999996,10.599999999999998,2000,18-15.199999999999999=2.8000000000000007,1.8000000000000007,-5,9.3999999999999986,2000,17-15.199999999999999=1.8000000000000007
B1_TFIDF,A1_RF_anchor,fold5,769,74,16,14,14.819245773732121,-0.00089441959945552041,-0.076969015672482308,0.078642279690368702,2000,0.49966945362628817-0.50056387322574369=-0.00089441959945552041,2,-5,9,2000,16-14=2,0.027027027027027029,-0.071428571428571425,0.125,2000,(16-14)/74=0.027027027027027029,1.1807542262678794,-5.2210988296488976,7.981794538361509,2000,16-14.819245773732121=1.1807542262678794,-0.8192457737321206,-7.0182379713914189,5.7815344603381007,2000,14-14.819245773732121=-0.8192457737321206
B1_TFIDF,A1_RF_anchor,pooled,3812,386,81,88,77.362908429580997,-0.0039691901914346017,-0.043085814621392562,0.03662922546256539,2000,0.51234010568375332-0.51630929587518792=-0.0039691901914346017,-7,-27,14,2000,81-88=-7,-0.018134715025906734,-0.071052418538757336,0.036946682198394393,2000,(81-88)/386=-0.018134715025906734,3.6370915704190026,-11.576430473628498,19.65027696366187,2000,81-77.362908429580997=3.6370915704190026,10.637091570419003,-5.1566855041541206,27.245405189374647,2000,88-77.362908429580997=10.637091570419003
QUEUE_BOOTSTRAP_METHOD seed=42, 2000 paired essay resamples within each displayed scope; fixed scores and original fold queues; no reranking/refit/budget recomputation. Excess-vs-random uses each original fold rate k_f/n_f times the resampled large-error labels. Pooled essay draws are not stratified by fold. AUC uses exact weighted tied ranks, first draw checked against direct repeated rows. CIs condition on fitted OOF models, not retraining.
CAPTURE_CAUGHT_VS_EXPECTED_AND_EXACT_P (same labels and rows for both signals)
source,anchor,scope,signal,n,K,k,caught,capture,capture_arithmetic,expected,expected_arithmetic,caught_minus_expected,exact_p,exact_p_formula
B1_TFIDF,A3_new_RF_and_B,fold1,D_old,769,47,154,12,0.25531914893617019,12/47=0.25531914893617019,9.4122236671001307,154*47/769=9.4122236671001307,2.5877763328998693,0.21237366347945527,"hypergeom.sf(11,769,47,154)"
B1_TFIDF,A3_new_RF_and_B,fold1,D_new,769,47,154,5,0.10638297872340426,5/47=0.10638297872340426,9.4122236671001307,154*47/769=9.4122236671001307,-4.4122236671001307,0.97500772313508022,"hypergeom.sf(4,769,47,154)"
B1_TFIDF,A3_new_RF_and_B,fold2,D_old,768,57,154,11,0.19298245614035087,11/57=0.19298245614035087,11.4296875,154*57/768=11.4296875,-0.4296875,0.61497663746071329,"hypergeom.sf(10,768,57,154)"
B1_TFIDF,A3_new_RF_and_B,fold2,D_new,768,57,154,10,0.17543859649122806,10/57=0.17543859649122806,11.4296875,154*57/768=11.4296875,-1.4296875,0.74088898271079362,"hypergeom.sf(9,768,57,154)"
B1_TFIDF,A3_new_RF_and_B,fold3,D_old,761,43,153,11,0.2558139534883721,11/43=0.2558139534883721,8.645203679369251,153*43/761=8.645203679369251,2.354796320630749,0.22876521545907427,"hypergeom.sf(10,761,43,153)"
B1_TFIDF,A3_new_RF_and_B,fold3,D_new,761,43,153,4,0.093023255813953487,4/43=0.093023255813953487,8.645203679369251,153*43/761=8.645203679369251,-4.645203679369251,0.98512871955467318,"hypergeom.sf(3,761,43,153)"
B1_TFIDF,A3_new_RF_and_B,fold4,D_old,745,44,149,10,0.22727272727272727,10/44=0.22727272727272727,8.8000000000000007,149*44/745=8.8000000000000007,1.1999999999999993,0.38076030526200944,"hypergeom.sf(9,745,44,149)"
B1_TFIDF,A3_new_RF_and_B,fold4,D_new,745,44,149,9,0.20454545454545456,9/44=0.20454545454545456,8.8000000000000007,149*44/745=8.8000000000000007,0.19999999999999929,0.53259850174246814,"hypergeom.sf(8,745,44,149)"
B1_TFIDF,A3_new_RF_and_B,fold5,D_old,769,42,154,8,0.19047619047619047,8/42=0.19047619047619047,8.4109232769830946,154*42/769=8.4109232769830946,-0.41092327698309461,0.62886221548320786,"hypergeom.sf(7,769,42,154)"
B1_TFIDF,A3_new_RF_and_B,fold5,D_new,769,42,154,7,0.16666666666666666,7/42=0.16666666666666666,8.4109232769830946,154*42/769=8.4109232769830946,-1.4109232769830946,0.77086485614416644,"hypergeom.sf(6,769,42,154)"
B1_TFIDF,A3_new_RF_and_B,pooled,D_old,3812,233,764,52,0.22317596566523606,52/233=0.22317596566523606,46.698038123452477,154*47/769+154*57/768+153*43/761+149*44/745+154*42/769=46.698038123452477,5.3019618765475229,0.20723401390577575,P(sum fold Hypergeom >= 52); exact PMF convolution
B1_TFIDF,A3_new_RF_and_B,pooled,D_new,3812,233,764,35,0.15021459227467812,35/233=0.15021459227467812,46.698038123452477,154*47/769+154*57/768+153*43/761+149*44/745+154*42/769=46.698038123452477,-11.698038123452477,0.98282421164695211,P(sum fold Hypergeom >= 35); exact PMF convolution
AUROC_95_PERCENT_ESSAY_BOOTSTRAP_CI (both signals; direct rank arithmetic)
source,anchor,scope,signal,n,K,AUROC,CI_low,CI_high,bootstrap_valid,bootstrap_skipped,arithmetic
B1_TFIDF,A3_new_RF_and_B,fold1,D_old,769,47,0.48022632168326751,0.38394253295903114,0.57602998686121532,2000,0,16296/(47*722)=0.48022632168326751
B1_TFIDF,A3_new_RF_and_B,fold1,D_new,769,47,0.39800789768373901,0.31928867377136677,0.48352516929631617,2000,0,13506/(47*722)=0.39800789768373901
B1_TFIDF,A3_new_RF_and_B,fold2,D_old,768,57,0.45322871172304885,0.36731623935160668,0.53859821018145848,2000,0,18368/(57*711)=0.45322871172304885
B1_TFIDF,A3_new_RF_and_B,fold2,D_new,768,57,0.48594763984504158,0.40781546683224396,0.56351996776899638,2000,0,19694/(57*711)=0.48594763984504158
B1_TFIDF,A3_new_RF_and_B,fold3,D_old,761,43,0.52186305629332119,0.42910257058408302,0.61747909657975886,2000,0,16112/(43*718)=0.52186305629332119
B1_TFIDF,A3_new_RF_and_B,fold3,D_new,761,43,0.43518818423268768,0.34770085267772738,0.51993113557078652,2000,0,13436/(43*718)=0.43518818423268768
B1_TFIDF,A3_new_RF_and_B,fold4,D_old,745,44,0.503177279211516,0.41476075997163897,0.59459872935889868,2000,0,15520/(44*701)=0.503177279211516
B1_TFIDF,A3_new_RF_and_B,fold4,D_new,745,44,0.46440150434444299,0.37090929672896938,0.55540820557923098,2000,0,14324/(44*701)=0.46440150434444299
B1_TFIDF,A3_new_RF_and_B,fold5,D_old,769,42,0.50393004519551976,0.41747197026958932,0.59376791625741199,2000,0,15387/(42*727)=0.50393004519551976
B1_TFIDF,A3_new_RF_and_B,fold5,D_new,769,42,0.41566778017947209,0.33095144219997846,0.50423312700361489,2000,0,12692/(42*727)=0.41566778017947209
B1_TFIDF,A3_new_RF_and_B,pooled,D_old,3812,233,0.48974166183998935,0.44779967190638625,0.52961647249709676,2000,0,408399/(233*3579)=0.48974166183998935
B1_TFIDF,A3_new_RF_and_B,pooled,D_new,3812,233,0.44139934069386633,0.40493615222838175,0.48174540494043083,2000,0,368086/(233*3579)=0.44139934069386633
PAIRED_NEW_VS_OLD_AND_RANDOM_REFERENCE_95_PERCENT_CI
source,anchor,scope,n,K,caught_new,caught_old,expected,delta_auc,delta_auc_CI_low,delta_auc_CI_high,delta_auc_bootstrap_valid,delta_auc_arithmetic,delta_caught,delta_caught_CI_low,delta_caught_CI_high,delta_caught_bootstrap_valid,delta_caught_arithmetic,delta_capture,delta_capture_CI_low,delta_capture_CI_high,delta_capture_bootstrap_valid,delta_capture_arithmetic,new_excess_random,new_excess_random_CI_low,new_excess_random_CI_high,new_excess_random_bootstrap_valid,new_excess_random_arithmetic,old_excess_random,old_excess_random_CI_low,old_excess_random_CI_high,old_excess_random_bootstrap_valid,old_excess_random_arithmetic
B1_TFIDF,A3_new_RF_and_B,fold1,769,47,5,12,9.4122236671001307,-0.0822184239995285,-0.22322622504058012,0.052184229175616402,2000,0.39800789768373901-0.48022632168326751=-0.0822184239995285,-7,-15,0,2000,5-12=-7,-0.14893617021276595,-0.30188679245283018,0,2000,(5-12)/47=-0.14893617021276595,-4.4122236671001307,-8.4122561768530559,0.1885565669700906,2000,5-9.4122236671001307=-4.4122236671001307,2.5877763328998693,-3.4109557867360203,8.3901170351105332,2000,12-9.4122236671001307=2.5877763328998693
B1_TFIDF,A3_new_RF_and_B,fold2,768,57,10,11,11.4296875,0.03271892812199273,-0.070259769932105115,0.13605045993295176,2000,0.48594763984504158-0.45322871172304885=0.03271892812199273,-1,-9,7,2000,10-11=-1,-0.017543859649122806,-0.15284722222222222,0.12280701754385964,2000,(10-11)/57=-0.017543859649122806,-1.4296875,-6.828125,4.3645833333333321,2000,10-11.4296875=-1.4296875,-0.4296875,-6.2265625,6.1615885416666645,2000,11-11.4296875=-0.4296875
B1_TFIDF,A3_new_RF_and_B,fold3,761,43,4,11,8.645203679369251,-0.086674872060633512,-0.18642090936974554,0.017467143566364678,2000,0.43518818423268768-0.52186305629332119=-0.086674872060633512,-7,-14,-1,2000,4-11=-7,-0.16279069767441862,-0.30235672757475079,-0.02564102564102564,2000,(4-11)/43=-0.16279069767441862,-4.645203679369251,-8.4645532194480957,-0.63994743758212813,2000,4-8.645203679369251=-4.645203679369251,2.354796320630749,-2.846254927726676,8.1637647831799995,2000,11-8.645203679369251=2.354796320630749
B1_TFIDF,A3_new_RF_and_B,fold4,745,44,9,10,8.8000000000000007,-0.03877577486707301,-0.16667375886524824,0.092412752202971044,2000,0.46440150434444299-0.503177279211516=-0.03877577486707301,-1,-8,6,2000,9-10=-1,-0.022727272727272728,-0.18181818181818182,0.14285714285714285,2000,(9-10)/44=-0.022727272727272728,0.19999999999999929,-4.8050000000000006,5.7999999999999989,2000,9-8.8000000000000007=0.19999999999999929,1.1999999999999993,-3.8000000000000007,6.9999999999999982,2000,10-8.8000000000000007=1.1999999999999993
B1_TFIDF,A3_new_RF_and_B,fold5,769,42,7,8,8.4109232769830946,-0.08826226501604767,-0.18843396360843054,0.019269666968831693,2000,0.41566778017947209-0.50393004519551976=-0.08826226501604767,-1,-6,4,2000,7-8=-1,-0.023809523809523808,-0.14705882352941177,0.097560975609756101,2000,(7-8)/42=-0.023809523809523808,-1.4109232769830946,-5.8114759427828355,3.3888491547464228,2000,7-8.4109232769830946=-1.4109232769830946,-0.41092327698309461,-5.0130689206762034,4.9883289986996102,2000,8-8.4109232769830946=-0.41092327698309461
B1_TFIDF,A3_new_RF_and_B,pooled,3812,233,35,52,46.698038123452477,-0.048342321146123024,-0.096732134403146361,0.0055683093552534625,2000,0.44139934069386633-0.48974166183998935=-0.048342321146123024,-17,-32,-2,2000,35-52=-17,-0.072961373390557943,-0.136160575789539,-0.0085460992907801479,2000,(35-52)/233=-0.072961373390557943,-11.698038123452477,-22.104406698744587,-0.88015125518994797,2000,35-46.698038123452477=-11.698038123452477,5.3019618765475229,-6.5061044626079498,18.101852498423636,2000,52-46.698038123452477=5.3019618765475229
QUEUE_BOOTSTRAP_METHOD seed=42, 2000 paired essay resamples within each displayed scope; fixed scores and original fold queues; no reranking/refit/budget recomputation. Excess-vs-random uses each original fold rate k_f/n_f times the resampled large-error labels. Pooled essay draws are not stratified by fold. AUC uses exact weighted tied ranks, first draw checked against direct repeated rows. CIs condition on fitted OOF models, not retraining.
OLD_SHARED_ERROR_SET_UNDER_NEW_SOURCE (fixed means both B target errors strictly <1; >=1 remains wrong)
source,scope,A3_old,also_wrong_under_B,fixed_B_max_error_lt_1,B_max_error_exactly_1,also_wrong_share,fixed_share,arithmetic
B1_TFIDF,fold1,52,40,12,0,0.76923076923076927,0.23076923076923078,40+12=52; also_wrong=40/52=0.76923076923076927; fixed=12/52=0.23076923076923078
B1_TFIDF,fold2,71,53,18,0,0.74647887323943662,0.25352112676056338,53+18=71; also_wrong=53/71=0.74647887323943662; fixed=18/71=0.25352112676056338
B1_TFIDF,fold3,56,39,17,0,0.6964285714285714,0.30357142857142855,39+17=56; also_wrong=39/56=0.6964285714285714; fixed=17/56=0.30357142857142855
B1_TFIDF,fold4,49,36,13,0,0.73469387755102045,0.26530612244897961,36+13=49; also_wrong=36/49=0.73469387755102045; fixed=13/49=0.26530612244897961
B1_TFIDF,fold5,48,35,13,0,0.72916666666666663,0.27083333333333331,35+13=48; also_wrong=35/48=0.72916666666666663; fixed=13/48=0.27083333333333331
B1_TFIDF,pooled,276,203,73,0,0.73550724637681164,0.26449275362318841,203+73=276; also_wrong=203/276=0.73550724637681164; fixed=73/276=0.26449275362318841
POOLED_EVIDENCE_FOR_FINAL_INTERPRETATION
source,anchor,n,K,k,caught_new,expected,exact_p_new,caught_old,new_excess_random_CI_low,new_excess_random_CI_high,new_minus_old_caught,new_minus_old_caught_CI_low,new_minus_old_caught_CI_high,AUROC_new,AUROC_new_CI_low,AUROC_new_CI_high,AUROC_new_minus_old,AUROC_delta_CI_low,AUROC_delta_CI_high
B1_TFIDF,A1_RF_anchor,3812,386,764,81,77.362908429580997,0.33383425043706638,88,-11.576430473628498,19.65027696366187,-7,-27,14,0.51234010568375332,0.48240820631542469,0.54340708629504686,-0.0039691901914346017,-0.043085814621392562,0.03662922546256539
B1_TFIDF,A3_new_RF_and_B,3812,233,764,35,46.698038123452477,0.98282421164695211,52,-22.104406698744587,-0.88015125518994797,-17,-32,-2,0.44139934069386633,0.40493615222838175,0.48174540494043083,-0.048342321146123024,-0.096732134403146361,0.0055683093552534625
LIMITATIONS exploratory, unadjusted comparisons; same development reused. Hypergeometric p uses a random-queue reference conditional on labels and fold budgets; pooled convolution assumes independent fold reference draws. Overlapping OOF training sets and prompt clustering are not modeled by ordinary essay-bootstrap CIs. TF-IDF is a different representation, not proof of statistical independence from feature inputs.
READ_AUDIT data/03_clean_ready_to_use/model_train_3128.csv SHA256=a56c0f3d195a3708f8ec74ca8dfabe125325050af14868a59ea571290658884e
READ_AUDIT data/03_clean_ready_to_use/validation_783.csv SHA256=7b80be5447dd8adadbecf6f492a4320f3e74c7290f91a99e11d43f5951a80e8e
READ_AUDIT outputs/phase6/feature_schema.json SHA256=77204d8b647522a497e459ce797fc1a433e0e5547993a9ddf83af5d8273ab620
READ_AUDIT reports/week9/t3_eligible_development.csv SHA256=f5649b7d2a85348b25945ec49592aed162bd3c1ab16422242696399dea9d1307
READ_AUDIT reports/week9/t3_fold_composition.csv SHA256=de596a84028e42b8aa0c605c523ee98eef87b6b74127a63b0c8e822d0e0629ea
READ_GUARD artifact_reads=5; allowlisted_only=True; blocked_attempts=0; no Test file opened; inputs_unchanged=True; configurations_unchanged=True; no prediction/model files saved; no essay text printed.
```

All eight TF-IDF-versus-feature signed-error correlations and their 95% essay-bootstrap intervals are below 0.95. For RF-anchor errors, D_new caught 81/386 against expected 77.362908429580997 (one-sided exact p=0.33383425043706638), versus old D at 88/386; the paired caught difference is -7, 95% CI [-27,14], and D_new AUROC is 0.51234010568375332, 95% CI [0.48240820631542469,0.54340708629504686]. For RF-and-B1 shared errors, D_new caught 35/233 against expected 46.698038123452477 (one-sided exact p=0.98282421164695211), versus old D at 52/233; the paired caught difference is -17, 95% CI [-32,-2], and D_new AUROC is 0.44139934069386633, 95% CI [0.40493615222838175,0.48174540494043083]. D_new does not demonstrate better-than-random or better-than-old-D selection on either anchor. Of the 276 old RF/Ridge shared-error essays, 203 remain large errors under B1 and 73 have both B1 target errors below 1.0. These are exploratory reused-development results; the intervals condition on fitted OOF models and do not account for prompt clustering or retraining.

```text
APPEND_ONLY_PREVIOUS_BYTES_UNCHANGED=True; previous_report_SHA256=f39ccc10cadb12ee91c11eeed830e68350116a5b25fb4169006c0ae00ab276f0
SCRIPT_UNCHANGED_SINCE_BEFORE_FIRST_FIT=True; SHA256=28a1063e6ab2111318bf275876a98f5b28d63d073d0320c0ee9ebe4f22da44ac
GREP ^READ_AUDIT .*test matches=0; five-file read allowlist; blocked_attempts=0.
```
