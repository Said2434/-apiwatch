"""
Database configuration and session management.
Uses SQLAlchemy 2.0 with async support.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Base class for SQLAlchemy models
Base = declarative_base()

# Synchronous engine (for Alembic migrations)
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20
)

# Async engine (for FastAPI endpoints)
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factories
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# Dependency for FastAPI endpoints
async def get_db() -> AsyncSession:
    """
    Async database session dependency.
    Usage in FastAPI:
        @app.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def create_tables():
    """Create all database tables. Used for initial setup."""
    Base.metadata.create_all(bind=sync_engine)


def drop_tables():
    """Drop all database tables. Use with caution!"""
    Base.metadata.drop_all(bind=sync_engine)
