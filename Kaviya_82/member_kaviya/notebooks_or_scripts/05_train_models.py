# ============================================================
# MODEL TRAINING - DRUG RX FORECASTING
# ============================================================

# Install if required:
# pip install pandas numpy scikit-learn joblib

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import joblib


# ============================================================
# 1. LOAD FEATURE-ENGINEERED DATA
# ============================================================

analog_df = pd.read_csv(
    "feature_engineered_analog_drugs.csv"
)

rx_df = pd.read_csv(
    "preprocessed_rx_curves.csv"
)


print("Analog data shape:", analog_df.shape)
print("RX data shape:", rx_df.shape)


# ============================================================
# 2. MERGE DRUG FEATURES WITH RX DATA
# ============================================================

model_df = rx_df.merge(
    analog_df,
    on="drug_id",
    how="left"
)


# ============================================================
# 3. CREATE TIME-BASED FEATURES
# ============================================================

model_df["month_squared"] = (
    model_df["month"] ** 2
)

model_df["month_log"] = np.log1p(
    model_df["month"]
)


# ============================================================
# 4. CREATE LAG FEATURES
# ============================================================

model_df = model_df.sort_values(
    ["drug_id", "month"]
)


# Previous month's RX
model_df["rx_lag_1"] = (
    model_df
    .groupby("drug_id")["rx"]
    .shift(1)
)


# Two months before
model_df["rx_lag_2"] = (
    model_df
    .groupby("drug_id")["rx"]
    .shift(2)
)


# Three months before
model_df["rx_lag_3"] = (
    model_df
    .groupby("drug_id")["rx"]
    .shift(3)
)


# ============================================================
# 5. REMOVE ROWS WITH MISSING LAG VALUES
# ============================================================

model_df = model_df.dropna(
    subset=[
        "rx_lag_1",
        "rx_lag_2",
        "rx_lag_3"
    ]
)


# ============================================================
# 6. SELECT FEATURES
# ============================================================

features = [

    # Time features
    "month",
    "month_squared",
    "month_log",

    # Previous RX values
    "rx_lag_1",
    "rx_lag_2",
    "rx_lag_3",

    # Drug characteristics
    "log_market_size",
    "competitive_density",
    "payer_restrictiveness",
    "promotional_intensity",
    "price_tier",
    "special_designation_numeric",

    # Engineered features
    "competition_pressure",
    "promotion_to_competition",
    "market_attractiveness",
    "price_promotion_index",
    "payer_access_score"
]


X = model_df[features]

y = model_df["rx"]


# ============================================================
# 7. TRAIN-TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 8. CREATE RANDOM FOREST MODEL
# ============================================================

model = RandomForestRegressor(

    n_estimators=200,

    max_depth=12,

    min_samples_split=4,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1
)


# ============================================================
# 9. TRAIN MODEL
# ============================================================

model.fit(
    X_train,
    y_train
)


print("\nModel training completed!")


# ============================================================
# 10. MAKE PREDICTIONS
# ============================================================

y_pred = model.predict(
    X_test
)


# ============================================================
# 11. MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


print("\n==========================================")
print("MODEL PERFORMANCE")
print("==========================================")

print(
    f"MAE  : {mae:.2f}"
)

print(
    f"RMSE : {rmse:.2f}"
)

print(
    f"R²   : {r2:.4f}"
)


# ============================================================
# 12. FEATURE IMPORTANCE
# ============================================================

importance_df = pd.DataFrame({

    "feature": features,

    "importance": model.feature_importances_

})


importance_df = importance_df.sort_values(
    "importance",
    ascending=False
)


print("\n==========================================")
print("FEATURE IMPORTANCE")
print("==========================================")

print(
    importance_df
)


# ============================================================
# 13. SAVE MODEL
# ============================================================

joblib.dump(
    model,
    "drug_rx_forecasting_model.pkl"
)


# Save feature names too
joblib.dump(
    features,
    "model_features.pkl"
)


# ============================================================
# 14. SAVE PREDICTIONS
# ============================================================

results = pd.DataFrame({

    "actual_rx": y_test.values,

    "predicted_rx": y_pred

})


results.to_csv(
    "model_predictions.csv",
    index=False
)


# ============================================================
# 15. FINAL OUTPUT
# ============================================================

print("\n==========================================")
print("MODEL TRAINING COMPLETED")
print("==========================================")

print(
    "\nModel saved as:"
)

print(
    "drug_rx_forecasting_model.pkl"
)

print(
    "\nPredictions saved as:"
)

print(
    "model_predictions.csv"
)