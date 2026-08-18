# ============================================================
# PREPROCESSING FOR DRUG ANALOG EMBEDDING SIMILARITY
# ============================================================

import json
import pandas as pd
import numpy as np


# ============================================================
# 1. LOAD JSON FILES
# ============================================================

with open("analog_drugs.json", "r") as f:
    analog_drugs = json.load(f)

with open("new_drug.json", "r") as f:
    new_drug = json.load(f)


print("Analog drugs:", len(analog_drugs))
print("New drug:", new_drug["drug_name"])


# ============================================================
# 2. CONVERT ANALOG DATA TO DATAFRAME
# ============================================================

# Remove rx_curve temporarily because it is
# time-series data and will be processed separately.

analog_data = []

for drug in analog_drugs:

    row = {
        "drug_id": drug["drug_id"],
        "drug_name": drug["drug_name"],
        "mechanism_of_action": drug["mechanism_of_action"],
        "route_of_administration": drug["route_of_administration"],
        "target_specialty": drug["target_specialty"],
        "market_size": drug["market_size"],
        "competitive_density": drug["competitive_density"],
        "payer_restrictiveness": drug["payer_restrictiveness"],
        "launch_quarter": drug["launch_quarter"],
        "promotional_intensity": drug["promotional_intensity"],
        "special_designation": drug["special_designation"],
        "price_tier": drug["price_tier"]
    }

    analog_data.append(row)


analog_df = pd.DataFrame(analog_data)


# ============================================================
# 3. CONVERT NEW DRUG TO DATAFRAME
# ============================================================

new_drug_df = pd.DataFrame([{
    "drug_id": new_drug["drug_id"],
    "drug_name": new_drug["drug_name"],
    "mechanism_of_action": new_drug["mechanism_of_action"],
    "route_of_administration": new_drug["route_of_administration"],
    "target_specialty": new_drug["target_specialty"],
    "market_size": new_drug["market_size"],
    "competitive_density": new_drug["competitive_density"],
    "payer_restrictiveness": new_drug["payer_restrictiveness"],
    "launch_quarter": new_drug["launch_quarter"],
    "promotional_intensity": new_drug["promotional_intensity"],
    "special_designation": new_drug["special_designation"],
    "price_tier": new_drug["price_tier"]
}])


# ============================================================
# 4. CHECK MISSING VALUES
# ============================================================

print("\nMissing values before preprocessing:")

print(analog_df.isnull().sum())


# ============================================================
# 5. REMOVE DUPLICATE DRUGS
# ============================================================

analog_df = analog_df.drop_duplicates(
    subset=["drug_id"]
)


# ============================================================
# 6. HANDLE MISSING VALUES
# ============================================================

categorical_columns = [
    "mechanism_of_action",
    "route_of_administration",
    "target_specialty",
    "launch_quarter"
]

numerical_columns = [
    "market_size",
    "competitive_density",
    "payer_restrictiveness",
    "promotional_intensity",
    "price_tier"
]


# Fill categorical missing values
for column in categorical_columns:

    analog_df[column] = analog_df[column].fillna(
        "Unknown"
    )

    new_drug_df[column] = new_drug_df[column].fillna(
        "Unknown"
    )


# Fill numerical missing values using median
for column in numerical_columns:

    analog_df[column] = analog_df[column].fillna(
        analog_df[column].median()
    )

    new_drug_df[column] = new_drug_df[column].fillna(
        analog_df[column].median()
    )


# ============================================================
# 7. CONVERT BOOLEAN VALUE
# ============================================================

analog_df["special_designation"] = (
    analog_df["special_designation"]
    .astype(bool)
)

new_drug_df["special_designation"] = (
    new_drug_df["special_designation"]
    .astype(bool)
)


# ============================================================
# 8. NORMALIZE NUMERICAL FEATURES
# ============================================================

# This makes numerical values comparable.
# Example:
# market size can be millions
# competitive density is only 1-5

for column in numerical_columns:

    min_value = analog_df[column].min()
    max_value = analog_df[column].max()

    if max_value != min_value:

        analog_df[column] = (
            analog_df[column] - min_value
        ) / (
            max_value - min_value
        )

        new_drug_df[column] = (
            new_drug_df[column] - min_value
        ) / (
            max_value - min_value
        )

    else:

        analog_df[column] = 0
        new_drug_df[column] = 0


# ============================================================
# 9. CLEAN TEXT COLUMNS
# ============================================================

text_columns = [
    "drug_name",
    "mechanism_of_action",
    "route_of_administration",
    "target_specialty",
    "launch_quarter"
]


for column in text_columns:

    analog_df[column] = (
        analog_df[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    new_drug_df[column] = (
        new_drug_df[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )


# ============================================================
# 10. CREATE TEXT FOR EMBEDDING
# ============================================================

def create_embedding_text(row):

    return (
        f"drug name {row['drug_name']}; "
        f"mechanism of action {row['mechanism_of_action']}; "
        f"route of administration {row['route_of_administration']}; "
        f"target specialty {row['target_specialty']}; "
        f"market size {row['market_size']:.4f}; "
        f"competitive density {row['competitive_density']:.4f}; "
        f"payer restrictiveness {row['payer_restrictiveness']:.4f}; "
        f"launch quarter {row['launch_quarter']}; "
        f"promotional intensity {row['promotional_intensity']:.4f}; "
        f"special designation {row['special_designation']}; "
        f"price tier {row['price_tier']:.4f}"
    )


# Create embedding text for analog drugs
analog_df["embedding_text"] = analog_df.apply(
    create_embedding_text,
    axis=1
)


# Create embedding text for new drug
new_drug_df["embedding_text"] = new_drug_df.apply(
    create_embedding_text,
    axis=1
)


# ============================================================
# 11. PROCESS RX CURVES SEPARATELY
# ============================================================

rx_data = []

for drug in analog_drugs:

    for point in drug["rx_curve"]:

        rx_data.append({
            "drug_id": drug["drug_id"],
            "month": point["month"],
            "rx": point["rx"]
        })


rx_df = pd.DataFrame(rx_data)


# ============================================================
# 12. CHECK RX DATA
# ============================================================

print("\nRX data shape:")
print(rx_df.shape)

print("\nMissing RX values:")
print(rx_df.isnull().sum())


# ============================================================
# 13. HANDLE RX MISSING VALUES
# ============================================================

rx_df["rx"] = rx_df.groupby(
    "drug_id"
)["rx"].transform(
    lambda x: x.interpolate()
)


# ============================================================
# 14. NORMALIZE RX CURVES
# ============================================================

rx_df["rx_normalized"] = (
    rx_df.groupby("drug_id")["rx"]
    .transform(
        lambda x: x / x.max()
    )
)


# ============================================================
# 15. SAVE PREPROCESSED DATA
# ============================================================

analog_df.to_csv(
    "preprocessed_analog_drugs.csv",
    index=False
)

new_drug_df.to_csv(
    "preprocessed_new_drug.csv",
    index=False
)

rx_df.to_csv(
    "preprocessed_rx_curves.csv",
    index=False
)


# ============================================================
# 16. DISPLAY RESULTS
# ============================================================

print("\n==========================================")
print("PREPROCESSING COMPLETED")
print("==========================================")

print("\nAnalog data:")
print(analog_df.head())

print("\nNew drug:")
print(new_drug_df.head())

print("\nRX data:")
print(rx_df.head())


print("\nFiles created:")

print("1. preprocessed_analog_drugs.csv")
print("2. preprocessed_new_drug.csv")
print("3. preprocessed_rx_curves.csv")