from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import DashboardStats, ImportedItemResponse
from ..repositories.job_repository import JobRepository
from ..repositories.item_repository import ItemRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the current user"""
    
    job_repo = JobRepository(db)
    item_repo = ItemRepository(db)
    
    total_jobs = job_repo.count_all(current_user.id)
    completed_jobs = job_repo.count_by_status(current_user.id, "Completed")
    failed_jobs = job_repo.count_by_status(current_user.id, "Failed")
    
    total_products = item_repo.count_by_source_and_user(current_user.id, "products")
    total_carts = item_repo.count_by_source_and_user(current_user.id, "carts")
    
    recent_items = item_repo.get_recent(current_user.id, limit=50)
    
    return DashboardStats(
        totalJobs=total_jobs,
        completedJobs=completed_jobs,
        failedJobs=failed_jobs,
        totalProducts=total_products,
        totalCarts=total_carts,
        recentItems=[ImportedItemResponse.model_validate(item) for item in recent_items]
    )
