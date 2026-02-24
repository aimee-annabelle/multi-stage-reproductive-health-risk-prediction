"""Stage 09: Final model evaluation for pregnancy v1 with report-ready plots."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, train_test_split

sns.set_theme(style="whitegrid")

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "processed" / "pregnancy-risk-dataset.csv"
MODEL_DIR = ROOT / "ml"
OUTPUT_DIR = ROOT / "evaluation" / "pregnancy_v1" / "model_evaluation"

LABEL_COLUMN = "risk_level"
FEATURE_COLUMNS = [
    "age",
    "systolic_bp",
    "diastolic",
    "bs",
    "body_temp",
    "bmi",
    "previous_complications",
    "preexisting_diabetes",
    "gestational_diabetes",
    "mental_health",
    "heart_rate",
]
TEST_SIZE = 0.25
RANDOM_STATE = 42


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_artifacts() -> tuple:
    model_path = MODEL_DIR / "pregnancy_v1_model.pkl"
    metadata_path = MODEL_DIR / "pregnancy_v1_metadata.pkl"

    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            "Missing pregnancy artifacts. Run notebooks/08_pregnancy_risk_training.py first."
        )

    model = joblib.load(model_path)
    metadata = joblib.load(metadata_path)
    return model, metadata, model_path, metadata_path


def _snake_case(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH)
    df = df.rename(columns={column: _snake_case(column) for column in df.columns})
    df = df.dropna(subset=[LABEL_COLUMN]).copy()

    labels = df[LABEL_COLUMN].astype(str).str.strip().str.lower()
    df = df[labels.isin({"high", "low"})].copy()
    df[LABEL_COLUMN] = labels[labels.isin({"high", "low"})]
    df = df.drop_duplicates().reset_index(drop=True)
    return df


def plot_confusion_matrix(y_true: pd.Series, y_pred: np.ndarray) -> None:
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title("Pregnancy V1 Confusion Matrix")
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
    plt.title("Pregnancy V1 ROC Curve")
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
    plt.title("Pregnancy V1 Precision-Recall Curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "precision_recall_curve.png", dpi=160)
    plt.close()

    return float(pr_auc)


def plot_feature_importance(model, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    classifier = model.named_steps["classifier"]
    preprocessor = model.named_steps["preprocessor"]
    transformed_features = preprocessor.get_feature_names_out()
    importances = classifier.feature_importances_

    feature_scores = {feature: 0.0 for feature in FEATURE_COLUMNS}
    for transformed_name, score in zip(transformed_features, importances):
        name = transformed_name.replace("num__", "")
        if name.startswith("missingindicator_"):
            continue
        if name in feature_scores:
            feature_scores[name] += float(score)

    feature_imp = pd.Series(feature_scores).sort_values(ascending=False)

    plt.figure(figsize=(9, 6))
    sns.barplot(x=feature_imp.values, y=feature_imp.index, color="#72b7b2")
    plt.title("Pregnancy V1 Model Feature Importance")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance_model.png", dpi=160)
    plt.close()

    feature_imp.rename("importance").to_csv(OUTPUT_DIR / "feature_importance_model.csv", header=True)

    perm = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=20,
        random_state=RANDOM_STATE,
        n_jobs=1,
        scoring="roc_auc",
    )
    perm_imp = pd.Series(perm.importances_mean, index=X_test.columns).sort_values(ascending=False)

    plt.figure(figsize=(9, 6))
    sns.barplot(x=perm_imp.values, y=perm_imp.index, color="#f58518")
    plt.title("Pregnancy V1 Permutation Importance (ROC-AUC)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance_permutation.png", dpi=160)
    plt.close()

    perm_imp.rename("importance").to_csv(OUTPUT_DIR / "feature_importance_permutation.csv", header=True)


def run_threshold_cv(
    model,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    threshold: float,
) -> pd.DataFrame:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    rows: list[dict] = []

    for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train), start=1):
        X_tr = X_train.iloc[train_idx]
        y_tr = y_train.iloc[train_idx]
        X_val = X_train.iloc[val_idx]
        y_val = y_train.iloc[val_idx]

        fold_model = clone(model)
        fold_model.fit(X_tr, y_tr)
        y_prob = fold_model.predict_proba(X_val)[:, 1]
        y_pred = (y_prob >= threshold).astype(int)

        rows.append(
            {
                "fold": fold_idx,
                "test_accuracy": float(accuracy_score(y_val, y_pred)),
                "test_precision": float(precision_score(y_val, y_pred, zero_division=0)),
                "test_recall": float(recall_score(y_val, y_pred, zero_division=0)),
                "test_f1": float(f1_score(y_val, y_pred, zero_division=0)),
                "test_roc_auc": float(roc_auc_score(y_val, y_prob)),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    ensure_dirs()

    model, metadata, model_path, metadata_path = load_artifacts()
    threshold = float(metadata.get("threshold", 0.5))
    emergency_threshold = float(metadata.get("emergency_threshold", max(0.9, threshold + 0.1)))

    df = load_dataset()
    X = df[FEATURE_COLUMNS].copy()
    y = (df[LABEL_COLUMN] == "high").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    (OUTPUT_DIR / "classification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    plot_confusion_matrix(y_test, y_pred)
    roc_auc = plot_roc_curve(y_test, y_prob)
    pr_auc = plot_pr_curve(y_test, y_prob)
    plot_feature_importance(model, X_test, y_test)

    cv_df = run_threshold_cv(model, X_train, y_train, threshold=threshold)
    cv_df.to_csv(OUTPUT_DIR / "cross_validation_scores.csv", index=False)

    metric_cols = ["test_accuracy", "test_precision", "test_recall", "test_f1", "test_roc_auc"]
    cv_summary = cv_df[metric_cols].agg(["mean", "std"]).to_dict()

    plt.figure(figsize=(9, 5))
    melted = cv_df[metric_cols].melt(var_name="metric", value_name="score")
    melted["metric"] = melted["metric"].str.replace("test_", "", regex=False)
    sns.boxplot(data=melted, x="metric", y="score", color="#54a24b")
    plt.ylim(0.0, 1.0)
    plt.title("Pregnancy V1 Cross-Validation Metric Distribution")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cross_validation_boxplot.png", dpi=160)
    plt.close()

    summary = {
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
        "threshold": threshold,
        "emergency_threshold": emergency_threshold,
        "roc_auc_test": roc_auc,
        "pr_auc_test": pr_auc,
        "cross_validation_summary": cv_summary,
    }
    (OUTPUT_DIR / "evaluation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Pregnancy v1 model evaluation complete. Outputs saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
