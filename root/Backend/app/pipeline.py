"""End-to-end forecasting pipeline with the supplied Stage-8 reference logic."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

import numpy as np
import pandas as pd

from app.config import DEFAULT_FORECAST_HORIZON_MONTHS, DEFAULT_TOP_K, DEFAULT_SCENARIOS
from app.services import (
    validation_service,
    preprocessing_service,
    feature_engineering_service,
    similarity_service,
    analog_curve_service,
    bass_model_service,
    scenario_service,
    csv_export_service,
)


def run_forecast_pipeline(
    new_drug_features: pd.DataFrame,
    analog_features: pd.DataFrame,
    new_drug_weekly_rx: pd.DataFrame,
    analog_monthly_rx: pd.DataFrame,
    scenario_assumptions: Optional[Dict] = None,
    top_k: int = DEFAULT_TOP_K,
    horizon_months: int = DEFAULT_FORECAST_HORIZON_MONTHS,
    run_id: Optional[str] = None,
) -> Dict:
    run_id = run_id or uuid.uuid4().hex[:12]
    uploaded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    scenario_assumptions = scenario_assumptions or DEFAULT_SCENARIOS
    warnings = []

    if horizon_months < 1:
        raise ValueError("horizon_months must be >= 1")

    validation_service.run_full_validation(
        new_drug_features,
        analog_features,
        new_drug_weekly_rx,
        analog_monthly_rx,
        scenario_assumptions,
    )

    new_drug_id = str(new_drug_features["drug_id"].iloc[0])
    new_drug_name = str(new_drug_features["drug_name"].iloc[0])

    new_features_clean = preprocessing_service.clean_dataframe(new_drug_features)
    analog_features_clean = preprocessing_service.clean_dataframe(analog_features)
    new_weekly_clean = preprocessing_service.clean_dataframe(new_drug_weekly_rx)
    analog_monthly_clean = preprocessing_service.clean_dataframe(analog_monthly_rx)

    # Stage-8 reference: aggregate the new drug's weekly early data to monthly.
    known_monthly = bass_model_service.aggregate_weekly_to_monthly(
        new_weekly_clean.rename(columns={"week_number": "week_number", "rx_count": "rx_count"})
        if not new_weekly_clean.empty
        else new_weekly_clean
    )
    if len(known_monthly) > horizon_months:
        warnings.append(
            f"Observed early history has {len(known_monthly)} complete months; "
            f"forecast horizon is {horizon_months}. Outputs are capped at the requested horizon."
        )
        known_monthly = known_monthly[:horizon_months]
    if len(known_monthly) == 0:
        warnings.append(
            "No early Rx history provided for the new drug -- scenarios are forecast from the analog/Bass model alone."
        )

    # Feature engineering and top-5 analog selection remain from the existing backend.
    new_vector, analog_matrix, analog_ids = feature_engineering_service.build_feature_matrix(
        new_features_clean, analog_features_clean
    )
    ranked = similarity_service.rank_analogs_by_similarity(new_vector, analog_matrix, analog_ids)
    selected = similarity_service.select_top_k(ranked, top_k=top_k)
    name_lookup = dict(
        zip(analog_features_clean["drug_id"].astype(str), analog_features_clean["drug_name"])
    )
    selected["drug_name"] = selected["drug_id"].map(name_lookup)

    analog_curves = preprocessing_service.prepare_analog_monthly_curves(analog_monthly_clean)
    selected_with_history = selected[
        selected["drug_id"].astype(str).isin(analog_curves.keys())
    ].copy()
    if selected_with_history.empty:
        raise validation_service.ValidationError(
            ["None of the top-K selected analogs have Rx history in analog_monthly_rx."]
        )
    if len(selected_with_history) < len(selected):
        dropped = set(selected["drug_id"]) - set(selected_with_history["drug_id"])
        warnings.append(
            f"Selected analog(s) {sorted(dropped)} had no Rx history and were excluded from curve blending."
        )

    # Existing analog blending becomes the analog_weighted_curve referenced by Stage 8.
    analog_weighted = analog_curve_service.build_blended_curve(
        analog_curves,
        selected_with_history,
        min_length=max(horizon_months, len(known_monthly), 1),
    ).astype(float)
    analog_weighted_curve = analog_weighted.to_numpy(dtype=float)

    # If there is no observed history, the Stage-8 calibration fit cannot be defined;
    # retain a neutral calibration and fit on the analog shape so the API remains usable.
    if len(known_monthly) > 0:
        calibrated_curve, calibration_factor = bass_model_service.calibrate_analog_curve(
            known_monthly, analog_weighted_curve
        )
        base_p, base_q, base_m = bass_model_service.fit_bass(calibrated_curve[: len(known_monthly)])
    else:
        calibration_factor = 1.0
        calibrated_curve = analog_weighted_curve.copy()
        # Reference fit requires known months; for an empty actual history use the
        # first available analog shape with the same fitting math rather than inventing a new model.
        base_p, base_q, base_m = bass_model_service.fit_bass(calibrated_curve)

    # Reproduce Stage-8 blend weight calculation using the fitted Bass curve over known months.
    if len(known_monthly) > 0:
        bass_full = bass_model_service.bass_forecast_months(
            base_p, base_q, base_m, 0, max(horizon_months, len(known_monthly))
        )
        bass_known_fit = bass_full[: len(known_monthly)]
        base_weight = bass_model_service.compute_blend_weight(
            known_monthly, calibrated_curve, bass_known_fit
        )
    else:
        base_weight = 0.5

    base_fit = {
        "calibration_factor": float(calibration_factor),
        "bass_p": float(base_p),
        "bass_q": float(base_q),
        "bass_m": float(base_m),
        "blend_weight_analog": float(base_weight),
        "blend_weight_bass": float(1.0 - base_weight),
    }

    scenario_results = scenario_service.build_scenario_results(
        known_monthly,
        analog_weighted_curve,
        horizon_months,
        base_p,
        base_q,
        base_m,
        calibration_factor,
        base_weight,
        scenario_assumptions,
    )

    # Directional market size for the Stage-8 KPI. Prefer an explicit market_size
    # column; otherwise fall back to target_population (shared logic with
    # csv_export_service so both layers agree on the same value).
    market_size = csv_export_service.market_size_from_features(new_features_clean)

    output_paths = csv_export_service.export_all(
        run_id=run_id,
        new_drug_id=new_drug_id,
        new_drug_name=new_drug_name,
        selected_df=selected_with_history,
        known_monthly=known_monthly,
        scenario_results=scenario_results,
        scenario_assumptions=scenario_assumptions,
        base_fit=base_fit,
        horizon_months=horizon_months,
        market_size=market_size,
        uploaded_at=uploaded_at,
    )

    return {
        "run_id": run_id,
        "new_drug_id": new_drug_id,
        "new_drug_name": new_drug_name,
        "selected_model": csv_export_service.SELECTED_MODEL_NAME,
        "uploaded_at": uploaded_at,
        "forecast_horizon_months": horizon_months,
        "top_k": top_k,
        "known_monthly_rx": known_monthly.tolist(),
        "selected_analogs": selected_with_history.to_dict(orient="records"),
        "blended_analog_curve": analog_weighted_curve.tolist(),
        "base_bass_params": base_fit,
        "scenario_results": scenario_results,
        "scenario_assumptions_used": scenario_assumptions,
        "output_files": output_paths,
        "warnings": warnings,
    }
