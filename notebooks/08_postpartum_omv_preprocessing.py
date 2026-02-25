"""Prepare a leakage-safe postpartum dataset from a jamovi .omv file.

Outputs:
- data/processed/postpartum_omv_cleaned.csv
- data/processed/postpartum_omv_feature_schema.json
- data/processed/postpartum_omv_data_dictionary.csv
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import numpy as np
import pandas as pd

MISSING_SENTINEL = -2147483648

LEAKAGE_COLUMNS = {
    "Normal and Depressed",
    "Have you ever been diagnosed with postpartum depression",
}

TARGET_COLUMN_CANDIDATE = "Depressed and Normal"

PLACEHOLDER_TOKENS = {
    "",
    " ",
    "empty",
    "ex",
    "na",
    "n/a",
    "nan",
    "none",
    "null",
    "missing",
    "missed",
    "not interested to say",
}

YES_TOKENS = {
    "yes",
    "yes/نعم",
    "نعم/yes",
    "yes/ نعم",
    "yes / نعم",
}

NO_TOKENS = {
    "no",
    "no/لا",
    "لا/no",
    "no لا",
    "لا / no",
}


def _load_omv_parts(path: Path) -> tuple[dict[str, Any], dict[str, Any], np.ndarray]:
    with ZipFile(path) as zf:
        metadata = json.loads(zf.read("metadata.json").decode("utf-8"))
        xdata = json.loads(zf.read("xdata.json").decode("utf-8"))
        raw = np.frombuffer(zf.read("data.bin"), dtype="<i4")
    return metadata, xdata, raw


def _decode_label_map(xdata: dict[str, Any], field_name: str) -> dict[int, str] | None:
    entry = xdata.get(field_name)
    if not entry or "labels" not in entry:
        return None

    mapping: dict[int, str] = {}
    for row in entry["labels"]:
        # jamovi xdata label row shape: [code, short_label, long_label, is_missing]
        if len(row) < 2:
            continue
        code = int(row[0])
        label = str(row[1])
        mapping[code] = label
    return mapping or None


def _build_dataframe(metadata: dict[str, Any], xdata: dict[str, Any], raw: np.ndarray) -> pd.DataFrame:
    ds = metadata["dataSet"]
    row_count = int(ds["rowCount"])
    fields = ds["fields"]
    field_count = len(fields)

    total_cells = raw.size
    inferred_cols = total_cells // row_count
    matrix = raw.reshape(row_count, inferred_cols)

    # .omv contains extra hidden columns; the first N match data fields.
    matrix = matrix[:, :field_count].copy()

    frame = pd.DataFrame()

    for i, field in enumerate(fields):
        name = field["name"]
        col = matrix[:, i].astype(np.int64)
        col = np.where(col == MISSING_SENTINEL, np.nan, col)

        label_map = _decode_label_map(xdata, name)
        if label_map:
            series = pd.Series(col).map(label_map)
        else:
            # Keep numeric when no label map is provided.
            series = pd.to_numeric(pd.Series(col), errors="coerce")

        frame[name] = series

    return frame


def _normalize_string(value: Any) -> Any:
    if pd.isna(value):
        return np.nan
    if not isinstance(value, str):
        return value

    text = re.sub(r"\s+", " ", value.strip())
    lowered = text.lower()

    if lowered in PLACEHOLDER_TOKENS:
        return np.nan
    if lowered in YES_TOKENS:
        return "Yes"
    if lowered in NO_TOKENS:
        return "No"
    return text


def _normalize_object_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    out = df.copy()
    placeholder_ratio: dict[str, float] = {}

    obj_cols = [c for c in out.columns if out[c].dtype == "object"]
    for col in obj_cols:
        original = out[col].copy()
        out[col] = out[col].map(_normalize_string)

        before_missing = original.isna().mean()
        after_missing = out[col].isna().mean()
        placeholder_ratio[col] = max(0.0, float(after_missing - before_missing))

        # Convert numeric-like text columns to numeric if strongly parseable.
        probe = pd.to_numeric(out[col], errors="coerce")
        parse_rate = probe.notna().mean()
        if parse_rate >= 0.9 and probe.nunique(dropna=True) > 5:
            out[col] = probe

    return out, placeholder_ratio


def _is_transform_or_duplicate_column(col: str) -> bool:
    # Jamovi expands transformed and recoded helper columns with " - ..." suffix.
    return " - " in col


def _build_feature_group(col: str) -> str:
    name = col.lower()

    psych_keys = [
        "anxious",
        "worried",
        "panicky",
        "unhappy",
        "sad",
        "crying",
        "harming",
        "mental",
        "depression",
        "guilt",
        "sleep",
        "problems with husband",
        "family problems",
        "financial problems",
    ]
    clinical_keys = [
        "baby",
        "delivery",
        "premature",
        "nicu",
        "feeding",
        "pregnancy problem",
        "postnatal problems",
        "natal problems",
        "comorbid",
        "kgs gained",
        "interpregnancy",
        "children",
        "miscarriges",
        "miscarriages",
    ]

    if any(k in name for k in psych_keys):
        return "psychological"
    if any(k in name for k in clinical_keys):
        return "physiological_clinical"
    return "sociodemographic_context"


def prepare_postpartum_dataset(input_path: Path, output_dir: Path) -> dict[str, Any]:
    metadata, xdata, raw = _load_omv_parts(input_path)
    df = _build_dataframe(metadata, xdata, raw)

    base_cols = [c for c in df.columns if not _is_transform_or_duplicate_column(c)]
    df_base = df[base_cols].copy()

    if TARGET_COLUMN_CANDIDATE not in df_base.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN_CANDIDATE}' not found in .omv dataset")

    target_raw = df_base[TARGET_COLUMN_CANDIDATE].astype(str).str.strip().str.lower()
    target_map = {"0": 0, "1": 1, "normal": 0, "depressed": 1}
    df_base["ppd_risk"] = target_raw.map(target_map)

    # Drop rows with unknown target coding.
    df_base = df_base[df_base["ppd_risk"].isin([0, 1])].copy()
    df_base["ppd_risk"] = df_base["ppd_risk"].astype(int)

    # Exclude label-leakage fields from model features.
    drop_cols = set(LEAKAGE_COLUMNS) | {TARGET_COLUMN_CANDIDATE}
    feature_cols = [c for c in df_base.columns if c not in drop_cols and c != "ppd_risk"]

    # Normalize placeholders and inconsistent categorical tokens.
    normalized, placeholder_ratio = _normalize_object_columns(df_base[feature_cols + ["ppd_risk"]])

    feature_matrix = normalized[feature_cols].copy()

    # Drop post-treatment barrier columns for predictive training use-case.
    post_treatment_barrier_cols = [
        c
        for c in feature_matrix.columns
        if c.lower().startswith("if you don't received any support or treatment for postpartum depression")
    ]
    feature_matrix = feature_matrix.drop(columns=post_treatment_barrier_cols, errors="ignore")

    # Keep columns with enough usable signal.
    missing_ratio = feature_matrix.isna().mean()
    unique_counts = feature_matrix.nunique(dropna=True)
    high_placeholder_cols = [
        c for c, r in placeholder_ratio.items() if c in feature_matrix.columns and r > 0.45
    ]
    low_signal_cols = [c for c in feature_matrix.columns if unique_counts[c] <= 1]
    high_missing_cols = [c for c in feature_matrix.columns if missing_ratio[c] > 0.35]

    keep_features = [
        c
        for c in feature_matrix.columns
        if c not in set(high_missing_cols) | set(low_signal_cols) | set(high_placeholder_cols)
    ]

    clean = pd.concat(
        [feature_matrix[keep_features], normalized[["ppd_risk"]]],
        axis=1,
    ).copy()

    output_dir.mkdir(parents=True, exist_ok=True)
    clean_path = output_dir / "postpartum_omv_cleaned.csv"
    schema_path = output_dir / "postpartum_omv_feature_schema.json"
    dict_path = output_dir / "postpartum_omv_data_dictionary.csv"
    quality_path = output_dir / "postpartum_omv_quality_report.json"

    clean.to_csv(clean_path, index=False)

    feature_groups = {
        col: _build_feature_group(col) for col in keep_features
    }

    schema = {
        "source_file": str(input_path),
        "rows": int(clean.shape[0]),
        "columns": int(clean.shape[1]),
        "target_column": "ppd_risk",
        "target_distribution": clean["ppd_risk"].value_counts().to_dict(),
        "excluded_for_leakage": sorted(drop_cols),
        "excluded_for_post_treatment_or_noise": sorted(
            set(post_treatment_barrier_cols) | set(high_placeholder_cols) | set(high_missing_cols) | set(low_signal_cols)
        ),
        "features": keep_features,
        "feature_groups": feature_groups,
        "notes": [
            "Columns with ' - ' suffix were removed as transformed/duplicate jamovi helper fields.",
            "Target is derived from 'Depressed and Normal' (0/1).",
            "Placeholder-like values (e.g., empty/ex/na) were normalized to missing.",
            "Post-treatment barrier columns were excluded to avoid unstable signal.",
            "Columns exceeding 35% missingness were removed.",
        ],
    }
    schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    data_dict = pd.DataFrame(
        {
            "column": keep_features + ["ppd_risk"],
            "group": [feature_groups.get(c, "target") for c in keep_features] + ["target"],
            "dtype": [str(clean[c].dtype) for c in keep_features + ["ppd_risk"]],
            "missing_ratio": [float(clean[c].isna().mean()) for c in keep_features + ["ppd_risk"]],
        }
    )
    data_dict.to_csv(dict_path, index=False)

    quality = {
        "missing_ratio_top_20": clean[keep_features].isna().mean().sort_values(ascending=False).head(20).to_dict(),
        "placeholder_ratio_top_20": dict(
            sorted(placeholder_ratio.items(), key=lambda kv: kv[1], reverse=True)[:20]
        ),
        "removed_columns": {
            "post_treatment_barrier_cols": sorted(post_treatment_barrier_cols),
            "high_placeholder_cols": sorted(high_placeholder_cols),
            "high_missing_cols": sorted(high_missing_cols),
            "low_signal_cols": sorted(low_signal_cols),
        },
    }
    quality_path.write_text(json.dumps(quality, indent=2), encoding="utf-8")

    return {
        "clean_path": str(clean_path),
        "schema_path": str(schema_path),
        "dictionary_path": str(dict_path),
        "quality_report_path": str(quality_path),
        "rows": int(clean.shape[0]),
        "features": len(keep_features),
        "target_distribution": schema["target_distribution"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract and clean postpartum .omv dataset")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/raw/Post_Partum_Depression_dataset1.omv"),
        help="Path to .omv file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../data/processed"),
        help="Directory for cleaned outputs",
    )
    args = parser.parse_args()

    result = prepare_postpartum_dataset(args.input, args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
