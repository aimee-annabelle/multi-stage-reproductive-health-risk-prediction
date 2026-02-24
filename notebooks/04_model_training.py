"""Stage 04: Baseline model training for infertility v1."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.tree import DecisionTreeClassifier

sns.set_theme(style="whitegrid")

SPLIT_DIR = Path("data/processed/infertility_v1_splits")
ML_DIR = Path("ml")
OUTPUT_DIR = Path("evaluation/infertility_v1/training")

TARGET_COLUMN = "Infertility_Prediction"


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ML_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
    }


def plot_model_comparison(results_df: pd.DataFrame) -> None:
    melted = results_df.melt(id_vars=["model"], var_name="metric", value_name="score")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=melted, x="metric", y="score", hue="model")
    plt.title("Baseline Model Comparison")
    plt.ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "baseline_model_comparison.png", dpi=160)
    plt.close()


def main() -> None:
    ensure_dirs()

    train_df = pd.read_csv(SPLIT_DIR / "train_scaled.csv")
    test_df = pd.read_csv(SPLIT_DIR / "test_scaled.csv")

    X_train = train_df.drop(columns=[TARGET_COLUMN])
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df.drop(columns=[TARGET_COLUMN])
    y_test = test_df[TARGET_COLUMN]

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "DecisionTree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=5, random_state=42),
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(random_state=42),
    }

    results = []
    fitted_models = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        results.append({"model": name, **metrics})
        fitted_models[name] = model

    results_df = pd.DataFrame(results).sort_values("f1", ascending=False)
    results_df.to_csv(OUTPUT_DIR / "baseline_model_metrics.csv", index=False)
    plot_model_comparison(results_df)

    best_name = results_df.iloc[0]["model"]
    best_metrics = results_df.iloc[0].drop("model").to_dict()
    best_model = fitted_models[best_name]

    joblib.dump(best_model, ML_DIR / "infertility_model.pkl")

    metadata = {
        "model_name": best_name,
        "accuracy": float(best_metrics["accuracy"]),
        "precision": float(best_metrics["precision"]),
        "recall": float(best_metrics["recall"]),
        "f1_score": float(best_metrics["f1"]),
        "roc_auc": float(best_metrics["roc_auc"]),
        "features": list(X_train.columns),
        "training_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "training_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
    }
    joblib.dump(metadata, ML_DIR / "model_metadata.pkl")

    (OUTPUT_DIR / "best_model_summary.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("Baseline training complete. Best model:", best_name)
    print("Metrics saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
