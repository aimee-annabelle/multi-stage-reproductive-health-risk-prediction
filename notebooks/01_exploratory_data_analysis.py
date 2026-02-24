"""Stage 01: Exploratory Data Analysis for infertility v1 model."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")

DATASET_PATH = Path("data/processed/Female infertility.csv")
OUTPUT_DIR = Path("evaluation/infertility_v1/eda")


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


def save_dataset_summary(df: pd.DataFrame) -> None:
    summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "target_distribution": df["Infertility_Prediction"].value_counts().to_dict(),
        "missing_values": df.isna().sum().to_dict(),
        "age": {
            "min": float(df["Age"].min()),
            "max": float(df["Age"].max()),
            "mean": float(df["Age"].mean()),
            "median": float(df["Age"].median()),
        },
    }

    (OUTPUT_DIR / "dataset_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    df.describe(include="all").transpose().to_csv(OUTPUT_DIR / "descriptive_statistics.csv")
    df.isna().sum().reset_index(name="missing_count").rename(
        columns={"index": "feature"}
    ).to_csv(OUTPUT_DIR / "missing_values.csv", index=False)


def plot_target_distribution(df: pd.DataFrame) -> None:
    counts = df["Infertility_Prediction"].value_counts().sort_index()
    labels = ["No Risk (0)", "At Risk (1)"]

    plt.figure(figsize=(7, 5))
    ax = sns.barplot(x=labels, y=counts.values, palette=["#4c78a8", "#e45756"])
    ax.set_title("Infertility Target Distribution")
    ax.set_ylabel("Count")
    ax.set_xlabel("Class")

    for i, v in enumerate(counts.values):
        ax.text(i, v + 2, str(v), ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "target_distribution.png", dpi=160)
    plt.close()


def plot_age_distribution(df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    sns.histplot(
        data=df,
        x="Age",
        hue="Infertility_Prediction",
        bins=20,
        multiple="stack",
        palette={0: "#4c78a8", 1: "#e45756"},
    )
    plt.title("Age Distribution by Target")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "age_distribution_by_target.png", dpi=160)
    plt.close()


def plot_feature_prevalence(df: pd.DataFrame) -> None:
    symptom_cols = [
        c
        for c in df.columns
        if c
        not in {
            "Patient ID",
            "Age",
            "Infertility_Prediction",
        }
    ]

    prevalence = df[symptom_cols].mean().sort_values(ascending=False)

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=prevalence.values, y=prevalence.index, color="#72b7b2")
    ax.set_title("Feature Prevalence (Positive Rate)")
    ax.set_xlabel("Positive Rate")
    ax.set_ylabel("Feature")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_prevalence.png", dpi=160)
    plt.close()


def plot_correlation(df: pd.DataFrame) -> None:
    corr = df.drop(columns=["Patient ID"], errors="ignore").corr(numeric_only=True)

    plt.figure(figsize=(12, 9))
    sns.heatmap(corr, cmap="coolwarm", center=0.0, square=True)
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "correlation_heatmap.png", dpi=160)
    plt.close()

    target_corr = (
        corr["Infertility_Prediction"].drop("Infertility_Prediction").sort_values(ascending=False)
    )
    target_corr.rename("correlation_with_target").to_csv(
        OUTPUT_DIR / "feature_target_correlation.csv", header=True
    )


def main() -> None:
    ensure_dirs()

    df = pd.read_csv(DATASET_PATH)
    df = rename_columns(df)

    save_dataset_summary(df)
    plot_target_distribution(df)
    plot_age_distribution(df)
    plot_feature_prevalence(df)
    plot_correlation(df)

    print("EDA complete. Outputs saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
