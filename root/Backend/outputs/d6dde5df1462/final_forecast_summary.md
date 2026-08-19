# Final Forecast Summary
Generated: 2026-08-19T14:00:34+00:00

**Run ID:** `d6dde5df1462`

**Drug:** NEWDRUG_001 — Zorvatide

**Model:** analog_bass_static (selected via Stage 6 LOO validation across 35 analogs — mean MASE 0.497, std 0.263)

**Known months observed:** 2

## Scenario comparison (12-month horizon)
| scenario | peak month | peak Rx | month-12 Rx | 12mo cumulative Rx | avg forecast MoM growth |
|---|---:|---:|---:|---:|---:|
| bull | 6 | 2553 | 830 | 20759 | -7.05% |
| base | 6 | 2172 | 778 | 18268 | -5.56% |
| bear | 7 | 1792 | 720 | 15706 | -4.0% |

**Scenario spread at month 12:** Bull +6.7% vs Base, Bear -7.5% vs Base

## Top-5 analogs

| rank | id | name | similarity | weight |
|---:|---|---|---:|---:|
| 1 | ANALOG_E | Odaphex | 0.9666 | 0.2555 |
| 2 | ANALOG_A | Kinovex | 0.9640 | 0.2548 |
| 3 | ANALOG_C | Maravex | 0.6966 | 0.1842 |
| 4 | ANALOG_B | Trellonib | 0.6802 | 0.1798 |
| 5 | ANALOG_D | Sentrolix | 0.4754 | 0.1257 |

## Model transparency
- Calibration factor: 0.683379
- Blend weight analog: 0.5000
- Blend weight Bass: 0.5000
- Base Bass p: 0.05118758
- Base Bass q: 0.39523359
- Base Bass m: 13355.93
- Validation: MASE 0.497 across 35 analogs
