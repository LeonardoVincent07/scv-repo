import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app exactly as defined in app_backend/main.py
from app_backend.main import app


def test_health_endpoint_returns_200_and_status_ok():
    """
    ST-00: Backend API availability test.

    Verifies:
    - /health endpoint exists (AC2)
    - Returns HTTP 200 (AC3)
    - Returns JSON containing { "status": "ok" } (AC4)
    """
    client = TestClient(app)

    response = client.get("/health")

    # AC3: HTTP 200
    assert response.status_code == 200

    data = response.json()

    # AC4: JSON contains "status": "ok"
    assert isinstance(data, dict)
    assert data.get("status") == "ok"
