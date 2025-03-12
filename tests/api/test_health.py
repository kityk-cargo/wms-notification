from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_liveness_endpoint():
    """Test the liveness endpoint returns a 200 status code and UP status."""
    response = client.get("/health/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "timestamp" in data


def test_readiness_endpoint():
    """Test the readiness endpoint returns a 200 status code and UP status."""
    response = client.get("/health/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "timestamp" in data
    assert "components" in data
    assert data["components"]["application"]["status"] == "UP"


def test_startup_endpoint():
    """Test the startup endpoint returns a 200 status code and UP status."""
    response = client.get("/health/startup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "timestamp" in data


def test_health_endpoint():
    """Test the main health endpoint returns a 200 status code and overall health status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "timestamp" in data
    assert "components" in data
    assert data["components"]["application"]["status"] == "UP"
