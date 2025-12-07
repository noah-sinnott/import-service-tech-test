"""Tests for dashboard_controller.py"""
import pytest


def test_get_dashboard_unauthenticated(client):
    """Test accessing dashboard without auth fails"""
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 401


def test_get_dashboard_success(client, auth_headers):
    """Test getting dashboard stats"""
    response = client.get("/api/v1/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "totalJobs" in data
    assert "completedJobs" in data
    assert "failedJobs" in data
    assert "totalProducts" in data
    assert "totalCarts" in data
    assert "recentItems" in data


def test_dashboard_user_isolation(client, auth_headers):
    """Test dashboard only shows user's data"""
    # Create job for first user
    client.post("/api/v1/import_jobs", json={
        "selectedSources": ["products"],
        "credentials": {"products": {"apiKey": "test"}}
    }, headers=auth_headers)
    
    # First user's dashboard
    response = client.get("/api/v1/dashboard", headers=auth_headers)
    data1 = response.json()
    
    # Register second user
    client.post("/api/v1/auth/register", json={
        "email": "other@example.com",
        "username": "otheruser",
        "password": "password123"
    })
    login_response = client.post("/api/v1/auth/login", json={
        "username": "otheruser",
        "password": "password123"
    })
    other_token = login_response.json()["accessToken"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Second user's dashboard should be empty
    response = client.get("/api/v1/dashboard", headers=other_headers)
    data2 = response.json()
    assert data2["totalJobs"] == 0
    assert data1["totalJobs"] == 1
