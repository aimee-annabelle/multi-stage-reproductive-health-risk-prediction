from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import joblib


_ARTIFACT_CACHE: Dict[str, Any] | None = None


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


def get_v2_artifacts() -> Dict[str, Any]:
    return load_v2_artifacts(force_reload=False)


def v2_artifacts_available() -> bool:
    if _ARTIFACT_CACHE is not None:
        return True

    paths = _artifact_paths()
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


def load_artifacts(force_reload: bool = False) -> Dict[str, Any]:
    return load_v2_artifacts(force_reload=force_reload)


def get_artifacts() -> Dict[str, Any]:
    return get_v2_artifacts()


def artifacts_available() -> bool:
    return v2_artifacts_available()


def get_model_info() -> Dict[str, Any]:
    return get_v2_model_info()
