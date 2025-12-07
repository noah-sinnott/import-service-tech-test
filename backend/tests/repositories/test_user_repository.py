"""Tests for user_repository.py"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.repositories.user_repository import UserRepository


def test_create_user(db_session):
    """Test creating a user"""
    repo = UserRepository(db_session)
    
    user = repo.create(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123"
    )
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password == "hashedpassword123"
    assert user.is_active is True


def test_get_user_by_id(db_session):
    """Test getting user by ID"""
    repo = UserRepository(db_session)
    
    user = repo.create("test@example.com", "testuser", "hashed")
    
    retrieved = repo.get_by_id(user.id)
    assert retrieved is not None
    assert retrieved.id == user.id
    assert retrieved.username == "testuser"


def test_get_user_by_username(db_session):
    """Test getting user by username"""
    repo = UserRepository(db_session)
    
    repo.create("test@example.com", "testuser", "hashed")
    
    user = repo.get_by_username("testuser")
    assert user is not None
    assert user.username == "testuser"


def test_get_user_by_email(db_session):
    """Test getting user by email"""
    repo = UserRepository(db_session)
    
    repo.create("test@example.com", "testuser", "hashed")
    
    user = repo.get_by_email("test@example.com")
    assert user is not None
    assert user.email == "test@example.com"


def test_exists_by_username(db_session):
    """Test checking if username exists"""
    repo = UserRepository(db_session)
    
    assert repo.exists_by_username("testuser") is False
    
    repo.create("test@example.com", "testuser", "hashed")
    
    assert repo.exists_by_username("testuser") is True
    assert repo.exists_by_username("otheruser") is False


def test_exists_by_email(db_session):
    """Test checking if email exists"""
    repo = UserRepository(db_session)
    
    assert repo.exists_by_email("test@example.com") is False
    
    repo.create("test@example.com", "testuser", "hashed")
    
    assert repo.exists_by_email("test@example.com") is True
    assert repo.exists_by_email("other@example.com") is False
