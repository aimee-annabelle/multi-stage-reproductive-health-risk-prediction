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
from backend.services.model_service import artifacts_available  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def ensure_artifacts() -> None:
    if artifacts_available():
        return

    training_script = ROOT / "notebooks" / "07_infertility_fusion_training.py"
    subprocess.run([sys.executable, str(training_script)], check=True)


@pytest.fixture(scope="session")
def client(ensure_artifacts: None) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
