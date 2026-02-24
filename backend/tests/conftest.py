from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app  # noqa: E402
from backend.db.session import engine  # noqa: E402
from backend.services.model_service import (  # noqa: E402
    artifacts_available,
    postpartum_artifacts_available,
    pregnancy_artifacts_available,
)


@pytest.fixture(scope="session", autouse=True)
def ensure_artifacts() -> None:
    if artifacts_available():
        pass
    else:
        infertility_training_script = ROOT / "notebooks" / "07_infertility_fusion_training.py"
        subprocess.run([sys.executable, str(infertility_training_script)], check=True)

    if pregnancy_artifacts_available():
        pass
    else:
        pregnancy_training_script = ROOT / "notebooks" / "08_pregnancy_risk_training.py"
        subprocess.run([sys.executable, str(pregnancy_training_script)], check=True)

    if postpartum_artifacts_available():
        return

    postpartum_pipeline_script = ROOT / "notebooks" / "run_postpartum_v1_pipeline.py"
    subprocess.run([sys.executable, str(postpartum_pipeline_script)], check=True)


@pytest.fixture(scope="session", autouse=True)
def enforce_postgresql_test_db() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError(
            "Integration tests require PostgreSQL. "
            "Set DATABASE_URL to a PostgreSQL test database before running pytest."
        )


@pytest.fixture(scope="session")
def client(ensure_artifacts: None, enforce_postgresql_test_db: None) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
