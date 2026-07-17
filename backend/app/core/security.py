from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.config import settings
from app.core.database import get_db
from app.models import User
from app.services.token_blacklist import token_blacklist_service

# Password hashing context with configurable cost
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# HTTP Bearer scheme for API auth (optional to allow cookie fallback)
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> Tuple[str, str]:
    """
    Create a JWT access token with unique JTI.
    
    Returns:
        Tuple of (token, jti)
    """
    to_encode = data.copy()
    
    # Generate unique JWT ID
    jti = f"{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:16]}"
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire, 
        "type": "access",
        "jti": jti,
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti


def create_refresh_token(data: dict) -> Tuple[str, str]:
    """
    Create a JWT refresh token with unique JTI.
    
    Returns:
        Tuple of (token, jti)
    """
    to_encode = data.copy()
    
    # Generate unique JWT ID
    jti = f"{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:16]}"
    
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire, 
        "type": "refresh",
        "jti": jti,
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti


def decode_token(token: str, db: AsyncSession = None) -> dict:
    """
    Decode and verify a JWT token.
    Checks blacklist if db session provided.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        
        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and db:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If in async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    is_blacklisted = pool.submit(
                        asyncio.run, 
                        token_blacklist_service.is_blacklisted(jti, db)
                    ).result()
            else:
                is_blacklisted = asyncio.run(
                    token_blacklist_service.is_blacklisted(jti, db)
                )
            
            if is_blacklisted:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": {
                            "code": "TOKEN_REVOKED",
                            "message": "Token has been revoked"
                        }
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "TOKEN_EXPIRED",
                    "message": "Token has expired"
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid token"
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str) -> Optional[dict]:
    """Verify an access token."""
    try:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None
    except HTTPException:
        return None


def verify_refresh_token(token: str) -> Optional[dict]:
    """Verify a refresh token."""
    try:
        payload = decode_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None
    except HTTPException:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
    request: Request = None
) -> User:
    """
    Get the current authenticated user from the JWT token.
    Supports both Bearer token and httpOnly cookie.
    """
    token = None
    
    # Try Bearer token first
    if credentials:
        token = credentials.credentials
    
    # Fall back to cookie
    if not token and request:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Not authenticated"
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "Could not validate credentials"
            }
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token, db)
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INACTIVE_USER",
                    "message": "Inactive user"
                }
            }
        )
    return current_user


def set_auth_cookies(response, access_token: str, refresh_token: str = None):
    """Set authentication cookies on response."""
    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    # Refresh token cookie (if provided)
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )


def clear_auth_cookies(response):
    """Clear authentication cookies."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
