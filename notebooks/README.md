# Notebooks - ML Pipeline

Jupyter notebooks for the complete machine learning workflow.

## Notebooks

1. **01_exploratory_data_analysis.py** - Data exploration and analysis
2. **02_feature_engineering.py** - Feature creation and selection
3. **03_data_preprocessing.py** - Data cleaning and preprocessing
4. **04_model_training.py** - Model training (baseline and advanced)
5. **05_hyperparameter_tuning.py** - Hyperparameter optimization
6. **06_model_evaluation.py** - Model evaluation and analysis

## Setup

```bash
# Install dependencies
pip install -r ../requirements.txt
pip install jupyter notebook ipykernel

# Add kernel
python -m ipykernel install --user --name=reproductive-health

# Run Jupyter
jupyter notebook
```

## Usage

Execute notebooks in sequential order (01-06). Each notebook builds on the previous ones.

Or run the full infertility v1 pipeline and auto-generate a consolidated report:

```bash
python notebooks/run_infertility_v1_pipeline.py
```

Useful flags:

```bash
# Skip hyperparameter tuning stage (faster)
python notebooks/run_infertility_v1_pipeline.py --skip-tuning

# Rebuild only the consolidated report from existing outputs
python notebooks/run_infertility_v1_pipeline.py --report-only
```

## Output

- Processed data → `../data/processed/`
- Trained models → `../ml/`
- Evaluation reports → `../evaluation/`
