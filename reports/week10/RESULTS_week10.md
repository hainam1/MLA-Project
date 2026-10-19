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
