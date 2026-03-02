from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.database import get_db, User, APIKey
from app.models.schemas import User as UserSchema
import hashlib
import secrets

from config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user ID."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return hash_api_key(api_key) == hashed_key


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def authenticate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Authenticate using API key."""
    api_key = credentials.credentials
    hashed_key = hash_api_key(api_key)
    
    api_key_record = db.query(APIKey).filter(
        APIKey.key_hash == hashed_key,
        APIKey.is_active == True
    ).first()
    
    if not api_key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check if key has expired
    if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    # Update last used timestamp
    api_key_record.last_used_at = datetime.utcnow()
    db.commit()
    
    user = db.query(User).filter(User.id == api_key_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


def check_dataset_permission(user: User, dataset_id: str, db: Session) -> bool:
    """Check if user has permission to access dataset."""
    from app.models.database import Dataset
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        return False
    
    # Owner can always access
    if dataset.owner_id == user.id:
        return True
    
    # Public datasets can be accessed by anyone
    if dataset.is_public:
        return True
    
    return False


def check_run_permission(user: User, run_id: str, db: Session) -> bool:
    """Check if user has permission to access run."""
    from app.models.database import Run
    
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        return False
    
    return run.user_id == user.id


def sanitize_sensitive_data(data: dict, sensitive_columns: list = None) -> dict:
    """Sanitize sensitive data from logs and responses."""
    if sensitive_columns is None:
        sensitive_columns = settings.SENSITIVE_COLUMNS
    
    if not isinstance(data, dict):
        return data
    
    sanitized = data.copy()
    
    def _sanitize_value(key: str, value: any) -> any:
        # Check if key contains sensitive information
        key_lower = key.lower()
        for sensitive in sensitive_columns:
            if sensitive in key_lower:
                return "[REDACTED]"
        
        # Recursively sanitize nested structures
        if isinstance(value, dict):
            return {k: _sanitize_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_sanitize_value(f"{key}[{i}]", item) for i, item in enumerate(value)]
        else:
            return value
    
    return {k: _sanitize_value(k, v) for k, v in sanitized.items()}
