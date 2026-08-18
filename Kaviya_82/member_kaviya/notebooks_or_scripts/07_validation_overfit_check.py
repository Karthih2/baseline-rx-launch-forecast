# ============================================================
# VALIDATION AND OVERFITTING CHECK
# DRUG RX FORECASTING
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
# 3. SORT DATA BY TIME
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


# Remove rows without enough historical information
model_df = model_df.dropna(
    subset=[
        "rx_lag_1",
        "rx_lag_2",
        "rx_lag_3"
    ]
)


# ============================================================
# 6. FEATURES
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
# 7. TIME-SERIES CROSS VALIDATION
# ============================================================

tscv = TimeSeriesSplit(
    n_splits=5
)


# ============================================================
# 8. MODELS
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
# 9. VALIDATION
# ============================================================

validation_results = []


for model_name, model in models.items():

    print("\n==========================================")
    print(model_name)
    print("==========================================")


    fold_number = 1

    fold_scores = []


    for train_index, validation_index in tscv.split(X):

        X_train = X.iloc[train_index]
        X_validation = X.iloc[validation_index]

        y_train = y.iloc[train_index]
        y_validation = y.iloc[validation_index]


        # Train model
        model.fit(
            X_train,
            y_train
        )


        # Training prediction
        train_prediction = model.predict(
            X_train
        )


        # Validation prediction
        validation_prediction = model.predict(
            X_validation
        )


        # ----------------------------------------------------
        # TRAINING METRICS
        # ----------------------------------------------------

        train_mae = mean_absolute_error(
            y_train,
            train_prediction
        )

        train_rmse = np.sqrt(
            mean_squared_error(
                y_train,
                train_prediction
            )
        )

        train_r2 = r2_score(
            y_train,
            train_prediction
        )


        # ----------------------------------------------------
        # VALIDATION METRICS
        # ----------------------------------------------------

        validation_mae = mean_absolute_error(
            y_validation,
            validation_prediction
        )

        validation_rmse = np.sqrt(
            mean_squared_error(
                y_validation,
                validation_prediction
            )
        )

        validation_r2 = r2_score(
            y_validation,
            validation_prediction
        )


        # ----------------------------------------------------
        # OVERFITTING GAP
        # ----------------------------------------------------

        rmse_gap = (
            validation_rmse -
            train_rmse
        )

        r2_gap = (
            train_r2 -
            validation_r2
        )


        print(
            f"\nFold {fold_number}"
        )

        print(
            f"Train RMSE      : {train_rmse:.2f}"
        )

        print(
            f"Validation RMSE : {validation_rmse:.2f}"
        )

        print(
            f"Train R²        : {train_r2:.4f}"
        )

        print(
            f"Validation R²   : {validation_r2:.4f}"
        )

        print(
            f"RMSE Gap        : {rmse_gap:.2f}"
        )

        print(
            f"R² Gap          : {r2_gap:.4f}"
        )


        fold_scores.append({

            "Fold": fold_number,

            "Train_RMSE": train_rmse,

            "Validation_RMSE":
                validation_rmse,

            "Train_R2": train_r2,

            "Validation_R2":
                validation_r2,

            "RMSE_Gap": rmse_gap,

            "R2_Gap": r2_gap

        })


        fold_number += 1


    # ========================================================
    # AVERAGE VALIDATION RESULTS
    # ========================================================

    fold_df = pd.DataFrame(
        fold_scores
    )


    validation_results.append({

        "Model": model_name,

        "Average Train RMSE":
            fold_df["Train_RMSE"].mean(),

        "Average Validation RMSE":
            fold_df["Validation_RMSE"].mean(),

        "Average Train R2":
            fold_df["Train_R2"].mean(),

        "Average Validation R2":
            fold_df["Validation_R2"].mean(),

        "Average RMSE Gap":
            fold_df["RMSE_Gap"].mean(),

        "Average R2 Gap":
            fold_df["R2_Gap"].mean()

    })


# ============================================================
# 10. VALIDATION RESULTS
# ============================================================

validation_df = pd.DataFrame(
    validation_results
)


print("\n==========================================")
print("VALIDATION SUMMARY")
print("==========================================")

print(
    validation_df.to_string(
        index=False
    )
)


# ============================================================
# 11. OVERFITTING CHECK
# ============================================================

print("\n==========================================")
print("OVERFITTING CHECK")
print("==========================================")


for _, row in validation_df.iterrows():

    model_name = row["Model"]

    train_rmse = row[
        "Average Train RMSE"
    ]

    validation_rmse = row[
        "Average Validation RMSE"
    ]

    train_r2 = row[
        "Average Train R2"
    ]

    validation_r2 = row[
        "Average Validation R2"
    ]

    rmse_gap = row[
        "Average RMSE Gap"
    ]

    r2_gap = row[
        "Average R2 Gap"
    ]


    print(
        f"\nModel: {model_name}"
    )

    # --------------------------------------------------------
    # Overfitting rules
    # --------------------------------------------------------

    if (
        rmse_gap > validation_rmse * 0.30
        and r2_gap > 0.15
    ):

        print(
            "Result: POSSIBLE OVERFITTING"
        )

        print(
            "Training performance is "
            "much better than validation."
        )

    elif (
        rmse_gap > validation_rmse * 0.15
        or r2_gap > 0.10
    ):

        print(
            "Result: MILD OVERFITTING"
        )

        print(
            "Monitor model complexity."
        )

    else:

        print(
            "Result: NO SIGNIFICANT OVERFITTING"
        )

        print(
            "Training and validation "
            "performance are reasonably close."
        )


# ============================================================
# 12. SAVE VALIDATION RESULTS
# ============================================================

validation_df.to_csv(
    "validation_results.csv",
    index=False
)


print(
    "\nValidation results saved to:"
)

print(
    "validation_results.csv"
)