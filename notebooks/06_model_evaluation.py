"""Stage 06: Final model evaluation for infertility v1 with report-ready plots."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    auc,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate

sns.set_theme(style="whitegrid")

SPLIT_DIR = Path("data/processed/infertility_v1_splits")
MODEL_DIR = Path("ml")
OUTPUT_DIR = Path("evaluation/infertility_v1/model_evaluation")
TARGET_COLUMN = "Infertility_Prediction"


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_best_model_path() -> Path:
    tuned = MODEL_DIR / "infertility_model_tuned.pkl"
    baseline = MODEL_DIR / "infertility_model.pkl"
    if tuned.exists():
        return tuned
    if baseline.exists():
        return baseline
    raise FileNotFoundError("No trained model found. Run notebooks/04_model_training.py first.")


def plot_confusion_matrix(y_true: pd.Series, y_pred: np.ndarray) -> None:
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=160)
    plt.close()


def plot_roc_curve(y_true: pd.Series, y_prob: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = roc_auc_score(y_true, y_prob)

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"ROC AUC = {roc_auc:.3f}", color="#e45756")
    plt.plot([0, 1], [0, 1], "k--", alpha=0.6)
    plt.title("ROC Curve")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "roc_curve.png", dpi=160)
    plt.close()

    return float(roc_auc)


def plot_pr_curve(y_true: pd.Series, y_prob: np.ndarray) -> float:
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision)

    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, label=f"PR AUC = {pr_auc:.3f}", color="#4c78a8")
    plt.title("Precision-Recall Curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "precision_recall_curve.png", dpi=160)
    plt.close()

    return float(pr_auc)


def plot_feature_importance(model, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    if not hasattr(model, "feature_importances_"):
        return

    feature_imp = pd.Series(model.feature_importances_, index=X_test.columns).sort_values(ascending=False)

    plt.figure(figsize=(9, 6))
    sns.barplot(x=feature_imp.values, y=feature_imp.index, color="#72b7b2")
    plt.title("Model Feature Importance")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance_model.png", dpi=160)
    plt.close()

    feature_imp.rename("importance").to_csv(OUTPUT_DIR / "feature_importance_model.csv", header=True)

    perm = permutation_importance(model, X_test, y_test, n_repeats=20, random_state=42, n_jobs=1)
    perm_imp = pd.Series(perm.importances_mean, index=X_test.columns).sort_values(ascending=False)

    plt.figure(figsize=(9, 6))
    sns.barplot(x=perm_imp.values, y=perm_imp.index, color="#f58518")
    plt.title("Permutation Importance (Test Set)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance_permutation.png", dpi=160)
    plt.close()

    perm_imp.rename("importance").to_csv(OUTPUT_DIR / "feature_importance_permutation.csv", header=True)


def main() -> None:
    ensure_dirs()

    train_df = pd.read_csv(SPLIT_DIR / "train_scaled.csv")
    test_df = pd.read_csv(SPLIT_DIR / "test_scaled.csv")

    X_train = train_df.drop(columns=[TARGET_COLUMN])
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df.drop(columns=[TARGET_COLUMN])
    y_test = test_df[TARGET_COLUMN]

    model_path = load_best_model_path()
    model = joblib.load(model_path)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    (OUTPUT_DIR / "classification_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    plot_confusion_matrix(y_test, y_pred)
    roc_auc = plot_roc_curve(y_test, y_prob)
    pr_auc = plot_pr_curve(y_test, y_prob)
    plot_feature_importance(model, X_test, y_test)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_validate(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring={
            "accuracy": "accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
            "roc_auc": "roc_auc",
        },
        n_jobs=1,
    )

    cv_df = pd.DataFrame(cv_scores)
    cv_df.to_csv(OUTPUT_DIR / "cross_validation_scores.csv", index=False)

    metric_cols = [
        "test_accuracy",
        "test_precision",
        "test_recall",
        "test_f1",
        "test_roc_auc",
    ]

    cv_summary = cv_df[metric_cols].agg(["mean", "std"]).to_dict()

    plt.figure(figsize=(9, 5))
    melted = cv_df[metric_cols].melt(var_name="metric", value_name="score")
    melted["metric"] = melted["metric"].str.replace("test_", "", regex=False)
    sns.boxplot(data=melted, x="metric", y="score", color="#54a24b")
    plt.ylim(0.0, 1.0)
    plt.title("Cross-Validation Metric Distribution")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cross_validation_boxplot.png", dpi=160)
    plt.close()

    summary = {
        "model_path": str(model_path),
        "roc_auc_test": roc_auc,
        "pr_auc_test": pr_auc,
        "cross_validation_summary": cv_summary,
    }
    (OUTPUT_DIR / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("Model evaluation complete. Outputs saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
