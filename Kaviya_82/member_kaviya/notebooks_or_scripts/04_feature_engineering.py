# ============================================================
# FEATURE ENGINEERING FOR DRUG ANALOG PROJECT
# ============================================================

import pandas as pd
import numpy as np


# ============================================================
# 1. LOAD PREPROCESSED DATA
# ============================================================

analog_df = pd.read_csv(
    "preprocessed_analog_drugs.csv"
)

new_drug_df = pd.read_csv(
    "preprocessed_new_drug.csv"
)

rx_df = pd.read_csv(
    "preprocessed_rx_curves.csv"
)


# ============================================================
# 2. MARKET SIZE FEATURES
# ============================================================

# Log transformation reduces the effect of very large markets
analog_df["log_market_size"] = np.log1p(
    analog_df["market_size"]
)

new_drug_df["log_market_size"] = np.log1p(
    new_drug_df["market_size"]
)


# ============================================================
# 3. COMPETITION FEATURES
# ============================================================

# Higher competition = more difficult market
analog_df["competition_pressure"] = (
    analog_df["competitive_density"] *
    analog_df["payer_restrictiveness"]
)

new_drug_df["competition_pressure"] = (
    new_drug_df["competitive_density"] *
    new_drug_df["payer_restrictiveness"]
)


# ============================================================
# 4. PROMOTIONAL FEATURES
# ============================================================

# Promotion relative to competition
analog_df["promotion_to_competition"] = (
    analog_df["promotional_intensity"] /
    (analog_df["competitive_density"] + 1)
)

new_drug_df["promotion_to_competition"] = (
    new_drug_df["promotional_intensity"] /
    (new_drug_df["competitive_density"] + 1)
)


# ============================================================
# 5. MARKET ATTRACTIVENESS SCORE
# ============================================================

analog_df["market_attractiveness"] = (
    analog_df["market_size"] *
    (1 + analog_df["promotional_intensity"]) /
    (
        1 +
        analog_df["competitive_density"] +
        analog_df["payer_restrictiveness"]
    )
)

new_drug_df["market_attractiveness"] = (
    new_drug_df["market_size"] *
    (1 + new_drug_df["promotional_intensity"]) /
    (
        1 +
        new_drug_df["competitive_density"] +
        new_drug_df["payer_restrictiveness"]
    )
)


# ============================================================
# 6. PRICE-PROMOTION FEATURE
# ============================================================

analog_df["price_promotion_index"] = (
    analog_df["price_tier"] *
    analog_df["promotional_intensity"]
)

new_drug_df["price_promotion_index"] = (
    new_drug_df["price_tier"] *
    new_drug_df["promotional_intensity"]
)


# ============================================================
# 7. PAYER ACCESS SCORE
# ============================================================

# Lower payer restrictiveness = better access
analog_df["payer_access_score"] = (
    6 - analog_df["payer_restrictiveness"]
)

new_drug_df["payer_access_score"] = (
    6 - new_drug_df["payer_restrictiveness"]
)


# ============================================================
# 8. SPECIAL DESIGNATION FEATURE
# ============================================================

analog_df["special_designation_numeric"] = (
    analog_df["special_designation"]
    .astype(str)
    .str.lower()
    .map({
        "true": 1,
        "false": 0
    })
    .fillna(0)
)

new_drug_df["special_designation_numeric"] = (
    new_drug_df["special_designation"]
    .astype(str)
    .str.lower()
    .map({
        "true": 1,
        "false": 0
    })
    .fillna(0)
)


# ============================================================
# 9. RX CURVE FEATURES
# ============================================================

# Calculate summary statistics for every analog drug

rx_features = rx_df.groupby(
    "drug_id"
)["rx"].agg(
    [
        "mean",
        "std",
        "min",
        "max",
        "median"
    ]
).reset_index()


# Rename columns
rx_features = rx_features.rename(
    columns={
        "mean": "rx_mean",
        "std": "rx_std",
        "min": "rx_min",
        "max": "rx_max",
        "median": "rx_median"
    }
)


# ============================================================
# 10. RX GROWTH FEATURES
# ============================================================

def calculate_growth(group):

    group = group.sort_values("month")

    first_rx = group["rx"].iloc[0]
    last_rx = group["rx"].iloc[-1]

    if first_rx != 0:

        growth = (
            (last_rx - first_rx)
            / first_rx
        )

    else:

        growth = 0

    return growth


rx_growth = (
    rx_df.groupby("drug_id")
    .apply(calculate_growth)
    .reset_index(name="rx_growth")
)


# ============================================================
# 11. PEAK MONTH
# ============================================================

peak_month = (
    rx_df.loc[
        rx_df.groupby("drug_id")["rx"].idxmax()
    ][
        ["drug_id", "month"]
    ]
    .rename(
        columns={
            "month": "peak_month"
        }
    )
)


# ============================================================
# 12. MERGE RX FEATURES
# ============================================================

analog_df = analog_df.merge(
    rx_features,
    on="drug_id",
    how="left"
)

analog_df = analog_df.merge(
    rx_growth,
    on="drug_id",
    how="left"
)

analog_df = analog_df.merge(
    peak_month,
    on="drug_id",
    how="left"
)


# ============================================================
# 13. NORMALIZE ENGINEERED FEATURES
# ============================================================

engineered_features = [
    "competition_pressure",
    "promotion_to_competition",
    "market_attractiveness",
    "price_promotion_index",
    "payer_access_score",
    "rx_mean",
    "rx_std",
    "rx_min",
    "rx_max",
    "rx_median",
    "rx_growth",
    "peak_month"
]


for column in engineered_features:

    min_value = analog_df[column].min()
    max_value = analog_df[column].max()

    if max_value != min_value:

        analog_df[
            column + "_normalized"
        ] = (
            analog_df[column] - min_value
        ) / (
            max_value - min_value
        )

    else:

        analog_df[
            column + "_normalized"
        ] = 0


# ============================================================
# 14. CREATE FINAL FEATURE SET
# ============================================================

final_features = [
    "drug_id",
    "drug_name",
    "mechanism_of_action",
    "route_of_administration",
    "target_specialty",
    "log_market_size",
    "competitive_density",
    "payer_restrictiveness",
    "promotional_intensity",
    "price_tier",
    "special_designation_numeric",
    "competition_pressure",
    "promotion_to_competition",
    "market_attractiveness",
    "price_promotion_index",
    "payer_access_score",
    "rx_mean",
    "rx_std",
    "rx_min",
    "rx_max",
    "rx_median",
    "rx_growth",
    "peak_month"
]


final_analog_df = analog_df[
    final_features
]


# ============================================================
# 15. SAVE FEATURE-ENGINEERED DATA
# ============================================================

final_analog_df.to_csv(
    "feature_engineered_analog_drugs.csv",
    index=False
)

new_drug_df.to_csv(
    "feature_engineered_new_drug.csv",
    index=False
)


# ============================================================
# 16. DISPLAY RESULTS
# ============================================================

print("\n==========================================")
print("FEATURE ENGINEERING COMPLETED")
print("==========================================")

print(
    "\nFinal feature shape:",
    final_analog_df.shape
)

print(
    "\nEngineered features:"
)

print(
    final_analog_df.columns.tolist()
)

print(
    "\nSample data:"
)

print(
    final_analog_df.head()
)


print(
    "\nFiles created:"
)

print(
    "1. feature_engineered_analog_drugs.csv"
)

print(
    "2. feature_engineered_new_drug.csv"
)