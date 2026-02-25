"""Run postpartum v1 pipeline (10-11) and generate a consolidated markdown report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "evaluation" / "postpartum_v1"
REPORT_PATH = EVAL_ROOT / "POSTPARTUM_V1_REPORT.md"
BASE_METADATA_PATH = ROOT / "ml" / "postpartum_v1_metadata.pkl"

BASE_STAGE_FILES = [
    ROOT / "notebooks" / "10_postpartum_risk_training.py",
]
EVAL_STAGE = ROOT / "notebooks" / "11_postpartum_model_evaluation.py"


def run_stage(path: Path) -> None:
    print(f"\\n[RUN] {path.relative_to(ROOT)}")
    subprocess.run([sys.executable, str(path)], check=True, cwd=ROOT)


def fmt_metric(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_metadata() -> dict:
    if BASE_METADATA_PATH.exists():
        return joblib.load(BASE_METADATA_PATH)
    return {}


def generate_report() -> None:
    EVAL_ROOT.mkdir(parents=True, exist_ok=True)

    eval_summary_path = EVAL_ROOT / "model_evaluation" / "evaluation_summary.json"
    cls_report_path = EVAL_ROOT / "model_evaluation" / "classification_report.json"
    model_comparison_path = EVAL_ROOT / "training" / "model_comparison.csv"
    eval_summary = load_json(eval_summary_path)
    cls_report = load_json(cls_report_path)
    metadata = load_metadata()
    model_comparison_df = pd.read_csv(model_comparison_path) if model_comparison_path.exists() else None

    risk_precision = cls_report.get("1", {}).get("precision")
    risk_recall = cls_report.get("1", {}).get("recall")
    risk_f1 = cls_report.get("1", {}).get("f1-score")
    accuracy = cls_report.get("accuracy")
    low_risk_precision = cls_report.get("0", {}).get("precision")
    low_risk_recall = cls_report.get("0", {}).get("recall")

    cv_summary = eval_summary.get("cross_validation_summary", {})
    cv_f1 = cv_summary.get("test_f1", {}).get("mean")
    cv_recall = cv_summary.get("test_recall", {}).get("mean")
    cv_roc_auc = cv_summary.get("test_roc_auc", {}).get("mean")

    decision_threshold = eval_summary.get(
        "decision_threshold",
        eval_summary.get("threshold", metadata.get("decision_threshold", metadata.get("threshold"))),
    )
    emergency_threshold = eval_summary.get(
        "emergency_threshold",
        metadata.get("emergency_threshold"),
    )
    emergency_precision = eval_summary.get("emergency_precision")
    emergency_recall = eval_summary.get("emergency_recall")
    emergency_f1 = eval_summary.get("emergency_f1")

    lines: list[str] = []
    lines.append("# Postpartum V1 Model Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Selected model: {metadata.get('selected_model_name', 'N/A')}")
    lines.append(f"- Classification accuracy: {fmt_metric(accuracy)}")
    lines.append(
        f"- At-risk precision/recall/F1: {fmt_metric(risk_precision)} / {fmt_metric(risk_recall)} / {fmt_metric(risk_f1)}"
    )
    lines.append(
        f"- Low-risk precision/recall: {fmt_metric(low_risk_precision)} / {fmt_metric(low_risk_recall)}"
    )
    lines.append(
        f"- Test ROC-AUC: {fmt_metric(eval_summary.get('roc_auc_test'))}, PR-AUC: {fmt_metric(eval_summary.get('pr_auc_test'))}"
    )
    lines.append(f"- Decision threshold: {fmt_metric(decision_threshold)}")
    lines.append(f"- Emergency threshold: {fmt_metric(emergency_threshold)}")
    lines.append(
        f"- Emergency precision/recall/F1: {fmt_metric(emergency_precision)} / {fmt_metric(emergency_recall)} / {fmt_metric(emergency_f1)}"
    )
    lines.append("")

    lines.append("## Cross-Validation Summary")
    lines.append("")
    lines.append(f"- CV mean F1: {fmt_metric(cv_f1)}")
    lines.append(f"- CV mean recall: {fmt_metric(cv_recall)}")
    lines.append(f"- CV mean ROC-AUC: {fmt_metric(cv_roc_auc)}")
    lines.append("")

    lines.append("## Dataset and Training Metadata")
    lines.append("")
    if metadata:
        train_samples = metadata.get("training_samples", {})
        class_distribution = metadata.get("class_distribution", {}).get("full", {})

        lines.append(f"- Training rows: {train_samples.get('total', 'N/A')}")
        lines.append(
            f"- Train/Test split rows: {train_samples.get('train', 'N/A')} / {train_samples.get('test', 'N/A')}"
        )
        lines.append(
            f"- Class distribution (at-risk/low-risk): {class_distribution.get('at_risk', 'N/A')} / {class_distribution.get('low_risk', 'N/A')}"
        )
        lines.append(
            f"- Feature count: {len(metadata.get('features', {}).get('all_features', []))}"
        )
        lines.append(f"- Best hyperparameters: `{metadata.get('best_params', {})}`")
    else:
        lines.append("Model metadata not found.")
    lines.append("")

    lines.append("## Threshold Semantics")
    lines.append("")
    lines.append(
        "- Decision threshold is the recall-priority screening cutoff for predicting at-risk postpartum cases."
    )
    lines.append(
        "- Emergency threshold is stricter and intended for urgent escalation to emergency care guidance."
    )
    lines.append("")

    lines.append("## Clinical Interpretation")
    lines.append("")
    lines.append(
        "- This model is designed as a screening support tool, not a diagnostic replacement for clinical assessment."
    )
    lines.append(
        "- Decision-threshold positives should trigger timely mental health and maternal care review."
    )
    lines.append(
        "- Emergency-threshold positives indicate severe concern and should trigger immediate emergency referral."
    )
    lines.append(
        "- Lower scores should still be re-evaluated when symptoms worsen or new warning signs appear."
    )
    lines.append("")

    if model_comparison_df is not None and not model_comparison_df.empty:
        lines.append("## Model Comparison")
        lines.append("")
        lines.append("| Model | ROC-AUC | F1 | Precision | Recall | Decision Threshold |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for _, row in model_comparison_df.sort_values(
            ["f1", "roc_auc", "precision"], ascending=False
        ).iterrows():
            lines.append(
                f"| {row['model_name']} | {fmt_metric(row['roc_auc'])} | {fmt_metric(row['f1'])} | {fmt_metric(row['precision'])} | {fmt_metric(row['recall'])} | {fmt_metric(row['decision_threshold'])} |"
            )
        lines.append("")

    lines.append("## Key Artifacts")
    lines.append("")
    artifact_paths = [
        EVAL_ROOT / "model_evaluation" / "classification_report.json",
        EVAL_ROOT / "model_evaluation" / "evaluation_summary.json",
        EVAL_ROOT / "model_evaluation" / "cross_validation_scores.csv",
        EVAL_ROOT / "model_evaluation" / "confusion_matrix.png",
        EVAL_ROOT / "model_evaluation" / "roc_curve.png",
        EVAL_ROOT / "model_evaluation" / "precision_recall_curve.png",
        EVAL_ROOT / "model_evaluation" / "cross_validation_boxplot.png",
        EVAL_ROOT / "model_evaluation" / "feature_importance_model.png",
        EVAL_ROOT / "model_evaluation" / "feature_importance_model.csv",
        EVAL_ROOT / "model_evaluation" / "feature_importance_permutation.png",
        EVAL_ROOT / "model_evaluation" / "feature_importance_permutation.csv",
        EVAL_ROOT / "training" / "model_comparison.csv",
        EVAL_ROOT / "training" / "randomforest_random_search_results.csv",
        EVAL_ROOT / "training" / "logisticregression_random_search_results.csv",
        EVAL_ROOT / "training" / "gradientboosting_random_search_results.csv",
        EVAL_ROOT / "training" / "extratrees_random_search_results.csv",
    ]
    for p in artifact_paths:
        if p.exists():
            lines.append(f"- `{rel(p)}`")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\\n[OK] Report written to {rel(REPORT_PATH)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate markdown report from existing artifacts.",
    )
    args = parser.parse_args()

    if not args.report_only:
        stages = list(BASE_STAGE_FILES)
        stages.append(EVAL_STAGE)
        for stage in stages:
            run_stage(stage)

    generate_report()


if __name__ == "__main__":
    main()
