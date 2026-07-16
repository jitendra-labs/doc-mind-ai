from typing import Generic, Type, TypeVar, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Stateless Base Repository providing common CRUD operations.
    The AsyncSession must be passed explicitly to ensure atomic transaction control
    at the service/orchestration layer.
    """
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, session: AsyncSession, id: Any) -> Optional[T]:
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def list_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        result = await session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, obj_in: dict) -> T:
        session_obj = self.model(**obj_in)
        session.add(session_obj)
        await session.flush()  # Populates the ID field without committing the transaction
        return session_obj

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        result = await session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0