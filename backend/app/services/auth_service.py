from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

from ..config import settings
from ..schemas import TokenData


class AuthService:
    """Service for handling authentication"""
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        # Encode password and hash, truncate to 72 bytes for bcrypt
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Hash a password"""
        # Encode and truncate to 72 bytes for bcrypt
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @classmethod
    def decode_access_token(cls, token: str) -> Optional[TokenData]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: int = payload.get("user_id")
            username: str = payload.get("username")
            
            if user_id is None or username is None:
                return None
            
            return TokenData(user_id=user_id, username=username)
        except JWTError:
            return None
