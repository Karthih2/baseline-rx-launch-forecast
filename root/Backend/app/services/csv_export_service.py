"""Stage-8 / dashboard-ready export service."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import pandas as pd
import numpy as np

from app.config import OUTPUT_DIR

SELECTED_MODEL_NAME = "analog_bass_static"
VALIDATION_BADGE = "MASE 0.497 across 35 analogs"


def _run_dir(run_id: str) -> Path:
    d = OUTPUT_DIR / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _top5(selected_df: pd.DataFrame):
    rows = []
    for _, r in selected_df.sort_values("rank").head(5).iterrows():
        rows.append({
            "top_analog_rank": int(r["rank"]),
            "top_analog_id": str(r["drug_id"]),
            "top_analog_name": None if pd.isna(r.get("drug_name")) else str(r.get("drug_name")),
            "similarity_score": float(r["similarity_score"]),
            "similarity_weight": float(r["weight"]),
        })
    return rows


def _kpis_for_scenario(known_monthly, forecast_values, market_size=None):
    known_monthly = np.asarray(known_monthly, dtype=float)
    forecast_values = np.asarray(forecast_values, dtype=float)
    rx = np.concatenate([known_monthly, forecast_values])
    months = np.arange(1, len(rx) + 1)
    peak_idx = int(np.argmax(rx)) if len(rx) else 0
    forecast_growth = None
    if len(forecast_values) > 1:
        denom = np.where(forecast_values[:-1] == 0, 1, forecast_values[:-1])
        forecast_growth = float(np.mean(np.diff(forecast_values) / denom) * 100)
    total = float(rx.sum())
    capture = None if not market_size else total / float(market_size) * 100
    return {
        "peak_month": int(months[peak_idx]) if len(rx) else None,
        "peak_rx": round(float(rx[peak_idx]), 1) if len(rx) else None,
        "month_12_rx": round(float(rx[-1]), 1) if len(rx) else None,
        "total_12mo_rx_cumulative": round(total, 1),
        "known_months_rx_cumulative": round(float(known_monthly.sum()), 1),
        "forecast_months_rx_cumulative": round(float(forecast_values.sum()), 1),
        "avg_forecast_growth_rate_mom_pct": round(forecast_growth, 2) if forecast_growth is not None else None,
        "market_capture_pct_directional": round(float(capture), 3) if capture is not None else None,
    }


def market_size_from_features(new_drug_features: pd.DataFrame):
    """Prefer an explicit market_size column; otherwise fall back to
    target_population, which is the closest available field in the
    production data contract (new_drug_features.csv has no market_size
    column, only target_population). Returns None if neither is present
    or parseable, so callers can handle "unknown" explicitly rather than
    silently defaulting to 0."""
    if "market_size" in new_drug_features.columns:
        v = pd.to_numeric(new_drug_features["market_size"].iloc[0], errors="coerce")
        if pd.notna(v):
            return float(v)
    if "target_population" in new_drug_features.columns:
        v = pd.to_numeric(new_drug_features["target_population"].iloc[0], errors="coerce")
        if pd.notna(v):
            return float(v)
    return None


def export_all(
    run_id: str,
    new_drug_id: str,
    new_drug_name: str,
    selected_df: pd.DataFrame,
    known_monthly,
    scenario_results: Dict[str, Dict],
    scenario_assumptions: Dict[str, Dict],
    base_fit: Dict[str, float],
    horizon_months: int,
    market_size: float | None = None,
    uploaded_at: str | None = None,
) -> Dict[str, str]:
    out_dir = _run_dir(run_id)
    uploaded_at = uploaded_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    top5 = _top5(selected_df)
    rows = []
    order = ["bull", "base", "bear"]
    for scenario in order:
        result = scenario_results[scenario]
        forecast = result["forecast"]
        params = result["params"]
        raw = result["raw_assumptions"]
        combined = list(known_monthly) + list(forecast)
        for idx in range(min(horizon_months, len(combined))):
            row = {
                "run_id": run_id,
                "drug_id": new_drug_id,
                "drug_name": new_drug_name,
                "uploaded_at": uploaded_at,
                "selected_model": SELECTED_MODEL_NAME,
                "scenario": scenario,
                "forecast_month": idx + 1,
                "forecast_rx": round(float(combined[idx]), 1),
                "type": "known" if idx < len(known_monthly) else "forecast",
                "bass_p": params["p"],
                "bass_q": params["q"],
                "bass_m": params["m"],
                "calibration_factor": params["calibration_factor"],
                "blend_weight_analog": base_fit["blend_weight_analog"],
                "blend_weight_bass": base_fit["blend_weight_bass"],
                "market_size_multiplier": scenario_results[scenario]["ceiling_mult"],
                "market_size_adjustment_pct": raw.get("market_size_adjustment_pct"),
                "peak_penetration": raw.get("peak_penetration"),
                "adoption_speed_multiplier": raw.get("adoption_speed_multiplier"),
                "competition_factor": raw.get("competition_factor"),
                "payer_access_factor": raw.get("payer_access_factor"),
                "promotion_factor": raw.get("promotion_factor"),
                "competitive_entry_flag": raw.get("competitive_entry_flag"),
                "payer_access_trend": raw.get("payer_access_trend"),
                "promotional_spend_trend": raw.get("promotional_spend_trend"),
            }
            rows.append(row)
    final_df = pd.DataFrame(rows)
    csv_path = out_dir / "final_forecast_scenarios.csv"
    final_df.to_csv(csv_path, index=False)

    # Backward-compatible legacy name.
    legacy_csv = out_dir / "final_forecast.csv"
    final_df.to_csv(legacy_csv, index=False)

    top5_df = pd.DataFrame(top5)
    top5_path = out_dir / "top5_analogs_selected.csv"
    top5_df.to_csv(top5_path, index=False)

    kpis = {}
    for scenario in order:
        kpis[scenario] = {
            "ceiling_mult": scenario_results[scenario]["ceiling_mult"],
            "speed_mult": scenario_results[scenario]["speed_mult"],
            "raw_assumptions": scenario_results[scenario]["raw_assumptions"],
            "fitted_params": scenario_results[scenario]["params"],
            "kpis": _kpis_for_scenario(known_monthly, scenario_results[scenario]["forecast"], market_size),
        }
    base_m12 = kpis["base"]["kpis"]["month_12_rx"]
    old_shape_forecast = {}
    for scenario in order:
        monthly = scenario_results[scenario]["forecast"]
        old_shape_forecast[scenario] = [
            {"forecast_month": i + 1, "forecast_rx": float(v)}
            for i, v in enumerate(monthly)
        ]

    kpi_record = {
        # Original final_forecast.json contract (preserved)
        "drug_id": new_drug_id,
        "drug_name": new_drug_name,
        "selected_model": SELECTED_MODEL_NAME,
        "top_5_analogs": top5,
        "assumptions": scenario_assumptions,
        "bass_parameters": {
            "p": base_fit["bass_p"],
            "q": base_fit["bass_q"],
            "m": kpis["base"]["fitted_params"]["m"],
        },
        "forecast": old_shape_forecast,
        # Stage-8 / dashboard additions
        "run_id": run_id,
        "uploaded_at": uploaded_at,
        "generated": uploaded_at,
        "model": SELECTED_MODEL_NAME,
        "n_known_months": len(known_monthly),
        "market_size": market_size,
        "scenario_assumptions_source": "request.model_market_assumptions",
        "validation_badge": VALIDATION_BADGE,
        "base_fit": base_fit,
        "scenarios": kpis,
        "scenario_spread": {
            "bull_vs_base_pct": round((kpis["bull"]["kpis"]["month_12_rx"] / base_m12 - 1) * 100, 1) if base_m12 else None,
            "bear_vs_base_pct": round((kpis["bear"]["kpis"]["month_12_rx"] / base_m12 - 1) * 100, 1) if base_m12 else None,
        },
    }
    kpi_path = out_dir / "final_forecast_kpis.json"
    with open(kpi_path, "w") as f:
        json.dump(kpi_record, f, indent=2, default=str)

    # Stage-8-readable summary.
    md = [
        "# Final Forecast Summary\n",
        f"Generated: {uploaded_at}\n",
        f"\n**Run ID:** `{run_id}`\n",
        f"\n**Drug:** {new_drug_id} — {new_drug_name}\n",
        f"\n**Model:** analog_bass_static (selected via Stage 6 LOO validation across 35 analogs — mean MASE 0.497, std 0.263)\n",
        f"\n**Known months observed:** {len(known_monthly)}\n",
        "\n## Scenario comparison (12-month horizon)\n",
        "| scenario | peak month | peak Rx | month-12 Rx | 12mo cumulative Rx | avg forecast MoM growth |\n",
        "|---|---:|---:|---:|---:|---:|\n",
    ]
    for scenario in order:
        k = kpis[scenario]["kpis"]
        md.append(
            f"| {scenario} | {k['peak_month']} | {k['peak_rx']:.0f} | {k['month_12_rx']:.0f} | {k['total_12mo_rx_cumulative']:.0f} | {k['avg_forecast_growth_rate_mom_pct']}% |\n"
        )
    md.append(
        f"\n**Scenario spread at month 12:** Bull {kpi_record['scenario_spread']['bull_vs_base_pct']:+.1f}% vs Base, Bear {kpi_record['scenario_spread']['bear_vs_base_pct']:+.1f}% vs Base\n"
    )
    md.append("\n## Top-5 analogs\n\n| rank | id | name | similarity | weight |\n|---:|---|---|---:|---:|\n")
    for r in top5:
        md.append(f"| {r['top_analog_rank']} | {r['top_analog_id']} | {r['top_analog_name']} | {r['similarity_score']:.4f} | {r['similarity_weight']:.4f} |\n")
    md.append("\n## Model transparency\n")
    md.append(
        f"- Calibration factor: {base_fit['calibration_factor']:.6f}\n"
        f"- Blend weight analog: {base_fit['blend_weight_analog']:.4f}\n"
        f"- Blend weight Bass: {base_fit['blend_weight_bass']:.4f}\n"
        f"- Base Bass p: {base_fit['bass_p']:.8f}\n"
        f"- Base Bass q: {base_fit['bass_q']:.8f}\n"
        f"- Base Bass m: {base_fit['bass_m']:.2f}\n"
        f"- Validation: {VALIDATION_BADGE}\n"
    )
    md_path = out_dir / "final_forecast_summary.md"
    md_path.write_text("".join(md), encoding="utf-8")

    # Backward-compatible JSON name, enriched with Stage-8 fields.
    json_path = out_dir / "final_forecast.json"
    with open(json_path, "w") as f:
        json.dump(kpi_record, f, indent=2, default=str)

    return {
        "final_forecast_scenarios_csv": str(csv_path),
        "final_forecast_csv": str(legacy_csv),
        "final_forecast_kpis_json": str(kpi_path),
        "final_forecast_json": str(json_path),
        "final_forecast_summary_md": str(md_path),
        "top5_analogs_selected_csv": str(top5_path),
    }
