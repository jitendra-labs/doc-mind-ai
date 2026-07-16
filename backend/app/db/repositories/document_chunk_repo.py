from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import joinedload

from ..models.document_chunk import DocumentChunk
from ..models.document import Document
from .base import BaseRepository

class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self):
        super().__init__(DocumentChunk)

    async def bulk_create_chunks(self, session: AsyncSession, chunks_data: List[dict]) -> List[DocumentChunk]:
        """
        High-performance bulk insertion for text blocks during ingestion pipelines.
        Leverages SQLAlchemy unit of work batch processing.
        """
        chunks = [DocumentChunk(**data) for data in chunks_data]
        session.add_all(chunks)
        await session.flush()  # Pushes records to Postgres engine buffer instantly
        return chunks

    async def vector_similarity_search(
        self, 
        session: AsyncSession,
        query_embedding: List[float], 
        top_k: int = 4, 
        doc_type_filter: Optional[str] = None,
        document_id_filter: Optional[int] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Performs high-performance vector similarity lookups utilizing pgvector cosine operators.
        
        Returns:
            List[Tuple[DocumentChunk, float]]: Pairs of (Chunk record, Cosine distance score)
        """
        # Hook directly into pgvector's native distance calculation operators
        distance_metric = DocumentChunk.embedding.cosine_distance(query_embedding)
        
        # Build relational execution statement
        stmt = (
            select(DocumentChunk, distance_metric.label("distance"))
            # Eagerly load the associated document record via a JOIN
            .options(joinedload(DocumentChunk.document))
            .where(DocumentChunk.embedding.is_not(None))
        )
        
        # Metadata Filtering Constraint: Query isolated document subsets (e.g. only 'lab_report')
        # Apply your metadata filters if provided
        if document_id_filter:
            stmt = stmt.where(DocumentChunk.document_id == document_id_filter)
        if doc_type_filter:
            # Assumes document table contains a doc_type or mapping
            stmt = stmt.join(Document).where(Document.doc_type == doc_type_filter)
            
        stmt = stmt.order_by("distance").limit(top_k)
        
        result = await session.execute(stmt)
        return result.all()