"""
HTTP-facing router. Thin wrapper around app.pipeline.run_forecast_pipeline --
all business logic lives in the services, this file only handles
upload parsing, HTTP errors, and file downloads.

Exactly 3 inputs, per the production data contract:
  1. new_drug_dataset          -- .csv, .json, or .zip: new drug static
                                    features (required) + optional early
                                    weekly Rx history. A plain .csv is fine
                                    here since Rx history is optional (one
                                    required table). To include Rx history,
                                    upload .json: {"features": {...},
                                    "weekly_rx": [...]}.
  2. analog_dataset             -- .json or .zip: analog static features +
                                    analog monthly Rx history (BOTH
                                    required). A single .csv can't hold two
                                    differently-shaped tables, so this one
                                    needs .json: {"features": [...],
                                    "monthly_rx": [...]}, or a .zip with
                                    analog_features.csv + analog_monthly_rx.csv.
  3. model_market_assumptions   -- JSON file: bull/base/bear assumptions
                                    (market_size_multiplier, peak_penetration,
                                    adoption_speed_multiplier,
                                    competition_factor, payer_access_factor,
                                    promotion_factor)

Top-5 analog selection and the 12-month horizon are fixed by the production
spec, not user-tunable inputs, so they are no longer separate form fields --
they come from app.config's DEFAULT_TOP_K / DEFAULT_FORECAST_HORIZON_MONTHS.
"""
import json
from typing import Optional

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import (
    ANALOG_DATASET_REQUIRED_FILES,
    DEFAULT_FORECAST_HORIZON_MONTHS,
    DEFAULT_SCENARIOS,
    DEFAULT_TOP_K,
    NEW_DRUG_DATASET_OPTIONAL_FILES,
    NEW_DRUG_DATASET_REQUIRED_FILES,
    OUTPUT_DIR,
)
from app.models.schemas import ValidationError
from app.pipeline import run_forecast_pipeline
from app.utils.file_utils import read_dataset_upload, read_json_upload

router = APIRouter(prefix="/api/v1/forecast", tags=["forecast"])


@router.post("/run")
async def run_forecast(
    new_drug_dataset: UploadFile = File(
        ...,
        description=(
            "New drug data. Accepts .csv (new_drug_features only -- fine "
            "since Rx history is optional), .json "
            '(e.g. {"features": {...one row...}, "weekly_rx": [...]}), '
            "or .zip (new_drug_features.csv + optional new_drug_weekly_rx.csv)."
        ),
    ),
    analog_dataset: UploadFile = File(
        ...,
        description=(
            "Analog drug data -- needs BOTH static features and monthly Rx "
            "history, so a plain .csv won't work here. Accepts .json "
            '(e.g. {"features": [...many rows...], "monthly_rx": [...]}) '
            "or .zip (analog_features.csv + analog_monthly_rx.csv)."
        ),
    ),
    model_market_assumptions: UploadFile = File(
        ...,
        description=(
            "JSON file with bull/base/bear assumptions, using the exact "
            "parameter names/ranges/defaults from the assumptions control "
            "panel: market_size_multiplier, peak_penetration, "
            "adoption_speed_multiplier, competition_factor, "
            "payer_access_factor, promotion_factor."
        ),
    ),
):
    """Runs the full pipeline end to end: validation -> preprocessing ->
    feature engineering -> similarity -> analog curve -> Bass model ->
    scenario analysis -> forecast -> final_forecast.csv + final_forecast.json."""
    try:
        new_drug_files = await read_dataset_upload(
            new_drug_dataset,
            required_files=NEW_DRUG_DATASET_REQUIRED_FILES,
            optional_files=NEW_DRUG_DATASET_OPTIONAL_FILES,
            label="new_drug_dataset",
        )
        analog_files = await read_dataset_upload(
            analog_dataset,
            required_files=ANALOG_DATASET_REQUIRED_FILES,
            label="analog_dataset",
        )
        scenario_assumptions = await read_json_upload(model_market_assumptions)

        result = run_forecast_pipeline(
            new_drug_features=new_drug_files["features"],
            analog_features=analog_files["features"],
            new_drug_weekly_rx=new_drug_files.get("weekly_rx", pd.DataFrame()),
            analog_monthly_rx=analog_files["monthly_rx"],
            scenario_assumptions=scenario_assumptions,
            top_k=DEFAULT_TOP_K,
            horizon_months=DEFAULT_FORECAST_HORIZON_MONTHS,
        )
        return result

    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"issues": e.issues})
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid model_market_assumptions: {e}")
    except Exception as e:  # pragma: no cover - safety net
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")


@router.get("/download/{run_id}/{filename}")
async def download_output_file(run_id: str, filename: str):
    path = OUTPUT_DIR / run_id / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    media_type = "application/json" if filename.endswith(".json") else "text/csv"
    return FileResponse(path, filename=filename, media_type=media_type)


@router.get("/assumptions-defaults")
async def get_assumptions_defaults():
    """Convenience endpoint so a frontend can pre-populate the model/market
    assumptions control panel with sensible starting values (still fully
    editable by the user -- these are never hard-coded into the pipeline
    math itself)."""
    return DEFAULT_SCENARIOS
