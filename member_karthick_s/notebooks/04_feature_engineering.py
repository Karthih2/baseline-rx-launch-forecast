"""
STAGE 4 — FEATURE ENGINEERING
Reads preprocessed static features + long-format curves, plus top-5 analog
selection from Stage 2. Builds three feature groups:
  1. New-drug early-Rx features
  2. Analog-derived features (from selected top 5 only)
  3. Encoded static/product features
Saves the final combined model-input table.
"""

import os
import numpy as np
import pandas as pd

PREP_DIR = "../03_preprocessed"
EMBED_DIR = "../02_embeddings"
OUT_DIR = "../04_features"
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. New-drug early-Rx features
# ---------------------------------------------------------------------------
def build_new_drug_rx_features(new_curve):
    """new_curve: dataframe with columns drug_id, week, rx, rx_pct_of_peak
    sorted ascending by week. Returns a single-row dict of features."""
    curve = new_curve.sort_values("week").reset_index(drop=True)
    rx = curve["rx"].values

    latest_rx = rx[-1]
    previous_rx = rx[-2] if len(rx) > 1 else rx[-1]
    rx_growth_rate = (latest_rx - previous_rx) / previous_rx if previous_rx != 0 else 0.0
    cumulative_rx = rx.sum()
    rolling_mean_rx = rx[-4:].mean() if len(rx) >= 4 else rx.mean()

    # early growth slope: simple linear regression slope over all known weeks
    x = np.arange(len(rx))
    if len(rx) > 1:
        slope = np.polyfit(x, rx, 1)[0]
    else:
        slope = 0.0

    return {
        "latest_rx": float(latest_rx),
        "previous_rx": float(previous_rx),
        "rx_growth_rate": float(rx_growth_rate),
        "cumulative_rx": float(cumulative_rx),
        "rolling_mean_rx": float(rolling_mean_rx),
        "early_growth_slope": float(slope),
        "n_weeks_observed": int(len(rx)),
    }


# ---------------------------------------------------------------------------
# 2. Analog-derived features (from selected top-5 analogs only)
# ---------------------------------------------------------------------------
def build_analog_features(top5_df, analog_curve_long):
    """top5_df: drug_id, similarity, weight (from Stage 2 output)
    analog_curve_long: drug_id, month, rx, rx_pct_of_peak (from Stage 3)."""
    selected_ids = top5_df["drug_id"].tolist()
    weights = dict(zip(top5_df["drug_id"], top5_df["weight"]))

    curves = {}
    peaks, month_to_peak, growth_rates = [], [], []
    for drug_id in selected_ids:
        c = analog_curve_long[analog_curve_long["drug_id"] == drug_id].sort_values("month")
        rx = c["rx"].values.astype(float)
        curves[drug_id] = rx
        peaks.append(rx.max())
        month_to_peak.append(int(c["month"].values[rx.argmax()]))
        # growth rate: avg month-over-month % growth over first 6 months
        first6 = rx[:6]
        pct_changes = np.diff(first6) / np.where(first6[:-1] == 0, 1, first6[:-1])
        growth_rates.append(np.mean(pct_changes))

    # align all curves to same length (36 months) for weighted averaging
    max_len = max(len(v) for v in curves.values())
    aligned = np.array([np.pad(v, (0, max_len - len(v)), constant_values=np.nan)
                         for v in curves.values()])

    w = np.array([weights[d] for d in selected_ids])
    w = w / w.sum()

    analog_mean_rx = float(np.nanmean(aligned))
    analog_weighted_rx_curve = np.nansum(aligned * w[:, None], axis=0)  # weighted monthly curve

    analog_variability = float(np.nanstd(aligned, axis=0).mean())

    features = {
        "top_analog_similarity": float(top5_df["similarity"].iloc[0]),
        "analog_mean_rx": analog_mean_rx,
        "analog_growth_rate": float(np.mean(growth_rates)),
        "analog_peak_rx": float(np.mean(peaks)),
        "analog_month_to_peak": float(np.mean(month_to_peak)),
        "analog_variability": analog_variability,
    }
    return features, analog_weighted_rx_curve


# ---------------------------------------------------------------------------
# 3. Encode static/product features (same encoding logic as Stage 2)
# ---------------------------------------------------------------------------
def encode_static_features(new_static_row):
    row = new_static_row.iloc[0]
    encoded = {
        f"moa_{row['mechanism_of_action']}": 1,
        f"route_{row['route_of_administration']}": 1,
        f"specialty_{row['target_specialty']}": 1,
        f"quarter_{row['launch_quarter']}": 1,
        "market_size": float(row["market_size"]),
        "competitive_density": float(row["competitive_density"]),
        "payer_restrictiveness": float(row["payer_restrictiveness"]),
        "promotional_intensity": float(row["promotional_intensity"]),
        "price_tier": float(row["price_tier"]),
        "special_designation": int(row["special_designation"]),
    }
    return encoded


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    new_curve = pd.read_csv(os.path.join(PREP_DIR, "new_drug_rx_early_long.csv"))
    analog_curve_long = pd.read_csv(os.path.join(PREP_DIR, "analog_rx_curve_long.csv"))
    new_static = pd.read_csv(os.path.join(PREP_DIR, "new_drug_static_clean.csv"))
    top5_df = pd.read_csv(os.path.join(EMBED_DIR, "top5_analogs_selected.csv"))

    print("=" * 60)
    print("STAGE 4 — FEATURE ENGINEERING")
    print("=" * 60)

    new_rx_features = build_new_drug_rx_features(new_curve)
    print("\nNew-drug early-Rx features:")
    for k, v in new_rx_features.items():
        print(f"  {k}: {v}")

    analog_features, weighted_curve = build_analog_features(top5_df, analog_curve_long)
    print("\nAnalog-derived features (from top 5 selected analogs):")
    for k, v in analog_features.items():
        print(f"  {k}: {v}")

    static_features = encode_static_features(new_static)
    print(f"\nEncoded static features: {len(static_features)} fields")

    # --- combine everything into one final row ---
    final_row = {"drug_id": new_static["drug_id"].iloc[0]}
    final_row.update(new_rx_features)
    final_row.update(analog_features)
    final_row.update(static_features)

    final_df = pd.DataFrame([final_row])
    final_df.to_csv(os.path.join(OUT_DIR, "final_model_input.csv"), index=False)

    # save the analog weighted monthly curve separately (used by Analog/Bass models)
    weighted_curve_df = pd.DataFrame({
        "month": np.arange(1, len(weighted_curve) + 1),
        "analog_weighted_rx": weighted_curve,
    })
    weighted_curve_df.to_csv(os.path.join(OUT_DIR, "analog_weighted_curve.csv"), index=False)

    print(f"\nFinal engineered feature count: {len(final_row) - 1}")
    print(f"Saved -> {OUT_DIR}/final_model_input.csv")
    print(f"Saved -> {OUT_DIR}/analog_weighted_curve.csv "
          f"({len(weighted_curve_df)} months, used later by Analog+Bass models)")


if __name__ == "__main__":
    main()