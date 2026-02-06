# Multi-Stage Reproductive Health Risk Prediction System

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

A data-driven system for predicting infertility risk based on symptoms and health indicators, designed for **women and couples as end-users**. The goal is to provide accessible reproductive health risk screening and next-step guidance using only symptoms and history that do not require hospital-level diagnostic equipment. The system offers personalized risk predictions and suggestions for what to do next (for example, lifestyle changes, monitoring symptoms, or seeking professional medical care).

**GitHub Repository:** [https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction](https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction)

## Project Description

This MVP focuses on **Stage 1: Infertility Risk Prediction** using symptom-based inputs that can be self-reported by women without any specialized medical tools. The system uses a scoring pipeline built from 705 patient records and 11 health indicators to predict infertility risk levels and provide clear, human-readable guidance on appropriate next steps (such as self-care advice, monitoring, or seeking professional care).

### Key Features

- **Symptom-Based Prediction**: Uses 10 self-reportable symptoms + age (no hospital diagnostics required)
- **Risk Scoring Pipeline**: Built from a curated dataset of 705 records with 11 indicators
- **RESTful API**: FastAPI backend with interactive Swagger UI documentation
- **High Recall**: Tuned to minimize false negatives (critical for healthcare)
- **Interpretable Results**: Returns risk levels, probabilities, and key drivers
- **Actionable Guidance for Users**: Returns risk levels plus suggested next steps (e.g., self-care guidance, monitoring, or talking to a health professional) rather than providing direct medical diagnoses.

### Input Features

1. Age (18-100 years)
2. Irregular Menstrual Cycles (Yes/No)
3. Hormonal Imbalances (Yes/No)
4. Pelvic Infections (Yes/No)
5. Endometriosis (Yes/No)
6. Uterine Fibroids (Yes/No)
7. Blocked Fallopian Tubes (Yes/No)
8. Obesity (Yes/No)
9. Smoking or Alcohol Use (Yes/No)
10. Age-Related Factors (Yes/No)
11. Male Factor (Yes/No)

### Validation Summary

- **Recall**: Tuned to catch at-risk patients
- **Evaluation**: Accuracy, Precision, Recall, F1-Score, ROC-AUC

## Project Structure

```
multi-stage-reproductive-health-risk-prediction/
├── backend/
│   ├── __init__.py
│   └── main.py                 # FastAPI application
├── data/
│   ├── processed/
│   │   ├── dhs_cleaned.csv
│   │   └── Female infertility.csv
│   └── raw/
├── docs/
│   └── diagrams/               # API designs and Swagger UI screenshots
├── ml/
│   ├── infertility_model.pkl   # Scoring artifact
│   ├── scaler.pkl              # Feature scaler
│   ├── feature_names.pkl       # Feature names
│   └── model_metadata.pkl      # Scoring metadata
├── notebooks/
│   └── infertility_risk_prediction.ipynb  # Pipeline notebook
├── requirements.txt            # Python dependencies
├── README.md
└── LICENSE
```

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction.git
   cd multi-stage-reproductive-health-risk-prediction
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import fastapi, sklearn, pandas; print('All dependencies installed successfully!')"
   ```

### Rebuilding Scoring Artifacts

1. **Open the Jupyter notebook**

   ```bash
   jupyter notebook notebooks/infertility_risk_prediction.ipynb
   ```

2. **Run all cells** to:
   - Load and explore the dataset
   - Visualize data distributions
   - Build and validate the scoring pipeline
   - Save artifacts to the `ml/` directory

### Running the API

1. **Start the FastAPI server**

   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - **Swagger UI (Interactive)**: http://localhost:8000/docs
   - **API Root**: http://localhost:8000
   - **Health Check**: http://localhost:8000/health
   - **Scoring Info**: http://localhost:8000/model/info

### Testing the API

**Using Swagger UI (Recommended)**

1. Open http://localhost:8000/docs
2. Click on `POST /predict/infertility`
3. Click "Try it out"
4. Enter patient data (or use the example)
5. Click "Execute"

**Using curl**

```bash
curl -X POST "http://localhost:8000/predict/infertility" \
  -H "Content-Type: application/json" \
  -d '{
    "Age": 32,
    "Irregular_Menstrual_Cycles": 1,
    "Hormonal_Imbalances": 1,
    "Pelvic_Infections": 0,
    "Endometriosis": 0,
    "Uterine_Fibroids": 0,
    "Blocked_Fallopian_Tubes": 0,
    "Obesity": 0,
    "Smoking_or_Alcohol": 0,
    "Age_Related_Factors": 0,
    "Male_Factor": 0
  }'
```

**Using Python requests**

```python
import requests

response = requests.post(
    "http://localhost:8000/predict/infertility",
    json={
        "Age": 32,
        "Irregular_Menstrual_Cycles": 1,
        "Hormonal_Imbalances": 1,
        "Pelvic_Infections": 0,
        "Endometriosis": 0,
        "Uterine_Fibroids": 0,
        "Blocked_Fallopian_Tubes": 0,
        "Obesity": 0,
        "Smoking_or_Alcohol": 0,
        "Age_Related_Factors": 0,
        "Male_Factor": 0
    }
)
print(response.json())
```

## API Endpoints

| Method | Endpoint               | Description                            |
| ------ | ---------------------- | -------------------------------------- |
| GET    | `/`                    | Root endpoint with API overview        |
| GET    | `/health`              | Health check for scoring status        |
| GET    | `/model/info`          | Scoring metadata and performance       |
| POST   | `/predict/infertility` | Predict infertility risk from symptoms |
| GET    | `/docs`                | Interactive Swagger UI documentation   |

## API Response Example

```json
{
  "prediction": "At Risk",
  "risk_level": "High Risk",
  "probability": 0.8542,
  "confidence": "High Confidence",
  "message": "Patient shows multiple risk factors for infertility. Medical consultation strongly recommended.",
  "feature_importance": {
    "Irregular_Menstrual_Cycles": 0.2341,
    "Hormonal_Imbalances": 0.1987,
    "Age": 0.1654,
    "Endometriosis": 0.1432,
    "Blocked_Fallopian_Tubes": 0.1234
  }
}
```

## Designs & Documentation

- **Prototype (Figma)**: https://www.figma.com/design/0fClURC8ZRryDMdNn2CpjZ/multi-stage?node-id=0-1&t=Em188Im0QQF3P6si-1
- **Swagger UI Screenshots**: See [docs/diagrams/](docs/diagrams/) folder
- **API Design Mockups**: Interactive documentation at `/docs` endpoint
- **Pipeline Details**: Documented in Jupyter notebook

## Deployment Plan

### Development

- Local testing with `uvicorn` development server
- Hot-reload enabled for rapid development

### Production Deployment Options

1. **Docker Deployment**

   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Environment Variables**
   - Set `PORT` for cloud platform requirements
   - Configure `CORS_ORIGINS` for frontend domain
   - Add `SECRET_KEY` for production security

## Video Demo

**Project Demo Video**: [Link to video](https://vimeo.com/1162615593/2d04bce8cf)

The video demonstration covers:

- Project overview and motivation
- Scoring pipeline development process
- API functionality demonstration
- Testing with Swagger UI
- Real-world use case scenarios

## Dataset

### Primary Dataset (Used in Current MVP)

**Source**: Female Infertility Dataset
**Size**: 705 patient records
**Features**: 11 health indicators (Age + 10 binary symptom features) + 1 target variable
**Class Distribution**: 82% at-risk, 18% no-risk

**Why this dataset?**
This dataset contains symptom-based features that can be self-reported or easily assessed without requiring hospital diagnostics. It aligns with the Stage 1 MVP goal of accessible infertility risk screening for women.

### Additional Dataset (Reserved for Future Stages)

**Source**: DHS (Demographic and Health Survey) Cleaned Data
**Size**: 2,775 records
**Location**: `data/processed/dhs_cleaned.csv`
**Purpose**: Contains demographic, socioeconomic, and healthcare access data from Rwanda

**Future Use Cases:**

- Stage 2: Pregnancy complications prediction with demographic context
- Stage 3: Maternal health risk assessment incorporating regional factors
- Enhanced model with demographic features (education, wealth index, healthcare access)
- Population-level risk stratification and resource allocation

## Technologies Used

- **Python 3.12**: Core programming language
- **FastAPI 0.115.0**: Modern web framework for APIs
- **pandas 2.3.3**: Data manipulation
- **uvicorn 0.32.0**: ASGI server
- **Jupyter Notebook**: Interactive development

## Future Enhancements

### Stage 2 & 3 Expansions

- [ ] Integrate DHS demographic data for enhanced predictions
- [ ] Stage 2: Pregnancy complications risk prediction
- [ ] Stage 3: Maternal health outcomes prediction
- [ ] Multi-stage scoring that combines clinical and demographic features
- [ ] Population-level risk mapping using DHS regional data

### Technical Improvements

- [ ] Frontend web application for women and couples
- [ ] Mobile app integration - later (iOS/Android)
- [ ] User authentication and session management
- [ ] Prediction history tracking and analytics dashboard
- [ ] Multi-language support (Kinyarwanda, English, French)
- [ ] Integration with electronic health records (EHR)
- [ ] Automated scoring refresh pipeline with new data
- [ ] A/B testing framework for scoring improvements

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Project Author**: Aimee Annabelle
**GitHub**: [@aimee-annabelle](https://github.com/aimee-annabelle)
**Repository**: [multi-stage-reproductive-health-risk-prediction](https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction)

## Acknowledgments

- Dataset providers for Female Infertility data
- Rwanda Ministry of Health for healthcare context
- ALU (African Leadership University) for academic support
- Community health workers and clinicians for domain expertise

---

**Note**: This is an MVP (Minimum Viable Product) for Stage 1 of a multi-stage reproductive health prediction system. The system is designed for women and couples as an educational and screening support tool. It should not replace professional medical diagnosis, and users should always consult qualified health professionals for medical decisions.
