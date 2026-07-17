from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging
import asyncio

from app.core.config import settings
from app.core.database import init_db, engine
from app.api import api_router
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.logging import RequestLoggingMiddleware, logger

# Configure basic logging for startup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
app_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.log("info", "application_starting", app_name=settings.APP_NAME)
    
    # Initialize Sentry if configured
    if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.SENTRY_ENVIRONMENT,
                traces_sample_rate=0.1,
            )
            logger.log("info", "sentry_initialized")
        except ImportError:
            logger.log("warning", "sentry_not_installed")
        except Exception as e:
            logger.log("error", "sentry_init_failed", error=str(e))
    
    # Initialize database
    try:
        await init_db()
        logger.log("info", "database_initialized")
    except Exception as e:
        logger.log("error", "database_init_failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.log("info", "application_shutting_down")
    
    # Close database connections
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Recruitment Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler with structured error codes
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.log(
        "error",
        "unhandled_exception",
        request_id=request_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            }
        }
    )


# Include API router
app.include_router(api_router)


# Enhanced health check with dependency status
@app.get("/health")
async def health_check():
    """Enhanced health check endpoint."""
    checks = {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
    
    # Database check
    db_status = "healthy"
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        logger.log("error", "health_check_db_failed", error=str(e))
    
    checks["database"] = db_status
    
    # Overall status
    overall = "healthy" if db_status == "healthy" else "degraded"
    
    return {
        "status": overall,
        **checks
    }


# Readiness probe
@app.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"}
        )


# Liveness probe
@app.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG if hasattr(settings, 'DEBUG') else False
    )
