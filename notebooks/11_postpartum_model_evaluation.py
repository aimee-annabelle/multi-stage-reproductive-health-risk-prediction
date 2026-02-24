"""Stage 11: Final model evaluation for postpartum v1 with report-ready plots."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
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
DATASET_PATH = ROOT / "data" / "processed" / "postpartum_omv_cleaned.csv"
MODEL_DIR = ROOT / "ml"
OUTPUT_DIR = ROOT / "evaluation" / "postpartum_v1" / "model_evaluation"

TARGET_COLUMN = "ppd_risk"
TEST_SIZE = 0.25
RANDOM_STATE = 42


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_artifacts() -> tuple:
    base_model_path = MODEL_DIR / "postpartum_v1_model.pkl"
    base_metadata_path = MODEL_DIR / "postpartum_v1_metadata.pkl"
    model_path = base_model_path
    metadata_path = base_metadata_path

    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            "Missing postpartum artifacts. Run notebooks/10_postpartum_risk_training.py first."
        )

    model = joblib.load(model_path)
    metadata = joblib.load(metadata_path)
    return model, metadata, model_path, metadata_path


def load_dataset(feature_cols: list[str]) -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH)
    return df[feature_cols + [TARGET_COLUMN]].copy()


def plot_confusion_matrix(y_true: pd.Series, y_pred) -> None:
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title("Postpartum V1 Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=160)
    plt.close()


def plot_roc_curve(y_true: pd.Series, y_prob) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = roc_auc_score(y_true, y_prob)

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"ROC AUC = {roc_auc:.3f}", color="#e45756")
    plt.plot([0, 1], [0, 1], "k--", alpha=0.6)
    plt.title("Postpartum V1 ROC Curve")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "roc_curve.png", dpi=160)
    plt.close()

    return float(roc_auc)


def plot_pr_curve(y_true: pd.Series, y_prob) -> float:
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision)

    plt.figure(figsize=(7, 5))
    plt.plot(recall, precision, label=f"PR AUC = {pr_auc:.3f}", color="#4c78a8")
    plt.title("Postpartum V1 Precision-Recall Curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "precision_recall_curve.png", dpi=160)
    plt.close()

    return float(pr_auc)


def aggregate_feature_importance(model, all_features: list[str]) -> pd.Series:
    clf = model.named_steps["classifier"]
    pre = model.named_steps["preprocessor"]
    transformed = pre.get_feature_names_out()
    scores = clf.feature_importances_

    out = {f: 0.0 for f in all_features}
    for tname, score in zip(transformed, scores):
        clean = tname.replace("num__", "").replace("cat__", "")
        if clean.startswith("missingindicator_"):
            continue
        if clean in out:
            out[clean] += float(score)
        else:
            for f in all_features:
                if clean.startswith(f"{f}_"):
                    out[f] += float(score)
                    break

    return pd.Series(out).sort_values(ascending=False)


def plot_feature_importance(model, X_test: pd.DataFrame, y_test: pd.Series, all_features: list[str]) -> None:
    imp = aggregate_feature_importance(model, all_features)

    plt.figure(figsize=(10, 7))
    sns.barplot(x=imp.values[:20], y=imp.index[:20], color="#72b7b2")
    plt.title("Postpartum V1 Model Feature Importance (Top 20)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance_model.png", dpi=160)
    plt.close()

    imp.rename("importance").to_csv(OUTPUT_DIR / "feature_importance_model.csv", header=True)

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

    plt.figure(figsize=(10, 7))
    sns.barplot(x=perm_imp.values[:20], y=perm_imp.index[:20], color="#f58518")
    plt.title("Postpartum V1 Permutation Importance (Top 20)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_importance_permutation.png", dpi=160)
    plt.close()

    perm_imp.rename("importance").to_csv(OUTPUT_DIR / "feature_importance_permutation.csv", header=True)


def run_threshold_cv(model, X_train: pd.DataFrame, y_train: pd.Series, threshold: float) -> pd.DataFrame:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    rows = []

    for fold_idx, (tr_idx, va_idx) in enumerate(cv.split(X_train, y_train), start=1):
        X_tr = X_train.iloc[tr_idx]
        y_tr = y_train.iloc[tr_idx]
        X_va = X_train.iloc[va_idx]
        y_va = y_train.iloc[va_idx]

        m = clone(model)
        m.fit(X_tr, y_tr)
        prob = m.predict_proba(X_va)[:, 1]
        pred = (prob >= threshold).astype(int)

        rows.append(
            {
                "fold": fold_idx,
                "test_accuracy": float(accuracy_score(y_va, pred)),
                "test_precision": float(precision_score(y_va, pred, zero_division=0)),
                "test_recall": float(recall_score(y_va, pred, zero_division=0)),
                "test_f1": float(f1_score(y_va, pred, zero_division=0)),
                "test_roc_auc": float(roc_auc_score(y_va, prob)),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    ensure_dirs()

    model, metadata, model_path, metadata_path = load_artifacts()
    decision_threshold = float(metadata.get("decision_threshold", metadata.get("threshold", 0.5)))
    emergency_threshold = float(
        metadata.get("emergency_threshold", min(0.99, max(0.90, decision_threshold + 0.10)))
    )

    feature_cols = metadata.get("features", {}).get("all_features", [])
    if not feature_cols:
        raise ValueError("No feature list found in postpartum metadata.")

    df = load_dataset(feature_cols)
    X = df[feature_cols].copy()
    y = pd.to_numeric(df[TARGET_COLUMN], errors="coerce").fillna(0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= decision_threshold).astype(int)
    y_pred_emergency = (y_prob >= emergency_threshold).astype(int)

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    (OUTPUT_DIR / "classification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    plot_confusion_matrix(y_test, y_pred)
    roc_auc = plot_roc_curve(y_test, y_prob)
    pr_auc = plot_pr_curve(y_test, y_prob)
    plot_feature_importance(model, X_test, y_test, feature_cols)

    cv_df = run_threshold_cv(model, X_train, y_train, decision_threshold)
    cv_df.to_csv(OUTPUT_DIR / "cross_validation_scores.csv", index=False)

    metric_cols = ["test_accuracy", "test_precision", "test_recall", "test_f1", "test_roc_auc"]
    cv_summary = cv_df[metric_cols].agg(["mean", "std"]).to_dict()

    plt.figure(figsize=(9, 5))
    melted = cv_df[metric_cols].melt(var_name="metric", value_name="score")
    melted["metric"] = melted["metric"].str.replace("test_", "", regex=False)
    sns.boxplot(data=melted, x="metric", y="score", color="#54a24b")
    plt.ylim(0.0, 1.0)
    plt.title("Postpartum V1 Cross-Validation Metric Distribution")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cross_validation_boxplot.png", dpi=160)
    plt.close()

    summary = {
        "model_path": str(model_path),
        "metadata_path": str(metadata_path),
        "threshold": decision_threshold,
        "decision_threshold": decision_threshold,
        "emergency_threshold": emergency_threshold,
        "emergency_precision": float(precision_score(y_test, y_pred_emergency, zero_division=0)),
        "emergency_recall": float(recall_score(y_test, y_pred_emergency, zero_division=0)),
        "emergency_f1": float(f1_score(y_test, y_pred_emergency, zero_division=0)),
        "roc_auc_test": roc_auc,
        "pr_auc_test": pr_auc,
        "cross_validation_summary": cv_summary,
    }
    (OUTPUT_DIR / "evaluation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Postpartum v1 model evaluation complete. Outputs saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
