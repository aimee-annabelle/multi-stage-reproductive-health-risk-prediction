"""Stage 02: Feature engineering for infertility v1 model."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_selection import mutual_info_classif

sns.set_theme(style="whitegrid")

RAW_DATASET_PATH = Path("data/processed/Female infertility.csv")
ENGINEERED_DATASET_PATH = Path("data/processed/infertility_features_v1.csv")
OUTPUT_DIR = Path("evaluation/infertility_v1/feature_engineering")


FEATURE_COLUMNS = [
    "Age",
    "Irregular_Menstrual_Cycles",
    "Tubal_Issues_Risk",
    "Chronic_Pelvic_Pain",
    "Uterine_Issues_Risk",
    "History_Pelvic_Infections",
    "Hormonal_Symptoms",
    "Early_Menopause_Risk",
    "Autoimmune_History",
    "Reproductive_Surgery_History",
    "Unexplained_Difficulty_Conceiving",
]
TARGET_COLUMN = "Infertility_Prediction"


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Ovulation Disorders": "Irregular_Menstrual_Cycles",
        "Blocked Fallopian Tubes": "Tubal_Issues_Risk",
        "Endometriosis": "Chronic_Pelvic_Pain",
        "Uterine Abnormalities": "Uterine_Issues_Risk",
        "Pelvic Inflammatory Disease": "History_Pelvic_Infections",
        "Hormonal Imbalances": "Hormonal_Symptoms",
        "Premature Ovarian Insufficiency": "Early_Menopause_Risk",
        "Autoimmune Disorders": "Autoimmune_History",
        "Previous Reproductive Surgeries": "Reproductive_Surgery_History",
        "Unexplained Infertility": "Unexplained_Difficulty_Conceiving",
        "Infertility Prediction": "Infertility_Prediction",
    }
    return df.rename(columns=mapping)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = rename_columns(df)

    base_cols = ["Patient ID", *FEATURE_COLUMNS, TARGET_COLUMN]
    out = df[base_cols].copy()

    symptom_cols = [c for c in FEATURE_COLUMNS if c != "Age"]
    out["Symptom_Burden_Score"] = out[symptom_cols].sum(axis=1)
    out["Age_x_Symptom_Burden"] = out["Age"] * out["Symptom_Burden_Score"]

    return out


def compute_mutual_information(df: pd.DataFrame) -> pd.DataFrame:
    X = df[FEATURE_COLUMNS + ["Symptom_Burden_Score", "Age_x_Symptom_Burden"]]
    y = df[TARGET_COLUMN]

    mi = mutual_info_classif(X, y, random_state=42)
    mi_df = pd.DataFrame({"feature": X.columns, "mutual_information": mi}).sort_values(
        "mutual_information", ascending=False
    )
    return mi_df


def plot_mutual_information(mi_df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 6))
    sns.barplot(data=mi_df, x="mutual_information", y="feature", color="#f58518")
    plt.title("Feature Importance via Mutual Information")
    plt.xlabel("Mutual Information")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mutual_information.png", dpi=160)
    plt.close()


def main() -> None:
    ensure_dirs()

    raw_df = pd.read_csv(RAW_DATASET_PATH)
    featured_df = build_features(raw_df)

    featured_df.to_csv(ENGINEERED_DATASET_PATH, index=False)

    mi_df = compute_mutual_information(featured_df)
    mi_df.to_csv(OUTPUT_DIR / "mutual_information.csv", index=False)
    plot_mutual_information(mi_df)

    feature_summary = {
        "engineered_dataset_path": str(ENGINEERED_DATASET_PATH),
        "n_rows": int(featured_df.shape[0]),
        "n_columns": int(featured_df.shape[1]),
        "model_features": FEATURE_COLUMNS,
        "additional_engineered_features": ["Symptom_Burden_Score", "Age_x_Symptom_Burden"],
        "target": TARGET_COLUMN,
    }
    (OUTPUT_DIR / "feature_summary.json").write_text(
        json.dumps(feature_summary, indent=2), encoding="utf-8"
    )

    print("Feature engineering complete. Outputs saved to", OUTPUT_DIR)
    print("Engineered dataset saved to", ENGINEERED_DATASET_PATH)


if __name__ == "__main__":
    main()
