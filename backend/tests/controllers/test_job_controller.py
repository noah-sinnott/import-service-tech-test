"""Tests for job_controller.py"""
import pytest


def test_create_job_unauthenticated(client):
    """Test creating job without authentication fails"""
    response = client.post("/api/v1/import_jobs", json={
        "selectedSources": ["products"],
        "credentials": {"products": {"apiKey": "test"}}
    })
    assert response.status_code == 401


def test_create_job_success(client, auth_headers):
    """Test creating a job successfully"""
    response = client.post("/api/v1/import_jobs", json={
        "selectedSources": ["products"],
        "credentials": {"products": {"apiKey": "test"}}
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "jobId" in data
    assert data["status"] == "Pending"


def test_create_job_invalid_source(client, auth_headers):
    """Test creating job with invalid source fails"""
    response = client.post("/api/v1/import_jobs", json={
        "selectedSources": ["invalid"],
        "credentials": {"invalid": {"apiKey": "test"}}
    }, headers=auth_headers)
    assert response.status_code == 400


def test_create_job_missing_credentials(client, auth_headers):
    """Test creating job without credentials fails"""
    response = client.post("/api/v1/import_jobs", json={
        "selectedSources": ["products"],
        "credentials": {}
    }, headers=auth_headers)
    assert response.status_code == 400


def test_get_job_success(client, auth_headers):
    """Test getting a job by ID"""
    # Create job first
    create_response = client.post("/api/v1/import_jobs", json={
        "selectedSources": ["products"],
        "credentials": {"products": {"apiKey": "test"}}
    }, headers=auth_headers)
    job_id = create_response.json()["jobId"]
    
    # Get job
    response = client.get(f"/api/v1/import_jobs/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["jobId"] == job_id
    assert "progress" in data


def test_get_job_not_found(client, auth_headers):
    """Test getting nonexistent job fails"""
    response = client.get("/api/v1/import_jobs/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_job_different_user(client, auth_headers):
    """Test user cannot access another user's job"""
    # Create job with first user
    create_response = client.post("/api/v1/import_jobs", json={
        "selectedSources": ["products"],
        "credentials": {"products": {"apiKey": "test"}}
    }, headers=auth_headers)
    job_id = create_response.json()["jobId"]
    
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
    
    # Try to access first user's job
    response = client.get(f"/api/v1/import_jobs/{job_id}", headers=other_headers)
    assert response.status_code == 403


def test_list_jobs(client, auth_headers):
    """Test listing jobs"""
    # Create some jobs
    for i in range(3):
        client.post("/api/v1/import_jobs", json={
            "selectedSources": ["products"],
            "credentials": {"products": {"apiKey": f"test{i}"}}
        }, headers=auth_headers)
    
    response = client.get("/api/v1/import_jobs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_jobs_pagination(client, auth_headers):
    """Test job list pagination"""
    # Create 5 jobs
    for i in range(5):
        client.post("/api/v1/import_jobs", json={
            "selectedSources": ["products"],
            "credentials": {"products": {"apiKey": f"test{i}"}}
        }, headers=auth_headers)
    
    # Get first 2
    response = client.get("/api/v1/import_jobs?limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Get next 2
    response = client.get("/api/v1/import_jobs?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_jobs_user_isolation(client, auth_headers):
    """Test users only see their own jobs"""
    # Create job with first user
    client.post("/api/v1/import_jobs", json={
        "selectedSources": ["products"],
        "credentials": {"products": {"apiKey": "test"}}
    }, headers=auth_headers)
    
    # Register and login as second user
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
    
    # Second user should see no jobs
    response = client.get("/api/v1/import_jobs", headers=other_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
