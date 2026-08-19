"""
Feature Engineering service.

Step 4 of the pipeline:
 - Extract relevant static features
 - Encode categorical features (one-hot, fit jointly on new + analog drugs
   so the resulting vector spaces are directly comparable)
 - Scale numerical features (StandardScaler, fit jointly)
 - Create feature vectors for the new drug and all analog drugs

Fully reusable: feature columns are discovered from what's actually present
in the uploaded files (required + optional columns from config), so a new
dataset with extra/fewer optional columns does not require code changes.
"""
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from app.config import (
    REQUIRED_FEATURE_COLUMNS,
    OPTIONAL_NUMERIC_FEATURES,
    OPTIONAL_CATEGORICAL_FEATURES,
)

# drug_id / drug_name are identifiers, never used as model features
_ID_COLUMNS = {"drug_id", "drug_name"}

# from the required contract, these are categorical / textual descriptors
_REQUIRED_CATEGORICAL = [
    c for c in REQUIRED_FEATURE_COLUMNS
    if c not in _ID_COLUMNS and c != "target_population"
]


def _present_columns(df: pd.DataFrame, candidates: List[str]) -> List[str]:
    return [c for c in candidates if c in df.columns]


def build_feature_matrix(
    new_features: pd.DataFrame, analog_features: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Combine the new drug (1 row) with all analogs (n rows), encode
    categoricals and scale numerics jointly, then split back apart.

    Returns:
        new_vector: shape (1, d)
        analog_matrix: shape (n, d)
        analog_ids: list of analog drug_id strings, in row order matching
            analog_matrix
    """
    new_df = new_features.copy()
    analog_df = analog_features.copy()
    analog_ids = analog_df["drug_id"].astype(str).tolist()

    new_df["__is_new__"] = 1
    analog_df["__is_new__"] = 0
    combined = pd.concat([new_df, analog_df], ignore_index=True, sort=False)

    categorical_cols = _present_columns(
        combined, _REQUIRED_CATEGORICAL + OPTIONAL_CATEGORICAL_FEATURES
    )
    numeric_cols = _present_columns(
        combined, ["target_population"] + OPTIONAL_NUMERIC_FEATURES
    )

    # --- categorical encoding (one-hot, fit jointly) ---
    if categorical_cols:
        cat_encoded = pd.get_dummies(
            combined[categorical_cols].astype(str), prefix=categorical_cols
        )
    else:
        cat_encoded = pd.DataFrame(index=combined.index)

    # --- numeric scaling (fit jointly) ---
    if numeric_cols:
        numeric_df = combined[numeric_cols].apply(pd.to_numeric, errors="coerce")
        numeric_df = numeric_df.fillna(numeric_df.median(numeric_only=True)).fillna(0)
        scaler = StandardScaler()
        numeric_scaled = pd.DataFrame(
            scaler.fit_transform(numeric_df), columns=numeric_cols, index=combined.index
        )
    else:
        numeric_scaled = pd.DataFrame(index=combined.index)

    feature_df = pd.concat([numeric_scaled, cat_encoded], axis=1).fillna(0)

    new_mask = combined["__is_new__"] == 1
    new_vector = feature_df[new_mask].to_numpy(dtype=float)
    analog_matrix = feature_df[~new_mask].to_numpy(dtype=float)

    return new_vector, analog_matrix, analog_ids
