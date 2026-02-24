"""Run pregnancy v1 pipeline (08-09) and generate a consolidated markdown report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "evaluation" / "pregnancy_v1"
REPORT_PATH = EVAL_ROOT / "PREGNANCY_V1_REPORT.md"
MODEL_METADATA_PATH = ROOT / "ml" / "pregnancy_v1_metadata.pkl"

STAGE_FILES = [
    ROOT / "notebooks" / "08_pregnancy_risk_training.py",
    ROOT / "notebooks" / "09_pregnancy_model_evaluation.py",
]


def run_stage(path: Path) -> None:
    print(f"\n[RUN] {path.relative_to(ROOT)}")
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
    if not MODEL_METADATA_PATH.exists():
        return {}
    return joblib.load(MODEL_METADATA_PATH)


def generate_report() -> None:
    EVAL_ROOT.mkdir(parents=True, exist_ok=True)

    eval_summary_path = EVAL_ROOT / "model_evaluation" / "evaluation_summary.json"
    cls_report_path = EVAL_ROOT / "model_evaluation" / "classification_report.json"
    cv_scores_path = EVAL_ROOT / "model_evaluation" / "cross_validation_scores.csv"

    eval_summary = load_json(eval_summary_path)
    cls_report = load_json(cls_report_path)
    metadata = load_metadata()

    high_risk_precision = cls_report.get("1", {}).get("precision")
    high_risk_recall = cls_report.get("1", {}).get("recall")
    high_risk_f1 = cls_report.get("1", {}).get("f1-score")
    accuracy = cls_report.get("accuracy")

    cv_summary = eval_summary.get("cross_validation_summary", {})
    cv_f1 = cv_summary.get("test_f1", {}).get("mean")
    cv_recall = cv_summary.get("test_recall", {}).get("mean")
    cv_roc_auc = cv_summary.get("test_roc_auc", {}).get("mean")

    threshold = eval_summary.get("threshold", metadata.get("threshold"))
    emergency_threshold = eval_summary.get(
        "emergency_threshold", metadata.get("emergency_threshold")
    )

    lines: list[str] = []
    lines.append("# Pregnancy V1 Model Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(
        f"- Classification accuracy (threshold-based): {fmt_metric(accuracy)}"
    )
    lines.append(
        f"- High-risk precision/recall/F1: {fmt_metric(high_risk_precision)} / {fmt_metric(high_risk_recall)} / {fmt_metric(high_risk_f1)}"
    )
    lines.append(
        f"- Test ROC-AUC: {fmt_metric(eval_summary.get('roc_auc_test'))}, PR-AUC: {fmt_metric(eval_summary.get('pr_auc_test'))}"
    )
    lines.append(
        f"- Decision threshold: {fmt_metric(threshold)}, emergency threshold: {fmt_metric(emergency_threshold)}"
    )
    lines.append("")

    lines.append("## Threshold Policy")
    lines.append("")
    lines.append(
        "- Prediction class uses the decision threshold selected for high-risk recall target."
    )
    lines.append(
        "- Emergency-care advice uses a stricter emergency threshold."
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
        dropped_rows = metadata.get("dropped_rows", {})

        lines.append(
            f"- Training rows (post-cleaning): {train_samples.get('total_labeled_after_dedup', 'N/A')}"
        )
        lines.append(
            f"- Train/Test split rows: {train_samples.get('train', 'N/A')} / {train_samples.get('test', 'N/A')}"
        )
        lines.append(
            f"- Class distribution (high/low): {class_distribution.get('high', 'N/A')} / {class_distribution.get('low', 'N/A')}"
        )
        lines.append(
            f"- Dropped rows (missing label / invalid label / duplicate): {dropped_rows.get('missing_label_rows', 'N/A')} / {dropped_rows.get('invalid_label_rows', 'N/A')} / {dropped_rows.get('duplicate_rows', 'N/A')}"
        )
        lines.append(
            f"- Feature count: {len(metadata.get('features', {}).get('all_features', []))}"
        )
    else:
        lines.append("Model metadata not found.")
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
    ]
    for p in artifact_paths:
        if p.exists():
            lines.append(f"- `{rel(p)}`")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    if cv_scores_path.exists():
        lines.append("- Cross-validation metrics are computed with threshold-based class predictions.")
    lines.append(
        "- This report is suitable for capstone documentation and appendix references."
    )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[OK] Report written to {rel(REPORT_PATH)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate markdown report from existing artifacts.",
    )
    args = parser.parse_args()

    if not args.report_only:
        for stage in STAGE_FILES:
            run_stage(stage)

    generate_report()


if __name__ == "__main__":
    main()
