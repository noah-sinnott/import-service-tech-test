from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, List, Any
from datetime import datetime


# ===== Authentication Schemas =====

class UserRegisterRequest(BaseModel):
    """Request to register a new user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)


class UserLoginRequest(BaseModel):
    """Request to login"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    
    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    """User information response"""
    id: int
    email: str
    username: str
    created_at: datetime = Field(..., alias="createdAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TokenData(BaseModel):
    """Data stored in JWT token"""
    user_id: int
    username: str


# ===== Import Job Schemas =====

class CreateImportJobRequest(BaseModel):
    """Request to create an import job"""
    selected_sources: List[str] = Field(..., description="List of data sources to import", alias="selectedSources")
    credentials: Dict[str, Dict[str, str]] = Field(..., description="Credentials per source")
    
    class Config:
        populate_by_name = True


class CreateImportJobResponse(BaseModel):
    """Response after creating an import job"""
    job_id: int = Field(..., alias="jobId")
    status: str
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


class SourceProgress(BaseModel):
    """Progress for a single source"""
    completed: int
    total: int
    status: str


class GetImportJobResponse(BaseModel):
    """Response for getting job details"""
    job_id: int = Field(..., alias="jobId")
    status: str
    selected_sources: List[str] = Field(..., alias="selectedSources")
    progress: Dict[str, SourceProgress]
    error: Optional[str]
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True


class SimulateImportRequest(BaseModel):
    """Request to simulate an import"""
    job_id: int = Field(..., alias="jobId")
    force_failure: bool = Field(False, alias="forceFailure")

    class Config:
        populate_by_name = True


class SimulateImportResponse(BaseModel):
    """Response after simulating an import"""
    job_id: int = Field(..., alias="jobId")
    updated_status: str = Field(..., alias="updatedStatus")
    imported_count: int = Field(..., alias="importedCount")
    failed_count: int = Field(..., alias="failedCount")

    class Config:
        populate_by_name = True


class ImportedItemResponse(BaseModel):
    """Response for an imported item"""
    id: int
    source: str
    remote_id: int = Field(..., alias="remoteId")
    status: str
    created_at: datetime = Field(..., alias="createdAt")
    payload: Dict[str, Any]

    class Config:
        populate_by_name = True
        from_attributes = True


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_jobs: int = Field(..., alias="totalJobs")
    completed_jobs: int = Field(..., alias="completedJobs")
    failed_jobs: int = Field(..., alias="failedJobs")
    total_products: int = Field(..., alias="totalProducts")
    total_carts: int = Field(..., alias="totalCarts")
    recent_items: List[ImportedItemResponse] = Field(..., alias="recentItems")

    class Config:
        populate_by_name = True
