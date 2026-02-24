# Postpartum V1 Model Report

Generated: 2026-02-24T19:06:32.858232+00:00

## Executive Summary

- Selected model: RandomForest
- Classification accuracy: 0.7007
- At-risk precision/recall/F1: 0.5765 / 0.9074 / 0.7050
- Low-risk precision/recall: 0.9038 / 0.5663
- Test ROC-AUC: 0.8561, PR-AUC: 0.8015
- Decision threshold: 0.3300
- Emergency threshold: 0.7595
- Emergency precision/recall/F1: 0.7941 / 0.5000 / 0.6136

## Cross-Validation Summary

- CV mean F1: 0.7489
- CV mean recall: 0.9563
- CV mean ROC-AUC: 0.8689

## Dataset and Training Metadata

- Training rows: 545
- Train/Test split rows: 408 / 137
- Class distribution (at-risk/low-risk): 214 / 331
- Feature count: 49
- Best hyperparameters: `{'classifier__n_estimators': 200, 'classifier__min_samples_split': 4, 'classifier__min_samples_leaf': 8, 'classifier__max_features': 'sqrt', 'classifier__max_depth': 6}`

## Threshold Semantics

- Decision threshold is the recall-priority screening cutoff for predicting at-risk postpartum cases.
- Emergency threshold is stricter and intended for urgent escalation to emergency care guidance.

## Clinical Interpretation

- This model is designed as a screening support tool, not a diagnostic replacement for clinical assessment.
- Decision-threshold positives should trigger timely mental health and maternal care review.
- Emergency-threshold positives indicate severe concern and should trigger immediate emergency referral.
- Lower scores should still be re-evaluated when symptoms worsen or new warning signs appear.

## Model Comparison

| Model | ROC-AUC | F1 | Precision | Recall | Decision Threshold |
|---|---:|---:|---:|---:|---:|
| RandomForest | 0.8561 | 0.7050 | 0.5765 | 0.9074 | 0.3300 |
| LogisticRegression | 0.8452 | 0.6950 | 0.5632 | 0.9074 | 0.2100 |
| GradientBoosting | 0.8581 | 0.6901 | 0.5568 | 0.9074 | 0.2750 |
| ExtraTrees | 0.8474 | 0.6759 | 0.5385 | 0.9074 | 0.2700 |

## Key Artifacts

- `evaluation/postpartum_v1/model_evaluation/classification_report.json`
- `evaluation/postpartum_v1/model_evaluation/evaluation_summary.json`
- `evaluation/postpartum_v1/model_evaluation/cross_validation_scores.csv`
- `evaluation/postpartum_v1/model_evaluation/confusion_matrix.png`
- `evaluation/postpartum_v1/model_evaluation/roc_curve.png`
- `evaluation/postpartum_v1/model_evaluation/precision_recall_curve.png`
- `evaluation/postpartum_v1/model_evaluation/cross_validation_boxplot.png`
- `evaluation/postpartum_v1/model_evaluation/feature_importance_model.png`
- `evaluation/postpartum_v1/model_evaluation/feature_importance_model.csv`
- `evaluation/postpartum_v1/model_evaluation/feature_importance_permutation.png`
- `evaluation/postpartum_v1/model_evaluation/feature_importance_permutation.csv`
- `evaluation/postpartum_v1/training/model_comparison.csv`
- `evaluation/postpartum_v1/training/randomforest_random_search_results.csv`
- `evaluation/postpartum_v1/training/logisticregression_random_search_results.csv`
- `evaluation/postpartum_v1/training/gradientboosting_random_search_results.csv`
- `evaluation/postpartum_v1/training/extratrees_random_search_results.csv`
