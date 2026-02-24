"""Pregnancy v1 single-branch model training.

This script trains a binary classifier for pregnancy risk prediction:
- Target labels: High (1) vs Low (0)
- Model: RandomForest + median imputation
- Threshold policy: highest threshold that keeps high-risk recall >= 0.90

It writes artifacts to ../ml:
- pregnancy_v1_model.pkl
- pregnancy_v1_metadata.pkl
- pregnancy_v1_feature_schema.pkl
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


RANDOM_STATE = 42
TEST_SIZE = 0.25
RECALL_TARGET = 0.90
EMERGENCY_MIN_THRESHOLD = 0.90

LABEL_COLUMN = "risk_level"

ALL_FEATURES = [
    "age",
    "systolic_bp",
    "diastolic",
    "bs",
    "body_temp",
    "bmi",
    "previous_complications",
    "preexisting_diabetes",
    "gestational_diabetes",
    "mental_health",
    "heart_rate",
]
REQUIRED_FEATURES = ["age", "systolic_bp", "diastolic"]
OPTIONAL_FEATURES = [
    "bs",
    "body_temp",
    "bmi",
    "previous_complications",
    "preexisting_diabetes",
    "gestational_diabetes",
    "mental_health",
    "heart_rate",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _snake_case(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def load_dataset(path: Path) -> Tuple[pd.DataFrame, Dict[str, int]]:
    raw_df = pd.read_csv(path)
    raw_df = raw_df.rename(columns={column: _snake_case(column) for column in raw_df.columns})

    missing_label_rows = int(raw_df[LABEL_COLUMN].isna().sum())
    labeled_df = raw_df.dropna(subset=[LABEL_COLUMN]).copy()

    label_values = labeled_df[LABEL_COLUMN].astype(str).str.strip().str.lower()
    valid_label_mask = label_values.isin({"high", "low"})
    invalid_label_rows = int((~valid_label_mask).sum())
    labeled_df = labeled_df[valid_label_mask].copy()
    labeled_df[LABEL_COLUMN] = label_values[valid_label_mask]

    duplicate_rows = int(labeled_df.duplicated().sum())
    deduplicated_df = labeled_df.drop_duplicates().reset_index(drop=True)

    dropped_rows = {
        "missing_label_rows": missing_label_rows,
        "invalid_label_rows": invalid_label_rows,
        "duplicate_rows": duplicate_rows,
    }
    return deduplicated_df, dropped_rows


def build_pipeline(features: List[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        (
                            "imputer",
                            SimpleImputer(strategy="median", add_indicator=True),
                        )
                    ]
                ),
                features,
            )
        ],
        remainder="drop",
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=10,
        min_samples_leaf=3,
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )


def select_threshold_for_recall(
    y_true: pd.Series, y_prob: np.ndarray, recall_target: float
) -> float:
    thresholds = np.linspace(0.95, 0.05, 181)
    valid_thresholds = []
    for threshold in thresholds:
        y_pred = (y_prob >= threshold).astype(int)
        recall = recall_score(y_true, y_pred, zero_division=0)
        if recall >= recall_target:
            valid_thresholds.append(threshold)

    if not valid_thresholds:
        return 0.5

    return float(max(valid_thresholds))


def compute_metrics(
    y_true: pd.Series, y_prob: np.ndarray, threshold: float
) -> Dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
    }


def extract_feature_importance(model: Pipeline, features: List[str]) -> Dict[str, float]:
    rf = model.named_steps["classifier"]
    preprocessor = model.named_steps["preprocessor"]
    transformed_features = preprocessor.get_feature_names_out()
    importances = rf.feature_importances_

    score_map: Dict[str, float] = {feature: 0.0 for feature in features}

    for transformed_name, score in zip(transformed_features, importances):
        clean_name = transformed_name.replace("num__", "")
        if clean_name.startswith("missingindicator_"):
            continue
        if clean_name in score_map:
            score_map[clean_name] += float(score)

    return dict(sorted(score_map.items(), key=lambda item: item[1], reverse=True))


def resolve_emergency_threshold(decision_threshold: float) -> float:
    return float(min(0.99, max(EMERGENCY_MIN_THRESHOLD, decision_threshold + 0.10)))


def main() -> None:
    root = project_root()
    data_path = root / "data" / "processed" / "pregnancy-risk-dataset.csv"
    ml_dir = root / "ml"
    ml_dir.mkdir(parents=True, exist_ok=True)

    df, dropped_rows = load_dataset(data_path)
    X = df[ALL_FEATURES].copy()
    y = (df[LABEL_COLUMN] == "high").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = build_pipeline(ALL_FEATURES)
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    threshold = select_threshold_for_recall(y_test, y_prob, RECALL_TARGET)
    emergency_threshold = resolve_emergency_threshold(threshold)
    metrics = compute_metrics(y_test, y_prob, threshold)
    feature_importance = extract_feature_importance(model, ALL_FEATURES)

    feature_schema = {
        "required_features": REQUIRED_FEATURES,
        "optional_features": OPTIONAL_FEATURES,
        "all_features": ALL_FEATURES,
    }

    metadata = {
        "model_version": "1.0.0",
        "training_date_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline_type": "single_branch_classifier",
        "target_name": "pregnancy_high_risk",
        "label_mapping": {"low": 0, "high": 1},
        "recall_target": RECALL_TARGET,
        "threshold_selection_rule": "highest_threshold_meeting_recall_target",
        "threshold": float(threshold),
        "emergency_threshold": float(emergency_threshold),
        "evaluation_metrics": metrics,
        "features": feature_schema,
        "feature_importance": feature_importance,
        "training_samples": {
            "total_labeled_after_dedup": int(len(df)),
            "train": int(len(X_train)),
            "test": int(len(X_test)),
        },
        "class_distribution": {
            "full": {
                "high": int((y == 1).sum()),
                "low": int((y == 0).sum()),
            },
            "train": {
                "high": int((y_train == 1).sum()),
                "low": int((y_train == 0).sum()),
            },
            "test": {
                "high": int((y_test == 1).sum()),
                "low": int((y_test == 0).sum()),
            },
        },
        "dropped_rows": dropped_rows,
        "notes": [
            "Rows with missing labels are excluded from training.",
            "Exact duplicate rows are removed before train/test split.",
            "Optional inputs are supported at inference time via median imputation.",
            "Emergency threshold is stricter than referral threshold for immediate-care advice.",
        ],
    }

    artifact_paths = {
        "model": ml_dir / "pregnancy_v1_model.pkl",
        "metadata": ml_dir / "pregnancy_v1_metadata.pkl",
        "feature_schema": ml_dir / "pregnancy_v1_feature_schema.pkl",
    }

    joblib.dump(model, artifact_paths["model"])
    joblib.dump(metadata, artifact_paths["metadata"])
    joblib.dump(feature_schema, artifact_paths["feature_schema"])

    print("=" * 80)
    print("Pregnancy V1 Training Complete")
    print("=" * 80)
    print(f"Saved: {artifact_paths['model']}")
    print(f"Saved: {artifact_paths['metadata']}")
    print(f"Saved: {artifact_paths['feature_schema']}")
    print()
    print("Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    print(f"  threshold: {threshold:.4f}")
    print(f"  emergency_threshold: {emergency_threshold:.4f}")


if __name__ == "__main__":
    main()
