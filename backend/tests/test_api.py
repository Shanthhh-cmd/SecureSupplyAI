import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_login_demo_user():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@securesupply.ai", "password": "admin123"}
        )
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

def test_dashboard_summary():
    with TestClient(app) as client:
        # Login first
        login_res = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@securesupply.ai", "password": "admin123"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/dashboard/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "risk_distribution" in data
