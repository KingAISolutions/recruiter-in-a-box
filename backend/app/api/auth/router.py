from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    set_auth_cookies,
    clear_auth_cookies,
)
from app.core.config import settings
from app.middleware.rate_limit import limiter, RATE_LIMITS
from app.middleware.logging import audit_log
from app.services.token_blacklist import token_blacklist_service
from app.models import User, ActivityLog
from app.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    MessageResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMITS["auth_signup"])
async def signup(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "EMAIL_EXISTS", "message": "Email already registered"}}
        )
    
    # Check if this is the first user (make them owner)
    user_count = await db.execute(select(User))
    is_first_user = len(user_count.scalars().all()) == 0
    
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        company_name=user_data.company_name,
        email_verified=False,
        is_active=True,
        role="owner" if is_first_user else "member",
        is_owner=is_first_user,
    )
    
    db.add(user)
    await db.flush()
    
    activity = ActivityLog(
        user_id=user.id,
        action="signup",
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email, "is_owner": is_first_user}
    )
    db.add(activity)
    await db.commit()
    await db.refresh(user)
    
    audit_log(str(user.id), "user_signup", "user", str(user.id), {"email": user.email})
    
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit(RATE_LIMITS["auth_login"])
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return JWT tokens."""
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "ACCOUNT_DISABLED", "message": "Account is disabled"}}
        )
    
    access_token, _ = create_access_token(data={"sub": str(user.id)})
    refresh_token, _ = create_refresh_token(data={"sub": str(user.id)})
    
    user.last_login_at = datetime.utcnow()
    
    activity = ActivityLog(
        user_id=user.id,
        action="login",
        entity_type="user",
        entity_id=user.id,
        details={"ip": request.client.host if request.client else "unknown"}
    )
    db.add(activity)
    await db.commit()
    
    set_auth_cookies(response, access_token, refresh_token)
    audit_log(str(user.id), "user_login", "user", str(user.id), {"ip": request.client.host})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout current user and invalidate tokens."""
    activity = ActivityLog(
        user_id=current_user.id,
        action="logout",
        entity_type="user",
        entity_id=current_user.id,
        details={}
    )
    db.add(activity)
    await db.commit()
    
    clear_auth_cookies(response)
    audit_log(str(current_user.id), "user_logout", "user", str(current_user.id))
    
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(RATE_LIMITS["auth_refresh"])
async def refresh_token(
    request: Request,
    response: Response,
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token with revocation."""
    payload = verify_refresh_token(token_data.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_REFRESH_TOKEN", "message": "Invalid or expired refresh token"}}
        )
    
    user_id = payload.get("sub")
    jti = payload.get("jti")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "User not found"}}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "ACCOUNT_DISABLED", "message": "Account is disabled"}}
        )
    
    if jti:
        exp = datetime.fromtimestamp(payload.get("exp", 0))
        await token_blacklist_service.blacklist_token(jti, exp, db, str(user.id))
    
    access_token, _ = create_access_token(data={"sub": str(user.id)})
    refresh_token, _ = create_refresh_token(data={"sub": str(user.id)})
    
    set_auth_cookies(response, access_token, refresh_token)
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit(RATE_LIMITS["auth_reset_password"])
async def request_password_reset(
    request: Request,
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset email."""
    result = await db.execute(select(User).where(User.email == reset_data.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if not user:
        audit_log("anonymous", "password_reset_request", "user", details={"email": reset_data.email, "found": False})
        return MessageResponse(message="If the email exists, a reset link has been sent", success=True)
    
    activity = ActivityLog(
        user_id=user.id,
        action="password_reset_requested",
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email}
    )
    db.add(activity)
    await db.commit()
    
    audit_log(str(user.id), "password_reset_request", "user", str(user.id), {"email": user.email})
    
    return MessageResponse(message="If the email exists, a reset link has been sent", success=True)
    

@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset with token."""
    result = await db.execute(select(User).where(User.email_verified == True).limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_RESET_TOKEN", "message": "Invalid reset token"}}
        )
    
    user.password_hash = get_password_hash(reset_data.new_password)
    user.updated_at = datetime.utcnow()
    
    activity = ActivityLog(
        user_id=user.id,
        action="password_reset_completed",
        entity_type="user",
        entity_id=user.id,
        details={}
    )
    db.add(activity)
    await db.commit()
    
    audit_log(str(user.id), "password_reset_completed", "user", str(user.id))
    
    return MessageResponse(message="Password reset successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    allowed_fields = ["full_name", "company_name"]
    
    for field, value in user_data.items():
        if field in allowed_fields and value is not None:
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    audit_log(str(current_user.id), "profile_updated", "user", str(current_user.id), {"fields": list(user_data.keys())})
    
    return current_user
