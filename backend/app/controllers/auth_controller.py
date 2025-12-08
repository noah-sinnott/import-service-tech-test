from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import UserRegisterRequest, UserLoginRequest, Token, UserResponse
from ..services.auth_service import AuthService
from ..repositories.user_repository import UserRepository


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    user_repo = UserRepository(db)
    
    # Check if username already exists
    if user_repo.exists_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_repo.exists_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = AuthService.get_password_hash(request.password)
    user = user_repo.create(
        email=request.email,
        username=request.username,
        hashed_password=hashed_password
    )
    
    # Create access token
    access_token = AuthService.create_access_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    user_repo = UserRepository(db)
    
    # Get user by username
    user = user_repo.get_by_username(request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not AuthService.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = AuthService.create_access_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return Token(access_token=access_token, token_type="bearer")
