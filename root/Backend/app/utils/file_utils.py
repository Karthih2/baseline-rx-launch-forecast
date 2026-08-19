"""Small helpers for reading uploaded files into pandas / dicts safely.

Each "dataset" input (new_drug_dataset, analog_dataset) can bundle more than
one logical table (static features + Rx history), which have different
column schemas. Three upload formats are supported for these:

  - .csv  : only works when the dataset has exactly ONE required table
            (currently: new_drug_dataset, since new_drug_weekly_rx is
            optional). The whole CSV is treated as that one required table.
  - .json : a single JSON object keyed by the same logical table names used
            internally (e.g. {"features": {...}, "weekly_rx": [...]}) --
            values can be a single record (dict) or a list of records.
            Works for any dataset, including ones needing 2+ required
            tables (e.g. analog_dataset).
  - .zip  : a zip archive containing the original per-table CSV files
            (e.g. new_drug_features.csv, new_drug_weekly_rx.csv), matched by
            filename. Kept for backwards compatibility.
"""
import io
import json
import zipfile
from typing import Dict, List, Optional

import pandas as pd
from fastapi import UploadFile

from app.models.schemas import ValidationError


async def read_csv_upload(file: UploadFile) -> pd.DataFrame:
    """Read an UploadFile (CSV) into a DataFrame. Returns an empty
    DataFrame if no file was provided."""
    if file is None:
        return pd.DataFrame()
    raw = await file.read()
    if not raw:
        return pd.DataFrame()
    return pd.read_csv(io.BytesIO(raw))


async def read_json_upload(file: UploadFile) -> Dict:
    if file is None:
        return {}
    raw = await file.read()
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def parse_json_string(raw: str) -> Dict:
    if not raw:
        return {}
    return json.loads(raw)


def _find_member(zf: zipfile.ZipFile, expected_filename: str) -> Optional[str]:
    """Find a member inside the zip matching expected_filename, ignoring
    case and any folder prefix (e.g. 'data/new_drug_features.csv' still
    matches 'new_drug_features.csv')."""
    target = expected_filename.lower()
    for name in zf.namelist():
        base = name.rsplit("/", 1)[-1].lower()
        if base == target:
            return name
    return None


def _records_to_df(value, label: str, key: str) -> pd.DataFrame:
    """Convert a JSON value (dict = single row, list = many rows) into a
    DataFrame. Matches the same columns/schema as the equivalent CSV."""
    if value is None:
        return pd.DataFrame()
    if isinstance(value, dict):
        return pd.DataFrame([value])
    if isinstance(value, list):
        return pd.DataFrame(value)
    raise ValidationError(
        [f"{label}: '{key}' must be a JSON object (one row) or array of objects (many rows)"]
    )


def _read_zip_dataset(
    raw: bytes,
    required_files: Dict[str, str],
    optional_files: Dict[str, str],
    label: str,
) -> Dict[str, pd.DataFrame]:
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise ValidationError([f"{label}: uploaded .zip is not a valid archive"])

    result: Dict[str, pd.DataFrame] = {}
    missing = []

    for key, expected_filename in required_files.items():
        member = _find_member(zf, expected_filename)
        if member is None:
            missing.append(expected_filename)
            continue
        with zf.open(member) as fh:
            result[key] = pd.read_csv(fh)

    if missing:
        raise ValidationError([f"{label}: missing required file(s) inside zip: {missing}"])

    for key, expected_filename in optional_files.items():
        member = _find_member(zf, expected_filename)
        result[key] = pd.read_csv(zf.open(member)) if member else pd.DataFrame()

    return result


def _read_json_dataset(
    raw: bytes,
    required_keys: List[str],
    optional_keys: List[str],
    label: str,
) -> Dict[str, pd.DataFrame]:
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise ValidationError([f"{label}: invalid JSON ({e})"])

    if not isinstance(data, dict):
        raise ValidationError(
            [f"{label}: JSON must be an object keyed by {required_keys + optional_keys}"]
        )

    missing = [k for k in required_keys if k not in data or data[k] in (None, [], {})]
    if missing:
        raise ValidationError([f"{label}: missing required key(s) in JSON: {missing}"])

    result: Dict[str, pd.DataFrame] = {}
    for key in required_keys:
        result[key] = _records_to_df(data[key], label, key)
    for key in optional_keys:
        result[key] = _records_to_df(data.get(key), label, key)
    return result


async def read_dataset_upload(
    file: UploadFile,
    required_files: Dict[str, str],
    optional_files: Optional[Dict[str, str]] = None,
    label: str = "dataset",
) -> Dict[str, pd.DataFrame]:
    """Read a dataset input that may be .csv, .json, or .zip and return a
    dict keyed by the same logical keys as required_files/optional_files
    (e.g. {"features": df, "weekly_rx": df}).

    required_files / optional_files: {logical_key: expected_csv_filename}
    -- the filename is used for matching inside a .zip; for .csv/.json only
    the key names matter.
    """
    optional_files = optional_files or {}
    if file is None or not file.filename:
        raise ValidationError([f"{label}: no file uploaded"])

    raw = await file.read()
    if not raw:
        raise ValidationError([f"{label}: uploaded file is empty"])

    filename = file.filename.lower()
    required_keys = list(required_files.keys())
    optional_keys = list(optional_files.keys())

    if filename.endswith(".zip"):
        return _read_zip_dataset(raw, required_files, optional_files, label)

    if filename.endswith(".json"):
        return _read_json_dataset(raw, required_keys, optional_keys, label)

    if filename.endswith(".csv"):
        if len(required_keys) != 1:
            example_keys = required_keys + (optional_keys[:1] if optional_keys else [])
            example = ", ".join(f'"{k}": [...]' for k in example_keys)
            raise ValidationError(
                [
                    f"{label}: a single .csv only works when this dataset has exactly "
                    f"one required table, but it needs {required_keys} -- upload a "
                    f".json bundling those tables instead (e.g. {{{example}}}), "
                    "or a .zip."
                ]
            )
        result = {required_keys[0]: pd.read_csv(io.BytesIO(raw))}
        for key in optional_keys:
            result[key] = pd.DataFrame()
        return result

    raise ValidationError(
        [f"{label}: unsupported file type '{file.filename}' -- upload a .csv, .json, or .zip"]
    )
