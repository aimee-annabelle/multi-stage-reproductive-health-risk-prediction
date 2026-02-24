"""Infertility V2 dual-branch fusion model training.

This script trains:
1) Symptom branch model on hospital infertility data
2) History branch model on DHS infertility data
3) Fusion logic metadata for combined infertility probability

It writes artifacts to ../ml:
- infertility_v2_symptom_model.pkl
- infertility_v2_history_model.pkl
- infertility_v2_metadata.pkl
- infertility_v2_feature_schema.pkl
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

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
RECALL_TARGET = 0.90
TEST_SIZE = 0.25

FUSION_WEIGHTS = {
    "symptom": 0.4679,
    "history": 0.5321,
}

SYMPTOM_FEATURES = [
    "age",
    "irregular_menstrual_cycles",
    "chronic_pelvic_pain",
    "history_pelvic_infections",
    "hormonal_symptoms",
    "early_menopause_symptoms",
    "autoimmune_history",
    "reproductive_surgery_history",
]

HISTORY_FEATURES = [
    "age",
    "bmi",
    "smoked_last_12mo",
    "alcohol_last_12mo",
    "children_ever_born",
    "age_at_first_marriage",
    "months_since_first_cohabitation",
    "months_since_last_sex",
]


@dataclass
class BranchResult:
    model: Pipeline
    threshold: float
    metrics: Dict[str, float]
    feature_importance: Dict[str, float]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_hospital_data(data_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(data_dir / "Female infertility.csv")
    rename_map = {
        "Age": "age",
        "Ovulation Disorders": "irregular_menstrual_cycles",
        "Endometriosis": "chronic_pelvic_pain",
        "Pelvic Inflammatory Disease": "history_pelvic_infections",
        "Hormonal Imbalances": "hormonal_symptoms",
        "Premature Ovarian Insufficiency": "early_menopause_symptoms",
        "Autoimmune Disorders": "autoimmune_history",
        "Previous Reproductive Surgeries": "reproductive_surgery_history",
        "Infertility Prediction": "infertile",
    }
    keep_cols = list(rename_map.keys())
    df = df[keep_cols].rename(columns=rename_map)
    return df


def load_dhs_data(data_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(data_dir / "dhs_cleaned.csv")

    # DHS v445 BMI is often stored as BMI*100. Normalize to human-readable units
    # only when values are clearly in BMI*100 format, to match inference-time
    # preprocessing behavior.
    if "bmi" in df.columns:
        bmi = df["bmi"]
        df["bmi"] = np.where(bmi > 100, bmi / 100.0, bmi)

    return df[[*HISTORY_FEATURES, "infertile"]].copy()


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
                        ),
                    ]
                ),
                features,
            )
        ],
        remainder="drop",
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
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
    valid = []
    for threshold in thresholds:
        y_pred = (y_prob >= threshold).astype(int)
        rec = recall_score(y_true, y_pred)
        if rec >= recall_target:
            valid.append(threshold)

    if not valid:
        return 0.5

    # Most conservative threshold that still satisfies recall target.
    return float(max(valid))


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


def extract_base_feature_importance(model: Pipeline, features: List[str]) -> Dict[str, float]:
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


def train_branch(df: pd.DataFrame, features: List[str]) -> BranchResult:
    X = df[features]
    y = df["infertile"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = build_pipeline(features)
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    threshold = select_threshold_for_recall(y_test, y_prob, RECALL_TARGET)
    metrics = compute_metrics(y_test, y_prob, threshold)
    feature_importance = extract_base_feature_importance(model, features)

    return BranchResult(
        model=model,
        threshold=threshold,
        metrics=metrics,
        feature_importance=feature_importance,
    )


def build_feature_schema() -> Dict[str, List[str]]:
    required_features = ["age", "children_ever_born"]
    symptom_optional = [f for f in SYMPTOM_FEATURES if f != "age"]
    history_optional = [
        "bmi",
        "smoked_last_12mo",
        "alcohol_last_12mo",
        "age_at_first_marriage",
        "months_since_first_cohabitation",
        "months_since_last_sex",
    ]

    return {
        "required_features": required_features,
        "symptom_features": SYMPTOM_FEATURES,
        "history_features": HISTORY_FEATURES,
        "symptom_optional_features": symptom_optional,
        "history_optional_features": history_optional,
        "all_optional_features": symptom_optional + history_optional,
    }


def main() -> None:
    root = project_root()
    data_dir = root / "data" / "processed"
    ml_dir = root / "ml"
    ml_dir.mkdir(parents=True, exist_ok=True)

    hospital_df = load_hospital_data(data_dir)
    dhs_df = load_dhs_data(data_dir)

    symptom_result = train_branch(hospital_df, SYMPTOM_FEATURES)
    history_result = train_branch(dhs_df, HISTORY_FEATURES)

    fused_threshold = (
        FUSION_WEIGHTS["symptom"] * symptom_result.threshold
        + FUSION_WEIGHTS["history"] * history_result.threshold
    )

    schema = build_feature_schema()

    metadata = {
        "model_version": "2.0.0",
        "training_date_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline_type": "dual_branch_fusion",
        "target_name": "infertile",
        "recall_target": RECALL_TARGET,
        "threshold_selection_rule": "highest_threshold_meeting_recall_target",
        "fusion_weights": FUSION_WEIGHTS,
        "thresholds": {
            "symptom": float(symptom_result.threshold),
            "history": float(history_result.threshold),
            "fused": float(fused_threshold),
        },
        "features": schema,
        "branch_metrics": {
            "symptom": symptom_result.metrics,
            "history": history_result.metrics,
        },
        "feature_importance": {
            "symptom": symptom_result.feature_importance,
            "history": history_result.feature_importance,
        },
        "training_samples": {
            "symptom": int(len(hospital_df)),
            "history": int(len(dhs_df)),
        },
        "class_distribution": {
            "symptom": {
                "positive": int(hospital_df["infertile"].sum()),
                "negative": int((hospital_df["infertile"] == 0).sum()),
            },
            "history": {
                "positive": int(dhs_df["infertile"].sum()),
                "negative": int((dhs_df["infertile"] == 0).sum()),
            },
        },
        "notes": [
            "No row-level merge between hospital and DHS datasets.",
            "Primary vs secondary infertility classification is determined at inference time using children_ever_born.",
            "Maternal dataset excluded from infertility v2 training.",
        ],
    }

    artifact_paths = {
        "symptom_model": ml_dir / "infertility_v2_symptom_model.pkl",
        "history_model": ml_dir / "infertility_v2_history_model.pkl",
        "metadata": ml_dir / "infertility_v2_metadata.pkl",
        "feature_schema": ml_dir / "infertility_v2_feature_schema.pkl",
    }

    joblib.dump(symptom_result.model, artifact_paths["symptom_model"])
    joblib.dump(history_result.model, artifact_paths["history_model"])
    joblib.dump(metadata, artifact_paths["metadata"])
    joblib.dump(schema, artifact_paths["feature_schema"])

    print("=" * 80)
    print("Infertility V2 Training Complete")
    print("=" * 80)
    print(f"Saved: {artifact_paths['symptom_model']}")
    print(f"Saved: {artifact_paths['history_model']}")
    print(f"Saved: {artifact_paths['metadata']}")
    print(f"Saved: {artifact_paths['feature_schema']}")
    print()
    print("Symptom Branch Metrics:")
    for key, value in symptom_result.metrics.items():
        print(f"  {key}: {value:.4f}")
    print(f"  threshold: {symptom_result.threshold:.4f}")
    print()
    print("History Branch Metrics:")
    for key, value in history_result.metrics.items():
        print(f"  {key}: {value:.4f}")
    print(f"  threshold: {history_result.threshold:.4f}")
    print()
    print(f"Fusion Threshold: {fused_threshold:.4f}")


if __name__ == "__main__":
    main()
