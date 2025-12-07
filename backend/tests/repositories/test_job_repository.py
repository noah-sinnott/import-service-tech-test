"""Tests for job_repository.py"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.repositories.job_repository import JobRepository
from app.models import User


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


def test_create_job(db_session, test_user_obj):
    """Test creating a job"""
    repo = JobRepository(db_session)
    
    job = repo.create(
        user_id=test_user_obj.id,
        selected_sources="products,carts",
        credentials='{"products": {"apiKey": "test"}}'
    )
    
    assert job.id is not None
    assert job.user_id == test_user_obj.id
    assert job.selected_sources == "products,carts"
    assert job.status == "Pending"


def test_get_job_by_id(db_session, test_user_obj):
    """Test getting job by ID"""
    repo = JobRepository(db_session)
    
    job = repo.create(test_user_obj.id, "products", '{}')
    
    retrieved = repo.get_by_id(job.id)
    assert retrieved is not None
    assert retrieved.id == job.id


def test_list_jobs_by_user(db_session, test_user_obj):
    """Test listing jobs filtered by user"""
    repo = JobRepository(db_session)
    
    # Create jobs for test user
    job1 = repo.create(test_user_obj.id, "products", '{}')
    job2 = repo.create(test_user_obj.id, "carts", '{}')
    
    # Create another user and job
    other_user = User(email="other@example.com", username="other", hashed_password="h")
    db_session.add(other_user)
    db_session.commit()
    repo.create(other_user.id, "products", '{}')
    
    # List jobs for test user
    jobs = repo.list_jobs(test_user_obj.id, skip=0, limit=10)
    
    assert len(jobs) == 2
    assert all(job.user_id == test_user_obj.id for job in jobs)


def test_list_jobs_pagination(db_session, test_user_obj):
    """Test job list pagination"""
    repo = JobRepository(db_session)
    
    # Create 5 jobs
    for i in range(5):
        repo.create(test_user_obj.id, f"source{i}", '{}')
    
    # Get first 2
    jobs = repo.list_jobs(test_user_obj.id, skip=0, limit=2)
    assert len(jobs) == 2
    
    # Get next 2
    jobs = repo.list_jobs(test_user_obj.id, skip=2, limit=2)
    assert len(jobs) == 2


def test_update_job(db_session, test_user_obj):
    """Test updating job status"""
    repo = JobRepository(db_session)
    
    job = repo.create(test_user_obj.id, "products", '{}')
    
    repo.update_status(job.id, "Running")
    db_session.refresh(job)
    
    assert job.status == "Running"


def test_count_by_status(db_session, test_user_obj):
    """Test counting jobs by status"""
    repo = JobRepository(db_session)
    
    # Create jobs with different statuses
    job1 = repo.create(test_user_obj.id, "products", '{}')
    job2 = repo.create(test_user_obj.id, "carts", '{}')
    repo.update_status(job1.id, "Completed")
    
    # Create job for another user (should not be counted)
    other_user = User(email="other@example.com", username="other", hashed_password="h")
    db_session.add(other_user)
    db_session.commit()
    repo.create(other_user.id, "products", '{}')
    
    completed = repo.count_by_status(test_user_obj.id, "Completed")
    pending = repo.count_by_status(test_user_obj.id, "Pending")
    
    assert completed == 1
    assert pending == 1


def test_count_all_jobs(db_session, test_user_obj):
    """Test counting all jobs for user"""
    repo = JobRepository(db_session)
    
    # Create jobs
    repo.create(test_user_obj.id, "products", '{}')
    repo.create(test_user_obj.id, "carts", '{}')
    
    # Create job for another user
    other_user = User(email="other@example.com", username="other", hashed_password="h")
    db_session.add(other_user)
    db_session.commit()
    repo.create(other_user.id, "products", '{}')
    
    count = repo.count_all(test_user_obj.id)
    assert count == 2
