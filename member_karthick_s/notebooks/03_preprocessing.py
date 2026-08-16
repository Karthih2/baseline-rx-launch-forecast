"""
STAGE 3 — PREPROCESSING  (FIXED + OPTIMIZED)
Reads analog_drugs.json + new_drug.json, flattens nested Rx curves into
long format, validates ordering, normalizes Rx values, cleans/standardizes
static features. Saves clean CSVs for the feature engineering stage.
"""

import json
import os
import numpy as np
import pandas as pd

DATA_DIR = "../01_data"
OUT_DIR = "../03_preprocessed"
os.makedirs(OUT_DIR, exist_ok=True)

STATIC_COLS = [
    "drug_id", "drug_name", "mechanism_of_action", "route_of_administration",
    "target_specialty", "market_size", "competitive_density",
    "payer_restrictiveness", "launch_quarter", "promotional_intensity",
    "special_designation", "price_tier",
]

CATEGORICAL_COLS = [
    "drug_id", "drug_name", "mechanism_of_action",
    "route_of_administration", "target_specialty", "launch_quarter",
]

# Single source of truth for valid bounds of each numeric static field.
# MUST stay in sync with the randint()/uniform() ranges used in Stage 1
# (generate_datasets.py -> generate_static_features()).
VALID_RANGES = {
    "market_size": (1, None),              # no hard upper bound, floor only
    "competitive_density": (1, 5),
    "payer_restrictiveness": (1, 5),
    "promotional_intensity": (1, 5),       # FIXED: was (1, 3)
    "price_tier": (1, 5),                  # FIXED: was (1, 3)
}


def load_json(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 1. Flatten nested curves into long format
# ---------------------------------------------------------------------------
def flatten_analog_curves(analogs):
    rows = [
        {"drug_id": d["drug_id"], "month": pt["month"], "rx": pt["rx"]}
        for d in analogs for pt in d["rx_curve"]
    ]
    df = pd.DataFrame(rows)
    df = df.sort_values(["drug_id", "month"]).reset_index(drop=True)
    return df


def flatten_new_drug_curve(new_drug):
    rows = [{"drug_id": new_drug["drug_id"], "week": pt["week"], "rx": pt["rx"]}
            for pt in new_drug["early_rx"]]
    df = pd.DataFrame(rows).sort_values(["drug_id", "week"]).reset_index(drop=True)
    return df


def build_static_df(records):
    df = pd.DataFrame([{c: d[c] for c in STATIC_COLS} for d in records])
    for c in CATEGORICAL_COLS:
        df[c] = df[c].astype("string")
    return df


# ---------------------------------------------------------------------------
# 2. Validation checks (missing, duplicates, dtypes, ordering, ranges)
# ---------------------------------------------------------------------------
def validate_long_curve(df, id_col, time_col, expected_len=None, label=""):
    issues = []

    dup = df.duplicated(subset=[id_col, time_col]).sum()
    if dup > 0:
        issues.append(f"{dup} duplicate ({id_col},{time_col}) rows")

    n_missing = df["rx"].isna().sum()
    if n_missing > 0:
        issues.append(f"{n_missing} missing rx values")

    n_negative = (df["rx"] < 0).sum()
    if n_negative > 0:
        issues.append(f"{n_negative} negative rx values")

    # ordering per drug (vectorized instead of per-group python loop)
    sorted_check = df.sort_values([id_col, time_col])
    is_sorted_already = df[[id_col, time_col]].reset_index(drop=True).equals(
        sorted_check[[id_col, time_col]].reset_index(drop=True)
    )
    if not is_sorted_already:
        bad_order = sum(
            not np.all(grp[time_col].values == np.sort(grp[time_col].values))
            for _, grp in df.groupby(id_col)
        )
        if bad_order > 0:
            issues.append(f"{bad_order} drugs with out-of-order {time_col}")

    if expected_len is not None:
        counts = df.groupby(id_col).size()
        bad_len = counts[counts != expected_len]
        if len(bad_len) > 0:
            issues.append(f"{len(bad_len)} drugs without exactly {expected_len} points")

    print(f"[{label}] validation: {'OK - no issues' if not issues else '; '.join(issues)}")
    return issues


def validate_static(df, label="", check_ranges=False):
    issues = []
    if df["drug_id"].duplicated().sum() > 0:
        issues.append("duplicate drug_id")

    n_missing = df.isna().sum().sum()
    if n_missing > 0:
        issues.append(f"{n_missing} missing static values")

    if check_ranges:
        for col, (lo, hi) in VALID_RANGES.items():
            if col not in df.columns:
                continue
            below = (df[col] < lo).sum() if lo is not None else 0
            above = (df[col] > hi).sum() if hi is not None else 0
            if below or above:
                issues.append(f"{col}: {below} below {lo}, {above} above {hi} (post-clean)")

    print(f"[{label}] validation: {'OK - no issues' if not issues else '; '.join(issues)}")
    return issues


# ---------------------------------------------------------------------------
# 3. Clean / standardize static features (dtypes, invalid ranges)
# ---------------------------------------------------------------------------
def clean_static_df(df, label=""):
    df = df.copy()
    df["special_designation"] = df["special_designation"].astype(bool)

    for col in ["market_size", "competitive_density", "payer_restrictiveness",
                "promotional_intensity", "price_tier"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clip out-of-range values to valid bounds (instead of dropping rows),
    # using VALID_RANGES as the single source of truth. Report how many
    # values actually needed clipping so a bounds mismatch is visible.
    for col, (lo, hi) in VALID_RANGES.items():
        if col not in df.columns:
            continue
        before = df[col].copy()
        df[col] = df[col].clip(lower=lo, upper=hi)
        n_clipped = (before != df[col]).sum()
        if n_clipped > 0:
            print(f"  [{label}] clipped {n_clipped} out-of-range value(s) in '{col}' "
                  f"to [{lo}, {hi}]")

    return df


# ---------------------------------------------------------------------------
# 4. Normalize Rx curves (% of peak) — separate column, raw kept alongside
# ---------------------------------------------------------------------------
def normalize_curve(df, id_col):
    df = df.copy()
    df["rx"] = df["rx"].clip(lower=0)  # handle any negative/zero safely
    peak_per_drug = df.groupby(id_col)["rx"].transform("max")
    peak_per_drug = peak_per_drug.replace(0, 1)  # avoid divide-by-zero
    df["rx_pct_of_peak"] = df["rx"] / peak_per_drug
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    analogs = load_json("analog_drugs.json")
    new_drug = load_json("new_drug.json")

    # --- flatten ---
    analog_curve_long = flatten_analog_curves(analogs)
    new_curve_long = flatten_new_drug_curve(new_drug)
    analog_static = build_static_df(analogs)
    new_static = build_static_df([new_drug])

    print("=" * 60)
    print("STAGE 3 — PREPROCESSING")
    print("=" * 60)

    # --- validate (before cleaning) ---
    validate_long_curve(analog_curve_long, "drug_id", "month", expected_len=36,
                         label="analog rx_curve")
    validate_long_curve(new_curve_long, "drug_id", "week", label="new_drug early_rx")
    validate_static(analog_static, label="analog static features (pre-clean)")
    validate_static(new_static, label="new_drug static features (pre-clean)")

    # --- clean static features ---
    print()
    analog_static_clean = clean_static_df(analog_static, label="analog")
    new_static_clean = clean_static_df(new_static, label="new_drug")

    # --- post-clean range check (defensive; should always pass now) ---
    validate_static(analog_static_clean, label="analog static features (post-clean)",
                     check_ranges=True)
    validate_static(new_static_clean, label="new_drug static features (post-clean)",
                     check_ranges=True)

    # --- remove accidental exact-duplicate rows (not legitimate repeats) ---
    before = len(analog_curve_long)
    analog_curve_long = analog_curve_long.drop_duplicates(subset=["drug_id", "month"])
    after = len(analog_curve_long)
    if before != after:
        print(f"\nRemoved {before - after} accidental duplicate analog curve rows")

    # --- normalize Rx curves (% of peak, raw rx kept too) ---
    analog_curve_norm = normalize_curve(analog_curve_long, "drug_id")
    new_curve_norm = normalize_curve(new_curve_long, "drug_id")

    # --- save outputs ---
    analog_static_clean.to_csv(os.path.join(OUT_DIR, "analog_static_clean.csv"), index=False)
    new_static_clean.to_csv(os.path.join(OUT_DIR, "new_drug_static_clean.csv"), index=False)
    analog_curve_norm.to_csv(os.path.join(OUT_DIR, "analog_rx_curve_long.csv"), index=False)
    new_curve_norm.to_csv(os.path.join(OUT_DIR, "new_drug_rx_early_long.csv"), index=False)

    print(f"\nSaved cleaned static features -> {OUT_DIR}/analog_static_clean.csv, "
          f"new_drug_static_clean.csv")
    print(f"Saved flattened + normalized curves -> {OUT_DIR}/analog_rx_curve_long.csv, "
          f"new_drug_rx_early_long.csv")

    # --- final summary ---
    print("\nOutput summary")
    print("-" * 60)
    print(f"analog_static_clean:      {analog_static_clean.shape}")
    print(f"new_drug_static_clean:    {new_static_clean.shape}")
    print(f"analog_rx_curve_long:     {analog_curve_norm.shape}")
    print(f"new_drug_rx_early_long:   {new_curve_norm.shape}")
    print("\nPost-clean value distributions (sanity check vs. Stage 1 generation ranges):")
    for col in ["competitive_density", "payer_restrictiveness",
                "promotional_intensity", "price_tier"]:
        print(f"  {col}: {analog_static_clean[col].value_counts().sort_index().to_dict()}")


if __name__ == "__main__":
    main()