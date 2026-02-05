# Multi-Stage Reproductive Health Risk Prediction System

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

A machine learning-powered system for predicting infertility risk based on symptoms and health indicators. This project aims to provide accessible reproductive health risk screening for community health workers in Rwanda, enabling early detection and intervention without requiring hospital-level diagnostic equipment.

**GitHub Repository:** [https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction](https://github.com/aimee-annabelle/multi-stage-reproductive-health-risk-prediction)

## Project Description

This MVP focuses on **Stage 1: Infertility Risk Prediction** using symptom-based inputs that can be collected by community health workers. The system uses machine learning models trained on 705 patient records with 11 health indicators to predict infertility risk levels.

### Key Features

- **Symptom-Based Prediction**: Uses 10 self-reportable symptoms + age (no hospital diagnostics required)
- **Machine Learning Models**: Logistic Regression and Random Forest with SMOTE balancing
- **RESTful API**: FastAPI backend with interactive Swagger UI documentation
- **High Recall**: Optimized to minimize false negatives (critical for healthcare)
- **Interpretable Results**: Returns risk levels, probabilities, and feature importance

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

### Model Performance

- **Best Model**: Random Forest (selected based on recall)
- **Recall**: Optimized to catch at-risk patients
- **Training**: SMOTE-balanced data to handle 82/18 class imbalance
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
│   ├── infertility_model.pkl   # Trained ML model
│   ├── scaler.pkl              # Feature scaler
│   ├── feature_names.pkl       # Feature names
│   └── model_metadata.pkl      # Model metadata
├── notebooks/
│   └── infertility_risk_prediction.ipynb  # ML pipeline notebook
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

### Training the Model

1. **Open the Jupyter notebook**

   ```bash
   jupyter notebook notebooks/infertility_risk_prediction.ipynb
   ```

2. **Run all cells** to:
   - Load and explore the dataset
   - Visualize data distributions
   - Train Logistic Regression and Random Forest models
   - Evaluate model performance
   - Save models to `ml/` directory

### Running the API

1. **Start the FastAPI server**

   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - **Swagger UI (Interactive)**: http://localhost:8000/docs
   - **API Root**: http://localhost:8000
   - **Health Check**: http://localhost:8000/health
   - **Model Info**: http://localhost:8000/model/info

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
| GET    | `/health`              | Health check for model status          |
| GET    | `/model/info`          | Model metadata and performance metrics |
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

- **Swagger UI Screenshots**: See [docs/diagrams/](docs/diagrams/) folder
- **API Design Mockups**: Interactive documentation at `/docs` endpoint
- **Model Architecture**: Detailed in Jupyter notebook

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

**Project Demo Video**: [Link to be added]

The video demonstration covers:

- Project overview and motivation
- ML model training process
- API functionality demonstration
- Testing with Swagger UI
- Real-world use case scenarios

## Dataset

### Primary Dataset (Used in Current MVP)

**Source**: Female Infertility Dataset
**Size**: 705 patient records
**Features**: 11 health indicators (Age + 10 binary symptom features) + 1 target variable
**Class Distribution**: 82% at-risk, 18% no-risk (balanced with SMOTE during training)

**Why this dataset?**
This dataset contains symptom-based features that can be self-reported or easily assessed by community health workers without requiring hospital diagnostics. It aligns perfectly with the Stage 1 MVP goal of accessible infertility risk screening.

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
- **scikit-learn 1.8.0**: Machine learning models
- **pandas 2.3.3**: Data manipulation
- **imbalanced-learn 0.12.4**: SMOTE for class balancing
- **uvicorn 0.32.0**: ASGI server
- **Jupyter Notebook**: Interactive development

## Future Enhancements

### Stage 2 & 3 Expansions

- [ ] Integrate DHS demographic data for enhanced predictions
- [ ] Stage 2: Pregnancy complications risk prediction
- [ ] Stage 3: Maternal health outcomes prediction
- [ ] Multi-stage ensemble models combining clinical and demographic features
- [ ] Population-level risk mapping using DHS regional data

### Technical Improvements

- [ ] Frontend web application for community health workers
- [ ] Mobile app integration - later (iOS/Android)
- [ ] User authentication and session management
- [ ] Prediction history tracking and analytics dashboard
- [ ] Multi-language support (Kinyarwanda, English, French)
- [ ] Integration with electronic health records (EHR)
- [ ] Automated model retraining pipeline with new data
- [ ] A/B testing framework for model improvements

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
- Community health workers for domain expertise

---

**Note**: This is an MVP (Minimum Viable Product) for Stage 1 of a multi-stage reproductive health prediction system. The system is designed for screening purposes and should not replace professional medical diagnosis.
