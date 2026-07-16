from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from .config import AsyncSessionLocal

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection with strict lifecycle rollback boundaries."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # 💡 Guarantee database state integrity if service logic crashes downstream
            await session.rollback()
            raise
        finally:
            # Clean close ensures connection is safely returned to the pool immediately
            await session.close()