# Data

This directory holds the raw and processed datasets used for EveBloom model training and evaluation.

## Directory Layout

```text
data/
├── raw/
│   └── Post_Partum_Depression_dataset1.omv   # Original postpartum survey (JASP/OMV format)
├── processed/
│   ├── infertility_features_v1.csv           # Processed infertility feature set (v1 pipeline)
│   ├── dhs_cleaned.csv                       # Cleaned DHS survey data (infertility v2 fusion)
│   ├── Female infertility.csv                # Intermediate infertility dataset
│   ├── pregnancy-risk-dataset.csv            # Pregnancy risk dataset
│   ├── postpartum_omv_cleaned.csv            # Cleaned postpartum dataset (converted from OMV)
│   ├── postpartum_omv_data_dictionary.csv    # Column-level metadata for postpartum dataset
│   ├── postpartum_omv_feature_schema.json    # Feature group schema for postpartum model
│   ├── postpartum_omv_quality_report.json    # Data quality report generated during preprocessing
│   └── infertility_v1_splits/               # Train/test split files for infertility v1
└── dhs_data_cleaning.py                      # Script to clean raw DHS survey export
```

## Dataset Sources

### Infertility

The infertility model was trained on a combination of two datasets:

**1. Female Infertility — Kaggle**

- **Source:** [Female Infertility — Kaggle](https://www.kaggle.com/datasets/fida5073/female-infertility/data?select=Female+infertility.csv)
- **File:** `processed/Female infertility.csv` → feature-engineered to `processed/infertility_features_v1.csv`
- Used for the v1 pipeline (symptom-based modeling).

**2. Demographic and Health Surveys (DHS)**

- **Source:** [DHS Program](https://dhsprogram.com/) — requires free registration and approval at [dhsprogram.com/data](https://dhsprogram.com/data/new-user-registration.cfm)
- **Note:** Raw DHS exports are **not redistributed** in this repository due to DHS data use agreement restrictions.
- **Processing script:** `data/dhs_data_cleaning.py` cleans the raw DHS export to produce `processed/dhs_cleaned.csv`
- Used for the v2 fusion model (history-branch modeling).

### Pregnancy Risk

- **Source:** [Maternal Health and High Risk Pregnancy Dataset — Kaggle](https://www.kaggle.com/datasets/vmohammedraiyyan/maternal-health-and-high-risk-pregnancy-dataset)
- **File:** `processed/pregnancy-risk-dataset.csv`

### Postpartum Depression

- **Source:** [Predictors and Prevalence of Postpartum Depression — Kaggle](https://www.kaggle.com/datasets/abdallahabbas9/redictors-and-prevalence-of-postpartum-depression)
- **Raw file:** `raw/Post_Partum_Depression_dataset1.omv` (JASP/OMV format)
- **Preprocessing notebook:** `notebooks/08_postpartum_omv_preprocessing.py` converts the OMV file to `processed/postpartum_omv_cleaned.csv`.
- **Data dictionary:** `processed/postpartum_omv_data_dictionary.csv` documents each column's group, type, and missing rate.

## Reproducing Processed Files

If `data/processed/` files are missing, regenerate them with:

```bash
# Infertility
python data/dhs_data_cleaning.py
python notebooks/01_exploratory_data_analysis.py  # or the full pipeline
python notebooks/run_infertility_v1_pipeline.py

# Pregnancy (CSV is already processed; no extra step needed)

# Postpartum
python notebooks/08_postpartum_omv_preprocessing.py
```

## Notes

- `infertility_v1_splits/` contains train/test CSVs generated during the v1 pipeline run. These are reproducible from source data.
- The `postpartum_omv_feature_schema.json` defines which columns belong to which feature group and drives the postpartum preprocessing service.
- Do **not** commit raw DHS export files to this repository.
