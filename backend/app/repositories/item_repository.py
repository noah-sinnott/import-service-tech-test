from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..models import ImportedItem, ImportJob


class ItemRepository:
    """Repository for ImportedItem data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, job_id: int, source: str, remote_id: int, payload: dict) -> ImportedItem:
        """Create a new imported item"""
        item = ImportedItem(
            job_id=job_id,
            source=source,
            remote_id=remote_id,
            payload=payload,
            status="Success",
            created_at=datetime.utcnow()
        )
        self.db.add(item)
        return item
    
    def bulk_create(self, items: List[ImportedItem]) -> None:
        """Bulk create items"""
        self.db.add_all(items)
        self.db.commit()
    
    def count_by_job_and_source(self, job_id: int, source: str) -> int:
        """Count items for a job and source"""
        return self.db.query(ImportedItem).filter(
            ImportedItem.job_id == job_id,
            ImportedItem.source == source
        ).count()
    
    def count_by_source(self, source: str) -> int:
        """Count items by source"""
        return self.db.query(ImportedItem).filter(
            ImportedItem.source == source
        ).count()
    
    def count_by_source_and_user(self, user_id: int, source: str) -> int:
        """Count items by source for a specific user"""
        return self.db.query(ImportedItem).join(ImportJob).filter(
            ImportJob.user_id == user_id,
            ImportedItem.source == source
        ).count()
    
    def get_recent(self, user_id: int, limit: int = 50) -> List[ImportedItem]:
        """Get recent items for a specific user"""
        return self.db.query(ImportedItem).join(ImportJob).filter(
            ImportJob.user_id == user_id
        ).order_by(
            ImportedItem.created_at.desc()
        ).limit(limit).all()
    
    def delete_by_job(self, job_id: int) -> None:
        """Delete all items for a job"""
        self.db.query(ImportedItem).filter(
            ImportedItem.job_id == job_id
        ).delete()
        self.db.commit()
