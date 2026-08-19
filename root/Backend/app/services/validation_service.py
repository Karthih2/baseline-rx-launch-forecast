"""
Data Validation service.

Responsible for step 2 of the pipeline: validate uploaded files and
required fields, check data types, missing values, Rx history, and
scenario inputs. Every function either returns cleanly or raises
ValidationError with a full list of human-readable issues (we collect
all problems instead of failing on the first one, so the caller gets
one actionable error response).
"""
from typing import Dict, List

import numpy as np
import pandas as pd

from app.config import (
    REQUIRED_FEATURE_COLUMNS,
    REQUIRED_NEW_WEEKLY_RX_COLUMNS,
    REQUIRED_ANALOG_MONTHLY_RX_COLUMNS,
    REQUIRED_SCENARIO_FIELDS,
    SCENARIO_NAMES,
)
from app.models.schemas import ValidationError


def _check_required_columns(df: pd.DataFrame, required: List[str], label: str) -> List[str]:
    issues = []
    missing = [c for c in required if c not in df.columns]
    if missing:
        issues.append(f"{label}: missing required column(s): {missing}")
    return issues


def _check_no_fully_empty(df: pd.DataFrame, label: str) -> List[str]:
    if df is None or df.empty:
        return [f"{label}: file is empty"]
    return []


def validate_new_drug_features(df: pd.DataFrame) -> List[str]:
    issues = []
    issues += _check_no_fully_empty(df, "new_drug_features")
    if issues:
        return issues
    issues += _check_required_columns(df, REQUIRED_FEATURE_COLUMNS, "new_drug_features")
    if len(df) != 1:
        issues.append(
            f"new_drug_features: expected exactly 1 row describing the new drug, found {len(df)}"
        )
    if "target_population" in df.columns:
        bad = df[pd.to_numeric(df["target_population"], errors="coerce").isna()]
        if not bad.empty:
            issues.append("new_drug_features: 'target_population' must be numeric")
    for col in REQUIRED_FEATURE_COLUMNS:
        if col in df.columns and df[col].isna().any():
            issues.append(f"new_drug_features: missing value(s) in required column '{col}'")
    return issues


def validate_analog_features(df: pd.DataFrame) -> List[str]:
    issues = []
    issues += _check_no_fully_empty(df, "analog_features")
    if issues:
        return issues
    issues += _check_required_columns(df, REQUIRED_FEATURE_COLUMNS, "analog_features")
    if len(df) < 1:
        issues.append("analog_features: at least 1 analog drug is required")
    if "drug_id" in df.columns and df["drug_id"].duplicated().any():
        dupes = df.loc[df["drug_id"].duplicated(), "drug_id"].tolist()
        issues.append(f"analog_features: duplicate drug_id values found: {dupes}")
    if "target_population" in df.columns:
        bad = df[pd.to_numeric(df["target_population"], errors="coerce").isna()]
        if not bad.empty:
            issues.append("analog_features: 'target_population' must be numeric for all rows")
    for col in REQUIRED_FEATURE_COLUMNS:
        if col in df.columns and df[col].isna().any():
            issues.append(f"analog_features: missing value(s) in required column '{col}'")
    return issues


def validate_new_weekly_rx(df: pd.DataFrame, new_drug_id: str) -> List[str]:
    """New-drug weekly Rx is allowed to be empty (pure launch, no history yet),
    but if provided it must satisfy the contract."""
    issues = []
    if df is None or df.empty:
        return issues  # empty is acceptable -- forecast falls back to pure analog+bass
    issues += _check_required_columns(df, REQUIRED_NEW_WEEKLY_RX_COLUMNS, "new_drug_weekly_rx")
    if issues:
        return issues
    if not (df["drug_id"] == new_drug_id).all():
        issues.append(
            "new_drug_weekly_rx: 'drug_id' values must all match the new drug's drug_id "
            f"('{new_drug_id}')"
        )
    if pd.to_numeric(df["week_number"], errors="coerce").isna().any():
        issues.append("new_drug_weekly_rx: 'week_number' must be numeric")
    if pd.to_numeric(df["rx_count"], errors="coerce").isna().any():
        issues.append("new_drug_weekly_rx: 'rx_count' must be numeric")
    elif (pd.to_numeric(df["rx_count"], errors="coerce") < 0).any():
        issues.append("new_drug_weekly_rx: 'rx_count' cannot be negative")
    return issues


def validate_analog_monthly_rx(df: pd.DataFrame, valid_analog_ids: set) -> List[str]:
    issues = []
    issues += _check_no_fully_empty(df, "analog_monthly_rx")
    if issues:
        return issues
    issues += _check_required_columns(df, REQUIRED_ANALOG_MONTHLY_RX_COLUMNS, "analog_monthly_rx")
    if issues:
        return issues
    if pd.to_numeric(df["month_number"], errors="coerce").isna().any():
        issues.append("analog_monthly_rx: 'month_number' must be numeric")
    if pd.to_numeric(df["rx_count"], errors="coerce").isna().any():
        issues.append("analog_monthly_rx: 'rx_count' must be numeric")
    unknown_ids = set(df["drug_id"].unique()) - valid_analog_ids
    if unknown_ids:
        issues.append(
            f"analog_monthly_rx: found Rx history for drug_id(s) not present in "
            f"analog_features: {sorted(unknown_ids)}"
        )
    ids_with_history = set(df["drug_id"].unique()) & valid_analog_ids
    if not ids_with_history:
        issues.append("analog_monthly_rx: no Rx history rows match any known analog drug_id")
    return issues


def validate_scenario_assumptions(scenarios: Dict) -> List[str]:
    """Validate either the backend's six-factor numeric contract or the
    supplied Stage-8 reference contract (market_size_adjustment_pct plus
    Fast/Normal/Slow adoption speed and optional qualitative fields)."""
    issues = []
    if not isinstance(scenarios, dict):
        return ["scenario_assumptions: must be a JSON object keyed by scenario name"]

    missing_scenarios = [s for s in SCENARIO_NAMES if s not in scenarios]
    if missing_scenarios:
        issues.append(f"scenario_assumptions: missing scenario(s): {missing_scenarios}")

    for name, cfg in scenarios.items():
        if name not in SCENARIO_NAMES:
            issues.append(
                f"scenario_assumptions: unknown scenario '{name}' "
                f"(expected one of {SCENARIO_NAMES})"
            )
            continue
        if not isinstance(cfg, dict):
            issues.append(f"scenario_assumptions['{name}']: must be an object")
            continue

        has_reference_contract = "market_size_adjustment_pct" in cfg
        if has_reference_contract:
            pct = cfg.get("market_size_adjustment_pct")
            if not isinstance(pct, (int, float)):
                try:
                    float(pct)
                except (TypeError, ValueError):
                    issues.append(
                        f"scenario_assumptions['{name}']['market_size_adjustment_pct']: must be numeric"
                    )
            speed = cfg.get("adoption_speed_multiplier")
            if not isinstance(speed, (int, float, str)):
                issues.append(
                    f"scenario_assumptions['{name}']['adoption_speed_multiplier']: must be numeric or Fast/Normal/Slow"
                )
            elif isinstance(speed, str) and speed.title() not in {"Fast", "Normal", "Slow"}:
                try:
                    float(speed)
                except (TypeError, ValueError):
                    issues.append(
                        f"scenario_assumptions['{name}']['adoption_speed_multiplier']: expected Fast, Normal, Slow or numeric"
                    )
            continue

        missing_fields = [f for f in REQUIRED_SCENARIO_FIELDS if f not in cfg]
        if missing_fields:
            issues.append(f"scenario_assumptions['{name}']: missing field(s): {missing_fields}")
        for f in REQUIRED_SCENARIO_FIELDS:
            if f not in cfg:
                continue
            value = cfg[f]
            if f == "adoption_speed_multiplier":
                if not isinstance(value, (int, float, str)):
                    issues.append(
                        f"scenario_assumptions['{name}']['{f}']: must be numeric or Fast/Normal/Slow"
                    )
            elif not isinstance(value, (int, float)):
                issues.append(f"scenario_assumptions['{name}']['{f}']: must be numeric")
        if "peak_penetration" in cfg and isinstance(cfg["peak_penetration"], (int, float)):
            if not (0 < cfg["peak_penetration"] <= 1):
                issues.append(
                    f"scenario_assumptions['{name}']['peak_penetration']: must be in (0, 1]"
                )
    return issues


def run_full_validation(
    new_features: pd.DataFrame,
    analog_features: pd.DataFrame,
    new_weekly_rx: pd.DataFrame,
    analog_monthly_rx: pd.DataFrame,
    scenario_assumptions: Dict,
) -> None:
    """Runs every validator and raises a single ValidationError with all
    accumulated issues if any are found. Raises nothing on success."""
    issues: List[str] = []
    issues += validate_new_drug_features(new_features)
    issues += validate_analog_features(analog_features)

    new_drug_id = None
    if not issues and "drug_id" in new_features.columns and len(new_features) == 1:
        new_drug_id = str(new_features["drug_id"].iloc[0])
        issues += validate_new_weekly_rx(new_weekly_rx, new_drug_id)

    if "drug_id" in analog_features.columns:
        valid_ids = set(analog_features["drug_id"].astype(str).unique())
        issues += validate_analog_monthly_rx(analog_monthly_rx, valid_ids)

    issues += validate_scenario_assumptions(scenario_assumptions)

    if issues:
        raise ValidationError(issues)
