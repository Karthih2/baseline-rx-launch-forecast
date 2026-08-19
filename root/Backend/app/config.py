"""
Central configuration for the Drug Launch Forecasting backend.

Keeping all "data contract" constants here (required columns, defaults,
scenario keys) is what makes the pipeline reusable: a new user can point
the API at a differently-named drug / analog dataset without touching
any service code, as long as the CSVs follow this contract.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_DATA_DIR = BASE_DIR / "sample_data"

# ---------------------------------------------------------------------------
# Required columns (the "data contract")
# ---------------------------------------------------------------------------
# Static feature files (new drug: one row. analogs: many rows.)
REQUIRED_FEATURE_COLUMNS = [
    "drug_id",
    "drug_name",
    "therapeutic_area",
    "route_of_administration",
    "line_of_therapy",
    "mechanism_of_action",
    "target_population",       # numeric: addressable patient population
]

# Optional but recommended numeric/categorical static features used to
# improve similarity matching if present in the uploaded file.
OPTIONAL_NUMERIC_FEATURES = [
    "competitor_count",
    "avg_treatment_duration_months",
    "list_price_monthly_usd",
    "peak_analog_rx",
]
OPTIONAL_CATEGORICAL_FEATURES = [
    "orphan_status",
    "chronic_or_acute",
    "payer_restriction_level",
]

# Weekly Rx history for the NEW drug (early launch data, can be short/empty)
REQUIRED_NEW_WEEKLY_RX_COLUMNS = ["drug_id", "week_number", "rx_count"]

# Monthly Rx history for ANALOG drugs (full post-launch curves)
REQUIRED_ANALOG_MONTHLY_RX_COLUMNS = ["drug_id", "month_number", "rx_count"]

# ---------------------------------------------------------------------------
# Dataset bundle contract (zip uploads)
# ---------------------------------------------------------------------------
# The API surface exposes exactly 3 inputs: new_drug_dataset, analog_dataset,
# and model_market_assumptions. The first two are .zip uploads bundling the
# static-feature CSV together with the Rx-history CSV, since those two files
# have different schemas and can't be merged into one CSV without inventing
# a new format. Filenames inside each zip must match these exactly (case-
# insensitive, any folder prefix is stripped).
NEW_DRUG_DATASET_REQUIRED_FILES = {"features": "new_drug_features.csv"}
NEW_DRUG_DATASET_OPTIONAL_FILES = {"weekly_rx": "new_drug_weekly_rx.csv"}

ANALOG_DATASET_REQUIRED_FILES = {
    "features": "analog_features.csv",
    "monthly_rx": "analog_monthly_rx.csv",
}

# Scenario assumptions contract
SCENARIO_NAMES = ["bull", "base", "bear"]
REQUIRED_SCENARIO_FIELDS = [
    "market_size_multiplier",   # scales addressable market / ceiling (m)
    "peak_penetration",         # fraction of target population captured at peak
    "adoption_speed_multiplier",# scales Bass p+q (how fast diffusion happens)
    "competition_factor",       # >1 helps, <1 hurts (affects m and q)
    "payer_access_factor",      # >1 helps, <1 hurts (affects m)
    "promotion_factor",         # >1 helps, <1 hurts (affects p, innovation rate)
]

# ---------------------------------------------------------------------------
# Pipeline defaults (overridable per-request; nothing here is hard-coded
# into the scenario math itself -- these are just fallback defaults)
# ---------------------------------------------------------------------------
DEFAULT_TOP_K = 5
DEFAULT_FORECAST_HORIZON_MONTHS = 12
WEEKS_PER_MONTH = 4.345  # standard pharma convention (52 weeks / 12 months)

# Bass model fitting bounds
BASS_P_BOUNDS = (1e-4, 0.5)
BASS_Q_BOUNDS = (1e-4, 0.9)

DEFAULT_SCENARIOS = {
    "bull": {
        "market_size_multiplier": 1.20,
        "peak_penetration": 0.35,
        "adoption_speed_multiplier": 1.20,
        "competition_factor": 1.10,
        "payer_access_factor": 1.10,
        "promotion_factor": 1.15,
    },
    "base": {
        "market_size_multiplier": 1.00,
        "peak_penetration": 0.25,
        "adoption_speed_multiplier": 1.00,
        "competition_factor": 1.00,
        "payer_access_factor": 1.00,
        "promotion_factor": 1.00,
    },
    "bear": {
        "market_size_multiplier": 0.80,
        "peak_penetration": 0.15,
        "adoption_speed_multiplier": 0.80,
        "competition_factor": 0.90,
        "payer_access_factor": 0.90,
        "promotion_factor": 0.85,
    },
}
