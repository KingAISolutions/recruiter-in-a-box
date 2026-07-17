from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Recruiter In A Box"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - NO DEFAULTS for security
    DATABASE_URL: str
    
    # SSL configuration for database
    DATABASE_SSL_MODE: str = "require"  # require, verify-full, verify-ca
    
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # JWT - SECURITY: No default secret key
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_PROFESSIONAL: Optional[str] = None
    STRIPE_PRICE_AGENCY: Optional[str] = None
    
    # Frontend URL (for redirects)
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Email (Resend or other SMTP provider)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@recruiterinabox.com"
    
    # CORS - Must be explicit in production
    CORS_ORIGINS: str = '["http://localhost:5173"]'
    
    @field_validator('CORS_ORIGINS')
    @classmethod
    def parse_cors_origins(cls, v):
        import json
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Allowed file types (MIME types)
    ALLOWED_FILE_TYPES: str = '["application/pdf"]'
    
    @field_validator('ALLOWED_FILE_TYPES')
    @classmethod
    def parse_allowed_types(cls, v):
        import json
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    # Trial settings
    TRIAL_DAYS: int = 14
    
    # Redis for rate limiting and token blacklist (optional but recommended)
    REDIS_URL: Optional[str] = None
    
    # Sentry error tracking (optional)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    
    # Security headers
    SECURITY_HEADERS_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get settings with validation."""
    settings = Settings()
    
    # Validate critical settings
    _validate_settings(settings)
    
    return settings


def _validate_settings(settings: Settings):
    """Validate required settings."""
    errors = []
    
    # Check for insecure defaults
    if settings.SECRET_KEY == "your-secret-key-change-in-production":
        errors.append("SECRET_KEY must be changed from default value")
    
    if settings.SECRET_KEY and len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY must be at least 32 characters")
    
    # In production, enforce strict settings
    if not settings.DEBUG:
        if not settings.STRIPE_SECRET_KEY:
            errors.append("STRIPE_SECRET_KEY is required in production")
        
        # Check CORS configuration
        if "*" in str(settings.CORS_ORIGINS):
            errors.append("CORS_ORIGINS cannot contain wildcards in production")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")


# Create settings instance
try:
    settings = get_settings()
except ValueError as e:
    # In development, allow missing settings
    import os
    if os.environ.get("ENVIRONMENT", "development") == "production":
        raise
    # Use minimal settings for development
    class MinimalSettings:
        APP_NAME = "Recruiter In A Box"
        APP_VERSION = "1.0.0"
        DEBUG = True
        HOST = "0.0.0.0"
        PORT = 8000
        SECRET_KEY = "dev-secret-key-not-for-production"
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 15
        REFRESH_TOKEN_EXPIRE_DAYS = 7
        DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
        DATABASE_SSL_MODE = "disable"
        DATABASE_POOL_SIZE = 10
        DATABASE_MAX_OVERFLOW = 20
        FRONTEND_URL = "http://localhost:5173"
        EMAIL_FROM = "noreply@recruiterinabox.com"
        SMTP_HOST = None
        SMTP_PORT = 587
        SMTP_USER = None
        SMTP_PASSWORD = None
        UPLOAD_DIR = "./uploads"
        MAX_FILE_SIZE = 10 * 1024 * 1024
        ALLOWED_FILE_TYPES = ["application/pdf"]
        TRIAL_DAYS = 14
        CORS_ORIGINS = ["http://localhost:5173"]
        OPENAI_API_KEY = None
        OPENAI_MODEL = "gpt-4-turbo-preview"
        STRIPE_SECRET_KEY = None
        STRIPE_PUBLISHABLE_KEY = None
        STRIPE_WEBHOOK_SECRET = None
        STRIPE_PRICE_PROFESSIONAL = None
        STRIPE_PRICE_AGENCY = None
        SUPABASE_URL = None
        SUPABASE_KEY = None
        SUPABASE_SERVICE_KEY = None
        REDIS_URL = None
        SENTRY_DSN = None
        SENTRY_ENVIRONMENT = "development"
        SECURITY_HEADERS_ENABLED = True
    settings = MinimalSettings()
