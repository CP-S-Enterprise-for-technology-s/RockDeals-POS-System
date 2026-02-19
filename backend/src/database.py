"""
CP'S Enterprise POS - Database Module
======================================
Database connection and session management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Create async engine
engine = create_async_engine(
    str(settings.database_url).replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    echo=settings.is_development,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency.
    
    Yields:
        AsyncSession: Database session
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


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session as async context manager.
    
    Yields:
        AsyncSession: Database session
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


async def init_db() -> None:
    """Initialize database tables."""
    from src.models import Base
    
    async with engine.begin() as conn:
        if settings.is_development:
            # In development, create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        else:
            # In production, use migrations
            logger.info("Database initialization skipped (use migrations in production)")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")


async def check_db_connection() -> bool:
    """
    Check database connection health.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
