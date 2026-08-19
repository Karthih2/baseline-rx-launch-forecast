# Drug Launch Forecasting Backend

A modular **FastAPI** backend that forecasts monthly Rx (prescription) volume for a
new drug launch using an **Analog + Bass Static** approach, with **Bull / Base / Bear**
scenario analysis driven entirely by user-supplied assumptions (nothing scenario-related
is hard-coded).

## Pipeline

```
New Drug + Analog Data + Scenario Assumptions
        │
        ▼
Data Validation            (validation_service.py)
        │
        ▼
Preprocessing               (preprocessing_service.py)
        │
        ▼
Feature Engineering         (feature_engineering_service.py)
        │
        ▼
Cosine Similarity           (similarity_service.py)
        │
        ▼
Top-K Analog Selection      (similarity_service.py)
        │
        ▼
Weighted Analog Curve       (analog_curve_service.py)
        │
        ▼
Analog + Bass Static        (bass_model_service.py)
        │
        ▼
Bull / Base / Bear          (scenario_service.py)
        │
        ▼
N-Month Forecast            (pipeline.py)
        │
        ▼
CSV Output                  (csv_export_service.py)
```

Every box above is its own service module under `app/services/`. `app/pipeline.py` is
the only file that wires them together, and `app/routers/forecast_router.py` is a thin
HTTP wrapper around it — business logic is never duplicated in the router.

## Project layout

```
app/
  config.py                 # data contract, defaults (NOT scenario logic)
  main.py                   # FastAPI app entry point
  pipeline.py                # orchestrates all services end-to-end
  models/
    schemas.py               # pydantic response models + ValidationError
  services/
    validation_service.py
    preprocessing_service.py
    feature_engineering_service.py
    similarity_service.py
    analog_curve_service.py
    bass_model_service.py
    scenario_service.py
    csv_export_service.py
  routers/
    forecast_router.py       # HTTP endpoints
  utils/
    file_utils.py             # upload parsing helpers
sample_data/                 # example CSVs/JSON you can run immediately
outputs/                      # per-run CSV outputs (created at runtime)
requirements.txt
```

## Running it

```bash
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for interactive Swagger docs.

## Endpoints

### `POST /api/v1/forecast/run`
Multipart form with **exactly 3 inputs**. Top-5 analog selection and the
12-month horizon are fixed by the production spec, so they are no longer
separate form fields.

| Field | Accepted formats | Required | Description |
|---|---|---|---|
| `new_drug_dataset` | `.csv`, `.json`, or `.zip` | yes | New drug static features (required) + optional early weekly Rx history |
| `analog_dataset` | `.json` or `.zip` | yes | Analog static features **and** analog monthly Rx history (both required) |
| `model_market_assumptions` | `.json` file | yes | `bull`/`base`/`bear` assumptions |

**Why `analog_dataset` can't be a plain `.csv`:** it always needs two tables
with different columns (features vs. monthly Rx history), and a CSV can only
hold one table. `new_drug_dataset` *can* be a plain `.csv` because its Rx
history is optional — a CSV there is treated as `new_drug_features.csv` alone.

**`.json` format** — a single JSON object keyed by table name, values are
either one record (object) or many records (array of objects), with the
same columns as the equivalent CSV:
```json
// new_drug_dataset.json
{
  "features": {"drug_id": "NEWDRUG_001", "drug_name": "Zorvatide", "...": "..."},
  "weekly_rx": [{"drug_id": "NEWDRUG_001", "week_number": 1, "rx_count": 178.2}, "..."]
}
```
```json
// analog_dataset.json
{
  "features": [{"drug_id": "ANALOG_A", "drug_name": "Kinovex", "...": "..."}, "..."],
  "monthly_rx": [{"drug_id": "ANALOG_A", "month_number": 1, "rx_count": 1324.2}, "..."]
}
```

**`.zip` format** (fallback) — filenames inside must match exactly
(case-insensitive, folder prefixes stripped): `new_drug_features.csv`,
`new_drug_weekly_rx.csv`, `analog_features.csv`, `analog_monthly_rx.csv`.

### `GET /api/v1/forecast/download/{run_id}/{filename}`
Download `final_forecast.csv` or `final_forecast.json` from a completed run.

### `GET /api/v1/forecast/assumptions-defaults`
Returns example Bull/Base/Bear assumption values you can use as a form starting point.

### `GET /health`
Liveness check.

## Data contract

The API takes exactly 3 inputs. `analog_dataset` bundles two tables with
different schemas (static features + Rx history), so it needs `.json` or
`.zip`; `new_drug_dataset` can be a plain `.csv` since its Rx history is
optional. See the `/run` endpoint docs above for exact formats.

### CSV / table formats

**`new_drug_features.csv`** — exactly 1 row:
```
drug_id,drug_name,therapeutic_area,route_of_administration,line_of_therapy,mechanism_of_action,target_population,competitor_count,avg_treatment_duration_months,list_price_monthly_usd,orphan_status,chronic_or_acute,payer_restriction_level
```
Only `drug_id, drug_name, therapeutic_area, route_of_administration, line_of_therapy,
mechanism_of_action, target_population` are required; the rest are optional but improve
similarity matching if present.

**`analog_features.csv`** — same columns, one row per analog drug.

**`new_drug_weekly_rx.csv`** (optional):
```
drug_id,week_number,rx_count
```

**`analog_monthly_rx.csv`** (long format, all analogs together):
```
drug_id,month_number,rx_count
```

**`model_market_assumptions`** (third input, uploaded as a JSON file):
```json
{
  "bull": {"market_size_multiplier":1.2,"peak_penetration":0.35,"adoption_speed_multiplier":1.2,
           "competition_factor":1.1,"payer_access_factor":1.1,"promotion_factor":1.15},
  "base": {"market_size_multiplier":1.0,"peak_penetration":0.25,"adoption_speed_multiplier":1.0,
           "competition_factor":1.0,"payer_access_factor":1.0,"promotion_factor":1.0},
  "bear": {"market_size_multiplier":0.8,"peak_penetration":0.15,"adoption_speed_multiplier":0.8,
           "competition_factor":0.9,"payer_access_factor":0.9,"promotion_factor":0.85}
}
```
All six fields are required for each of `bull`/`base`/`bear`. Nothing here is hard-coded
in the pipeline — `app/config.py::DEFAULT_SCENARIOS` is only a convenience fallback for
demo runs; whatever the caller supplies always takes precedence.

> **Note:** these six parameter names/defaults come from the original JSON contract
> shipped with this backend. The exact slider ranges, min/max, step values, and
> dropdown/toggle options for a UI control panel have not been supplied yet — if you
> have a mockup of that control panel, share it and this contract (and the
> `/assumptions-defaults` response) will be updated to match it exactly, without
> changing the underlying `market_size_multiplier` / `peak_penetration` / ... parameter
> names or the pipeline math.

## Modeling approach (Analog + Bass Static)

1. **Similarity**: static features of the new drug and every analog are one-hot
   encoded (categoricals) and standard-scaled (numerics) jointly, then compared with
   cosine similarity. The top-K most similar analogs are kept, with blend weights
   proportional to (non-negative) similarity.
2. **Blended analog curve**: the selected analogs' monthly Rx curves are aligned to a
   common relative launch month (month 1, 2, 3...) and combined into a single
   weighted-average curve.
3. **Bass fitting**: the blended curve's *cumulative adoption shape* is fit to the Bass
   diffusion model to obtain base coefficients `p` (innovation) and `q` (imitation).
   This is the "static" part — p, q are estimated once from analog shape.
4. **Scenario-adjusted forecast**: for each of Bull/Base/Bear, the market ceiling `m` is
   computed from `target_population × peak_penetration × market_size_multiplier ×
   payer_access_factor`, and `p`/`q` are scaled by `promotion_factor`/`competition_factor`
   and `adoption_speed_multiplier`. The Bass curve is regenerated per scenario.
5. **Blending with actuals**: if the new drug has its own early Rx history, those
   months are used verbatim and a smoothly-decaying correction factor reconciles the
   model curve with reality before it settles back onto the fitted Bass trajectory.

## Final outputs (per run, under `outputs/<run_id>/`)

Exactly two files are written per run — no intermediate/per-stage CSVs:

- **`final_forecast.csv`** — one row per (scenario, forecast_month), for all of
  Bull/Base/Bear × Month 1–12 (36 rows for a 12-month horizon). Columns:
  `drug_id, drug_name, selected_model, scenario, forecast_month, forecast_rx,
  top_analog_rank, top_analog_id, top_analog_name, similarity_score,
  similarity_weight, bass_p, bass_q, bass_m, market_size_multiplier,
  peak_penetration, adoption_speed_multiplier, competition_factor,
  payer_access_factor, promotion_factor`. `top_analog_*`/`similarity_*` reflect
  the single best-matched (rank 1) analog; `bass_p/q/m` are the scenario-adjusted
  parameters used for that row's scenario.
- **`final_forecast.json`** — one object per run: `drug_id`, `drug_name`,
  `selected_model` ("Analog + Bass"), `top_5_analogs` (all Top-K analogs with
  rank/similarity/weight), `assumptions` (the bull/base/bear assumptions used),
  `bass_parameters` (the base fitted `p`/`q` from the analog curve shape, plus
  the Base scenario's market ceiling `m`), and `forecast` (`bull`/`base`/`bear`,
  each a list of `{forecast_month, forecast_rx}` for Month 1–N).

Both paths are printed to stdout at the end of the run and returned in the API
response's `output_files` field.

## Reusability

Nothing about a specific drug, analog set, or scenario is hard-coded anywhere in
`app/`. To forecast a different launch, upload a different `new_drug_dataset.zip`,
`analog_dataset.zip`, and `model_market_assumptions` JSON — no code changes required.
Extra optional columns in your feature CSVs are picked up automatically (see
`OPTIONAL_NUMERIC_FEATURES` / `OPTIONAL_CATEGORICAL_FEATURES` in `app/config.py`).
Top-5 analog selection and the 12-month horizon are fixed by the production spec
(`app/config.py::DEFAULT_TOP_K` / `DEFAULT_FORECAST_HORIZON_MONTHS`).

## Sample data

`sample_data/` contains a ready-to-run example (an oncology drug vs. 6 analogs)
in every accepted format: individual CSVs, `new_drug_dataset.json` /
`analog_dataset.json` bundles, `new_drug_dataset.zip` / `analog_dataset.zip`
archives, and `model_market_assumptions.json`. Use it with the `/docs`
Swagger UI or curl, e.g.:

```bash
# new_drug_dataset as a plain CSV (no early Rx history), analog_dataset as JSON
curl -X POST http://localhost:8000/api/v1/forecast/run \
  -F "new_drug_dataset=@sample_data/new_drug_features.csv;type=text/csv" \
  -F "analog_dataset=@sample_data/analog_dataset.json;type=application/json" \
  -F "model_market_assumptions=@sample_data/model_market_assumptions.json;type=application/json"

# both datasets as JSON
curl -X POST http://localhost:8000/api/v1/forecast/run \
  -F "new_drug_dataset=@sample_data/new_drug_dataset.json;type=application/json" \
  -F "analog_dataset=@sample_data/analog_dataset.json;type=application/json" \
  -F "model_market_assumptions=@sample_data/model_market_assumptions.json;type=application/json"
```

## Stage 8 / dashboard-ready outputs

Each completed run now writes the original forecast artifacts plus the Stage-8 artifacts required by the dashboard:

- `final_forecast_scenarios.csv`: 36 rows for a 12-month horizon (Bull/Base/Bear × Month 1–12), including `run_id`, `drug_id`, `uploaded_at`, `forecast_month`, `forecast_rx`, `type` (`known`/`forecast`), scenario-specific Bass `p/q/m`, calibration factor, and analog/Bass blend weights.
- `final_forecast_kpis.json`: per-scenario peak month/Rx, month-12 Rx, 12-month cumulative Rx, scenario spread around Base, model transparency, assumptions, run identity, and Top-5 analogs.
- `top5_analogs_selected.csv`: exactly five rows when five eligible analogs exist, with rank, analog ID/name, similarity score and similarity weight.
- `final_forecast_summary.md`: readable Stage-8 one-page summary.
- `final_forecast.csv` and `final_forecast.json`: retained for backward compatibility and enriched with the new Stage-8 fields.

The forecasting math follows the supplied Stage-8 reference: constrained SLSQP Bass fitting, the peak-month constraint, analog calibration, error-based analog/Bass blending, scenario ceiling adjustment, Fast/Normal/Slow adoption-speed mapping, and the defensive ceiling floor.
