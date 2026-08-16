"""
STAGE 8 — FINAL FORECAST: 12-MONTH BASE + BULL/BASE/BEAR SCENARIOS + KPIs
===========================================================================
Final deliverable stage. Model selection is complete (Stage 6 LOO validation
across 35 analogs selected analog_bass_static as the winner).

This script:
  1. Re-fits only the winning analog+Bass static model using the same fitting
     logic from 05_train_models.py; no fitting math is changed.
  2. Generates Bull/Base/Bear forecasts from the base fit using the REAL
     scenario assumptions from 01_data/scenario_assumptions.json (Stage 1's
     actual output) -- not hardcoded multipliers. market_size_adjustment_pct
     drives the Bass ceiling (m); adoption_speed_multiplier drives adoption
     speed (p, q). So scenarios differ in level and ramp speed, sourced
     directly from your generated scenario file.
  3. Computes business KPIs: 12-month cumulative Rx, peak month, market
     capture %, and Bull/Bear spread around Base.

Outputs:
  forecast_outputs/final_forecast_scenarios.csv   (month, rx, type, scenario)
  forecast_outputs/final_forecast_kpis.json       (KPIs per scenario)
  forecast_outputs/final_forecast_summary.md      (readable one-pager)
"""

import os
import json
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.optimize import minimize

DATA_DIR = "01_data"
PREP_DIR = "03_preprocessed"
FEAT_DIR = "04_features"
OUT_DIR = "forecast_outputs"
os.makedirs(OUT_DIR, exist_ok=True)

FORECAST_HORIZON = 12
WEEKS_PER_MONTH = 4.345

# Maps the qualitative adoption_speed_multiplier label from
# scenario_assumptions.json to a quantitative multiplier on Bass p, q.
# market_size_adjustment_pct needs no such map -- it's already a number.
ADOPTION_SPEED_MAP = {
    "Fast": 1.10,
    "Normal": 1.00,
    "Slow": 0.90,
}


# ---------------------------------------------------------------------------
# Load real scenario assumptions (Stage 1 output) instead of hardcoding them
# ---------------------------------------------------------------------------
def load_scenario_assumptions(path):
    with open(path) as f:
        rows = json.load(f)

    scenarios = {}
    for row in rows:
        scenario_id = row["scenario_id"].lower()
        pct = row["market_size_adjustment_pct"]
        speed_label = row["adoption_speed_multiplier"]

        if speed_label not in ADOPTION_SPEED_MAP:
            raise ValueError(
                f"Unrecognized adoption_speed_multiplier '{speed_label}' for "
                f"scenario '{row['scenario_id']}' -- add it to ADOPTION_SPEED_MAP."
            )

        scenarios[scenario_id] = {
            "ceiling_mult": 1 + pct / 100,
            "speed_mult": ADOPTION_SPEED_MAP[speed_label],
            # carried through as context, NOT currently modeled quantitatively:
            "raw_assumptions": {
                "market_size_adjustment_pct": pct,
                "peak_penetration_ceiling_label": row.get("peak_penetration_ceiling"),
                "adoption_speed_multiplier_label": speed_label,
                "competitive_entry_flag": row.get("competitive_entry_flag"),
                "payer_access_trend": row.get("payer_access_trend"),
                "promotional_spend_trend": row.get("promotional_spend_trend"),
            },
        }
    return scenarios


# ---------------------------------------------------------------------------
# Fitting logic (lifted from 05_train_models.py -- winning model only)
# ---------------------------------------------------------------------------
def aggregate_weekly_to_monthly(new_curve_long: pd.DataFrame) -> np.ndarray:
    df = new_curve_long.sort_values("week").reset_index(drop=True)
    df["month"] = np.ceil(df["week"] / WEEKS_PER_MONTH).astype(int)
    monthly = df.groupby("month")["rx"].sum()
    full_weeks_needed = monthly.index * WEEKS_PER_MONTH
    max_week = df["week"].max()
    complete_months = monthly.index[full_weeks_needed <= max_week]
    return monthly.loc[complete_months].values.astype(float)


def bass_cumulative(t, p, q, m):
    return m * (1 - np.exp(-(p + q) * t)) / (1 + (q / p) * np.exp(-(p + q) * t))


def bass_peak_month(p, q):
    return np.log(q / p) / (p + q)


def fit_bass(monthly_values: np.ndarray, min_peak_margin: float = 2.5):
    n = len(monthly_values)
    cum = np.cumsum(monthly_values)
    t = np.arange(1, n + 1)
    peak_monthly = max(monthly_values.max(), 1.0)
    cum_scaled = cum / peak_monthly

    p_lo, p_hi = 0.005, 0.25
    q_lo, q_hi = 0.05, 0.75
    m_scaled_lo, m_scaled_hi = 1.5, 25.0
    m_scaled_lo = max(m_scaled_lo, (cum[-1] / peak_monthly) * 1.05)
    if m_scaled_hi <= m_scaled_lo:
        m_scaled_hi = m_scaled_lo * 1.5

    bounds = [(p_lo, p_hi), (q_lo, q_hi), (m_scaled_lo, m_scaled_hi)]
    p0 = np.array([0.03, 0.35, min(max(4.0, m_scaled_lo), m_scaled_hi)])

    def sse_scaled(params):
        p, q, m_scaled = params
        pred = bass_cumulative(t, p, q, m_scaled)
        return np.sum((pred - cum_scaled) ** 2)

    required_peak = n - 1 + min_peak_margin

    def peak_constraint(params):
        p, q, _ = params
        return bass_peak_month(p, q) - required_peak

    try:
        res = minimize(
            sse_scaled, p0, method="SLSQP", bounds=bounds,
            constraints=[{"type": "ineq", "fun": peak_constraint}],
            options={"maxiter": 1000, "ftol": 1e-12},
        )
        p, q, m_scaled = res.x
        m = m_scaled * peak_monthly
        if not res.success or p <= 0 or q <= 0 or not np.all(np.isfinite(res.x)):
            raise ValueError("constrained fit failed")
        return float(p), float(q), float(m)
    except Exception:
        p_fallback, q_fallback = 0.03, 0.30
        for _ in range(50):
            if bass_peak_month(p_fallback, q_fallback) >= required_peak:
                break
            q_fallback *= 0.9
        return p_fallback, q_fallback, peak_monthly * 4.0


def bass_forecast_months(p, q, m, n_known, horizon):
    t_full = np.arange(1, horizon + 1)
    cum_full = bass_cumulative(t_full, p, q, m)
    monthly_full = np.diff(np.concatenate([[0], cum_full]))
    return np.maximum(monthly_full[n_known:], 0)


def calibrate_analog_curve(known_monthly, analog_weighted_curve, clip_pct=(5, 95)):
    n_known = len(known_monthly)
    analog_known = analog_weighted_curve[:n_known]
    analog_known_safe = np.where(analog_known == 0, 1, analog_known)
    ratios = known_monthly / analog_known_safe

    if n_known >= 3:
        lo, hi = np.percentile(ratios, clip_pct)
        ratios = np.clip(ratios, lo, hi)

    calibration_factor = float(np.median(ratios))
    return analog_weighted_curve * calibration_factor, calibration_factor


def compute_blend_weight(known_monthly, analog_calibrated, bass_fitted_known, min_known=2):
    n_known = len(known_monthly)
    if n_known < min_known:
        return 0.5
    analog_err = np.mean(np.abs(known_monthly - analog_calibrated[:n_known]))
    bass_err = np.mean(np.abs(known_monthly - bass_fitted_known[:n_known]))
    if analog_err + bass_err == 0:
        return 0.5
    w_analog = bass_err / (analog_err + bass_err)
    return float(np.clip(w_analog, 0.25, 0.75))


# ---------------------------------------------------------------------------
# Scenario forecast builder
# ---------------------------------------------------------------------------
def build_scenario_forecast(known_monthly, analog_weighted_curve, horizon,
                             base_p, base_q, base_m, base_calibration_factor,
                             base_weight, ceiling_mult=1.0, speed_mult=1.0,
                             min_ceiling_margin=1.02):
    """Apply a scenario's ceiling/speed multiplier to the BASE fit and
    produce that scenario's month-by-month forecast. Known months are
    always the real observed data -- scenarios only change the forward-
    looking forecast, never rewrite history.

    Defensive floor: fit_bass() guarantees base_m >= ~1.05x cumulative
    known Rx (its own m_scaled_lo bound), but only just barely when a
    fit is bound-pinned (documented as happening "routinely" on real,
    noisier data). A Bear ceiling_mult < 1.0 applied to a base_m that's
    already close to that floor can push scenario_m BELOW cumulative
    known Rx -- i.e. imply the market ceiling is smaller than what's
    already been prescribed, which is nonsensical and collapses the
    forecast to near-zero via the np.maximum(...,0) clip downstream.
    Cheap insurance for a drug whose base fit lands close to the floor.
    """
    n_known = len(known_monthly)
    cum_known = float(known_monthly.sum())

    scenario_p = base_p * speed_mult
    scenario_q = base_q * speed_mult
    scenario_m = base_m * ceiling_mult

    min_scenario_m = cum_known * min_ceiling_margin
    if scenario_m < min_scenario_m:
        scenario_m = min_scenario_m

    scenario_calibration = base_calibration_factor * ceiling_mult

    bass_full = bass_forecast_months(scenario_p, scenario_q, scenario_m, 0, horizon)
    bass_shape = bass_full[n_known:horizon]

    analog_forecast = (analog_weighted_curve * scenario_calibration)[n_known:horizon]

    forecast = np.maximum(base_weight * analog_forecast + (1 - base_weight) * bass_shape, 0)
    return forecast, {
        "p": scenario_p, "q": scenario_q, "m": scenario_m,
        "calibration_factor": scenario_calibration,
    }


def make_scenario_df(known_monthly, forecast_values, scenario_name):
    n_known, n_fore = len(known_monthly), len(forecast_values)
    months = np.arange(1, n_known + n_fore + 1)
    rx = np.concatenate([known_monthly, forecast_values])
    types = ["known"] * n_known + ["forecast"] * n_fore
    return pd.DataFrame({
        "month": months, "rx": np.round(rx, 1), "type": types, "scenario": scenario_name
    })


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
def compute_kpis(df_scenario: pd.DataFrame, market_size: float, n_known: int) -> dict:
    rx = df_scenario["rx"].values
    months = df_scenario["month"].values
    forecast_rx = df_scenario.loc[df_scenario["type"] == "forecast", "rx"].values
    known_rx = df_scenario.loc[df_scenario["type"] == "known", "rx"].values

    peak_idx = int(np.argmax(rx))
    peak_month = int(months[peak_idx])
    peak_rx = float(rx[peak_idx])

    total_12mo_rx = float(rx.sum())
    month12_rx = float(rx[-1])

    if len(forecast_rx) > 1:
        mom_growth = np.diff(forecast_rx) / np.where(forecast_rx[:-1] == 0, 1, forecast_rx[:-1])
        avg_forecast_growth_rate_mom = float(np.mean(mom_growth))
    else:
        avg_forecast_growth_rate_mom = None

    market_capture_pct = float(total_12mo_rx / market_size * 100) if market_size else None

    return {
        "peak_month": peak_month,
        "peak_rx": round(peak_rx, 1),
        "month_12_rx": round(month12_rx, 1),
        "total_12mo_rx_cumulative": round(total_12mo_rx, 1),
        "known_months_rx_cumulative": round(float(known_rx.sum()), 1),
        "forecast_months_rx_cumulative": round(float(forecast_rx.sum()), 1),
        "avg_forecast_growth_rate_mom_pct": round(avg_forecast_growth_rate_mom * 100, 2)
            if avg_forecast_growth_rate_mom is not None else None,
        "market_capture_pct_directional": round(market_capture_pct, 3)
            if market_capture_pct is not None else None,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    new_curve = pd.read_csv(os.path.join(PREP_DIR, "new_drug_rx_early_long.csv"))
    new_static = pd.read_csv(os.path.join(PREP_DIR, "new_drug_static_clean.csv"))
    weighted_curve_df = pd.read_csv(os.path.join(FEAT_DIR, "analog_weighted_curve.csv"))
    analog_weighted_curve = weighted_curve_df["analog_weighted_rx"].values.astype(float)
    market_size = float(new_static["market_size"].iloc[0])

    scenario_assumptions = load_scenario_assumptions(
        os.path.join(DATA_DIR, "scenario_assumptions.json")
    )

    known_monthly = aggregate_weekly_to_monthly(new_curve)
    n_known = len(known_monthly)

    print("=" * 60)
    print("STAGE 8 — FINAL FORECAST: BASE FIT + BULL/BASE/BEAR + KPIs")
    print("=" * 60)
    print(f"Winning model: analog_bass_static (selected via Stage 6 LOO validation)")
    print(f"Known months: {n_known}  |  Known Rx: {np.round(known_monthly, 1)}")
    print(f"Forecast horizon: month {n_known + 1} -> month {FORECAST_HORIZON}")
    print(f"\nScenario assumptions loaded from {DATA_DIR}/scenario_assumptions.json:")
    for name, adj in scenario_assumptions.items():
        print(f"  {name}: ceiling_mult={adj['ceiling_mult']:.2f}, "
              f"speed_mult={adj['speed_mult']:.2f}  "
              f"(from market_size_adjustment_pct="
              f"{adj['raw_assumptions']['market_size_adjustment_pct']}, "
              f"adoption_speed_multiplier="
              f"'{adj['raw_assumptions']['adoption_speed_multiplier_label']}')")
    print()

    # --- fit the BASE case once (this is analog_bass_static, unchanged) ---
    calibrated_curve, calibration_factor = calibrate_analog_curve(known_monthly, analog_weighted_curve)
    base_p, base_q, base_m = fit_bass(calibrated_curve[:n_known])
    bass_full = bass_forecast_months(base_p, base_q, base_m, 0, FORECAST_HORIZON)
    bass_known_fit = bass_full[:n_known]
    base_weight = compute_blend_weight(known_monthly, calibrated_curve, bass_known_fit)

    print(f"Base fit: calibration_factor={calibration_factor:.4f}, "
          f"Bass p={base_p:.5f} q={base_q:.5f} m={base_m:.1f}, "
          f"blend weight (analog)={base_weight:.2f} / (bass)={1-base_weight:.2f}\n")

    # --- build all 3 scenarios from that one base fit, using the REAL
    #     scenario_assumptions.json multipliers loaded above ---
    all_rows = []
    kpi_record = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "model": "analog_bass_static",
        "n_known_months": n_known,
        "market_size": market_size,
        "scenario_assumptions_source": os.path.join(DATA_DIR, "scenario_assumptions.json"),
        "base_fit": {
            "calibration_factor": calibration_factor,
            "bass_p": base_p, "bass_q": base_q, "bass_m": base_m,
            "blend_weight_analog": base_weight,
            "blend_weight_bass": 1 - base_weight,
        },
        "scenarios": {},
    }

    for scenario, adj in scenario_assumptions.items():
        forecast_vals, scenario_params = build_scenario_forecast(
            known_monthly, analog_weighted_curve, FORECAST_HORIZON,
            base_p, base_q, base_m, calibration_factor, base_weight,
            ceiling_mult=adj["ceiling_mult"], speed_mult=adj["speed_mult"],
        )
        df_scenario = make_scenario_df(known_monthly, forecast_vals, scenario)
        all_rows.append(df_scenario)

        kpis = compute_kpis(df_scenario, market_size, n_known)
        kpi_record["scenarios"][scenario] = {
            "ceiling_mult": adj["ceiling_mult"],
            "speed_mult": adj["speed_mult"],
            "raw_assumptions": adj["raw_assumptions"],
            "fitted_params": scenario_params,
            "kpis": kpis,
        }

        print(f"[{scenario.upper()}] month {n_known+1}-{FORECAST_HORIZON} forecast: "
              f"{df_scenario[df_scenario['type']=='forecast']['rx'].round(0).tolist()}")
        print(f"    peak_month={kpis['peak_month']}, peak_rx={kpis['peak_rx']:.0f}, "
              f"month12_rx={kpis['month_12_rx']:.0f}, "
              f"12mo_cumulative_rx={kpis['total_12mo_rx_cumulative']:.0f}")

    # --- bull/bear spread around base, at month 12 ---
    base_m12 = kpi_record["scenarios"]["base"]["kpis"]["month_12_rx"]
    bull_m12 = kpi_record["scenarios"]["bull"]["kpis"]["month_12_rx"]
    bear_m12 = kpi_record["scenarios"]["bear"]["kpis"]["month_12_rx"]
    kpi_record["scenario_spread"] = {
        "bull_vs_base_pct": round((bull_m12 / base_m12 - 1) * 100, 1) if base_m12 else None,
        "bear_vs_base_pct": round((bear_m12 / base_m12 - 1) * 100, 1) if base_m12 else None,
    }
    print(f"\nScenario spread at month 12: "
          f"Bull {kpi_record['scenario_spread']['bull_vs_base_pct']:+.1f}% vs Base, "
          f"Bear {kpi_record['scenario_spread']['bear_vs_base_pct']:+.1f}% vs Base")

    # --- save outputs ---
    combined_df = pd.concat(all_rows, ignore_index=True)
    csv_path = os.path.join(OUT_DIR, "final_forecast_scenarios.csv")
    combined_df.to_csv(csv_path, index=False)

    kpi_path = os.path.join(OUT_DIR, "final_forecast_kpis.json")
    with open(kpi_path, "w") as f:
        json.dump(kpi_record, f, indent=2)

    # --- readable one-page summary ---
    md_lines = ["# Final Forecast Summary\n", f"Generated: {kpi_record['generated']}\n"]
    md_lines.append(f"\n**Model:** analog_bass_static (selected via Stage 6 LOO validation "
                     f"across 35 analogs — mean MASE 0.497, std 0.263)\n")
    md_lines.append(f"\n**Known months observed:** {n_known} "
                     f"(from {n_known * WEEKS_PER_MONTH:.0f} weeks of early Rx)\n")
    md_lines.append(f"\n**Scenario assumptions source:** `{DATA_DIR}/scenario_assumptions.json`\n")
    md_lines.append("\n## Scenario comparison (12-month horizon)\n")
    md_lines.append("| scenario | peak month | peak Rx | month-12 Rx | 12mo cumulative Rx | avg forecast MoM growth |")
    md_lines.append("|---|---|---|---|---|---|")
    for scenario in ["bull", "base", "bear"]:
        k = kpi_record["scenarios"][scenario]["kpis"]
        md_lines.append(
            f"| {scenario} | {k['peak_month']} | {k['peak_rx']:.0f} | {k['month_12_rx']:.0f} | "
            f"{k['total_12mo_rx_cumulative']:.0f} | "
            f"{k['avg_forecast_growth_rate_mom_pct']}% |"
        )
    md_lines.append(f"\n**Scenario spread at month 12:** Bull "
                     f"{kpi_record['scenario_spread']['bull_vs_base_pct']:+.1f}% vs Base, "
                     f"Bear {kpi_record['scenario_spread']['bear_vs_base_pct']:+.1f}% vs Base\n")

    md_lines.append("\n## Scenario qualitative context (not quantitatively modeled)\n")
    md_lines.append("| scenario | competitive entry | payer access trend | promo spend trend |")
    md_lines.append("|---|---|---|---|")
    for scenario in ["bull", "base", "bear"]:
        raw = kpi_record["scenarios"][scenario]["raw_assumptions"]
        md_lines.append(
            f"| {scenario} | {raw['competitive_entry_flag']} | "
            f"{raw['payer_access_trend']} | {raw['promotional_spend_trend']} |"
        )
    md_lines.append(
        "\nThese three fields come straight from scenario_assumptions.json but are "
        "NOT currently converted into a number that moves the forecast -- there's no "
        "established rule for e.g. how much 'payer access improving' should shift the "
        "curve. Treat them as narrative context for the brand team, not inputs the "
        "model has already accounted for.\n"
    )

    md_lines.append(
        "\n**Assumption note:** ceiling and speed multipliers are derived directly "
        "from `market_size_adjustment_pct` and `adoption_speed_multiplier` in "
        f"`{DATA_DIR}/scenario_assumptions.json` (Fast/Normal/Slow -> "
        f"{ADOPTION_SPEED_MAP['Fast']}/{ADOPTION_SPEED_MAP['Normal']}/{ADOPTION_SPEED_MAP['Slow']}x "
        "speed). They are not statistically fitted -- there is only one new drug, so "
        "scenario magnitude can't be estimated from data. Treat Bull/Bear as directional "
        "planning bounds, not confidence intervals.\n"
    )

    md_path = os.path.join(OUT_DIR, "final_forecast_summary.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines))

    print(f"\nSaved: {csv_path}")
    print(f"Saved: {kpi_path}")
    print(f"Saved: {md_path}")
    print("\nStage 8 complete.")


if __name__ == "__main__":
    main()