"""
Rate limiting middleware using SlowAPI.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


def get_real_ip(request: Request) -> str:
    """Get real client IP from request headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(key_func=get_real_ip)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "details": [
                    {
                        "field": "rate_limit",
                        "message": f"Limit: {exc.detail}"
                    }
                ]
            }
        }
    )


# Rate limit configurations
RATE_LIMITS = {
    # Auth endpoints - very strict
    "auth_login": "5/minute",
    "auth_signup": "3/minute",
    "auth_reset_password": "3/minute",
    "auth_refresh": "10/minute",
    
    # API endpoints - moderate
    "api_read": "100/minute",
    "api_write": "50/minute",
    "api_bulk": "10/minute",
    
    # File uploads - limited
    "file_upload": "20/minute",
    
    # Default for unknown endpoints
    "default": "60/minute",
}
