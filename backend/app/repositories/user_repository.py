from sqlalchemy.orm import Session
from typing import Optional

from ..models import User


class UserRepository:
    """Repository for User data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, username: str, hashed_password: str) -> User:
        """Create a new user"""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        return self.db.query(User).filter(User.username == username).count() > 0
    
    def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        return self.db.query(User).filter(User.email == email).count() > 0
