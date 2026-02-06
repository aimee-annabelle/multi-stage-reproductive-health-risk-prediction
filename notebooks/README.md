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

## Output

- Processed data → `../data/processed/`
- Trained models → `../ml/`
- Evaluation reports → `../evaluation/`
