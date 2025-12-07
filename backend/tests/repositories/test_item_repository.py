"""Tests for item_repository.py"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.repositories.item_repository import ItemRepository
from app.models import User, ImportJob


@pytest.fixture
def test_user_obj(db_session):
    """Create a test user object"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_job(db_session, test_user_obj):
    """Create a test job"""
    job = ImportJob(
        user_id=test_user_obj.id,
        selected_sources="products",
        credentials='{}',
        status="Completed"
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


def test_create_item(db_session, test_job):
    """Test creating imported item"""
    repo = ItemRepository(db_session)
    
    item = repo.create(
        job_id=test_job.id,
        source="products",
        remote_id=123,
        payload={"name": "Test Product"}
    )
    db_session.commit()
    db_session.refresh(item)
    
    assert item.id is not None
    assert item.job_id == test_job.id
    assert item.source == "products"
    assert item.remote_id == 123


def test_count_by_source_and_user(db_session, test_user_obj, test_job):
    """Test counting items by source for user"""
    repo = ItemRepository(db_session)
    
    # Create items
    repo.create(test_job.id, "products", 1, {})
    repo.create(test_job.id, "products", 2, {})
    repo.create(test_job.id, "carts", 1, {})
    db_session.commit()
    
    # Create job and items for another user
    other_user = User(email="other@example.com", username="other", hashed_password="h")
    db_session.add(other_user)
    db_session.commit()
    other_job = ImportJob(user_id=other_user.id, selected_sources="products", credentials='{}', status="Completed")
    db_session.add(other_job)
    db_session.commit()
    repo.create(other_job.id, "products", 3, {})
    db_session.commit()
    
    # Count products for test user
    count = repo.count_by_source_and_user(test_user_obj.id, "products")
    assert count == 2
    
    # Count carts
    count = repo.count_by_source_and_user(test_user_obj.id, "carts")
    assert count == 1


def test_get_recent_items(db_session, test_user_obj, test_job):
    """Test getting recent items"""
    repo = ItemRepository(db_session)
    
    # Create items
    item1 = repo.create(test_job.id, "products", 1, {"name": "Product 1"})
    item2 = repo.create(test_job.id, "products", 2, {"name": "Product 2"})
    db_session.commit()
    
    # Create items for another user
    other_user = User(email="other@example.com", username="other", hashed_password="h")
    db_session.add(other_user)
    db_session.commit()
    other_job = ImportJob(user_id=other_user.id, selected_sources="products", credentials='{}', status="Completed")
    db_session.add(other_job)
    db_session.commit()
    repo.create(other_job.id, "products", "prod3", '{}')
    
    # Get recent items for test user
    items = repo.get_recent(test_user_obj.id, limit=10)
    
    assert len(items) == 2
    assert all(item.job.user_id == test_user_obj.id for item in items)


def test_get_recent_items_limit(db_session, test_user_obj, test_job):
    """Test limiting recent items"""
    repo = ItemRepository(db_session)
    
    # Create 5 items
    for i in range(5):
        repo.create(test_job.id, "products", i, {})
    db_session.commit()
    
    # Get only 3
    items = repo.get_recent(test_user_obj.id, limit=3)
    assert len(items) == 3


def test_get_recent_items_ordering(db_session, test_user_obj, test_job):
    """Test recent items are ordered by created date DESC"""
    repo = ItemRepository(db_session)
    
    item1 = repo.create(test_job.id, "products", 1, {})
    item2 = repo.create(test_job.id, "products", 2, {})
    item3 = repo.create(test_job.id, "products", 3, {})
    db_session.commit()
    
    items = repo.get_recent(test_user_obj.id, limit=10)
    
    # Should be in reverse order (newest first)
    assert items[0].remote_id == 3
    assert items[1].remote_id == 2
    assert items[2].remote_id == 1
