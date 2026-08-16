# Overfit Check Notes (auto-generated)

Generated: 2026-08-16T07:50:44


**Best model (primary metric — LOO mean MASE across 6 models / 35 analogs):** analog_bass_static (MASE mean=0.497, std=0.263)


This is the recommended metric for model selection: it's averaged over 35 independent analog drugs, so a single lucky/unlucky split can't dominate it the way it can in the single-drug backtest below.



## Backtest on the new drug (single split — illustrative only, NOT the model-selection criterion)

**Caveat:** this section is based on a single train/test split (train months 1-3, predict months 4-5) on ONE drug. With only 2 held-out points, a very low MAE/MASE here can easily be a lucky calibration rather than a generalizable result — treat it as a sanity check, not proof of the best model. Use the LOO result above for the actual decision.


Lowest single-split backtest MASE: analog_bass_static (MASE=0.012, n=2 held-out points)


- **naive**: consistently over-forecasting (Bias is a large share of MAE); negative R2 -- worse than predicting the mean; expected/noted, don't over-read R2 here

- **arima**: consistently over-forecasting (Bias is a large share of MAE); negative R2 -- worse than predicting the mean; expected/noted, don't over-read R2 here

- **analog_only**: consistently over-forecasting (Bias is a large share of MAE); negative R2 -- worse than predicting the mean; expected/noted, don't over-read R2 here

- **bass_only**: high MASE relative to naive -- more flexible model not earning its complexity here; consistently over-forecasting (Bias is a large share of MAE); negative R2 -- worse than predicting the mean; expected/noted, don't over-read R2 here

- **analog_bass_static**: consistently under-forecasting (Bias is a large share of MAE)

- **analog_bass_adaptive**: consistently under-forecasting (Bias is a large share of MAE)


## LOO validation across 35 analogs (stability check)

| model | MASE mean | MASE std | MAE mean | MAE std |
|---|---|---|---|---|
| analog_bass_adaptive | 0.520 | 0.277 | 19410.7 | 21342.6 |
| analog_bass_static | 0.497 | 0.263 | 18461.3 | 20045.9 |
| analog_only | 0.506 | 0.351 | 16073.7 | 15647.5 |
| arima | 0.939 | 0.092 | 30863.6 | 24822.3 |
| bass_only | 0.820 | 0.221 | 25142.1 | 18717.3 |
| naive | 1.000 | 0.000 | 33060.4 | 27442.8 |

**High MASE_std relative to MASE_mean means the model does great on some analogs and terrible on others -- that's overfitting to specific analog shapes, not a generalizable pattern. Prefer a model with a slightly worse mean but a much smaller std over one with the best mean but a huge spread.**



## Training fit vs. backtest error (overfitting check)

| model | training MAE (in-sample, months 1-3) | backtest MAE (out-of-sample, months 4-5) | ratio |
|---|---|---|---|
| naive | 64147.5 | 51628.0 | 0.80x |
| arima | 64147.5 | 51628.0 | 0.80x |
| analog_only | 33081.5 | 16703.8 | 0.50x |
| bass_only | 16358.1 | 138111.9 | 8.44x |
| analog_bass_static | 33741.7 | 603.9 | 0.02x |
| analog_bass_adaptive | 34244.3 | 6380.9 | 0.19x |

**A high ratio (backtest error much bigger than training error) means the model fits the months it already saw far better than it predicts new ones -- classic overfitting. A ratio near 1x means the model generalizes about as well as it fits.**


- **bass_only**: backtest error is 8.4x its training-window error -- strong overfitting signal, treat its backtest score with caution