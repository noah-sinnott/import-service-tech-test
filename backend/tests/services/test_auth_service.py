"""Tests for auth_service.py"""
import pytest
from unittest.mock import patch
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.auth_service import AuthService


def test_hash_password():
    """Test password hashing"""
    password = "testpassword123"
    hashed = AuthService.get_password_hash(password)
    
    # Hash should be different from password
    assert hashed != password
    # Hash should be bcrypt format
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    """Test password verification with correct password"""
    password = "testpassword123"
    hashed = AuthService.get_password_hash(password)
    
    assert AuthService.verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with wrong password"""
    password = "testpassword123"
    hashed = AuthService.get_password_hash(password)
    
    assert AuthService.verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    """Test JWT token creation"""
    user_id = 1
    username = "testuser"
    data = {"sub": username, "user_id": user_id}
    token = AuthService.create_access_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    # Token should have JWT format (3 base64 parts)
    assert len(token.split(".")) == 3


def test_decode_access_token_valid():
    """Test decoding valid JWT token"""
    user_id = 1
    username = "testuser"
    data = {"sub": username, "user_id": user_id, "username": username}
    token = AuthService.create_access_token(data)
    
    decoded = AuthService.decode_access_token(token)
    
    assert decoded is not None
    assert decoded.username == username
    assert decoded.user_id == user_id


def test_decode_access_token_invalid():
    """Test decoding invalid token"""
    decoded = AuthService.decode_access_token("invalid.token.here")
    assert decoded is None


def test_decode_access_token_expired():
    """Test decoding expired token"""
    with patch("app.services.auth_service.datetime") as mock_datetime:
        # Set current time
        mock_datetime.utcnow.return_value = datetime(2024, 1, 1)
        
        # Create token
        data = {"sub": "testuser", "user_id": 1}
        token = AuthService.create_access_token(data)
        
        # Move time forward past expiration
        mock_datetime.utcnow.return_value = datetime(2024, 1, 10)
        
        # Token should be expired
        decoded = AuthService.decode_access_token(token)
        assert decoded is None
