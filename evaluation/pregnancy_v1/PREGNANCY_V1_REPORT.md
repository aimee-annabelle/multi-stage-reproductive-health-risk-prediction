# Pregnancy V1 Model Report

Generated: 2026-02-24T10:32:52.076841+00:00

## Executive Summary

- Classification accuracy (threshold-based): 0.9625
- High-risk precision/recall/F1: 1.0000 / 0.9076 / 0.9515
- Test ROC-AUC: 0.9997, PR-AUC: 0.9996
- Decision threshold: 0.7550, emergency threshold: 0.9000

## Threshold Policy

- Prediction class uses the decision threshold selected for high-risk recall target.
- Emergency-care advice uses a stricter emergency threshold.

## Cross-Validation Summary

- CV mean F1: 0.9377
- CV mean recall: 0.8841
- CV mean ROC-AUC: 0.9981

## Dataset and Training Metadata

- Training rows (post-cleaning): 1169
- Train/Test split rows: 876 / 293
- Class distribution (high/low): 473 / 696
- Dropped rows (missing label / invalid label / duplicate): 18 / 0 / 18
- Feature count: 11

## Key Artifacts

- `evaluation/pregnancy_v1/model_evaluation/classification_report.json`
- `evaluation/pregnancy_v1/model_evaluation/evaluation_summary.json`
- `evaluation/pregnancy_v1/model_evaluation/cross_validation_scores.csv`
- `evaluation/pregnancy_v1/model_evaluation/confusion_matrix.png`
- `evaluation/pregnancy_v1/model_evaluation/roc_curve.png`
- `evaluation/pregnancy_v1/model_evaluation/precision_recall_curve.png`
- `evaluation/pregnancy_v1/model_evaluation/cross_validation_boxplot.png`
- `evaluation/pregnancy_v1/model_evaluation/feature_importance_model.png`
- `evaluation/pregnancy_v1/model_evaluation/feature_importance_model.csv`
- `evaluation/pregnancy_v1/model_evaluation/feature_importance_permutation.png`
- `evaluation/pregnancy_v1/model_evaluation/feature_importance_permutation.csv`

## Notes

- Cross-validation metrics are computed with threshold-based class predictions.
- This report is suitable for capstone documentation and appendix references.
