"""Database configuration and connection setup."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from ..core.logging_config import logger
from .base import Base
from app.config import config

# Create async engine
engine = create_async_engine(
    config.DATABASE_URL,
    echo=config.SQL_ECHO,
    future=True,
    pool_pre_ping=True,      # Automatically drops dead/stale connections
    pool_size=10,            # Maintain up to 10 persistent connections
    max_overflow=20,         # Allow bursting up to 20 additional temporary connections
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False
)

async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            # Force enable the vector extension first
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database tables", exc_info=e)
        raise
