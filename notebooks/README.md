# Notebooks and Training Scripts

This directory contains the model-development scripts used in the project.

## Infertility V1 Pipeline Scripts

- `01_exploratory_data_analysis.py`
- `02_feature_engineering.py`
- `03_data_preprocessing.py`
- `04_model_training.py`
- `05_hyperparameter_tuning.py`
- `06_model_evaluation.py`

Run full infertility v1 pipeline + report:

```bash
python notebooks/run_infertility_v1_pipeline.py
```

Optional flags:

```bash
python notebooks/run_infertility_v1_pipeline.py --skip-tuning
python notebooks/run_infertility_v1_pipeline.py --report-only
```

Outputs are written under `evaluation/infertility_v1/` and model artifacts under `ml/`.

## Infertility V2 (Production Inference Artifacts)

- `07_infertility_fusion_training.py`

Run:

```bash
python notebooks/07_infertility_fusion_training.py
```

Creates:

- `ml/infertility_v2_symptom_model.pkl`
- `ml/infertility_v2_history_model.pkl`
- `ml/infertility_v2_metadata.pkl`
- `ml/infertility_v2_feature_schema.pkl`

## Pregnancy V1 Pipeline Scripts

- `08_pregnancy_risk_training.py`
- `09_pregnancy_model_evaluation.py`

Run full pregnancy v1 pipeline + report:

```bash
python notebooks/run_pregnancy_v1_pipeline.py
```

Report-only mode:

```bash
python notebooks/run_pregnancy_v1_pipeline.py --report-only
```

Creates:

- `ml/pregnancy_v1_model.pkl`
- `ml/pregnancy_v1_metadata.pkl`
- `ml/pregnancy_v1_feature_schema.pkl`
- `evaluation/pregnancy_v1/PREGNANCY_V1_REPORT.md`

## Environment Setup

```bash
pip install -r requirements.txt
```

Optional for notebook UI work:

```bash
pip install jupyter notebook ipykernel
jupyter notebook
```
