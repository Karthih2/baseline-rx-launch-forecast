"""
STAGE 5 — TRAIN 6 FORECASTING MODELS  (OPTIMIZED)
==================================================
Uses the new drug's known early weekly Rx (aggregated to monthly) plus the
analog pool to produce a 12-month forecast under each of 6 approaches:

  1. Naive
  2. ARIMA
  3. Analog-only            (similarity-weighted analog curve, calibrated)
  4. Bass-only              (fit Bass on the new drug's own known data)
  5. Analog + Bass (static) (calibrate once, blend with fitted Bass shape)
  6. Analog + Bass (adaptive) (walk-forward recalibration + walk-forward Bass refit)

Saves one forecast_<model>.csv per model with columns: month, rx, type
(type = 'known' for observed months, 'forecast' for predicted months).
"""

import os
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")

PREP_DIR = "../03_preprocessed"
FEAT_DIR = "../04_features"
OUT_DIR = "../05_models"
os.makedirs(OUT_DIR, exist_ok=True)

FORECAST_HORIZON = 12          # total months we want a forecast for
WEEKS_PER_MONTH = 4.345
MIN_KNOWN_FOR_ARIMA = 4
MIN_KNOWN_FOR_BLEND_WEIGHTING = 2   # below this, fall back to 0.5/0.5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def aggregate_weekly_to_monthly(new_curve_long: pd.DataFrame) -> np.ndarray:
    """Aggregate the new drug's weekly early_rx into monthly buckets.
    Returns array of known monthly totals (only FULL months included)."""
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
    """Month at which the Bass curve peaks: t* = ln(q/p) / (p+q)."""
    return np.log(q / p) / (p + q)


def fit_bass(monthly_values: np.ndarray, min_peak_margin: float = 2.5,
             debug: bool = False, warn: bool = True):
    """Fit Bass p, q, m to a short monthly series.

    p/q live on a ~0.01-0.75 scale while m lives on a ~500K-3.8M scale;
    gradient optimizers struggle across 6+ orders of magnitude, so we
    normalize by peak_monthly (fit on curves that are ~O(1)) and rescale
    m back up afterwards. A peak-position constraint keeps the fitted
    curve from claiming we've already passed peak adoption based on 3-5
    noisy early points.
    """
    n = len(monthly_values)
    if n < 1:
        raise ValueError("fit_bass requires at least 1 known month")

    cum = np.cumsum(monthly_values)
    t = np.arange(1, n + 1)
    peak_monthly = max(monthly_values.max(), 1.0)
    cum_scaled = cum / peak_monthly

    p_lo, p_hi = 0.005, 0.25
    q_lo, q_hi = 0.05, 0.75
    # widened from 12.0: a 12x cap on m/peak-known was binding routinely on
    # real (noisier, less textbook) data, forcing an artificially early
    # peak. 25x gives the optimizer real room before we treat a bound-hit
    # as a genuine "not identified" signal rather than an artifact of a
    # too-tight cap.
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
        if debug:
            print(f"  [fit_bass debug] success={res.success} msg={res.message} "
                  f"p={p:.5f} q={q:.5f} m_scaled={m_scaled:.3f} m={m:.1f}")
        if not res.success or p <= 0 or q <= 0 or not np.all(np.isfinite(res.x)):
            raise ValueError(f"constrained fit failed: {res.message}")

        # Flag when the fit is pinned against its bounds -- means the
        # optimizer wants values outside our safe range, i.e. the fit is
        # not well-identified from this little data. Forecast is still
        # returned, but should be treated with lower confidence.
        m_at_bound = np.isclose(m_scaled, m_scaled_hi, rtol=1e-3) or np.isclose(m_scaled, m_scaled_lo, rtol=1e-3)
        peak_at_bound = np.isclose(bass_peak_month(p, q), required_peak, rtol=1e-3)
        if m_at_bound and peak_at_bound and warn:
            print(f"  [fit_bass WARNING] both m and peak-position bounds are binding -- "
                  f"fit is poorly identified from {n} known months; treat this "
                  f"Bass forecast with low confidence")

        return float(p), float(q), float(m)
    except Exception as e:
        if debug:
            print(f"  [fit_bass debug] EXCEPTION: {e} -- using fallback")
        p_fallback, q_fallback = 0.03, 0.30
        for _ in range(50):
            if bass_peak_month(p_fallback, q_fallback) >= required_peak:
                break
            q_fallback *= 0.9
        return p_fallback, q_fallback, peak_monthly * 4.0


def bass_forecast_months(p, q, m, n_known, horizon):
    """Return monthly (non-cumulative) Bass forecast for months
    n_known+1 .. horizon."""
    t_full = np.arange(1, horizon + 1)
    cum_full = bass_cumulative(t_full, p, q, m)
    monthly_full = np.diff(np.concatenate([[0], cum_full]))
    return np.maximum(monthly_full[n_known:], 0)


def make_output_df(known_values, forecast_values):
    n_known = len(known_values)
    n_fore = len(forecast_values)
    months = np.arange(1, n_known + n_fore + 1)
    rx = np.concatenate([known_values, forecast_values])
    types = ["known"] * n_known + ["forecast"] * n_fore
    return pd.DataFrame({"month": months, "rx": np.round(rx, 1), "type": types})


def calibrate_analog_curve(known_monthly: np.ndarray, analog_weighted_curve: np.ndarray,
                            clip_pct: tuple = (5, 95)):
    """Scale the analog curve up/down to match the new drug's observed
    known months.

    Uses the MEDIAN ratio (not mean) -- with only a handful of known
    months, a single noisy month can drag a mean ratio far off; the
    median is robust to that. Per-month ratios are clipped to the
    [clip_pct] percentile range before taking the median as an extra
    guard against one wild outlier month dominating.
    """
    n_known = len(known_monthly)
    analog_known = analog_weighted_curve[:n_known]
    analog_known_safe = np.where(analog_known == 0, 1, analog_known)
    ratios = known_monthly / analog_known_safe

    if n_known >= 3:
        lo, hi = np.percentile(ratios, clip_pct)
        ratios = np.clip(ratios, lo, hi)

    calibration_factor = float(np.median(ratios))
    calibrated_curve = analog_weighted_curve * calibration_factor
    return calibrated_curve, calibration_factor


def compute_blend_weight(known_monthly: np.ndarray, analog_calibrated: np.ndarray,
                          bass_fitted_known: np.ndarray) -> float:
    """Data-driven replacement for a hardcoded 0.5/0.5 blend.

    Weight = inverse-error weighting between the analog-calibrated curve
    and the Bass-fitted curve, evaluated on the known months only: the
    component with lower in-sample error gets more weight in the blend.
    Falls back to 0.5 (equal blend) when there's too little known data
    to judge reliably, or if either error is degenerate (all zeros).
    """
    n_known = len(known_monthly)
    if n_known < MIN_KNOWN_FOR_BLEND_WEIGHTING:
        return 0.5

    analog_err = np.mean(np.abs(known_monthly - analog_calibrated[:n_known]))
    bass_err = np.mean(np.abs(known_monthly - bass_fitted_known[:n_known]))

    if analog_err + bass_err == 0:
        return 0.5

    # weight favors whichever has the SMALLER error
    w_analog = bass_err / (analog_err + bass_err)
    # keep some floor/ceiling so one component never fully dominates
    # on very short series (avoids overfitting the blend itself to noise)
    return float(np.clip(w_analog, 0.25, 0.75))


# ---------------------------------------------------------------------------
# Model 1 — Naive
# ---------------------------------------------------------------------------
def model_naive(known_monthly, horizon):
    last = known_monthly[-1]
    n_fore = horizon - len(known_monthly)
    return np.full(n_fore, last)


# ---------------------------------------------------------------------------
# Model 2 — ARIMA (new drug's own data only)
# ---------------------------------------------------------------------------
def model_arima(known_monthly, horizon, debug: bool = True):
    """Try a couple of orders suited to very short series before giving up.
    Logs which order (if any) actually fit, so an ARIMA==naive result is
    diagnosable instead of a silent fallback."""
    n_fore = horizon - len(known_monthly)

    if len(known_monthly) < MIN_KNOWN_FOR_ARIMA:
        if debug:
            print(f"  [ARIMA] only {len(known_monthly)} known months "
                  f"(< {MIN_KNOWN_FOR_ARIMA}) -- skipping fit, using naive fallback")
        return model_naive(known_monthly, horizon)

    candidate_orders = [(1, 1, 0), (0, 1, 1), (1, 0, 0)]
    for order in candidate_orders:
        try:
            fit = ARIMA(known_monthly, order=order).fit()
            forecast = np.maximum(np.array(fit.forecast(steps=n_fore)), 0)
            if debug:
                print(f"  [ARIMA] fit succeeded with order={order}")
            return forecast
        except Exception as e:
            if debug:
                print(f"  [ARIMA] order={order} failed: {e}")
            continue

    if debug:
        print("  [ARIMA] all candidate orders failed -- using naive fallback")
    return model_naive(known_monthly, horizon)


# ---------------------------------------------------------------------------
# Model 3 — Analog-only (similarity-weighted analog curve, calibrated)
# ---------------------------------------------------------------------------
def model_analog_only(known_monthly, analog_weighted_curve, horizon):
    n_known = len(known_monthly)
    calibrated_curve, calibration_factor = calibrate_analog_curve(
        known_monthly, analog_weighted_curve
    )
    forecast = calibrated_curve[n_known:horizon]
    return np.maximum(forecast, 0), calibration_factor


# ---------------------------------------------------------------------------
# Model 4 — Bass-only (fit Bass on new drug's own known data only)
# ---------------------------------------------------------------------------
def model_bass_only(known_monthly, horizon):
    p, q, m = fit_bass(known_monthly, debug=False)
    forecast = bass_forecast_months(p, q, m, len(known_monthly), horizon)
    return forecast, (p, q, m)


# ---------------------------------------------------------------------------
# Model 5 — Analog + Bass (static): calibrate analog curve once, fit Bass
# once, blend with a DATA-DRIVEN weight instead of a fixed 50/50.
# ---------------------------------------------------------------------------
def model_analog_bass_static(known_monthly, analog_weighted_curve, horizon,
                              blend_weight: float = None):
    n_known = len(known_monthly)
    calibrated_curve, calibration_factor = calibrate_analog_curve(
        known_monthly, analog_weighted_curve
    )

    p, q, m = fit_bass(calibrated_curve[:n_known])
    bass_full = bass_forecast_months(p, q, m, 0, horizon)  # months 1..horizon
    bass_shape = bass_full[n_known:horizon]
    bass_known_fit = bass_full[:n_known]

    w = blend_weight if blend_weight is not None else compute_blend_weight(
        known_monthly, calibrated_curve, bass_known_fit
    )

    analog_forecast = calibrated_curve[n_known:horizon]
    forecast = w * analog_forecast + (1 - w) * bass_shape
    return np.maximum(forecast, 0), calibration_factor, w


# ---------------------------------------------------------------------------
# Model 6 — Analog + Bass (adaptive): TRUE walk-forward recalibration.
# At each known month, recalibrate against data available "so far" AND
# refit Bass on that same partial window, mirroring how the forecast
# would actually be refreshed live as each new month of real Rx arrives.
# ---------------------------------------------------------------------------
def model_analog_bass_adaptive(known_monthly, analog_weighted_curve, horizon,
                                alpha: float = 0.6):
    n_known = len(known_monthly)
    smoothed_calib = None
    calib_history = []
    last_bass_params = None

    for step in range(1, n_known + 1):
        window_known = known_monthly[:step]
        window_analog = analog_weighted_curve[:step]

        # recalibrate using only data seen "so far" (median-based, same
        # robust logic as the static model)
        _, step_calib = calibrate_analog_curve(window_known, window_analog)

        smoothed_calib = step_calib if smoothed_calib is None \
            else alpha * step_calib + (1 - alpha) * smoothed_calib
        calib_history.append(smoothed_calib)

        # walk-forward Bass refit: refit using only the calibrated curve
        # up to this step, so the model genuinely updates its shape as
        # more months arrive (not just a smoothed scalar applied once
        # at the very end)
        calibrated_window = window_analog * smoothed_calib
        is_final_step = (step == n_known)
        try:
            # only surface the bound-binding warning on the final step --
            # intermediate 2-3 month windows hit bounds routinely and
            # aren't informative on their own
            last_bass_params = fit_bass(calibrated_window, warn=is_final_step)
        except Exception:
            pass  # keep previous step's params if this step's fit fails

    calibrated_curve_full = analog_weighted_curve * smoothed_calib
    p, q, m = last_bass_params
    bass_full = bass_forecast_months(p, q, m, 0, horizon)
    bass_shape = bass_full[n_known:horizon]
    bass_known_fit = bass_full[:n_known]

    w = compute_blend_weight(known_monthly, calibrated_curve_full, bass_known_fit)

    analog_forecast = calibrated_curve_full[n_known:horizon]
    final_forecast = w * analog_forecast + (1 - w) * bass_shape
    return np.maximum(final_forecast, 0), calib_history, w


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    new_curve = pd.read_csv(os.path.join(PREP_DIR, "new_drug_rx_early_long.csv"))
    weighted_curve_df = pd.read_csv(os.path.join(FEAT_DIR, "analog_weighted_curve.csv"))
    analog_weighted_curve = weighted_curve_df["analog_weighted_rx"].values.astype(float)

    known_monthly = aggregate_weekly_to_monthly(new_curve)
    n_known = len(known_monthly)

    print("=" * 60)
    print("STAGE 5 — TRAIN 6 FORECASTING MODELS (OPTIMIZED)")
    print("=" * 60)
    print(f"Known complete months from early weekly data: {n_known}")
    print(f"Known monthly Rx values: {np.round(known_monthly, 1)}")
    print(f"Forecast horizon: month {n_known + 1} -> month {FORECAST_HORIZON}")

    results = {}

    # 1. Naive
    f = model_naive(known_monthly, FORECAST_HORIZON)
    results["naive"] = make_output_df(known_monthly, f)

    # 2. ARIMA
    print("\n[Model: ARIMA]")
    f = model_arima(known_monthly, FORECAST_HORIZON, debug=True)
    results["arima"] = make_output_df(known_monthly, f)

    # 3. Analog-only
    f, analog_only_calib = model_analog_only(known_monthly, analog_weighted_curve, FORECAST_HORIZON)
    results["analog_only"] = make_output_df(known_monthly, f)
    print(f"\nAnalog-only calibration factor (median-based): {analog_only_calib:.4f}")

    # 4. Bass-only
    f, bass_params = model_bass_only(known_monthly, FORECAST_HORIZON)
    results["bass_only"] = make_output_df(known_monthly, f)
    peak_m = bass_peak_month(bass_params[0], bass_params[1])
    print(f"Bass-only fitted params: p={bass_params[0]:.5f}, "
          f"q={bass_params[1]:.5f}, m={bass_params[2]:.1f} "
          f"(m / peak-known = {bass_params[2] / known_monthly.max():.2f}x, "
          f"fitted peak at month {peak_m:.2f} vs {n_known} known months)")

    # 5. Analog + Bass static
    f, calib, w_static = model_analog_bass_static(known_monthly, analog_weighted_curve, FORECAST_HORIZON)
    results["analog_bass_static"] = make_output_df(known_monthly, f)
    print(f"Analog+Bass static: calibration factor={calib:.4f}, "
          f"blend weight (analog)={w_static:.2f} / (bass)={1-w_static:.2f}")

    # 6. Analog + Bass adaptive
    f, history, w_adaptive = model_analog_bass_adaptive(known_monthly, analog_weighted_curve, FORECAST_HORIZON)
    results["analog_bass_adaptive"] = make_output_df(known_monthly, f)
    print(f"Analog+Bass adaptive: walk-forward recalibrated+refit {len(history)} times, "
          f"final blend weight (analog)={w_adaptive:.2f} / (bass)={1-w_adaptive:.2f}")

    # --- save all outputs ---
    print("\nSaved forecasts:")
    for name, df in results.items():
        path = os.path.join(OUT_DIR, f"forecast_{name}.csv")
        df.to_csv(path, index=False)
        print(f"  {path}  (month {n_known+1}-{FORECAST_HORIZON} forecast: "
              f"{df[df['type']=='forecast']['rx'].round(0).tolist()})")

    print(f"\nAll 6 models trained and forecasts saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()