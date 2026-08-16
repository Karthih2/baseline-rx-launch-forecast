"""
STAGE 2 — EMBEDDING / SIMILARITY
Reads analog_drugs.json + new_drug.json, encodes static features,
computes cosine similarity, selects top 5 analogs.
"""

import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = "../01_data"
OUT_DIR = "02_embeddings"
import os
os.makedirs(OUT_DIR, exist_ok=True)

CATEGORICAL_COLS = ["mechanism_of_action", "route_of_administration",
                     "target_specialty", "launch_quarter"]
ORDINAL_COLS = ["payer_restrictiveness", "promotional_intensity", "price_tier"]
NUMERIC_COLS = ["market_size", "competitive_density"]
BINARY_COLS = ["special_designation"]

TOP_K = 5


def load_static_df(analogs, new_drug):
    rows = []
    for d in analogs:
        row = {c: d[c] for c in CATEGORICAL_COLS + ORDINAL_COLS + NUMERIC_COLS + BINARY_COLS}
        row["drug_id"] = d["drug_id"]
        rows.append(row)
    new_row = {c: new_drug[c] for c in CATEGORICAL_COLS + ORDINAL_COLS + NUMERIC_COLS + BINARY_COLS}
    new_row["drug_id"] = new_drug["drug_id"]
    rows.append(new_row)
    df = pd.DataFrame(rows)
    df[BINARY_COLS] = df[BINARY_COLS].astype(int)
    return df


def build_feature_matrix(df):
    ohe = OneHotEncoder(sparse_output=False)
    cat_encoded = ohe.fit_transform(df[CATEGORICAL_COLS])
    cat_cols_out = ohe.get_feature_names_out(CATEGORICAL_COLS)

    scaler = StandardScaler()
    num_scaled = scaler.fit_transform(df[ORDINAL_COLS + NUMERIC_COLS])
    num_cols_out = ORDINAL_COLS + NUMERIC_COLS

    binary_vals = df[BINARY_COLS].values

    X = np.hstack([cat_encoded, num_scaled, binary_vals])
    feature_names = list(cat_cols_out) + num_cols_out + BINARY_COLS
    return X, feature_names


def main():
    with open(os.path.join(DATA_DIR, "analog_drugs.json")) as f:
        analogs = json.load(f)
    with open(os.path.join(DATA_DIR, "new_drug.json")) as f:
        new_drug = json.load(f)

    df = load_static_df(analogs, new_drug)
    X, feature_names = build_feature_matrix(df)

    new_idx = df.index[df["drug_id"] == new_drug["drug_id"]][0]
    analog_idx = df.index[df["drug_id"] != new_drug["drug_id"]]

    new_vec = X[new_idx].reshape(1, -1)
    analog_vecs = X[analog_idx]

    sims = cosine_similarity(new_vec, analog_vecs)[0]

    sim_df = pd.DataFrame({
        "drug_id": df.loc[analog_idx, "drug_id"].values,
        "similarity": sims
    }).sort_values("similarity", ascending=False).reset_index(drop=True)

    sim_df.to_csv(os.path.join(OUT_DIR, "similarity_vectors.csv"), index=False)

    top5 = sim_df.head(TOP_K).copy()
    weight_sum = top5["similarity"].sum()
    top5["weight"] = top5["similarity"] / weight_sum
    top5.to_csv(os.path.join(OUT_DIR, "top5_analogs_selected.csv"), index=False)

    print("=" * 60)
    print("STAGE 2 — EMBEDDING / SIMILARITY COMPLETE")
    print("=" * 60)
    print(f"Feature vector length: {X.shape[1]}")
    print(f"Feature names: {feature_names}")
    print(f"\nAll {len(sim_df)} analog similarity scores saved -> "
          f"{OUT_DIR}/similarity_vectors.csv")
    print(f"\nTop {TOP_K} analogs selected:")
    print(top5.to_string(index=False))
    print(f"\nSaved -> {OUT_DIR}/top5_analogs_selected.csv")


if __name__ == "__main__":
    main()