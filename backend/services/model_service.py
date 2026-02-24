from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import joblib


_ARTIFACT_CACHE: Dict[str, Any] | None = None
_PREGNANCY_ARTIFACT_CACHE: Dict[str, Any] | None = None


def _model_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "ml"


def _artifact_paths() -> Dict[str, Path]:
    model_dir = _model_dir()
    return {
        "symptom_model": model_dir / "infertility_v2_symptom_model.pkl",
        "history_model": model_dir / "infertility_v2_history_model.pkl",
        "metadata": model_dir / "infertility_v2_metadata.pkl",
        "feature_schema": model_dir / "infertility_v2_feature_schema.pkl",
    }


def _pregnancy_artifact_paths() -> Dict[str, Path]:
    model_dir = _model_dir()
    return {
        "model": model_dir / "pregnancy_v1_model.pkl",
        "metadata": model_dir / "pregnancy_v1_metadata.pkl",
        "feature_schema": model_dir / "pregnancy_v1_feature_schema.pkl",
    }


def _resolve_pregnancy_emergency_threshold(
    decision_threshold: float,
    metadata: Dict[str, Any],
) -> float:
    stored = metadata.get("emergency_threshold")
    if stored is not None:
        return float(stored)

    return float(min(0.99, max(0.90, decision_threshold + 0.10)))


def load_v2_artifacts(force_reload: bool = False) -> Dict[str, Any]:
    global _ARTIFACT_CACHE

    if _ARTIFACT_CACHE is not None and not force_reload:
        return _ARTIFACT_CACHE

    paths = _artifact_paths()
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        missing_names = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing infertility v2 artifacts: {missing_names}. "
            "Run notebooks/07_infertility_fusion_training.py first."
        )

    symptom_model = joblib.load(paths["symptom_model"])
    history_model = joblib.load(paths["history_model"])
    metadata = joblib.load(paths["metadata"])
    feature_schema = joblib.load(paths["feature_schema"])

    _ARTIFACT_CACHE = {
        "symptom_model": symptom_model,
        "history_model": history_model,
        "metadata": metadata,
        "feature_schema": feature_schema,
        "paths": {name: str(path) for name, path in paths.items()},
    }

    return _ARTIFACT_CACHE


def load_pregnancy_artifacts(force_reload: bool = False) -> Dict[str, Any]:
    global _PREGNANCY_ARTIFACT_CACHE

    if _PREGNANCY_ARTIFACT_CACHE is not None and not force_reload:
        return _PREGNANCY_ARTIFACT_CACHE

    paths = _pregnancy_artifact_paths()
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        missing_names = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing pregnancy v1 artifacts: {missing_names}. "
            "Run notebooks/08_pregnancy_risk_training.py first."
        )

    model = joblib.load(paths["model"])
    metadata = joblib.load(paths["metadata"])
    feature_schema = joblib.load(paths["feature_schema"])

    _PREGNANCY_ARTIFACT_CACHE = {
        "model": model,
        "metadata": metadata,
        "feature_schema": feature_schema,
        "paths": {name: str(path) for name, path in paths.items()},
    }

    return _PREGNANCY_ARTIFACT_CACHE


def get_v2_artifacts() -> Dict[str, Any]:
    return load_v2_artifacts(force_reload=False)


def get_pregnancy_artifacts() -> Dict[str, Any]:
    return load_pregnancy_artifacts(force_reload=False)


def v2_artifacts_available() -> bool:
    if _ARTIFACT_CACHE is not None:
        return True

    paths = _artifact_paths()
    return all(path.exists() for path in paths.values())


def pregnancy_artifacts_available() -> bool:
    if _PREGNANCY_ARTIFACT_CACHE is not None:
        return True

    paths = _pregnancy_artifact_paths()
    return all(path.exists() for path in paths.values())


def get_v2_model_info() -> Dict[str, Any]:
    artifacts = get_v2_artifacts()
    metadata = artifacts["metadata"]

    return {
        "model_version": metadata.get("model_version", "unknown"),
        "pipeline_type": metadata.get("pipeline_type", "dual_branch_fusion"),
        "target_name": metadata.get("target_name", "infertile"),
        "training_date_utc": metadata.get("training_date_utc"),
        "recall_target": metadata.get("recall_target"),
        "thresholds": metadata.get("thresholds", {}),
        "fusion_weights": metadata.get("fusion_weights", {}),
        "branch_metrics": metadata.get("branch_metrics", {}),
        "features": metadata.get("features", {}),
        "training_samples": metadata.get("training_samples", {}),
        "class_distribution": metadata.get("class_distribution", {}),
        "notes": metadata.get("notes", []),
    }


def get_pregnancy_model_info() -> Dict[str, Any]:
    artifacts = get_pregnancy_artifacts()
    metadata = artifacts["metadata"]
    decision_threshold = float(metadata.get("threshold", 0.5))
    emergency_threshold = _resolve_pregnancy_emergency_threshold(
        decision_threshold=decision_threshold,
        metadata=metadata,
    )

    return {
        "model_version": metadata.get("model_version", "unknown"),
        "pipeline_type": metadata.get("pipeline_type", "single_branch_classifier"),
        "target_name": metadata.get("target_name", "pregnancy_high_risk"),
        "training_date_utc": metadata.get("training_date_utc"),
        "recall_target": metadata.get("recall_target"),
        "threshold": decision_threshold,
        "emergency_threshold": emergency_threshold,
        "evaluation_metrics": metadata.get("evaluation_metrics", {}),
        "features": metadata.get("features", {}),
        "class_distribution": metadata.get("class_distribution", {}),
        "dropped_rows": metadata.get("dropped_rows", {}),
        "training_samples": metadata.get("training_samples", {}),
        "label_mapping": metadata.get("label_mapping", {}),
        "notes": metadata.get("notes", []),
    }


def load_artifacts(force_reload: bool = False) -> Dict[str, Any]:
    return load_v2_artifacts(force_reload=force_reload)


def get_artifacts() -> Dict[str, Any]:
    return get_v2_artifacts()


def artifacts_available() -> bool:
    return v2_artifacts_available()


def get_model_info() -> Dict[str, Any]:
    return get_v2_model_info()
