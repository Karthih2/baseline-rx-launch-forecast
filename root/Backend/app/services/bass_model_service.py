"""Bass fitting and Stage-8 forecast logic.

This module follows the supplied Stage 8 reference implementation:
- fit the winning Analog + Bass Static model once on calibrated early data
- use constrained SLSQP Bass fitting with the peak-month guard
- apply scenario ceiling and adoption-speed adjustments only to the
  forward-looking forecast
- preserve observed new-drug months verbatim
"""
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from app.config import WEEKS_PER_MONTH


def bass_cumulative(t, p, q, m):
    t = np.asarray(t, dtype=float)
    p = max(float(p), 1e-12)
    q = max(float(q), 1e-12)
    return m * (1 - np.exp(-(p + q) * t)) / (1 + (q / p) * np.exp(-(p + q) * t))


def bass_peak_month(p, q):
    p = max(float(p), 1e-12)
    q = max(float(q), 1e-12)
    return np.log(q / p) / (p + q)


def fit_bass(monthly_values: np.ndarray, min_peak_margin: float = 2.5):
    """Exact constrained fitting logic from the supplied Stage 8 reference."""
    monthly_values = np.asarray(monthly_values, dtype=float)
    n = len(monthly_values)
    if n == 0:
        return 0.03, 0.30, 1.0

    monthly_values = np.maximum(monthly_values, 0.0)
    cum = np.cumsum(monthly_values)
    t = np.arange(1, n + 1, dtype=float)
    peak_monthly = max(float(monthly_values.max()), 1.0)
    cum_scaled = cum / peak_monthly

    p_lo, p_hi = 0.005, 0.25
    q_lo, q_hi = 0.05, 0.75
    m_scaled_lo, m_scaled_hi = 1.5, 25.0
    m_scaled_lo = max(m_scaled_lo, (cum[-1] / peak_monthly) * 1.05)
    if m_scaled_hi <= m_scaled_lo:
        m_scaled_hi = m_scaled_lo * 1.5

    bounds = [(p_lo, p_hi), (q_lo, q_hi), (m_scaled_lo, m_scaled_hi)]
    p0 = np.array([
        0.03,
        0.35,
        min(max(4.0, m_scaled_lo), m_scaled_hi),
    ])

    def sse_scaled(params):
        p, q, m_scaled = params
        pred = bass_cumulative(t, p, q, m_scaled)
        return float(np.sum((pred - cum_scaled) ** 2))

    required_peak = n - 1 + min_peak_margin

    def peak_constraint(params):
        p, q, _ = params
        return bass_peak_month(p, q) - required_peak

    try:
        res = minimize(
            sse_scaled,
            p0,
            method="SLSQP",
            bounds=bounds,
            constraints=[{"type": "ineq", "fun": peak_constraint}],
            options={"maxiter": 1000, "ftol": 1e-12},
        )
        p, q, m_scaled = res.x
        m = m_scaled * peak_monthly
        if (
            not res.success
            or p <= 0
            or q <= 0
            or not np.all(np.isfinite(res.x))
        ):
            raise ValueError("constrained fit failed")
        return float(p), float(q), float(m)
    except Exception:
        p_fallback, q_fallback = 0.03, 0.30
        for _ in range(50):
            if bass_peak_month(p_fallback, q_fallback) >= required_peak:
                break
            q_fallback *= 0.9
        return p_fallback, q_fallback, float(peak_monthly * 4.0)


def bass_forecast_months(p, q, m, n_known, horizon):
    """Exact Stage-8 incremental Bass forecast slicing behavior."""
    horizon = int(horizon)
    n_known = int(n_known)
    if horizon <= 0:
        return np.array([], dtype=float)
    t_full = np.arange(1, horizon + 1, dtype=float)
    cum_full = bass_cumulative(t_full, p, q, m)
    monthly_full = np.diff(np.concatenate([[0.0], cum_full]))
    return np.maximum(monthly_full[n_known:], 0.0)


def calibrate_analog_curve(known_monthly, analog_weighted_curve, clip_pct=(5, 95)):
    """Exact Stage-8 analog calibration logic."""
    known_monthly = np.asarray(known_monthly, dtype=float)
    analog_weighted_curve = np.asarray(analog_weighted_curve, dtype=float)
    n_known = len(known_monthly)
    analog_known = analog_weighted_curve[:n_known]
    analog_known_safe = np.where(analog_known == 0, 1.0, analog_known)
    ratios = known_monthly / analog_known_safe
    if n_known >= 3:
        lo, hi = np.percentile(ratios, clip_pct)
        ratios = np.clip(ratios, lo, hi)
    calibration_factor = float(np.median(ratios)) if len(ratios) else 1.0
    return analog_weighted_curve * calibration_factor, calibration_factor


def compute_blend_weight(known_monthly, analog_calibrated, bass_fitted_known, min_known=2):
    """Exact Stage-8 error-based analog/Bass blend weight."""
    known_monthly = np.asarray(known_monthly, dtype=float)
    analog_calibrated = np.asarray(analog_calibrated, dtype=float)
    bass_fitted_known = np.asarray(bass_fitted_known, dtype=float)
    n_known = len(known_monthly)
    if n_known < min_known:
        return 0.5
    analog_err = np.mean(np.abs(known_monthly - analog_calibrated[:n_known]))
    bass_err = np.mean(np.abs(known_monthly - bass_fitted_known[:n_known]))
    if analog_err + bass_err == 0:
        return 0.5
    w_analog = bass_err / (analog_err + bass_err)
    return float(np.clip(w_analog, 0.25, 0.75))


def build_scenario_forecast(
    known_monthly,
    analog_weighted_curve,
    horizon,
    base_p,
    base_q,
    base_m,
    base_calibration_factor,
    base_weight,
    ceiling_mult=1.0,
    speed_mult=1.0,
    min_ceiling_margin=1.02,
):
    """Exact Stage-8 scenario forecast builder."""
    known_monthly = np.asarray(known_monthly, dtype=float)
    analog_weighted_curve = np.asarray(analog_weighted_curve, dtype=float)
    n_known = len(known_monthly)
    cum_known = float(known_monthly.sum())

    scenario_p = float(base_p) * float(speed_mult)
    scenario_q = float(base_q) * float(speed_mult)
    scenario_m = float(base_m) * float(ceiling_mult)

    min_scenario_m = cum_known * float(min_ceiling_margin)
    if scenario_m < min_scenario_m:
        scenario_m = min_scenario_m

    scenario_calibration = float(base_calibration_factor) * float(ceiling_mult)

    # For the Stage-8 reference implementation, both the analog and Bass
    # forecast curves are derived directly from the single base fit.
    bass_full = bass_forecast_months(scenario_p, scenario_q, scenario_m, 0, horizon)
    bass_shape = bass_full[n_known:horizon]
    analog_forecast = (analog_weighted_curve * scenario_calibration)[n_known:horizon]

    forecast = np.maximum(
        float(base_weight) * analog_forecast
        + (1.0 - float(base_weight)) * bass_shape,
        0.0,
    )
    return forecast, {
        "p": scenario_p,
        "q": scenario_q,
        "m": scenario_m,
        "calibration_factor": scenario_calibration,
    }


def aggregate_weekly_to_monthly(new_curve_long: pd.DataFrame) -> np.ndarray:
    """Exact Stage-8 weekly -> monthly aggregation."""
    df = new_curve_long.sort_values("week_number").reset_index(drop=True)
    if df.empty:
        return np.array([], dtype=float)
    df["month"] = np.ceil(df["week_number"] / WEEKS_PER_MONTH).astype(int)
    monthly = df.groupby("month")["rx_count"].sum()
    full_weeks_needed = monthly.index * WEEKS_PER_MONTH
    max_week = df["week_number"].max()
    complete_months = monthly.index[full_weeks_needed <= max_week]
    return monthly.loc[complete_months].values.astype(float)
