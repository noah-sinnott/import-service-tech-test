from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import (
    CreateImportJobRequest,
    CreateImportJobResponse,
    GetImportJobResponse
)
from ..services.job_service import JobService
from ..services.import_service import ImportService

router = APIRouter(prefix="/import_jobs", tags=["jobs"])


@router.post("", response_model=CreateImportJobResponse, status_code=201)
async def create_import_job(
    request: CreateImportJobRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new import job and start processing immediately"""
    
    try:
        service = JobService(db)
        job = service.create_job(current_user.id, request.selected_sources, request.credentials)
        
        # Start processing in background
        background_tasks.add_task(
            ImportService.process_import_job,
            job.id,
            request.selected_sources
        )
        
        return CreateImportJobResponse(
            jobId=job.id,
            status=job.status,
            createdAt=job.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_id}", response_model=GetImportJobResponse)
def get_import_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get import job details"""
    
    service = JobService(db)
    job = service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if job belongs to current user
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    progress = service.calculate_progress(job)
    
    return GetImportJobResponse(
        jobId=job.id,
        status=job.status,
        selectedSources=job.selected_sources,
        progress=progress,
        error=job.error_message,
        createdAt=job.created_at,
        updatedAt=job.updated_at
    )


@router.get("", response_model=List[GetImportJobResponse])
def list_import_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all import jobs for the current user"""
    
    service = JobService(db)
    jobs = service.list_jobs(current_user.id, skip, limit)
    
    result = []
    for job in jobs:
        progress = service.calculate_progress(job)
        
        result.append(GetImportJobResponse(
            jobId=job.id,
            status=job.status,
            selectedSources=job.selected_sources,
            progress=progress,
            error=job.error_message,
            createdAt=job.created_at,
            updatedAt=job.updated_at
        ))
    
    return result
