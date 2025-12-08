"""Tests for auth_controller.py"""
import pytest


def test_register_user(client):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"


def test_register_duplicate_username(client, test_user):
    """Test registering with duplicate username fails"""
    response = client.post("/api/v1/auth/register", json={
        "email": "another@example.com",
        "username": test_user["username"],
        "password": "password123"
    })
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()


def test_register_duplicate_email(client, test_user):
    """Test registering with duplicate email fails"""
    response = client.post("/api/v1/auth/register", json={
        "email": test_user["email"],
        "username": "differentuser",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_register_invalid_email(client):
    """Test registration with invalid email fails"""
    response = client.post("/api/v1/auth/register", json={
        "email": "notanemail",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_short_password(client):
    """Test registration with short password fails"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "short"
    })
    assert response.status_code == 422


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post("/api/v1/auth/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password fails"""
    response = client.post("/api/v1/auth/login", json={
        "username": test_user["username"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with nonexistent user fails"""
    response = client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "password123"
    })
    assert response.status_code == 401
