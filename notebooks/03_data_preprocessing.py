"""Stage 03: Data preprocessing for infertility v1 model."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sns.set_theme(style="whitegrid")

INPUT_DATASET = Path("data/processed/infertility_features_v1.csv")
OUTPUT_SPLIT_DIR = Path("data/processed/infertility_v1_splits")
EVAL_DIR = Path("evaluation/infertility_v1/preprocessing")
ML_DIR = Path("ml")

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
    OUTPUT_SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    ML_DIR.mkdir(parents=True, exist_ok=True)


def plot_class_distribution(y_train: pd.Series, y_test: pd.Series) -> None:
    train_counts = y_train.value_counts().sort_index()
    test_counts = y_test.value_counts().sort_index()

    labels = ["No Risk (0)", "At Risk (1)"]
    chart = pd.DataFrame(
        {
            "Train": train_counts.values,
            "Test": test_counts.values,
        },
        index=labels,
    )

    ax = chart.plot(kind="bar", figsize=(8, 5), color=["#4c78a8", "#e45756"])
    ax.set_title("Class Distribution in Train/Test Splits")
    ax.set_ylabel("Count")
    ax.set_xlabel("Class")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "train_test_class_distribution.png", dpi=160)
    plt.close()


def main() -> None:
    ensure_dirs()

    df = pd.read_csv(INPUT_DATASET)
    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    # Scale age to improve linear model stability while keeping binary variables unchanged.
    X_train_scaled["Age"] = scaler.fit_transform(X_train[["Age"]]).ravel()
    X_test_scaled["Age"] = scaler.transform(X_test[["Age"]]).ravel()

    pd.concat(
        [X_train_scaled.reset_index(drop=True), y_train.reset_index(drop=True)], axis=1
    ).to_csv(
        OUTPUT_SPLIT_DIR / "train_scaled.csv", index=False
    )
    pd.concat(
        [X_test_scaled.reset_index(drop=True), y_test.reset_index(drop=True)], axis=1
    ).to_csv(
        OUTPUT_SPLIT_DIR / "test_scaled.csv", index=False
    )

    pd.concat([X_train.reset_index(drop=True), y_train.reset_index(drop=True)], axis=1).to_csv(
        OUTPUT_SPLIT_DIR / "train_raw.csv", index=False
    )
    pd.concat([X_test.reset_index(drop=True), y_test.reset_index(drop=True)], axis=1).to_csv(
        OUTPUT_SPLIT_DIR / "test_raw.csv", index=False
    )

    joblib.dump(scaler, ML_DIR / "scaler.pkl")
    joblib.dump(FEATURE_COLUMNS, ML_DIR / "feature_names.pkl")

    preprocessing_summary = {
        "input_dataset": str(INPUT_DATASET),
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "test_size": 0.25,
        "random_state": 42,
        "target_distribution_train": y_train.value_counts().to_dict(),
        "target_distribution_test": y_test.value_counts().to_dict(),
        "scaled_columns": ["Age"],
        "feature_columns": FEATURE_COLUMNS,
    }
    (EVAL_DIR / "preprocessing_summary.json").write_text(
        json.dumps(preprocessing_summary, indent=2), encoding="utf-8"
    )

    plot_class_distribution(y_train, y_test)

    print("Preprocessing complete. Outputs saved to", OUTPUT_SPLIT_DIR)


if __name__ == "__main__":
    main()
