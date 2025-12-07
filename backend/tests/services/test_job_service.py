"""Tests for job_service.py"""
import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.job_service import JobService


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def job_service(mock_db):
    """Create job service with mocked database"""
    return JobService(mock_db)


def test_create_job_valid_sources(job_service):
    """Test creating job with valid sources"""
    job_service.job_repo.create = Mock(return_value=Mock(id=1, status="Pending"))
    
    selected_sources = ["products", "carts"]
    credentials = {
        "products": {"apiKey": "test123"},
        "carts": {"apiKey": "test456"}
    }
    
    job = job_service.create_job(user_id=1, selected_sources=selected_sources, credentials=credentials)
    
    # Should create job
    job_service.job_repo.create.assert_called_once()
    assert job.id == 1
    assert job.status == "Pending"


def test_create_job_invalid_source(job_service):
    """Test creating job with invalid source fails"""
    selected_sources = ["invalid"]
    credentials = {"invalid": {"apiKey": "test"}}
    
    with pytest.raises(ValueError, match="Invalid source"):
        job_service.create_job(user_id=1, selected_sources=selected_sources, credentials=credentials)


def test_create_job_missing_credentials(job_service):
    """Test creating job without required credentials fails"""
    selected_sources = ["products"]
    credentials = {}
    
    with pytest.raises(ValueError, match="Credentials are required"):
        job_service.create_job(user_id=1, selected_sources=selected_sources, credentials=credentials)


def test_list_jobs(job_service):
    """Test listing jobs"""
    mock_jobs = [
        Mock(id=1, status="Completed"),
        Mock(id=2, status="Pending")
    ]
    job_service.job_repo.list_jobs = Mock(return_value=mock_jobs)
    
    jobs = job_service.list_jobs(user_id=1, skip=0, limit=10)
    
    job_service.job_repo.list_jobs.assert_called_once_with(1, 0, 10)
    assert len(jobs) == 2
    assert jobs[0].id == 1


def test_get_job(job_service):
    """Test getting job by ID"""
    mock_job = Mock(id=1, status="Completed", user_id=1)
    job_service.job_repo.get_by_id = Mock(return_value=mock_job)
    
    job = job_service.get_job(job_id=1)
    
    job_service.job_repo.get_by_id.assert_called_once_with(1)
    assert job.id == 1
