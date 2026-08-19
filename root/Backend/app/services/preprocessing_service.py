"""
Preprocessing service.

Step 3 of the pipeline:
 - Clean the data (trim strings, coerce types, drop exact duplicate rows)
 - Convert the new drug's weekly Rx into monthly Rx
 - Prepare analog historical monthly Rx curves as aligned per-drug series
"""
from typing import Dict

import numpy as np
import pandas as pd

from app.config import WEEKS_PER_MONTH


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Generic cleaning: strip whitespace on string columns, drop exact
    duplicate rows, reset index. Safe to call on any of the pipeline's
    dataframes."""
    if df is None or df.empty:
        return df
    df = df.copy()
    df = df.drop_duplicates()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    df = df.reset_index(drop=True)
    return df


def weekly_to_monthly(weekly_df: pd.DataFrame) -> pd.DataFrame:
    """Convert a long-format weekly Rx dataframe (drug_id, week_number,
    rx_count) into monthly Rx using the standard 4.345 weeks/month pharma
    convention. Returns columns: drug_id, month_number, rx_count.
    """
    if weekly_df is None or weekly_df.empty:
        return pd.DataFrame(columns=["drug_id", "month_number", "rx_count"])

    df = weekly_df.copy()
    df["week_number"] = pd.to_numeric(df["week_number"], errors="coerce")
    df["rx_count"] = pd.to_numeric(df["rx_count"], errors="coerce").fillna(0)
    df = df.dropna(subset=["week_number"])
    df["month_number"] = np.ceil(df["week_number"] / WEEKS_PER_MONTH).astype(int)
    df.loc[df["month_number"] < 1, "month_number"] = 1

    monthly = (
        df.groupby(["drug_id", "month_number"], as_index=False)["rx_count"]
        .sum()
        .sort_values(["drug_id", "month_number"])
        .reset_index(drop=True)
    )
    return monthly


def prepare_analog_monthly_curves(monthly_df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Pivot the long-format analog monthly Rx table into a dict of
    {drug_id: pd.Series indexed by month_number (1..N), sorted}. Missing
    interior months are linearly interpolated; missing values are not
    extrapolated beyond each analog's own observed range.
    """
    curves: Dict[str, pd.Series] = {}
    if monthly_df is None or monthly_df.empty:
        return curves

    df = monthly_df.copy()
    df["month_number"] = pd.to_numeric(df["month_number"], errors="coerce").astype(int)
    df["rx_count"] = pd.to_numeric(df["rx_count"], errors="coerce").fillna(0)

    for drug_id, g in df.groupby("drug_id"):
        g = g.sort_values("month_number")
        full_index = range(int(g["month_number"].min()), int(g["month_number"].max()) + 1)
        series = pd.Series(g["rx_count"].values, index=g["month_number"].values)
        series = series.reindex(full_index)
        series = series.interpolate(method="linear").bfill().fillna(0)
        curves[str(drug_id)] = series

    return curves


def prepare_new_drug_actuals(monthly_df: pd.DataFrame, new_drug_id: str) -> pd.Series:
    """Extract the new drug's own (short) actual monthly Rx history, if any,
    as a pd.Series indexed by month_number starting at 1."""
    if monthly_df is None or monthly_df.empty:
        return pd.Series(dtype=float)
    sub = monthly_df[monthly_df["drug_id"].astype(str) == str(new_drug_id)]
    if sub.empty:
        return pd.Series(dtype=float)
    sub = sub.sort_values("month_number")
    return pd.Series(sub["rx_count"].values, index=sub["month_number"].values.astype(int))
