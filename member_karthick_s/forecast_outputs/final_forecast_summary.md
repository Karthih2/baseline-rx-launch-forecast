# Final Forecast Summary

Generated: 2026-08-16T19:47:30


**Model:** analog_bass_static (selected via Stage 6 LOO validation across 35 analogs � mean MASE 0.497, std 0.263)


**Known months observed:** 5 (from 22 weeks of early Rx)


**Scenario assumptions source:** `01_data/scenario_assumptions.json`


## Scenario comparison (12-month horizon)

| scenario | peak month | peak Rx | month-12 Rx | 12mo cumulative Rx | avg forecast MoM growth |
|---|---|---|---|---|---|
| bull | 12 | 675832 | 675832 | 6408298 | 2.92% |
| base | 12 | 568641 | 568641 | 5649964 | 3.46% |
| bear | 3 | 476050 | 463575 | 4938673 | 3.92% |

**Scenario spread at month 12:** Bull +18.9% vs Base, Bear -18.5% vs Base


## Scenario qualitative context (not quantitatively modeled)

| scenario | competitive entry | payer access trend | promo spend trend |
|---|---|---|---|
| bull | False | Improving | Ramping |
| base | None | Static | Sustained |
| bear | True | Worsening | Tapering |

These three fields come straight from scenario_assumptions.json but are NOT currently converted into a number that moves the forecast -- there's no established rule for e.g. how much 'payer access improving' should shift the curve. Treat them as narrative context for the brand team, not inputs the model has already accounted for.


**Assumption note:** ceiling and speed multipliers are derived directly from `market_size_adjustment_pct` and `adoption_speed_multiplier` in `01_data/scenario_assumptions.json` (Fast/Normal/Slow -> 1.1/1.0/0.9x speed). They are not statistically fitted -- there is only one new drug, so scenario magnitude can't be estimated from data. Treat Bull/Bear as directional planning bounds, not confidence intervals.
