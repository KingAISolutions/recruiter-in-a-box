from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from urllib.parse import urlparse

# Convert postgresql:// to postgresql+asyncpg:// for async support
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Build engine arguments
engine_args = {
    "pool_size": settings.DATABASE_POOL_SIZE,
    "max_overflow": settings.DATABASE_MAX_OVERFLOW,
}

# Add SSL configuration for production
if hasattr(settings, 'DATABASE_SSL_MODE') and settings.DATABASE_SSL_MODE != "disable":
    # Parse URL to add query parameters
    parsed = urlparse(DATABASE_URL)
    if parsed.query:
        new_query = f"{parsed.query}&sslmode={settings.DATABASE_SSL_MODE}"
    else:
        new_query = f"sslmode={settings.DATABASE_SSL_MODE}"
    
    # Rebuild URL with SSL parameters
    DATABASE_URL = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}{parsed.fragment}"

engine = create_async_engine(
    DATABASE_URL,
    **engine_args,
    echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
