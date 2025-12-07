from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from ..models import ImportJob
from ..schemas import SourceProgress
from ..repositories.job_repository import JobRepository
from ..repositories.item_repository import ItemRepository


class JobService:
    """Service for managing import jobs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
        self.item_repo = ItemRepository(db)
    
    def create_job(self, user_id: int, selected_sources: List[str], credentials: Dict) -> ImportJob:
        """Create a new import job"""
        # Validate
        self._validate_sources(selected_sources)
        self._validate_credentials(selected_sources, credentials)
        
        return self.job_repo.create(user_id, selected_sources, credentials)
    
    def get_job(self, job_id: int) -> Optional[ImportJob]:
        """Get a job by ID"""
        return self.job_repo.get_by_id(job_id)
    
    def list_jobs(self, user_id: int, skip: int, limit: int) -> List[ImportJob]:
        """List all jobs for a user with pagination"""
        return self.job_repo.list_jobs(user_id, skip, limit)
    
    def calculate_progress(self, job: ImportJob) -> Dict[str, SourceProgress]:
        """Calculate progress for each source in a job"""
        progress = {}
        
        for source in job.selected_sources:
            completed = self.item_repo.count_by_job_and_source(job.id, source)
            total = 30 if source == "products" else 20
            
            # Determine source status
            if job.status == "Completed":
                source_status = "Completed"
            elif job.status == "Failed":
                source_status = "Failed"
            elif completed > 0:
                source_status = "Running"
            else:
                source_status = "Pending"
            
            progress[source] = SourceProgress(
                completed=completed,
                total=total,
                status=source_status
            )
        
        return progress
    
    def _validate_sources(self, sources: List[str]) -> None:
        """Validate that sources are valid"""
        valid_sources = {"products", "carts"}
        if not all(source in valid_sources for source in sources):
            raise ValueError("Invalid sources. Must be one of: products, carts")
    
    def _validate_credentials(self, sources: List[str], credentials: Dict) -> None:
        """Validate that all sources have credentials"""
        if not credentials:
            raise ValueError("Credentials are required")
        
        for source in sources:
            if source not in credentials:
                raise ValueError(f"Missing credentials for source: {source}")
