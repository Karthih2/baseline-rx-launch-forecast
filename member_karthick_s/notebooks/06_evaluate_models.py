"""
STAGE 6 — EVALUATE 6 FORECASTING MODELS  (matched to optimized Stage 5)
=========================================================================

PART A — Backtest on the new drug (IMPLEMENTED)
  Train each model on months 1-3 only, predict months 4-5, compare to the
  real known months 4-5.

PART B — Leave-one-out (LOO) across the 35 analogs (IMPLEMENTED)

PART C — Training-window fit vs. backtest error (overfitting check)

Outputs:
  ../06_evaluation/model_comparison_metrics.csv   (6 rows x metrics, backtest)
  ../06_evaluation/training_vs_backtest.csv
  ../06_evaluation/loo_validation_results.csv
  ../06_evaluation/loo_summary.csv
  ../06_evaluation/overfit_check_notes.md
"""

import os
import sys
import warnings
from datetime import datetime

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "train_models", os.path.join(os.path.dirname(os.path.abspath(__file__)), "05_train_models.py")
)
train_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train_models)

# Suppress fit_bass's bound-binding warning for this module's calls only
# (see note 4 above) -- does not affect 05_train_models.py when run
# directly, since this only patches the defaults on the copy of the
# function object imported into THIS module's namespace.
train_models.fit_bass.__defaults__ = (2.5, False, False)  # (min_peak_margin, debug, warn)

PREP_DIR = "../03_preprocessed"
FEAT_DIR = "../04_features"
OUT_DIR = "../06_evaluation"
os.makedirs(OUT_DIR, exist_ok=True)

BACKTEST_HOLDOUT_MONTHS = 2   # hold out the last 2 known months


# ---------------------------------------------------------------------------
# Shared evaluate() function
# ---------------------------------------------------------------------------
def evaluate(actual, predicted, naive_mae_reference=None):
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)

    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))

    nonzero_mask = actual != 0
    mape = (
        np.mean(np.abs((actual[nonzero_mask] - predicted[nonzero_mask]) / actual[nonzero_mask])) * 100
        if nonzero_mask.any() else None
    )

    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else None

    mase = mae / naive_mae_reference if naive_mae_reference not in (None, 0) else None

    bias = np.mean(predicted - actual)

    return {"MAE": mae, "RMSE": rmse, "MAPE": mape, "R2": r2, "MASE": mase, "Bias": bias}


# ---------------------------------------------------------------------------
# Dispatch: normalize each model's differing return signature down to just
# the forecast array. Static/adaptive return 3 values -- unpacked with `_`.
# ---------------------------------------------------------------------------
def run_model(name, known_monthly, analog_weighted_curve, horizon):
    tm = train_models
    if name == "naive":
        return tm.model_naive(known_monthly, horizon)
    elif name == "arima":
        return tm.model_arima(known_monthly, horizon, debug=False)
    elif name == "analog_only":
        forecast, _ = tm.model_analog_only(known_monthly, analog_weighted_curve, horizon)
        return forecast
    elif name == "bass_only":
        forecast, _ = tm.model_bass_only(known_monthly, horizon)
        return forecast
    elif name == "analog_bass_static":
        forecast, _, _ = tm.model_analog_bass_static(known_monthly, analog_weighted_curve, horizon)
        return forecast
    elif name == "analog_bass_adaptive":
        forecast, _, _ = tm.model_analog_bass_adaptive(known_monthly, analog_weighted_curve, horizon)
        return forecast
    else:
        raise ValueError(f"unknown model: {name}")


MODEL_NAMES = [
    "naive", "arima", "analog_only", "bass_only",
    "analog_bass_static", "analog_bass_adaptive",
]


# ---------------------------------------------------------------------------
# PART A — Backtest on the new drug
# ---------------------------------------------------------------------------
def run_backtest(known_monthly, analog_weighted_curve):
    n_known = len(known_monthly)
    if n_known <= BACKTEST_HOLDOUT_MONTHS:
        raise ValueError(
            f"Only {n_known} known months -- not enough to hold out "
            f"{BACKTEST_HOLDOUT_MONTHS} for backtesting. Reduce BACKTEST_HOLDOUT_MONTHS."
        )

    train_months = known_monthly[: n_known - BACKTEST_HOLDOUT_MONTHS]
    test_actual = known_monthly[n_known - BACKTEST_HOLDOUT_MONTHS:]
    backtest_horizon = len(train_months) + BACKTEST_HOLDOUT_MONTHS

    print(f"Backtest split: train on months 1-{len(train_months)}, "
          f"predict months {len(train_months)+1}-{backtest_horizon}, "
          f"compare against real values {np.round(test_actual, 1)}")

    naive_forecast_full = run_model("naive", train_months, analog_weighted_curve, backtest_horizon)
    naive_predicted = naive_forecast_full[-BACKTEST_HOLDOUT_MONTHS:]
    naive_mae_reference = evaluate(test_actual, naive_predicted)["MAE"]
    print(f"Naive backtest MAE (MASE denominator for all models): {naive_mae_reference:.2f}\n")

    rows = []
    for name in MODEL_NAMES:
        forecast_full = run_model(name, train_months, analog_weighted_curve, backtest_horizon)
        predicted = forecast_full[-BACKTEST_HOLDOUT_MONTHS:]

        metrics = evaluate(test_actual, predicted, naive_mae_reference=naive_mae_reference)
        metrics["model_name"] = name
        metrics["split_type"] = "backtest"
        metrics["timestamp"] = datetime.now().isoformat(timespec="seconds")
        rows.append(metrics)

        print(f"{name:22s} | predicted {np.round(predicted,0)} | "
              f"MAE={metrics['MAE']:.1f} RMSE={metrics['RMSE']:.1f} "
              f"MAPE={metrics['MAPE']:.2f}% R2={metrics['R2']:.3f} "
              f"MASE={metrics['MASE']:.3f} Bias={metrics['Bias']:.1f}")

    df = pd.DataFrame(rows)
    cols = ["model_name", "split_type", "MAE", "RMSE", "MAPE", "R2", "MASE", "Bias", "timestamp"]
    return df[cols]


# ---------------------------------------------------------------------------
# PART B — Leave-one-out across the 35 analogs
# ---------------------------------------------------------------------------
ANALOG_CURVE_PATH = os.path.join(PREP_DIR, "analog_rx_curve_long.csv")
ANALOG_STATIC_PATH = os.path.join(PREP_DIR, "analog_static_clean.csv")

N_KNOWN_LOO = 5
TOP_N_ANALOGS = 5

CAT_COLS = ["mechanism_of_action", "route_of_administration", "target_specialty", "launch_quarter"]
NUM_COLS = ["market_size", "competitive_density", "payer_restrictiveness", "promotional_intensity", "price_tier"]
BIN_COLS = ["special_designation"]


def build_feature_matrix(static_df):
    from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

    try:
        cat_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    except TypeError:
        cat_encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")

    cat_matrix = cat_encoder.fit_transform(static_df[CAT_COLS])
    num_matrix = MinMaxScaler().fit_transform(static_df[NUM_COLS])
    bin_matrix = static_df[BIN_COLS].astype(int).values

    return np.hstack([cat_matrix, num_matrix, bin_matrix])


def load_analog_data():
    curve_long = pd.read_csv(ANALOG_CURVE_PATH)
    static_df = pd.read_csv(ANALOG_STATIC_PATH).reset_index(drop=True)

    curves = {}
    for drug_id, grp in curve_long.groupby("drug_id"):
        curves[drug_id] = grp.sort_values("month")["rx"].values.astype(float)

    feature_matrix = build_feature_matrix(static_df)
    drug_ids = static_df["drug_id"].values

    return curves, drug_ids, feature_matrix


def select_top_n_and_weights(target_idx, drug_ids, feature_matrix, n=TOP_N_ANALOGS):
    from sklearn.metrics.pairwise import cosine_similarity

    sims = cosine_similarity(
        feature_matrix[target_idx].reshape(1, -1), feature_matrix
    )[0]
    sims[target_idx] = -np.inf

    top_idx = np.argsort(sims)[::-1][:n]
    top_sims = sims[top_idx]
    weights = top_sims / top_sims.sum()
    top_ids = drug_ids[top_idx]
    return top_ids, weights


def build_weighted_curve(top_ids, weights, curves, length=36):
    weighted = np.zeros(length)
    for drug_id, w in zip(top_ids, weights):
        weighted += w * curves[drug_id][:length]
    return weighted


# ---------------------------------------------------------------------------
# PART C — Training-window fit vs. backtest error (overfitting check)
# ---------------------------------------------------------------------------
def training_fit_naive(known_monthly):
    actual = known_monthly[1:]
    predicted = known_monthly[:-1]
    return actual, predicted


def training_fit_arima(known_monthly):
    from statsmodels.tsa.arima.model import ARIMA
    try:
        if len(known_monthly) < 4:
            raise ValueError("too few points")
        fit = ARIMA(known_monthly, order=(1, 1, 0)).fit()
        fitted = np.asarray(fit.fittedvalues)
        mask = np.isfinite(fitted) & (np.arange(len(fitted)) > 0)
        return known_monthly[mask], fitted[mask]
    except Exception:
        return training_fit_naive(known_monthly)


def training_fit_analog_only(known_monthly, analog_weighted_curve):
    calibrated_curve, _ = train_models.calibrate_analog_curve(known_monthly, analog_weighted_curve)
    n = len(known_monthly)
    return known_monthly, calibrated_curve[:n]


def training_fit_bass_only(known_monthly):
    p, q, m = train_models.fit_bass(known_monthly)  # warn=False via patched default
    n = len(known_monthly)
    t = np.arange(1, n + 1)
    cum_fit = train_models.bass_cumulative(t, p, q, m)
    monthly_fit = np.diff(np.concatenate([[0], cum_fit]))
    return known_monthly, monthly_fit


def training_fit_analog_bass_static(known_monthly, analog_weighted_curve):
    """Uses the same data-driven blend weight as Stage 5's actual model."""
    n = len(known_monthly)
    calibrated_curve, _ = train_models.calibrate_analog_curve(known_monthly, analog_weighted_curve)
    p, q, m = train_models.fit_bass(calibrated_curve[:n])
    t = np.arange(1, n + 1)
    cum_fit = train_models.bass_cumulative(t, p, q, m)
    bass_fit = np.diff(np.concatenate([[0], cum_fit]))

    w = train_models.compute_blend_weight(known_monthly, calibrated_curve[:n], bass_fit)
    blended = w * calibrated_curve[:n] + (1 - w) * bass_fit
    return known_monthly, blended


def training_fit_analog_bass_adaptive(known_monthly, analog_weighted_curve, alpha=0.6):
    """Mirrors Stage 5's true walk-forward recalibration + Bass refit at
    each step, using the data-driven blend weight."""
    n = len(known_monthly)
    smoothed_calib = None
    last_bass_params = None

    for step in range(1, n + 1):
        window_known = known_monthly[:step]
        window_analog = analog_weighted_curve[:step]
        _, step_calib = train_models.calibrate_analog_curve(window_known, window_analog)

        smoothed_calib = step_calib if smoothed_calib is None \
            else alpha * step_calib + (1 - alpha) * smoothed_calib

        calibrated_window = window_analog * smoothed_calib
        try:
            last_bass_params = train_models.fit_bass(calibrated_window)
        except Exception:
            pass

    calibrated_curve = analog_weighted_curve * smoothed_calib
    p, q, m = last_bass_params
    t = np.arange(1, n + 1)
    cum_fit = train_models.bass_cumulative(t, p, q, m)
    bass_fit = np.diff(np.concatenate([[0], cum_fit]))

    w = train_models.compute_blend_weight(known_monthly, calibrated_curve[:n], bass_fit)
    blended = w * calibrated_curve[:n] + (1 - w) * bass_fit
    return known_monthly, blended


def run_training_vs_backtest(known_monthly, analog_weighted_curve, backtest_df):
    n_known = len(known_monthly)
    fits = {
        "naive": training_fit_naive(known_monthly),
        "arima": training_fit_arima(known_monthly),
        "analog_only": training_fit_analog_only(known_monthly, analog_weighted_curve),
        "bass_only": training_fit_bass_only(known_monthly),
        "analog_bass_static": training_fit_analog_bass_static(known_monthly, analog_weighted_curve),
        "analog_bass_adaptive": training_fit_analog_bass_adaptive(known_monthly, analog_weighted_curve),
    }

    rows = []
    for name, (actual, predicted) in fits.items():
        m = evaluate(actual, predicted)
        backtest_mae = backtest_df.loc[backtest_df["model_name"] == name, "MAE"].values[0]
        ratio = backtest_mae / m["MAE"] if m["MAE"] not in (None, 0) else np.inf
        rows.append({
            "model_name": name,
            "training_MAE": m["MAE"],
            "training_RMSE": m["RMSE"],
            "backtest_MAE": backtest_mae,
            "backtest_over_training_ratio": ratio,
        })

    df = pd.DataFrame(rows)
    print("\nTraining fit (months 1-{}) vs backtest (months {}-{}):".format(
        n_known, n_known + 1, n_known + BACKTEST_HOLDOUT_MONTHS))
    print(df.to_string(index=False))
    return df


def run_loo_validation():
    curves, drug_ids, feature_matrix = load_analog_data()
    n_drugs = len(drug_ids)
    horizon = N_KNOWN_LOO + 7

    if n_drugs <= TOP_N_ANALOGS:
        print(f"  WARNING: only {n_drugs} analogs available but TOP_N_ANALOGS="
              f"{TOP_N_ANALOGS} -- similarity selection will return fewer than "
              f"{TOP_N_ANALOGS} analogs per target, weakening the weighted curve.")

    print(f"Running LOO across {n_drugs} analogs "
          f"(known months={N_KNOWN_LOO}, forecast horizon={horizon})...\n")

    rows = []
    for target_idx, target_id in enumerate(drug_ids):
        target_curve = curves[target_id]
        known_monthly = target_curve[:N_KNOWN_LOO]
        test_actual = target_curve[N_KNOWN_LOO:horizon]

        top_ids, weights = select_top_n_and_weights(target_idx, drug_ids, feature_matrix)
        analog_weighted_curve = build_weighted_curve(top_ids, weights, curves, length=horizon)

        naive_forecast_full = run_model("naive", known_monthly, analog_weighted_curve, horizon)
        naive_predicted = naive_forecast_full[-len(test_actual):]
        naive_mae_ref = evaluate(test_actual, naive_predicted)["MAE"]

        for name in MODEL_NAMES:
            forecast_full = run_model(name, known_monthly, analog_weighted_curve, horizon)
            predicted = forecast_full[-len(test_actual):]
            metrics = evaluate(test_actual, predicted, naive_mae_reference=naive_mae_ref)
            metrics["model_name"] = name
            metrics["analog_id"] = target_id
            rows.append(metrics)

        if (target_idx + 1) % 10 == 0 or target_idx == n_drugs - 1:
            print(f"  ...{target_idx + 1}/{n_drugs} analogs done")

    detail_df = pd.DataFrame(rows)[["analog_id", "model_name", "MAE", "RMSE", "MAPE", "R2", "MASE", "Bias"]]

    summary_df = (
        detail_df.groupby("model_name")[["MAE", "RMSE", "MAPE", "MASE", "Bias"]]
        .agg(["mean", "std"])
    )
    summary_df.columns = ["_".join(c) for c in summary_df.columns]
    summary_df = summary_df.reset_index()

    return detail_df, summary_df


# ---------------------------------------------------------------------------
# Overfitting check notes
# ---------------------------------------------------------------------------
def write_overfit_notes(backtest_df, loo_summary_df=None, training_vs_backtest_df=None):
    lines = ["# Overfit Check Notes (auto-generated)\n"]
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")

    # --- PRIMARY headline: LOO across 35 analogs (robust, many data points) ---
    if loo_summary_df is not None:
        best_loo = loo_summary_df.loc[loo_summary_df["MASE_mean"].idxmin()]
        lines.append(
            f"\n**Best model (primary metric — LOO mean MASE across "
            f"{loo_summary_df.shape[0]} models / 35 analogs):** "
            f"{best_loo['model_name']} "
            f"(MASE mean={best_loo['MASE_mean']:.3f}, std={best_loo['MASE_std']:.3f})\n"
        )
        lines.append(
            "\nThis is the recommended metric for model selection: it's averaged "
            "over 35 independent analog drugs, so a single lucky/unlucky split "
            "can't dominate it the way it can in the single-drug backtest below.\n"
        )
    else:
        lines.append(
            "\n**No LOO summary available yet — see 'Still needed' section below.**\n"
        )

    # --- SECONDARY: single-split backtest on the new drug (illustrative only) ---
    lines.append(
        "\n\n## Backtest on the new drug (single split — illustrative only, NOT the "
        "model-selection criterion)\n"
    )
    lines.append(
        "**Caveat:** this section is based on a single train/test split (train "
        "months 1-3, predict months 4-5) on ONE drug. With only 2 held-out points, "
        "a very low MAE/MASE here can easily be a lucky calibration rather than a "
        "generalizable result — treat it as a sanity check, not proof of the best "
        "model. Use the LOO result above for the actual decision.\n"
    )
    best_backtest = backtest_df.loc[backtest_df["MASE"].idxmin()]
    lines.append(f"\nLowest single-split backtest MASE: {best_backtest['model_name']} "
                 f"(MASE={best_backtest['MASE']:.3f}, n=2 held-out points)\n")

    for _, row in backtest_df.iterrows():
        flags = []
        if row["model_name"] in ("analog_bass_adaptive", "bass_only") and row["MASE"] is not None and row["MASE"] > 1.5:
            flags.append("high MASE relative to naive -- more flexible model not earning its complexity here")
        if row["Bias"] is not None and abs(row["Bias"]) > row["MAE"] * 0.5:
            direction = "over" if row["Bias"] > 0 else "under"
            flags.append(f"consistently {direction}-forecasting (Bias is a large share of MAE)")
        if row["R2"] is not None and row["R2"] < 0:
            flags.append("negative R2 -- worse than predicting the mean; expected/noted, don't over-read R2 here")
        if flags:
            lines.append(f"\n- **{row['model_name']}**: " + "; ".join(flags))

    if loo_summary_df is not None:
        lines.append("\n\n## LOO validation across 35 analogs (stability check)\n")
        lines.append("| model | MASE mean | MASE std | MAE mean | MAE std |")
        lines.append("|---|---|---|---|---|")
        for _, row in loo_summary_df.iterrows():
            lines.append(
                f"| {row['model_name']} | {row['MASE_mean']:.3f} | {row['MASE_std']:.3f} | "
                f"{row['MAE_mean']:.1f} | {row['MAE_std']:.1f} |"
            )
        lines.append(
            "\n**High MASE_std relative to MASE_mean means the model does great on some "
            "analogs and terrible on others -- that's overfitting to specific analog shapes, "
            "not a generalizable pattern. Prefer a model with a slightly worse mean but a "
            "much smaller std over one with the best mean but a huge spread.**\n"
        )
        for _, row in loo_summary_df.iterrows():
            if row["MASE_mean"] > 0 and row["MASE_std"] / row["MASE_mean"] > 0.75:
                lines.append(f"\n- **{row['model_name']}**: high relative spread across analogs "
                             f"(MASE_std/MASE_mean = {row['MASE_std']/row['MASE_mean']:.2f}) -- "
                             f"investigate before trusting this model's average score")
    else:
        lines.append(
            "\n\n## Still needed before declaring a final winner\n"
            "- [ ] LOO validation across all 35 analogs\n"
        )

    if training_vs_backtest_df is not None:
        lines.append("\n\n## Training fit vs. backtest error (overfitting check)\n")
        lines.append("| model | training MAE (in-sample, months 1-3) | backtest MAE (out-of-sample, months 4-5) | ratio |")
        lines.append("|---|---|---|---|")
        for _, row in training_vs_backtest_df.iterrows():
            lines.append(
                f"| {row['model_name']} | {row['training_MAE']:.1f} | {row['backtest_MAE']:.1f} | "
                f"{row['backtest_over_training_ratio']:.2f}x |"
            )
        lines.append(
            "\n**A high ratio (backtest error much bigger than training error) means the model "
            "fits the months it already saw far better than it predicts new ones -- classic "
            "overfitting. A ratio near 1x means the model generalizes about as well as it fits.**\n"
        )
        for _, row in training_vs_backtest_df.iterrows():
            if row["backtest_over_training_ratio"] > 3:
                lines.append(f"\n- **{row['model_name']}**: backtest error is "
                             f"{row['backtest_over_training_ratio']:.1f}x its training-window error -- "
                             f"strong overfitting signal, treat its backtest score with caution")
    else:
        lines.append(
            "\n\n## Also still needed\n"
            "- [ ] Compare backtest performance to each model's fit on its OWN training "
            "months (1-3) -- if training-period error is much lower than backtest error, that's overfitting\n"
        )

    path = os.path.join(OUT_DIR, "overfit_check_notes.md")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"\nOverfit notes written to {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    new_curve = pd.read_csv(os.path.join(PREP_DIR, "new_drug_rx_early_long.csv"))
    weighted_curve_df = pd.read_csv(os.path.join(FEAT_DIR, "analog_weighted_curve.csv"))
    analog_weighted_curve = weighted_curve_df["analog_weighted_rx"].values.astype(float)

    print("=" * 60)
    print("STAGE 6 — EVALUATE 6 FORECASTING MODELS")
    print("=" * 60)
    print(f"Input check: new_drug_rx_early_long.csv rows={len(new_curve)}, "
          f"analog_weighted_curve.csv rows={len(weighted_curve_df)}")
    print("(If you just re-ran Stage 3, make sure Stages 2 and 4 were also "
          "re-run before trusting these numbers -- LOO uses analog_static_clean.csv "
          "directly, and the weighted curve depends on Stage 2's top-5 selection.)\n")

    known_monthly = train_models.aggregate_weekly_to_monthly(new_curve)

    print("=" * 60)
    print("Part A: Backtest")
    print("=" * 60)

    backtest_df = run_backtest(known_monthly, analog_weighted_curve)

    out_path = os.path.join(OUT_DIR, "model_comparison_metrics.csv")
    backtest_df.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")

    print("\n" + "=" * 60)
    print("Part C: Training fit vs backtest")
    print("=" * 60)

    train_months_only = known_monthly[: len(known_monthly) - BACKTEST_HOLDOUT_MONTHS]
    training_vs_backtest_df = run_training_vs_backtest(train_months_only, analog_weighted_curve, backtest_df)
    tvb_path = os.path.join(OUT_DIR, "training_vs_backtest.csv")
    training_vs_backtest_df.to_csv(tvb_path, index=False)
    print(f"\nSaved: {tvb_path}")

    print("\n" + "=" * 60)
    print("Part B: LOO across 35 analogs")
    print("=" * 60)

    loo_detail_df, loo_summary_df = run_loo_validation()

    loo_detail_path = os.path.join(OUT_DIR, "loo_validation_results.csv")
    loo_summary_path = os.path.join(OUT_DIR, "loo_summary.csv")
    loo_detail_df.to_csv(loo_detail_path, index=False)
    loo_summary_df.to_csv(loo_summary_path, index=False)
    print(f"\nSaved: {loo_detail_path}")
    print(f"Saved: {loo_summary_path}")
    print("\nLOO summary (mean +/- std across 35 analogs):")
    print(loo_summary_df[["model_name", "MASE_mean", "MASE_std", "MAE_mean", "MAE_std"]]
          .to_string(index=False))

    write_overfit_notes(backtest_df, loo_summary_df, training_vs_backtest_df)

    print("\nStage 6 complete.")


if __name__ == "__main__":
    main()