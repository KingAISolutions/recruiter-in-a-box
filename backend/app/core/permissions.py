"""
Role-Based Access Control (RBAC) permissions system.
"""
from enum import Enum
from functools import wraps
from typing import List, Optional, Callable
from fastapi import HTTPException, status, Depends
from app.models import User


class Role(str, Enum):
    """User roles in the system."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Permission(str, Enum):
    """Available permissions."""
    # Candidates
    CANDIDATE_READ = "candidate:read"
    CANDIDATE_CREATE = "candidate:create"
    CANDIDATE_UPDATE = "candidate:update"
    CANDIDATE_DELETE = "candidate:delete"
    CANDIDATE_SCORING = "candidate:scoring"
    
    # Jobs
    JOB_READ = "job:read"
    JOB_CREATE = "job:create"
    JOB_UPDATE = "job:update"
    JOB_DELETE = "job:delete"
    
    # Templates
    TEMPLATE_READ = "template:read"
    TEMPLATE_CREATE = "template:create"
    TEMPLATE_UPDATE = "template:update"
    TEMPLATE_DELETE = "template:delete"
    
    # Outreach
    OUTREACH_READ = "outreach:read"
    OUTREACH_SEND = "outreach:send"
    
    # Team
    TEAM_READ = "team:read"
    TEAM_INVITE = "team:invite"
    TEAM_UPDATE = "team:update"
    TEAM_DELETE = "team:delete"
    
    # Billing
    BILLING_READ = "billing:read"
    BILLING_MANAGE = "billing:manage"
    
    # Admin
    ADMIN_ALL = "admin:all"


# Role-permission mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [
        Permission.CANDIDATE_READ,
        Permission.CANDIDATE_CREATE,
        Permission.CANDIDATE_UPDATE,
        Permission.CANDIDATE_DELETE,
        Permission.CANDIDATE_SCORING,
        Permission.JOB_READ,
        Permission.JOB_CREATE,
        Permission.JOB_UPDATE,
        Permission.JOB_DELETE,
        Permission.TEMPLATE_READ,
        Permission.TEMPLATE_CREATE,
        Permission.TEMPLATE_UPDATE,
        Permission.TEMPLATE_DELETE,
        Permission.OUTREACH_READ,
        Permission.OUTREACH_SEND,
        Permission.TEAM_READ,
        Permission.TEAM_INVITE,
        Permission.TEAM_UPDATE,
        Permission.TEAM_DELETE,
        Permission.BILLING_READ,
        Permission.BILLING_MANAGE,
        Permission.ADMIN_ALL,
    ],
    Role.ADMIN: [
        Permission.CANDIDATE_READ,
        Permission.CANDIDATE_CREATE,
        Permission.CANDIDATE_UPDATE,
        Permission.CANDIDATE_DELETE,
        Permission.CANDIDATE_SCORING,
        Permission.JOB_READ,
        Permission.JOB_CREATE,
        Permission.JOB_UPDATE,
        Permission.JOB_DELETE,
        Permission.TEMPLATE_READ,
        Permission.TEMPLATE_CREATE,
        Permission.TEMPLATE_UPDATE,
        Permission.TEMPLATE_DELETE,
        Permission.OUTREACH_READ,
        Permission.OUTREACH_SEND,
        Permission.TEAM_READ,
        Permission.TEAM_INVITE,
        Permission.TEAM_UPDATE,
        # Cannot delete team members
        Permission.BILLING_READ,
    ],
    Role.MEMBER: [
        Permission.CANDIDATE_READ,
        Permission.CANDIDATE_CREATE,
        Permission.CANDIDATE_UPDATE,
        # Cannot delete candidates
        Permission.CANDIDATE_SCORING,
        Permission.JOB_READ,
        Permission.JOB_CREATE,
        Permission.JOB_UPDATE,
        Permission.TEMPLATE_READ,
        Permission.TEMPLATE_CREATE,
        Permission.TEMPLATE_UPDATE,
        Permission.OUTREACH_READ,
        Permission.OUTREACH_SEND,
        Permission.TEAM_READ,
        # Cannot manage team
        Permission.BILLING_READ,
    ],
}


def get_user_role(user: User) -> Role:
    """Get the role for a user."""
    if not user:
        return Role.MEMBER
    
    # Check if user is owner (first user or explicitly set)
    if getattr(user, 'is_owner', False) or getattr(user, 'role', None) == Role.OWNER:
        return Role.OWNER
    
    # Check team membership for role
    if hasattr(user, 'team_role'):
        role_str = getattr(user, 'team_role', Role.MEMBER)
        return Role(role_str) if role_str in [r.value for r in Role] else Role.MEMBER
    
    return Role.MEMBER


def has_permission(user: User, permission: Permission) -> bool:
    """Check if a user has a specific permission."""
    if not user:
        return False
    
    role = get_user_role(user)
    return permission in ROLE_PERMISSIONS.get(role, [])


def has_any_permission(user: User, permissions: List[Permission]) -> bool:
    """Check if a user has any of the specified permissions."""
    return any(has_permission(user, p) for p in permissions)


def has_all_permissions(user: User, permissions: List[Permission]) -> bool:
    """Check if a user has all of the specified permissions."""
    return all(has_permission(user, p) for p in permissions)


def require_permissions(*permissions: Permission):
    """
    Decorator to require specific permissions for an endpoint.
    
    Usage:
        @router.delete("/{id}")
        @require_permissions(Permission.CANDIDATE_DELETE)
        async def delete_candidate(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs or args
            current_user = kwargs.get('current_user')
            if current_user is None:
                # Try to get from bound dependencies
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "PERMISSION_DENIED",
                            "message": "Authentication required"
                        }
                    }
                )
            
            if not has_any_permission(current_user, list(permissions)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "PERMISSION_DENIED",
                            "message": f"Required permissions: {[p.value for p in permissions]}"
                        }
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(*roles: Role):
    """
    Decorator to require specific roles for an endpoint.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if current_user is None:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "PERMISSION_DENIED",
                            "message": "Authentication required"
                        }
                    }
                )
            
            user_role = get_user_role(current_user)
            if user_role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "ROLE_REQUIRED",
                            "message": f"Required roles: {[r.value for r in roles]}"
                        }
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Permission dependency for FastAPI
class PermissionChecker:
    """FastAPI dependency for checking permissions."""
    
    def __init__(self, required_permissions: List[Permission]):
        self.required_permissions = required_permissions
    
    async def __call__(self, current_user: User = Depends(lambda: None)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "UNAUTHORIZED", "message": "Not authenticated"}}
            )
        
        if not has_any_permission(current_user, self.required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "PERMISSION_DENIED", "message": "Insufficient permissions"}}
            )
        
        return current_user


def require(*permissions: Permission):
    """FastAPI dependency for requiring permissions."""
    return Depends(PermissionChecker(list(permissions)))
