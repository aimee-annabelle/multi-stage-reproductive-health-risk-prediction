"""Run infertility v1 pipeline (01-06) and generate a consolidated markdown report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "evaluation" / "infertility_v1"
REPORT_PATH = EVAL_ROOT / "INFERTILITY_V1_REPORT.md"

STAGE_FILES = [
    ROOT / "notebooks" / "01_exploratory_data_analysis.py",
    ROOT / "notebooks" / "02_feature_engineering.py",
    ROOT / "notebooks" / "03_data_preprocessing.py",
    ROOT / "notebooks" / "04_model_training.py",
    ROOT / "notebooks" / "05_hyperparameter_tuning.py",
    ROOT / "notebooks" / "06_model_evaluation.py",
]


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


def generate_report() -> None:
    EVAL_ROOT.mkdir(parents=True, exist_ok=True)

    baseline_path = EVAL_ROOT / "training" / "baseline_model_metrics.csv"
    tuning_path = EVAL_ROOT / "tuning" / "tuning_summary.json"
    eval_summary_path = EVAL_ROOT / "model_evaluation" / "evaluation_summary.json"
    cls_report_path = EVAL_ROOT / "model_evaluation" / "classification_report.json"
    best_model_path = EVAL_ROOT / "training" / "best_model_summary.json"

    baseline_df = pd.read_csv(baseline_path) if baseline_path.exists() else pd.DataFrame()
    tuning = load_json(tuning_path)
    eval_summary = load_json(eval_summary_path)
    cls_report = load_json(cls_report_path)
    best_model = load_json(best_model_path)

    top_model_line = "N/A"
    if not baseline_df.empty:
        best_row = baseline_df.sort_values("f1", ascending=False).iloc[0]
        top_model_line = (
            f"{best_row['model']} (F1={fmt_metric(best_row['f1'])}, "
            f"Recall={fmt_metric(best_row['recall'])}, ROC-AUC={fmt_metric(best_row['roc_auc'])})"
        )

    cv_summary = eval_summary.get("cross_validation_summary", {})
    test_f1_cv = cv_summary.get("test_f1", {}).get("mean")
    test_recall_cv = cv_summary.get("test_recall", {}).get("mean")
    test_roc_cv = cv_summary.get("test_roc_auc", {}).get("mean")

    accuracy = cls_report.get("accuracy")
    weighted_f1 = cls_report.get("weighted avg", {}).get("f1-score")
    weighted_precision = cls_report.get("weighted avg", {}).get("precision")
    weighted_recall = cls_report.get("weighted avg", {}).get("recall")

    lines: list[str] = []
    lines.append("# Infertility V1 Model Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Baseline best model: {top_model_line}")
    lines.append(
        f"- Tuned model test F1: {fmt_metric(tuning.get('tuned_test_f1'))}"
    )
    lines.append(
        f"- Final test ROC-AUC: {fmt_metric(eval_summary.get('roc_auc_test'))}, PR-AUC: {fmt_metric(eval_summary.get('pr_auc_test'))}"
    )
    lines.append(
        f"- Final classification accuracy: {fmt_metric(accuracy)}, weighted F1: {fmt_metric(weighted_f1)}"
    )
    lines.append("")

    lines.append("## Baseline Model Comparison")
    lines.append("")
    if not baseline_df.empty:
        try:
            lines.append(baseline_df.to_markdown(index=False))
        except Exception:
            lines.append(baseline_df.to_csv(index=False))
    else:
        lines.append("Baseline metrics not found.")
    lines.append("")

    lines.append("## Tuned Model Summary")
    lines.append("")
    lines.append(f"- Random search best CV F1: {fmt_metric(tuning.get('random_search_best_cv_f1'))}")
    lines.append(f"- Grid search best CV F1: {fmt_metric(tuning.get('grid_search_best_cv_f1'))}")
    lines.append(f"- Tuned test F1: {fmt_metric(tuning.get('tuned_test_f1'))}")
    lines.append(f"- Tuned params: `{tuning.get('grid_search_best_params', {})}`")
    lines.append("")

    lines.append("## Final Evaluation")
    lines.append("")
    lines.append(f"- Accuracy: {fmt_metric(accuracy)}")
    lines.append(f"- Weighted precision: {fmt_metric(weighted_precision)}")
    lines.append(f"- Weighted recall: {fmt_metric(weighted_recall)}")
    lines.append(f"- Weighted F1: {fmt_metric(weighted_f1)}")
    lines.append(f"- CV mean F1: {fmt_metric(test_f1_cv)}")
    lines.append(f"- CV mean recall: {fmt_metric(test_recall_cv)}")
    lines.append(f"- CV mean ROC-AUC: {fmt_metric(test_roc_cv)}")
    lines.append("")

    lines.append("## Key Artifacts")
    lines.append("")
    artifact_paths = [
        EVAL_ROOT / "eda" / "target_distribution.png",
        EVAL_ROOT / "eda" / "age_distribution_by_target.png",
        EVAL_ROOT / "eda" / "correlation_heatmap.png",
        EVAL_ROOT / "feature_engineering" / "mutual_information.png",
        EVAL_ROOT / "training" / "baseline_model_comparison.png",
        EVAL_ROOT / "tuning" / "grid_search_top_configs.png",
        EVAL_ROOT / "model_evaluation" / "confusion_matrix.png",
        EVAL_ROOT / "model_evaluation" / "roc_curve.png",
        EVAL_ROOT / "model_evaluation" / "precision_recall_curve.png",
        EVAL_ROOT / "model_evaluation" / "cross_validation_boxplot.png",
        EVAL_ROOT / "model_evaluation" / "feature_importance_model.png",
        EVAL_ROOT / "model_evaluation" / "feature_importance_permutation.png",
    ]
    for p in artifact_paths:
        if p.exists():
            lines.append(f"- `{rel(p)}`")
    lines.append("")

    lines.append("## Model Metadata")
    lines.append("")
    if best_model:
        lines.append(f"- Saved model name: {best_model.get('model_name', 'N/A')}")
        lines.append(f"- Training samples: {best_model.get('training_samples', 'N/A')}")
        lines.append(f"- Test samples: {best_model.get('test_samples', 'N/A')}")
        lines.append(f"- Feature count: {len(best_model.get('features', []))}")
    else:
        lines.append("No best model metadata found.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\\n[OK] Report written to {rel(REPORT_PATH)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-tuning",
        action="store_true",
        help="Skip stage 05 hyperparameter tuning.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate markdown report from existing artifacts.",
    )
    args = parser.parse_args()

    if not args.report_only:
        for stage in STAGE_FILES:
            if args.skip_tuning and stage.name.startswith("05_"):
                print(f"[SKIP] {stage.relative_to(ROOT)}")
                continue
            run_stage(stage)

    generate_report()


if __name__ == "__main__":
    main()
