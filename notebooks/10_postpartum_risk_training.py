"""Postpartum v1 model training with multi-model selection.

This script trains and compares multiple classifiers with hyperparameter search,
then selects the best-performing model on holdout data under a recall-priority
screening policy.

Artifacts saved to ml/:
- postpartum_v1_model.pkl
- postpartum_v1_metadata.pkl
- postpartum_v1_feature_schema.pkl

Training reports saved to evaluation/postpartum_v1/training/:
- model_comparison.csv
- <model>_random_search_results.csv
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
TEST_SIZE = 0.25
RECALL_TARGET = 0.90

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "processed" / "postpartum_omv_cleaned.csv"
SCHEMA_PATH = ROOT / "data" / "processed" / "postpartum_omv_feature_schema.json"
ML_DIR = ROOT / "ml"
TRAINING_EVAL_DIR = ROOT / "evaluation" / "postpartum_v1" / "training"

TARGET_COLUMN = "ppd_risk"


def load_inputs() -> tuple[pd.DataFrame, Dict]:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Missing dataset: {DATASET_PATH}. Run notebooks/08_postpartum_omv_preprocessing.py first."
        )
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Missing schema: {SCHEMA_PATH}. Run notebooks/08_postpartum_omv_preprocessing.py first."
        )

    df = pd.read_csv(DATASET_PATH)
    schema_dict = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return df, schema_dict


def build_preprocessor(numeric_features: List[str], categorical_features: List[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=0.01)),
                    ]
                ),
                categorical_features,
            ),
        ],
        remainder="drop",
    )


def select_threshold_for_recall(y_true: pd.Series, y_prob: np.ndarray, recall_target: float) -> float:
    thresholds = np.linspace(0.95, 0.05, 181)
    valid_thresholds = []
    for threshold in thresholds:
        y_pred = (y_prob >= threshold).astype(int)
        rec = recall_score(y_true, y_pred, zero_division=0)
        if rec >= recall_target:
            valid_thresholds.append(threshold)

    if not valid_thresholds:
        return 0.5
    return float(max(valid_thresholds))


def select_emergency_threshold(
    y_true: pd.Series,
    y_prob: np.ndarray,
    decision_threshold: float,
    min_precision: float = 0.75,
    min_recall: float = 0.50,
) -> float:
    candidate_thresholds = np.linspace(0.99, max(decision_threshold, 0.05), 190)
    valid: list[float] = []
    for threshold in candidate_thresholds:
        y_pred = (y_prob >= threshold).astype(int)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        if precision >= min_precision and recall >= min_recall:
            valid.append(float(threshold))

    if valid:
        return float(max(valid))
    return float(min(0.99, max(decision_threshold + 0.10, decision_threshold)))


def compute_metrics(y_true: pd.Series, y_prob: np.ndarray, threshold: float) -> Dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
    }


def aggregate_feature_importance(
    model: Pipeline,
    numeric_features: List[str],
    categorical_features: List[str],
) -> Dict[str, float]:
    clf = model.named_steps["classifier"]
    pre = model.named_steps["preprocessor"]
    transformed = pre.get_feature_names_out()

    feature_scores: Dict[str, float] = {f: 0.0 for f in (numeric_features + categorical_features)}

    if hasattr(clf, "feature_importances_"):
        raw_scores = np.asarray(clf.feature_importances_)
    elif hasattr(clf, "coef_"):
        raw_scores = np.abs(np.asarray(clf.coef_)).ravel()
    else:
        return feature_scores

    for tname, score in zip(transformed, raw_scores):
        clean = tname.replace("num__", "").replace("cat__", "")
        if clean.startswith("missingindicator_"):
            continue

        matched = None
        if clean in feature_scores:
            matched = clean
        else:
            for c in categorical_features:
                if clean.startswith(f"{c}_"):
                    matched = c
                    break

        if matched is not None:
            feature_scores[matched] += float(score)

    return dict(sorted(feature_scores.items(), key=lambda x: x[1], reverse=True))


def build_model_specs() -> Dict[str, Dict]:
    return {
        "LogisticRegression": {
            "estimator": LogisticRegression(max_iter=3000, class_weight="balanced"),
            "params": {
                "classifier__C": [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
                "classifier__solver": ["liblinear", "lbfgs"],
            },
            "n_iter": 12,
        },
        "RandomForest": {
            "estimator": RandomForestClassifier(
                class_weight="balanced_subsample",
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
            "params": {
                "classifier__n_estimators": [200, 300, 400, 500, 700],
                "classifier__max_depth": [6, 8, 10, 12, None],
                "classifier__min_samples_split": [2, 4, 6, 8, 10],
                "classifier__min_samples_leaf": [1, 2, 3, 4, 5, 8],
                "classifier__max_features": ["sqrt", "log2", None],
            },
            "n_iter": 18,
        },
        "ExtraTrees": {
            "estimator": ExtraTreesClassifier(
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
            "params": {
                "classifier__n_estimators": [200, 300, 400, 500],
                "classifier__max_depth": [6, 8, 10, 12, None],
                "classifier__min_samples_split": [2, 4, 6, 8],
                "classifier__min_samples_leaf": [1, 2, 3, 4],
                "classifier__max_features": ["sqrt", "log2", None],
            },
            "n_iter": 16,
        },
        "GradientBoosting": {
            "estimator": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "params": {
                "classifier__n_estimators": [100, 150, 200, 250, 300],
                "classifier__learning_rate": [0.01, 0.03, 0.05, 0.1, 0.2],
                "classifier__max_depth": [2, 3, 4, 5],
                "classifier__min_samples_split": [2, 4, 6, 8],
                "classifier__min_samples_leaf": [1, 2, 3, 4],
            },
            "n_iter": 18,
        },
    }


def choose_best_model(rows: list[dict]) -> dict:
    # Primary objective: maximize F1 under recall-priority behavior.
    # Tie-breakers: ROC-AUC, then precision.
    ranked = sorted(
        rows,
        key=lambda r: (
            r["metrics"]["f1"],
            r["metrics"]["roc_auc"],
            r["metrics"]["precision"],
        ),
        reverse=True,
    )
    return ranked[0]


def main() -> None:
    df, schema = load_inputs()

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' missing in cleaned dataset.")

    all_features = [c for c in df.columns if c != TARGET_COLUMN]
    X = df[all_features].copy()
    y = pd.to_numeric(df[TARGET_COLUMN], errors="coerce").fillna(0).astype(int)

    numeric_features = [c for c in all_features if pd.api.types.is_numeric_dtype(X[c])]
    categorical_features = [c for c in all_features if c not in numeric_features]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    preprocessor = build_preprocessor(numeric_features, categorical_features)
    specs = build_model_specs()

    TRAINING_EVAL_DIR.mkdir(parents=True, exist_ok=True)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    candidate_rows: list[dict] = []

    for model_name, spec in specs.items():
        pipe = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", spec["estimator"]),
            ]
        )

        search = RandomizedSearchCV(
            estimator=pipe,
            param_distributions=spec["params"],
            n_iter=spec["n_iter"],
            scoring="roc_auc",
            cv=cv,
            random_state=RANDOM_STATE,
            n_jobs=1,
            verbose=0,
            refit=True,
        )
        search.fit(X_train, y_train)

        best_model = search.best_estimator_
        y_prob = best_model.predict_proba(X_test)[:, 1]
        decision_threshold = select_threshold_for_recall(y_test, y_prob, RECALL_TARGET)
        metrics = compute_metrics(y_test, y_prob, decision_threshold)

        # Save search table for this model.
        cv_results = pd.DataFrame(search.cv_results_)
        keep_cols = [
            "mean_test_score",
            "std_test_score",
            "rank_test_score",
        ] + [c for c in cv_results.columns if c.startswith("param_classifier__")]
        keep_cols = [c for c in keep_cols if c in cv_results.columns]
        cv_results[keep_cols].sort_values("rank_test_score").to_csv(
            TRAINING_EVAL_DIR / f"{model_name.lower()}_random_search_results.csv",
            index=False,
        )

        candidate_rows.append(
            {
                "model_name": model_name,
                "best_model": best_model,
                "best_params": search.best_params_,
                "best_cv_roc_auc": float(search.best_score_),
                "decision_threshold": float(decision_threshold),
                "metrics": metrics,
            }
        )

    best = choose_best_model(candidate_rows)
    best_model = best["best_model"]
    best_probs = best_model.predict_proba(X_test)[:, 1]
    decision_threshold = float(best["decision_threshold"])
    emergency_threshold = select_emergency_threshold(
        y_test,
        best_probs,
        decision_threshold=decision_threshold,
    )

    feature_importance = aggregate_feature_importance(
        best_model,
        numeric_features,
        categorical_features,
    )

    feature_schema = {
        "target": TARGET_COLUMN,
        "all_features": all_features,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "feature_groups": schema.get("feature_groups", {}),
    }

    comparison_rows = []
    for row in candidate_rows:
        comparison_rows.append(
            {
                "model_name": row["model_name"],
                "best_cv_roc_auc": row["best_cv_roc_auc"],
                "decision_threshold": row["decision_threshold"],
                **row["metrics"],
            }
        )
    comparison_df = pd.DataFrame(comparison_rows).sort_values(
        ["f1", "roc_auc", "precision"], ascending=False
    )
    comparison_df.to_csv(TRAINING_EVAL_DIR / "model_comparison.csv", index=False)

    metadata = {
        "model_version": "1.1.0",
        "training_date_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline_type": "single_branch_classifier_multi_model_selection",
        "target_name": TARGET_COLUMN,
        "label_mapping": {"low_risk": 0, "at_risk": 1},
        "recall_target": RECALL_TARGET,
        "threshold_selection_rule": "highest_threshold_meeting_recall_target",
        "emergency_threshold_rule": "highest_threshold_ge_decision_with_precision_gte_0.75_and_recall_gte_0.50_else_decision_plus_0.10",
        "selected_model_name": best["model_name"],
        "threshold": decision_threshold,
        "decision_threshold": decision_threshold,
        "emergency_threshold": emergency_threshold,
        "evaluation_metrics": best["metrics"],
        "best_params": best["best_params"],
        "best_cv_roc_auc": float(best["best_cv_roc_auc"]),
        "model_comparison": comparison_rows,
        "features": feature_schema,
        "feature_importance": feature_importance,
        "training_samples": {
            "total": int(len(df)),
            "train": int(len(X_train)),
            "test": int(len(X_test)),
        },
        "class_distribution": {
            "full": {"at_risk": int((y == 1).sum()), "low_risk": int((y == 0).sum())},
            "train": {"at_risk": int((y_train == 1).sum()), "low_risk": int((y_train == 0).sum())},
            "test": {"at_risk": int((y_test == 1).sum()), "low_risk": int((y_test == 0).sum())},
        },
        "source": {
            "clean_dataset": str(DATASET_PATH),
            "preprocessing_schema": str(SCHEMA_PATH),
        },
        "notes": [
            "Uses cleaned OMV-derived postpartum dataset with leakage exclusions.",
            "Multiple model families are tuned and compared; best holdout model is selected.",
            "Decision threshold is tuned for recall-priority screening.",
            "Emergency threshold is stricter and used for urgent escalation signaling.",
        ],
    }

    ML_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "model": ML_DIR / "postpartum_v1_model.pkl",
        "metadata": ML_DIR / "postpartum_v1_metadata.pkl",
        "feature_schema": ML_DIR / "postpartum_v1_feature_schema.pkl",
    }

    joblib.dump(best_model, paths["model"])
    joblib.dump(metadata, paths["metadata"])
    joblib.dump(feature_schema, paths["feature_schema"])

    print("=" * 80)
    print("Postpartum V1 Training Complete (Multi-Model Selection)")
    print("=" * 80)
    for k, p in paths.items():
        print(f"Saved {k}: {p}")
    print(f"Selected model: {best['model_name']}")
    print("Selected model metrics:")
    for k, v in best["metrics"].items():
        print(f"  {k}: {v:.4f}")
    print(f"  decision_threshold: {decision_threshold:.4f}")
    print(f"  emergency_threshold: {emergency_threshold:.4f}")


if __name__ == "__main__":
    main()
