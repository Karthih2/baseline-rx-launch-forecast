"""
Analog Similarity service.

Step 5 of the pipeline:
 - Calculate cosine similarity between the new drug and all analog drugs
 - Rank analogs by similarity
 - Select the Top-K most similar analogs
 - Calculate and store similarity scores and weights (normalized so
   selected analog weights sum to 1, used later to blend curves)
"""
from typing import List

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from app.config import DEFAULT_TOP_K


def rank_analogs_by_similarity(
    new_vector: np.ndarray, analog_matrix: np.ndarray, analog_ids: List[str]
) -> pd.DataFrame:
    """Returns a dataframe with columns [drug_id, similarity_score],
    sorted descending by similarity."""
    sims = cosine_similarity(new_vector, analog_matrix)[0]
    # cosine_similarity can be undefined (NaN) for all-zero vectors; treat as 0
    sims = np.nan_to_num(sims, nan=0.0)
    df = pd.DataFrame({"drug_id": analog_ids, "similarity_score": sims})
    df = df.sort_values("similarity_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def select_top_k(ranked_df: pd.DataFrame, top_k: int = DEFAULT_TOP_K) -> pd.DataFrame:
    """Select the top-K analogs and compute normalized blend weights.

    Weighting scheme: similarity scores are shifted to be non-negative
    (cosine similarity can be negative for very dissimilar drugs) and then
    normalized to sum to 1 across the selected set. If every selected
    similarity is 0 or negative, falls back to equal weights.
    """
    top_k = max(1, min(top_k, len(ranked_df)))
    selected = ranked_df.head(top_k).copy()

    shifted = selected["similarity_score"].clip(lower=0)
    total = shifted.sum()
    if total <= 0:
        selected["weight"] = 1.0 / len(selected)
    else:
        selected["weight"] = shifted / total

    return selected.reset_index(drop=True)
