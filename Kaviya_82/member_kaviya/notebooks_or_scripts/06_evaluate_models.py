# ============================================================
# MODEL EVALUATION - DRUG RX FORECASTING
# ============================================================

# Install if required:
# pip install pandas numpy scikit-learn joblib

import pandas as pd
import numpy as np

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.model_selection import TimeSeriesSplit


# ============================================================
# 1. LOAD DATA
# ============================================================

analog_df = pd.read_csv(
    "feature_engineered_analog_drugs.csv"
)

rx_df = pd.read_csv(
    "preprocessed_rx_curves.csv"
)


# ============================================================
# 2. MERGE DATA
# ============================================================

model_df = rx_df.merge(
    analog_df,
    on="drug_id",
    how="left"
)


# ============================================================
# 3. SORT BY TIME
# ============================================================

model_df = model_df.sort_values(
    ["month", "drug_id"]
)


# ============================================================
# 4. CREATE TIME FEATURES
# ============================================================

model_df["month_squared"] = (
    model_df["month"] ** 2
)

model_df["month_log"] = np.log1p(
    model_df["month"]
)


# ============================================================
# 5. CREATE LAG FEATURES
# ============================================================

model_df = model_df.sort_values(
    ["drug_id", "month"]
)

model_df["rx_lag_1"] = (
    model_df
    .groupby("drug_id")["rx"]
    .shift(1)
)

model_df["rx_lag_2"] = (
    model_df
    .groupby("drug_id")["rx"]
    .shift(2)
)

model_df["rx_lag_3"] = (
    model_df
    .groupby("drug_id")["rx"]
    .shift(3)
)


# Remove rows where lag values are unavailable
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

    "month",
    "month_squared",
    "month_log",

    "rx_lag_1",
    "rx_lag_2",
    "rx_lag_3",

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
    "payer_access_score"
]


X = model_df[features]

y = model_df["rx"]


# ============================================================
# 7. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

# Use first 80% of time periods for training
# and last 20% for testing.

unique_months = sorted(
    model_df["month"].unique()
)

split_index = int(
    len(unique_months) * 0.80
)

train_months = unique_months[:split_index]

test_months = unique_months[split_index:]


train_data = model_df[
    model_df["month"].isin(train_months)
]

test_data = model_df[
    model_df["month"].isin(test_months)
]


X_train = train_data[features]

y_train = train_data["rx"]

X_test = test_data[features]

y_test = test_data["rx"]


print("Training months:", train_months)

print("Testing months:", test_months)

print(
    "\nTraining samples:",
    len(X_train)
)

print(
    "Testing samples:",
    len(X_test)
)


# ============================================================
# 8. CREATE MODELS
# ============================================================

models = {

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )
}


# ============================================================
# 9. TRAIN AND EVALUATE MODELS
# ============================================================

results = []


for model_name, model in models.items():

    print(
        f"\nTraining {model_name}..."
    )

    # Train
    model.fit(
        X_train,
        y_train
    )

    # Predict
    predictions = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Evaluation metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    # MAPE
    non_zero = y_test != 0

    mape = np.mean(
        np.abs(
            (
                y_test[non_zero]
                - predictions[non_zero]
            )
            / y_test[non_zero]
        )
    ) * 100


    # Store results
    results.append({

        "Model": model_name,

        "MAE": mae,

        "RMSE": rmse,

        "R2": r2,

        "MAPE (%)": mape
    })


# ============================================================
# 10. CREATE RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)


print("\n==========================================")
print("MODEL EVALUATION RESULTS")
print("==========================================")

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 11. SELECT BEST MODEL
# ============================================================

# Lower RMSE is better
best_model_name = (
    results_df
    .sort_values("RMSE")
    .iloc[0]["Model"]
)


print(
    "\nBest model based on RMSE:"
)

print(
    best_model_name
)


# ============================================================
# 12. SAVE RESULTS
# ============================================================

results_df.to_csv(
    "model_evaluation_results.csv",
    index=False
)


# ============================================================
# 13. TRAIN BEST MODEL AGAIN
# ============================================================

best_model = models[
    best_model_name
]

best_model.fit(
    X_train,
    y_train
)


# ============================================================
# 14. SAVE BEST MODEL
# ============================================================

import joblib

joblib.dump(
    best_model,
    "best_drug_rx_model.pkl"
)

joblib.dump(
    features,
    "best_model_features.pkl"
)


print(
    "\nBest model saved as:"
)

print(
    "best_drug_rx_model.pkl"
)

print(
    "\nEvaluation results saved as:"
)

print(
    "model_evaluation_results.csv"
)