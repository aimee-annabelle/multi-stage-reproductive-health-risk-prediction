# Notebooks and ML Training Pipelines

This directory contains the model-development backbone of EveBloom. It covers exploratory analysis, feature engineering, model training, tuning, evaluation, and report generation.

## ML Workflow Coverage

These scripts represent a complete student-friendly ML lifecycle:

1. Data understanding and quality checks
2. Feature engineering and preprocessing
3. Baseline model comparison
4. Hyperparameter tuning
5. Evaluation and visualization
6. Artifact persistence for production inference
7. Report generation for reproducibility

## Infertility Modeling

### V1 pipeline scripts
- `01_exploratory_data_analysis.py`
- `02_feature_engineering.py`
- `03_data_preprocessing.py`
- `04_model_training.py`
- `05_hyperparameter_tuning.py`
- `06_model_evaluation.py`

Run full infertility pipeline:

```bash
python notebooks/run_infertility_v1_pipeline.py
```

Optional modes:

```bash
python notebooks/run_infertility_v1_pipeline.py --skip-tuning
python notebooks/run_infertility_v1_pipeline.py --report-only
```

### V2 production artifacts (active runtime lineage)
- `07_infertility_fusion_training.py`

Run:

```bash
python notebooks/07_infertility_fusion_training.py
```

Outputs:
- `ml/infertility_v2_symptom_model.pkl`
- `ml/infertility_v2_history_model.pkl`
- `ml/infertility_v2_metadata.pkl`
- `ml/infertility_v2_feature_schema.pkl`

## Pregnancy Modeling

Scripts:
- `08_pregnancy_risk_training.py`
- `09_pregnancy_model_evaluation.py`

Run full pipeline:

```bash
python notebooks/run_pregnancy_v1_pipeline.py
```

## Postpartum Modeling

Scripts:
- `08_postpartum_omv_preprocessing.py`
- `10_postpartum_risk_training.py`
- `11_postpartum_model_evaluation.py`

Run full pipeline:

```bash
python notebooks/run_postpartum_v1_pipeline.py
```

## Outputs and Artifacts

- Runtime model artifacts in `ml/`
- Metrics, charts, and markdown reports in `evaluation/`

## Environment Setup

```bash
pip install -r requirements.txt
```

Optional notebook UI:

```bash
pip install jupyter notebook ipykernel
jupyter notebook
```
