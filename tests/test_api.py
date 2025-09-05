"""Test API endpoints."""
import pytest
from fastapi.testclient import TestClient

from web.app import app


@pytest.fixture
def test_client():
    """Create test client."""
    return TestClient(app)


def test_health_check(test_client):
    """Test health check endpoint."""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "card-collector-web"


def test_home_page(test_client):
    """Test home page loads."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Card Collector" in response.text