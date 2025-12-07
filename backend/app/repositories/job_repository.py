from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models import ImportJob


class JobRepository:
    """Repository for ImportJob data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, selected_sources: List[str], credentials: dict) -> ImportJob:
        """Create a new import job"""
        job = ImportJob(
            user_id=user_id,
            status="Pending",
            selected_sources=selected_sources,
            credentials=credentials,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_by_id(self, job_id: int) -> Optional[ImportJob]:
        """Get job by ID"""
        return self.db.query(ImportJob).filter(ImportJob.id == job_id).first()
    
    def list_jobs(self, user_id: int, skip: int = 0, limit: int = 20) -> List[ImportJob]:
        """List jobs for a user with pagination"""
        return self.db.query(ImportJob).filter(
            ImportJob.user_id == user_id
        ).order_by(
            ImportJob.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def update_status(self, job_id: int, status: str, error_message: str = None) -> None:
        """Update job status"""
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            if error_message:
                job.error_message = error_message
            job.updated_at = datetime.utcnow()
            self.db.commit()
    
    def count_by_status(self, user_id: int, status: str) -> int:
        """Count jobs by status for a user"""
        return self.db.query(ImportJob).filter(
            ImportJob.user_id == user_id,
            ImportJob.status == status
        ).count()
    
    def count_all(self, user_id: int) -> int:
        """Count all jobs for a user"""
        return self.db.query(ImportJob).filter(ImportJob.user_id == user_id).count()
