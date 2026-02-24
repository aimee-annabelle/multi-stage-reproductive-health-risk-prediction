# Infertility V1 Model Report

Generated: 2026-02-24T09:03:12.630426+00:00

## Executive Summary

- Baseline best model: GradientBoosting (F1=0.9662, Recall=0.9862, ROC-AUC=0.9744)
- Tuned model test F1: 0.9568
- Final test ROC-AUC: 0.9662, PR-AUC: 0.9924
- Final classification accuracy: 0.9266, weighted F1: 0.9203

## Baseline Model Comparison

model,accuracy,precision,recall,f1,roc_auc
GradientBoosting,0.943502824858757,0.9470198675496688,0.986206896551724,0.9662162162162162,0.974353448275862
DecisionTree,0.9265536723163842,0.9342105263157896,0.9793103448275862,0.9562289562289562,0.9165948275862068
LogisticRegression,0.9209039548022598,0.9281045751633988,0.9793103448275862,0.953020134228188,0.9596982758620688
RandomForest,0.8983050847457628,0.9319727891156464,0.9448275862068966,0.9383561643835616,0.9648706896551724


## Tuned Model Summary

- Random search best CV F1: 0.9417
- Grid search best CV F1: 0.9429
- Tuned test F1: 0.9568
- Tuned params: `{'max_depth': 10, 'max_features': 'sqrt', 'min_samples_leaf': 1, 'min_samples_split': 2, 'n_estimators': 400}`

## Final Evaluation

- Accuracy: 0.9266
- Weighted precision: 0.9284
- Weighted recall: 0.9266
- Weighted F1: 0.9203
- CV mean F1: 0.9429
- CV mean recall: 0.9678
- CV mean ROC-AUC: 0.9221

## Key Artifacts

- `evaluation/infertility_v1/eda/target_distribution.png`
- `evaluation/infertility_v1/eda/age_distribution_by_target.png`
- `evaluation/infertility_v1/eda/correlation_heatmap.png`
- `evaluation/infertility_v1/feature_engineering/mutual_information.png`
- `evaluation/infertility_v1/training/baseline_model_comparison.png`
- `evaluation/infertility_v1/tuning/grid_search_top_configs.png`
- `evaluation/infertility_v1/model_evaluation/confusion_matrix.png`
- `evaluation/infertility_v1/model_evaluation/roc_curve.png`
- `evaluation/infertility_v1/model_evaluation/precision_recall_curve.png`
- `evaluation/infertility_v1/model_evaluation/cross_validation_boxplot.png`
- `evaluation/infertility_v1/model_evaluation/feature_importance_model.png`
- `evaluation/infertility_v1/model_evaluation/feature_importance_permutation.png`

## Model Metadata

- Saved model name: GradientBoosting
- Training samples: 528
- Test samples: 177
- Feature count: 11
