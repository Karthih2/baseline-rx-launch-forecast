"""
Analog Curve service.

Step 6 of the pipeline:
 - Use the selected analogs and their similarity weights
 - Create a weighted/blended analog Rx curve, aligned month-by-month
   from launch month 1 through the longest selected analog's history
   (or the requested forecast horizon, whichever is longer, so the Bass
   fitting step below has enough shape to work with).
"""
from typing import Dict, List

import numpy as np
import pandas as pd


def build_blended_curve(
    analog_curves: Dict[str, pd.Series],
    selected: pd.DataFrame,
    min_length: int = 1,
) -> pd.Series:
    """
    Args:
        analog_curves: dict of drug_id -> pd.Series (month_number index)
        selected: dataframe with columns [drug_id, weight] for the chosen
            top-K analogs
        min_length: pad/extend the blended curve to at least this many months

    Returns:
        pd.Series indexed 1..N of the weighted-average monthly Rx curve.
        Analogs shorter than N contribute their last observed value going
        forward (flat continuation) rather than dragging the average down
        with implicit zeros.
    """
    weight_map = dict(zip(selected["drug_id"], selected["weight"]))
    series_list = []
    max_len = min_length
    for drug_id in selected["drug_id"]:
        s = analog_curves.get(str(drug_id))
        if s is None or s.empty:
            continue
        max_len = max(max_len, len(s))

    if not weight_map:
        return pd.Series(dtype=float)

    months = range(1, max_len + 1)
    aligned = {}
    for drug_id, weight in weight_map.items():
        s = analog_curves.get(str(drug_id))
        if s is None or s.empty:
            continue
        # reindex to start at month 1 (relative launch month), extend flat
        s = s.copy()
        s.index = range(1, len(s) + 1)
        s = s.reindex(months)
        s = s.ffill().fillna(0)
        aligned[drug_id] = s * weight

    if not aligned:
        return pd.Series(dtype=float)

    blended = sum(aligned.values())
    blended.name = "blended_analog_rx"
    return blended
