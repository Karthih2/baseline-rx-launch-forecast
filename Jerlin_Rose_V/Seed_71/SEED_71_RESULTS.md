# Seed 71 — RX Forecasting Experiment

## Experiment Configuration

- Seed: 71
- Historical analog drugs: 35
- New drug: 1
- Scenario records: 3

---
Active code page: 65001

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>cd "C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN"

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python --version
Python 3.14.4

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python generate_datasets.py --seed 71 --outdir ./data_seed71
Wrote 35 analog drugs, 1 new drug, 3 scenarios to 'data_seed71/'

Exit Criteria Check
------------------------------------------------------------
[PASS] 35 analog drugs generated
[PASS] Each analog drug has 12 static features + rx_curve
[PASS] Each analog rx_curve has 36 months
[PASS] New drug has 12 static features + early_rx
[PASS] New drug early_rx has 18-26 weekly points
[PASS] 3 scenario rows with 6 assumption fields each
[PASS] All Drug IDs unique and joinable (Table A <-> Table B)
------------------------------------------------------------
ALL CHECKS PASSED

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python validate_data.py
======================================================================
STEP 2 — DATA INGESTION & VALIDATION
======================================================================

Loading datasets...
[OK] data_seed71\analog_drugs.json
[OK] data_seed71\new_drug.json
[OK] data_seed71\scenario_assumptions.json

======================================================================
1. DATASET DIMENSIONS
======================================================================
Analog drugs      : 35
New products      : 1
Scenario records  : 3

======================================================================
2. EXPECTED COUNTS
======================================================================
[PASS] 35 historical analog drugs
[PASS] 1 new drug object
[PASS] 3 scenario records

======================================================================
3. AVAILABLE KEYS
======================================================================

Analog drug keys:
  - drug_id
  - drug_name
  - mechanism_of_action
  - route_of_administration
  - target_specialty
  - market_size
  - competitive_density
  - payer_restrictiveness
  - launch_quarter
  - promotional_intensity
  - special_designation
  - price_tier
  - rx_curve

New drug keys:
  - drug_id
  - drug_name
  - mechanism_of_action
  - route_of_administration
  - target_specialty
  - market_size
  - competitive_density
  - payer_restrictiveness
  - launch_quarter
  - promotional_intensity
  - special_designation
  - price_tier
  - early_rx

Scenario keys:
  - scenario_id
  - market_size_adjustment_pct
  - peak_penetration_ceiling
  - adoption_speed_multiplier
  - competitive_entry_flag
  - payer_access_trend
  - promotional_spend_trend

======================================================================
4. DATA TYPES
======================================================================

Analog drug data types:
  drug_id                        str
  drug_name                      str
  mechanism_of_action            str
  route_of_administration        str
  target_specialty               str
  market_size                    int
  competitive_density            int
  payer_restrictiveness          int
  launch_quarter                 str
  promotional_intensity          int
  special_designation            bool
  price_tier                     int

  rx_curve:
    month                        int
    rx                           int

New drug data types:
  drug_id                        str
  drug_name                      str
  mechanism_of_action            str
  route_of_administration        str
  target_specialty               str
  market_size                    int
  competitive_density            int
  payer_restrictiveness          int
  launch_quarter                 str
  promotional_intensity          int
  special_designation            bool
  price_tier                     int

  early_rx:
    week                         int
    rx                           int

======================================================================
5. MISSING VALUES
======================================================================

Analog records with missing values: 0
New drug missing values: None
Scenario Base missing: ['competitive_entry_flag']
Scenario records with missing values: 1

======================================================================
6. DUPLICATE IDs
======================================================================
[PASS] No duplicate analog drug IDs

======================================================================
7. UNIQUE IDs
======================================================================
Unique analog IDs: 35
New drug ID: NEW_001

======================================================================
8. RX OBSERVATION COUNTS
======================================================================
ANL_001    Rx observations: 36
ANL_002    Rx observations: 36
ANL_003    Rx observations: 36
ANL_004    Rx observations: 36
ANL_005    Rx observations: 36
ANL_006    Rx observations: 36
ANL_007    Rx observations: 36
ANL_008    Rx observations: 36
ANL_009    Rx observations: 36
ANL_010    Rx observations: 36
ANL_011    Rx observations: 36
ANL_012    Rx observations: 36
ANL_013    Rx observations: 36
ANL_014    Rx observations: 36
ANL_015    Rx observations: 36
ANL_016    Rx observations: 36
ANL_017    Rx observations: 36
ANL_018    Rx observations: 36
ANL_019    Rx observations: 36
ANL_020    Rx observations: 36
ANL_021    Rx observations: 36
ANL_022    Rx observations: 36
ANL_023    Rx observations: 36
ANL_024    Rx observations: 36
ANL_025    Rx observations: 36
ANL_026    Rx observations: 36
ANL_027    Rx observations: 36
ANL_028    Rx observations: 36
ANL_029    Rx observations: 36
ANL_030    Rx observations: 36
ANL_031    Rx observations: 36
ANL_032    Rx observations: 36
ANL_033    Rx observations: 36
ANL_034    Rx observations: 36
ANL_035    Rx observations: 36

Minimum analog Rx observations: 36
Maximum analog Rx observations: 36
[PASS] Every analog has 36 monthly Rx observations

======================================================================
9. NEW DRUG EARLY Rx
======================================================================
New drug ID: NEW_001
Weekly observations: 22
[PASS] New drug has 18–26 weekly observations

======================================================================
10. CHRONOLOGICAL ORDER
======================================================================
[PASS] All analog Rx curves are ordered Month 1 → Month 36
[PASS] New drug weekly Rx is chronologically ordered

======================================================================
11. INVALID Rx VALUES
======================================================================
[PASS] No negative or non-numeric Rx values

======================================================================
12. NUMERICAL RANGES
======================================================================
Market size                    min=214,277.00 max=2,983,244.00
Competitive density            min=1.00 max=5.00
Payer restrictiveness          min=1.00 max=5.00
Promotional intensity          min=1.00 max=5.00
Price tier                     min=1.00 max=5.00

======================================================================
13. CATEGORICAL DISTRIBUTIONS
======================================================================

Mechanism of Action
  Complement C5 inhibitor: 2
  TNF-alpha inhibitor: 3
  CGRP antagonist: 3
  Anti-CD20 monoclonal antibody: 2
  IL-17 inhibitor: 2
  mTOR inhibitor: 4
  Dopamine agonist: 1
  ACE inhibitor: 1
  PCSK9 inhibitor: 1
  SGLT2 inhibitor: 1
  Integrin antagonist: 2
  Proton pump inhibitor: 2
  Tyrosine kinase inhibitor: 2
  Beta-2 agonist: 2
  GLP-1 agonist: 2
  PD-1 inhibitor: 2
  Factor Xa inhibitor: 2
  DPP-4 inhibitor: 1

Route of Administration
  Oral: 7
  Injectable: 3
  Intravenous: 9
  Topical: 8
  Inhaled: 5
  Subcutaneous: 3

Target Specialty
  Neurology: 4
  Psychiatry: 3
  Cardiology: 4
  Nephrology: 3
  Primary Care: 2
  Rheumatology: 3
  Endocrinology: 1
  Gastroenterology: 3
  Dermatology: 6
  Oncology: 3
  Pulmonology: 1
  Hematology: 2

Launch Quarter
  Q1: 6
  Q3: 13
  Q4: 6
  Q2: 10

Special Designation
  False: 30
  True: 5

======================================================================
FINAL VALIDATION SUMMARY
======================================================================
Checks passed: 5/5

 DATA INGESTION & VALIDATION PASSED
The Seed-71 datasets are ready for the next stage.

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python preprocess_data.py 
======================================================================
STEP 3 — DATA PREPROCESSING
======================================================================

Loading Seed-71 data...
[OK] Analog drugs loaded
[OK] New drug loaded
[OK] Scenario data loaded

Missing values after preprocessing:

Analog static:
drug_id                    0
drug_name                  0
mechanism_of_action        0
route_of_administration    0
target_specialty           0
market_size                0
competitive_density        0
payer_restrictiveness      0
launch_quarter             0
promotional_intensity      0
special_designation        0
price_tier                 0
dtype: int64

Analog Rx:
drug_id    0
month      0
rx         0
dtype: int64

New drug static:
drug_id                    0
drug_name                  0
mechanism_of_action        0
route_of_administration    0
target_specialty           0
market_size                0
competitive_density        0
payer_restrictiveness      0
launch_quarter             0
promotional_intensity      0
special_designation        0
price_tier                 0
dtype: int64

New drug Rx:
drug_id    0
week       0
rx         0
dtype: int64

Scenarios:
scenario_id                   0
market_size_adjustment_pct    0
peak_penetration_ceiling      0
adoption_speed_multiplier     0
competitive_entry_flag        1
payer_access_trend            0
promotional_spend_trend       0
dtype: int64

======================================================================
PREPROCESSING SUMMARY
======================================================================
Analog static rows : 35
Analog Rx rows     : 1260
New drug static    : 1
New drug Rx rows   : 22
Scenario rows      : 3

Generated files:
[OK] processed_data\analog_static.csv
[OK] processed_data\analog_rx.csv
[OK] processed_data\new_drug_static.csv
[OK] processed_data\new_drug_rx.csv
[OK] processed_data\scenarios.csv

======================================================================
STEP 3 PREPROCESSING COMPLETE
======================================================================

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python analog_selection.py
======================================================================
STEP 4 + 5 — ANALOG SIMILARITY & TOP-5 SELECTION
======================================================================

Loading processed data...
[OK] Analog drugs loaded: 35
[OK] New drug loaded: 1

Preparing static features...
Encoding categorical features...
Scaling numerical features...

Final feature vector size: 46

Calculating cosine similarity...

======================================================================
ALL 35 ANALOGS — SIMILARITY RANKING
======================================================================
 rank drug_id  drug_name  similarity_score
    1 ANL_024   Onyxmune          0.621671
    2 ANL_009  Glimzumab          0.534298
    3 ANL_013    Xelprel          0.480910
    4 ANL_033   Kynzumab          0.399604
    5 ANL_020  Amarapara          0.386017
    6 ANL_034   Zoralith          0.306826
    7 ANL_015 Kestrapara          0.230596
    8 ANL_027   Haloflux          0.213173
    9 ANL_018  Nurotinib          0.152907
   10 ANL_026    Calaxen          0.149554
   11 ANL_028 Solixzumab          0.122773
   12 ANL_029  Perinmune          0.122027
   13 ANL_005  Brentinib          0.062257
   14 ANL_004    Kynprel          0.036503
   15 ANL_023    Kynvara          0.019118
   16 ANL_001   Onyxsera          0.015197
   17 ANL_032  Jovexdine          0.000262
   18 ANL_012    Vynprel         -0.006104
   19 ANL_011   Nuroprel         -0.010232
   20 ANL_010  Lumispara         -0.048351
   21 ANL_002  Amaraflux         -0.061211
   22 ANL_008   Brengene         -0.070514
   23 ANL_014   Haloprel         -0.097686
   24 ANL_031   Trexdine         -0.123481
   25 ANL_021   Glimtide         -0.140598
   26 ANL_006   Nuroflux         -0.167036
   27 ANL_030  Jovexflux         -0.172677
   28 ANL_007    Vynmune         -0.180212
   29 ANL_035   Zoravara         -0.192471
   30 ANL_025    Kyntide         -0.210202
   31 ANL_003   Nuromune         -0.218452
   32 ANL_019    Kyngene         -0.231069
   33 ANL_022 Ferrozumab         -0.292170
   34 ANL_016   Vyntinib         -0.300351
   35 ANL_017  Perinprel         -0.340794

======================================================================
🏆 TOP 5 ANALOG DRUGS
======================================================================
 rank drug_id drug_name  similarity_score
    1 ANL_024  Onyxmune          0.621671
    2 ANL_009 Glimzumab          0.534298
    3 ANL_013   Xelprel          0.480910
    4 ANL_033  Kynzumab          0.399604
    5 ANL_020 Amarapara          0.386017

======================================================================
ANALOG SELECTION COMPLETE
======================================================================
Total analogs evaluated : 35
Top analogs selected    : 5

Generated files:
[OK] processed_data\analog_similarity_scores.csv
[OK] processed_data\top5_analogs.csv

======================================================================
STEP 4 + STEP 5 COMPLETE
======================================================================

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python feature_engineering.py
======================================================================
STEP 6 — FEATURE ENGINEERING
======================================================================

Loading processed datasets...
[OK] Analog static: 35 rows
[OK] Analog Rx: 1260 rows
[OK] New drug static: 1 row
[OK] New drug Rx: 22 rows
[OK] Top analogs: 5

======================================================================
1. NEW-DRUG FEATURES
======================================================================
Latest Rx          : 42447.00
Previous Rx        : 39129.00
Growth rate        : 0.0848
Cumulative Rx      : 755666.00
Rolling mean       : 40688.50
Early growth slope : 665.34

======================================================================
2. TOP-5 ANALOG RX DATA
======================================================================
[OK] Retrieved Rx curves for 5 top analogs

Top-5 analog engineered features:
drug_id  similarity_score  analog_mean_rx  analog_weighted_rx  analog_growth_rate  analog_peak_rx  analog_month_to_peak  analog_variability
ANL_024          0.621671    80781.083333        95564.620120            2.178021        126402.0                    34        26643.676787
ANL_009          0.534298    29428.277778        39247.343844           11.933642         59036.0                    35        17621.553521
ANL_013          0.480910   156259.027778       206555.441441           10.116824        296419.0                    36        90217.950244
ANL_033          0.399604    94834.833333       124808.881381           18.521403        164175.0                    36        54485.075093
ANL_020          0.386017   135648.416667       179169.225225           10.055843        262643.0                    35        78298.045685

======================================================================
3. AGGREGATING TOP-5 ANALOG FEATURES
======================================================================

======================================================================
4. FINAL FEATURE VECTOR
======================================================================
drug_id                              NEW_001
latest_rx                            42447.0
previous_rx                          39129.0
rx_growth_rate                      0.084796
cumulative_rx                       755666.0
rolling_mean_rx                      40688.5
early_growth_slope                665.341615
top_analog_similarity                 0.4845
analog_mean_rx                  95499.766275
analog_weighted_rx             123323.238085
analog_growth_rate                  9.856913
analog_peak_rx                 173235.788532
analog_month_to_peak                35.10685
analog_variability              50097.950187
market_size                           814309
competitive_density                        2
payer_restrictiveness                      2
promotional_intensity                      2
special_designation                     True
price_tier                                 4
mechanism_of_action      Factor Xa inhibitor
route_of_administration              Inhaled
target_specialty                   Neurology
launch_quarter                            Q2

======================================================================
FEATURE ENGINEERING COMPLETE
======================================================================
Final feature count: 23
[OK] processed_data\engineered_features.csv
[OK] processed_data\analog_engineered_features.csv

======================================================================
STEP 6 COMPLETE
======================================================================

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python weekly_monthly_alignment.py
======================================================================
STEP 7 — WEEKLY → MONTHLY Rx ALIGNMENT
======================================================================

Loading weekly new-drug Rx data...
[OK] Weekly observations loaded: 22
[OK] Week range: 1 → 22
[PASS] Weeks are continuous
[PASS] No missing Rx values
[PASS] No negative Rx values

Assigning weekly observations to monthly buckets...

======================================================================
WEEKLY → MONTHLY ALIGNMENT
======================================================================
 month  first_week  last_week  weeks_observed  monthly_rx  is_partial_month  monthly_rx_4week_equivalent
     1           1          4               4    112206.0             False                     112206.0
     2           5          8               4    124955.0             False                     124955.0
     3           9         12               4    136467.0             False                     136467.0
     4          13         16               4    142238.0             False                     142238.0
     5          17         20               4    158224.0             False                     158224.0
     6          21         22               2     81576.0              True                     163152.0

======================================================================
ALIGNMENT VALIDATION
======================================================================
Total weekly Rx : 755,666.00
Total monthly Rx: 755,666.00
[PASS] Monthly aggregation preserves total observed Rx
[INFO] Partial month(s): [6]

======================================================================
STEP 7 COMPLETE
======================================================================
Weekly observations : 22
Monthly observations: 6
Partial month(s)    : 1

[OK] processed_data\new_drug_monthly_rx.csv
[OK] processed_data\rx_alignment_summary.csv

======================================================================

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python eda.py
======================================================================
STEP 8 — EXPLORATORY DATA ANALYSIS
======================================================================

Loading processed datasets...
[OK] Analog static: 35 rows
[OK] Analog Rx: 1260 rows
[OK] New drug weekly Rx: 22 rows
[OK] New drug monthly Rx: 6 rows
[OK] Top-5 analogs: 5

======================================================================
1. BASIC Rx STATISTICS
======================================================================

Analog Rx statistics:
count      1260.000000
mean     178359.635714
std      168090.572675
min        4325.000000
25%       62047.500000
50%      127662.000000
75%      239111.000000
max      959770.000000
Name: rx, dtype: float64

New drug weekly Rx statistics:
count       22.000000
mean     34348.454545
std       4599.585745
min      25897.000000
25%      30891.750000
50%      34463.000000
75%      37789.500000
max      42447.000000
Name: rx, dtype: float64

New drug monthly Rx statistics:
count         6.000000
mean     125944.333333
std       26744.930560
min       81576.000000
25%      115393.250000
50%      130711.000000
75%      140795.250000
max      158224.000000
Name: monthly_rx, dtype: float64

Creating analog Rx distribution plot...
Creating new-drug Rx distribution plot...
Creating analog launch curves...
Creating top-5 analog launch curves...
Creating new-drug weekly Rx curve...
Creating new-drug monthly Rx curve...
Creating categorical plot: mechanism_of_action
Creating categorical plot: route_of_administration
Creating categorical plot: target_specialty
Creating categorical plot: launch_quarter
Creating numerical plot: market_size
Creating numerical plot: competitive_density
Creating numerical plot: payer_restrictiveness
Creating numerical plot: promotional_intensity
Creating numerical plot: price_tier

Creating numerical correlation matrix...

Correlation matrix:
                       market_size  ...  price_tier
market_size               1.000000  ...    0.107255
competitive_density      -0.245633  ...   -0.087247
payer_restrictiveness    -0.060111  ...    0.174307
promotional_intensity     0.005740  ...   -0.016614
price_tier                0.107255  ...    1.000000

[5 rows x 5 columns]
Creating market size vs Rx plot...
Creating top-5 vs new-drug comparison...
Saving descriptive statistics...

======================================================================
EDA COMPLETE
======================================================================
EDA outputs saved to: eda

Generated visualizations include:
[OK] Analog Rx distribution
[OK] New-drug Rx distribution
[OK] 35 analog launch curves
[OK] Top-5 analog curves
[OK] New-drug weekly curve
[OK] New-drug monthly curve
[OK] Categorical distributions
[OK] Numerical distributions
[OK] Correlation matrix
[OK] Market size vs mean Rx
[OK] New drug vs top-5 analogs

======================================================================
STEP 8 COMPLETE
======================================================================

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python time_validation.py 
======================================================================
STEP 9 — TIME-AWARE VALIDATION SETUP
======================================================================

Loading analog monthly Rx data...
[OK] Loaded 1260 Rx observations
[OK] Number of analog drugs: 35

Validating monthly histories...
[PASS] Every analog has exactly 36 months

Creating rolling-origin validation splits...

======================================================================
ROLLING-ORIGIN SPLITS
======================================================================
split_id  train_start  train_end  validation_start  validation_end
 split_1            1         18                19              24
 split_2            1         24                25              30
 split_3            1         30                31              36

======================================================================
SPLIT VALIDATION
======================================================================
[PASS] split_1: train=18, validation=6
[PASS] split_2: train=24, validation=6
[PASS] split_3: train=30, validation=6

Checking temporal ordering...
[PASS] No temporal overlap between training and validation periods
[PASS] Training data always precedes validation data

Creating validation timeline...

======================================================================
STEP 9 COMPLETE
======================================================================
Validation strategy: Rolling-Origin
Number of splits: 3
Validation horizon per split: 6 months

Split 1: Train 1–18  → Validate 19–24
Split 2: Train 1–24  → Validate 25–30
Split 3: Train 1–30  → Validate 31–36

[OK] validation\rolling_origin_splits.csv
[OK] validation\validation_records.csv
[OK] validation\validation_timeline.png

======================================================================

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python -m pip install statsmodels scipy
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: statsmodels in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (0.14.6)
Requirement already satisfied: scipy in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (1.18.0)
Requirement already satisfied: numpy<3,>=1.22.3 in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (from statsmodels) (2.5.1)
Requirement already satisfied: pandas!=2.1.0,>=1.4 in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (from statsmodels) (3.0.3)
Requirement already satisfied: patsy>=0.5.6 in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (from statsmodels) (1.0.2)
Requirement already satisfied: packaging>=21.3 in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (from statsmodels) (26.2)
Requirement already satisfied: python-dateutil>=2.8.2 in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (from pandas!=2.1.0,>=1.4->statsmodels) (2.9.0.post0)
Requirement already satisfied: tzdata in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (from pandas!=2.1.0,>=1.4->statsmodels) (2026.3)
Requirement already satisfied: six>=1.5 in C:\Users\JESHWIN RAJ\AppData\Roaming\Python\Python314\site-packages (from python-dateutil>=2.8.2->pandas!=2.1.0,>=1.4->statsmodels) (1.17.0)

[notice] A new release of pip is available: 26.0.1 -> 26.2.1
[notice] To update, run: python.exe -m pip install --upgrade pip

C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>
C:\Users\JESHWIN RAJ\Downloads\RX_FORCASTING_JERLIN>python model_training.py
================================================================================
STEP 10 — SIX FORECASTING MODELS
================================================================================

Loading data...
[OK] Historical drugs : 35
[OK] Historical Rx rows: 1260
[OK] Validation splits: 3

================================================================================
ROLLING-ORIGIN BACKTEST
================================================================================

split_1: Train 1–18 → Validate 19–24

split_2: Train 1–24 → Validate 25–30

split_3: Train 1–30 → Validate 31–36

================================================================================
MODEL-WISE BACKTEST PERFORMANCE
================================================================================
                 model     MAE_mean      MAE_std    RMSE_mean     RMSE_std  MAPE_mean  MAPE_std  sMAPE_mean  sMAPE_std  MASE_mean  MASE_std     R2_mean     R2_std  Accuracy_mean  Precision_mean  Recall_mean  F1_mean
                 ARIMA 22419.214373 19576.747861 25840.904812 21878.621320   9.125491  3.982350    9.698089   4.517571   2.522745  1.057632   -3.429723   5.653607       1.000000        1.000000     1.000000 1.000000
                 Naive 24592.593651 21434.141495 28094.422124 23967.949840  10.092441  4.848823   10.902814   5.618847   2.783230  1.261765   -3.512899   3.675406       1.000000        1.000000     1.000000 1.000000
Analog + Bass Adaptive 40567.570307 75477.623042 43263.161099 77128.601414  11.452615  9.855294   12.663450  12.663871   2.983618  2.313979  -11.628716  27.631078       0.995238        1.000000     0.995238 0.996825
                  Bass 44140.422278 81579.497184 47840.180147 84714.428063  12.537052 11.837950   14.463111  15.687640   3.248929  2.711935  -26.663194 102.220126       0.973016        0.990476     0.973016 0.978499
  Analog + Bass Static 62313.838266 65461.609242 63973.901273 66143.714466  35.318879 40.007124   28.684989  22.846268   9.849713 11.731859  -88.108240 196.985206       0.995238        1.000000     0.995238 0.997229
           Analog-Only 81994.692442 64599.910802 83394.029213 64532.927556  54.886673 68.906346   38.414330  30.027733  15.496886 20.153921 -234.194499 565.825836       1.000000        1.000000     1.000000 1.000000

================================================================================
MODEL RANKING
================================================================================
1. ARIMA | MASE=2.5227 | RMSE=25840.90 | sMAPE=9.70%
2. Naive | MASE=2.7832 | RMSE=28094.42 | sMAPE=10.90%
3. Analog + Bass Adaptive | MASE=2.9836 | RMSE=43263.16 | sMAPE=12.66%
4. Bass | MASE=3.2489 | RMSE=47840.18 | sMAPE=14.46%
5. Analog + Bass Static | MASE=9.8497 | RMSE=63973.90 | sMAPE=28.68%
6. Analog-Only | MASE=15.4969 | RMSE=83394.03 | sMAPE=38.41%

WINNER: ARIMA
MASE : 2.5227
RMSE : 25840.90
sMAPE: 9.70%

================================================================================
GENERALIZATION ANALYSIS
================================================================================

Naive
  Mean validation MAE : 24592.59
  Mean validation MASE: 2.7832
  Conclusion: POSSIBLE UNDERPERFORMANCE
  Reason: MASE >= 1 means the model does not consistently beat the naive benchmark.

ARIMA
  Mean validation MAE : 22419.21
  Mean validation MASE: 2.5227
  Conclusion: POSSIBLE UNDERPERFORMANCE
  Reason: MASE >= 1 means the model does not consistently beat the naive benchmark.

Analog-Only
  Mean validation MAE : 81994.69
  Mean validation MASE: 15.4969
  Conclusion: POSSIBLE UNDERPERFORMANCE
  Reason: MASE >= 1 means the model does not consistently beat the naive benchmark.

Bass
  Mean validation MAE : 44140.42
  Mean validation MASE: 3.2489
  Conclusion: POSSIBLE UNDERPERFORMANCE
  Reason: MASE >= 1 means the model does not consistently beat the naive benchmark.

Analog + Bass Static
  Mean validation MAE : 62313.84
  Mean validation MASE: 9.8497
  Conclusion: POSSIBLE UNDERPERFORMANCE
  Reason: MASE >= 1 means the model does not consistently beat the naive benchmark.

Analog + Bass Adaptive
  Mean validation MAE : 40567.57
  Mean validation MASE: 2.9836
  Conclusion: POSSIBLE UNDERPERFORMANCE
  Reason: MASE >= 1 means the model does not consistently beat the naive benchmark.

================================================================================
STEP 10 COMPLETE
================================================================================
[OK] Evaluated 6 models
[OK] Historical drugs: 35
[OK] Rolling validation windows: 3
[OK] Selected model: ARIMA

Generated files:
[OK] models/rolling_backtest_results.csv
[OK] models/rolling_predictions.csv
[OK] models/model_comparison.csv
[OK] models/selected_model.csv

================================================================================
