from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """User entity"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    import_jobs = relationship("ImportJob", back_populates="user", cascade="all, delete-orphan")


class ImportJob(Base):
    """Import job entity"""
    __tablename__ = "import_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="Pending")  # Pending, Running, Completed, Failed
    selected_sources = Column(JSON, nullable=False)  # List of sources: ["products", "carts"]
    credentials = Column(JSON)  # Credentials per source
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="import_jobs")
    imported_items = relationship("ImportedItem", back_populates="job", cascade="all, delete-orphan")


class ImportedItem(Base):
    """Imported item entity"""
    __tablename__ = "imported_items"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("import_jobs.id"), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # "products" or "carts"
    remote_id = Column(Integer, nullable=False)  # ID from external API
    payload = Column(JSON, nullable=False)  # Full item data
    status = Column(String(50), nullable=False, default="Success")  # Success, Failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    job = relationship("ImportJob", back_populates="imported_items")
