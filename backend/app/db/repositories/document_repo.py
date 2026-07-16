from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.db.models import Document, DocumentChunk
from .base import BaseRepository

class DocumentRepository(BaseRepository[Document]):
    def __init__(self):
        super().__init__(Document)

    async def update_status(self, session: AsyncSession, document_id: int, status: str) -> Optional[Document]:
        """Updates the operational processing pipeline phase state."""
        await session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(status=status)
        )
        return await self.get_by_id(session, document_id)

    async def get_by_filename(self, session: AsyncSession, filename: str) -> Optional[Document]:
        """Checks for pre-existing files to prevent redundant ingestion processing."""
        result = await session.execute(
            select(Document).where(Document.filename == filename)
        )
        return result.scalars().first()

    async def update_metadata(
        self, session: AsyncSession, document_id: int, page_count: int, raw_text_chars: int
    ) -> Optional[Document]:
        """Populates vital extraction telemetry markers post-parsing."""
        await session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(page_count=page_count, raw_text_chars=raw_text_chars)
        )
        return await self.get_by_id(session, document_id)
    
    async def list_documents_with_chunk_counts(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Tuple[Document, int]]:
        """
        Fetches documents along with their pre-calculated chunk counts 
        via an efficient database group-by operation. Prevents lazy-loading crashes.
        """

        stmt = (
            select(Document, func.count(DocumentChunk.id).label("chunk_count"))
            .join(DocumentChunk, Document.id == DocumentChunk.document_id, isouter=True)  # <-- Changed here
            .group_by(Document.id)
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        # Returns a list of tuples: [(DocumentObject, count), ...]
        return [(row[0], int(row[1])) for row in result.all()]